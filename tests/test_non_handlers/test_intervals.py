from datetime import datetime
from zoneinfo import ZoneInfo

# import pytest

from bot.intervals import Interval, IMMUTABLE_DATE

# TODO: change commented tests according to the current intervals.py
# def test_zone_must_be_valid():
#     """
#     Check correctness of the validation of the time zone.
#     """
#     a = Interval.zone_must_be_valid("Us/eastern")
#     assert a == "Us/eastern"
#
#     a = Interval.zone_must_be_valid("Europe/Moscow")
#     assert a == "Europe/Moscow"
#
#     with pytest.raises(ValueError):
#         b = Interval.zone_must_be_valid("somezone")


# def test_from_string():
#     """
#     Checks correctness of the creation of an interval.
#     """
#     tz_1 = "UTC"
#     tz_2 = "Europe/Moscow"
#     time_start_1 = datetime.strptime("1:00", "%H:%M").time()
#     time_end_1 = datetime.strptime("11:20", "%H:%M").time()
#
#     datetime_start_1 = datetime.combine(IMMUTABLE_DATE, time_start_1, ZoneInfo(tz_1))
#     datetime_end_1 = datetime.combine(IMMUTABLE_DATE, time_end_1, ZoneInfo(tz_1))
#
#     datetime_start_2 = datetime.combine(IMMUTABLE_DATE, time_start_1, ZoneInfo(tz_2))
#     datetime_end_2 = datetime.combine(IMMUTABLE_DATE, time_end_1, ZoneInfo(tz_2))
#
#     a = Interval.from_string("1:00 - 11:20", tz_1)
#     assert a.start_time_utc == datetime_start_1
#     assert a.end_time_utc == datetime_end_1
#     assert a.tz == tz_1
#
#     # Start time should be less than end one
#     with pytest.raises(InvalidIntervalException):
#         a = Interval.from_string("11:20 - 1:00", tz_1)
#
#     # Skip time zone
#     a = Interval.from_string("1:00 - 11:20")
#     assert a.start_time_utc == datetime_start_1
#     assert a.end_time_utc == datetime_end_1
#     assert a.tz == tz_1
#
#     # Other time zone
#     a = Interval.from_string("1:00 - 11:20", tz_2)
#     assert a.start_time_utc == datetime_start_2
#     assert a.end_time_utc == datetime_end_2
#     assert a.tz == tz_2
#
#     # Other time format
#     a = Interval.from_string("1.00 - 11.20", tz_2)
#     assert a.start_time_utc == datetime_start_2
#     assert a.end_time_utc == datetime_end_2
#     assert a.tz == tz_2
#

def test_convert_to_utc():
    tz_1 = "Europe/Moscow"
    time_start_1 = datetime.strptime("1:00", "%H:%M").time()
    datetime_1 = datetime.combine(IMMUTABLE_DATE, time_start_1, ZoneInfo(tz_1))

    assert datetime_1.astimezone(ZoneInfo("UTC")) == Interval.convert_to_utc(datetime_1)


# def test_parse_time():
#     time_1 = "01:00"
#     time_2 = "23.12"
#     wrong_time = "24:99"
#
#     assert datetime.strptime(time_1, "%H:%M").time() == Interval.parse_time(time_1)
#     assert datetime.strptime(time_2, "%H.%M").time() == Interval.parse_time(time_2)
#
#     with pytest.raises(InvalidTimeFormatException):
#         Interval.parse_time(wrong_time)


def test_overlaps_with():
    interval_1 = Interval.from_string("1:00 - 4:00", tz="UTC")
    # Should overlap with 1
    interval_2 = Interval.from_string("4:00 - 5:00", tz="UTC")
    interval_3 = Interval.from_string("3:00 - 5:00", tz="UTC")
    interval_4 = Interval.from_string("2:00 - 3:00", tz="UTC")

    # Should not overlap with 1
    interval_5 = Interval.from_string("6:00 - 7:00", tz="UTC")

    test_func = Interval.overlaps_with
    assert test_func(interval_1, interval_1) is True
    assert test_func(interval_1, interval_2) is False
    assert test_func(interval_1, interval_3) is True
    assert test_func(interval_1, interval_4) is True
    assert test_func(interval_1, interval_5) is False


# def test_merge_intervals():
#     # TODO several same intervals
#     interval_1 = Interval.from_string("1:00 - 4:00", tz="UTC")
#     interval_2 = Interval.from_string("1:20 - 4:00", tz="UTC")
#     interval_3 = Interval.from_string("2:00 - 3:00", tz="UTC")
#     interval_4 = Interval.from_string("4:00 - 5:00", tz="UTC")
#     interval_5 = Interval.from_string("7:00 - 8:00", tz="UTC")
#
#     interval_6 = Interval.from_string("1:00 - 5:00", tz="UTC")
#
#     interval_7 = Interval.from_string("2:00 - 3:00", tz="Europe/Moscow")
#
#     arr = [interval_1, interval_2, interval_3, interval_4, interval_5]
#     merged = [interval_6, interval_5]
#
#     assert Interval.merge_intervals(arr) == merged
#
#     # Different time zones
#     with pytest.raises(ValueError):
#         Interval.merge_intervals(arr + [interval_7])
#
#     # Empty
#     # TODO output should be empty
#     with pytest.raises(ValueError):
#         Interval.merge_intervals([])
