"""Tests for pull_load helpers: event windows, cache freshness, completeness."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import config as cfg
import pull_load as pl


def _flags(ts_strings, zone):
    ts = pd.Series(pd.to_datetime(ts_strings))
    return pl.event_flag(ts, zone).tolist()


def test_event_flag_he24_boundaries():
    # HE24 of Feb 9 is labeled 2021-02-10 00:00 — must NOT be uri;
    # HE24 of Feb 20 is labeled 2021-02-21 00:00 — MUST be uri.
    got = _flags(
        ["2021-02-10 00:00", "2021-02-10 01:00", "2021-02-21 00:00", "2021-02-21 01:00"],
        "NCENT",
    )
    assert got == [pd.NA, "uri", "uri", pd.NA]


def test_event_flag_outage_zone_scoped():
    ts = ["2024-07-10 12:00", "2024-05-17 12:00", "2024-03-10 12:00"]
    assert _flags(ts, "COAST") == ["outage", "outage", pd.NA]
    assert _flags(ts, "NCENT") == [pd.NA, pd.NA, pd.NA]


def test_cache_is_fresh_rules(tmp_path):
    full = tmp_path / "full_2020.parquet"
    pd.DataFrame({"date": ["2020-01-01", "2020-12-31"]}).to_parquet(full)
    assert pl._cache_is_fresh(full, 2020)

    partial = tmp_path / "partial_2020.parquet"
    pd.DataFrame({"date": ["2020-01-01", "2020-08-01"]}).to_parquet(partial)
    assert not pl._cache_is_fresh(partial, 2020)

    current_year = int(pd.Timestamp.now().year)
    yesterday = (pd.Timestamp.now().normalize() - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    cur = tmp_path / "cur.parquet"
    pd.DataFrame({"date": [f"{current_year}-01-01", yesterday]}).to_parquet(cur)
    assert pl._cache_is_fresh(cur, current_year)


def _hourly_frame(zone, days, hours_per_day):
    rows = []
    for day, n in zip(days, hours_per_day):
        base = pd.Timestamp(day)
        for h in range(1, n + 1):
            rows.append({"weather_zone": zone, "ts_local": base + pd.Timedelta(hours=h),
                         "load_mw": 1000.0})
    return pd.DataFrame(rows)


def test_completeness_report_catches_holes_but_not_dst():
    # 2023-03-12 is the 2nd Sunday of March (spring-forward): 23h is normal.
    days = ["2023-03-10", "2023-03-11", "2023-03-12", "2023-03-13", "2023-03-15"]
    hours = [24, 24, 23, 20, 24]  # 03-14 missing entirely, 03-13 short
    df = _hourly_frame("NCENT", days, hours)
    rep = pl.completeness_report(df)
    got = {(r.weather_zone, r.date): r.n_hours for r in rep.itertuples()}
    assert ("NCENT", "2023-03-13") in got and got[("NCENT", "2023-03-13")] == 20
    assert ("NCENT", "2023-03-14") in got and got[("NCENT", "2023-03-14")] == 0
    assert ("NCENT", "2023-03-12") not in got  # DST day excluded


def test_qc_summary_counts_days_and_missing():
    days = [f"2023-06-{d:02d}" for d in range(1, 11)]
    df = _hourly_frame("SCENT", days, [24] * 10)
    qc = pl.qc_summary(df)
    row = qc.loc[(qc["weather_zone"] == "SCENT") & (qc["year"] == 2023)].iloc[0]
    assert row["rows"] == 240 and row["n_days"] == 10
