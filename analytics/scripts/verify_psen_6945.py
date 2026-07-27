"""
Read-only verification for the 6945 shift-factor decomposition.

The user supplied psenShiftID = 86037069 and pointed at:
  AW.dbo.psenShiftDef  (definition/lookup: congConstraintID -> psenShiftID)
  AW.dbo.psenShift     (the vector: psenShiftID, cpNodeId, psen)

We DO NOT run the INSERT the user pasted (all-zero row into a live table);
it was only shown to reveal psenShiftDef's columns. Everything here is SELECT.

Checks:
  1. Which source (SQL Server dbo vs Snowflake AW.DBO) actually has these tables.
  2. psenShiftDef row(s) for psenShiftID = 86037069 -> confirm branch/ctg = 6945.
  3. psenShiftDef rows for the 6945 congConstraintIDs -> is 86037069 among them?
  4. psenShift vector size + psen distribution for 86037069.
"""
import sys
from pathlib import Path

import awconnect
import pandas as pd
from awconnect import db, snowflake

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_common import load, parse_constraint_names  # noqa: E402

PSEN_ID = 86037069


def sqlserver_has(table):
    r = db.getDfFromAwDb(
        f"SELECT COUNT(*) n FROM INFORMATION_SCHEMA.TABLES "
        f"WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='{table}'"
    )
    return int(r["n"].iloc[0]) > 0


def main():
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 60)
    awconnect.configure("read_only")

    # 6945 constraint ids from local parquet
    defc = parse_constraint_names(load("congDefConstraint_ercot"))
    ids = sorted(
        defc[(defc.elem == "MGSES:345KV-CATSW:345KV") & defc.code.str.startswith("6945")]
        ["congConstraintID"].tolist()
    )
    print(f"6945 congConstraintIDs ({len(ids)}): {ids}")

    for t in ["psenShiftDef", "psenShift"]:
        print(f"\n=== dbo.{t} in SQL Server? {sqlserver_has(t)} ===")
        try:
            c = db.getDfFromAwDb(
                f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS "
                f"WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='{t}' ORDER BY ORDINAL_POSITION"
            )
            print(c.to_string())
        except Exception as e:
            print("cols ERROR:", e)

    # (2) def row for the given psen id
    print(f"\n=== psenShiftDef WHERE psenShiftID = {PSEN_ID} ===")
    try:
        d = db.getDfFromAwDb(
            f"SELECT psenShiftID, congConstraintID, branchConstraintID, branchLabel, "
            f"ctgLabel, interfaceName, direction, referenceBus, fromBus, toBus, ckt, "
            f"topologyID, fDateHB, beginDate, endDate, psenShiftCreationDate, description "
            f"FROM dbo.psenShiftDef WHERE psenShiftID = {PSEN_ID}"
        )
        print(d.to_string())
    except Exception as e:
        print("ERROR:", e)

    # (3) def rows for the 6945 congConstraintIDs
    idlist = ",".join(str(i) for i in ids)
    print(f"\n=== psenShiftDef WHERE congConstraintID IN (6945 ids) — is {PSEN_ID} present? ===")
    try:
        d2 = db.getDfFromAwDb(
            f"SELECT psenShiftID, congConstraintID, branchLabel, ctgLabel, direction, "
            f"fDateHB, psenShiftCreationDate "
            f"FROM dbo.psenShiftDef WHERE congConstraintID IN ({idlist}) "
            f"ORDER BY psenShiftCreationDate DESC"
        )
        print(f"rows: {len(d2)}; contains {PSEN_ID}: {PSEN_ID in set(d2['psenShiftID'])}")
        print(d2.head(25).to_string())
    except Exception as e:
        print("ERROR:", e)

    # (4) the vector
    print(f"\n=== psenShift vector for {PSEN_ID} ===")
    try:
        v = db.getDfFromAwDb(
            f"SELECT COUNT(*) n_nodes, MIN(psen) min_psen, MAX(psen) max_psen, "
            f"SUM(CASE WHEN psen > 0 THEN 1 ELSE 0 END) n_pos, "
            f"SUM(CASE WHEN psen < 0 THEN 1 ELSE 0 END) n_neg "
            f"FROM dbo.psenShift WHERE psenShiftID = {PSEN_ID}"
        )
        print(v.to_string())
        top = db.getDfFromAwDb(
            f"SELECT TOP 10 psenShiftID, cpNodeId, psen FROM dbo.psenShift "
            f"WHERE psenShiftID = {PSEN_ID} ORDER BY ABS(psen) DESC"
        )
        print("--- top |psen| nodes ---")
        print(top.to_string())
    except Exception as e:
        print("ERROR:", e)


if __name__ == "__main__":
    main()
