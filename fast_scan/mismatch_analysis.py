"""Row-level mismatch analysis for validation-fast-scan shift comparisons.
Reuses the June (2026-06-01..2026-06-30) per-set cache already pulled by
compare_validation_shifts.py (cache/<set_id>_2026-06-01_2026-06-30.parquet).

GRAIN, precisely (2026-09-12 round-2 fix): a "topology-hour" (psenshiftid) is
a (topology VARIANT x clock-hour) pair -- several variants can share the same
clock-hour (e.g. 6965/MCATPRL5 2026-06-30 h15 has 4 variants). Counts are
reported at BOTH grains: n_bad_topology_variants (variant grain) and
bad_clock_hours/tot_clock_hours (distinct simdate+simhour grain, what a human
means by "hours"). Table 1 is sorted by severity (max nodes off in any bad
hour, then avg|diff| in bad hours), which is what Table 1b (the flat list of
bad hours) is also sorted by -- the two agree by construction.

Sign is resolved PER TOPOLOGY-HOUR: diagnosis found the same branch/ctg text
label can span multiple DART congConstraintID/congMontID definitions over
time with opposite orientation; a per-config fit averages over this. A
SIGN_UNRESOLVED guard (--sign-guard, default 0.02) flags topologies where
neither sign fits well (min(mae_pos,mae_neg) > guard); such topologies keep
the study convention sign +1 rather than picking a spurious "best" sign.

REF_OFFSET: a near-constant bias across nearly all of a config's cpnodes
(reference-bus normalization offset) is subtracted before mismatch counting;
before/after June-wide mismatching-node counts are both reported.

DUP_FANOUT: root cause was duplicate rows inside AW.dbo.PSENSHIFT itself
(and mirrored on the study side) -- fixed upstream in compare_validation_shifts
.py via QUALIFY ROW_NUMBER() dedupe in both CTEs; the 3 affected sets were
re-pulled with cache bypass before this script ran.

Node/day analysis and SYSTEMIC/CONSTRAINT_SPECIFIC/MIXED labels are rebased
on BAD CLOCK-HOURS only, and a node must be off in >=2 bad clock-hours of a
constraint to count as "off in constraint X" (a single bad hour no longer
taints a node's whole-June record).
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "powerflow_analytics"))
from pfa.sf import query  # noqa: E402

REF_TOLS = [0.0005, 0.001, 0.01]
REF_OFFSET_BAND = 0.002
MIN_BAD_CLOCK_HOURS_FOR_MEMBERSHIP = 2


def get_configs(study_id: int, created_after: str) -> pd.DataFrame:
    sql = f"""
    SELECT TOPOLOGYSHIFTSETID, BRANCHLABEL, CTGLABEL, INTERFACENAME, DIRECTION
    FROM AW.POPT.TOPOLOGYSHIFTSETDEF
    WHERE STUDYID={study_id} AND CREATEDATE >= '{created_after}'
    """
    return query("AW", sql)


def resolve_signs_and_offset(raw: pd.DataFrame, sign_guard: float) -> tuple[pd.DataFrame, dict]:
    df = raw.copy()
    df["diff_pos"] = df["psens_raw"] + df["ref_psen"] - df["dart_psen"]
    df["diff_neg"] = -1 * df["psens_raw"] + df["ref_psen"] - df["dart_psen"]

    per_topo = df.groupby("psenshiftid").agg(
        mae_pos=("diff_pos", lambda s: s.abs().mean()),
        mae_neg=("diff_neg", lambda s: s.abs().mean()),
    )
    per_topo["fit_sign"] = np.where(per_topo["mae_pos"] <= per_topo["mae_neg"], 1, -1)
    per_topo["min_mae"] = per_topo[["mae_pos", "mae_neg"]].min(axis=1)
    per_topo["SIGN_UNRESOLVED"] = per_topo["min_mae"] > sign_guard
    per_topo["sign"] = np.where(per_topo["SIGN_UNRESOLVED"], 1, per_topo["fit_sign"])

    df = df.merge(per_topo[["sign", "SIGN_UNRESOLVED"]], on="psenshiftid", how="left")

    df["diff"] = np.where(df["sign"] == 1, df["diff_pos"], df["diff_neg"])
    df["abs_diff_raw"] = df["diff"].abs()
    df["study_psen"] = df["sign"] * df["psens_raw"]

    n_topo_pos = int((per_topo["sign"] == 1).sum())
    n_topo_neg = int((per_topo["sign"] == -1).sum())
    n_topo_total = n_topo_pos + n_topo_neg
    mixed_sign = n_topo_pos > 0 and n_topo_neg > 0
    sign_agreement_rate = max(n_topo_pos, n_topo_neg) / n_topo_total if n_topo_total else np.nan
    n_sign_unresolved = int(per_topo["SIGN_UNRESOLVED"].sum())

    bias = df["diff"].mean()
    mae = df["abs_diff_raw"].mean()
    per_node_bias = df.groupby("cpnodeid")["diff"].mean()
    share_in_band = (per_node_bias.sub(bias).abs() <= REF_OFFSET_BAND).mean() if len(per_node_bias) else 0
    ref_offset = bool(mae > 0 and abs(bias) > 0.8 * mae and share_in_band >= 0.90)

    df["diff_before_offset"] = df["diff"]
    df["diff_adj"] = df["diff"] - bias if ref_offset else df["diff"]
    df["abs_diff"] = df["diff_adj"].abs()

    meta = {
        "n_topo_sign_pos": n_topo_pos, "n_topo_sign_neg": n_topo_neg,
        "sign_agreement_rate": sign_agreement_rate, "mixed_sign": mixed_sign,
        "n_sign_unresolved": n_sign_unresolved,
        "bias_raw": bias, "mae_raw": mae,
        "share_cpnodes_in_offset_band": share_in_band, "ref_offset": ref_offset,
    }
    return df, meta


def load_all_raw(cache_dir: Path, configs: pd.DataFrame, date_from: str, date_to: str, sign_guard: float) -> dict:
    raws, metas = {}, {}
    for _, r in configs.iterrows():
        set_id = int(r["TOPOLOGYSHIFTSETID"])
        p = cache_dir / f"{set_id}_{date_from}_{date_to}.parquet"
        if p.exists():
            df = pd.read_parquet(p)
            if not df.empty:
                df, meta = resolve_signs_and_offset(df, sign_guard)
                raws[set_id] = df
                metas[set_id] = meta
    return raws, metas


def june_wide_node_rate(df: pd.DataFrame, col: str, rank_tol: float) -> int:
    per_node = df.groupby("cpnodeid").agg(
        matched=("psenshiftid", "size"),
        mism=(col, lambda s: (s.abs() > rank_tol).sum()),
    )
    per_node["rate"] = per_node["mism"] / per_node["matched"]
    return int((per_node["rate"] >= 0.10).sum())


def build_topology_hour_table(raws: dict, configs: pd.DataFrame, rank_tol: float, hour_bad_share: float) -> pd.DataFrame:
    label_map = configs.set_index("TOPOLOGYSHIFTSETID")[["BRANCHLABEL", "CTGLABEL"]].to_dict("index")
    frames = []
    for set_id, df in raws.items():
        g = df.groupby(["psenshiftid", "simdate", "simhour"]).agg(
            n_nodes=("cpnodeid", "size"),
            n_mismatch_nodes=("abs_diff", lambda s: (s > rank_tol).sum()),
            avg_abs_diff_mismatch=("abs_diff", lambda s: s[s > rank_tol].mean() if (s > rank_tol).any() else np.nan),
            max_abs_diff=("abs_diff", "max"),
            TOPOLOGYID=("topologyid", "first"),
            RUNBEGINTIME=("runbegintime", "first"),
            SIGN_UNRESOLVED=("SIGN_UNRESOLVED", "first"),
        ).reset_index()
        g["set_id"] = set_id
        g["BRANCHLABEL"] = label_map[set_id]["BRANCHLABEL"]
        g["CTGLABEL"] = label_map[set_id]["CTGLABEL"]
        g["share_mismatch_nodes"] = g["n_mismatch_nodes"] / g["n_nodes"]
        g["BAD"] = g["share_mismatch_nodes"] >= hour_bad_share
        frames.append(g)
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if not out.empty:
        out["simdate"] = pd.to_datetime(out["simdate"]).dt.strftime("%Y-%m-%d")
    return out


def build_constraint_summary(raws: dict, metas: dict, configs: pd.DataFrame, topo_hours: pd.DataFrame,
                              rank_tol: float, node_rate: float):
    label_map = configs.set_index("TOPOLOGYSHIFTSETID")[["BRANCHLABEL", "CTGLABEL"]].to_dict("index")
    rows = []
    node_set_rate = {}

    for set_id, df in raws.items():
        branch_label = label_map[set_id]["BRANCHLABEL"]
        ctg_label = label_map[set_id]["CTGLABEL"]
        meta = metas[set_id]
        th = topo_hours[topo_hours["set_id"] == set_id]
        bad_th = th[th["BAD"]]

        n_rows = len(df)
        n_topo_variants = len(th)
        n_bad_variants = len(bad_th)
        tot_clock_hours = th[["simdate", "simhour"]].drop_duplicates().shape[0]
        bad_clock_hours_df = bad_th[["simdate", "simhour"]].drop_duplicates()
        bad_clock_hours = bad_clock_hours_df.shape[0]
        n_cpnodes = df["cpnodeid"].nunique()

        bad_psenshiftids = set(bad_th["psenshiftid"])
        bad_rows = df[df["psenshiftid"].isin(bad_psenshiftids)]
        bad_mismatch_rows = bad_rows[bad_rows["abs_diff"] > rank_tol]

        # bad hours list, clock-hour grain, with (xk variants) suffix
        variant_counts = bad_th.groupby(["simdate", "simhour"]).size().reset_index(name="n_variants")
        variant_counts = variant_counts.sort_values(["simdate", "simhour"]).head(5)
        bad_hours_str = "; ".join(
            f"{r.simdate} h{int(r.simhour)} (x{int(r.n_variants)} variants)" if r.n_variants > 1
            else f"{r.simdate} h{int(r.simhour)}"
            for r in variant_counts.itertuples()
        )

        # June-wide before/after REF_OFFSET node-mismatch counts
        n_nodes_before = june_wide_node_rate(df, "diff_before_offset", rank_tol)
        n_nodes_after = june_wide_node_rate(df, "diff_adj", rank_tol)

        row = {
            "TOPOLOGYSHIFTSETID": set_id, "BRANCHLABEL": branch_label, "CTGLABEL": ctg_label,
            "n_topology_variants": n_topo_variants,
            "n_bad_topology_variants": n_bad_variants,
            "tot_clock_hours": tot_clock_hours,
            "bad_clock_hours": bad_clock_hours,
            "share_bad_clock_hours": bad_clock_hours / tot_clock_hours if tot_clock_hours else np.nan,
            "median_nodes_mismatch_bad_hours": bad_th["n_mismatch_nodes"].median() if n_bad_variants else 0,
            "max_nodes_mismatch_bad_hours": bad_th["n_mismatch_nodes"].max() if n_bad_variants else 0,
            "max_nodes_mismatch_any_hour": th["n_mismatch_nodes"].max() if n_topo_variants else 0,
            "avg_abs_diff_mismatch_bad_hours": bad_mismatch_rows["abs_diff"].mean() if len(bad_mismatch_rows) else np.nan,
            "bad_hours_list": bad_hours_str,
            "n_topo_sign_pos": meta["n_topo_sign_pos"], "n_topo_sign_neg": meta["n_topo_sign_neg"],
            "sign_agreement_rate": meta["sign_agreement_rate"],
            "MIXED_SIGN": meta["mixed_sign"], "n_sign_unresolved": meta["n_sign_unresolved"],
            "REF_OFFSET": meta["ref_offset"], "bias_raw": meta["bias_raw"],
            "n_nodes_mismatch_junewide_before_offset": n_nodes_before,
            "n_nodes_mismatch_junewide_after_offset": n_nodes_after,
            "n_rows_total": n_rows, "n_cpnodes_total": n_cpnodes,
        }

        for tol in REF_TOLS:
            mism = df[df["abs_diff"] > tol]
            row[f"n_mismatch_rows_tol{tol}"] = len(mism)
            row[f"share_mismatch_tol{tol}"] = len(mism) / n_rows if n_rows else np.nan

        per_node = df.groupby("cpnodeid").agg(
            matched_hours=("psenshiftid", "size"),
            mism_hours=("abs_diff", lambda s: (s > rank_tol).sum()),
        )
        per_node["rate"] = per_node["mism_hours"] / per_node["matched_hours"]
        for cpnodeid, r in per_node.iterrows():
            node_set_rate[(set_id, cpnodeid)] = r["rate"]
        row["n_distinct_cpnodes_mismatching_junewide"] = int((per_node["rate"] >= node_rate).sum())

        rows.append(row)

    summary = pd.DataFrame(rows).sort_values(
        ["max_nodes_mismatch_bad_hours", "avg_abs_diff_mismatch_bad_hours"], ascending=[False, False]
    )
    return summary, node_set_rate


def build_bad_hours_list(topo_hours: pd.DataFrame) -> pd.DataFrame:
    bad = topo_hours[topo_hours["BAD"]].copy()
    return bad.sort_values("n_mismatch_nodes", ascending=False)


def build_bad_hour_mismatch_rows(raws: dict, configs: pd.DataFrame, topo_hours: pd.DataFrame, rank_tol: float) -> pd.DataFrame:
    label_map = configs.set_index("TOPOLOGYSHIFTSETID")[["BRANCHLABEL", "CTGLABEL"]].to_dict("index")
    frames = []
    for set_id, df in raws.items():
        bad_ids = set(topo_hours[(topo_hours["set_id"] == set_id) & topo_hours["BAD"]]["psenshiftid"])
        if not bad_ids:
            continue
        sub = df[df["psenshiftid"].isin(bad_ids) & (df["abs_diff"] > rank_tol)].copy()
        if sub.empty:
            continue
        sub["set_id"] = set_id
        sub["branchlabel"] = label_map[set_id]["BRANCHLABEL"]
        sub["ctglabel"] = label_map[set_id]["CTGLABEL"]
        frames.append(sub[["set_id", "branchlabel", "ctglabel", "psenshiftid", "simdate", "simhour",
                            "cpnodeid", "cpnode_name", "study_psen", "ref_psen", "dart_psen", "diff_adj", "abs_diff"]]
                      .rename(columns={"diff_adj": "diff"}))
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if not out.empty:
        out["simdate"] = pd.to_datetime(out["simdate"]).dt.strftime("%Y-%m-%d")
    return out


def build_node_day_matrix(raws: dict, bad_mismatch: pd.DataFrame) -> pd.DataFrame:
    """Node x (simdate, simhour) is now a bad-CLOCK-HOUR view: dedupe across
    variants sharing a clock-hour (a node counts once per constraint per
    clock-hour even if multiple bad variants exist that hour)."""
    evaluated_rows = []
    for set_id, raw in raws.items():
        sub = raw[["simdate", "cpnodeid", "cpnode_name"]].drop_duplicates().copy()
        sub["simdate"] = pd.to_datetime(sub["simdate"]).dt.strftime("%Y-%m-%d")
        sub["set_id"] = set_id
        evaluated_rows.append(sub)
    evaluated = pd.concat(evaluated_rows, ignore_index=True)
    eval_counts = (
        evaluated.groupby(["simdate", "cpnodeid", "cpnode_name"])["set_id"]
        .nunique().reset_index(name="n_constraints_evaluated_that_day")
    )

    if bad_mismatch.empty:
        return pd.DataFrame(columns=[
            "simdate", "cpnodeid", "cpnode_name", "n_constraints_mismatching",
            "n_constraints_evaluated_that_day", "share", "mean_abs_diff", "constraints"
        ])

    dedup = bad_mismatch.drop_duplicates(subset=["set_id", "simdate", "simhour", "cpnodeid"])
    grp = dedup.groupby(["simdate", "cpnodeid", "cpnode_name"])
    node_day = grp.agg(
        n_constraints_mismatching=("set_id", "nunique"),
        mean_abs_diff=("abs_diff", "mean"),
    ).reset_index()
    constraint_list = grp.apply(
        lambda d: ", ".join(sorted(set(d["branchlabel"] + "/" + d["ctglabel"])))
    ).reset_index(name="constraints")
    node_day = node_day.merge(constraint_list, on=["simdate", "cpnodeid", "cpnode_name"])
    node_day = node_day.merge(eval_counts, on=["simdate", "cpnodeid", "cpnode_name"], how="left")
    node_day["share"] = node_day["n_constraints_mismatching"] / node_day["n_constraints_evaluated_that_day"]
    return node_day.sort_values("n_constraints_mismatching", ascending=False)


def build_day_summary(raws: dict, bad_mismatch: pd.DataFrame, node_day: pd.DataFrame) -> pd.DataFrame:
    eval_by_day = {}
    for set_id, raw in raws.items():
        for d in pd.to_datetime(raw["simdate"]).dt.strftime("%Y-%m-%d").unique():
            eval_by_day.setdefault(d, set()).add(set_id)

    days = sorted(eval_by_day.keys())
    rows = []
    for d in days:
        n_eval = len(eval_by_day[d])
        day_mism = bad_mismatch[bad_mismatch["simdate"] == d] if not bad_mismatch.empty else pd.DataFrame()
        n_mism_constraints = day_mism["set_id"].nunique() if len(day_mism) else 0
        n_nodes_mism = day_mism["cpnodeid"].nunique() if len(day_mism) else 0
        n_bad_clock_hours_that_day = (
            day_mism.drop_duplicates(subset=["set_id", "simhour"]).shape[0] if len(day_mism) else 0
        )
        day_nd = node_day[node_day["simdate"] == d] if not node_day.empty else pd.DataFrame()
        n_nodes_2plus = (day_nd["n_constraints_mismatching"] >= 2).sum() if len(day_nd) else 0
        n_nodes_half = (day_nd["share"] >= 0.5).sum() if len(day_nd) else 0
        rows.append({
            "simdate": d, "n_constraints_evaluated": n_eval,
            "n_constraints_with_mismatch": n_mism_constraints,
            "n_bad_constraint_clock_hours": n_bad_clock_hours_that_day,
            "n_nodes_mismatching": n_nodes_mism,
            "n_nodes_mismatching_2plus_constraints": n_nodes_2plus,
            "n_nodes_mismatching_50pct_constraints": n_nodes_half,
        })
    return pd.DataFrame(rows).sort_values("simdate")


def build_node_summary(raws: dict, bad_mismatch: pd.DataFrame, node_day: pd.DataFrame) -> pd.DataFrame:
    if bad_mismatch.empty:
        return pd.DataFrame()

    evaluated_rows = []
    for set_id, raw in raws.items():
        sub = raw[["cpnodeid", "cpnode_name"]].drop_duplicates()
        sub["set_id"] = set_id
        evaluated_rows.append(sub)
    evaluated = pd.concat(evaluated_rows, ignore_index=True)
    n_eval = evaluated.groupby(["cpnodeid", "cpnode_name"])["set_id"].nunique().reset_index(name="n_constraints_evaluated")

    # membership: >=2 distinct bad clock-hours of a constraint
    dedup = bad_mismatch.drop_duplicates(subset=["set_id", "simdate", "simhour", "cpnodeid"])
    per_node_set_hours = dedup.groupby(["cpnodeid", "cpnode_name", "set_id"]).size().reset_index(name="n_bad_clock_hours")
    membership = per_node_set_hours[per_node_set_hours["n_bad_clock_hours"] >= MIN_BAD_CLOCK_HOURS_FOR_MEMBERSHIP]
    n_constraints_mism = (
        membership.groupby(["cpnodeid", "cpnode_name"])["set_id"].nunique().reset_index(name="n_constraints_mismatching")
    )
    n_days_mism = (
        node_day.groupby(["cpnodeid", "cpnode_name"])["simdate"].nunique().reset_index(name="n_days_mismatching")
        if not node_day.empty else pd.DataFrame(columns=["cpnodeid", "cpnode_name", "n_days_mismatching"])
    )
    mean_diff = dedup.groupby(["cpnodeid", "cpnode_name"])["abs_diff"].mean().reset_index(name="mean_abs_diff")

    node_sum = n_eval.merge(n_constraints_mism, on=["cpnodeid", "cpnode_name"], how="right")
    node_sum = node_sum.merge(n_days_mism, on=["cpnodeid", "cpnode_name"], how="left")
    node_sum["n_days_mismatching"] = node_sum["n_days_mismatching"].fillna(0).astype(int)
    node_sum = node_sum.merge(mean_diff, on=["cpnodeid", "cpnode_name"], how="left")
    node_sum["share_constraints_mismatching"] = node_sum["n_constraints_mismatching"] / node_sum["n_constraints_evaluated"]

    def label(r):
        if r["share_constraints_mismatching"] >= 0.5 and r["n_days_mismatching"] >= 3:
            return "SYSTEMIC_NODE"
        if r["n_constraints_mismatching"] == 1:
            return "CONSTRAINT_SPECIFIC"
        return "MIXED"

    node_sum["label"] = node_sum.apply(label, axis=1)
    return node_sum.sort_values("n_constraints_mismatching", ascending=False)


def build_topo_and_node_detail(raws: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    topo_frames, node_frames = [], []
    for set_id, df in raws.items():
        d = df.copy()
        d["set_id"] = set_id
        d["abs_diff_final"] = d["diff_adj"].abs()
        pt = d.groupby(["set_id", "psenshiftid", "simdate", "simhour"]).agg(
            n=("diff_adj", "size"), mae=("abs_diff_final", "mean"), max_abs=("abs_diff_final", "max"),
        ).reset_index()
        topo_frames.append(pt)
        pc = d.groupby(["set_id", "cpnodeid", "cpnode_name"]).agg(
            n=("diff_adj", "size"), mae=("abs_diff_final", "mean"), max_abs=("abs_diff_final", "max"),
        ).reset_index()
        node_frames.append(pc)
    per_topo = pd.concat(topo_frames, ignore_index=True) if topo_frames else pd.DataFrame()
    per_node = pd.concat(node_frames, ignore_index=True) if node_frames else pd.DataFrame()
    if not per_topo.empty:
        per_topo["simdate"] = pd.to_datetime(per_topo["simdate"]).dt.strftime("%Y-%m-%d")
    return per_topo, per_node


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--created-after", type=str, required=True)
    ap.add_argument("--date-from", type=str, required=True)
    ap.add_argument("--date-to", type=str, required=True)
    ap.add_argument("--rank-tol", type=float, default=0.01)
    ap.add_argument("--node-rate", type=float, default=0.10)
    ap.add_argument("--hour-bad-share", type=float, default=0.05)
    ap.add_argument("--sign-guard", type=float, default=0.02)
    ap.add_argument("--out-subdir", type=str, default="june")
    args = ap.parse_args()

    base_dir = Path(__file__).resolve().parent / "output" / "validation_shift_compare" / str(args.study)
    cache_dir = base_dir / "cache"
    out_dir = base_dir / args.out_subdir
    out_dir.mkdir(parents=True, exist_ok=True)

    configs = get_configs(args.study, args.created_after)
    configs = configs[configs["INTERFACENAME"].isna() & configs["CTGLABEL"].notna()]

    raws, metas = load_all_raw(cache_dir, configs, args.date_from, args.date_to, args.sign_guard)
    print(f"Loaded {len(raws)} cached sets with data")

    topo_hours = build_topology_hour_table(raws, configs, args.rank_tol, args.hour_bad_share)
    summary, node_set_rate = build_constraint_summary(raws, metas, configs, topo_hours, args.rank_tol, args.node_rate)
    bad_hours_list = build_bad_hours_list(topo_hours)
    bad_mismatch = build_bad_hour_mismatch_rows(raws, configs, topo_hours, args.rank_tol)
    node_day = build_node_day_matrix(raws, bad_mismatch)
    day_summary = build_day_summary(raws, bad_mismatch, node_day)
    node_summary = build_node_summary(raws, bad_mismatch, node_day)
    per_topo, per_node = build_topo_and_node_detail(raws)

    topo_hours.to_parquet(out_dir / "topology_hours.parquet")
    bad_hours_list.to_csv(out_dir / "bad_topology_hours.csv", index=False)
    bad_mismatch.to_parquet(out_dir / "mismatch_rows.parquet")
    summary.to_csv(out_dir / "mismatch_summary.csv", index=False)
    node_day.to_csv(out_dir / "node_day_matrix.csv", index=False)
    day_summary.to_csv(out_dir / "day_summary.csv", index=False)
    node_summary.to_csv(out_dir / "node_summary.csv", index=False)
    per_topo.to_parquet(out_dir / "per_topology_detail.parquet")
    per_node.to_parquet(out_dir / "per_node_detail.parquet")

    params = {"rank_tol": args.rank_tol, "node_rate": args.node_rate,
              "hour_bad_share": args.hour_bad_share, "sign_guard": args.sign_guard,
              "min_bad_clock_hours_for_membership": MIN_BAD_CLOCK_HOURS_FOR_MEMBERSHIP}
    (out_dir / "mismatch_params.json").write_text(json.dumps(params))

    n_total_rows = sum(len(r) for r in raws.values())
    print(f"Total joined rows: {n_total_rows}; total topology-variants: {len(topo_hours)}; bad variants: {int(topo_hours['BAD'].sum())}")
    n_mixed = sum(1 for m in metas.values() if m["mixed_sign"])
    n_ref_offset = sum(1 for m in metas.values() if m["ref_offset"])
    n_sign_unresolved = sum(m["n_sign_unresolved"] for m in metas.values())
    print(f"MIXED_SIGN configs: {n_mixed}/{len(metas)}; REF_OFFSET configs: {n_ref_offset}/{len(metas)}; SIGN_UNRESOLVED topologies: {n_sign_unresolved}")
    print(f"Wrote outputs to {out_dir}")
    print("\nTop 10 (Table 1, severity sort):")
    print(summary.head(10)[["BRANCHLABEL", "CTGLABEL", "bad_clock_hours", "tot_clock_hours",
                             "max_nodes_mismatch_bad_hours", "avg_abs_diff_mismatch_bad_hours"]].to_string(index=False))
    print("\nTop 15 bad topology-hours (Table 1b):")
    print(bad_hours_list.head(15)[["BRANCHLABEL", "CTGLABEL", "psenshiftid", "simdate", "simhour",
                                    "n_mismatch_nodes", "n_nodes", "avg_abs_diff_mismatch", "max_abs_diff"]].to_string(index=False))
    if not node_summary.empty:
        print("\nlabel distribution:\n", node_summary["label"].value_counts())
    else:
        print("\nnode_summary is empty")


if __name__ == "__main__":
    main()
