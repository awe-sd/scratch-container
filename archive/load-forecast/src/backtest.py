"""Rolling-origin backtest: train everything ≤ wall year, predict wall+1 with
that year's ACTUAL weather, score, roll the wall forward.

This is the honest level test the LOYO CV cannot provide (the size index is
re-fitted per fold, so the held-out year's level is genuinely unseen).

Folds: wall 2019 → target 2020 (covid — expect a miss, that's informative),
…, wall 2024 → target 2025 (weather truncates ~Aug 25). uri/outage hours are
excluded from SCORING (blackout load is not demand); covid hours stay in.

Run:  uv run python load-forecast/src/backtest.py [--zones NCENT COAST SCENT]
Output: printed table + load-forecast/output/backtest_rolling.csv
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg
import shape_model as sm
import size_index as si

OUTPUT_DIR = cfg.PROJECT_ROOT / "output"
BACKTEST_CSV = OUTPUT_DIR / "backtest_rolling.csv"


def fold_size_index(
    daily: pd.DataFrame, zone: str, wall_year: int, n_fit_years: int | None = None
) -> pd.DataFrame:
    """Per-fold size index through wall_year+1 (extrapolated), scaled to the
    fold's first year. Only RATIOS matter downstream (target = load/idx[y],
    prediction = pu × idx[target]), so the base choice cancels.
    n_fit_years None → the per-zone default (cfg.SIZE_EXTRAP_YEARS)."""
    train_end = f"{wall_year}-12-31"
    fit = si.fit_zone(daily, zone, train_end=train_end)
    annual = si.normalized_annual_gwh(fit, daily, train_end=train_end)
    n_fit = n_fit_years if n_fit_years is not None else cfg.SIZE_EXTRAP_YEARS.get(zone, 6)
    extra = si.extrapolate(annual, wall_year + 1, n_fit_years=n_fit)
    both = pd.concat([annual, extra], ignore_index=True)
    both["size_idx"] = both["normalized_gwh"] / float(both["normalized_gwh"].iloc[0])
    both["weather_zone"] = zone
    return both[["weather_zone", "year", "size_idx"]]


def run_fold(
    zone: str,
    wall_year: int,
    load_hourly: pd.DataFrame,
    zone_weather: pd.DataFrame,
    daily: pd.DataFrame,
    params: dict | None = None,
    num_rounds: int = sm.NUM_ROUNDS,
    n_fit_years: int | None = None,
) -> dict:
    """One (zone, wall) fold → metric dict. daily = si.build_daily output."""
    t0 = time.time()
    train_end = f"{wall_year}-12-31"
    target_year = wall_year + 1

    idx_df = fold_size_index(daily, zone, wall_year, n_fit_years=n_fit_years)
    frame = sm.build_frame(load_hourly, zone_weather, idx_df, zone)
    booster = sm.train_zone(frame, num_rounds=num_rounds, train_end=train_end, params=params)

    day_year = (frame["ts_local"] - pd.Timedelta(hours=1)).dt.year
    flags = frame["event_flag"].fillna("")
    scoreable = ~flags.isin(["uri", "outage"])
    test = frame.loc[(day_year == target_year) & scoreable].copy()
    if len(test) < 1000:
        return {"zone": zone, "wall_year": wall_year, "target_year": target_year,
                "status": f"skipped ({len(test)} scoreable hours)"}

    idx_target = float(
        idx_df.loc[idx_df["year"] == target_year, "size_idx"].iloc[0]
    )
    pred_mw = booster.predict(test[sm.FEATURES]) * idx_target
    actual_mw = (test["target_pu"] * test["size_idx"]).to_numpy() if "size_idx" in test else None
    # frame doesn't carry size_idx column — reconstruct actual from target_pu × its own year idx
    idx_map = idx_df.set_index("year")["size_idx"]
    actual_mw = (test["target_pu"] * day_year.loc[test.index].map(idx_map)).to_numpy()

    month = test["ts_local"].dt.to_period("M")
    dfm = pd.DataFrame({"month": month, "pred": pred_mw, "act": actual_mw})
    m = dfm.groupby("month")[["pred", "act"]].sum()
    monthly_mape = float((100 * (m["pred"] - m["act"]).abs() / m["act"]).mean())
    annual_err_pct = float(100 * (pred_mw.sum() / actual_mw.sum() - 1))
    hourly_mape = float(100 * np.mean(np.abs(pred_mw - actual_mw) / actual_mw))

    # growth error on matched (month, day, hour) vs the wall year's actuals
    keys = set(zip(test["ts_local"].dt.month, test["ts_local"].dt.day, test["ts_local"].dt.hour))
    wall_rows = frame.loc[(day_year == wall_year) & scoreable]
    wk = list(zip(wall_rows["ts_local"].dt.month, wall_rows["ts_local"].dt.day, wall_rows["ts_local"].dt.hour))
    wall_mask = pd.Series([k in keys for k in wk], index=wall_rows.index)
    wall_act = (
        wall_rows.loc[wall_mask, "target_pu"]
        * day_year.loc[wall_rows.loc[wall_mask].index].map(idx_map)
    ).sum()
    actual_growth = 100 * (actual_mw.sum() / wall_act - 1)
    pred_growth = 100 * (pred_mw.sum() / wall_act - 1)

    return {
        "zone": zone, "wall_year": wall_year, "target_year": target_year,
        "monthly_mape_pct": round(monthly_mape, 2),
        "annual_err_pct": round(annual_err_pct, 2),
        "growth_err_pp": round(pred_growth - actual_growth, 2),
        "hourly_mape_pct": round(hourly_mape, 2),
        "n_hours": len(test), "runtime_s": round(time.time() - t0, 1),
        "status": "ok",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zones", nargs="+", default=cfg.ZONES, choices=cfg.ZONES)
    ap.add_argument("--walls", nargs="+", type=int, default=[2019, 2020, 2021, 2022, 2023, 2024])
    args = ap.parse_args()

    load_hourly = pd.read_parquet(cfg.DERIVED_DIR / "load_hourly.parquet")
    zone_weather = pd.read_parquet(cfg.DERIVED_DIR / "zone_weather_hourly.parquet")

    rows = []
    for zone in args.zones:
        daily = si.build_daily(load_hourly, zone_weather, zone)
        for wall in args.walls:
            r = run_fold(zone, wall, load_hourly, zone_weather, daily)
            rows.append(r)
            print(r)
    out = pd.DataFrame(rows)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(BACKTEST_CSV, index=False)
    ok = out.loc[out["status"] == "ok"]
    if len(ok):
        print("\n=== rolling backtest summary (mean over folds) ===")
        print(ok.groupby("zone")[["monthly_mape_pct", "annual_err_pct", "growth_err_pp"]]
              .mean().round(2).to_string())
        print(f"\nwrote {BACKTEST_CSV}")


if __name__ == "__main__":
    main()
