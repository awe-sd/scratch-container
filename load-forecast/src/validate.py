"""Task 06: honest 2025–2026 scorecard.

Models trained ≤2024 only (enforced upstream). Replay actual 2025–2026 weather
through shape model × extrapolated size_idx; score against actual load.

Monthly columns: actual, pred_wx, ape_pct, miss_gwh, and
weather_anomaly_gwh = pred_wx − pred_norm — the model's own estimate of how far
the month's weather pushed load off climate-normal. NOTE (review D2): the
former "trend_component" column was pred_norm − actual, which is dominated by
the weather anomaly and carries no trend information — removed. Level/trend
accuracy is judged by the growth-error rows and hourly/peak metrics, not by a
per-month decomposition.

Also reported per zone: hourly MAPE per year, top-50-actual-hours energy bias
per year (the scarcity hours a trader prices), annual peak error, and growth
error for 2025 (1-yr) and 2026 (2-yr annualized), both vs the 2024 base on
symmetric matched hours.

Outputs: output/validation_scores.parquet + output/validation_report.md.
Run:  uv run python load-forecast/src/validate.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg
import shape_model as sm

OUTPUT_DIR = cfg.PROJECT_ROOT / "output"
VAL_YEARS = (2025, 2026)


def hourly_normals(zone_weather: pd.DataFrame, zone: str) -> pd.DataFrame:
    """Climate-normal weather features by (mm-dd, hour) from ≤TRAIN_END years —
    the hourly analogue of size_index.climate_normal_temp."""
    wx = zone_weather.loc[
        (zone_weather["weather_zone"] == zone) & (zone_weather["ts_local"] <= cfg.TRAIN_END)
    ].copy()
    key_day = (wx["ts_local"] - pd.Timedelta(hours=1)).dt.strftime("%m-%d")
    wx["key"] = key_day + "H" + wx["ts_local"].dt.hour.astype(str)
    cols = ["temp_f_popwt", "dewpoint_f_popwt", "temp_f_avg24", "temp_f_ewm3d"]
    return wx.groupby("key")[cols].mean().reset_index()


def predict_hourly(
    zone: str, zone_weather: pd.DataFrame, size_index: pd.DataFrame, at_normals: bool
) -> pd.DataFrame:
    """Prediction for VAL_YEARS hours: actual calendar, actual-or-normal weather."""
    wx = zone_weather.loc[
        (zone_weather["weather_zone"] == zone)
        & (zone_weather["ts_local"].dt.year.isin(VAL_YEARS))
    ].copy()
    if at_normals:
        key_day = (wx["ts_local"] - pd.Timedelta(hours=1)).dt.strftime("%m-%d")
        wx["key"] = key_day + "H" + wx["ts_local"].dt.hour.astype(str)
        normals = hourly_normals(zone_weather, zone)
        cols = ["temp_f_popwt", "dewpoint_f_popwt", "temp_f_avg24", "temp_f_ewm3d"]
        wx = wx.drop(columns=cols).merge(normals, on="key", how="left")
    feats = pd.concat(
        [wx.reset_index(drop=True), sm.calendar_features(wx["ts_local"]).reset_index(drop=True)],
        axis=1,
    ).dropna(subset=sm.FEATURES)
    booster = sm.load_model(zone)
    pred_pu = sm.predict_per_unit(booster, feats)
    idx = size_index.loc[size_index["weather_zone"] == zone].set_index("year")["size_idx"]
    # year attribution via (ts − 1h), same convention as shape_model.build_frame
    year = (feats["ts_local"] - pd.Timedelta(hours=1)).dt.year
    scale = year.map(idx).to_numpy()
    return pd.DataFrame({"ts_local": feats["ts_local"].values, "pred_mw": pred_pu * scale})


def monthly_scores(actual: pd.DataFrame, pred_wx: pd.DataFrame, pred_norm: pd.DataFrame) -> pd.DataFrame:
    """Join on hours present in all three; aggregate to month."""
    a = actual.set_index("ts_local")["load_mw"].rename("actual")
    w = pred_wx.set_index("ts_local")["pred_mw"].rename("pred_wx")
    n = pred_norm.set_index("ts_local")["pred_mw"].rename("pred_norm")
    df = pd.concat([a, w, n], axis=1, join="inner").dropna().reset_index()
    df["month"] = df["ts_local"].dt.to_period("M").astype(str)
    m = df.groupby("month")[["actual", "pred_wx", "pred_norm"]].sum().div(1000.0)  # GWh
    m["ape_pct"] = 100 * (m["pred_wx"] - m["actual"]).abs() / m["actual"]
    m["miss_gwh"] = m["pred_wx"] - m["actual"]
    m["weather_anomaly_gwh"] = m["pred_wx"] - m["pred_norm"]
    return m.drop(columns=["pred_norm"]).reset_index()


def hourly_and_peak_metrics(actual: pd.DataFrame, pred_wx: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
    """Per year: hourly MAPE, top-N-actual-hours energy bias, annual peak error.
    The top-hours bias is the trader-relevant one — monthly averages cancel a
    seasonal bias that scarcity hours do not."""
    a = actual.set_index("ts_local")["load_mw"].rename("act")
    p = pred_wx.set_index("ts_local")["pred_mw"].rename("pred")
    df = pd.concat([a, p], axis=1, join="inner").dropna()
    df["year"] = (df.index - pd.Timedelta(hours=1)).year
    df = df[df["year"].isin(VAL_YEARS)]  # drop the lone Dec-31 HE24 spillover bucket
    rows = []
    for year, g in df.groupby("year"):
        top = g.nlargest(top_n, "act")
        rows.append({
            "year": int(year),
            "hourly_mape_pct": round(float(100 * ((g["pred"] - g["act"]).abs() / g["act"]).mean()), 2),
            f"top{top_n}h_bias_pct": round(float(100 * (top["pred"].sum() / top["act"].sum() - 1)), 2),
            "peak_err_pct": round(float(100 * (g["pred"].max() / g["act"].max() - 1)), 2),
        })
    return pd.DataFrame(rows)


def annual_growth_error(
    actual: pd.DataFrame, pred_wx: pd.DataFrame, base_year_actual: pd.DataFrame,
    target_year: int = 2025,
) -> pd.DataFrame:
    """Growth 2024→target_year on MATCHED calendar hours, in pp/yr (annualized
    when the target is more than one year past the base — 2026 is a 2-yr CAGR).
    Matching restricts BOTH sides to the same (month, day, hour) set, which
    handles partial years and drops 2024's Feb 29 naturally."""
    n_years = target_year - 2024
    a = actual.set_index("ts_local")["load_mw"]
    p = pred_wx.set_index("ts_local")["pred_mw"]
    common = a.index.intersection(p.index)
    common25 = common[common.year == target_year]
    b = base_year_actual.dropna(subset=["load_mw"]).set_index("ts_local")["load_mw"]

    # SYMMETRIC matching: an hour enters the growth calc only if its
    # (month, day, hour) key is valid in BOTH years. One-sided filtering
    # (e.g. dropping Beryl-outage hours from 2024 only) shrinks the
    # denominator while the numerator keeps those calendar hours → inflated
    # "actual growth" (COAST showed a bogus 10.7% that way).
    k25 = {(t.month, t.day, t.hour) for t in common25}
    k24 = {(t.month, t.day, t.hour) for t in b.index}
    matched = k25 & k24

    m25 = pd.Series([(t.month, t.day, t.hour) in matched for t in common25], index=common25)
    m24 = pd.Series([(t.month, t.day, t.hour) in matched for t in b.index], index=b.index)
    a25 = a.loc[common25][m25.to_numpy()].sum()
    p25 = p.loc[common25][m25.to_numpy()].sum()
    a24 = b[m24.to_numpy()].sum()
    actual_g = 100 * ((a25 / a24) ** (1.0 / n_years) - 1)
    pred_g = 100 * ((p25 / a24) ** (1.0 / n_years) - 1)
    label = f"{target_year}" + ("" if n_years == 1 else f" ({n_years}-yr annualized)")
    return pd.DataFrame(
        {"metric": [f"actual_growth_pct_{label}", f"pred_growth_pct_{label}",
                    f"error_pp_{label}", f"matched_hours_{label}"],
         "value": [actual_g, pred_g, pred_g - actual_g, float(int(m25.sum()))]}
    )


def validate_zone(zone: str, load_hourly: pd.DataFrame, zone_weather: pd.DataFrame, size_index: pd.DataFrame) -> dict:
    actual = load_hourly.loc[
        (load_hourly["weather_zone"] == zone)
        & (load_hourly["ts_local"].dt.year.isin(VAL_YEARS))
        & ~load_hourly["event_flag"].fillna("").isin(["uri", "outage"])
    ][["ts_local", "load_mw"]]
    actual_2024 = load_hourly.loc[
        (load_hourly["weather_zone"] == zone)
        & (load_hourly["ts_local"].dt.year == 2024)
        & ~load_hourly["event_flag"].fillna("").isin(["uri", "outage"])
    ][["ts_local", "load_mw"]]
    pred_wx = predict_hourly(zone, zone_weather, size_index, at_normals=False)
    pred_norm = predict_hourly(zone, zone_weather, size_index, at_normals=True)
    monthly = monthly_scores(actual, pred_wx, pred_norm)
    growth = pd.concat(
        [annual_growth_error(actual, pred_wx, actual_2024, target_year=y) for y in (2025, 2026)],
        ignore_index=True,
    )
    hourly_peak = hourly_and_peak_metrics(actual, pred_wx)
    monthly["weather_zone"] = zone
    growth["weather_zone"] = zone
    hourly_peak["weather_zone"] = zone
    return {"monthly": monthly, "growth": growth, "hourly_peak": hourly_peak}


def main() -> None:
    load_hourly = pd.read_parquet(cfg.DERIVED_DIR / "load_hourly.parquet")
    zone_weather = pd.read_parquet(cfg.DERIVED_DIR / "zone_weather_hourly.parquet")
    size_index = pd.read_parquet(cfg.DERIVED_DIR / "size_index.parquet")

    monthlies, growths, lines = [], [], ["# Validation scorecard (train ≤2024, score 2025–2026)\n"]
    for zone in cfg.ZONES:
        r = validate_zone(zone, load_hourly, zone_weather, size_index)
        monthlies.append(r["monthly"])
        growths.append(r["growth"])
        mape = r["monthly"]["ape_pct"].mean()
        err_pp = r["growth"].loc[r["growth"]["metric"] == "error_pp_2025", "value"].iloc[0]
        hp = r["hourly_peak"]
        max_hourly = hp["hourly_mape_pct"].max()
        verdict = "PASS" if (mape <= 4.0 and abs(err_pp) <= 1.0 and max_hourly < 10.0) else "FAIL"
        lines += [
            f"\n## {zone} — monthly MAPE {mape:.2f}% (target ≤4%), "
            f"2025 growth error {err_pp:+.2f} pp (target ≤1), "
            f"worst-year hourly MAPE {max_hourly:.2f}% (target <10) → {verdict}\n",
            r["monthly"].drop(columns="weather_zone").round(2).to_markdown(index=False),
            "\n",
            r["hourly_peak"].drop(columns="weather_zone").to_markdown(index=False),
            "\n",
            r["growth"].drop(columns="weather_zone").round(3).to_markdown(index=False),
        ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.concat(monthlies, ignore_index=True).to_parquet(OUTPUT_DIR / "validation_scores.parquet")
    (OUTPUT_DIR / "validation_report.md").write_text("\n".join(lines))
    print(f"wrote {OUTPUT_DIR / 'validation_report.md'}")


if __name__ == "__main__":
    main()
