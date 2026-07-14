"""
Small cross-source pulls for the 6945 decomposition + integrity checks.
Read-only. Writes only parquet under analytics/data/.

  A. psenShift vector for 86037069           (SQL Server dbo, 1114 rows)
  B. SCED gen dim isoErcotScedGen            (Snowflake AW.DBO, ~1810 rows)
  C. wind unit->region mapping               (SQL Server dbo)

Then diagnostics:
  - distinct SCED ResourceType among wind-mapped units
  - cpnode-id overlap between SCED dim and the psen vector (join integrity!)
"""
from pathlib import Path

import awconnect
import pandas as pd
from awconnect import db, snowflake

DATA = Path(__file__).resolve().parents[1] / "data"
PSEN_ID = 86037069


def main():
    pd.set_option("display.width", 220)
    awconnect.configure("read_only")

    # A. psen vector
    psen = db.getDfFromAwDb(
        f"SELECT psenShiftID, cpNodeId, psen FROM dbo.psenShift WHERE psenShiftID = {PSEN_ID}"
    )
    psen.to_parquet(DATA / f"psenShift_{PSEN_ID}.parquet", index=False)
    print(f"A. psenShift vector: {len(psen)} nodes -> psenShift_{PSEN_ID}.parquet")

    # B. SCED gen dim (Snowflake). Keep latest attribute row per genId.
    dim = snowflake.performQuery(
        dbName="AW",
        sqlQuery="""
        SELECT genId, ResourceName, ResourceType, cpnodeid, QSE, insertDate
        FROM AW.DBO.isoErcotScedGen
        QUALIFY ROW_NUMBER() OVER (PARTITION BY genId ORDER BY insertDate DESC) = 1
        """,
        warehouse=snowflake.READ_ONLY_WH,
    )
    dim.to_parquet(DATA / "sced_gen_dim.parquet", index=False)
    print(f"B. SCED gen dim: {len(dim)} genIds -> sced_gen_dim.parquet")
    print("   ResourceType counts:")
    print(dim["ResourceType"].value_counts().to_string())

    # C. wind unit -> region
    clu = db.getDfFromAwDb(
        "SELECT unitName, windCluster, awepWindCluster, county, clusterId "
        "FROM dbo.ercotWindClusterUnitMapping"
    )
    reg = db.getDfFromAwDb(
        "SELECT windRegion, awepWindRegion, county, countyId "
        "FROM dbo.ercotWindRegionCountyMapping"
    )
    clu.to_parquet(DATA / "wind_cluster_unit_map.parquet", index=False)
    reg.to_parquet(DATA / "wind_region_county_map.parquet", index=False)
    unit_region = clu.merge(reg[["county", "windRegion"]], on="county", how="left")
    unit_region.to_parquet(DATA / "wind_unit_region.parquet", index=False)
    print(f"C. wind units: {len(clu)}; region coverage:")
    print(unit_region["windRegion"].value_counts(dropna=False).to_string())

    # ---- diagnostics ----
    dim["ResourceName_u"] = dim["ResourceName"].str.upper().str.strip()
    unit_region["unitName_u"] = unit_region["unitName"].str.upper().str.strip()
    wind_units = set(unit_region["unitName_u"])
    dim_wind = dim[dim["ResourceName_u"].isin(wind_units)]
    print(f"\nSCED units matching wind mapping by name: {len(dim_wind)} of {len(dim)}")
    print("   their ResourceType:")
    print(dim_wind["ResourceType"].value_counts().to_string())

    # cpnode overlap between SCED dim and psen vector — THE critical join
    sced_cp = set(pd.to_numeric(dim["cpnodeid"], errors="coerce").dropna().astype(int))
    psen_cp = set(psen["cpNodeId"].astype(int))
    windsced_cp = set(pd.to_numeric(dim_wind["cpnodeid"], errors="coerce").dropna().astype(int))
    print(f"\ncpnode overlap: SCED-dim ∩ psen = {len(sced_cp & psen_cp)} "
          f"(SCED {len(sced_cp)}, psen {len(psen_cp)})")
    print(f"cpnode overlap: SCED-wind ∩ psen = {len(windsced_cp & psen_cp)} of {len(windsced_cp)} wind cpnodes")

    # wind cpnodes that carry psen, split by region, with psen sign
    dim_wind = dim_wind.copy()
    dim_wind["cpnodeid_i"] = pd.to_numeric(dim_wind["cpnodeid"], errors="coerce")
    j = dim_wind.merge(psen, left_on="cpnodeid_i", right_on="cpNodeId", how="inner")
    j = j.merge(unit_region[["unitName_u", "windRegion"]].drop_duplicates("unitName_u"),
                left_on="ResourceName_u", right_on="unitName_u", how="left")
    print("\nmean psen by wind region (units on the 6945 vector):")
    print(j.groupby("windRegion")["psen"].agg(["count", "mean", "min", "max"]).round(4).to_string())


if __name__ == "__main__":
    main()
