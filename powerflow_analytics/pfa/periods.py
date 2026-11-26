"""Calendar rules: settlement months, NERC holidays, on-peak days, hour classes."""
from __future__ import annotations

import datetime as dt

import pandas as pd

ONPEAK_HE = range(7, 23)  # HE7-22


def parse_month(month: str) -> tuple[int, int]:
    """'YYYY-MM' -> (year, month)."""
    try:
        y, m = (int(x) for x in month.split("-"))
        dt.date(y, m, 1)
    except ValueError:
        raise ValueError(f"month must be 'YYYY-MM', got {month!r}") from None
    return y, m


def month_range(month: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    """First and last calendar day of a 'YYYY-MM' settlement month."""
    y, m = parse_month(month)
    first = pd.Timestamp(year=y, month=m, day=1)
    return first, first + pd.offsets.MonthEnd(0)


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> pd.Timestamp:
    """n-th (1-based) given weekday of the month; n=-1 is the last."""
    days = pd.date_range(f"{year}-{month:02d}-01", periods=pd.Period(f"{year}-{month:02d}").days_in_month)
    hits = days[days.dayofweek == weekday]
    return hits[n - 1] if n > 0 else hits[-1]


def nerc_holidays(year: int) -> pd.DatetimeIndex:
    """NERC holidays: a Sunday holiday is observed the following Monday; a Saturday holiday is not moved."""
    fixed = [pd.Timestamp(year=year, month=1, day=1), pd.Timestamp(year=year, month=7, day=4),
             pd.Timestamp(year=year, month=12, day=25)]
    fixed = [d + pd.Timedelta(days=1) if d.dayofweek == 6 else d for d in fixed]
    rule = [_nth_weekday(year, 5, 0, -1), _nth_weekday(year, 9, 0, 1), _nth_weekday(year, 11, 3, 4)]
    return pd.DatetimeIndex(sorted(fixed + rule))


def onpeak_days(month: str) -> pd.DatetimeIndex:
    """Business days (Mon-Fri minus NERC holidays) of a 'YYYY-MM' month."""
    first, last = month_range(month)
    days = pd.bdate_range(first, last)
    return days[~days.isin(nerc_holidays(first.year))]


def hour_class(day, he: int) -> str:
    """'OnPeak' = weekday non-holiday HE7-22; '2x16' = weekend/holiday HE7-22; '7x8' = HE23-24 and HE1-6."""
    if he not in ONPEAK_HE:
        return "7x8"
    d = pd.Timestamp(day).normalize()
    return "OnPeak" if d.dayofweek < 5 and d not in nerc_holidays(d.year) else "2x16"


def month_label(month: str) -> str:
    """Short month name for headers; 'Sept' for September."""
    m = parse_month(month)[1]
    return "Sept" if m == 9 else dt.date(2000, m, 1).strftime("%b")


def month_name(month: str) -> str:
    return dt.date(2000, parse_month(month)[1], 1).strftime("%B")
