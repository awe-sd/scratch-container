import pandas as pd
import pytest

from pfa import periods


def _h(year):
    return [d.strftime("%Y-%m-%d") for d in periods.nerc_holidays(year)]


def test_holidays_2025():
    assert _h(2025) == ["2025-01-01", "2025-05-26", "2025-07-04", "2025-09-01", "2025-11-27", "2025-12-25"]


def test_holidays_2026_cover_old_constant():
    old = ["2026-01-01", "2026-05-25", "2026-07-04", "2026-09-07", "2026-11-26", "2026-12-25"]
    assert _h(2026) == old  # 07-04 is a Saturday: not moved


def test_holidays_2027_sunday_moved_saturday_not():
    # 2027-07-04 is Sunday -> 07-05; 2027-01-01 Friday; 2027-12-25 Saturday stays
    assert _h(2027) == ["2027-01-01", "2027-05-31", "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-25"]


def test_holidays_2028():
    # 2028-01-01 is a Saturday (not moved); 07-04 Tuesday; 12-25 Monday
    assert _h(2028) == ["2028-01-01", "2028-05-29", "2028-07-04", "2028-09-04", "2028-11-23", "2028-12-25"]


def test_sunday_holiday_observed_monday():
    assert pd.Timestamp("2023-01-01").dayofweek == 6
    assert "2023-01-02" in _h(2023)
    assert pd.Timestamp("2022-12-25").dayofweek == 6 and "2022-12-26" in _h(2022)
    assert pd.Timestamp("2021-07-04").dayofweek == 6 and "2021-07-05" in _h(2021)


def test_month_range():
    assert periods.month_range("2026-02") == (pd.Timestamp("2026-02-01"), pd.Timestamp("2026-02-28"))
    assert periods.month_range("2028-02")[1] == pd.Timestamp("2028-02-29")


def test_parse_month_rejects_garbage():
    for bad in ("2026", "2026-13", "x-y", ""):
        with pytest.raises(ValueError):
            periods.parse_month(bad)


def test_onpeak_days_sep_2026():
    d = periods.onpeak_days("2026-09")
    assert len(d) == 21 and len(d) * 16 == 336
    assert pd.Timestamp("2026-09-07") not in d


def test_onpeak_days_2027_months():
    assert len(periods.onpeak_days("2027-09")) == 21  # Labor Day 9/6
    assert len(periods.onpeak_days("2027-05")) == 20  # 21 weekdays minus Memorial Day 5/31
    assert len(periods.onpeak_days("2027-03")) == 23


def test_hour_class():
    assert periods.hour_class("2026-09-08", 7) == "OnPeak"
    assert periods.hour_class("2026-09-08", 22) == "OnPeak"
    assert periods.hour_class("2026-09-08", 23) == "7x8"
    assert periods.hour_class("2026-09-08", 6) == "7x8"
    assert periods.hour_class("2026-09-07", 12) == "2x16"  # Labor Day
    assert periods.hour_class("2026-09-12", 12) == "2x16"  # Saturday
    assert periods.hour_class("2026-09-12", 3) == "7x8"
