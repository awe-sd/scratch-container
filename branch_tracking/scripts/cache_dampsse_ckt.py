"""
Cache each ercotDampsseId's psseCktId (circuit id) locally, so
map_unmapped_dampsse_teids.py can add a circuit-aware tier to resolve
station-pair-ambiguous candidates (parallel elements between the same two
stations differ by circuit id).

psseCktId lives on the hourly fact (ercotDampsseTimeseries), not the Def
dimension -- aggregate over a recent window (an element's ckt id is
stable; GROUP BY collapses the hours) rather than sampling one hour, so
elements on outage during any single hour still appear.

Read-only. Writes only to branch_tracking/data/raw/.
"""
from pathlib import Path

import awconnect
from awconnect import db

CKT_WINDOW_DAYS = 90

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"


def main():
    awconnect.configure("read_only")

    max_row = db.getDfFromAwDb(
        "SELECT MAX(awDateID) AS max_id FROM AW.dbo.ercotDampsseTimeseries"
    )
    cutoff = int(max_row["max_id"].iloc[0]) - CKT_WINDOW_DAYS

    ckt = db.getDfFromAwDb(
        f"""
        SELECT ercotDampsseId, psseCktId,
               MAX(psseFromBusNumber) AS psseFromBusNumber,
               MAX(psseToBusNumber) AS psseToBusNumber,
               COUNT(*) AS n_hours
        FROM AW.dbo.ercotDampsseTimeseries
        WHERE ercotDampsseFileTypeId IN (1, 2)
          AND awDateID > {cutoff}
        GROUP BY ercotDampsseId, psseCktId
        """
    )
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ckt.to_csv(RAW_DIR / "dampsse_ckt_snapshot.csv", index=False)
    print(f"Elements with ckt cached: {ckt['ercotDampsseId'].nunique()} ({len(ckt)} rows)")
    multi = ckt.groupby("ercotDampsseId").size()
    print(f"Elements with >1 distinct psseCktId in window: {(multi > 1).sum()}")
    print(f"Wrote {RAW_DIR / 'dampsse_ckt_snapshot.csv'}")


if __name__ == "__main__":
    main()
