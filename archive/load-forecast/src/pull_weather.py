"""Task 02 (weather half): NOAA Global Hourly (ISD in CSV) → weather_hourly cache.

Source  : https://noaa-global-hourly-pds.s3.amazonaws.com/{year}/{USAF}{WBAN}.csv
          AWS Open Data, PUBLIC bucket — anonymous plain-HTTPS GET, no boto3, no
          awconnect, no corporate AWS profile. Layout verified 2026-08-14.
Raw cache: data/raw/weather/{USAF-WBAN}_{year}.parquet — canonical weather_hourly
          schema: station_id | ts_local | temp_f | dewpoint_f | qc_flag.
Cache-first: an existing station-year parquet is never re-downloaded (delete the
file to force a refresh — the current, incomplete year especially).

Pipeline per station-year (strictly one at a time — 8 GiB cgroup cap):
 1. GET the CSV (404 → warn + skip, other HTTP errors raise)
 2. parse TMP/DEW "+0261,1" → tenths-°C + element QC code; +9999 = missing;
    QC codes 3/7 (erroneous) → NaN; convert to °F
 3. physical QC: temp outside −30..130 °F → NaN; dewpoint outside the same
    bounds → NaN; dewpoint > temp + 3 °F → dewpoint NaN
 4. keep hourly-representative reports (summaries SOD/SOM excluded; FM-15/METAR
    family preferred) and collapse sub-hourly to ONE obs per UTC hour-ending
    bucket (t−1h, t] — best report rank, then nearest the top of the hour
 5. reindex to the complete UTC hourly grid for the file year, then linear-
    interpolate gaps ≤ 3 consecutive hours (qc_flag='interp'); longer gaps stay
    NaN (qc_flag='suspect'); untouched obs are 'raw'
 6. label hour-ending local CPT (tz-naive) — see TIMEZONE below.

TIMEZONE / DST (must line up with pull_load.py's ts_local = date + he hours):
ISD DATE is UTC. Each physical hour (t−1h, t] is labeled with the local WALL
CLOCK OF ITS START + 1 h, which reproduces ERCOT's hour-ending labels exactly
(verified against ercotLoadView 2023 DST days):
  * spring forward — label 03:00 never occurs (23 labels that day, he=3 absent
    in the load view too). It is a real absence, NOT a gap: interpolation runs
    on the physically-uniform UTC grid *before* labeling, so nothing is ever
    interpolated "across" the jump.
  * fall back — two physical hours map to label 02:00 → keep the FIRST (the CDT
    hour), giving 24 labels, matching the load view.
A station-year file covers the UTC year, so ts_local spans Dec-31 ~19:00 of the
prior year → Dec-31 18:00 CST. Consecutive year files are contiguous and never
overlap; gaps touching a file edge stay 'suspect' (no anchor to interpolate).

Run:
  uv run python load-forecast/src/pull_weather.py --stations 722590-03927 \
      --start-year 2023 --end-year 2023
  (default stations = crosswalk stations if present, else provisional anchors;
   default years = 2015..2026)
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg

WEATHER_RAW_DIR = cfg.RAW_DIR / "weather"
BUCKET_URL = "https://noaa-global-hourly-pds.s3.amazonaws.com"
LOCAL_TZ = "America/Chicago"

TEMP_BOUNDS_F = (-30.0, 130.0)
DEW_OVER_TEMP_MAX_F = 3.0
MAX_INTERP_HOURS = 3

# ISD element QC codes meaning "erroneous" — everything else passes here and
# the physical bounds do the rest.
_BAD_VALUE_QC = {"3", "7"}
# Daily/monthly summary report types — never hourly observations.
_SUMMARY_TYPES = {"SOD", "SOM"}
# Per-hour preference: METAR family first, synop-merged/synop last, unknown worst.
_REPORT_RANK = {"FM-15": 0, "SAO": 1, "FM-16": 2, "SY-MT": 3, "SY-SA": 3, "FM-12": 4}
_DEFAULT_RANK = 5


def station_file_id(station_id: str) -> str:
    """'722590-03927' → '72259003927' (USAF zero-padded to 6, WBAN to 5)."""
    usaf, wban = station_id.split("-")
    return f"{usaf.zfill(6)}{wban.zfill(5)}"


def cache_path(station_id: str, year: int) -> Path:
    return WEATHER_RAW_DIR / f"{station_id}_{year}.parquet"


def download_csv(station_id: str, year: int, session: requests.Session | None = None) -> str | None:
    """Anonymous GET of one station-year CSV. 404 → None; other errors raise."""
    url = f"{BUCKET_URL}/{year}/{station_file_id(station_id)}.csv"
    get = (session or requests).get
    resp = get(url, timeout=180)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.text


def _element_to_f(raw: pd.Series) -> pd.Series:
    """ISD element '+0261,1' → °F. +9999 (missing) or QC code 3/7 → NaN."""
    parts = raw.fillna("").astype(str).str.split(",", n=1, expand=True)
    val = pd.to_numeric(parts[0], errors="coerce")
    if parts.shape[1] > 1:
        qc = parts[1].fillna("").str.strip()
    else:
        qc = pd.Series("", index=raw.index)
    val = val.where(val.abs() < 9000)  # 9999 in tenths-°C is the missing sentinel
    val = val.where(~qc.isin(_BAD_VALUE_QC))
    return val / 10.0 * 9.0 / 5.0 + 32.0


def parse_global_hourly_csv(text: str) -> pd.DataFrame:
    """CSV text → obs frame [ts_utc (tz-aware UTC), report_type, temp_f, dewpoint_f]."""
    df = pd.read_csv(
        io.StringIO(text),
        usecols=lambda c: c in {"DATE", "REPORT_TYPE", "TMP", "DEW"},
        dtype=str,
        low_memory=False,
    )
    for col in ("TMP", "DEW", "REPORT_TYPE"):
        if col not in df.columns:
            df[col] = pd.NA
    return pd.DataFrame(
        {
            "ts_utc": pd.to_datetime(df["DATE"], utc=True),
            "report_type": df["REPORT_TYPE"].fillna("").str.strip(),
            "temp_f": _element_to_f(df["TMP"]),
            "dewpoint_f": _element_to_f(df["DEW"]),
        }
    )


def qc_physical(obs: pd.DataFrame) -> pd.DataFrame:
    """Drop physically impossible values (→ NaN). Never drops rows."""
    out = obs.copy()
    t = out["temp_f"]
    d = out["dewpoint_f"]
    t = t.where((t >= TEMP_BOUNDS_F[0]) & (t <= TEMP_BOUNDS_F[1]))
    d = d.where((d >= TEMP_BOUNDS_F[0]) & (d <= TEMP_BOUNDS_F[1]))
    d = d.where(~(t.notna() & (d > t + DEW_OVER_TEMP_MAX_F)))  # supersaturation slack 3 °F
    out["temp_f"] = t
    out["dewpoint_f"] = d
    return out


def collapse_to_utc_hours(obs: pd.DataFrame) -> pd.DataFrame:
    """ONE row per UTC hour-ending bucket (t−1h, t]: exclude summary reports,
    prefer the METAR family, break ties by nearest-the-top-of-hour."""
    o = obs[~obs["report_type"].isin(_SUMMARY_TYPES)]
    o = o[o["temp_f"].notna() | o["dewpoint_f"].notna()].copy()
    if o.empty:
        return pd.DataFrame(columns=["temp_f", "dewpoint_f"], dtype=float)
    o["he_utc"] = o["ts_utc"].dt.ceil("h")  # obs exactly on the hour stays in that HE
    o["rank"] = o["report_type"].map(_REPORT_RANK).fillna(_DEFAULT_RANK).astype(int)
    o["dist_s"] = (o["he_utc"] - o["ts_utc"]).dt.total_seconds()
    o = o.sort_values(["he_utc", "rank", "dist_s"], kind="stable")
    o = o.drop_duplicates("he_utc", keep="first")
    return o.set_index("he_utc")[["temp_f", "dewpoint_f"]]


def _interp_short_gaps(s: pd.Series, max_gap: int) -> tuple[pd.Series, pd.Series]:
    """Linear-fill NaN runs of length ≤ max_gap that have anchors on BOTH sides
    (edge runs stay NaN). Returns (filled series, was-filled mask)."""
    isna = s.isna()
    run_id = (isna != isna.shift()).cumsum()
    run_len = isna.groupby(run_id).transform("size")
    fillable = isna & (run_len <= max_gap)
    filled_all = s.interpolate(method="linear", limit_area="inside")
    out = s.copy()
    out[fillable] = filled_all[fillable]
    return out, fillable & out.notna()


def year_utc_grid(year: int) -> pd.DatetimeIndex:
    """Complete UTC hour-ending grid for a file year: Jan-1 01:00Z … Jan-1 00:00Z
    of the next year (8760/8784 labels). The current year truncates at 'now'."""
    start = pd.Timestamp(f"{year}-01-01 01:00", tz="UTC")
    end = pd.Timestamp(f"{year + 1}-01-01 00:00", tz="UTC")
    now_floor = pd.Timestamp.now(tz="UTC").floor("h")
    return pd.date_range(start, min(end, now_floor), freq="h")


def process_observations(
    obs: pd.DataFrame, grid: pd.DatetimeIndex, max_gap: int = MAX_INTERP_HOURS
) -> pd.DataFrame:
    """obs [ts_utc, report_type, temp_f, dewpoint_f] → canonical hourly frame
    [ts_local, temp_f, dewpoint_f, qc_flag] on the given UTC hour-ending grid.

    Order matters: QC → collapse → reindex to the uniform UTC grid → interpolate
    → THEN label local. DST can therefore never fabricate or bridge gaps."""
    hourly = collapse_to_utc_hours(qc_physical(obs)).reindex(grid)
    temp, t_filled = _interp_short_gaps(hourly["temp_f"], max_gap)
    dew, d_filled = _interp_short_gaps(hourly["dewpoint_f"], max_gap)

    qc = pd.Series("raw", index=grid, dtype=object)
    qc[(t_filled | d_filled).to_numpy()] = "interp"
    qc[(temp.isna() | dew.isna()).to_numpy()] = "suspect"

    # Hour-ending local label = wall clock of the hour START + 1h (ERCOT he
    # convention: spring-forward day skips 03:00, fall-back day repeats 02:00).
    start_wall = (grid - pd.Timedelta(hours=1)).tz_convert(LOCAL_TZ).tz_localize(None)
    out = pd.DataFrame(
        {
            "ts_local": start_wall + pd.Timedelta(hours=1),
            "temp_f": temp.to_numpy(),
            "dewpoint_f": dew.to_numpy(),
            "qc_flag": qc.to_numpy(),
        }
    )
    # Fall-back duplicate local hour: keep first (grid is UTC-ordered → CDT hour).
    return out.drop_duplicates("ts_local", keep="first").reset_index(drop=True)


def pull_station_year(
    station_id: str, year: int, session: requests.Session | None = None
) -> Path | None:
    """Download+process one station-year, cache-first. Returns the parquet path,
    or None when the bucket has no file / the year is entirely in the future."""
    path = cache_path(station_id, year)
    if path.exists():
        print(f"  {station_id} {year}: cached ({path.name})")
        return path
    grid = year_utc_grid(year)
    if len(grid) == 0:
        print(f"  {station_id} {year}: year is in the future — skipped")
        return None
    text = download_csv(station_id, year, session=session)
    if text is None:
        print(f"  WARNING {station_id} {year}: 404 — no file in bucket, skipped")
        return None
    obs = parse_global_hourly_csv(text)
    del text
    df = process_observations(obs, grid)
    del obs
    df.insert(0, "station_id", station_id)
    WEATHER_RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    counts = df["qc_flag"].value_counts()
    print(
        f"  {station_id} {year}: {len(df):,} rows | "
        f"raw {counts.get('raw', 0):,} / interp {counts.get('interp', 0):,} / "
        f"suspect {counts.get('suspect', 0):,} | "
        f"temp NaN {df['temp_f'].isna().mean():.2%}"
    )
    del df
    return path


def pull_weather(stations, years) -> list[Path]:
    """Pull many station-years, strictly one at a time (8 GiB cap). `stations`
    may be plain 'USAF-WBAN' strings or tuples whose first element is the id."""
    ids = [s[0] if isinstance(s, (tuple, list)) else s for s in stations]
    session = requests.Session()
    written: list[Path] = []
    for sid in ids:
        for year in years:
            p = pull_station_year(sid, year, session=session)
            if p is not None:
                written.append(p)
    return written


def _default_stations() -> list[str]:
    """Crosswalk stations when the crosswalk exists, else provisional anchors."""
    import zone_weather  # deferred: zone_weather imports this module at top level

    weights, source = zone_weather.get_station_weights()
    ids = sorted({sid for z in weights.values() for sid in z})
    print(f"stations from {source}: {ids}")
    return ids


def main() -> None:
    ap = argparse.ArgumentParser(description="Pull NOAA Global Hourly station-years → parquet cache")
    ap.add_argument("--stations", type=str, default=None,
                    help="comma-separated USAF-WBAN ids (default: crosswalk/provisional set)")
    ap.add_argument("--start-year", type=int, default=cfg.HISTORY_START_YEAR)
    ap.add_argument("--end-year", type=int, default=2026)
    args = ap.parse_args()

    stations = (
        [s.strip() for s in args.stations.split(",") if s.strip()]
        if args.stations
        else _default_stations()
    )
    years = list(range(args.start_year, args.end_year + 1))
    print(f"pulling {len(stations)} station(s) × {years[0]}–{years[-1]} → {WEATHER_RAW_DIR}")
    written = pull_weather(stations, years)
    print(f"done: {len(written)} station-year file(s) available")


if __name__ == "__main__":
    main()
