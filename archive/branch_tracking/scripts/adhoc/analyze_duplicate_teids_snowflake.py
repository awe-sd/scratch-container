"""
Same analysis as analyze_duplicate_teids.py, but against the Snowflake
AW.DBO.BRANCH mirror instead of SQL Server dbo.BRANCH -- the two sources
already disagree on total row count for isomarketid = 6 (see
explore_branch_schema.py / explore_branch_sqlserver.py), so it's worth
checking whether the duplicate-teid picture differs too, not just the count.

Read-only. Writes only to branch_tracking/output/.
"""
from pathlib import Path

import awconnect
from awconnect import snowflake

ISOMARKETID_ERCOT = 6
DB_NAME = "AW"
SCHEMA = "DBO"

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_CSV = REPO_ROOT / "output" / "duplicate_teid_groups_snowflake.csv"


def load_branch():
    return snowflake.performQuery(
        dbName=DB_NAME,
        sqlQuery=f"SELECT * FROM {SCHEMA}.BRANCH WHERE ISOMARKETID = {ISOMARKETID_ERCOT}",
        logInfo=False,
    )


def identity_key(df):
    return (
        df["B1"].fillna("").astype(str).str.strip()
        + "|"
        + df["B2"].fillna("").astype(str).str.strip()
        + "|"
        + df["CKT"].fillna("").astype(str).str.strip()
    )


def main():
    awconnect.configure("read_only")
    branch = load_branch()

    with_teid = branch[branch["TEID"].notna()].copy()
    with_teid["identity_key"] = identity_key(with_teid)

    dup_teids = with_teid.groupby("TEID").filter(lambda g: len(g) > 1).copy()
    n_distinct_identity = dup_teids.groupby("TEID")["identity_key"].transform("nunique")
    dup_teids["dup_type"] = "same_identity_reinserted"
    dup_teids.loc[n_distinct_identity > 1, "dup_type"] = "teid_collision_different_branches"

    same_devtype = dup_teids.groupby("TEID")["DEVICETYPE"].transform("nunique") == 1

    n_teids = dup_teids["TEID"].nunique()
    n_same_devtype_groups = dup_teids.loc[same_devtype, "TEID"].nunique()
    n_mixed_devtype_groups = n_teids - n_same_devtype_groups

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    dup_teids.sort_values(["TEID", "INSERTDATE"]).to_csv(OUTPUT_CSV, index=False)

    print(f"BRANCH rows (isomarketid={ISOMARKETID_ERCOT}), Snowflake AW.DBO: {len(branch)}")
    print(f"Rows with NULL teid (excluded): {branch['TEID'].isna().sum()}")
    print(f"Distinct duplicated teids: {n_teids}")
    print(f"  groups with consistent DeviceType: {n_same_devtype_groups}")
    print(f"  groups with MIXED DeviceType (likely genuine collisions): {n_mixed_devtype_groups}")
    print(f"Wrote {OUTPUT_CSV} ({len(dup_teids)} rows)")


if __name__ == "__main__":
    main()
