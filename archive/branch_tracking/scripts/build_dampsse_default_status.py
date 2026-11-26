"""
Second-source `default_status` inference from ERCOT's published DAM PSSE
hourly models (dbo.ercotDampsse*), using the per-DA-hour `inService` bit
-- per the user's direction, this is the direct status signal (impedances
and ratings stay populated even when a line is out, so column presence
proves nothing; `inService` is what matters).

Why a second source: the existing implied_default_status comes from
Monthly Auction PTOBRANCH snapshots (~20 samples over 2025-2026). The
base-model comparison showed two systematic weaknesses: (1) the snapshot
window lags recently-energized equipment, and (2) the auction model
carries default-closed statuses for switchable/normally-open ties that
operational reality keeps open (125 robust disagreements, median
pct_closed=1.0). DAM PSSE gives HOURLY status back to 2015, published
daily -- far denser sampling of what ERCOT actually models in-service.

Linkage problem: ercotDampsse* has NO teid and NO rdfid. The mapping
goes through branchNameRaw, which uses the same raw naming convention as
BRANCH.OP_EQCODE (e.g. "6115__J"), confirmed by schema exploration
(scripts/explore_rt_rating_dampsse_schema.py). Method:
  1. Load ercotDampsseDef (Ln fileType=1, Xf fileType=2) + Station dim.
  2. Normalize branchNameRaw and our OP_EQCODE (uppercase alphanumeric,
     same normalize as build_inservice_retirement_dates.py) and match
     exact-first. Report ambiguous (one name -> many teids or many
     dampsse ids) separately rather than guessing.
  3. Pull last ~N days of hourly inService aggregated per ercotDampsseId
     (single GROUP BY, filtered by awDateID -- awDateID is a day-serial
     int, NOT YYYYMMDD; anchor confirmed 44926 <-> 2023-01-01).
  4. Per mapped teid: pct_inservice over the window ->
     dampsse_default_status (Closed if majority in service, Open
     otherwise), plus n_hours for confidence.
  5. Compare against implied_default_status (auction-based) and against
     the robust base-model disagreement list -- print agreement stats.

Future enhancement (per the user, not built yet): for elements whose
dominant status is Closed but that show Open hours, cross-reference the
Open periods against the outage data (toChangesAllIsos) -- if every Open
stretch coincides with a logged outage, that CONFIRMS default Closed
(only opened by outages); Open stretches with no outage would instead
suggest a switchable/normally-open element.

Output: output/dampsse_default_status.csv (one row per mapped teid).
Read-only. Writes only to branch_tracking/output/.
"""
import sys
from datetime import timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from branch_tracking.pipeline.dampsse import (  # noqa: E402
    compute_inservice_status, map_exact_names,
)
from branch_tracking.pipeline.naming import normalize_name  # noqa: E402
from branch_tracking.pipeline.config import AWDATEID_ANCHOR, WINDOW_DAYS  # noqa: E402

import awconnect
import pandas as pd
from awconnect import db

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"  # local cache of DB pulls (gitignore later)
TEID_MAP_CSV = REPO_ROOT / "output" / "teid_branch_id_map.csv"
TABLE_CSV = REPO_ROOT / "output" / "branch_tracking_table.csv"
CLEAN_CMP_CSV = REPO_ROOT / "output" / "base_model_status_comparison.csv"
OUTAGE_CMP_CSV = REPO_ROOT / "output" / "base_model_outages_status_comparison.csv"
OUTPUT_CSV = REPO_ROOT / "output" / "dampsse_default_status.csv"


def date_to_awdateid(d):
    anchor_id, anchor_date = AWDATEID_ANCHOR
    return anchor_id + (d - anchor_date).days


def main():
    awconnect.configure("read_only")

    # --- dimensions (small, fast) ---
    dampsse_def = db.getDfFromAwDb(
        """
        SELECT ercotDampsseId, ercotDampsseFileTypeId, branchName, branchNameRaw,
               fromStationId, toStationId, rpu, xpu, bpu
        FROM AW.dbo.ercotDampsseDef
        WHERE ercotDampsseFileTypeId IN (1, 2)
        """
    )
    stations = db.getDfFromAwDb(
        "SELECT ercotDampsseStationId, stationName, stationKv FROM AW.dbo.ercotDampsseStation"
    )
    print(f"ercotDampsseDef Ln+Xf rows: {len(dampsse_def)}")
    print(f"Stations: {len(stations)}")

    # Cache the dimensions locally so follow-on mapping work (diagnosing
    # unmapped teids, station/impedance fallback tiers) is DB-free.
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dampsse_def.to_csv(RAW_DIR / "ercotDampsseDef.csv", index=False)
    stations.to_csv(RAW_DIR / "ercotDampsseStation.csv", index=False)

    # --- current max awDateID, then windowed inService aggregate ---
    max_row = db.getDfFromAwDb(
        "SELECT MAX(awDateID) AS max_id FROM AW.dbo.ercotDampsseTimeseries"
    )
    max_awdateid = int(max_row["max_id"].iloc[0])
    cutoff = max_awdateid - WINDOW_DAYS
    anchor_id, anchor_date = AWDATEID_ANCHOR
    print(f"max awDateID: {max_awdateid} (~{anchor_date + timedelta(days=max_awdateid - anchor_id)})")
    print(f"window cutoff awDateID: {cutoff}")

    agg = db.getDfFromAwDb(
        f"""
        SELECT ercotDampsseId,
               COUNT(*) AS n_hours,
               SUM(CAST(inService AS int)) AS n_inservice
        FROM AW.dbo.ercotDampsseTimeseries
        WHERE ercotDampsseFileTypeId IN (1, 2)
          AND awDateID > {cutoff}
        GROUP BY ercotDampsseId
        """
    )
    print(f"Elements with hourly data in window: {len(agg)}")
    agg.to_csv(RAW_DIR / "dampsse_inservice_agg.csv", index=False)

    # --- name mapping to our teids ---
    teid_map = pd.read_csv(TEID_MAP_CSV)
    ours = teid_map[teid_map["match_status"] != "unmatched"][
        ["teid", "branch_id", "OP_EQCODE", "FromName", "ToName", "DeviceType"]
    ].copy()

    st = stations.set_index("ercotDampsseStationId")
    dampsse_def["from_station"] = dampsse_def["fromStationId"].map(st["stationName"])
    dampsse_def["to_station"] = dampsse_def["toStationId"].map(st["stationName"])

    # Exact normalized-name match (map_exact_names). Ambiguity accounting: a
    # normalized name can appear on multiple dampsse ids (re-definitions
    # over the years) or multiple teids -- keep 1:1 matches as high
    # confidence; for many-dampsse-to-one-teid keep the dampsse id with
    # hourly data in the current window (i.e., currently published),
    # reporting how often that resolves it.
    active_ids = set(agg["ercotDampsseId"])
    mapping = map_exact_names(ours, dampsse_def, active_ids)
    print(f"\nName-mapped teids: {mapping['teid'].nunique()} of {ours['teid'].nunique()} ours")

    # Ambiguity accounting for the print below only (map_exact_names already
    # skips these internally): a normalized name that maps to >1 teid.
    name_to_teids = (
        ours.assign(_opeq_norm=ours["OP_EQCODE"].apply(normalize_name))
        .dropna(subset=["_opeq_norm"]).groupby("_opeq_norm")["teid"].apply(list)
    )
    dampsse_names = dampsse_def["branchNameRaw"].apply(normalize_name).dropna().unique()
    ambiguous_teid_names = sum(
        1 for n in dampsse_names
        if n in name_to_teids.index and len(set(name_to_teids[n])) > 1
    )
    print(f"Names skipped as ambiguous (one name -> multiple teids): {ambiguous_teid_names}")

    # --- status inference ---
    merged = mapping.merge(agg, on="ercotDampsseId", how="inner")
    per_teid = merged.groupby("teid").agg(
        n_hours=("n_hours", "sum"), n_inservice=("n_inservice", "sum"),
        dampsse_ids=("ercotDampsseId", "nunique"),
    ).reset_index()
    per_teid = compute_inservice_status(per_teid)

    table = pd.read_csv(TABLE_CSV)[
        ["teid", "branch_id", "implied_default_status", "pct_closed", "from_bus", "to_bus", "DeviceType"]
    ]
    out = per_teid.merge(table, on="teid", how="left")
    # One representative ercotDampsseId per teid: prefer the one active in
    # the current window (mapping already prefers active ids when a name
    # has several definitions over the years).
    rep = mapping.merge(agg[["ercotDampsseId"]], on="ercotDampsseId", how="left", indicator=True)
    rep = rep.sort_values("_merge", ascending=False).groupby("teid").first().reset_index()
    out = out.merge(
        rep[["teid", "ercotDampsseId", "dampsse_name_raw", "dampsse_from_station", "dampsse_to_station"]],
        on="teid", how="left",
    )
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_CSV, index=False)

    print(f"\nTeids with DAM PSSE status: {len(out)}")
    print("dampsse_default_status breakdown:")
    print(out["dampsse_default_status"].value_counts().to_string())

    both = out.dropna(subset=["implied_default_status"])
    agree = (both["dampsse_default_status"] == both["implied_default_status"]).sum()
    print(f"\nvs auction implied_default_status: {agree}/{len(both)} agree "
          f"({agree/len(both)*100:.1f}%)")
    dis = both[both["dampsse_default_status"] != both["implied_default_status"]]
    print("Disagreement directions:")
    print(dis.groupby(["implied_default_status", "dampsse_default_status"]).size().to_string())

    # --- the acid test: the robust base-model disagreements ---
    try:
        clean = pd.read_csv(CLEAN_CMP_CSV)
        outg = pd.read_csv(OUTAGE_CMP_CSV)
        robust = clean.merge(outg[["teid"]], on="teid", how="inner")
        rj = robust.merge(
            out[["teid", "dampsse_default_status", "pct_inservice", "n_hours"]],
            on="teid", how="left",
        )
        covered = rj.dropna(subset=["dampsse_default_status"])
        print(f"\n=== robust base-model disagreements ({robust['teid'].nunique()} teids) ===")
        print(f"Covered by DAM PSSE mapping: {covered['teid'].nunique()}")
        agrees_base = (covered["dampsse_default_status"] == covered["base_model_status"]).sum()
        agrees_ours = (covered["dampsse_default_status"] == covered["implied_default_status"]).sum()
        print(f"DAM PSSE agrees with BASE MODEL: {agrees_base}")
        print(f"DAM PSSE agrees with AUCTION (ours): {agrees_ours}")
        print("\nSample where DAM PSSE sides with base model:")
        flipped = covered[covered["dampsse_default_status"] == covered["base_model_status"]]
        cols = ["teid", "base_model_status", "implied_default_status",
                "dampsse_default_status", "pct_inservice", "base_from_name", "base_to_name"]
        print(flipped[cols].head(10).to_string())
    except FileNotFoundError:
        print("(base-model comparison files not found; skipping acid test)")

    print(f"\nWrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
