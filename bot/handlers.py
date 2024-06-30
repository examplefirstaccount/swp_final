from datetime import datetime
import json
from aiogram import Router, html, Bot
from aiogram import types
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from .state import ChatState, save_state, load_state
from .filters import HasMessageText, HasMessageUserUsername, HasChatState
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .meeting import schedule_meeting
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from .custom_types import SendMessage, SaveState, LoadState
from aiogram.utils.i18n import I18n, gettext as _
from .constants import (
    day_of_week_pretty,
    datetime_time_format,
    iso8601,
    time_url,
    sample_time,
)
from .commands import bot_command_names
from .messages import make_help_message
from textwrap import dedent
import logging
from aiogram.enums import ParseMode

def make_router(scheduler: AsyncIOScheduler, send_message: SendMessage, i18n: I18n):
    router = Router()

    handle_global_commands(
        scheduler=scheduler, send_message=send_message, router=router, i18n=i18n
    )

    handle_team_settings_commands(
        scheduler=scheduler, send_message=send_message, router=router
    )

    handle_personal_settings_commands(
        scheduler=scheduler, send_message=send_message, router=router
    )

    handle_info_commands(scheduler=scheduler, send_message=send_message, router=router)

    return router


class LanguageForm(StatesGroup):
    choosing = State()


def handle_global_commands(
        scheduler: AsyncIOScheduler, send_message: SendMessage, router: Router, i18n: I18n
):
    @router.message(Command(bot_command_names.start), HasChatState())
    async def start(message: Message, chat_state: ChatState):
        await get_help(message=message, chat_state=chat_state, i18n=i18n)

    @router.message(Command(bot_command_names.help), HasChatState())
    async def get_help(message: Message, chat_state: ChatState, i18n: I18n):
        I18n.current_locale = chat_state.language
        await message.reply(i18n.gettext(make_help_message()))


    @router.message(Command(bot_command_names.lang), HasChatState())
    async def set_lang(message: types.Message, chat_state: ChatState, state: FSMContext,  i18n: I18n):
        await state.set_state(LanguageForm.choosing)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="English", callback_data='lang_en')],
            [InlineKeyboardButton(text="Русский", callback_data='lang_ru')],
        ])
        await message.answer("Please choose your language / Пожалуйста, выберите язык", reply_markup=keyboard)

    @router.callback_query(lambda c: c.data == 'lang_en' or c.data == 'lang_ru')
    async def process_callback_button_language(callback_query: types.CallbackQuery, i18n: I18n):
        chat_id = callback_query.message.chat.id
        chat_state = await load_state(chat_id)
        new_language = 'en' if callback_query.data == 'lang_en' else 'ru'
        chat_state.language = new_language
        i18n.current_locale = new_language


        try:
            await save_state(chat_state)
            await callback_query.answer()
            confirmation_message = 'English language selected!' if new_language == 'en' else 'Выбран русский язык!'
            await callback_query.message.answer(confirmation_message)
        except Exception as e:
            await callback_query.answer()
            await callback_query.message.answer(_('Error saving language state: {error}').format(error=e))


def handle_team_settings_commands(
        scheduler: AsyncIOScheduler, send_message: SendMessage, router: Router
):
    @router.message(
        Command(bot_command_names.set_meetings_time), HasMessageText(), HasChatState()
    )
    async def set_meetings_time(
            message: Message, message_text: str, chat_state: ChatState
    ):
        meeting_time_str = message_text.split(" ", 1)

        try:
            meeting_time = datetime.fromisoformat(meeting_time_str[1])
            chat_state.meeting_time = meeting_time
            await save_state(chat_state=chat_state)

            schedule_meeting(
                meeting_time=meeting_time,
                chat_id=chat_state.chat_id,
                scheduler=scheduler,
                send_message=send_message,
            )

            await message.reply(
                _(
                    "OK, we'll meet at {meeting_time} on {week_days} starting than on {start_date}!"
                ).format(
                    meeting_time=html.bold(meeting_time.strftime("%H:%M")),
                    week_days=html.bold(day_of_week_pretty),
                    start_date=html.bold(meeting_time.strftime("%Y-%m-%d")),
                )
            )
        except Exception as e:
            await message.reply(
                dedent(
                    _(
                        """
                        Please write the meetings time in the {iso8601} format with an offset relative to the UTC time zone.

                        You can calculate the time on the site {time_url}.

                        Example:

                        /{set_meetings_time} {sample_time}
                        """
                    ).format(
                        iso8601=iso8601,
                        time_url=time_url,
                        set_meetings_time=bot_command_names.set_meetings_time,
                        sample_time=sample_time,
                    )
                )
            )


def handle_personal_settings_commands(
        scheduler: AsyncIOScheduler, send_message: SendMessage, router: Router
):
    @router.message(
        Command(bot_command_names.join), HasMessageUserUsername(), HasChatState()
    )
    async def subscribe(message: Message, username: str, chat_state: ChatState):
        if username in chat_state.joined_users:
            await message.reply(
                _("You've already joined, @{username}!").format(username=username)
            )
        else:
            chat_state.joined_users.add(username)
            await save_state(chat_state=chat_state)
            await message.reply(
                dedent(
                    _(
                        """
                        You've just joined, @{username}!

                        You can skip meetings via the /{command_skip} command.
                        """
                    ).format(
                        username=username, command_skip=bot_command_names.skip
                    )
                )
            )

    @router.message(
        Command(bot_command_names.skip), HasMessageUserUsername(), HasChatState()
    )
    async def unsubscribe(message: Message, username: str, chat_state: ChatState):
        if username in chat_state.joined_users:
            chat_state.joined_users.remove(username)
            await save_state(chat_state=chat_state)
            await message.reply(
                dedent(
                    _(
                        """
                        See you later, @{username}!

                        You can join via the /{command_join} command.
                        """
                    )
                ).format(username=username, command_join=bot_command_names.join)
            )
        else:
            await message.reply(
                dedent(
                    _("You've not yet joined, @{username}!").format(
                        username=username
                    )
                )
            )


def handle_info_commands(
        scheduler: AsyncIOScheduler, send_message: SendMessage, router: Router
):
    @router.message(Command(bot_command_names.get_chat_state), HasChatState())
    async def get_chat_state(message: Message, chat_state: ChatState):
        chat_state_json = chat_state.model_dump_json(indent=2)
        await message.reply(
            dedent(
                f"""<pre><code class="language-json">{chat_state_json}</code></pre>"""
            ),
            parse_mode=ParseMode.HTML,
        )
