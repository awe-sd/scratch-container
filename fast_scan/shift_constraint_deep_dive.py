"""Deep-dive (shift_constraint_deep_dive.py) on one validation constraint (BRANCHLABEL/CTGLABEL) for a study.
Reuses compare_validation_shifts.py (config lookup, get_date_range, pull_joined_raw,
check_duplicates) and mismatch_analysis.py (resolve_signs_and_offset: per-topology
sign resolution + REF_OFFSET) rather than re-deriving the join/sign logic.
"""
import argparse
import sys

import pandas as pd

from pfa.sf import query

from compare_validation_shifts import get_date_range, pull_joined_raw, check_duplicates
from mismatch_analysis import resolve_signs_and_offset
from shift_common import REFERENCE_CPNODEID, cache_dir as study_cache_dir, dart_chain_sql, output_dir, window_label

HUBZONE_PREFIXES = ("LZ_", "HB_")


def pull_zone_raw(set_id: int, branch_label: str, ctg_label: str, start_date: str, end_date: str,
                   date_from: str | None, date_to: str | None) -> pd.DataFrame:
    """Same join as compare_validation_shifts.pull_joined_raw but WITHOUT the
    cv.deadbus=0 filter, restricted to LZ_/HB_ named cpnodes (see CLAUDE.md gotcha:
    load zones/hubs are stamped deadbus=4 in CPNODE_SHIFTS_VIEW, unlike real buses).
    Prefers deadbus=0 rows over deadbus=4 duplicates for the same topology/cpnode.
    """
    study_date_filter = ""
    if date_from:
        study_date_filter += f" AND orun.simdate >= '{date_from}'"
    if date_to:
        study_date_filter += f" AND orun.simdate <= '{date_to}'"
    sql = f"""
    WITH study_shifts AS (
        SELECT cv.PSENSHIFTID, cv.RUNID, cv.psens AS psens_raw, cv.deadbus, cv.branchlabel, cv.ctglabel,
            cv.cpnodeid, cv.name, orun.simdate, orun.simhour, orun.TOPOLOGYID, orun.RUNBEGINTIME
        FROM shift_factors.dbo.cpnode_shifts_view cv
        INNER JOIN AWOPF.DBO.OPFRUN orun ON cv.runid = orun.runid
        WHERE cv.PSENSHIFTID IN (
            SELECT PSENSHIFTID FROM AW.POPT.TOPOLOGYSHIFTSET WHERE TOPOLOGYSHIFTSETID={set_id}
        )
        AND cv.isomarketid = 6
        AND (cv.name LIKE 'LZ$_%' ESCAPE '$' OR cv.name LIKE 'HB$_%' ESCAPE '$')
        {study_date_filter}
        QUALIFY ROW_NUMBER() OVER (PARTITION BY cv.PSENSHIFTID, cv.cpnodeid ORDER BY cv.deadbus ASC, cv.RUNID) = 1
    ),
    DART_shifts AS (
        {dart_chain_sql(
            "psd.psenshiftid, ps.psen, ps.cpnodeid, b.branchName AS branchlabel, cdc.congContName AS ctglabel, "
            "TO_DATE(psd.extractionEnd) AS simdate, HOUR(psd.extractionEnd)+1 AS simhour",
            start_date, end_date, branch_label, ctg_label, psenshift=True, dedupe=True)}
    )
    SELECT ss.psenshiftid, ss.psens_raw, ss.deadbus, ss.cpnodeid, ss.name AS cpnode_name,
        ss.simdate, ss.simhour, ss.TOPOLOGYID, ss.RUNBEGINTIME,
        ds.psen AS dart_psen, ref.psen AS ref_psen
    FROM study_shifts ss
    INNER JOIN DART_shifts ds ON ss.branchlabel = ds.branchlabel
        AND ss.cpnodeid = ds.cpnodeid AND ss.ctglabel = ds.ctglabel
        AND ss.simdate = ds.simdate AND ss.simhour = ds.simhour
    INNER JOIN DART_shifts ref ON ss.simdate = ref.simdate AND ss.simhour = ref.simhour
        AND ref.psenshiftid = ds.psenshiftid AND ref.cpnodeid = {REFERENCE_CPNODEID}
    """
    df = query("AW", sql)
    df.columns = [c.lower() for c in df.columns]
    return df


def get_set(study_id: int, branch_label: str, ctg_label: str) -> pd.DataFrame:
    sql = f"""
    SELECT * FROM AW.POPT.TOPOLOGYSHIFTSETDEF
    WHERE STUDYID={study_id} AND BRANCHLABEL='{branch_label}' AND CTGLABEL='{ctg_label}'
    """
    return query("AW", sql)


def identify_id(check_id: int, study_id: int, branch_label: str, ctg_label: str) -> dict:
    result = {"id": check_id, "matches": []}
    df = query("AW", f"SELECT * FROM AW.POPT.TOPOLOGYSHIFTSET WHERE TOPOLOGYSHIFTSETID={check_id}")
    if not df.empty:
        result["matches"].append("TOPOLOGYSHIFTSETID")
    df = query("AW", f"SELECT * FROM AW.DBO.congDefConstraint WHERE congConstraintID={check_id}")
    if not df.empty:
        result["matches"].append("congConstraintID")
    df = query("AW", f"SELECT COUNT(*) n FROM AW.DBO.PSENSHIFT WHERE psenshiftid={check_id}")
    n = int(df.iloc[0, 0]) if not df.empty else 0
    if n > 0:
        result["matches"].append(f"PSENSHIFTID ({n} PSENSHIFT rows)")
        sd = query("AW", f"SELECT * FROM AW.dbo.psenShiftDef WHERE psenshiftid={check_id}")
        if not sd.empty:
            r = sd.iloc[0]
            result["psenshiftdef"] = {
                "isoMarketID": r.get("ISOMARKETID"), "studyID": r.get("STUDYID"),
                "extractionEnd": r.get("EXTRACTIONEND"), "branchLabel": r.get("BRANCHLABEL"),
                "ctgLabel": r.get("CTGLABEL"), "congConstraintID": r.get("CONGCONSTRAINTID"),
            }
    ts = query(
        "AW",
        f"""SELECT * FROM AW.POPT.TOPOLOGYSHIFTSET
        WHERE PSENSHIFTID={check_id} AND TOPOLOGYSHIFTSETID IN
        (SELECT TOPOLOGYSHIFTSETID FROM AW.POPT.TOPOLOGYSHIFTSETDEF
         WHERE STUDYID={study_id} AND BRANCHLABEL='{branch_label}' AND CTGLABEL='{ctg_label}')""",
    )
    result["member_of_this_set"] = not ts.empty
    return result


def dart_congconstraintids(branch_label: str, ctg_label: str, date_from: str, date_to: str) -> pd.DataFrame:
    sql = dart_chain_sql("DISTINCT cd.congConstraintID", date_from, date_to, branch_label, ctg_label)
    return query("AW", sql)


def dart_load_zones_hubs(branch_label: str, ctg_label: str, date_from: str, date_to: str) -> pd.DataFrame:
    sql = dart_chain_sql(
        "DISTINCT cp.name, cp.cpnodeid", date_from, date_to, branch_label, ctg_label, psenshift=True, cpnode=True,
        extra_where="AND (cp.name LIKE 'LZ$_%' ESCAPE '$' OR cp.name LIKE 'HB$_%' ESCAPE '$')")
    return query("AW", sql)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--branch", type=str, required=True)
    ap.add_argument("--ctg", type=str, required=True)
    ap.add_argument("--date-from", type=str, required=True)
    ap.add_argument("--date-to", type=str, required=True)
    ap.add_argument("--out-subdir", type=str, required=True)
    ap.add_argument("--check-id", type=int, default=None)
    ap.add_argument("--sign-guard", type=float, default=0.02)
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args()

    setdef = get_set(args.study, args.branch, args.ctg)
    if setdef.empty:
        print("NEEDS_CONTEXT: TOPOLOGYSHIFTSETDEF has no row for "
              f"STUDYID={args.study} BRANCHLABEL={args.branch} CTGLABEL={args.ctg}")
        sys.exit(1)
    set_row = setdef.iloc[0]
    set_id = int(set_row["TOPOLOGYSHIFTSETID"])
    print(f"TOPOLOGYSHIFTSETID={set_id} (DIRECTION={set_row['DIRECTION']}, CREATEDATE={set_row['CREATEDATE']})")

    id_info = None
    if args.check_id is not None:
        id_info = identify_id(args.check_id, args.study, args.branch, args.ctg)
        print(f"check-id {args.check_id}: matches={id_info['matches']}, "
              f"member_of_this_set={id_info['member_of_this_set']}")
        if id_info.get("psenshiftdef"):
            print(f"  psenShiftDef row: {id_info['psenshiftdef']}")

    out_dir = output_dir(args.study, args.out_subdir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = study_cache_dir(args.study)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{set_id}_{args.date_from}_{args.date_to}.parquet"

    start_date, end_date = get_date_range(set_id, args.date_from, args.date_to)
    if start_date is None:
        print("NEEDS_CONTEXT: no study data / date overlap for this topology set in the given window")
        sys.exit(1)

    if not args.no_cache and cache_path.exists():
        raw = pd.read_parquet(cache_path)
    else:
        raw = pull_joined_raw(set_id, args.branch, args.ctg, start_date, end_date, args.date_from, args.date_to)
        raw.to_parquet(cache_path)

    if raw.empty:
        print("NEEDS_CONTEXT: joined pull returned zero rows (NO_HOUR_OVERLAP)")
        sys.exit(1)

    df, meta = resolve_signs_and_offset(raw, args.sign_guard)

    per_topo_hour = (
        df.groupby(["psenshiftid", "simdate", "simhour"])
        .apply(lambda g: pd.Series({
            "n_nodes": g["cpnodeid"].nunique(),
            "mae": g["abs_diff"].mean(),
            "max_abs_diff": g["abs_diff"].max(),
            "max_node_cpnodeid": g.loc[g["abs_diff"].idxmax(), "cpnodeid"],
            "max_node_name": g.loc[g["abs_diff"].idxmax(), "cpnode_name"],
            "sign": g["sign"].iloc[0],
        }), include_groups=False)
        .reset_index()
    )

    overall_avg_abs = df["abs_diff"].mean()
    worst_row = df.loc[df["abs_diff"].idxmax()]
    overall_max = {
        "abs_diff": worst_row["abs_diff"], "cpnodeid": worst_row["cpnodeid"],
        "name": worst_row["cpnode_name"], "simdate": worst_row["simdate"], "simhour": worst_row["simhour"],
    }

    all_nodes = (
        df.groupby(["cpnodeid", "cpnode_name"])
        .agg(mae=("abs_diff", "mean"), bias=("diff_adj", "mean"), max_abs=("abs_diff", "max"),
             mean_study=("study_psen", "mean"), mean_dart=("dart_psen", "mean"), n=("abs_diff", "size"))
        .reset_index().sort_values("mae", ascending=False)
    )
    top10_nodes = all_nodes.head(10)

    # Zones/hubs: pull WITHOUT the deadbus=0 filter (LZ_/HB_ rows are stamped
    # deadbus=4 in CPNODE_SHIFTS_VIEW and get dropped by the standard join).
    # Sign is resolved per-topology from the full node fit (`per_topo`/`meta`
    # above); apply that same sign+offset to the zone rows rather than refitting.
    zone_raw = pull_zone_raw(set_id, args.branch, args.ctg, start_date, end_date, args.date_from, args.date_to)
    topo_sign = df.groupby("psenshiftid")["sign"].first()
    zone_df = pd.DataFrame()
    zone_hour = pd.DataFrame()
    zone_summary = pd.DataFrame()
    n_zone_no_sign = 0
    if not zone_raw.empty:
        zone_raw = zone_raw.merge(topo_sign.rename("sign"), on="psenshiftid", how="left")
        n_zone_no_sign = int(zone_raw["sign"].isna().sum())
        zone_df = zone_raw.dropna(subset=["sign"]).copy()
        zone_df["study_psen"] = zone_df["sign"] * zone_df["psens_raw"]
        zone_df["diff"] = zone_df["study_psen"] + zone_df["ref_psen"] - zone_df["dart_psen"]
        zone_df["diff_adj"] = zone_df["diff"] - meta["bias_raw"] if meta["ref_offset"] else zone_df["diff"]
        zone_df["abs_diff"] = zone_df["diff_adj"].abs()
        zone_df["study_plus_ref"] = zone_df["study_psen"] + zone_df["ref_psen"]
        zone_hour = zone_df[[
            "cpnode_name", "psenshiftid", "simdate", "simhour", "deadbus", "study_psen", "ref_psen",
            "study_plus_ref", "dart_psen", "diff_adj",
        ]].sort_values(["cpnode_name", "simdate", "simhour"])
        zone_summary = (
            zone_df.groupby("cpnode_name")
            .agg(mean_study_plus_ref=("study_plus_ref", "mean"), mean_dart=("dart_psen", "mean"),
                 mean_diff=("diff_adj", "mean"), max_abs_diff=("abs_diff", "max"), n=("abs_diff", "size"))
            .reset_index()
        )

    dart_zones = dart_load_zones_hubs(args.branch, args.ctg, args.date_from, args.date_to)
    study_zone_names = set(zone_df["cpnode_name"].unique()) if not zone_df.empty else set()
    dart_zone_names = set(dart_zones["name"].unique()) if not dart_zones.empty else set()
    both = sorted(study_zone_names & dart_zone_names)
    missing_from_study = sorted(dart_zone_names - study_zone_names)
    missing_from_dart = sorted(study_zone_names - dart_zone_names)

    # union summary: every LZ_/HB_ name seen on either side, one-side-only flagged
    if not zone_summary.empty:
        zone_summary["side"] = zone_summary["cpnode_name"].apply(
            lambda n: "BOTH" if n in both else ("STUDY_ONLY" if n in missing_from_dart else "DART_ONLY"))
    for name in missing_from_study:
        zone_summary = pd.concat([zone_summary, pd.DataFrame([{
            "cpnode_name": name, "mean_study_plus_ref": None, "mean_dart": None,
            "mean_diff": None, "max_abs_diff": None, "n": 0, "side": "DART_ONLY",
        }])], ignore_index=True)
    if not zone_summary.empty:
        zone_summary = zone_summary.sort_values("cpnode_name").reset_index(drop=True)

    if not study_zone_names and not dart_zone_names:
        zone_gap_note = "Load zones/hubs absent on BOTH sides (study CPNODE_SHIFTS_VIEW join and DART/PSENSHIFT) for this branch/ctg/window."
    else:
        zone_gap_note = (
            f"Load zones/hubs (deadbus filter dropped for LZ_/HB_ rows): study side has {len(study_zone_names)} "
            f"({sorted(study_zone_names)}), DART/PSENSHIFT has {len(dart_zone_names)} ({sorted(dart_zone_names)}). "
            f"Missing from study side ({len(missing_from_study)}): {missing_from_study}. "
            f"Missing from DART side ({len(missing_from_dart)}): {missing_from_dart}. "
            f"n_zone_rows_dropped_no_topology_sign={n_zone_no_sign}."
        )

    dup_n = check_duplicates(set_id, args.branch, args.ctg, args.date_from, args.date_to)
    congids = dart_congconstraintids(args.branch, args.ctg, args.date_from, args.date_to)
    congids.columns = [c.upper() for c in congids.columns]
    n_congids = len(congids)

    per_topo = df.groupby("psenshiftid").agg(sign=("sign", "first"), SIGN_UNRESOLVED=("SIGN_UNRESOLVED", "first")).reset_index()

    fname = f"deep_dive_{args.branch}_{args.ctg}"
    csv_path = out_dir / f"{fname}.csv"
    per_topo_hour.to_csv(csv_path, index=False)
    nodes_csv_path = out_dir / f"{fname}_nodes.csv"
    all_nodes.to_csv(nodes_csv_path, index=False)
    zones_csv_path = out_dir / f"{fname}_zones.csv"
    zone_summary.to_csv(zones_csv_path, index=False)

    def df_to_html(d: pd.DataFrame, title: str) -> str:
        return f"<h2>{title}</h2>" + d.to_html(index=False, border=1) if not d.empty else f"<h2>{title}</h2><p>(empty)</p>"

    month = window_label(args.date_from, args.date_to)
    wl = f"{month} " if month else ""
    html_parts = [
        f"<h1>Deep dive: study {args.study} {args.branch}/{args.ctg} (set {set_id})</h1>",
        f"<p>{wl}{args.date_from}..{args.date_to}. REF_OFFSET={meta['ref_offset']} (bias_raw={meta['bias_raw']:.4f}). "
        f"n_topo_sign_pos={meta['n_topo_sign_pos']} n_topo_sign_neg={meta['n_topo_sign_neg']} "
        f"n_sign_unresolved={meta['n_sign_unresolved']}. dup_rows_flagged={dup_n}. "
        f"distinct DART congConstraintIDs in {month or "window"}: {n_congids} {list(congids['CONGCONSTRAINTID']) if n_congids else ''}</p>",
    ]
    if id_info is not None:
        html_parts.append(f"<p>check-id {args.check_id}: matches={id_info['matches']}, "
                           f"member_of_this_set={id_info['member_of_this_set']}, "
                           f"psenshiftdef={id_info.get('psenshiftdef')}</p>")
    html_parts.append(df_to_html(per_topo_hour, "1. Per topology-hour"))
    html_parts.append(f"<p>Overall avg|diff|={overall_avg_abs:.4f}; overall max|diff|={overall_max}</p>")
    html_parts.append(df_to_html(top10_nodes, "2. Top 10 nodes by MAE"))
    html_parts.append(f"<p>{zone_gap_note}</p>")
    html_parts.append(df_to_html(zone_hour, "3a. Zones/hubs per topology-hour"))
    html_parts.append(df_to_html(zone_summary, "3b. Zones/hubs summary"))
    html_parts.append(df_to_html(per_topo, "4. Per-topology sign resolution"))

    html_path = out_dir / f"{fname}.html"
    html_path.write_text("\n".join(html_parts))

    print(f"Wrote {csv_path}")
    print(f"Wrote {html_path}")
    print(f"Overall avg|diff|={overall_avg_abs:.4f} max={overall_max}")
    print(top10_nodes.to_string(index=False))
    if not zone_summary.empty:
        print(zone_summary.to_string(index=False))
    print(zone_gap_note)
    print(f"REF_OFFSET={meta['ref_offset']} n_sign_unresolved={meta['n_sign_unresolved']} distinct_congConstraintIDs={n_congids}")


if __name__ == "__main__":
    main()
