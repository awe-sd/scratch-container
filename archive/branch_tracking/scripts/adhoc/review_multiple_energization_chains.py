"""
Ad hoc reviewer for the multiple_confirmed_energization_events bucket in
teid_inservice_retirement_dates.csv (237 teids as of this run). Not part of
the regular pipeline -- pulls all flagged teids' ReasonID=4 events in ONE
query (not one per teid) and reuses build_inservice_retirement_dates.py's
own filtering/chain logic, so the chain boundaries shown here exactly match
what produced the flag.

Output: one row per (teid, chain) -- its date range, BranchId/EquipmentName,
and a sample GroupLabel/Notes -- to eyeball whether the 237 share a common
explanation (like the teid=70365 bundled-clearance pattern) worth encoding
as another systematic fix, rather than reviewing 237 raw dumps by hand.

Read-only. Writes only to branch_tracking/output/ (a review worklist, not
a pipeline artifact).
"""
import sys
from pathlib import Path

import awconnect
import pandas as pd
from awconnect import db

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_inservice_retirement_dates import (
    ISOMARKETID_ERCOT, REASON_NEW_EQUIPMENT, is_invalid_status,
    assign_chain_ids,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESULT_CSV = REPO_ROOT / "output" / "teid_inservice_retirement_dates.csv"
TEID_MAP_CSV = REPO_ROOT / "output" / "teid_branch_id_map.csv"
OUTPUT_CSV = REPO_ROOT / "output" / "multiple_energization_review.csv"


def load_events(teids):
    teid_list = ",".join(str(int(t)) for t in teids)
    return db.getDfFromAwDb(
        f"""
        SELECT teid, BranchId, EquipmentName, ReasonID, toOutageIdentifierId,
               toStateId, plannedStartDate, plannedEndDate, actualStartDate,
               actualEndDate, CancellationDate, CancellationReason,
               status, ReqStatus, GroupLabel, Notes
        FROM AW.dbo.toChangesAllIsos
        WHERE isoMarketId = {ISOMARKETID_ERCOT}
          AND ReasonID = {REASON_NEW_EQUIPMENT}
          AND teid IN ({teid_list})
        """
    )


def main():
    awconnect.configure("read_only")

    result = pd.read_csv(RESULT_CSV)
    flagged_teids = result[result["review_flag"] == "multiple_confirmed_energization_events"]["teid"].tolist()
    print(f"Flagged teids: {len(flagged_teids)}")

    teid_map = pd.read_csv(TEID_MAP_CSV)
    legit_map = (
        teid_map[teid_map["match_status"] != "unmatched"][["teid", "branch_id"]]
        .drop_duplicates()
    )
    legit_map["branch_id"] = legit_map["branch_id"].astype(int)

    events = load_events(flagged_teids)
    events["event_date"] = events["actualStartDate"].fillna(events["plannedStartDate"])
    events["event_end_date"] = (
        events["actualEndDate"].fillna(events["plannedEndDate"]).fillna(events["event_date"])
    )
    events = events.dropna(subset=["event_date"])

    events = (
        events.sort_values("toStateId", ascending=False)
        .drop_duplicates(subset="toOutageIdentifierId", keep="first")
    )
    events["invalid"] = events.apply(is_invalid_status, axis=1)
    valid = events[~events["invalid"]].copy()

    merged = valid.merge(legit_map, on="teid", how="left")
    branch_mismatch = (
        merged["BranchId"].notna() & merged["branch_id"].notna()
        & (merged["BranchId"] != merged["branch_id"])
    )
    valid = merged[~branch_mismatch]

    actual_tier = valid[valid["actualStartDate"].notna()]

    rows = []
    for teid, group in actual_tier.groupby("teid"):
        tier = group.sort_values("event_date")
        tier = tier.assign(chain_id=assign_chain_ids(tier))
        for chain_id, chain in tier.groupby("chain_id"):
            rows.append({
                "teid": teid,
                "chain_id": chain_id,
                "n_tickets_in_chain": len(chain),
                "chain_start": chain["event_date"].min(),
                "chain_end": chain["event_end_date"].max(),
                "branch_ids": ", ".join(sorted(set(str(x) for x in chain["BranchId"].dropna().unique()))),
                "equipment_names": ", ".join(sorted(set(chain["EquipmentName"].dropna().unique()))),
                "group_labels": ", ".join(sorted(set(str(x) for x in chain["GroupLabel"].dropna().unique()))),
                "sample_notes": next((n for n in chain["Notes"].dropna() if n), None),
            })

    review = pd.DataFrame(rows).sort_values(["teid", "chain_id"])
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    review.to_csv(OUTPUT_CSV, index=False)

    print(f"Chains across {review['teid'].nunique()} teids: {len(review)}")
    print()
    print("=== gap between consecutive chains (chain N start - chain N-1 end), in days ===")
    gaps = []
    for teid, g in review.groupby("teid"):
        g = g.sort_values("chain_id")
        starts = pd.to_datetime(g["chain_start"]).tolist()
        ends = pd.to_datetime(g["chain_end"]).tolist()
        for i in range(1, len(g)):
            gaps.append((pd.Timestamp(starts[i]) - pd.Timestamp(ends[i - 1])).days)
    gap_series = pd.Series(gaps)
    print(gap_series.describe().to_string())
    print()
    print("=== equipment_names: same across chains vs different, per teid ===")
    same_or_diff = review.groupby("teid")["equipment_names"].nunique()
    print(f"teids where all chains share the same equipment_names: {(same_or_diff == 1).sum()}")
    print(f"teids where equipment_names differ across chains: {(same_or_diff > 1).sum()}")
    print(f"Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
