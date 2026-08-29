import datetime

from sunsynk.resource import to_bool, to_datetime, to_float, to_int


def test_to_float():
    assert to_float('12.2') == 12.2
    assert to_float(5) == 5.0
    assert to_float(None) is None
    assert to_float('') is None
    assert to_float('abc') is None


def test_to_int():
    assert to_int('2') == 2
    assert to_int(3.0) == 3
    assert to_int(None) is None
    assert to_int('') is None
    assert to_int('abc') is None


def test_to_bool():
    assert to_bool(True) is True
    assert to_bool('false') is False
    assert to_bool('1') is True
    assert to_bool(0) is False
    assert to_bool(None) is None
    assert to_bool('') is None
    assert to_bool('maybe') is None


def test_to_datetime():
    utc = to_datetime('2023-01-07T16:50:17Z')
    assert utc == datetime.datetime(2023, 1, 7, 16, 50, 17, tzinfo=datetime.timezone.utc)
    naive = to_datetime('2023-01-07 16:50:17')
    assert naive.tzinfo == datetime.timezone.utc
    assert naive.hour == 16
    assert to_datetime('2023-01-07T16:50:17.500+02:00').utcoffset() == datetime.timedelta(hours=2)
    assert to_datetime('2026-07-01').day == 1
    assert to_datetime(None) is None
    assert to_datetime('') is None
    assert to_datetime('not a date') is None
