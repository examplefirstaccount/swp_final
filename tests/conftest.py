import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from aiogram import Dispatcher

from bot.state import ChatState, UserPM, create_state, get_user, save_state

from tests.utils import TEST_CHAT, TEST_USER, TEST_USER_2


# @pytest.fixture()
# def bot():
#     return MockedBot()


@pytest_asyncio.fixture()
async def dispatcher():
    dp = Dispatcher()
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()


@pytest_asyncio.fixture(autouse=True)
async def mock_db():
    """
    Automatic fixture. Create new mongodb instance for each test.
    """
    client = AsyncMongoMockClient()
    await init_beanie(document_models=[ChatState, UserPM], database=client.get_database(name="db"))


@pytest_asyncio.fixture()
async def chat_state_2_users(mock_db) -> ChatState:
    """
    Create new ChatState with 2 test users.
    Does not register users (they do not /start bot in PM).
    Returns:
        ChatState: The chat state instance created.
    """
    chat_state = await create_state(TEST_CHAT.id, topic_id=1)
    await get_user(chat_state, TEST_USER.username)
    await get_user(chat_state, TEST_USER_2.username)
    await save_state(chat_state)
    yield chat_state

# @pytest.fixture(scope="session")
# def event_loop():
#     return asyncio.get_event_loop()
