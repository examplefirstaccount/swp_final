from dataclasses import dataclass
from datetime import datetime
from textwrap import dedent
from typing import List

from aiogram import html
from .i18n import _

from .commands import bot_command_descriptions, bot_command_names
from .constants import day_of_week_pretty
from .language import Language


def bot_intro():
    return _(
        """
        I can help you conduct daily (or at least regular) meetings.

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
        /{command_names.set_personal_meetings_days} - {command_descriptions.set_personal_meetings_days}
        /{command_names.set_reminder_period} - {command_descriptions.set_reminder_period}
        /{command_names.join} - {command_descriptions.join}
        /{command_names.skip} - {command_descriptions.skip}
        
        {html.bold(_("Chat information commands"))}
        /{command_names.get_chat_state} - {command_descriptions.get_chat_state}
        /{command_names.reset} - {command_descriptions.reset}
        /{command_names.get_report} - {command_descriptions.get_report}
        """
    ).strip()


def make_daily_messages(usernames: str) -> List[str]:
    return [
        _("What did you do last working day? {usernames}").format(usernames=usernames),
        _("What will you do today? {usernames}").format(usernames=usernames),
        _("What (if anything) is blocking your progress? {usernames}").format(
            usernames=usernames
        ),
    ]
