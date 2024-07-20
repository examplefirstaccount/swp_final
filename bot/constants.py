from aiogram import html

ENCODING = "utf-8"


class AppCommands:
    print_bot_message = "print-bot-message"
    print_meeting_messages = "print-meeting-messages"
    start = "start"


jobstore = "bot_jobs"

time_url = "https://time.lol"

iso8601 = "ISO 8601"

datetime_time_format = "%H:%M %Y-%m-%d"

day_of_week = "0-6"

day_of_week_pretty = "Monday - Friday"

day_of_week_to_num = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
    "понедельник": 0,
    "вторник": 1,
    "среда": 2,
    "четверг": 3,
    "пятница": 4,
    "суббота": 5,
    "воскресенье": 6,
}

sample_time = "2024-06-03T14:00:00+03:00"

report_tag = "daily_report"

title_max_length = 120