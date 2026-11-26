"""Task 05: scenario engine — model(weather_year) × size_idx(system_year).

run_scenario(zone, wx_year, sys_year): build the feature frame from
wx_year's zone weather ON wx_year's own calendar, predict per-unit load with
the zone's shape model, scale by size_idx[sys_year]. Canonical output schema
(CLAUDE.md scenario_hourly): weather_zone, scenario_id, ts_local, load_mw_pred.

Run:  uv run python load-forecast/src/scenario.py --zone NCENT --wx-year 2023 --sys-year 2026
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg
import shape_model as sm

SCENARIO_PATH = cfg.DERIVED_DIR / "scenario_hourly.parquet"


def scenario_features(zone_weather_hourly: pd.DataFrame, zone: str, wx_year: int) -> pd.DataFrame:
    day = (zone_weather_hourly["ts_local"] - pd.Timedelta(hours=1))
    wx = zone_weather_hourly.loc[
        (zone_weather_hourly["weather_zone"] == zone) & (day.dt.year == wx_year)
    ].copy()
    if wx.empty:
        raise ValueError(f"no zone weather for {zone} {wx_year}")
    if wx_year == 2021:
        # Task 05 spec: wx2021 is EX-URI. The shape model never trained on Uri
        # temperatures; LightGBM would silently clamp at its training minimum
        # and return physically wrong load. Drop the window outright.
        d = (wx["ts_local"] - pd.Timedelta(hours=1)).dt.strftime("%Y-%m-%d")
        uri = (d >= cfg.URI_WINDOW[0]) & (d <= cfg.URI_WINDOW[1])
        print(f"wx2021: dropping {int(uri.sum())} Uri-window hours (ex-Uri per spec) "
              "— annual sums cover the remaining hours only")
        wx = wx.loc[~uri]
    cal = sm.calendar_features(wx["ts_local"])
    return pd.concat([wx.reset_index(drop=True), cal.reset_index(drop=True)], axis=1)


def run_scenario(
    zone: str,
    wx_year: int,
    sys_year: int,
    zone_weather_hourly: pd.DataFrame,
    size_index: pd.DataFrame,
    booster=None,
) -> pd.DataFrame:
    """One (zone, weather year, system year) scenario → scenario_hourly rows.
    wx_year 2021 is automatically ex-Uri (see scenario_features)."""
    booster = booster if booster is not None else sm.load_model(zone)
    feats = scenario_features(zone_weather_hourly, zone, wx_year)
    feats = feats.dropna(subset=sm.FEATURES)
    idx = size_index.loc[
        (size_index["weather_zone"] == zone) & (size_index["year"] == sys_year), "size_idx"
    ]
    if idx.empty:
        raise ValueError(f"size_idx missing for {zone} {sys_year} — run Task 03 through that year")
    pred_pu = sm.predict_per_unit(booster, feats)
    return pd.DataFrame(
        {
            "weather_zone": zone,
            "scenario_id": f"wx{wx_year}_sys{sys_year}",
            "ts_local": feats["ts_local"].values,
            "load_mw_pred": pred_pu * float(idx.iloc[0]),
        }
    )


def _upsert_scenarios(new: pd.DataFrame) -> None:
    """Atomic upsert into scenario_hourly.parquet keyed on (zone, scenario_id):
    write to a temp file then rename, so a crash can't lose prior scenarios."""
    SCENARIO_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SCENARIO_PATH.exists():
        prior = pd.read_parquet(SCENARIO_PATH)
        new_keys = set(zip(new["weather_zone"], new["scenario_id"]))
        keep = ~pd.Series(
            list(zip(prior["weather_zone"], prior["scenario_id"])), index=prior.index
        ).isin(new_keys)
        new = pd.concat([prior.loc[keep], new], ignore_index=True)
    tmp = SCENARIO_PATH.with_suffix(".parquet.tmp")
    new.to_parquet(tmp)
    tmp.replace(SCENARIO_PATH)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zone", choices=cfg.ZONES)
    ap.add_argument("--wx-year", type=int)
    ap.add_argument("--sys-year", type=int)
    ap.add_argument(
        "--all", action="store_true",
        help="run the task-05 matrix: wx {2019,2021ex-Uri,2022,2023} × sys {2026,2028} × all zones",
    )
    args = ap.parse_args()

    zone_weather = pd.read_parquet(cfg.DERIVED_DIR / "zone_weather_hourly.parquet")
    size_index = pd.read_parquet(cfg.DERIVED_DIR / "size_index.parquet")

    if args.all:
        runs = [(z, w, s) for z in cfg.ZONES for w in (2019, 2021, 2022, 2023) for s in (2026, 2028)]
    else:
        if not (args.zone and args.wx_year and args.sys_year):
            ap.error("either --all or all of --zone/--wx-year/--sys-year")
        runs = [(args.zone, args.wx_year, args.sys_year)]

    outs = []
    for zone, wx_year, sys_year in runs:
        out = run_scenario(zone, wx_year, sys_year, zone_weather, size_index)
        print(
            f"{out['scenario_id'].iloc[0]} {zone}: {len(out):,} h, "
            f"annual {out['load_mw_pred'].sum() / 1e6:.2f} TWh, "
            f"peak {out['load_mw_pred'].max():,.0f} MW"
        )
        outs.append(out)
    _upsert_scenarios(pd.concat(outs, ignore_index=True))
    print(f"wrote {SCENARIO_PATH}")


if __name__ == "__main__":
    main()
