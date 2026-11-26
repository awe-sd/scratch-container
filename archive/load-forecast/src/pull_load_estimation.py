"""Task 09 step 1 -- pull AW.DBO.ERCOTLOADESTIMATION_TERM_BAL / _STATION_BAL /
_BAD_INTERVALS (Snowflake) for an explicit station list, cache-first, one
parquet file per station (mirrors pull_station_load.py's cache layout).

Source and platform (see docs/load_estimation_schema.md -- trust that doc over
anything else if they disagree):
  - Snowflake `AW.DBO` ONLY. `AWDev` on Snowflake carries ZERO rows for this
    family -- it lives only under `AW`. Do not query AWDev for this family.
  - NO `run_id` column on the Snowflake copy (SQL Server has one; Snowflake
    doesn't). Never add `WHERE run_id = ...` here.
  - Grain: `term_bal` is (se_timestamp, station, kv); `station_bal` is
    (se_timestamp, station). `TERMINAL` is a serialized label of (station, kv),
    not a finer grain (schema doc Sec 3.1).
  - Hourly, one snapshot per hour stamped at :57 past the hour (schema doc
    Sec 3.4) -- there is no intra-hour averaging to do.

MANDATORY trap avoidance (schema doc Sec 0, Sec 3.2; task spec Sec 2.1/2.2):
  - `term_bal` is summed over `kv` PER (station, se_timestamp) IN THE SQL
    ITSELF (GROUP BY station, se_timestamp) before this module ever returns a
    row. This is what makes joining term_bal's output to station_bal safe --
    both sides are already at (station, se_timestamp) grain, so the pandas
    merge in injection_benchmark.py cannot fan out.
  - The plain `STATION_EST_LOAD_MW` / `STATION_EST_GENERATION_MW` /
    `STATION_NET_LOAD_MW` columns on `station_bal` are NEVER queried here --
    they are zeroed by the pipeline itself for a meaningful share of
    PUN-scored station-hours (proved in the schema doc: SNDSW at
    2026-02-20 00:57 reads STATION_EST_LOAD_MW=0.0 while the RAW_ column and
    term_bal both read 685.46 MW). Only `RAW_STATION_*` columns are pulled.
  - `pun_score` / `unresolved_xfmr_count` / `coverage_flag` are carried through
    RAW, with NULLs left as NULL (not coalesced to 0 -- 2.2% of station_bal
    rows have NULL pun_score, exactly where COVERAGE_FLAG is also NULL --
    unresolved topology, not "clean").
  - Values are kept signed. No flooring at zero anywhere in this module.
  - Snowflake returns SUM()/aggregate NUMBER columns as Python Decimal
    objects (`object` dtype in pandas, verified empirically 2026-08-26 --
    TOTAL_EST_LOAD_MW etc. came back `dtype=object`, not float64). Every
    numeric column is explicitly cast to float64 immediately after each
    query in this module -- skip that cast and every downstream comparison
    silently degrades to slow/broken object-dtype arithmetic.

Raw cache (mirrors pull_station_load.py's per-station parquet layout):
  data/raw/load_estimation/term_bal/{station}.parquet
    columns: STATION, SE_TIMESTAMP, TOTAL_EST_LOAD_MW, TOTAL_EST_GENERATION_MW,
             TOTAL_NET_LOAD_MW, PUN_TOTAL_EST_LOAD_MW, PUN_TOTAL_EST_GENERATION_MW,
             PUN_TOTAL_NET_LOAD_MW, KV_COUNT
    (the PUN_TOTAL_* columns are gross behind-the-meter PUN quantities, pulled
    for CONTEXT/reporting only -- TOTAL_* remains the grid-facing comparison
    basis against ercotStationLoad; see _query_term_bal_batch's docstring)
  data/raw/load_estimation/station_bal/{station}.parquet
    columns: STATION, SE_TIMESTAMP, RAW_STATION_EST_LOAD_MW,
             RAW_STATION_EST_GENERATION_MW, RAW_STATION_NET_LOAD_MW,
             PUN_SCORE, UNRESOLVED_XFMR_COUNT, COVERAGE_FLAG
  data/raw/load_estimation/bad_intervals.parquet (single pull, not per-station;
    618 rows total per the schema doc -- still date-bounded on principle)
    columns: INTERVAL, NUM_ENTRIES, QUERY_DATETIME

Cache-first: a station already cached for THIS module's fixed window
(DEFAULT_START/DEFAULT_END) is never re-queried. The cache key is the
station name only (like pull_station_load.py) -- if you need a different
window for a station already cached, delete that station's parquet first;
this module does not detect a window mismatch on its own (documented
limitation, not a silent bug).

Query discipline: `term_bal` is 325M rows / 21 GB on Snowflake; `station_bal`
is 283M rows. Every query is bounded by BOTH an explicit station list
(`WHERE STATION IN (...)`, batched -- see BATCH_SIZE) AND the date window
(`WHERE SE_TIMESTAMP >= ... AND < ...`). Never SELECT *. Empirically
(2026-08-26 probe), the FIRST Snowflake call of a session pays a ~187s
warehouse spin-up; every call after that in the same session was sub-second
even against the full unpruned table -- so batching stations into one
IN-list query (rather than pull_station_load.py's one-station-per-query
style) is a real, measured win here, not a premature optimization: it cuts
~190 stations x 2 tables from ~380 round trips to ~14.

Window default: 2026-01-01 -> 2026-03-04 inclusive (task 09 spec Sec 5). The
family's data stops at 2026-03-04 on Snowflake (schema doc Sec 4) -- querying
past that returns nothing, which would misread as "missing" data rather than
"source doesn't extend that far" if not accounted for downstream.

Run: uv run python load-forecast/src/pull_load_estimation.py [--start-date 2026-01-01] [--end-date 2026-03-04] [--stations JCK,GBY,...]
  (with no --stations flag, pulls the 85-station NCL roster from
  data/derived/ncl_stations.csv, same default universe as pull_station_load.py)
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

LOAD_EST_RAW_DIR = cfg.RAW_DIR / "load_estimation"
TERM_BAL_DIR = LOAD_EST_RAW_DIR / "term_bal"
STATION_BAL_DIR = LOAD_EST_RAW_DIR / "station_bal"
BAD_INTERVALS_PATH = LOAD_EST_RAW_DIR / "bad_intervals.parquet"
NCL_STATIONS_CSV = cfg.DERIVED_DIR / "ncl_stations.csv"

DEFAULT_START = "2026-01-01"
DEFAULT_END = "2026-03-04"  # inclusive; family's Snowflake data stops here
BATCH_SIZE = 30  # stations per IN-list query -- see module docstring

TERM_BAL_COLS = ["STATION", "SE_TIMESTAMP", "TOTAL_EST_LOAD_MW", "TOTAL_EST_GENERATION_MW",
                  "TOTAL_NET_LOAD_MW", "PUN_TOTAL_EST_LOAD_MW", "PUN_TOTAL_EST_GENERATION_MW",
                  "PUN_TOTAL_NET_LOAD_MW", "KV_COUNT"]
TERM_BAL_FLOAT_COLS = ["TOTAL_EST_LOAD_MW", "TOTAL_EST_GENERATION_MW", "TOTAL_NET_LOAD_MW",
                        "PUN_TOTAL_EST_LOAD_MW", "PUN_TOTAL_EST_GENERATION_MW", "PUN_TOTAL_NET_LOAD_MW"]

STATION_BAL_COLS = ["STATION", "SE_TIMESTAMP", "RAW_STATION_EST_LOAD_MW", "RAW_STATION_EST_GENERATION_MW",
                     "RAW_STATION_NET_LOAD_MW", "PUN_SCORE", "UNRESOLVED_XFMR_COUNT", "COVERAGE_FLAG"]
STATION_BAL_FLOAT_COLS = ["RAW_STATION_EST_LOAD_MW", "RAW_STATION_EST_GENERATION_MW",
                           "RAW_STATION_NET_LOAD_MW", "PUN_SCORE"]

BAD_INTERVALS_COLS = ["INTERVAL", "NUM_ENTRIES", "QUERY_DATETIME"]


def _end_exclusive(end_date: str) -> str:
    """SE_TIMESTAMP upper bound is exclusive; end_date is inclusive on input."""
    return (pd.Timestamp(end_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")


def _station_in_list(stations: list[str]) -> str:
    return ", ".join("'{}'".format(s.replace("'", "''")) for s in stations)


def _cast_floats(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Snowflake SUM()/aggregate NUMBER columns come back as Decimal objects
    (pandas dtype=object) -- cast explicitly, see module docstring."""
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype(float)
    return df


def _empty_frame(cols: list[str]) -> pd.DataFrame:
    return pd.DataFrame({c: pd.Series(dtype="object") for c in cols})


def _term_bal_cache_path(station: str) -> Path:
    return TERM_BAL_DIR / f"{station}.parquet"


def _station_bal_cache_path(station: str) -> Path:
    return STATION_BAL_DIR / f"{station}.parquet"


def _query_term_bal_batch(stations: list[str], start_date: str, end_date: str) -> pd.DataFrame:
    """ONE date-bounded query covering an explicit list of stations. Sums over
    kv IN SQL (GROUP BY) -- this is what makes the term_bal/station_bal merge
    downstream safe from the kv fan-out trap (task spec Sec 3.1 / schema doc
    Sec 3.1).

    Also pulls the PUN_TOTAL_* siblings alongside TOTAL_*. These are NOT an
    alternate value to compare against ercotStationLoad (TOTAL_*/RAW_STATION_*
    remain the grid-facing comparison basis, per sdalvi 2026-08-26) -- they
    are the gross behind-the-meter quantity for stations that are private use
    networks (PUNs), pulled ONLY for context/reporting. Confirmed 2026-08-26:
    JCK's TOTAL_EST_LOAD_MW (grid-facing, ~25 MW) and PUN_TOTAL_EST_LOAD_MW
    (gross internal PUN load, ~800 MW weekly avg) are genuinely DIFFERENT
    quantities, not a bug -- conflating them (as every older doc in this repo
    did before this) manufactures a ~32x "error" that is not a disagreement
    between sources at all, just gross-vs-grid-facing confusion."""
    from pfa import sf

    end_excl = _end_exclusive(end_date)
    in_list = _station_in_list(stations)
    df = sf.query(
        "AW",
        f"""
        SELECT STATION, SE_TIMESTAMP,
               SUM(TOTAL_EST_LOAD_MW) AS TOTAL_EST_LOAD_MW,
               SUM(TOTAL_EST_GENERATION_MW) AS TOTAL_EST_GENERATION_MW,
               SUM(TOTAL_NET_LOAD_MW) AS TOTAL_NET_LOAD_MW,
               SUM(PUN_TOTAL_EST_LOAD_MW) AS PUN_TOTAL_EST_LOAD_MW,
               SUM(PUN_TOTAL_EST_GENERATION_MW) AS PUN_TOTAL_EST_GENERATION_MW,
               SUM(PUN_TOTAL_NET_LOAD_MW) AS PUN_TOTAL_NET_LOAD_MW,
               COUNT(DISTINCT KV) AS KV_COUNT
        FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
        WHERE STATION IN ({in_list})
          AND SE_TIMESTAMP >= '{start_date}' AND SE_TIMESTAMP < '{end_excl}'
        GROUP BY STATION, SE_TIMESTAMP
        ORDER BY STATION, SE_TIMESTAMP
        """,
    )
    df.columns = [c.upper() for c in df.columns]
    if df.empty:
        df = _empty_frame(TERM_BAL_COLS)
    return _cast_floats(df, TERM_BAL_FLOAT_COLS)


def _query_station_bal_batch(stations: list[str], start_date: str, end_date: str) -> pd.DataFrame:
    """ONE date-bounded query covering an explicit list of stations. RAW_
    columns only -- never the plain STATION_EST_*/STATION_NET_LOAD_MW columns
    (pipeline-zeroed, see module docstring). pun_score / unresolved_xfmr_count
    / coverage_flag kept as raw NULLs, not coalesced."""
    from pfa import sf

    end_excl = _end_exclusive(end_date)
    in_list = _station_in_list(stations)
    df = sf.query(
        "AW",
        f"""
        SELECT STATION, SE_TIMESTAMP,
               RAW_STATION_EST_LOAD_MW, RAW_STATION_EST_GENERATION_MW,
               RAW_STATION_NET_LOAD_MW, PUN_SCORE, UNRESOLVED_XFMR_COUNT,
               COVERAGE_FLAG
        FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
        WHERE STATION IN ({in_list})
          AND SE_TIMESTAMP >= '{start_date}' AND SE_TIMESTAMP < '{end_excl}'
        ORDER BY STATION, SE_TIMESTAMP
        """,
    )
    df.columns = [c.upper() for c in df.columns]
    if df.empty:
        df = _empty_frame(STATION_BAL_COLS)
    return _cast_floats(df, STATION_BAL_FLOAT_COLS)


def pull_bad_intervals(start_date: str = DEFAULT_START, end_date: str = DEFAULT_END) -> pd.DataFrame:
    """Cache-first pull of the (small, 618-row-total) bad-intervals table,
    still date-bounded on principle. Not per-station."""
    if BAD_INTERVALS_PATH.exists():
        return pd.read_parquet(BAD_INTERVALS_PATH)
    from pfa import sf

    end_excl = _end_exclusive(end_date)
    df = sf.query(
        "AW",
        f"""
        SELECT INTERVAL, NUM_ENTRIES, QUERY_DATETIME
        FROM AW.DBO.ERCOTLOADESTIMATION_BAD_INTERVALS
        WHERE INTERVAL >= '{start_date}' AND INTERVAL < '{end_excl}'
        """,
    )
    df.columns = [c.upper() for c in df.columns]
    if df.empty:
        df = _empty_frame(BAD_INTERVALS_COLS)
    LOAD_EST_RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(BAD_INTERVALS_PATH)
    return df


def pull_term_bal(station: str, start_date: str = DEFAULT_START, end_date: str = DEFAULT_END) -> pd.DataFrame:
    """Cache-first pull of term_bal (kv-summed) for ONE station. For many
    stations at once, prefer pull_all() (batched queries, one parquet each)."""
    path = _term_bal_cache_path(station)
    if path.exists():
        return pd.read_parquet(path)
    df = _query_term_bal_batch([station], start_date, end_date)
    TERM_BAL_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return df


def pull_station_bal(station: str, start_date: str = DEFAULT_START, end_date: str = DEFAULT_END) -> pd.DataFrame:
    """Cache-first pull of station_bal (RAW_ columns) for ONE station. For
    many stations at once, prefer pull_all() (batched queries, one parquet
    each)."""
    path = _station_bal_cache_path(station)
    if path.exists():
        return pd.read_parquet(path)
    df = _query_station_bal_batch([station], start_date, end_date)
    STATION_BAL_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return df


def pull_all(stations: list[str], start_date: str = DEFAULT_START, end_date: str = DEFAULT_END,
             batch_size: int = BATCH_SIZE) -> pd.DataFrame:
    """Cache-first pull for every station, batched into explicit-IN-list
    queries (never one-row-at-a-time, never unbounded) for whichever stations
    aren't already cached. Writes one parquet per station either way, so a
    re-run only pays for what's missing. Returns a small per-station summary
    frame (station-level data is not retained in memory after caching, per
    the 8 GiB container cap)."""
    pull_bad_intervals(start_date, end_date)
    TERM_BAL_DIR.mkdir(parents=True, exist_ok=True)
    STATION_BAL_DIR.mkdir(parents=True, exist_ok=True)

    need_term = [s for s in stations if not _term_bal_cache_path(s).exists()]
    need_stat = [s for s in stations if not _station_bal_cache_path(s).exists()]

    for i in range(0, len(need_term), batch_size):
        chunk = need_term[i:i + batch_size]
        df = _query_term_bal_batch(chunk, start_date, end_date)
        for s in chunk:
            sub = df[df["STATION"] == s].reset_index(drop=True) if not df.empty else _empty_frame(TERM_BAL_COLS)
            sub.to_parquet(_term_bal_cache_path(s))

    for i in range(0, len(need_stat), batch_size):
        chunk = need_stat[i:i + batch_size]
        df = _query_station_bal_batch(chunk, start_date, end_date)
        for s in chunk:
            sub = df[df["STATION"] == s].reset_index(drop=True) if not df.empty else _empty_frame(STATION_BAL_COLS)
            sub.to_parquet(_station_bal_cache_path(s))

    rows = []
    for station in stations:
        t = pd.read_parquet(_term_bal_cache_path(station))
        st = pd.read_parquet(_station_bal_cache_path(station))
        rows.append({
            "station": station,
            "n_term_bal_rows": len(t),
            "n_station_bal_rows": len(st),
            "matched": len(t) > 0,  # station namespace match -- see task09 Sec 3.6
        })
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start-date", default=DEFAULT_START)
    ap.add_argument("--end-date", default=DEFAULT_END)
    ap.add_argument("--stations", default=None, help="comma-separated station list; default is the 85-station NCL roster")
    args = ap.parse_args()

    if args.stations:
        stations = sorted(set(args.stations.split(",")))
    else:
        if not NCL_STATIONS_CSV.exists():
            print(f"NEEDS_CONTEXT: {NCL_STATIONS_CSV} not found -- run ncl_stations.py first")
            sys.exit(2)
        stations = sorted(pd.read_csv(NCL_STATIONS_CSV)["nmms_station_code"].unique().tolist())

    summary = pull_all(stations, start_date=args.start_date, end_date=args.end_date)
    n_unmatched = int((~summary["matched"]).sum())
    print(f"stations: {len(stations)} total")
    print(f"station namespace match: {len(stations) - n_unmatched}/{len(stations)} had >=1 term_bal row in window")
    if n_unmatched:
        print("unmatched stations (0 term_bal rows in window):")
        print(summary.loc[~summary["matched"], "station"].to_string(index=False))
    print(summary.to_string(index=False))
    print(f"\ncached under {LOAD_EST_RAW_DIR}/")


if __name__ == "__main__":
    main()
