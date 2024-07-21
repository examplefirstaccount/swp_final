from textwrap import dedent
from typing import List, Optional, Tuple

from aiogram import html
from aiogram.utils import markdown as fmt

from .commands import bot_command_descriptions, bot_command_names
from .i18n import _
from .intervals import (DEFAULT_EDITING_INTERVAL, Interval,
                        InvalidIntervalException, InvalidTimeFormatException)


def bot_intro():
    return _(
        """
        The bot can help you conduct daily (or at least regular) meetings.

        You can control me by sending these commands:
        """
    ).strip()


def make_help_message() -> str:
    command_names = bot_command_names
    command_descriptions = bot_command_descriptions()

    return dedent(
        f"""
        {bot_intro()}
        
        {html.bold(_("Global commands"))}
        /{command_names.start} - {command_descriptions.start}
        /{command_names.help} - {command_descriptions.help}
        /{command_names.set_language} - {command_descriptions.set_language}
        
        {html.bold(_("Team settings commands"))}
        /{command_names.set_meetings_time} - {command_descriptions.set_meetings_time}
        /{command_names.add_recurring_message} - {command_descriptions.add_recurring_message}
        
        {html.bold(_("Personal settings commands"))}
        /{command_names.set_reminder_period} - {command_descriptions.set_reminder_period}
        /{command_names.set_working_hours} - {command_descriptions.set_working_hours}
        /{command_names.join} - {command_descriptions.join}
        /{command_names.skip} - {command_descriptions.skip}
        
        {html.bold(_("Chat information commands"))}
        /{command_names.get_chat_state} - {command_descriptions.get_chat_state}
        /{command_names.reset} - {command_descriptions.reset}
        /{command_names.get_report} - {command_descriptions.get_report}
        """
    ).strip()


def make_daily_messages(usernames: str, locale: Optional[str] = None) -> List[str]:
    return [
        _("What did you do last working day? {usernames}", locale=locale).format(usernames=usernames),
        _("What will you do today? {usernames}", locale=locale).format(usernames=usernames),
        _("What (if anything) is blocking your progress? {usernames}", locale=locale).format(
            usernames=usernames
        ),
    ]


def make_interval_validation_message(
    interval_str: str, tz: str, shift: int
) -> Tuple[bool, str]:
    try:
        interval = Interval.from_string(interval_str=interval_str, tz=tz, shift=shift)
        msg = _("Successfully parsed interval: {interval}").format(interval=interval)
        return True, msg
    except InvalidTimeFormatException as e:
        msg = _("Invalid time format for '{time}'. {msg}\n").format(
            time=e.time_str, msg=e.message
        )
        return False, msg
    except InvalidIntervalException as e:
        msg = _("{msg} (start: {start}, end: {end}).\n").format(
            msg=e.message, start=e.start_time, end=e.end_time
        )
        return False, msg
    except Exception as e:
        msg = _("An unexpected error occurred. {error}").format(error=str(e))
        return False, msg


def make_interval_editing_instruction() -> str:
    instruction_text = _("Send a new interval in the 'hh:mm - hh:mm' format.")
    example_text = _("Example: ") + fmt.hcode(DEFAULT_EDITING_INTERVAL)
    tip_text = _("Tip: press the interval in the example to copy and then edit this interval.")

    text = fmt.text(
        instruction_text,
        example_text,
        tip_text,
        sep="\n\n",
    )
    return text


def make_interval_editing_error(error_msg: str) -> str:
    again_text = _("Press 'Enter again' to enter the interval again.")
    cancel_text = _("Press 'Cancel' to cancel editing this interval.")

    text = fmt.text(error_msg, again_text, cancel_text, sep="\n")
    return text


def make_chat_state_messages(json_string: str, max_length=4096) -> List[str]:
    """Split the json string into chunks of max length 4096 characters (Telegram API limit).

    Args:
        json_string: The chat state in formatted as json string.
        max_length: The max length of one chunk. By default, 4096.

    Returns:
        List[str]: List of string chunks formatted as json code.
    """
    chunks = []

    for i in range(0, len(json_string), max_length):
        chunk = json_string[i:i+max_length]
        chunk_fmt = dedent(f"""<pre><code class="language-json">{chunk}</code></pre>""")
        chunks.append(chunk_fmt)

    return chunks
