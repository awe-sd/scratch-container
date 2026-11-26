"""Task 07 (NCL exclusion) step 2 -- pull AW.dbo.ercotStationLoad (Snowflake)
for every station in ncl_stations.csv, cache-first, one station per query
(sequential; never parallelized, per repo DB hygiene).

Hour convention (verified 2026-08-15): MIN(HOUR)=0, MAX(HOUR)=23 across the
whole table -> HOUR is HOUR-BEGINNING (0 = midnight-01:00), NOT hour-ending
HE1-24. To align with load_hourly's hour-ending ts_local label (date 00:00 +
he hours, he=1 -> 01:00), station-load hours are shifted by +1:
    ts_local = DATE + (HOUR + 1) hours
e.g. HOUR=0 (midnight-1am) -> ts_local 01:00, matching he=1. This is a range
check, not a correlation guess -- 0..23 can only be hour-beginning (1..24
would be the hour-ending alternative and was ruled out directly).

Table coverage (verified 2026-08-15): 2014-12-03 -> 2026-06-14 overall;
individual stations can start later (a station with no rows before some date
simply didn't have recorded load yet -- not a gap to fill).

Raw cache: data/raw/station_load/{station}.parquet -- columns Date, Hour,
GenMW, WithdrawMW (renamed from Snowflake's uppercase return). Cache-first:
an existing station file is never re-queried (delete it to force a refresh).

Run: uv run python load-forecast/src/pull_station_load.py [--start-date 2015-01-01]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg  # noqa: E402

POWERFLOW_ANALYTICS = cfg.PROJECT_ROOT.parent / "powerflow_analytics"
sys.path.insert(0, str(POWERFLOW_ANALYTICS))

STATION_LOAD_RAW_DIR = cfg.RAW_DIR / "station_load"
NCL_STATIONS_CSV = cfg.DERIVED_DIR / "ncl_stations.csv"

HOUR_SHIFT = 1  # HOUR (0-23, hour-beginning) -> hour-ending label, see module docstring


def _station_cache_path(station: str) -> Path:
    return STATION_LOAD_RAW_DIR / f"{station}.parquet"


def _query_station(station: str, start_date: str) -> pd.DataFrame:
    """ONE date- and station-bounded Snowflake query. Callers stay sequential."""
    from pfa import sf

    safe = station.replace("'", "''")
    df = sf.query(
        "AW",
        f"""
        SELECT DATE, HOUR, GENMW, WITHDRAWMW
        FROM AW.dbo.ercotStationLoad
        WHERE NMMSSTATIONCODE = '{safe}'
          AND DATE >= '{start_date}'
        ORDER BY DATE, HOUR
        """,
    )
    return df.rename(columns={"DATE": "Date", "HOUR": "Hour", "GENMW": "GenMW", "WITHDRAWMW": "WithdrawMW"})


def pull_station(station: str, start_date: str = "2015-01-01") -> pd.DataFrame:
    """Cache-first pull for one station. Returns the cached/pulled frame
    (Date, Hour, GenMW, WithdrawMW)."""
    path = _station_cache_path(station)
    if path.exists():
        return pd.read_parquet(path)
    df = _query_station(station, start_date)
    STATION_LOAD_RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return df


def pull_all(stations: list[str], start_date: str = "2015-01-01") -> pd.DataFrame:
    """Sequential cache-first pull for every station; returns a small summary
    frame (no station-level data is retained in memory after caching, per the
    8 GiB container cap)."""
    rows = []
    for station in stations:  # sequential by design -- never parallelize
        path = _station_cache_path(station)
        cached = path.exists()
        df = pull_station(station, start_date=start_date)
        rows.append({
            "nmms_station_code": station,
            "cached": cached,
            "n_rows": len(df),
            "min_date": str(df["Date"].min()) if len(df) else None,
            "max_date": str(df["Date"].max()) if len(df) else None,
        })
        del df
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start-date", default="2015-01-01")
    args = ap.parse_args()

    if not NCL_STATIONS_CSV.exists():
        print(f"NEEDS_CONTEXT: {NCL_STATIONS_CSV} not found -- run ncl_stations.py first")
        sys.exit(2)
    stations = sorted(pd.read_csv(NCL_STATIONS_CSV)["nmms_station_code"].unique().tolist())

    summary = pull_all(stations, start_date=args.start_date)
    n_new = int((~summary["cached"]).sum())
    n_empty = int((summary["n_rows"] == 0).sum())
    print(f"stations: {len(stations)} total, {n_new} pulled fresh, {len(stations) - n_new} from cache")
    if n_empty:
        print(f"WARNING: {n_empty} station(s) returned 0 rows from ercotStationLoad:")
        print(summary.loc[summary['n_rows'] == 0, 'nmms_station_code'].to_string(index=False))
    print(summary.to_string(index=False))
    print(f"\ncached under {STATION_LOAD_RAW_DIR}/")


if __name__ == "__main__":
    main()
