"""Task 08-X shared truth-basis helpers.

Moved verbatim (2026-08-16, task08x2 amendment-2 build) from
scripts/experiment_prob_size.py (`zone_frame`) and
scripts/task08x_truth_diagnostic.py (`symmetric_growth`, `normalized_growth`)
so both the run-1 harness and the amendment-2 harness import one copy. No
behavior change -- see training_log.md task08x2 entry for the diff proof
(rerun of task08x_truth_diagnostic.py against the pre-existing
output/task08x_truth_diagnostic.csv).

truth_sym (symmetric_growth) and truth_norm (normalized_growth) are the two
corrected truth bases for task08x2; the defective pre-registered
matched_hour_growth basis (run_fold reproduction, calendar-asymmetric
whenever the base year has uri/outage exclusions) is retired and stays in
scripts/experiment_prob_size.py only, for run-1 reproducibility.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import size_index as si  # noqa: E402


def zone_frame(load_hourly: pd.DataFrame, zone_weather: pd.DataFrame, zone: str) -> pd.DataFrame:
    ld = load_hourly.loc[load_hourly["weather_zone"] == zone, ["ts_local", "load_mw", "event_flag"]]
    wx = zone_weather.loc[zone_weather["weather_zone"] == zone, ["ts_local", "temp_f_popwt"]]
    df = ld.merge(wx, on="ts_local", how="inner").dropna(subset=["load_mw", "temp_f_popwt"])
    df["day_year"] = (df["ts_local"] - pd.Timedelta(hours=1)).dt.year
    df["scoreable"] = ~df["event_flag"].fillna("").isin(["uri", "outage"])
    return df.reset_index(drop=True)


def symmetric_growth(frame: pd.DataFrame, base_year: int, target_year: int) -> float:
    t = frame.loc[(frame["day_year"] == target_year) & frame["scoreable"]]
    b = frame.loc[(frame["day_year"] == base_year) & frame["scoreable"]]
    if len(t) < 1000 or len(b) < 1000:
        return float("nan")
    tk = list(zip(t["ts_local"].dt.month, t["ts_local"].dt.day, t["ts_local"].dt.hour))
    bk = list(zip(b["ts_local"].dt.month, b["ts_local"].dt.day, b["ts_local"].dt.hour))
    common = set(tk) & set(bk)
    tsum = float(t.loc[[k in common for k in tk], "load_mw"].sum())
    bsum = float(b.loc[[k in common for k in bk], "load_mw"].sum())
    return 100.0 * (tsum / bsum - 1.0)


def normalized_growth(daily: pd.DataFrame, zone: str, target_year: int) -> float:
    """y/y of normalized_gwh from an annual fit through the target year."""
    train_end = f"{target_year}-12-31"
    fit = si.fit_zone(daily, zone, train_end=train_end)
    annual = si.normalized_annual_gwh(fit, daily, train_end=train_end)
    a = annual.set_index("year")["normalized_gwh"]
    if target_year not in a.index or (target_year - 1) not in a.index:
        return float("nan")
    return 100.0 * (float(a.loc[target_year]) / float(a.loc[target_year - 1]) - 1.0)
