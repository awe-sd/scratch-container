"""Analog-period replay benchmark: find history that looked like a recent
period, replay it at the current system size, compare to what actually happened.

Example (sdalvi's): "find a July in history whose weather was close to this
July, run it through the model at this year's size — do we get this July?"

Method:
  1. Weather signature of a (zone, year, month): the QUANTILE VECTOR of daily
     mean pop-weighted temps (interpolated to 15 points — compares the
     distribution, not the day ordering), plus mean dewpoint as a tiebreaker.
  2. Analog distance = RMSE between quantile vectors (°F) + 0.25 × |dewpoint
     mean diff|. Candidates default to the SAME calendar month of other years
     (apples-to-apples day counts and seasonality).
  3. Replay: the analog month's hourly weather (its own calendar — weekday mix
     differs from the target month's; that is ~1% noise on monthly energy and
     is reported, not hidden) → shape model → × size_idx[target year].
  4. Score vs the target month's actuals: energy %, peak %, hourly MAPE on
     temp-rank-matched hours is NOT attempted — hours aren't pairable across
     different months; energy and peak are the honest comparables.

Run:  uv run python load-forecast/src/analog.py --zone NCENT --target 2026-07 [--top 5]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg
import shape_model as sm
import size_index as si

N_QUANTILES = 15
DEW_WEIGHT = 0.25


def _month_slice(df: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
    day = df["ts_local"] - pd.Timedelta(hours=1)
    return df.loc[(day.dt.year == year) & (day.dt.month == month)]


def weather_signature(zone_weather: pd.DataFrame, zone: str, year: int, month: int) -> dict | None:
    wx = _month_slice(zone_weather.loc[zone_weather["weather_zone"] == zone], year, month)
    daily = si.daily_zone_temp(wx.assign(weather_zone=zone), zone)
    temps = daily["temp_mean_f"].dropna()
    if len(temps) < 25:  # demand a near-complete month
        return None
    q = np.quantile(temps, np.linspace(0.05, 0.95, N_QUANTILES))
    dew = wx["dewpoint_f_popwt"].mean()
    return {"quantiles": q, "dew_mean": float(dew), "temp_mean": float(temps.mean()),
            "n_days": int(len(temps))}


def analog_distance(a: dict, b: dict) -> float:
    q_rmse = float(np.sqrt(np.mean((a["quantiles"] - b["quantiles"]) ** 2)))
    return q_rmse + DEW_WEIGHT * abs(a["dew_mean"] - b["dew_mean"])


def find_analogs(
    zone_weather: pd.DataFrame, zone: str, target_year: int, target_month: int, top_k: int = 5
) -> pd.DataFrame:
    target = weather_signature(zone_weather, zone, target_year, target_month)
    if target is None:
        raise ValueError(f"{zone} {target_year}-{target_month:02d}: not enough weather data")
    years = sorted(set((zone_weather["ts_local"] - pd.Timedelta(hours=1)).dt.year.unique()))
    rows = []
    for y in years:
        if y == target_year:
            continue
        sig = weather_signature(zone_weather, zone, y, target_month)
        if sig is None:
            continue
        rows.append({
            "analog_year": y, "month": target_month,
            "distance_f": round(analog_distance(target, sig), 3),
            "temp_mean_f": round(sig["temp_mean"], 2),
            "target_temp_mean_f": round(target["temp_mean"], 2),
            "dew_mean_diff_f": round(sig["dew_mean"] - target["dew_mean"], 2),
        })
    return pd.DataFrame(rows).sort_values("distance_f").head(top_k).reset_index(drop=True)


def replay(
    zone: str, analog_year: int, target_year: int, month: int,
    zone_weather: pd.DataFrame, size_index: pd.DataFrame, load_hourly: pd.DataFrame,
    booster=None,
) -> dict:
    """Analog month's weather × target year's size vs target month's actuals."""
    booster = booster if booster is not None else sm.load_model(zone)
    wx = _month_slice(zone_weather.loc[zone_weather["weather_zone"] == zone], analog_year, month)
    feats = pd.concat(
        [wx.reset_index(drop=True), sm.calendar_features(wx["ts_local"]).reset_index(drop=True)],
        axis=1,
    ).dropna(subset=sm.FEATURES)
    idx = size_index.loc[
        (size_index["weather_zone"] == zone) & (size_index["year"] == target_year), "size_idx"
    ]
    if idx.empty:
        raise ValueError(f"no size_idx for {zone} {target_year}")
    pred_mw = sm.predict_per_unit(booster, feats) * float(idx.iloc[0])

    act = _month_slice(load_hourly.loc[load_hourly["weather_zone"] == zone], target_year, month)
    act = act.loc[act["event_flag"].fillna("") == ""].dropna(subset=["load_mw"])

    if len(act) != len(pred_mw):
        # mean × actual-hour-count, NOT the analog month's raw energy sum —
        # only triggers when hour counts diverge (filtered/partial months)
        print(f"  note: hour-count mismatch pred {len(pred_mw)} vs actual {len(act)} — "
              "pred energy scaled to the actual hour count")
    pred_energy = pred_mw.sum() / 1000.0 * (len(act) / max(len(pred_mw), 1))
    act_energy = act["load_mw"].sum() / 1000.0
    return {
        "zone": zone, "analog": f"{analog_year}-{month:02d}", "target": f"{target_year}-{month:02d}",
        "pred_energy_gwh": round(pred_energy, 1), "actual_energy_gwh": round(act_energy, 1),
        "energy_err_pct": round(100 * (pred_energy / act_energy - 1), 2),
        "pred_peak_mw": round(float(pred_mw.max()), 0), "actual_peak_mw": round(float(act["load_mw"].max()), 0),
        "peak_err_pct": round(100 * (float(pred_mw.max()) / float(act["load_mw"].max()) - 1), 2),
        "n_pred_hours": int(len(pred_mw)), "n_actual_hours": int(len(act)),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zone", required=True, choices=cfg.ZONES)
    ap.add_argument("--target", required=True, help="YYYY-MM, e.g. 2026-07")
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args()
    ty, tm = int(args.target[:4]), int(args.target[5:7])

    zone_weather = pd.read_parquet(cfg.DERIVED_DIR / "zone_weather_hourly.parquet")
    size_index = pd.read_parquet(cfg.DERIVED_DIR / "size_index.parquet")
    load_hourly = pd.read_parquet(cfg.DERIVED_DIR / "load_hourly.parquet")

    analogs = find_analogs(zone_weather, args.zone, ty, tm, top_k=args.top)
    print(f"closest weather analogs for {args.zone} {args.target}:")
    print(analogs.to_string(index=False))

    print("\nreplay benchmark (analog weather × target-year size vs target actuals):")
    rows = [
        replay(args.zone, int(r["analog_year"]), ty, tm, zone_weather, size_index, load_hourly)
        for _, r in analogs.iterrows()
    ]
    out = pd.DataFrame(rows).merge(
        analogs.rename(columns={"analog_year": "ay"}).assign(
            analog=lambda d: d["ay"].astype(str) + f"-{tm:02d}"
        )[["analog", "distance_f", "temp_mean_f", "target_temp_mean_f"]],
        on="analog", how="left",
    )
    print(out.to_string(index=False))
    csv_path = cfg.PROJECT_ROOT / "output" / "analog_benchmark.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if csv_path.exists():
        prior = pd.read_csv(csv_path)
        prior = prior.loc[~((prior["zone"] == args.zone) & (prior["target"] == out["target"].iloc[0]))]
        out = pd.concat([prior, out], ignore_index=True)
    out.to_csv(csv_path, index=False)


if __name__ == "__main__":
    main()
