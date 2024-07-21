from bot.reminder import get_message_link
from tests.utils import TEST_CHAT


def test_get_message_link():
    """
    Tests the accuracy of the generation of tg links.
    """
    msg_id = 1
    assert get_message_link(chat_id=TEST_CHAT.id,
                            message_id=msg_id,
                            thread_id=None,
                            chat_type="supergroup") == "https://t.me/c/%s/%s" % (str(TEST_CHAT.id)[4:], msg_id)

    assert get_message_link(chat_id=TEST_CHAT.id,
                            message_id=msg_id,
                            thread_id=1,
                            chat_type="supergroup") == "https://t.me/c/%s/%s/%s" % (str(TEST_CHAT.id)[4:], msg_id, 1)

    assert get_message_link(chat_id=TEST_CHAT.id,
                            message_id=msg_id,
                            thread_id=None,
                            chat_type="private") is None

    assert get_message_link(chat_id=TEST_CHAT.id,
                            message_id=msg_id,
                            thread_id=None,
                            chat_type="group") is None

    assert get_message_link(chat_id=TEST_CHAT.id,
                            message_id=msg_id,
                            thread_id=None,
                            chat_type="channel") is None

    assert get_message_link(chat_id=TEST_CHAT.id,
                            message_id=msg_id,
                            thread_id=1,
                            chat_type="channel") is None
