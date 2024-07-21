from pydantic import BaseModel

from .i18n import _


class BotCommands(BaseModel):
    # global commands
    start: str
    help: str
    set_language: str
    stop: str
    cancel: str
    # team settings
    set_up_meetings: str
    set_meetings_time_zone: str
    set_meetings_time: str
    set_meetings_days: str
    add_recurring_message: str
    # personal settings
    join: str
    skip: str
    set_working_hours: str
    set_reminder_period: str
    join_today: str
    skip_today: str
    schedule_personal_vacation: str
    unschedule_personal_vacation: str
    # info
    get_chat_state: str
    get_report: str
    reset: str


class BotCommandNames(BotCommands):
    pass


bot_command_names = BotCommandNames(
    # global commands
    start="start",
    help="help",
    set_language="set_language",
    stop="stop",
    cancel="cancel",
    # team settings
    set_up_meetings="set_up_meetings",
    set_meetings_time_zone="set_meetings_time_zone",
    set_meetings_time="set_meetings_time",
    set_meetings_days="set_meetings_days",
    add_recurring_message="add_recurring_message",
    # personal settings
    join="join",
    skip="skip",
    set_working_hours="set_working_hours",
    set_reminder_period="set_reminder_period",
    join_today="join_today",
    skip_today="skip_today",
    schedule_personal_vacation="schedule_personal_vacation",
    unschedule_personal_vacation="unschedule_personal_vacation",
    # info
    get_chat_state="get_chat_state",
    get_report="get_report",
    reset="reset",
)


class BotCommandDescriptions(BotCommands):
    pass


def bot_command_descriptions() -> BotCommandDescriptions:
    return BotCommandDescriptions(
        # global commands
        start=_("Enable the bot."),
        help=_("Get a help message."),
        set_language=_("Set the bot language."),
        stop=_("Disable the bot."),
        cancel=_("Cancel the current operation with the bot."),
        # team settings
        set_up_meetings=_("Set up daily meetings."),
        # TODO use the time zone
        set_meetings_time_zone=_("Set meetings time zone."),
        set_meetings_time=_("Set meetings time."),
        set_meetings_days=_("Set meetings days."),
        add_recurring_message=_("Add recurring message."),
        # personal settings
        join=_("Join meetings."),
        skip=_("Skip meetings."),
        set_working_hours=_("Set working hours."),
        set_reminder_period=_(
            "Set the period of reminders about unanswered questions."
        ),
        join_today=_("Join only today's meeting."),
        skip_today=_("Skip only today's meeting."),
        schedule_personal_vacation=_("Schedule a personal vacation."),
        unschedule_personal_vacation=_("Unschedule the personal vacation."),
        # info settings
        get_chat_state=_("Get the chat state stored by the bot."),
        reset=_("Reset the chat state."),
        get_report=_("Get the report."),
    )
