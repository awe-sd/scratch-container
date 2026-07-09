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
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from branch_tracking.pipeline.naming import normalize_name  # noqa: E402

import awconnect
import pandas as pd
from awconnect import db

WINDOW_DAYS = 730  # ~2 years of hourly DA models, per the user's direction
AWDATEID_ANCHOR = (44926, date(2023, 1, 1))  # confirmed by schema exploration

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
    ours["opeq_norm"] = ours["OP_EQCODE"].apply(normalize_name)

    dampsse_def["name_norm"] = dampsse_def["branchNameRaw"].apply(normalize_name)
    st = stations.set_index("ercotDampsseStationId")
    dampsse_def["from_station"] = dampsse_def["fromStationId"].map(st["stationName"])
    dampsse_def["to_station"] = dampsse_def["toStationId"].map(st["stationName"])

    # Exact normalized-name match. Ambiguity accounting: a normalized name
    # can appear on multiple dampsse ids (re-definitions over the years) or
    # multiple teids -- keep 1:1 matches as high confidence; for
    # many-dampsse-to-one-teid keep the dampsse id with hourly data in the
    # current window (i.e., currently published), reporting how often that
    # resolves it.
    ours_by_name = ours.dropna(subset=["opeq_norm"]).groupby("opeq_norm")
    name_to_teids = ours_by_name["teid"].apply(list)

    active_ids = set(agg["ercotDampsseId"])
    rows = []
    ambiguous_teid_names = 0
    for name, group in dampsse_def.dropna(subset=["name_norm"]).groupby("name_norm"):
        teids = name_to_teids.get(name)
        if teids is None:
            continue
        if len(set(teids)) > 1:
            ambiguous_teid_names += 1
            continue
        teid = teids[0]
        cands = group
        if len(cands) > 1:
            in_window = cands[cands["ercotDampsseId"].isin(active_ids)]
            cands = in_window if len(in_window) else cands.tail(1)
        for _, c in cands.iterrows():
            rows.append({
                "teid": teid,
                "ercotDampsseId": c["ercotDampsseId"],
                "dampsse_name_raw": c["branchNameRaw"],
                "dampsse_from_station": c["from_station"],
                "dampsse_to_station": c["to_station"],
                "dampsse_filetype": c["ercotDampsseFileTypeId"],
            })
    mapping = pd.DataFrame(rows).drop_duplicates(subset=["teid", "ercotDampsseId"])
    print(f"\nName-mapped teids: {mapping['teid'].nunique()} of {ours['teid'].nunique()} ours")
    print(f"Names skipped as ambiguous (one name -> multiple teids): {ambiguous_teid_names}")

    # --- status inference ---
    merged = mapping.merge(agg, on="ercotDampsseId", how="inner")
    per_teid = merged.groupby("teid").agg(
        n_hours=("n_hours", "sum"), n_inservice=("n_inservice", "sum"),
        dampsse_ids=("ercotDampsseId", "nunique"),
    ).reset_index()
    per_teid["pct_inservice"] = (per_teid["n_inservice"] / per_teid["n_hours"]).round(4)
    per_teid["dampsse_default_status"] = per_teid["pct_inservice"].apply(
        lambda p: "Closed" if p >= 0.5 else "Open"
    )

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
