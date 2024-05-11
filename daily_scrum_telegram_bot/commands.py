from pydantic import BaseModel
from .language import Language, language_en


class BotCommands(BaseModel):
    start: str
    help: str
    set_meeting_time: str
    subscribe: str
    unsubscribe: str
    get_subscribers: str


class BotCommandNames(BotCommands):
    pass


bot_command_names = BotCommandNames(
    start="start",
    help="help",
    set_meeting_time="set_meeting_time",
    subscribe="subscribe",
    unsubscribe="unsubscribe",
    get_subscribers="get_subscribers",
)


class BotCommandDescriptions(BotCommands):
    pass


bot_command_descriptions: dict[Language, BotCommandDescriptions] = {
    language_en: BotCommandDescriptions(
        start="enable me",
        help="get this help message",
        set_meeting_time="set the meeting start time and date",
        subscribe="subscribe so that I send you messages",
        unsubscribe="unsubscribe so that I don't send you messages",
        get_subscribers="get a list of subscribed users",
    ),
}
