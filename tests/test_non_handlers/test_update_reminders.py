import pytest
from unittest.mock import AsyncMock

from bot.reminder import update_reminders
from bot.state import ChatState, save_state
from tests.utils import TEST_USER, TEST_USER_2, register_2_users, set_meeting_time, set_reminder_period_2_users


@pytest.mark.asyncio
async def test_update_reminders(chat_state_2_users: ChatState):
    """
    Tests the update reminders function with various users and chat_state configurations.
    The main criteria - number of calls to scheduler.
    """
    bot = AsyncMock()
    username = TEST_USER.username
    username_2 = TEST_USER_2.username
    scheduler = AsyncMock()
    send_message = AsyncMock()

    # Call without username should not change anything
    await update_reminders(bot=bot, username=None, scheduler=scheduler, send_message=send_message)
    scheduler.assert_not_called()

    # Call without registered users should not change anything
    await update_reminders(bot=bot, username=username, scheduler=scheduler, send_message=send_message)
    scheduler.assert_not_called()

    await register_2_users()

    # Calls without set meeting time and set reminder periods should not change anything
    await update_reminders(bot=bot, username=username, scheduler=scheduler, send_message=send_message)
    scheduler.assert_not_called()
    await update_reminders(bot=bot, username=username_2, scheduler=scheduler, send_message=send_message)
    scheduler.assert_not_called()

    await set_meeting_time(chat_state_2_users)

    # Calls with set meeting time but without set reminder periods should not change anything
    await update_reminders(bot=bot, username=username, scheduler=scheduler, send_message=send_message)
    scheduler.assert_not_called()
    await update_reminders(bot=bot, username=username_2, scheduler=scheduler, send_message=send_message)
    scheduler.assert_not_called()

    chat_state_2_users.users[TEST_USER.username].reminder_period = 1
    await save_state(chat_state_2_users)

    # 1 user set reminder period - 1 call to scheduler
    await update_reminders(bot=bot, username=username, scheduler=scheduler, send_message=send_message)
    await update_reminders(bot=bot, username=username_2, scheduler=scheduler, send_message=send_message)
    assert scheduler.add_job.call_count == 1
    scheduler.reset_mock(return_value=True, side_effect=True)

    await set_reminder_period_2_users(chat_state_2_users)

    # 2 user set reminder period - 2 calls to scheduler
    await update_reminders(bot=bot, username=username, scheduler=scheduler, send_message=send_message)
    await update_reminders(bot=bot, username=username_2, scheduler=scheduler, send_message=send_message)
    assert scheduler.add_job.call_count == 2
