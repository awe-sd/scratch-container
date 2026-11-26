"""
For the duplicate_match teids in output/teid_branch_id_map.csv that have
exactly 2 matching branch_ids, check whether OP_EQCODE agrees between the
two BRANCH rows -- i.e. are these actually the same physical element listed
under two different branch_id values, or genuinely different elements that
happen to share a teid?

Note: pandas' nunique() excludes NaN by default, so a naive
"OP_EQCODE.nunique() == 1" check silently miscounts "both blank" as
"different" (nunique returns 0, not 1). This treats OP_EQCODE consistently
by filling blanks first, then classifies into three buckets rather than two.

Read-only. Writes only to branch_tracking/output/.
"""
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_CSV = REPO_ROOT / "output" / "teid_branch_id_map.csv"
OUTPUT_CSV = REPO_ROOT / "output" / "duplicate_opeqcode_classified.csv"


def main():
    df = pd.read_csv(INPUT_CSV)
    dup = df[df["match_status"] == "duplicate_match"].copy()

    n_branch_per_teid = dup.groupby("teid")["branch_id"].transform("nunique")
    two_branch = dup[n_branch_per_teid == 2].copy()

    two_branch["OP_EQCODE_filled"] = two_branch["OP_EQCODE"].fillna("<BLANK>")
    distinct_opeq = two_branch.groupby("teid")["OP_EQCODE_filled"].transform("nunique")

    two_branch["opeq_status"] = "different"
    two_branch.loc[
        (distinct_opeq == 1) & (two_branch["OP_EQCODE_filled"] == "<BLANK>"), "opeq_status"
    ] = "both_blank"
    two_branch.loc[
        (distinct_opeq == 1) & (two_branch["OP_EQCODE_filled"] != "<BLANK>"), "opeq_status"
    ] = "same_element"

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    two_branch.drop(columns=["OP_EQCODE_filled"]).sort_values("teid").to_csv(
        OUTPUT_CSV, index=False
    )

    n_teids = two_branch["teid"].nunique()
    status_counts = two_branch.groupby("teid")["opeq_status"].first().value_counts()

    print(f"duplicate_match teids with exactly 2 branch_ids: {n_teids}")
    print(status_counts.to_string())
    print(f"Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
