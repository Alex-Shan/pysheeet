"""Tests for datetime operations."""

import calendar
import time
from datetime import date, datetime, time as dt_time, timedelta, timezone


def test_current_datetime():
    """Get current date and time."""
    now = datetime.now()
    assert isinstance(now, datetime)

    utc_now = datetime.now(timezone.utc)
    assert utc_now.tzinfo == timezone.utc

    today = date.today()
    assert isinstance(today, date)


def test_create_datetime():
    """Create datetime objects."""
    dt = datetime(2024, 1, 15, 10, 30, 45)
    assert dt.year == 2024
    assert dt.month == 1
    assert dt.day == 15
    assert dt.hour == 10

    d = date(2024, 1, 15)
    t = dt_time(10, 30, 45)
    combined = datetime.combine(d, t)
    assert combined == dt


def test_timestamp_conversion():
    """Convert between timestamps and datetime."""
    ts = time.time()
    dt = datetime.fromtimestamp(ts)
    ts_back = dt.timestamp()
    assert abs(ts - ts_back) < 0.001

    dt_utc = datetime.fromtimestamp(ts, tz=timezone.utc)
    assert dt_utc.tzinfo == timezone.utc


def test_strftime_formatting():
    """Format datetime as string."""
    dt = datetime(2024, 1, 15, 14, 30, 45)

    assert dt.strftime("%Y-%m-%d") == "2024-01-15"
    assert dt.strftime("%d/%m/%Y") == "15/01/2024"
    assert dt.strftime("%Y-%m-%d %H:%M:%S") == "2024-01-15 14:30:45"
    assert dt.strftime("%Y%m%d_%H%M%S") == "20240115_143045"
    assert dt.isoformat() == "2024-01-15T14:30:45"


def test_strptime_parsing():
    """Parse string to datetime."""
    dt1 = datetime.strptime("2024-01-15", "%Y-%m-%d")
    assert dt1.year == 2024 and dt1.month == 1 and dt1.day == 15

    dt2 = datetime.strptime("15/01/2024", "%d/%m/%Y")
    assert dt2.day == 15

    dt3 = datetime.fromisoformat("2024-01-15T14:30:45")
    assert dt3.hour == 14 and dt3.minute == 30


def test_timedelta_arithmetic():
    """Date arithmetic with timedelta."""
    now = datetime(2024, 1, 15, 12, 0, 0)

    tomorrow = now + timedelta(days=1)
    assert tomorrow.day == 16

    yesterday = now - timedelta(days=1)
    assert yesterday.day == 14

    in_2_hours = now + timedelta(hours=2)
    assert in_2_hours.hour == 14

    date1 = datetime(2024, 1, 1)
    date2 = datetime(2024, 12, 31)
    diff = date2 - date1
    assert diff.days == 365


def test_timezone_operations():
    """Work with timezones."""
    utc = timezone.utc
    dt_utc = datetime(2024, 1, 15, 12, 0, 0, tzinfo=utc)
    assert dt_utc.tzinfo == utc

    pst = timezone(timedelta(hours=-8))
    dt_pst = dt_utc.astimezone(pst)
    assert dt_pst.hour == 4  # 12:00 UTC = 04:00 PST

    naive = datetime(2024, 1, 15, 10, 30)
    aware = naive.replace(tzinfo=utc)
    assert aware.tzinfo == utc


def test_date_comparison():
    """Compare datetime objects."""
    dt1 = datetime(2024, 1, 15, 10, 0)
    dt2 = datetime(2024, 1, 15, 14, 0)
    dt3 = datetime(2024, 1, 16, 10, 0)

    assert dt1 < dt2
    assert dt3 > dt2
    assert dt1 != dt2

    start = datetime(2024, 1, 1)
    end = datetime(2024, 12, 31)
    check = datetime(2024, 6, 15)
    assert start <= check <= end


def test_weekday_operations():
    """Work with weekdays and weeks."""
    dt = datetime(2024, 1, 15)  # 周一

    assert dt.weekday() == 0  # Monday = 0
    assert dt.isoweekday() == 1  # Monday = 1 (ISO)

    year, week, weekday = dt.isocalendar()
    assert year == 2024 and week == 3 and weekday == 1

    start_of_week = dt - timedelta(days=dt.weekday())
    assert start_of_week.weekday() == 0


def test_start_end_of_day():
    """Get start and end of day."""
    dt = datetime(2024, 1, 15, 14, 30, 45)

    start_of_day = datetime.combine(dt.date(), dt_time.min)
    assert start_of_day.hour == 0 and start_of_day.minute == 0

    end_of_day = datetime.combine(dt.date(), dt_time.max)
    assert end_of_day.hour == 23 and end_of_day.minute == 59


def test_start_end_of_month():
    """Get start and end of month."""
    dt = datetime(2024, 1, 15, 14, 30, 45)

    start_of_month = dt.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    assert start_of_month.day == 1

    last_day = calendar.monthrange(dt.year, dt.month)[1]
    end_of_month = dt.replace(day=last_day)
    assert end_of_month.day == 31


def test_calendar_operations():
    """Calendar module operations."""
    assert calendar.isleap(2024) is True
    assert calendar.isleap(2023) is False

    weekday, days = calendar.monthrange(2024, 2)
    assert days == 29  # 闰年


def test_date_range():
    """Generate date ranges."""

    def date_range(start, end, step=timedelta(days=1)):
        current = start
        while current <= end:
            yield current
            current += step

    start = date(2024, 1, 1)
    end = date(2024, 1, 7)
    dates = list(date_range(start, end))
    assert len(dates) == 7
    assert dates[0] == start
    assert dates[-1] == end


def test_age_calculation():
    """Calculate age from birthdate."""

    def calculate_age(birthdate, reference_date=None):
        if reference_date is None:
            reference_date = date.today()
        age = reference_date.year - birthdate.year
        if (reference_date.month, reference_date.day) < (
            birthdate.month,
            birthdate.day,
        ):
            age -= 1
        return age

    birthdate = date(1990, 6, 15)
    reference = date(2024, 1, 15)
    assert calculate_age(birthdate, reference) == 33

    reference_after = date(2024, 7, 1)
    assert calculate_age(birthdate, reference_after) == 34


def test_time_ago():
    """Human readable time differences."""

    def time_ago(dt, now=None):
        if now is None:
            now = datetime.now()
        diff = now - dt
        seconds = diff.total_seconds()
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(seconds // 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"

    now = datetime(2024, 1, 15, 12, 0, 0)
    assert time_ago(now - timedelta(seconds=30), now) == "just now"
    assert time_ago(now - timedelta(minutes=5), now) == "5 minutes ago"
    assert time_ago(now - timedelta(hours=2), now) == "2 hours ago"
    assert time_ago(now - timedelta(days=3), now) == "3 days ago"


def test_business_days():
    """Generate business days (skip weekends)."""

    def business_days(start, end):
        current = start
        while current <= end:
            if current.weekday() < 5:
                yield current
            current += timedelta(days=1)

    start = date(2024, 1, 15)  # 周一
    end = date(2024, 1, 21)  # 星期日
    bdays = list(business_days(start, end))
    assert len(bdays) == 5  # 周一至周五
    assert all(d.weekday() < 5 for d in bdays)
