import asyncio
import re

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils import markdown as fmt
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .callbacks import IntervalCallback, WeekdayCallback
from .commands import bot_command_names
from .custom_types import SendMessage
from .filters import HasChatState, HasMessageUserUsername
from .fsm_states import IntervalEditingState
from .i18n import _
from .intervals import Interval, get_default_interval
from .keyboards import (get_interval_edit_options, get_schedule_keyboard,
                        get_schedule_options)
from .messages import (make_interval_editing_error,
                       make_interval_editing_instruction,
                       make_interval_validation_message)
from .state import ChatState, ChatUser, get_user, save_state

INTERVAL_PATTERN = r"^\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}$"


class Mode:
    personal = "personal"
    default = "default"

    def __init__(self):
        self.default_i18n = _("default")
        self.personal_i18n = _("personal")


def mode_to_mode_i18n(mode: str):
    mode_constants = Mode()
    match mode:
        case Mode.personal:
            return mode_constants.personal_i18n
        case Mode.default:
            return mode_constants.default_i18n


def get_schedule_by_mode(chat_state: ChatState, user: ChatUser):
    mode = user.schedule_mode
    if mode == Mode.personal:
        week_schedule = user.temp_schedule
        tz = user.time_zone
        shift = user.time_zone_shift
    else:
        week_schedule = chat_state.temp_schedule
        tz = chat_state.time_zone
        shift = chat_state.time_zone_shift

    return week_schedule, tz, shift


async def clear_schedule_cache(
    bot: Bot, chat_state: ChatState, user: ChatUser, state: FSMContext
):
    if user.schedule_msg is not None:
        try:
            await bot.delete_message(chat_id=chat_state.chat_id, message_id=user.schedule_msg)
        except TelegramBadRequest as e:
            print(e.message)

    user.schedule_mode = None
    user.schedule_msg = None
    user.to_edit_weekday = None
    user.to_edit_interval = None

    if len(user.to_delete_msg_ids) > 0:
        for msg_id in user.to_delete_msg_ids:
            try:
                await bot.delete_message(chat_id=chat_state.chat_id, message_id=msg_id)
            except TelegramBadRequest as e:
                print(e.message)
        user.to_delete_msg_ids = set()

    await state.clear()


def handle_working_hours(
    scheduler: AsyncIOScheduler, send_message: SendMessage, router: Router, bot: Bot
):
    @router.message(Command(bot_command_names.set_working_hours))
    async def show_schedule_options(message: Message):

        layout = get_schedule_options()
        
        mode_constants = Mode()
        
        tip_default = _(
            "Press '{default}' to set working hours that will be used as default personal working hours by all people."
        ).format(default=mode_constants.default_i18n.capitalize())
        tip_personal = _("Press '{personal}' to set personal working hours.").format(
            personal=mode_constants.personal_i18n.capitalize()
        )
        text = fmt.text(tip_default, tip_personal, sep="\n\n")

        await message.answer(text=text, reply_markup=layout)

    @router.callback_query(
        F.data.regexp("(default|personal)_schedule"),
        HasMessageUserUsername(),
        HasChatState(),
    )
    async def show_schedule(cb: CallbackQuery, username: str, chat_state: ChatState):

        await cb.answer()

        mode = cb.data.split("_")[0] if cb.data else None

        user = await get_user(chat_state, username)

        if mode == Mode.personal:
            user.temp_schedule = user.schedule
            week_schedule = user.temp_schedule
            tz = user.time_zone
            shift = user.time_zone_shift
            text = _("@{username}, here is your personal schedule.").format(
                username=username
            )
        else:
            chat_state.temp_schedule = chat_state.schedule
            week_schedule = chat_state.temp_schedule
            tz = chat_state.time_zone
            shift = chat_state.time_zone_shift
            text = _("@{username}, here is the default chat schedule.").format(
                username=username
            )

        layout = get_schedule_keyboard(week_schedule, tz, shift)

        match cb.message:
            case Message():
                schedule_msg = await cb.message.answer(text=text, reply_markup=layout)
                user.schedule_msg = schedule_msg.message_id
            case _:
                user.schedule_msg = None

        # Cache
        user.schedule_mode = mode

        await save_state(chat_state)

    @router.callback_query(
        IntervalCallback.filter(F.action == "edit"),
        HasMessageUserUsername(),
        HasChatState(),
    )
    async def show_interval_editing_instruction(
        cb: CallbackQuery,
        state: FSMContext,
        callback_data: IntervalCallback,
        username: str,
        chat_state: ChatState,
    ):

        weekday = callback_data.weekday
        interval_uid = callback_data.interval

        text = make_interval_editing_instruction()

        await state.set_state(IntervalEditingState.EnterNewInterval)

        await cb.answer()

        user = await get_user(chat_state, username)
        match cb.message:
            case Message():
                edit_message = await cb.message.answer(text=text)
                user.to_delete_msg_ids.add(edit_message.message_id)

        # Cache
        user.to_edit_weekday = weekday
        user.to_edit_interval = interval_uid
        await save_state(chat_state)

    @router.message(
        IntervalEditingState.EnterNewInterval, HasMessageUserUsername(), HasChatState()
    )
    async def handle_interval_editing(
        message: Message, state: FSMContext, username: str, chat_state: ChatState
    ):

        parse_pattern = re.compile(INTERVAL_PATTERN)
        parse_match = (
            re.fullmatch(parse_pattern, message.text.strip()) if message.text else None
        )

        # Cache
        user = await get_user(chat_state, username)
        user.to_delete_msg_ids.add(message.message_id)

        # Text entered by user is not an interval
        if not parse_match:
            if message.text:
                error_msg_text = _(
                    "The interval {interval} is not in the 'hh:mm - hh:mm' format."
                ).format(message.text.strip())
            else:
                error_msg_text = _("The interval is not in the 'hh:mm - hh:mm' format.")

        # User entered one "valid" interval
        else:
            week_schedule, tz, shift = get_schedule_by_mode(
                chat_state=chat_state, user=user
            )

            weekday = user.to_edit_weekday
            old_interval_uid = user.to_edit_interval

            new_interval = parse_match[0]
            is_valid, error_msg_text = make_interval_validation_message(
                interval_str=new_interval, tz=tz, shift=shift
            )

            # Interval is valid
            if is_valid:
                old_interval_obj = week_schedule[weekday].get_interval(
                    uid=old_interval_uid
                )
                new_interval_obj = Interval.from_string(
                    interval_str=new_interval, tz=tz, shift=shift
                )
                week_schedule[weekday].remove_interval(
                    old_interval_obj, tz, shift, ignore_inclusion=True
                )
                week_schedule[weekday].add_interval(new_interval_obj)

                layout = get_schedule_keyboard(week_schedule, tz, shift)
                await bot.edit_message_reply_markup(
                    chat_id=chat_state.chat_id,
                    message_id=user.schedule_msg,
                    reply_markup=layout,
                )

                success_msg = await message.answer(
                    _("OK, the interval was set to {new_interval}.").format(
                        new_interval=new_interval
                    )
                )
                await asyncio.sleep(1)
                await success_msg.delete()
                for msg_id in user.to_delete_msg_ids:
                    try:
                        await bot.delete_message(chat_id=chat_state.chat_id, message_id=msg_id)
                    except TelegramBadRequest as e:
                        print(e.message)

                user.to_delete_msg_ids = set()

                await state.clear()
                await save_state(chat_state)
                return

        if user.to_edit_weekday and user.to_edit_interval:
            error_msg_text = make_interval_editing_error(error_msg=error_msg_text)
            layout = get_interval_edit_options(
                weekday=user.to_edit_weekday, interval_uid=user.to_edit_interval
            )
            error_msg = await message.answer(
                text=f"{error_msg_text}\n", reply_markup=layout
            )

            user.to_delete_msg_ids.add(error_msg.message_id)

        await save_state(chat_state)

    @router.callback_query(
        F.data == "cancel_interval_edit", HasMessageUserUsername(), HasChatState()
    )
    async def cancel_interval_editing(
        cb: CallbackQuery, state: FSMContext, username: str, chat_state: ChatState
    ):

        await cb.answer()
        user = await get_user(chat_state, username)

        user.to_edit_weekday = None
        user.to_edit_interval = None

        for msg_id in user.to_delete_msg_ids:
            try:
                await bot.delete_message(chat_id=chat_state.chat_id, message_id=msg_id)
            except TelegramBadRequest as e:
                print(e.message)
        user.to_delete_msg_ids = set()
        await state.clear()
        await save_state(chat_state)

    @router.callback_query(
        IntervalCallback.filter(F.action == "add"),
        HasMessageUserUsername(),
        HasChatState(),
    )
    async def add_interval(
        cb: CallbackQuery,
        callback_data: IntervalCallback,
        username: str,
        chat_state: ChatState,
    ):

        weekday = callback_data.weekday

        user = await get_user(chat_state, username)

        week_schedule, tz, shift = get_schedule_by_mode(
            chat_state=chat_state, user=user
        )

        interval = get_default_interval(tz=tz, shift=shift)
        week_schedule[weekday].add_interval(interval)

        match cb.message:
            case Message():
                layout = get_schedule_keyboard(week_schedule, tz, shift)
                await cb.message.edit_reply_markup(reply_markup=layout)
        await save_state(chat_state)

    @router.callback_query(
        IntervalCallback.filter(F.action == "remove"),
        HasMessageUserUsername(),
        HasChatState(),
    )
    async def remove_interval(
        cb: CallbackQuery,
        callback_data: IntervalCallback,
        username: str,
        chat_state: ChatState,
    ):

        weekday = callback_data.weekday
        interval_uid = callback_data.interval

        user = await get_user(chat_state, username)

        week_schedule, tz, shift = get_schedule_by_mode(
            chat_state=chat_state, user=user
        )

        interval = week_schedule[weekday].get_interval(interval_uid)
        week_schedule[weekday].remove_interval(interval, tz, shift)

        match cb.message:
            case Message():
                layout = get_schedule_keyboard(week_schedule, tz, shift)
                await cb.message.edit_reply_markup(reply_markup=layout)
        await save_state(chat_state)

    @router.callback_query(
        WeekdayCallback.filter(F.action == "toggle"),
        HasMessageUserUsername(),
        HasChatState(),
    )
    async def toggle_weekday(
        cb: CallbackQuery,
        callback_data: WeekdayCallback,
        username: str,
        chat_state: ChatState,
    ):

        weekday = callback_data.weekday

        user = await get_user(chat_state, username)

        week_schedule, tz, shift = get_schedule_by_mode(
            chat_state=chat_state, user=user
        )

        week_schedule[weekday].toggle_inclusion(tz, shift)

        match cb.message:
            case Message():
                layout = get_schedule_keyboard(week_schedule, tz, shift)
                await cb.message.edit_reply_markup(reply_markup=layout)
        await save_state(chat_state)

    @router.callback_query(
        F.data == "cancel_schedule", HasMessageUserUsername(), HasChatState()
    )
    async def cancel_changes(
        cb: CallbackQuery, state: FSMContext, username: str, chat_state: ChatState
    ):

        await cb.answer()

        user = await get_user(chat_state, username)
        mode = user.schedule_mode
        if mode == Mode.personal:
            user.temp_schedule = None
        else:
            chat_state.temp_schedule = None

        await clear_schedule_cache(
            bot=bot, chat_state=chat_state, user=user, state=state
        )

        match cb.message:
            case Message():
                if mode:
                    await cb.message.answer(
                        _("The {mode} schedule was not updated.").format(mode=mode_to_mode_i18n(mode))
                    )
        await save_state(chat_state)

    @router.callback_query(
        F.data == "save_schedule", HasMessageUserUsername(), HasChatState()
    )
    async def save_changes(
        cb: CallbackQuery, state: FSMContext, username: str, chat_state: ChatState
    ):

        await cb.answer()

        user = await get_user(chat_state, username)
        mode = user.schedule_mode
        if mode == Mode.personal and user.temp_schedule:
            norm_schedule = {
                item[0]: item[1].normalize_intervals()
                for item in user.temp_schedule.items()
            }
            user.schedule = norm_schedule
            user.temp_schedule = None
        elif mode == Mode.default and chat_state.temp_schedule:
            norm_schedule = {
                item[0]: item[1].normalize_intervals()
                for item in chat_state.temp_schedule.items()
            }
            chat_state.schedule = norm_schedule
            chat_state.temp_schedule = None

        await clear_schedule_cache(
            bot=bot, chat_state=chat_state, user=user, state=state
        )

        match cb.message:
            case Message():
                if mode:
                    await cb.message.answer(
                        _("The {mode} schedule was updated.").format(mode=mode_to_mode_i18n(mode))
                    )
        await save_state(chat_state)

    @router.callback_query(F.data == "#")
    async def handle_placeholders(cb: CallbackQuery):
        await cb.answer()
