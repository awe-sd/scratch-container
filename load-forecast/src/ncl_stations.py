"""Task 07 (NCL exclusion) step 1 -- build the confirmed non-conforming-load
(NCL) station set: datacenter/large-load sheet stations UNION the
ercotManuallyUpdatedLoad roster. PUN-flagged unknowns are NOT included here
(per sdalvi's ruling in docs/large_load_research.md -- "do not trust
clean_plus_internal_mw until the biggest excluded stations are named and
gut-checked"); this file only uses CONFIRMED sources.

Sources
-------
- roster: AW.dbo.ercotManuallyUpdatedLoad (SQL Server, pulled ONCE, cached).
  Already carries NmmsStationCode + PlanningBusCounty per row. Verified
  2026-08-15: all 119 current rows have isConforming=False (asserted, not
  silently assumed) -- the whole table IS the confirmed non-conforming set,
  no further filter needed.
- sheet: data/derived/large_loads.csv (per bus/phase rows from sdalvi's
  tracking sheet, produced by build_large_loads.py). Mapped via
  sswg_bus_id -> ercotDataDictionary.SswgBusNumber -> NmmsStationCode
  (latest fileDateMonth snapshot). Rows whose bus is absent from the
  snapshot (known gap, e.g. brand-new SSWG buses -- see
  docs/large_load_research.md) fall back to an EXACT (normalized) match of
  dam_bus_name against the dictionary's NmmsBusName, then SswgBusName. Rows
  that fail both are reported unmapped -- NEVER fuzzy-matched (memory rule).

Zone attribution (both sources): PlanningBusCounty -> weather_zone via
build_crosswalk.load_ercot_map() + build_crosswalk.ZONE_KEYS -- i.e. the SAME
parsed, split-resolved county->zone mapping Task 01 uses
(data/raw/crosswalk/ercot_county_weatherzone.csv, SPLIT_OVERRIDES for
ambiguous multi-zone counties), reused directly rather than re-derived.
data/derived/crosswalk_county_station.csv is NOT the zone source here (that
file is a weather-station selection artifact, not a zone crosswalk) -- see
tasks/07_ncl_exclusion.md.

Output: data/derived/ncl_stations.csv
  nmms_station_code, provenance (sheet/roster/both), site_name(s), county,
  weather_zone, first_online_date (sheet-derived only; null for roster-only),
  max_mw, expected_mw (sheet-derived rollup, max() across a station's sheet
  rows -- see organic_load.py's plausibility-check docstring for why max()
  and why it's a deliberately generous cap, null for roster-only). Added
  2026-08-15b (Opus-reviewed correction #2): organic_load.py needs
  first_online_date to gate NCL subtraction to hours the large load actually
  existed, and max_mw/expected_mw as a plausibility cap on the result --
  neither was consumed downstream before this correction.

Run: uv run python load-forecast/src/ncl_stations.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import build_crosswalk as bx  # noqa: E402
import config as cfg  # noqa: E402

POWERFLOW_ANALYTICS = cfg.PROJECT_ROOT.parent / "powerflow_analytics"

LOOKUP_RAW_DIR = cfg.RAW_DIR / "lookups"
DICTIONARY_CACHE = LOOKUP_RAW_DIR / "ercot_data_dictionary_latest.parquet"
ROSTER_CACHE = LOOKUP_RAW_DIR / "ercot_manually_updated_load.parquet"
LARGE_LOADS_CSV = cfg.DERIVED_DIR / "large_loads.csv"
NCL_STATIONS_CSV = cfg.DERIVED_DIR / "ncl_stations.csv"

OUT_COLUMNS = [
    "nmms_station_code", "provenance", "site_name(s)", "county",
    "weather_zone", "first_online_date", "max_mw", "expected_mw",
]


# ---------------------------------------------------------------------------
# Pulls (cache-first, SQL Server, small + bounded per load-forecast/CLAUDE.md)
# ---------------------------------------------------------------------------


def pull_dictionary_snapshot() -> tuple[pd.DataFrame, str]:
    """Cache-first pull of the latest ercotDataDictionary snapshot -- only the
    columns needed for bus->station->county mapping. Returns (df, snapshot)."""
    if DICTIONARY_CACHE.exists():
        df = pd.read_parquet(DICTIONARY_CACHE)
        return df, str(df["fileDateMonth"].iloc[0])[:10]
    cfg.configure()
    from awconnect import db

    snap = str(
        db.getDfFromAwDb(
            "SELECT MAX(fileDateMonth) AS m FROM AW.dbo.ercotDataDictionary",
            database="AW",
        )["m"].iloc[0]
    )[:10]
    df = db.getDfFromAwDb(
        f"""SELECT SswgBusNumber, SswgBusName, NmmsBusName, NmmsStationCode,
                    PlanningBusCounty, fileDateMonth
            FROM AW.dbo.ercotDataDictionary
            WHERE fileDateMonth = '{snap}'""",
        database="AW",
    )
    LOOKUP_RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(DICTIONARY_CACHE)
    return df, snap


def pull_roster() -> pd.DataFrame:
    """Cache-first pull of the FULL ercotManuallyUpdatedLoad roster (119 rows
    as of 2026-08-15) -- small table, pulled once (never re-queried while the
    cache file exists; delete it to force a refresh)."""
    if ROSTER_CACHE.exists():
        return pd.read_parquet(ROSTER_CACHE)
    cfg.configure()
    from awconnect import db

    df = db.getDfFromAwDb(
        """SELECT NmmsStationCode, NmmsStationName, isConforming,
                  PlanningBusCounty
           FROM AW.dbo.ercotManuallyUpdatedLoad""",
        database="AW",
    )
    LOOKUP_RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(ROSTER_CACHE)
    return df


# ---------------------------------------------------------------------------
# Zone attribution (reuse build_crosswalk, do not re-derive)
# ---------------------------------------------------------------------------


def zone_map() -> tuple[dict, dict]:
    """{county_key -> project weather_zone} restricted to NCENT/COAST/SCENT,
    via build_crosswalk's own parsed + split-resolved county->WZ_* mapping."""
    county_wz, diag = bx.load_ercot_map()
    county_wz = county_wz.copy()
    county_wz["weather_zone"] = county_wz["wz"].map(bx.ZONE_KEYS)
    m = (
        county_wz.dropna(subset=["weather_zone"])
        .set_index("county_key")["weather_zone"]
        .to_dict()
    )
    return m, diag


def _norm(s) -> str | None:
    if s is None or (isinstance(s, float) and pd.isna(s)) or pd.isna(s):
        return None
    s = str(s).strip().upper()
    return s or None


# ---------------------------------------------------------------------------
# Sheet mapping: bus/phase rows -> station code (bus id, then dam_bus_name)
# ---------------------------------------------------------------------------


def map_sheet_rows(sheet: pd.DataFrame, dictionary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Map each large_loads.csv row to a station. Priority: (1) sswg_bus_id ->
    SswgBusNumber: (2) dam_bus_name (normalized) exact match -> NmmsBusName;
    (3) dam_bus_name exact match -> SswgBusName. Rows failing all three are
    returned as `unmapped` -- reported, never fuzzy-matched.
    Returns (mapped_rows_with_station_and_county, unmapped_rows)."""
    d = dictionary.copy()
    d["_bus_num"] = pd.to_numeric(d["SswgBusNumber"], errors="coerce")
    by_bus = d.dropna(subset=["_bus_num"]).drop_duplicates("_bus_num").set_index("_bus_num")

    def _name_index(col: str) -> pd.DataFrame:
        t = d.dropna(subset=[col]).copy()
        t["_key"] = t[col].map(_norm)
        t = t.dropna(subset=["_key"]).drop_duplicates("_key")
        return t.set_index("_key")

    by_nmms_name = _name_index("NmmsBusName")
    by_sswg_name = _name_index("SswgBusName")

    rows = sheet.copy()
    rows["_bus_num"] = pd.to_numeric(rows["sswg_bus_id"], errors="coerce")
    rows["_dam_key"] = rows["dam_bus_name"].map(_norm)

    station_code = pd.Series(pd.NA, index=rows.index, dtype="object")
    county = pd.Series(pd.NA, index=rows.index, dtype="object")
    method = pd.Series(pd.NA, index=rows.index, dtype="object")

    hit = rows["_bus_num"].notna() & rows["_bus_num"].isin(by_bus.index)
    station_code[hit] = rows.loc[hit, "_bus_num"].map(by_bus["NmmsStationCode"])
    county[hit] = rows.loc[hit, "_bus_num"].map(by_bus["PlanningBusCounty"])
    method[hit] = "bus_id"

    remaining = station_code.isna() & rows["_dam_key"].notna()
    hit2 = remaining & rows["_dam_key"].isin(by_nmms_name.index)
    station_code[hit2] = rows.loc[hit2, "_dam_key"].map(by_nmms_name["NmmsStationCode"])
    county[hit2] = rows.loc[hit2, "_dam_key"].map(by_nmms_name["PlanningBusCounty"])
    method[hit2] = "dam_bus_name~NmmsBusName"

    remaining = station_code.isna() & rows["_dam_key"].notna()
    hit3 = remaining & rows["_dam_key"].isin(by_sswg_name.index)
    station_code[hit3] = rows.loc[hit3, "_dam_key"].map(by_sswg_name["NmmsStationCode"])
    county[hit3] = rows.loc[hit3, "_dam_key"].map(by_sswg_name["PlanningBusCounty"])
    method[hit3] = "dam_bus_name~SswgBusName"

    rows["nmms_station_code"] = station_code
    rows["county"] = county.map(_norm)
    rows["map_method"] = method

    mapped = rows.loc[rows["nmms_station_code"].notna()].copy()
    unmapped = rows.loc[rows["nmms_station_code"].isna()].copy()
    return mapped, unmapped


def build_sheet_stations(mapped: pd.DataFrame) -> pd.DataFrame:
    """One row per nmms_station_code from mapped sheet rows: site_name(s)
    (deduped, ';'-joined), county (deduped -- flagged via n_counties if a
    single station spans >1 county, not silently collapsed), first_online_date
    = earliest online_date across the station's rows, max_mw/expected_mw =
    max() across the station's rows (NOT sum -- large_loads.csv rows are
    per-phase/per-bus and max_mw looks like a shared site-level cap in some
    multi-row stations, e.g. DFWBE's 4 rows all show max_mw=201, so summing
    would overstate capacity; max() is the deliberately conservative-on-the-
    generous-side reading, used only as a plausibility ceiling downstream in
    organic_load.py, never to size anything)."""
    out = []
    for code, g in mapped.groupby("nmms_station_code"):
        counties = sorted({c for c in g["county"].dropna().unique()})
        sites = sorted({s for s in g["site_name"].dropna().unique()})
        dates = pd.to_datetime(g["online_date"], errors="coerce").dropna()
        max_mw = pd.to_numeric(g["max_mw"], errors="coerce").max()
        expected_mw = pd.to_numeric(g["expected_mw"], errors="coerce").max()
        out.append({
            "nmms_station_code": code,
            "site_name(s)": ";".join(sites) if sites else None,
            "county": counties[0] if counties else None,
            "n_counties": len(counties),
            "first_online_date": dates.min().date().isoformat() if len(dates) else None,
            "max_mw": float(max_mw) if pd.notna(max_mw) else None,
            "expected_mw": float(expected_mw) if pd.notna(expected_mw) else None,
        })
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# Combine sheet + roster -> ncl_stations.csv
# ---------------------------------------------------------------------------


def build_ncl_stations() -> tuple[pd.DataFrame, dict]:
    dictionary, snap = pull_dictionary_snapshot()
    roster_raw = pull_roster()
    not_conforming = roster_raw["isConforming"] == False  # noqa: E712 (pandas bool col)
    if not not_conforming.all():
        print(
            f"WARNING: {int((~not_conforming).sum())} ercotManuallyUpdatedLoad rows have "
            "isConforming != False -- excluding them (only confirmed non-conforming rows used)"
        )
    roster = roster_raw.loc[not_conforming].copy()
    roster["county"] = roster["PlanningBusCounty"].map(_norm)

    sheet = pd.read_csv(LARGE_LOADS_CSV)
    mapped, unmapped = map_sheet_rows(sheet, dictionary)
    sheet_stations = build_sheet_stations(mapped)

    zmap, zdiag = zone_map()
    sheet_stations["weather_zone"] = sheet_stations["county"].map(lambda c: zmap.get(c) if c else None)
    roster["weather_zone"] = roster["county"].map(lambda c: zmap.get(c) if c else None)

    sheet_no_county = sheet_stations.loc[sheet_stations["county"].isna()]
    sheet_zone_oos = sheet_stations.loc[sheet_stations["county"].notna() & sheet_stations["weather_zone"].isna()]
    roster_no_county = roster.loc[roster["county"].isna()]
    roster_zone_oos = roster.loc[roster["county"].notna() & roster["weather_zone"].isna()]

    sheet_codes = set(sheet_stations["nmms_station_code"])
    roster_codes = set(roster["NmmsStationCode"])
    both_codes = sheet_codes & roster_codes

    sheet_by_code = sheet_stations.set_index("nmms_station_code")
    roster_by_code = roster.set_index("NmmsStationCode")

    rows = []
    dropped_oos = []
    for code in sorted(sheet_codes | roster_codes):
        in_sheet, in_roster = code in sheet_codes, code in roster_codes
        prov = "both" if (in_sheet and in_roster) else ("sheet" if in_sheet else "roster")

        if in_sheet:
            srow = sheet_by_code.loc[code]
        if in_roster:
            rrow = roster_by_code.loc[code]

        max_mw = expected_mw = None
        if in_sheet and in_roster:
            sheet_sites = set(srow["site_name(s)"].split(";")) if pd.notna(srow["site_name(s)"]) else set()
            roster_name = rrow["NmmsStationName"] if pd.notna(rrow["NmmsStationName"]) else None
            site = ";".join(sorted(sheet_sites | ({roster_name} if roster_name else set())))
            county = srow["county"] if pd.notna(srow["county"]) else rrow["county"]
            zone = srow["weather_zone"] if pd.notna(srow["weather_zone"]) else rrow["weather_zone"]
            first_online = srow["first_online_date"]
            max_mw, expected_mw = srow["max_mw"], srow["expected_mw"]
        elif in_sheet:
            site, county, zone, first_online = (
                srow["site_name(s)"], srow["county"], srow["weather_zone"], srow["first_online_date"],
            )
            max_mw, expected_mw = srow["max_mw"], srow["expected_mw"]
        else:
            site, county, zone, first_online = rrow["NmmsStationName"], rrow["county"], rrow["weather_zone"], None

        if pd.isna(zone) or zone is None:
            dropped_oos.append({"nmms_station_code": code, "provenance": prov, "county": county})
            continue

        rows.append({
            "nmms_station_code": code, "provenance": prov, "site_name(s)": site,
            "county": county, "weather_zone": zone, "first_online_date": first_online,
            "max_mw": max_mw, "expected_mw": expected_mw,
        })

    out = pd.DataFrame(rows, columns=OUT_COLUMNS).sort_values(
        ["weather_zone", "nmms_station_code"]
    ).reset_index(drop=True)

    diag = {
        "dictionary_snapshot": snap,
        "n_roster_total": len(roster_raw),
        "n_roster_confirmed": len(roster),
        "n_sheet_rows": len(sheet),
        "n_sheet_rows_mapped": len(mapped),
        "n_sheet_rows_unmapped": len(unmapped),
        "unmapped_rows": unmapped[["site_name", "sswg_bus_id", "dam_bus_name", "online_date"]],
        "n_sheet_stations": len(sheet_stations),
        "n_both": len(both_codes),
        "sheet_no_county": sheet_no_county[["nmms_station_code", "site_name(s)"]],
        "sheet_zone_out_of_scope": sheet_zone_oos[["nmms_station_code", "county"]],
        "roster_no_county": roster_no_county[["NmmsStationCode", "NmmsStationName"]],
        "roster_zone_out_of_scope": roster_zone_oos[["NmmsStationCode", "county"]],
        "dropped_out_of_scope": pd.DataFrame(dropped_oos),
        "zone_diag": zdiag,
    }
    return out, diag


def main() -> None:
    out, diag = build_ncl_stations()
    cfg.DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(NCL_STATIONS_CSV, index=False)

    print(f"ercotDataDictionary snapshot used: {diag['dictionary_snapshot']}")
    print(f"roster: {diag['n_roster_confirmed']}/{diag['n_roster_total']} rows confirmed non-conforming")
    print(f"sheet: {diag['n_sheet_rows']} raw rows, {diag['n_sheet_rows_mapped']} mapped, "
          f"{diag['n_sheet_rows_unmapped']} unmapped -> {diag['n_sheet_stations']} distinct stations")
    print(f"stations present in BOTH sheet and roster: {diag['n_both']}")

    if diag["n_sheet_rows_unmapped"]:
        print(f"\nUNMAPPED SHEET ROWS ({diag['n_sheet_rows_unmapped']}) -- not fuzzy-matched:")
        print(diag["unmapped_rows"].to_string(index=False))

    for label in ["sheet_no_county", "sheet_zone_out_of_scope", "roster_no_county", "roster_zone_out_of_scope"]:
        d = diag[label]
        if len(d):
            print(f"\n{label} ({len(d)}):")
            print(d.to_string(index=False))

    if len(diag["dropped_out_of_scope"]):
        print(f"\nstations dropped (zone outside NCENT/COAST/SCENT): {len(diag['dropped_out_of_scope'])}")

    print(f"\nwrote {NCL_STATIONS_CSV} ({len(out)} stations)")
    print("\nzone distribution:")
    print(out["weather_zone"].value_counts().to_string())
    print("\nprovenance distribution:")
    print(out["provenance"].value_counts().to_string())


if __name__ == "__main__":
    main()
