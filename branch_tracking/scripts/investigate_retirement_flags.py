"""
Ad hoc investigation of the two remaining open review_flag categories in
teid_inservice_retirement_dates.csv: multiple_confirmed_retirement_events
(11 teids) and retirement_before_inservice (8 teids, flagged by the user as
most critical -- possible TSP mis-tagging of ReasonID, later corrected).

Pulls ALL revisions and ALL ReasonID values (not just 4/9) for these 19
teids in ONE query, so a ReasonID change across a single
toOutageIdentifierId's own revision history -- the signature of an
initial-mistag-then-fix -- is directly visible.

Read-only. Writes only to branch_tracking/output/ (a review aid).
"""
from pathlib import Path

import awconnect
import pandas as pd
from awconnect import db

ISOMARKETID_ERCOT = 6

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULT_CSV = REPO_ROOT / "output" / "teid_inservice_retirement_dates.csv"
OUTPUT_CSV = REPO_ROOT / "output" / "retirement_flags_investigation.csv"


def load_all_revisions(teids):
    teid_list = ",".join(str(int(t)) for t in teids)
    return db.getDfFromAwDb(
        f"""
        SELECT teid, BranchId, EquipmentName, ReasonID, toOutageIdentifierId,
               outageIdentifier, toStateId, plannedStartDate, plannedEndDate,
               actualStartDate, actualEndDate, submitTime, insertDate,
               CancellationDate, CancellationReason, status, ReqStatus,
               GroupLabel, Notes
        FROM AW.dbo.toChangesAllIsos
        WHERE isoMarketId = {ISOMARKETID_ERCOT}
          AND teid IN ({teid_list})
        ORDER BY teid, toOutageIdentifierId, toStateId
        """
    )


def main():
    awconnect.configure("read_only")

    result = pd.read_csv(RESULT_CSV)
    mre = result[result["review_flag"] == "multiple_confirmed_retirement_events"]["teid"].tolist()
    rbi = result[result["review_flag"] == "retirement_before_inservice"]["teid"].tolist()
    teids = sorted(set(mre) | set(rbi))
    print(f"multiple_confirmed_retirement_events: {len(mre)} teids")
    print(f"retirement_before_inservice: {len(rbi)} teids")
    print(f"Combined (deduped): {len(teids)} teids")

    events = load_all_revisions(teids)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    events.to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {len(events)} raw revision rows to {OUTPUT_CSV}")
    print()

    print("=== ReasonID changes WITHIN a single toOutageIdentifierId's own revision history ===")
    print("(the signature of an initial mis-tag later corrected)")
    reason_changes = events.groupby(["teid", "toOutageIdentifierId"])["ReasonID"].nunique()
    changed = reason_changes[reason_changes > 1]
    print(f"toOutageIdentifierIds with more than one distinct ReasonID across revisions: {len(changed)}")
    if len(changed):
        for (teid, oid), n in changed.items():
            sub = events[(events["teid"] == teid) & (events["toOutageIdentifierId"] == oid)]
            reasons = sub.sort_values("toStateId")[["toStateId", "ReasonID", "status", "actualStartDate", "actualEndDate"]]
            print(f"\nteid={teid}, toOutageIdentifierId={oid}:")
            print(reasons.to_string())

    print()
    print("=== distinct ReasonID values seen per teid (across ALL its outages, any identifier) ===")
    per_teid_reasons = events.groupby("teid")["ReasonID"].apply(lambda s: sorted(s.dropna().unique()))
    print(per_teid_reasons.to_string())


if __name__ == "__main__":
    main()
