"""Task 02 (load half): pull AW.dbo.ercotLoadView → load_hourly.

Raw cache : data/raw/load/ercot_load_{year}.parquet  (wide — all zone columns)
Derived   : data/derived/load_hourly.parquet         (long — canonical schema:
            weather_zone | ts_local | load_mw | event_flag)

One SQL Server query per year, strictly sequential, date-bounded. Cache-first:
an existing year file is never re-queried (delete it to force a refresh).

ts_local is the naive hour-ending CPT label: date 00:00 + he hours (he=1 →
01:00). This mirrors how ERCOT publishes; DST anomalies show up as per-year
row counts ≠ 8760/8784 and are reported by the QC summary, not "fixed".

Run:  uv run python load-forecast/src/pull_load.py [--start-year 2015] [--end-year 2026]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg

LOAD_RAW_DIR = cfg.RAW_DIR / "load"
LOAD_HOURLY_PATH = cfg.DERIVED_DIR / "load_hourly.parquet"

_PULL_COLUMNS = ["date", "he", cfg.SYSTEM_COLUMN] + list(cfg.ZONE_COLUMNS.values())


def _year_cache_path(year: int) -> Path:
    return LOAD_RAW_DIR / f"ercot_load_{year}.parquet"


def _query_year(year: int) -> pd.DataFrame:
    """ONE date-bounded query for one calendar year. Callers must stay sequential."""
    cfg.configure()
    from awconnect import db

    cols = ", ".join(_PULL_COLUMNS)
    sql = f"""
        SELECT {cols}
        FROM AW.dbo.ercotLoadView
        WHERE date BETWEEN '{year}-01-01' AND '{year}-12-31'
        ORDER BY date, he
    """
    return db.getDfFromAwDb(sql, database="AW")


def _cache_is_fresh(path: Path, year: int) -> bool:
    """A cached year is fresh if it reaches year-end, or (current year) through
    yesterday. Prevents a partial current-year pull from freezing forever."""
    if not path.exists():
        return False
    cached_max = str(pd.read_parquet(path, columns=["date"])["date"].max())[:10]
    target = min(
        pd.Timestamp(f"{year}-12-31"), pd.Timestamp.now().normalize() - pd.Timedelta(days=1)
    ).strftime("%Y-%m-%d")
    return cached_max >= target


def pull_year(year: int) -> pd.DataFrame:
    """One year of the wide view, cache-first (stale partial years re-queried)."""
    path = _year_cache_path(year)
    if _cache_is_fresh(path, year):
        return pd.read_parquet(path)
    df = _query_year(year)
    if df.empty:
        raise RuntimeError(
            f"ercotLoadView returned 0 rows for {year} — do not cache; "
            "check coverage before falling back to ERCOT archives."
        )
    LOAD_RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return df


def event_flag(ts: pd.Series, zone: str) -> pd.Series:
    """null / 'covid' / 'uri' / 'outage' per CLAUDE.md event windows.

    Day membership uses the (ts − 1h) date so HE24 stays on its own day —
    keying off the raw label date shifts every window one hour early
    (HE24 of the day BEFORE a window would be flagged; the window's own
    HE24 would not be)."""
    d = (ts - pd.Timedelta(hours=1)).dt.strftime("%Y-%m-%d")
    flag = pd.Series(pd.NA, index=ts.index, dtype="string")
    flag[(d >= cfg.COVID_WINDOW[0]) & (d <= cfg.COVID_WINDOW[1])] = "covid"
    flag[(d >= cfg.URI_WINDOW[0]) & (d <= cfg.URI_WINDOW[1])] = "uri"
    for start, end, zones in cfg.OUTAGE_WINDOWS:
        if zone in zones:
            flag[(d >= start) & (d <= end)] = "outage"
    return flag


def build_load_hourly(years: list[int]) -> pd.DataFrame:
    """Melt cached wide years into the canonical long load_hourly table."""
    frames = []
    for year in years:  # sequential by design — never parallelize DB pulls
        wide = pull_year(year)
        wide = wide.copy()
        wide["ts_local"] = pd.to_datetime(wide["date"].astype(str)) + pd.to_timedelta(
            wide["he"].astype(int), unit="h"
        )
        for zone in cfg.ZONES:
            col = cfg.ZONE_COLUMNS[zone]
            zf = pd.DataFrame(
                {
                    "weather_zone": zone,
                    "ts_local": wide["ts_local"],
                    "load_mw": pd.to_numeric(wide[col], errors="coerce"),
                }
            )
            zf["event_flag"] = event_flag(zf["ts_local"], zone)  # zone-scoped (outages)
            frames.append(zf)
        del wide
    out = pd.concat(frames, ignore_index=True)
    out = out.sort_values(["weather_zone", "ts_local"]).reset_index(drop=True)
    cfg.DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    out.to_parquet(LOAD_HOURLY_PATH)
    return out


def qc_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per (zone, year): row count, nulls, DAY completeness, min/max MW.

    Raw row counts hide holes — 2016 showed exactly 8,759 rows (the normal
    non-leap count) because the leap day and a missing 24-hour day cancelled.
    missing_days / short_days are the real check (year via ts−1h so HE24 of
    Dec 31 counts in its own year)."""
    day = (df["ts_local"] - pd.Timedelta(hours=1)).dt.normalize()
    d = df.assign(day=day, year=day.dt.year)
    per_day = d.groupby(["weather_zone", "year", "day"])["load_mw"].size().rename("n_hours")
    days = per_day.reset_index()
    g = d.groupby(["weather_zone", "year"])
    qc = g.agg(
        rows=("load_mw", "size"),
        nulls=("load_mw", lambda s: int(s.isna().sum())),
        min_mw=("load_mw", "min"),
        max_mw=("load_mw", "max"),
    ).reset_index()
    dd = days.groupby(["weather_zone", "year"]).agg(n_days=("day", "size")).reset_index()
    qc = qc.merge(dd, on=["weather_zone", "year"])
    is_current = qc["year"] == int(pd.Timestamp.now().year)
    expected = pd.Series(
        [pd.Timestamp(f"{y}-12-31").dayofyear for y in qc["year"]], index=qc.index
    )
    qc["missing_days"] = (expected - qc["n_days"]).where(~is_current, 0).clip(lower=0)
    return qc


def completeness_report(df: pd.DataFrame) -> pd.DataFrame:
    """Every (zone, date) that is absent or has <23 hours, over the full span.
    23-hour days on DST spring-forward Sundays are normal and excluded here;
    everything else is a data hole to investigate upstream."""
    day = (df["ts_local"] - pd.Timedelta(hours=1)).dt.normalize()
    rows = []
    for zone, grp in df.assign(day=day).groupby("weather_zone"):
        counts = grp.groupby("day")["load_mw"].size()
        full = pd.date_range(counts.index.min(), counts.index.max(), freq="D")
        counts = counts.reindex(full, fill_value=0)
        # spring-forward Sundays (2nd Sunday of March) legitimately have 23h
        dst = (counts.index.month == 3) & (counts.index.weekday == 6) & (counts.index.day <= 14) & (counts.index.day > 7)
        bad = counts[(counts < 24) & ~((counts == 23) & dst)]
        for dt, n in bad.items():
            rows.append({"weather_zone": zone, "date": str(dt.date()), "n_hours": int(n)})
    return pd.DataFrame(rows, columns=["weather_zone", "date", "n_hours"])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start-year", type=int, default=cfg.HISTORY_START_YEAR)
    ap.add_argument("--end-year", type=int, default=2026)
    args = ap.parse_args()

    years = list(range(args.start_year, args.end_year + 1))
    df = build_load_hourly(years)
    print(f"load_hourly: {len(df):,} rows → {LOAD_HOURLY_PATH}")
    print(qc_summary(df).to_string(index=False))
    holes = completeness_report(df)
    if len(holes):
        print(f"\nDATA HOLES ({len(holes)} zone-days incomplete or missing):")
        print(holes.to_string(index=False))
    else:
        print("\ncompleteness: no missing/short days beyond DST")


if __name__ == "__main__":
    main()
