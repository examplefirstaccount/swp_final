from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

from . import db, handlers
from .commands import bot_command_descriptions, bot_command_names
from .constants import jobstore
from .custom_types import ChatId, SendMessage
from .i18n import i18n
from .i18n_middleware import MyI18nMiddleware
from .meeting import schedule_meeting
from .middlewares import GroupCommandFilterMiddleware
from .recurring_message import update_recurring_message
from .settings import Settings
from .state import ChatState


def init_scheduler(settings: Settings) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=utc, jobstores={jobstore: MemoryJobStore()})
    scheduler.start()
    return scheduler


async def restore_scheduled_jobs(
    scheduler: AsyncIOScheduler, send_message: SendMessage
):
    chat_states = await ChatState.find_all().to_list()

    for chat_state in chat_states:
        if chat_state.meeting_time:
            is_topic = chat_state.topic_id is not None
            schedule_meeting(
                meeting_time=chat_state.meeting_time,
                chat_id=chat_state.chat_id,
                is_topic=is_topic,
                topic_id=chat_state.topic_id,
                scheduler=scheduler,
                send_message=send_message,
            )


async def set_default_commands(bot: Bot):
    commands = []
    descriptions = bot_command_descriptions()

    attribute_names = vars(bot_command_names).keys()
    for attr in attribute_names:
        cmd_name = getattr(bot_command_names, attr)
        cmd_descr = getattr(descriptions, attr)
        cmd = BotCommand(command=cmd_name, description=cmd_descr)
        commands.append(cmd)

    await bot.set_my_commands(commands=commands)


async def main(settings: Settings) -> None:
    await db.main(settings=settings)

    dp = Dispatcher()

    dp.update.middleware(MyI18nMiddleware(i18n=i18n))

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    async def send_message(
        chat_id: ChatId, message: str, message_thread_id: Optional[int] = None
    ):
        return await bot.send_message(
            chat_id=chat_id, text=message, message_thread_id=message_thread_id
        )

    dp.update.outer_middleware(GroupCommandFilterMiddleware())

    scheduler = init_scheduler(settings=settings)
    await restore_scheduled_jobs(scheduler=scheduler, send_message=send_message)

    router = handlers.make_router(
        scheduler=scheduler, send_message=send_message, bot=bot
    )

    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)

    await set_default_commands(bot=bot)
    await update_recurring_message(
        bot=bot,
        scheduler=scheduler,
        send_message=send_message
    )

    await dp.start_polling(bot)
