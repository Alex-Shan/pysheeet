.. meta::
    :description lang=zh_CN: Python 日期时间教程，涵盖时间戳、日期格式化、解析、时区、timedelta 计算、日历操作和时间算术
    :keywords: Python, Python3, datetime, date, time, timestamp, timezone, timedelta, strftime, strptime, calendar, UTC, ISO 8601, dateutil, zoneinfo

============================
日期时间（Datetime）
============================

:Source: `src/basic/datetime_.py <https://github.com/crazyguitar/pysheeet/blob/master/src/basic/datetime_.py>`_

.. contents:: 目录（Table of Contents）
    :backlinks: none

介绍（Introduction）
--------------------------------

Python 的 ``datetime`` module 提供了 classes 用于操作日期和时间。 module 包括用于日历日期的 ``date`` 、用于时钟时间的 ``time`` 、用于组合日期和时间的 ``datetime`` 、用于持续时间的 ``timedelta`` 以及用于 UTC 偏移量的 ``timezone`` 。 Python 3.9+ 还包括用于 IANA 时区支持的 ``zoneinfo`` 。了解这些 classes 对于日志记录、调度、数据分析以及任何处理时态数据的应用程序至关重要。

当前日期和时间（Current Date and Time）
------------------------------------------------------------

获取当前日期和时间是最常见的操作之一。使用 ``datetime.now()`` 表示当地时间，或使用 ``datetime.utcnow()`` 表示 UTC。在 Python 3.11+ 中，优先使用 ``datetime.now(timezone.utc)`` 而不是 ``utcnow()`` （已弃用）。

.. code-block:: python

    from datetime import datetime, date, time, timezone

    # 当前本地日期时间
    now = datetime.now()
    print(now)  # 2024-01-15 10:30:45.123456

    # 当前 UTC 日期时间（Python 3.11+ 首选）
    utc_now = datetime.now(timezone.utc)
    print(utc_now)  # 2024-01-15 02:30:45.123456+00:00

    # 仅当前日期
    today = date.today()
    print(today)  # 2024-01-15

    # 仅当前时间
    current_time = datetime.now().time()
    print(current_time)  # 10:30:45.123456

创建日期时间对象（Creating Datetime Objects）
----------------------------------------------------------------------

您可以通过指定年、月、日以及可选的小时、分钟、秒和微秒来创建日期时间 objects。 ``date`` 和 ``time`` classes 对于仅日期或仅时间 values 的工作方式类似。

.. code-block:: python

    from datetime import datetime, date, time

    # 创建特定日期时间
    dt = datetime(2024, 1, 15, 10, 30, 45)
    print(dt)  # 2024-01-15 10:30:45

    # 仅创建日期
    d = date(2024, 1, 15)
    print(d)  # 2024-01-15

    # 仅创建时间
    t = time(10, 30, 45)
    print(t)  # 10:30:45

    # 合并日期和时间
    combined = datetime.combine(d, t)
    print(combined)  # 2024-01-15 10:30:45

    # 从日期时间获取日期或时间
    print(dt.date())  # 2024-01-15
    print(dt.time())  # 10:30:45

时间戳（Timestamps）
------------------------------

Unix 时间戳表示自 1970 年 1 月 1 日（Unix 纪元）以来的秒数。使用 APIs、数据库和日志文件时，时间戳和日期时间 objects 之间的转换很常见。

.. code-block:: python

    import time
    from datetime import datetime, timezone

    # 当前时间戳
    ts = time.time()
    print(ts)  # 1705312245.123456

    # 时间戳到日期时间（当地时间）
    dt = datetime.fromtimestamp(ts)
    print(dt)  # 2024-01-15 10:30:45.123456

    # 时间戳到日期时间 (UTC)
    dt_utc = datetime.fromtimestamp(ts, tz=timezone.utc)
    print(dt_utc)  # 2024-01-15 02:30:45.123456+00:00

    # 日期时间到时间戳
    ts_back = dt.timestamp()
    print(ts_back)  # 1705312245.123456

    # 毫秒时间戳（常见于JavaScript/APIs）
    ts_ms = int(ts * 1000)
    print(ts_ms)  # 1705312245123

格式化日期 (strftime)（Formatting Dates (strftime)）
------------------------------------------------------------------------------------------

``strftime()`` method 使用格式代码将日期时间 objects 格式化为 strings。这对于向用户显示日期、生成文件名或格式化 APIs 的数据至关重要。

.. code-block:: python

    from datetime import datetime

    dt = datetime(2024, 1, 15, 14, 30, 45)

    # 常见格式
    print(dt.strftime("%Y-%m-%d"))           # 2024-01-15
    print(dt.strftime("%d/%m/%Y"))           # 15/01/2024
    print(dt.strftime("%B %d, %Y"))          # 2024 年 1 月 15 日
    print(dt.strftime("%Y-%m-%d %H:%M:%S"))  # 2024-01-15 14:30:45
    print(dt.strftime("%I:%M %p"))           # 02:30 PM
    print(dt.strftime("%A, %B %d"))          # 1 月 15 日星期一

    # ISO 8601格式
    print(dt.isoformat())                    # 2024-01-15T14:30:45

    # 对于文件名（无特殊字符）
    print(dt.strftime("%Y%m%d_%H%M%S"))      # 20240115_143045

常用格式代码：

- ``%Y`` - 4 位数年份 (2024)
- ``%m`` - 月份以零填充数字 (01-12)
- ``%d`` - 以零填充的数字形式的日 (01-31)
- ``%H`` - 小时 24 小时格式 (00-23)
- ``%I`` - 小时 12 小时格式 (01-12)
- ``%M`` - 分钟 (00-59)
- ``%S`` - 第二个 (00-59)
- ``%p`` - AM/PM
- ``%A`` - 工作日全名
- ``%B`` - 月份全名
- ``%z`` - UTC 偏移量 (+0000)
- ``%Z`` - 时区名称

解析日期 (strptime)（Parsing Dates (strptime)）
----------------------------------------------------------------------------------

``strptime()`` method 将 strings 解析为日期时间 objects。格式 string 必须与输入完全匹配。这通常在从文件、用户输入或 APIs 读取日期时使用。

.. code-block:: python

    from datetime import datetime

    # 解析各种格式
    dt1 = datetime.strptime("2024-01-15", "%Y-%m-%d")
    dt2 = datetime.strptime("15/01/2024", "%d/%m/%Y")
    dt3 = datetime.strptime("January 15, 2024", "%B %d, %Y")
    dt4 = datetime.strptime("2024-01-15 14:30:45", "%Y-%m-%d %H:%M:%S")

    print(dt1)  # 2024-01-15 00:00:00
    print(dt4)  # 2024-01-15 14:30:45

    # 解析ISO 8601格式
    dt5 = datetime.fromisoformat("2024-01-15T14:30:45")
    print(dt5)  # 2024-01-15 14:30:45

    # 使用时区解析 (Python 3.11+)
    dt6 = datetime.fromisoformat("2024-01-15T14:30:45+00:00")
    print(dt6)  # 2024-01-15 14:30:45+00:00

使用 timedelta 进行日期算术（Date Arithmetic with timedelta）
------------------------------------------------------------------------------------------------------

``timedelta`` class 表示持续时间 - 两个日期或时间之间的差异。使用它从日期时间 objects 中添加或减去时间，或计算两个日期之间的差异。

.. code-block:: python

    from datetime import datetime, timedelta

    now = datetime.now()

    # 添加时间
    tomorrow = now + timedelta(days=1)
    next_week = now + timedelta(weeks=1)
    in_2_hours = now + timedelta(hours=2)
    in_90_minutes = now + timedelta(minutes=90)

    # 减去时间
    yesterday = now - timedelta(days=1)
    last_month = now - timedelta(days=30)

    # 合并单位
    future = now + timedelta(days=5, hours=3, minutes=30)

    # 计算日期之间的差异
    date1 = datetime(2024, 1, 1)
    date2 = datetime(2024, 12, 31)
    diff = date2 - date1
    print(diff.days)          # 365
    print(diff.total_seconds())  # 31536000.0

    # 比较日期
    print(date2 > date1)      # True

时区（Timezones）
--------------------------

正确使用时区对于为不同地区的用户提供服务的应用程序至关重要。 Python 3.9+ 包括用于 IANA 时区支持的 ``zoneinfo`` 。对于早期版本，请使用 ``pytz`` 或 ``dateutil`` 。

.. code-block:: python

    from datetime import datetime, timezone, timedelta

    # UTC 时区
    utc = timezone.utc
    dt_utc = datetime.now(utc)
    print(dt_utc)  # 2024-01-15 02:30:45.123456+00:00

    # 固定偏移时区
    pst = timezone(timedelta(hours=-8))
    dt_pst = datetime.now(pst)
    print(dt_pst)  # 2024-01-14 18:30:45.123456-08:00

    # 时区之间转换
    dt_converted = dt_utc.astimezone(pst)
    print(dt_converted)

    # Python 3.9+ 带区域信息
    from zoneinfo import ZoneInfo

    eastern = ZoneInfo("America/New_York")
    tokyo = ZoneInfo("Asia/Tokyo")

    dt_eastern = datetime.now(eastern)
    dt_tokyo = dt_eastern.astimezone(tokyo)
    print(dt_tokyo)

    # 使天真的日期时间时区感知
    naive = datetime(2024, 1, 15, 10, 30)
    aware = naive.replace(tzinfo=utc)

比较日期（Comparing Dates）
------------------------------------------

日期时间 objects 支持比较 operators。当比较时区感知和天真的日期时间时，Python 会引发 TypeError 以防止细微的错误。

.. code-block:: python

    from datetime import datetime, date, timedelta

    dt1 = datetime(2024, 1, 15, 10, 0)
    dt2 = datetime(2024, 1, 15, 14, 0)
    dt3 = datetime(2024, 1, 16, 10, 0)

    # 比较
    print(dt1 < dt2)   # True
    print(dt1 == dt2)  # False
    print(dt3 > dt2)   # True

    # 检查日期是否为 range
    start = datetime(2024, 1, 1)
    end = datetime(2024, 12, 31)
    check = datetime(2024, 6, 15)
    print(start <= check <= end)  # True

    # 检查日期是否是今天
    today = date.today()
    some_date = date(2024, 1, 15)
    print(some_date == today)

    # 距离约会还有几天
    future = date(2024, 12, 25)
    days_until = (future - today).days
    print(f"Days until: {days_until}")

周相关操作（Working with Weeks）
--------------------------------------------------

获取周数、工作日以及使用 ISO 周日期对于报告和计划应用程序来说很常见。

.. code-block:: python

    from datetime import datetime, date, timedelta

    dt = datetime(2024, 1, 15)

    # Day of week (0=Monday, 6=Sunday)
    print(dt.weekday())     # 0（星期一）
    print(dt.isoweekday())  # 1（星期一，ISO 格式 1-7）

    # 周数
    print(dt.isocalendar())  # (2024, 3, 1) - 年、周、工作日

    # 开始一周（星期一）
    start_of_week = dt - timedelta(days=dt.weekday())
    print(start_of_week)  # 2024-01-15 00:00:00

    # 获取周末（周日）
    end_of_week = start_of_week + timedelta(days=6)
    print(end_of_week)  # 2024-01-21 00:00:00

    # 检查是否周末
    is_weekend = dt.weekday() >= 5
    print(is_weekend)  # False

日/月/年的开始和结束（Start and End of Day/Month/Year）
----------------------------------------------------------------------------------------

获取时间段的开始或结束对于日期 range 查询和报告非常有用。

.. code-block:: python

    from datetime import datetime, date, time, timedelta
    import calendar

    dt = datetime(2024, 1, 15, 14, 30, 45)

    # 一天的开始
    start_of_day = datetime.combine(dt.date(), time.min)
    print(start_of_day)  # 2024-01-15 00:00:00

    # 一天结束
    end_of_day = datetime.combine(dt.date(), time.max)
    print(end_of_day)  # 2024-01-15 23:59:59.999999

    # 月初
    start_of_month = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    print(start_of_month)  # 2024-01-01 00:00:00

    # 月底
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    end_of_month = dt.replace(day=last_day, hour=23, minute=59, second=59)
    print(end_of_month)  # 2024-01-31 23:59:59

    # 年初
    start_of_year = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    print(start_of_year)  # 2024-01-01 00:00:00

日历操作（Calendar Operations）
--------------------------------------------------

``calendar`` module 提供 functions 用于处理日历，包括检查闰年、获取月份 ranges 以及生成日历显示。

.. code-block:: python

    import calendar
    from datetime import date

    # 检查闰年
    print(calendar.isleap(2024))  # True
    print(calendar.isleap(2023))  # False

    # 一个月中的天数
    print(calendar.monthrange(2024, 2))  # (3, 29) - 1 号工作日，一个月中的天数
    days_in_feb = calendar.monthrange(2024, 2)[1]
    print(days_in_feb)  # 29

    # 生成月历
    print(calendar.month(2024, 1))

    # 迭代月份中的天数
    cal = calendar.Calendar()
    for day in cal.itermonthdays(2024, 1):
        if day != 0:
            print(day, end=" ")  # 1 2 3 ... 31

日期范围（Date Ranges）
----------------------------------

生成日期序列对于报告、图表和日程安排非常有用。

.. code-block:: python

    from datetime import datetime, date, timedelta

    def date_range(start, end, step=timedelta(days=1)):
        """Generate dates from start to end."""
        current = start
        while current <= end:
            yield current
            current += step

    # 每日日期
    start = date(2024, 1, 1)
    end = date(2024, 1, 7)
    for d in date_range(start, end):
        print(d)

    # 每周约会
    for d in date_range(start, date(2024, 1, 31), timedelta(weeks=1)):
        print(d)

    # 工作日（跳过周末）
    def business_days(start, end):
        current = start
        while current <= end:
            if current.weekday() < 5:  # Monday=0 to Friday=4
                yield current
            current += timedelta(days=1)

年龄计算（Age Calculation）
------------------------------------------

根据出生日期计算年龄需要处理今年尚未生日的边缘情况。

.. code-block:: python

    from datetime import date

    def calculate_age(birthdate):
        """Calculate age in years from birthdate."""
        today = date.today()
        age = today.year - birthdate.year
        # 如果今年没有生日则减 1
        if (today.month, today.day) < (birthdate.month, birthdate.day):
            age -= 1
        return age

    birthdate = date(1990, 6, 15)
    age = calculate_age(birthdate)
    print(f"Age: {age}")

    # 距离下一个生日还有几天
    def days_until_birthday(birthdate):
        today = date.today()
        next_birthday = birthdate.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

人类可读的时差（Human Readable Time Differences）
--------------------------------------------------------------------------------

将 timedelta 转换为人类可读的 strings（如 "2 hours ago" 或 "in 3 days"）可以改善用户体验。

.. code-block:: python

    from datetime import datetime, timedelta

    def time_ago(dt):
        """Convert datetime to human-readable relative time."""
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
        elif seconds < 604800:
            days = int(seconds // 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            return dt.strftime("%B %d, %Y")

    # 示例
    print(time_ago(datetime.now() - timedelta(minutes=5)))   # 5 分钟前
    print(time_ago(datetime.now() - timedelta(hours=2)))     # 2小时前
    print(time_ago(datetime.now() - timedelta(days=3)))      # 3天前

使用 dateutil 进行灵活解析（Using dateutil for Flexible Parsing）
--------------------------------------------------------------------------------------------------------------

``python-dateutil`` library 提供强大的解析功能，可自动处理多种日期格式以及相对增量计算。

.. code-block:: python

    # pip install python-dateutil
    from dateutil import parser
    from dateutil.relativedelta import relativedelta
    from datetime import datetime

    # 灵活的解析 - 自动处理多种格式
    dt1 = parser.parse("January 15, 2024")
    dt2 = parser.parse("15/01/2024")
    dt3 = parser.parse("2024-01-15T14:30:45Z")
    dt4 = parser.parse("Jan 15 2024 2:30 PM")

    # 相对增量 - 正确处理月份和年份
    now = datetime.now()

    # 添加 1 个月（处理不同的月份长度）
    next_month = now + relativedelta(months=1)

    # 添加1年
    next_year = now + relativedelta(years=1)

    # 下个月的最后一天
    last_of_next_month = now + relativedelta(months=1, day=31)

    # Complex 亲戚：2个月零3天前
    past = now - relativedelta(months=2, days=3)
