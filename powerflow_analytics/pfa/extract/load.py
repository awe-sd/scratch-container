"""ERCOT actual system load.

Primary source: SQL Server `AW.dbo.ercotLoadView` (per-year Sep-window pulls,
cached to parquet under cache/ercot_load/). SQL Server hygiene: ONE query at a
time, strictly sequential, never parallel — see powerflow_analytics/CLAUDE.md
and the toAllIsos precedent in pfa/extract/outages.py.

View columns (confirmed 2026-08-13): date, he (1-24), ERCOT_ALL_LD (system
total MW), WZ_*_LD (weather-zone MW). Covers back to at least 2011.

Fallback: if a pre-2024 year comes back empty from SQL Server, pull ERCOT's
published "Native Load" annual archive instead (columns: Hour Ending, COAST,
EAST, FWEST, NORTH, NCENT, SOUTH, SCENT, WEST, ERCOT). "Hour Ending" is a
string like "01/01/2021 01:00", with "24:00" for the last hour of the day,
and occasional " DST" suffix rows marking the repeated fall-back hour (dropped
here to avoid double-counting that HE).
"""
from __future__ import annotations

import re
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

from .. import config

SQL_CACHE_DIR = config.CACHE_ROOT / "ercot_load"
ARCHIVE_CACHE_DIR = config.CACHE_ROOT / "native_load"

# Known ERCOT Native Load archive URLs by year (fallback path only). If a
# future year 404s, look up the fresh URL on ercot.com > Historical RTM Load
# Data / Native Load and add it here.
ARCHIVE_URLS: dict[int, str] = {
    2021: "https://www.ercot.com/files/docs/2021/11/12/Native_Load_2021.zip",
    2022: "https://www.ercot.com/files/docs/2022/02/08/Native_Load_2022.zip",
    2023: "https://www.ercot.com/files/docs/2023/02/09/Native_Load_2023.zip",
}

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

WEATHER_ZONES = ["COAST", "EAST", "FWEST", "NORTH", "NCENT", "SOUTH", "SCENT", "WEST"]


def _mmdd_to_date(year: int, mmdd: str) -> str:
    mm, dd = mmdd.split("-")
    return f"{year:04d}-{mm}-{dd}"


def _sql_cache_path(year: int, start_mmdd: str, end_mmdd: str, zone: str) -> Path:
    # Zone-specific: the archive fallback (pre-2024, SQL-empty years) writes
    # a frame with only one zone's data under a generic column name, so a
    # shared cache file across zones would silently mislabel one zone's
    # numbers as another's. Slightly redundant for SQL-sourced years (each
    # zone re-caches the same query) but correct for the fallback path.
    tag = f"{start_mmdd}_{end_mmdd}".replace("-", "")
    return SQL_CACHE_DIR / f"{tag}_{year}_{zone}.parquet"


ZONE_COLUMNS = {
    "ERCOT": "ERCOT_ALL_LD",
    "COAST": "WZ_COAST_LD",
    "EAST": "WZ_EAST_LD",
    "FWEST": "WZ_FAR_WEST_LD",
    "NORTH": "WZ_NORTH_LD",
    "NCENT": "WZ_NORTH_CENTRAL_LD",
    "SOUTH": "WZ_SOUTHERN_LD",
    "SCENT": "WZ_SOUTH_CENTRAL_LD",
    "WEST": "WZ_WEST_LD",
}


def _query_load_view(year: int, start_mmdd: str, end_mmdd: str) -> pd.DataFrame:
    """One sequential SQL Server query for one year's date window. Never call
    this in a loop/parallel — see module docstring."""
    config.configure()
    from awconnect import db

    start = _mmdd_to_date(year, start_mmdd)
    end = _mmdd_to_date(year, end_mmdd)
    sql = f"""
        SELECT elv.*
        FROM AW.dbo.ercotLoadView AS elv
        WHERE elv.date BETWEEN '{start}' AND '{end}'
    """
    return db.getDfFromAwDb(sql, database="AW")


# ---------------------------------------------------------------------------
# Archive fallback (pre-2024 years only, if SQL Server comes back empty)
# ---------------------------------------------------------------------------


def _archive_xlsx_path(year: int) -> Path:
    return ARCHIVE_CACHE_DIR / f"Native_Load_{year}.xlsx"


def _ensure_archive_downloaded(year: int) -> Path:
    path = _archive_xlsx_path(year)
    if path.exists():
        return path
    if year not in ARCHIVE_URLS:
        raise ValueError(f"No known Native Load archive URL for {year}")
    ARCHIVE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    resp = requests.get(ARCHIVE_URLS[year], headers={"User-Agent": _UA}, timeout=60)
    resp.raise_for_status()
    with zipfile.ZipFile(BytesIO(resp.content)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(".xlsx")]
        if not names:
            raise ValueError(f"No xlsx found in Native Load archive for {year}")
        path.write_bytes(zf.read(names[0]))
    return path


def _load_archive_year(year: int, zone: str = "ERCOT") -> pd.DataFrame:
    """Parse one year's Native Load xlsx into (date, he, ERCOT_ALL_LD).

    zone: one of WEATHER_ZONES or "ERCOT" (system total) -- these are the
    archive's own column names (confirmed in the module docstring)."""
    path = _ensure_archive_downloaded(year)
    df = pd.read_excel(path)

    col_candidates = [c for c in df.columns if str(c).strip().lower().startswith("hour end")]
    if not col_candidates:
        raise ValueError(f"No 'Hour Ending'-like column in {path}: {list(df.columns)}")
    he_col = col_candidates[0]

    raw = df[he_col].astype(str)
    is_dst_repeat = raw.str.contains("DST", case=False, na=False)
    df = df.loc[~is_dst_repeat].copy()
    raw = raw.loc[~is_dst_repeat]

    parts = raw.str.strip().str.extract(r"^(\d{2}/\d{2}/\d{4})\s+(\d{1,2}):00")
    date_str, hour_str = parts[0], parts[1]
    bad = date_str.isna() | hour_str.isna()
    if bad.any():
        raise ValueError(f"Unparseable Hour Ending values in {path}: {raw[bad].head().tolist()}")

    dates = pd.to_datetime(date_str, format="%m/%d/%Y")
    he = hour_str.astype(int)

    if zone not in df.columns:
        raise ValueError(f"No {zone!r} column in {path}: {list(df.columns)}")

    out = pd.DataFrame(
        {"date": dates.dt.date.astype(str), "he": he.values, "ERCOT_ALL_LD": df[zone].values}
    )
    return out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_load_window(year: int, start_mmdd: str, end_mmdd: str, zone: str = "ERCOT") -> pd.DataFrame:
    """One year's load for a MM-DD..MM-DD date window, cache-first.

    zone: "ERCOT" (system total, default) or a weather-zone key from
    ZONE_COLUMNS (e.g. "NORTH" -> WZ_NORTH_LD).

    Order: local parquet cache (whole ercotLoadView row, all zones -- cache
    is NOT zone-specific) -> SQL Server AW.dbo.ercotLoadView (one sequential
    query) -> ERCOT Native Load archive fallback (pre-2024 only, triggered if
    the SQL Server view returns empty for that year; the archive itself has
    per-zone columns matching WEATHER_ZONES).

    Returns columns: date, he, load_mw (the requested zone's load), year.
    """
    sql_col = "ERCOT_ALL_LD" if zone == "ERCOT" else ZONE_COLUMNS[zone]

    cache_path = _sql_cache_path(year, start_mmdd, end_mmdd, zone)
    if cache_path.exists():
        df = pd.read_parquet(cache_path)
    else:
        df = _query_load_view(year, start_mmdd, end_mmdd)
        if df.empty and year < 2024:
            arc = _load_archive_year(year, zone=zone)
            start = _mmdd_to_date(year, start_mmdd)
            end = _mmdd_to_date(year, end_mmdd)
            mask = (arc["date"] >= start) & (arc["date"] <= end)
            df = arc.loc[mask].reset_index(drop=True)
            # archive path already returns just the one zone under ERCOT_ALL_LD
            sql_col = "ERCOT_ALL_LD"
        SQL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        df.to_parquet(cache_path)

    out = df[["date", "he", sql_col]].rename(columns={sql_col: "load_mw"}).copy()
    out["year"] = year
    return out.reset_index(drop=True)


def median_load_profile(years: list[int], start_mmdd: str, end_mmdd: str, zone: str = "ERCOT") -> pd.DataFrame:
    """Median load by hour-ending across a MM-DD..MM-DD window, per year, for
    one zone ("ERCOT" system total, default, or a WEATHER_ZONES key e.g. "NORTH").

    years: list of calendar years, e.g. [2021, 2022, 2023, 2024, 2025].
    start_mmdd/end_mmdd: "MM-DD" strings, e.g. "09-16", "09-30".

    Returns one row per (year, he): year, he, median_load_gw.
    """
    rows = []
    for year in years:
        df = get_load_window(year, start_mmdd, end_mmdd, zone=zone)
        med = df.groupby("he")["load_mw"].median().reset_index()
        med["median_load_gw"] = med["load_mw"] / 1000.0
        med["year"] = year
        rows.append(med[["year", "he", "median_load_gw"]])
    return (
        pd.concat(rows, ignore_index=True)
        .sort_values(["year", "he"])
        .reset_index(drop=True)
    )
