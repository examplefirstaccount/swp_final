from datetime import date

ENCODING = "utf-8"


class AppCommands:
    print_bot_message = "print-bot-message"
    print_meeting_messages = "print-meeting-messages"
    start = "start"


jobstore = "bot_jobs"

time_url = "https://time.lol"

iso8601 = "ISO 8601"

sample_time = date.today().strftime("%Y-%m-%d") + "T10:00:00+03:00"

default_time_zone = "Europe/Moscow"

days_array = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

report_tag = "daily_report"

title_max_length = 120
