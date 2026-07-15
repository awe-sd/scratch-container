"""Fetch BOTH full shift vectors for constraint 35055 (Q1), cache to parquet.

PRE  psenShiftID 75138717 (2026-05-13 topology, ~859 res at shift>=0.05)
POST psenShiftID 87025608 (2026-07-12 topology, ~106 res at shift>=0.05)

All rows (any shift). Left-join cpnode for name/displayName and isoErcotScedGen
for ResourceName/ResourceType so we can see which generator nodes carry the
big shifts and which stations/areas dropped out between the two topologies.
"""
from pathlib import Path
import awconnect
import pandas as pd
from awconnect import db

DATA = Path(__file__).resolve().parents[1] / "data"
awconnect.configure("read_only")

for pid in (75138717, 87025608):
    f = DATA / f"thm_shiftvec_{pid}.parquet"
    if f.exists():
        print(f"cached {f.name}")
        continue
    sql = f"""
        SELECT ps.cpNodeId,
               (ps.psen*ps.psenShiftSign) AS shift,
               ps.psen, ps.psenShiftSign,
               c.name AS cpnode_name, c.displayName AS cpnode_display,
               c.type AS cpnode_type, c.voltage AS cpnode_voltage,
               g.ResourceName, g.ResourceType
        FROM AW.dbo.psenShiftView ps
        JOIN AW.dbo.cpnode c ON ps.cpNodeId = c.cpnodeid
        LEFT JOIN AW.dbo.isoErcotScedGen g ON g.cpnodeid = c.cpnodeid
        WHERE ps.psenShiftID = {pid}
    """
    df = db.getDfFromAwDb(sql)
    df.to_parquet(f, index=False)
    print(f"[{pid}] {len(df)} rows -> {f.name}")

# quick summary
for pid in (75138717, 87025608):
    df = pd.read_parquet(DATA / f"thm_shiftvec_{pid}.parquet")
    isgen = df["ResourceName"].notna()
    print(f"\n=== {pid} ===")
    print(f"total cpnodes rows: {len(df)}, generator-node rows: {isgen.sum()}, "
          f"distinct ResourceName: {df['ResourceName'].nunique()}")
    a = df["shift"].abs()
    for thr in (0.01, 0.05, 0.10, 0.20):
        print(f"  |shift|>={thr:.2f}: {(a>=thr).sum():4d} cpnodes | "
              f"signed>={thr:.2f}: {(df['shift']>=thr).sum():4d} | "
              f"gen signed>={thr:.2f}: {((df['shift']>=thr)&isgen).sum():4d}")
