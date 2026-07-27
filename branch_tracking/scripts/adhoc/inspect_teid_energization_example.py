"""
One-off inspection of a single teid's energization event history, to
explain why it landed in the multiple_confirmed_energization_events
review_flag bucket. Not part of the regular pipeline -- ad hoc diagnostic.

Read-only.
"""
import sys

import awconnect
import pandas as pd
from awconnect import db

ISOMARKETID_ERCOT = 6
REASON_NEW_EQUIPMENT = 4

TEID = int(sys.argv[1]) if len(sys.argv) > 1 else 527244


def main():
    awconnect.configure("read_only")

    events = db.getDfFromAwDb(
        f"""
        SELECT teid, BranchId, EquipmentName, FacilityName, CommonName,
               ReasonID, toOutageIdentifierId, outageIdentifier, toStateId,
               plannedStartDate, plannedEndDate, actualStartDate, actualEndDate,
               submitTime, insertDate, CancellationDate, CancellationReason,
               status, ReqStatus, GroupLabel, Notes
        FROM AW.dbo.toChangesAllIsos
        WHERE isoMarketId = {ISOMARKETID_ERCOT}
          AND teid = {TEID}
          AND ReasonID = {REASON_NEW_EQUIPMENT}
        ORDER BY toOutageIdentifierId, toStateId
        """
    )
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 240)
    print(f"teid={TEID}, ReasonID={REASON_NEW_EQUIPMENT} (New Equipment Energization): {len(events)} raw rows")
    print(events.to_string())

    print()
    print("=== collapsed to latest toStateId per toOutageIdentifierId ===")
    latest = (
        events.sort_values("toStateId", ascending=False)
        .drop_duplicates(subset="toOutageIdentifierId", keep="first")
        .sort_values("toOutageIdentifierId")
    )
    print(latest.to_string())

    print()
    print("=== distinct BranchId / EquipmentName combos for this teid ===")
    print(events[["BranchId", "EquipmentName", "FacilityName", "CommonName"]].drop_duplicates().to_string())


if __name__ == "__main__":
    main()
