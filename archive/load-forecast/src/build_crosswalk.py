#!/usr/bin/env python
"""Task 01 — build crosswalk_county_station.csv (static county->station crosswalk).

Builds, per ERCOT weather zone (NCENT, COAST, SCENT):
  - county populations   : Census ACS 2023 5-yr, table B01003 (Census API)
  - county centroids     : Census 2023 Gazetteer counties file (INTPTLAT/INTPTLONG)
  - county -> zone       : user-provided ERCOT mapping (from internal ercotDataDictionary),
                           data/raw/crosswalk/ercot_county_weatherzone.csv  (NOT downloaded)
  - stations             : NOAA ISD history (isd-history.csv), TX ASOS airport stations
                           (ICAO present, USAF != 999999) with records spanning 2015->2025

Selection: per zone, most-populous counties until >= 90% of attributable zone
population; nearest qualifying station within 50 km of the county centroid,
else share the nearest same-zone selected county's station.
weight = county population / sum(selected-county population) per zone.

Cache-first: raw downloads land in data/raw/crosswalk/ and are never re-fetched
while present (delete a file to force refresh). Output:
data/derived/crosswalk_county_station.csv with schema
county_fips, county_name, weather_zone, population, station_id, station_name,
dist_km, weight.

Run from the repo root:  uv run python load-forecast/src/build_crosswalk.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

PROJECT = Path(__file__).resolve().parents[1]  # load-forecast/
RAW_DIR = PROJECT / "data" / "raw" / "crosswalk"
DERIVED_DIR = PROJECT / "data" / "derived"
OUT_CSV = DERIVED_DIR / "crosswalk_county_station.csv"

# ---------------------------------------------------------------- sources ---
# Population: Census PEP county estimates (static file, NO API key needed).
# The ACS API began requiring a key (302 -> missing_key.html, confirmed
# 2026-08-14), so per sdalvi's ruling we use POPESTIMATE2023 from this file
# instead of ACS B01003 — same 2023 vintage, frozen per CLAUDE.md rule 2.
POP_URL = (
    "https://www2.census.gov/programs-surveys/popest/datasets/"
    "2020-2023/counties/totals/co-est2023-alldata.csv"
)
GAZ_URL = (
    "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/"
    "2023_Gazetteer/2023_gaz_counties_48.txt"  # TX-only counties file
)
ISD_URL = "https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv"

POP_FILE = RAW_DIR / "co-est2023-alldata.csv"
GAZ_FILE = RAW_DIR / "2023_gaz_counties_48.txt"
ISD_FILE = RAW_DIR / "isd-history.csv"
ERCOT_MAP_FILE = RAW_DIR / "ercot_county_weatherzone.csv"  # user-provided input

# ------------------------------------------------------------- parameters ---
ZONE_KEYS = {  # WZ_* value in the mapping file -> project zone key
    "WZ_NORTH_CENTRAL": "NCENT",
    "WZ_COAST": "COAST",
    "WZ_SOUTH_CENTRAL": "SCENT",
}
COVERAGE_TARGET = 0.90     # select counties until >= this share of zone pop
MAX_STATION_KM = 50.0      # direct county->station assignment radius
ISD_BEGIN_REQ = 20150101   # station record must start on/before this ...
ISD_END_REQ = 20250101     # ... and end on/after this (spans 2015 -> 2025)
WEIGHT_TOL = 1e-6          # acceptance: per-zone weight sums within this of 1
MATERIALITY = 0.02         # flag ambiguous split counties above this zone share

# Rows in the ERCOT mapping that are not Texas counties (border/tie points and
# one non-county town). Dropped, with a note in docs/crosswalk_sources.md.
NON_TX_ROWS = {
    "CUIDAD ACUNA",
    "MATAMORAS",
    "NUEVEO LAREDO",
    "PIEDRAS NEGRAS",
    "REYNOSA",
    "MEXICO",
    "OKLAHOMA",
    "PITTSBURG",  # a city in Camp County, not a TX county
}

# Split counties (multiple WZ_* rows) resolved to the zone containing the
# county's dominant population center — per sdalvi 2026-08-14 (first three)
# plus TAYLOR, whose population center (Abilene) is in the West zone on every
# ERCOT weather-zone map; assigning it WZ_WEST is equivalent to excluding it
# from SCENT. All decisions documented in docs/crosswalk_sources.md.
SPLIT_OVERRIDES = {
    "COLLIN": "WZ_NORTH_CENTRAL",   # Plano / McKinney / Frisco
    "WILLIAMSON": "WZ_SOUTH_CENTRAL",  # Round Rock / Georgetown (Austin metro)
    "GRAYSON": "WZ_NORTH_CENTRAL",  # Sherman / Denison
    "TAYLOR": "WZ_WEST",            # Abilene -> out of SCENT
}


def fetch(url: str, dest: Path, desc: str, min_bytes: int) -> None:
    """Cache-first download: no-op when dest exists; hard stop on failure."""
    if dest.exists():
        print(f"[cache] {desc}: {dest.name} present, not re-downloading")
        return
    print(f"[fetch] {desc}: {url}")
    try:
        resp = requests.get(url, timeout=180)
        resp.raise_for_status()
    except requests.RequestException as exc:  # unreachable named resource
        print(f"NEEDS_CONTEXT: {desc} unreachable at {url} ({exc})")
        sys.exit(2)
    # A redirect to an HTML error page (e.g. Census missing_key.html) returns
    # 200 with an HTML body — must never be written into a data cache file.
    if resp.headers.get("content-type", "").lower().startswith("text/html"):
        print(f"NEEDS_CONTEXT: {desc} at {url} returned an HTML page, not data "
              f"(final URL: {resp.url})")
        sys.exit(2)
    if len(resp.content) < min_bytes:
        print(
            f"NEEDS_CONTEXT: {desc} at {url} returned only "
            f"{len(resp.content)} bytes — not the expected file"
        )
        sys.exit(2)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(resp.content)
    print(f"[fetch] wrote {dest} ({len(resp.content):,} bytes)")


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km; args in degrees, broadcastable arrays."""
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2.0 * 6371.0088 * np.arcsin(np.sqrt(a))


def load_population() -> pd.DataFrame:
    """POPESTIMATE2023 for all 254 TX counties from the PEP static file."""
    df = pd.read_csv(POP_FILE, encoding="latin-1", dtype={"STATE": str, "COUNTY": str})
    df = df[(df["STATE"] == "48") & (df["COUNTY"] != "000")].copy()
    df["county_fips"] = df["STATE"] + df["COUNTY"]
    # CTYNAME like "Anderson County" -> "Anderson"
    df["county_name"] = df["CTYNAME"].str.replace(r" County$", "", regex=True)
    df["county_key"] = df["county_name"].str.upper().str.strip()
    df["population"] = df["POPESTIMATE2023"].astype(int)
    df = df[["county_fips", "county_name", "county_key", "population"]]
    if len(df) != 254:
        print(f"NEEDS_CONTEXT: PEP file has {len(df)} TX counties, expected 254")
        sys.exit(2)
    return df


def load_gazetteer() -> pd.DataFrame:
    """Census 2023 Gazetteer internal-point centroids for TX counties."""
    df = pd.read_csv(GAZ_FILE, sep="\t", dtype=str, encoding="latin-1")
    df.columns = [c.strip() for c in df.columns]
    df = df[df["USPS"] == "TX"].copy()
    df["lat"] = pd.to_numeric(df["INTPTLAT"])
    df["lon"] = pd.to_numeric(df["INTPTLONG"])
    df = df.rename(columns={"GEOID": "county_fips"})[["county_fips", "lat", "lon"]]
    if len(df) != 254:
        print(f"NEEDS_CONTEXT: Gazetteer has {len(df)} TX counties, expected 254")
        sys.exit(2)
    return df


def load_ercot_map() -> tuple[pd.DataFrame, dict]:
    """User-provided ERCOT county->weather-zone mapping, split-resolved.

    Returns (df[county_key, wz], diagnostics dict).
    """
    if not ERCOT_MAP_FILE.exists():
        print(
            "NEEDS_CONTEXT: ERCOT county->weather-zone mapping not found at "
            f"{ERCOT_MAP_FILE} — this file is user-provided (from "
            "ercotDataDictionary), not downloadable"
        )
        sys.exit(2)
    df = pd.read_csv(ERCOT_MAP_FILE, dtype=str)
    df["county_key"] = df["COUNTY"].str.upper().str.strip()
    df["wz"] = df["WEATHERZONE"].str.upper().str.strip()

    dropped_non_tx = sorted(set(df["county_key"]) & NON_TX_ROWS)
    df = df[~df["county_key"].isin(NON_TX_ROWS)]

    zones_per_county = df.groupby("county_key")["wz"].agg(lambda s: sorted(set(s)))
    split = {k: v for k, v in zones_per_county.items() if len(v) > 1}

    resolved, excluded = {}, {}
    for county, zones in split.items():
        if county in SPLIT_OVERRIDES:
            resolved[county] = SPLIT_OVERRIDES[county]
        else:
            excluded[county] = zones  # ambiguous -> no single-zone attribution

    single = {k: v[0] for k, v in zones_per_county.items() if len(v) == 1}
    single.update(resolved)
    out = pd.DataFrame(
        {"county_key": list(single.keys()), "wz": list(single.values())}
    )
    diag = {
        "dropped_non_tx": dropped_non_tx,
        "split_resolved": {c: SPLIT_OVERRIDES[c] for c in resolved},
        "split_excluded": excluded,
        "n_rows_raw": len(df),
    }
    return out, diag


def load_stations() -> pd.DataFrame:
    """TX ASOS airport stations from isd-history with 2015->2025 record span."""
    df = pd.read_csv(ISD_FILE, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    df["BEGIN_I"] = pd.to_numeric(df["BEGIN"], errors="coerce")
    df["END_I"] = pd.to_numeric(df["END"], errors="coerce")
    df["lat"] = pd.to_numeric(df["LAT"], errors="coerce")
    df["lon"] = pd.to_numeric(df["LON"], errors="coerce")
    icao = df["ICAO"].fillna("").str.strip()
    keep = (
        (df["STATE"] == "TX")
        & (df["CTRY"] == "US")
        & (icao.str.len() >= 3)
        & (df["USAF"] != "999999")
        & df["lat"].notna()
        & df["lon"].notna()
        & (df["lat"].abs() > 0.1)
        & (df["BEGIN_I"] <= ISD_BEGIN_REQ)
        & (df["END_I"] >= ISD_END_REQ)
    )
    st = df.loc[keep].copy()
    st["station_id"] = st["USAF"] + "-" + st["WBAN"]
    st["station_name"] = st["STATION NAME"].str.strip()
    st = st[
        ["station_id", "station_name", "ICAO", "lat", "lon", "BEGIN_I", "END_I"]
    ].reset_index(drop=True)
    if len(st) < 20:
        print(
            f"NEEDS_CONTEXT: only {len(st)} qualifying TX ASOS stations in "
            "isd-history.csv — filter or file looks wrong"
        )
        sys.exit(2)
    return st


def build() -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED_DIR.mkdir(parents=True, exist_ok=True)

    fetch(POP_URL, POP_FILE, "Census PEP 2023 county population estimates", 100_000)
    fetch(GAZ_URL, GAZ_FILE, "Census 2023 Gazetteer TX counties file", 10_000)
    fetch(ISD_URL, ISD_FILE, "NOAA ISD station history", 1_000_000)

    acs = load_population()
    gaz = load_gazetteer()
    ercot, diag = load_ercot_map()
    stations = load_stations()

    counties = acs.merge(gaz, on="county_fips", how="inner")
    assert len(counties) == 254, "ACS/Gazetteer FIPS join lost counties"

    # --- join ERCOT mapping on normalized county name; report non-matches ---
    merged = ercot.merge(counties, on="county_key", how="left", indicator=True)
    unmatched = sorted(merged.loc[merged["_merge"] == "left_only", "county_key"])
    if unmatched:
        print(f"[warn] ERCOT rows with no Census county match: {unmatched}")
    merged = merged[merged["_merge"] == "both"].drop(columns="_merge")
    diag["unmatched_ercot_rows"] = unmatched

    # --- restrict to the three in-scope zones ------------------------------
    merged["weather_zone"] = merged["wz"].map(ZONE_KEYS)
    zdf = merged.dropna(subset=["weather_zone"]).copy()

    # materiality of ambiguous split counties (per candidate in-scope zone)
    zone_tot = zdf.groupby("weather_zone")["population"].sum().to_dict()
    flags = []
    for county, zones in diag["split_excluded"].items():
        for wz in zones:
            zk = ZONE_KEYS.get(wz)
            if zk is None:
                continue
            pop = counties.loc[counties["county_key"] == county, "population"]
            pop = int(pop.iloc[0]) if len(pop) else 0
            share = pop / (zone_tot[zk] + pop)
            flags.append((county, zk, pop, share))
            if share > MATERIALITY:
                print(
                    f"[FLAG] ambiguous split county {county} would be "
                    f"{share:.1%} of {zk} — excluded, needs a ruling"
                )
    diag["split_excluded_shares"] = flags

    # --- per-zone county selection: >= COVERAGE_TARGET of zone population --
    picks = []
    for zone, grp in zdf.groupby("weather_zone"):
        grp = grp.sort_values("population", ascending=False).reset_index(drop=True)
        total = grp["population"].sum()
        cum = grp["population"].cumsum()
        n_keep = int(np.searchsorted(cum.values, COVERAGE_TARGET * total) + 1)
        sel = grp.iloc[:n_keep].copy()
        sel["zone_coverage"] = cum.iloc[n_keep - 1] / total
        picks.append(sel)
        print(
            f"[select] {zone}: {n_keep} counties cover "
            f"{cum.iloc[n_keep - 1] / total:.1%} of zone pop {total:,}"
        )
    sel = pd.concat(picks, ignore_index=True)

    # --- nearest qualifying station within 50 km; else share neighbor's ----
    d = haversine_km(
        sel["lat"].values[:, None],
        sel["lon"].values[:, None],
        stations["lat"].values[None, :],
        stations["lon"].values[None, :],
    )
    nearest_idx = d.argmin(axis=1)
    nearest_km = d.min(axis=1)
    sel["station_idx"] = nearest_idx
    sel["dist_km"] = nearest_km
    sel["shared_from"] = ""

    direct = sel["dist_km"] <= MAX_STATION_KM
    for i in np.where(~direct)[0]:
        zone = sel.at[i, "weather_zone"]
        donors = sel.index[(sel["weather_zone"] == zone) & direct & (sel.index != i)]
        if len(donors) == 0:
            print(f"NEEDS_CONTEXT: no station within {MAX_STATION_KM} km for any "
                  f"county in zone {zone}")
            sys.exit(2)
        dc = haversine_km(
            sel.at[i, "lat"], sel.at[i, "lon"],
            sel.loc[donors, "lat"].values, sel.loc[donors, "lon"].values,
        )
        donor = donors[int(np.argmin(dc))]
        j = int(sel.at[donor, "station_idx"])
        sel.at[i, "station_idx"] = j
        sel.at[i, "dist_km"] = float(
            haversine_km(sel.at[i, "lat"], sel.at[i, "lon"],
                         stations.at[j, "lat"], stations.at[j, "lon"])
        )
        sel.at[i, "shared_from"] = sel.at[donor, "county_name"]
        print(
            f"[share] {sel.at[i, 'county_name']} ({zone}): no station within "
            f"{MAX_STATION_KM} km — sharing {stations.at[j, 'station_name']} "
            f"via {sel.at[donor, 'county_name']} "
            f"({sel.at[i, 'dist_km']:.1f} km from centroid)"
        )

    sel["station_id"] = stations.loc[sel["station_idx"], "station_id"].values
    sel["station_name"] = stations.loc[sel["station_idx"], "station_name"].values

    # --- weights ------------------------------------------------------------
    sel["weight"] = sel["population"] / sel.groupby("weather_zone")[
        "population"
    ].transform("sum")

    out = sel[
        [
            "county_fips",
            "county_name",
            "weather_zone",
            "population",
            "station_id",
            "station_name",
            "dist_km",
            "weight",
        ]
    ].copy()
    out["dist_km"] = out["dist_km"].round(2)
    out = out.sort_values(
        ["weather_zone", "weight"], ascending=[True, False]
    ).reset_index(drop=True)

    # --- acceptance checks ---------------------------------------------------
    print("\n=== acceptance checks ===")
    ok = True
    wsum = out.groupby("weather_zone")["weight"].sum()
    for zone, s in wsum.items():
        good = abs(s - 1.0) <= WEIGHT_TOL
        ok &= good
        print(f"weights sum {zone}: {s:.9f} {'OK' if good else 'FAIL'}")
    nst = out.groupby("weather_zone")["station_id"].nunique()
    for zone, n in nst.items():
        print(f"distinct stations {zone}: {n} (expect ~5-8)")
    span = out.merge(
        stations[["station_id", "BEGIN_I", "END_I"]].drop_duplicates("station_id"),
        on="station_id",
        how="left",
    )
    bad = span[(span["BEGIN_I"] > ISD_BEGIN_REQ) | (span["END_I"] < ISD_END_REQ)]
    if len(bad):
        ok = False
        print(f"FAIL: stations without 2015-2025 ISD span:\n{bad}")
    else:
        print("ISD record span 2015->2025: OK for all selected stations")
    if not ok:
        print("ACCEPTANCE FAILED")
        sys.exit(1)

    out.to_csv(OUT_CSV, index=False)
    print(f"\nwrote {OUT_CSV} ({len(out)} rows)")

    # --- per-zone summary for the report -------------------------------------
    print("\n=== per-zone station lists ===")
    for zone, grp in out.groupby("weather_zone"):
        print(f"\n{zone}:")
        for _, r in grp.iterrows():
            print(
                f"  {r['county_name']:<12} pop {r['population']:>9,} "
                f"w={r['weight']:.4f}  {r['station_id']}  "
                f"{r['station_name']} ({r['dist_km']:.1f} km)"
            )
    print("\n=== diagnostics ===")
    print("dropped non-TX rows:", diag["dropped_non_tx"])
    print("split resolved:", diag["split_resolved"])
    print("split excluded (ambiguous):", diag["split_excluded"])
    print("unmatched ERCOT rows:", diag["unmatched_ercot_rows"])
    return out


if __name__ == "__main__":
    build()
