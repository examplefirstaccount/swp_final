from typing import Annotated, Optional

import pymongo
from beanie import Indexed

from bot.chat import ChatId


def make_recurring_job_id(title: str, meeting_chat_id: Annotated[ChatId, Indexed(index_type=pymongo.ASCENDING)], meeting_topic_id: Optional[int]):
    if meeting_topic_id:
        return f"recurring_message_{title}_for_{meeting_chat_id}_{meeting_topic_id}"
    else:
        return f"recurring_message_{title}_for_{meeting_chat_id}"
