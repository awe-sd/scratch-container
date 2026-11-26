"""Refresh the EIA parquet slices the research tools read — the snapshot query, on disk.

The queue-research tools (`eia_history.py`, `spv.py`, `build_brief.py`) depend on two local
parquet slices of the EIA objects in SQL Server `AW.dbo`. Until now the SQL that produced them
lived nowhere on disk; this tool IS that SQL, so the slices can be re-pulled deterministically.

Slices (see gis-research/docs/eia_db_reference.md for the full schema review):
  generator  data/eia_generator_tx.parquet  — TX monthly generator inventory (EIA-860M),
             AW.dbo.eiaGenerator denormalized w/ plant/entity/status/technology. Monthly
             grain (reportDate × plantId × generatorId), 2022-04 →. The second-source
             history: planned COD, MW/MWh capacity, EIA status, operating date, coordinates.
  plant      data/eia_plant_tx.parquet      — TX plant-location file (EIA-860 annual),
             AW.dbo.eia860plant WHERE state='TX'. Fixed lat/lon/county per plant.

The generator slice keeps the original 17 columns byte-for-byte (so eia_history.py is
unaffected) and APPENDS four fully-populated columns the schema review surfaced:
nameplateEnergyCapacity (storage MWh), latitude, longitude, county. Matching logic elsewhere
is unchanged; these are an additive cross-check.

Usage (agents: run from repo root with `uv run`):
  eia_snapshot.py                 # refresh every slice
  eia_snapshot.py --only generator
  eia_snapshot.py --list          # show slice names and their outputs

Idempotent — overwrites the parquet(s) in place and prints row/column counts. Read-only DB.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]  # gis-research/
DATA = BASE / "data"

# The generator slice: exact filter that reproduces eia_generator_tx.parquet is
# plantState='TX' + INNER JOIN eiaStatus (drops null-status rows), LEFT joins otherwise.
# First 17 SELECT columns are the original slice, in order; last 4 are the additions.
GENERATOR_SQL = """
SELECT g.reportDate, g.plantId, p.eiaPlantName, e.eiaEntityName, g.generatorId,
       g.nameplateCapacity, g.netSummerCapacity, g.energySourceCode, g.primeMoverCode,
       t.eiaTechnology, s.eiaStatus,
       g.plannedOperationYear, g.plannedOperationMonth, g.operatingYear, g.operatingMonth,
       g.plannedRetirementYear, g.plannedRetirementMonth,
       g.nameplateEnergyCapacity, g.latitude, g.longitude, g.county
FROM dbo.eiaGenerator g
LEFT JOIN  dbo.eiaPlant p      ON g.plantId         = p.eiaPlantId
LEFT JOIN  dbo.eiaEntity e     ON g.entityId        = e.eiaEntityId
INNER JOIN dbo.eiaStatus s     ON g.eiaStatusId     = s.eiaStatusId
LEFT JOIN  dbo.eiaTechnology t ON g.eiaTechnologyId = t.eiaTechnologyId
WHERE g.plantState = 'TX'
"""

PLANT_SQL = """
SELECT yr, plantCode, plantName, utilityId, utilityName, city, county,
       latitude, longitude, balancingAuthorityCode
FROM dbo.eia860plant
WHERE state = 'TX'
"""

# per-slice: output filename, SQL, and columns to coerce (to reproduce existing dtypes:
# decimals/tinyint-with-nulls -> float64; ids -> int64; varchar stay str; date stays date).
SLICES = {
    "generator": {
        "out": "eia_generator_tx.parquet",
        "sql": GENERATOR_SQL,
        "int_cols": ["plantId"],
        "float_cols": ["nameplateCapacity", "netSummerCapacity", "plannedOperationYear",
                       "plannedOperationMonth", "operatingYear", "operatingMonth",
                       "plannedRetirementYear", "plannedRetirementMonth",
                       "nameplateEnergyCapacity", "latitude", "longitude"],
    },
    "plant": {
        "out": "eia_plant_tx.parquet",
        "sql": PLANT_SQL,
        "int_cols": ["yr", "plantCode", "utilityId"],
        "float_cols": ["latitude", "longitude"],
    },
}


def refresh(name: str, spec: dict, db) -> None:
    df = db.getDfFromAwDb(spec["sql"])
    for c in spec.get("int_cols", []):
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("int64")
    for c in spec.get("float_cols", []):
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("float64")
    out = DATA / spec["out"]
    df.to_parquet(out, index=False)
    span = ""
    if "reportDate" in df.columns:
        span = f", reportDate {df.reportDate.min()} -> {df.reportDate.max()}"
    print(f"{name}: {len(df):,} rows x {df.shape[1]} cols{span} -> data/{spec['out']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", choices=sorted(SLICES), help="refresh a single slice")
    ap.add_argument("--list", action="store_true", help="list slice names and outputs, then exit")
    a = ap.parse_args()

    if a.list:
        for name, spec in SLICES.items():
            print(f"{name}: data/{spec['out']}")
        return

    import awconnect
    awconnect.configure("read_only")
    from awconnect import db

    names = [a.only] if a.only else list(SLICES)
    for name in names:
        refresh(name, SLICES[name], db)
    print(f"done ({len(names)} slice{'s' if len(names) != 1 else ''})")


if __name__ == "__main__":
    main()
