from bot.reminder import make_job_id


def test_make_job_id():
    """
    Tests the accuracy of the generation of scheduler id.
    """
    assert make_job_id(user_chat_id=1, meeting_chat_id=2, meeting_topic_id=3) == "1_reminder_for_2_3"
    assert make_job_id(user_chat_id=1, meeting_chat_id=2, meeting_topic_id=None) == "1_reminder_for_2"
