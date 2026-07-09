"""
Understand why BRANCH.teid has duplicates for isomarketid = 6 (ERCOT):
are they (a) the same physical branch inserted more than once (e.g. a newer
snapshot/re-run superseding an older row), or (b) teid genuinely reused
across two or more distinct branches (a real data-quality collision)?

BRANCH.b1/b2 are blank for the vast majority of rows (only populated for
BRKR-type rows) -- they are NOT a usable from/to bus identity check. The
real from/to bus numbers live in PTOBRANCH, joined via branchID -> BRANCHID
(see thoughts.md: "go from branch_id to pto_branch_id to get the branch
from/to bus number"). So identity here is (fromNum, toNum, ckt) pulled from
PTOBRANCH, not BRANCH.b1/b2/ckt.

Pulls the whole isomarketid=6 slice of BRANCH and PTOBRANCH (~122K /
~similar rows -- small enough) and does the grouping in pandas rather than
SQL Server CONCAT/TOP, which proved unreliable for this (non-deterministic
TOP N without ORDER BY inside a CTE gave inconsistent samples on repeat
runs).

Read-only. Writes only to branch_tracking/output/.
"""
from pathlib import Path

import awconnect
from awconnect import db

ISOMARKETID_ERCOT = 6

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_CSV = REPO_ROOT / "output" / "duplicate_teid_groups.csv"


def load_branch():
    return db.getDfFromAwDb(
        f"SELECT * FROM dbo.BRANCH WHERE isomarketid = {ISOMARKETID_ERCOT}"
    )


MAX_VALID_BUS_NUM = 900000  # bus numbers above this are placeholder/dummy buses


def load_ptobranch():
    return db.getDfFromAwDb(
        f"""
        SELECT ptoBranchID, branchID, fromNum, toNum, ckt AS pto_ckt, deviceType AS pto_deviceType
        FROM dbo.PTOBRANCH
        WHERE isomarketid = {ISOMARKETID_ERCOT}
          AND fromNum <= {MAX_VALID_BUS_NUM} AND toNum <= {MAX_VALID_BUS_NUM}
        """
    )


def identity_key(df):
    # Treat NaN/blank the same way so a NULL and an empty string aren't
    # counted as "different" identities.
    return (
        df["fromNum"].fillna(-1).astype(int).astype(str)
        + "|"
        + df["toNum"].fillna(-1).astype(int).astype(str)
        + "|"
        + df["pto_ckt"].fillna("").astype(str).str.strip()
    )


def main():
    awconnect.configure("read_only")
    branch = load_branch()
    ptobranch = load_ptobranch()

    # branchID isn't unique in PTOBRANCH -- it carries many rows per branchID
    # (multiple ptoBranchID versions). Keep the latest: largest ptoBranchID,
    # after already excluding placeholder/dummy bus numbers (> 900000).
    pto_dupe_branchids = ptobranch["branchID"].duplicated().sum()
    ptobranch_dedup = ptobranch.sort_values("ptoBranchID", ascending=False).drop_duplicates(
        subset="branchID", keep="first"
    )

    merged = branch.merge(ptobranch_dedup, on="branchID", how="left")

    with_teid = merged[merged["teid"].notna()].copy()
    with_teid["identity_key"] = identity_key(with_teid)
    with_teid["has_pto_match"] = with_teid["fromNum"].notna()

    dup_teids = with_teid.groupby("teid").filter(lambda g: len(g) > 1).copy()

    # Only trust the fromNum/toNum/ckt identity check where at least 2 rows
    # in the group actually have PTOBRANCH data -- a group with 0 or 1
    # pto-backed rows can't be compared at all, and treating an all-missing
    # group as "identical" (because the placeholder keys all match) would be
    # a false signal, not a real finding.
    n_pto_backed = dup_teids.groupby("teid")["has_pto_match"].transform("sum")
    n_distinct_identity = dup_teids.groupby("teid")["identity_key"].transform("nunique")

    dup_teids["dup_type"] = "insufficient_pto_data"
    comparable = n_pto_backed >= 2
    dup_teids.loc[comparable & (n_distinct_identity == 1), "dup_type"] = "same_identity_reinserted"
    dup_teids.loc[comparable & (n_distinct_identity > 1), "dup_type"] = "teid_collision_different_branches"

    same_devtype = dup_teids.groupby("teid")["DeviceType"].transform("nunique") == 1

    n_teids = dup_teids["teid"].nunique()
    counts_by_type = dup_teids.groupby("dup_type")["teid"].nunique()
    n_same_devtype_groups = dup_teids.loc[same_devtype, "teid"].nunique()

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    dup_teids.sort_values(["teid", "InsertDate"]).to_csv(OUTPUT_CSV, index=False)

    print(f"BRANCH rows (isomarketid={ISOMARKETID_ERCOT}): {len(branch)}")
    print(f"PTOBRANCH rows with a duplicated branchID (deduped, first kept): {pto_dupe_branchids}")
    print(f"BRANCH rows with NO matching PTOBRANCH row (fromNum/toNum unavailable): {(~with_teid['has_pto_match']).sum()}")
    print(f"Rows with NULL teid (excluded from this analysis): {branch['teid'].isna().sum()}")
    print(f"Distinct duplicated teids: {n_teids}")
    print(counts_by_type.to_string())
    print(f"  (for reference) groups with consistent DeviceType: {n_same_devtype_groups}")
    print(f"Wrote {OUTPUT_CSV} ({len(dup_teids)} rows)")


if __name__ == "__main__":
    main()
