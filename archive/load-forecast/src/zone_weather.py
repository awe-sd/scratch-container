"""Task 02: zone_weather_hourly — population-weighted zone temp/dewpoint + features.

Reads ONLY the station-year parquet cache written by pull_weather.py (never the
network) and writes data/derived/zone_weather_hourly.parquet with the canonical
schema: weather_zone | ts_local | temp_f_popwt | dewpoint_f_popwt |
temp_f_avg24 (trailing 24 h mean) | temp_f_ewm3d (EWM, halflife 36 h).

Station weights per zone come from data/derived/crosswalk_county_station.csv
(weight column summed per station, renormalized per zone). Until that file
exists (it is built by Task 01), a PROVISIONAL equal-weight airport anchor set
is used and loudly labeled as such — do not trust derived output built from it
for anything beyond plumbing checks.

Provisional ids verified against isd-history 2026-08-14. Two ids in the original
spec were stale (station renumbered after 1997) and are corrected here:
  Dallas Love  722583-13960 (ended 1997-12-31) → 722580-13960 (active)
  Houston Hobby 722435-12918 (ended 1997-12-31) → 722440-12918 (active)

Per-hour weighting renormalizes over the stations that actually report that
hour, so one missing station degrades gracefully instead of NaN-ing the zone.
Feature windows are row-based on the hourly series (DST days have 23/24 rows,
so windows there are off by ±1 physical hour — accepted, documented).

Run:  uv run python load-forecast/src/zone_weather.py [--out path.parquet]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg
import pull_weather as pw

CROSSWALK_PATH = cfg.DERIVED_DIR / "crosswalk_county_station.csv"
OUT_PATH = cfg.DERIVED_DIR / "zone_weather_hourly.parquet"

EWM_HALFLIFE_HOURS = 36.0
AVG_WINDOW_HOURS = 24

# PROVISIONAL equal-weight anchors — used ONLY while the crosswalk is absent.
PROVISIONAL_ANCHORS: dict[str, list[str]] = {
    "NCENT": ["722590-03927", "722580-13960"],  # DFW Intl, Dallas Love Field
    "COAST": ["722430-12960", "722440-12918"],  # Houston IAH, Houston Hobby
    "SCENT": ["722540-13904", "722530-12921"],  # Austin ABIA, San Antonio Intl
}


def get_station_weights() -> tuple[dict[str, dict[str, float]], str]:
    """→ ({zone: {station_id: weight}}, source) with weights summing to 1 per
    zone. source is 'crosswalk' or 'provisional'."""
    if CROSSWALK_PATH.exists():
        cw = pd.read_csv(CROSSWALK_PATH, dtype={"county_fips": str})
        per_station = cw.groupby(["weather_zone", "station_id"])["weight"].sum()
        weights: dict[str, dict[str, float]] = {}
        for zone in cfg.ZONES:
            if zone in per_station.index.get_level_values(0):
                z = per_station.loc[zone]
                weights[zone] = (z / z.sum()).to_dict()
        return weights, "crosswalk"
    return (
        {z: {sid: 1.0 / len(sids) for sid in sids} for z, sids in PROVISIONAL_ANCHORS.items()},
        "provisional",
    )


def load_station_history(station_id: str) -> pd.DataFrame | None:
    """Concatenate every cached year for one station (None if nothing cached).
    Year files are contiguous and non-overlapping by construction; the dedupe
    is belt-and-braces only."""
    files = sorted(pw.WEATHER_RAW_DIR.glob(f"{station_id}_*.parquet"))
    if not files:
        return None
    df = pd.concat(
        [pd.read_parquet(f, columns=["ts_local", "temp_f", "dewpoint_f"]) for f in files],
        ignore_index=True,
    )
    return df.sort_values("ts_local").drop_duplicates("ts_local", keep="first")


def weighted_mean(mat: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """Row-wise weighted mean of station columns, renormalizing each hour over
    the stations that are non-NaN. All-NaN hour → NaN."""
    w_avail = mat.notna().mul(weights, axis=1).sum(axis=1)
    num = mat.mul(weights, axis=1).sum(axis=1, min_count=1)
    return num / w_avail.replace(0.0, np.nan)


def add_zone_features(z: pd.DataFrame) -> pd.DataFrame:
    """temp_f_avg24 = strict trailing 24-row mean (NaN inside window → NaN);
    temp_f_ewm3d = EWM mean with halflife 36 h (rows), min_periods=1."""
    z = z.sort_values("ts_local").reset_index(drop=True)
    z["temp_f_avg24"] = z["temp_f_popwt"].rolling(AVG_WINDOW_HOURS, min_periods=AVG_WINDOW_HOURS).mean()
    z["temp_f_ewm3d"] = z["temp_f_popwt"].ewm(halflife=EWM_HALFLIFE_HOURS, min_periods=1).mean()
    return z


def build_zone_weather(out_path: Path = OUT_PATH) -> pd.DataFrame:
    weights, source = get_station_weights()
    if source == "provisional":
        print("=" * 76)
        print("PROVISIONAL WEIGHTS: crosswalk_county_station.csv not found —")
        print("using the equal-weight airport anchor set. Rebuild once Task 01 lands.")
        for zone, w in weights.items():
            print(f"  {zone}: " + ", ".join(f"{sid} ({wt:.2f})" for sid, wt in w.items()))
        print("=" * 76)

    zone_frames: list[pd.DataFrame] = []
    for zone in cfg.ZONES:
        zw = weights.get(zone, {})
        series: dict[str, pd.Series] = {}
        for sid in zw:
            hist = load_station_history(sid)
            if hist is None:
                print(f"  WARNING {zone}: no cache for {sid} — run pull_weather.py; "
                      f"renormalizing over remaining stations")
                continue
            series[sid] = hist.set_index("ts_local")[["temp_f", "dewpoint_f"]]
        if not series:
            print(f"  WARNING {zone}: no cached stations at all — zone skipped")
            continue

        w = pd.Series({sid: zw[sid] for sid in series})
        w = w / w.sum()
        temp_mat = pd.concat({sid: s["temp_f"] for sid, s in series.items()}, axis=1)
        dew_mat = pd.concat({sid: s["dewpoint_f"] for sid, s in series.items()}, axis=1)
        del series

        z = pd.DataFrame(
            {
                "weather_zone": zone,
                "ts_local": temp_mat.index,
                "temp_f_popwt": weighted_mean(temp_mat, w).to_numpy(),
                "dewpoint_f_popwt": weighted_mean(dew_mat, w).to_numpy(),
            }
        )
        del temp_mat, dew_mat
        z = add_zone_features(z)
        nan_pct = z["temp_f_popwt"].isna().mean()
        print(
            f"  {zone}: {len(z):,} rows {z['ts_local'].min()} → {z['ts_local'].max()} | "
            f"stations {list(w.index)} weights {[round(x, 3) for x in w.to_list()]} | "
            f"temp_popwt NaN {nan_pct:.2%}"
        )
        zone_frames.append(z)

    if not zone_frames:
        raise RuntimeError("no zones could be built — is data/raw/weather/ empty?")
    out = pd.concat(zone_frames, ignore_index=True)
    out = out.sort_values(["weather_zone", "ts_local"]).reset_index(drop=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_path, index=False)
    print(f"zone_weather_hourly: {len(out):,} rows → {out_path}  (weights: {source})")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Build zone_weather_hourly from the station cache")
    ap.add_argument("--out", type=Path, default=OUT_PATH,
                    help="output parquet (default: data/derived/zone_weather_hourly.parquet)")
    args = ap.parse_args()
    build_zone_weather(args.out)


if __name__ == "__main__":
    main()
