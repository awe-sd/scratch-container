#!/usr/bin/env python
"""Task 07 (NCL exclusion) — parse sdalvi's manual datacenter/large-load tracking
sheet into two derived CSVs.

Input: data/raw/large_loads/datacenter_tracking_raw.txt — a verbatim paste of
sdalvi's tracking spreadsheet (tab-separated, trailing-blank-trimmed per row,
per the file's own header comment). One line per (site, bus, phase) — a site
can span multiple SSWG buses, and each bus has one line per ramp-up phase
(Online Date). Header comment (line 2 of the file) documents 20 columns;
two rows (the two earliest Lancium: Abilene rows) carry a 21st/22nd trailing
value ("1", "High") that is stray spreadsheet legend bleed ("Confidence
scale: 1 High", line 3 of the file) landing in those rows' overflow cells,
not real data for those rows — dropped, not parsed as a column.

Column mapping (raw header -> output column; TZL and Reference Links are
present in the raw file but NOT in the requested output schema, so dropped
here — TZL sometimes carries real analyst commentary, see parse report):
  0 Baxtel ID          -> baxtel_id
  1 TPIT ID            -> tpit_id
  2 BusID (SSWG)       -> sswg_bus_id
  3 BusName (SSWG)     -> sswg_bus_name
  4 DAM Bus Name       -> dam_bus_name
  5 kV                 -> kv
  6 Data Center Name   -> site_name
  7 Crypto/Non-Crypto  -> load_type
  8 Dispatchable       -> dispatchable
  9 Max MW             -> max_mw
  10 Expected MW       -> expected_mw
  11 DAM MW            -> dam_mw
  12 Confidence        -> confidence
  13 TZL               -> (dropped)
  14 Online Date       -> online_date
  15 End Date          -> end_date
  16 Notes             -> notes (truncated to 200 chars)
  17 Reference Links   -> (dropped)
  18 LatestUpdate      -> latest_update
  19 Updateby          -> updated_by

Run from the repo root:  uv run python load-forecast/src/build_large_loads.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]  # load-forecast/
RAW_FILE = PROJECT / "data" / "raw" / "large_loads" / "datacenter_tracking_raw.txt"
OUT_ROWS_CSV = PROJECT / "data" / "derived" / "large_loads.csv"
OUT_SITES_CSV = PROJECT / "data" / "derived" / "large_loads_sites.csv"

N_HEADER_LINES = 5  # Source / Columns / Confidence-scale / NOTE / --- separator
N_COLS = 20  # columns documented in the file's own "Columns:" header line

OUT_COLUMNS = [
    "baxtel_id", "tpit_id", "sswg_bus_id", "sswg_bus_name", "dam_bus_name",
    "kv", "site_name", "load_type", "dispatchable", "max_mw", "expected_mw",
    "dam_mw", "confidence", "online_date", "end_date", "notes",
    "latest_update", "updated_by",
]

NOTES_MAXLEN = 200


def _num(x: str) -> float:
    x = x.strip()
    if x == "":
        return float("nan")
    try:
        return float(x)
    except ValueError:
        return float("nan")


def _date(x: str) -> "pd.Timestamp | float":
    x = x.strip()
    if x == "":
        return pd.NaT
    ts = pd.to_datetime(x, format="%m/%d/%Y", errors="coerce")
    return ts


def parse_raw(path: Path) -> tuple[pd.DataFrame, dict]:
    with open(path, encoding="utf-8", errors="replace") as f:
        all_lines = f.readlines()

    data_lines = all_lines[N_HEADER_LINES:]
    stats = {
        "total_data_lines": len(data_lines),
        "rows_parsed": 0,
        "rows_dropped": 0,
        "dropped_detail": [],  # list of (line_no, reason, raw_line)
        "stray_trailing_fields_rows": 0,  # rows with >20 raw fields (legend bleed etc.)
        "short_stub_rows": 0,  # rows with <=10 populated leading fields
        "literal_blank_tokens_normalized": 0,  # literal "(blank)" text -> empty
    }

    out_rows = []
    for i, raw_line in enumerate(data_lines):
        line_no = N_HEADER_LINES + i + 1  # 1-indexed physical line number in the file
        line = raw_line.rstrip("\n").rstrip("\r")
        if line.strip() == "":
            stats["rows_dropped"] += 1
            stats["dropped_detail"].append((line_no, "blank line", raw_line))
            continue

        fields = line.split("\t")
        if len(fields) > N_COLS:
            # Extra trailing fields beyond the documented 20 columns. Verified
            # (recon pass): only the two earliest Lancium:Abilene rows hit
            # this, both with trailing ("1","High") == the file's own
            # "Confidence scale: 1 High" legend note bleeding into overflow
            # cells, not real per-row data. Drop anything past column 20.
            stats["stray_trailing_fields_rows"] += 1
        fields = (fields + [""] * N_COLS)[:N_COLS]
        # sdalvi's sheet uses the literal text "(blank)" as a human-typed
        # placeholder for an empty cell in several columns (confirmed by
        # recon: 126 occurrences across Baxtel ID, DAM Bus Name, End Date,
        # Notes, Reference Links, LatestUpdate, load_type, dispatchable --
        # heaviest in DAM Bus Name 33x and End Date 89x). Numeric/date fields
        # already fail safe to NaN/NaT on this text, but string fields would
        # otherwise carry the literal word "(blank)" through as if it were
        # real data (e.g. into dam_bus_name / sswg_bus_name rollups) --
        # normalize to true empty before any field-specific parsing.
        n_blank_tokens = sum(1 for f in fields if f.strip().lower() == "(blank)")
        stats["literal_blank_tokens_normalized"] += n_blank_tokens
        fields = ["" if f.strip().lower() == "(blank)" else f for f in fields]

        baxtel_id = fields[0].strip()
        tpit_id = fields[1].strip()
        sswg_bus_id = fields[2].strip()
        sswg_bus_name = fields[3].strip()
        dam_bus_name = fields[4].strip()
        kv = _num(fields[5])
        site_name = fields[6].strip()
        load_type = fields[7].strip()
        dispatchable = fields[8].strip()
        max_mw = _num(fields[9])
        expected_mw = _num(fields[10])
        dam_mw = _num(fields[11])
        confidence = _num(fields[12])
        # fields[13] = TZL, dropped (see module docstring)
        online_date = _date(fields[14])
        end_date = _date(fields[15])
        notes = fields[16].strip()[:NOTES_MAXLEN]
        # fields[17] = Reference Links, dropped
        latest_update = _date(fields[18])
        updated_by = fields[19].strip()

        # Drop rule: keep anything with at least one identifying field
        # (site name or an id). None of the 244 raw lines actually fail this
        # (even the sparsest "stub" rows carry a site name) — kept defensive
        # for future re-runs of this raw file.
        has_identity = bool(site_name or baxtel_id or sswg_bus_id)
        if not has_identity:
            stats["rows_dropped"] += 1
            stats["dropped_detail"].append((line_no, "no site_name/baxtel_id/sswg_bus_id", raw_line))
            continue

        n_populated = sum(1 for v in fields if v.strip() != "")
        if n_populated <= 3:
            stats["short_stub_rows"] += 1

        out_rows.append({
            "baxtel_id": baxtel_id or None,
            "tpit_id": tpit_id or None,
            "sswg_bus_id": sswg_bus_id or None,
            "sswg_bus_name": sswg_bus_name or None,
            "dam_bus_name": dam_bus_name or None,
            "kv": kv,
            "site_name": site_name or None,
            "load_type": load_type or None,
            "dispatchable": dispatchable or None,
            "max_mw": max_mw,
            "expected_mw": expected_mw,
            "dam_mw": dam_mw,
            "confidence": confidence,
            "online_date": online_date,
            "end_date": end_date,
            "notes": notes or None,
            "latest_update": latest_update,
            "updated_by": updated_by or None,
            "_line_no": line_no,
        })
        stats["rows_parsed"] += 1

    df = pd.DataFrame(out_rows)
    return df, stats


def build_sites_rollup(df: pd.DataFrame) -> pd.DataFrame:
    """One row per site_name. max_mw is the literal per-spec 'site max' =
    MAX(max_mw) across the site's rows. CAVEAT (flagged, not silently fixed):
    a site can span multiple SSWG buses, each with its own max_mw plateau
    (e.g. Lancium: Abilene = bus 6228 at 200 MW + bus 6230 at 1000 MW) --
    'site max' (1000) understates true combined ultimate capacity (1200).
    See parse report / caller notes for the per-bus-summed alternative.
    """
    recs = []
    for site, g in df.groupby("site_name", dropna=True):
        bus_ids = sorted({b for b in g["sswg_bus_id"].dropna().unique()})
        dam_buses = sorted({b for b in g["dam_bus_name"].dropna().unique()})
        load_types = sorted({t for t in g["load_type"].dropna().unique()})
        site_max_mw = g["max_mw"].max()  # literal "site max" per task spec
        current_dam_mw = g["dam_mw"].max()
        first_online = g["online_date"].min()

        phase_pairs = (
            g.dropna(subset=["online_date"])[["online_date", "expected_mw"]]
            .drop_duplicates()
            .sort_values("online_date")
        )
        phased_additions_count = len(phase_pairs)
        phased_additions = "; ".join(
            f"{d.date().isoformat()}:{mw:g}" if pd.notna(mw) else f"{d.date().isoformat()}:NA"
            for d, mw in zip(phase_pairs["online_date"], phase_pairs["expected_mw"])
        )

        recs.append({
            "site_name": site,
            "sswg_bus_ids": ";".join(bus_ids) if bus_ids else None,
            "dam_bus_names": ";".join(dam_buses) if dam_buses else None,
            "load_type": ";".join(load_types) if load_types else None,
            "max_mw": site_max_mw,
            "current_dam_mw": current_dam_mw,
            "first_online_date": first_online.date().isoformat() if pd.notna(first_online) else None,
            "phased_additions_count": phased_additions_count,
            "phased_additions": phased_additions or None,
        })
    out = pd.DataFrame(recs).sort_values("site_name").reset_index(drop=True)
    return out


def main() -> None:
    df, stats = parse_raw(RAW_FILE)

    print("=== parse stats ===")
    print(f"total data lines in raw file (excl. {N_HEADER_LINES} header lines): {stats['total_data_lines']}")
    print(f"rows parsed: {stats['rows_parsed']}")
    print(f"rows dropped: {stats['rows_dropped']}")
    if stats["dropped_detail"]:
        print("dropped lines:")
        for line_no, reason, raw in stats["dropped_detail"]:
            print(f"  line {line_no}: {reason} | {raw!r}")
    else:
        print("  (none — every line carried at least a site_name/baxtel_id/sswg_bus_id)")
    print(f"rows with stray trailing fields beyond column 20 (dropped, legend bleed): {stats['stray_trailing_fields_rows']}")
    print(f"literal '(blank)' placeholder tokens normalized to empty: {stats['literal_blank_tokens_normalized']}")
    print(f"bare 'stub' rows (<=3 populated fields, e.g. id+name only, no MW yet): {stats['short_stub_rows']}")

    n_sites = df["site_name"].nunique(dropna=True)
    n_dam_mw_pos = int((df["dam_mw"].fillna(0) > 0).sum())
    print(f"\ndistinct site_name count: {n_sites}")
    print(f"rows with dam_mw > 0: {n_dam_mw_pos}")

    # Sanity total: max_mw repeats per phase-row (same bus, same plateau), so
    # naively summing df['max_mw'] massively overcounts. De-dupe to one
    # max_mw per (site_name, sswg_bus_id) first, THEN sum -- this is the
    # dataset-wide "how much ultimate buildout does this sheet imply" check,
    # distinct from the per-site rollup's literal MAX() column (see below).
    per_bus = df.dropna(subset=["max_mw"]).drop_duplicates(subset=["site_name", "sswg_bus_id", "max_mw"])
    sum_max_mw_deduped = per_bus["max_mw"].sum()
    naive_sum_max_mw = df["max_mw"].sum()
    print(f"\nnaive SUM(max_mw) across all {len(df)} rows (WRONG -- double/triple counts phases): {naive_sum_max_mw:,.0f} MW")
    print(f"de-duped SUM(max_mw) across distinct (site,bus) pairs (sanity total): {sum_max_mw_deduped:,.0f} MW")

    df.drop(columns=["_line_no"]).reindex(columns=OUT_COLUMNS).to_csv(OUT_ROWS_CSV, index=False)
    print(f"\nwrote {OUT_ROWS_CSV} ({len(df)} rows)")

    sites = build_sites_rollup(df)
    sites.to_csv(OUT_SITES_CSV, index=False)
    print(f"wrote {OUT_SITES_CSV} ({len(sites)} rows)")


if __name__ == "__main__":
    sys.exit(main())
