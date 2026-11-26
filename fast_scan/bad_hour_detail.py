"""Bad-hour drill-down for a deep-dive constraint: reuses cached raw parquet + sign
resolution from constraint_deep_dive.py's pipeline instead of requerying Snowflake.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mismatch_analysis import resolve_signs_and_offset  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--branch", type=str, required=True)
    ap.add_argument("--ctg", type=str, required=True)
    ap.add_argument("--set-id", type=int, required=True)
    ap.add_argument("--date-from", type=str, required=True)
    ap.add_argument("--date-to", type=str, required=True)
    ap.add_argument("--rank-tol", type=float, default=0.01)
    ap.add_argument("--sign-guard", type=float, default=0.02)
    args = ap.parse_args()

    cache_dir = Path(__file__).resolve().parent / "output" / "validation_shift_compare" / str(args.study) / "cache"
    cache_path = cache_dir / f"{args.set_id}_{args.date_from}_{args.date_to}.parquet"
    raw = pd.read_parquet(cache_path)
    df, meta = resolve_signs_and_offset(raw, args.sign_guard)

    per_topo_hour = (
        df.groupby(["psenshiftid", "simdate", "simhour"])
        .agg(mae=("abs_diff", "mean"), max_abs_diff=("abs_diff", "max"),
             n_mismatch=("abs_diff", lambda s: (s > args.rank_tol).sum()))
        .reset_index()
    )
    clock_hour = (
        per_topo_hour.groupby(["simdate", "simhour"])
        .agg(mae=("mae", "max"), max_abs_diff=("max_abs_diff", "max"),
             n_mismatch=("n_mismatch", "max"), n_topo_variants=("psenshiftid", "nunique"))
        .reset_index().sort_values("max_abs_diff", ascending=False)
    )
    bad = clock_hour.iloc[0]
    bad_date, bad_hour = bad["simdate"], int(bad["simhour"])
    n_variants = int(bad["n_topo_variants"])

    bad_rows = df[(df["simdate"] == bad_date) & (df["simhour"] == bad_hour)].copy()
    bad_rows["study_plus_ref"] = bad_rows["study_psen"] + bad_rows["ref_psen"]
    n_mismatch_nodes = int((bad_rows.groupby("cpnodeid")["abs_diff"].max() > args.rank_tol).sum())

    top10 = (
        bad_rows.sort_values("abs_diff", ascending=False)
        .drop_duplicates("cpnodeid")
        .head(10)[["cpnodeid", "cpnode_name", "psenshiftid", "study_psen", "ref_psen",
                   "study_plus_ref", "dart_psen", "diff_adj"]]
        .rename(columns={"study_psen": "study_signed", "diff_adj": "diff"})
    )

    print(f"Bad clock-hour: {bad_date} hour {bad_hour}")
    print(f"Topology variants at this clock-hour: {n_variants} (psenshiftids: "
          f"{sorted(per_topo_hour[(per_topo_hour['simdate']==bad_date)&(per_topo_hour['simhour']==bad_hour)]['psenshiftid'].tolist())})")
    print(f"Distinct mismatched nodes (|diff|>{args.rank_tol}) at this hour: {n_mismatch_nodes}")
    print(top10.to_string(index=False))

    out_dir = Path(__file__).resolve().parent / "output" / "validation_shift_compare" / str(args.study) / "june"
    out_path = out_dir / f"deep_dive_{args.branch}_{args.ctg}_bad_hour.csv"
    top10.to_csv(out_path, index=False)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
