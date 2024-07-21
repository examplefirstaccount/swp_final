from datetime import datetime

from aiogram.types import User, Chat

from bot.constants import sample_time
from bot.state import create_user_pm, ChatState, save_state

TEST_USER = User(id=11111111111111, is_bot=False, first_name="Test",
                 last_name="User", username="test", language_code="en-US", is_premium=False)

TEST_USER_2 = User(id=2222222222222, is_bot=False, first_name="Test_2",
                   last_name="User_2", username="test_2", language_code="en-US", is_premium=False)

TEST_CHAT = Chat(id=33333333333333, type="supergroup", is_forum=True, title="Test chat", description="Test chat")

# TEST_USER's chat
TEST_CHAT_PRIVATE = Chat(id=44444444444444444, type="private", title="Test chat", description="Test chat")

# TEST_USER_2's chat
TEST_CHAT_PRIVATE_2 = Chat(id=5555555555555, type="private", title="Test chat", description="Test chat")


async def register_2_users():
    await create_user_pm(TEST_USER.username, TEST_CHAT_PRIVATE.id)
    await create_user_pm(TEST_USER_2.username, TEST_CHAT_PRIVATE_2.id)


async def set_reminder_period_2_users(chat_state: ChatState):
    chat_state.users[TEST_USER.username].reminder_period = 1
    chat_state.users[TEST_USER_2.username].reminder_period = 1
    await save_state(chat_state)


async def set_meeting_time(chat_state: ChatState):
    chat_state.meeting_time = datetime.fromisoformat(sample_time)
    await save_state(chat_state)