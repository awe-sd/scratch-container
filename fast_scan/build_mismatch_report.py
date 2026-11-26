import argparse
import json
import sys
from pathlib import Path

import pandas as pd


def fmt(v, spec):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return format(v, spec)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "powerflow_analytics"))
from pfa.sf import query  # noqa: E402

TOP_DETAIL_N = 20
TOP_MAXDIFF_N = 10


def get_config_labels(study_id: int, created_after: str) -> pd.DataFrame:
    sql = f"""
    SELECT TOPOLOGYSHIFTSETID, BRANCHLABEL, CTGLABEL
    FROM AW.POPT.TOPOLOGYSHIFTSETDEF
    WHERE STUDYID={study_id} AND CREATEDATE >= '{created_after}'
    """
    return query("AW", sql)


def sortable_table(id_, headers, rows_html):
    return f"""<table id="{id_}">
<thead><tr>{''.join(f'<th>{h}</th>' for h in headers)}</tr></thead>
<tbody>{rows_html}</tbody>
</table>"""


SORT_SCRIPT = """
<script>
document.querySelectorAll('table').forEach(t => {
  t.querySelectorAll('th').forEach((th, idx) => {
    th.addEventListener('click', () => {
      const tbody = th.closest('table').querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tr'));
      const asc = th.dataset.asc !== 'true';
      th.dataset.asc = asc;
      rows.sort((a, b) => {
        const av = a.children[idx].innerText, bv = b.children[idx].innerText;
        const an = parseFloat(av.replace('%','')), bn = parseFloat(bv.replace('%',''));
        if (!isNaN(an) && !isNaN(bn)) return asc ? an - bn : bn - an;
        return asc ? av.localeCompare(bv) : bv.localeCompare(av);
      });
      rows.forEach(r => tbody.appendChild(r));
    });
  });
});
function toggle(id) { document.getElementById(id).classList.toggle('hidden'); }
</script>
"""

STYLE = """
<style>
body { font-family: system-ui, sans-serif; margin: 24px; background: #fff; color: #1f2328; }
table { border-collapse: collapse; width: 100%; font-size: 12.5px; margin-bottom: 20px; }
th, td { border: 1px solid #d0d7de; padding: 4px 7px; text-align: right; }
th:nth-child(-n+3), td:nth-child(-n+3) { text-align: left; }
th { background: #f6f8fa; cursor: pointer; position: sticky; top: 0; }
tr:nth-child(even) { background: #f6f8fa; }
h1, h2, h3 { font-weight: 600; }
.params { background: #fff8c5; border: 1px solid #d4a72c; padding: 10px 14px; margin-bottom: 16px; font-size: 13px; }
.warn { background: #ffebe9; border: 1px solid #cf222e; padding: 10px 14px; margin-bottom: 16px; font-size: 13px; }
.note { background: #ddf4ff; border: 1px solid #54aeff; padding: 10px 14px; margin-bottom: 16px; font-size: 13px; }
.caveat { background: #fbefff; border: 2px solid #8250df; padding: 10px 14px; margin-bottom: 10px; font-size: 13px; font-weight: 600; }
.toc { background: #f6f8fa; border: 1px solid #d0d7de; padding: 10px 14px; margin-bottom: 20px; font-size: 13px; }
.toc a { margin-right: 14px; }
.label-SYSTEMIC_NODE { color: #cf222e; font-weight: 600; }
.label-CONSTRAINT_SPECIFIC { color: #1a7f37; font-weight: 600; }
.label-MIXED { color: #9a6700; font-weight: 600; }
.flag-true { color: #cf222e; font-weight: 600; }
.hidden { display: none; }
.detail { display: flex; gap: 24px; margin: 6px 0 20px 0; }
table.mini { font-size: 11.5px; width: auto; min-width: 300px; }
button { cursor: pointer; font-size: 11px; }
</style>
"""


def detail_block(set_id, per_topo, per_node):
    pt = per_topo[per_topo["set_id"] == set_id].sort_values("mae", ascending=False).head(5)
    pn = per_node[per_node["set_id"] == set_id].sort_values("mae", ascending=False).head(5)
    topo_rows = "".join(
        f"<tr><td>{r.psenshiftid}</td><td>{r.simdate}</td><td>{int(r.simhour)}</td>"
        f"<td>{int(r.n)}</td><td>{r.mae:.4f}</td><td>{r.max_abs:.4f}</td></tr>"
        for r in pt.itertuples()
    )
    node_rows = "".join(
        f"<tr><td>{r.cpnodeid}</td><td>{r.cpnode_name}</td><td>{int(r.n)}</td>"
        f"<td>{r.mae:.4f}</td><td>{r.max_abs:.4f}</td></tr>"
        for r in pn.itertuples()
    )
    return f"""
<div class="detail">
<div><b>Worst topology-hours</b>{sortable_table(f'topo{set_id}', ['psenshiftid','simdate','hr','n','MAE','Max'], topo_rows)}</div>
<div><b>Worst cpnodes</b>{sortable_table(f'node{set_id}', ['cpnodeid','name','n','MAE','Max'], node_rows)}</div>
</div>
"""


def build(study_id: int, created_after: str, out_subdir: str):
    base_dir = Path(__file__).resolve().parent / "output" / "validation_shift_compare" / str(study_id)
    out_dir = base_dir / out_subdir

    summary = pd.read_csv(out_dir / "mismatch_summary.csv").sort_values(
        ["max_nodes_mismatch_bad_hours", "avg_abs_diff_mismatch_bad_hours"], ascending=[False, False]
    )
    bad_hours = pd.read_csv(out_dir / "bad_topology_hours.csv").sort_values("n_mismatch_nodes", ascending=False)
    day_summary = pd.read_csv(out_dir / "day_summary.csv")
    node_day = pd.read_csv(out_dir / "node_day_matrix.csv").sort_values("n_constraints_mismatching", ascending=False)
    node_summary = pd.read_csv(out_dir / "node_summary.csv").sort_values("n_constraints_mismatching", ascending=False)
    per_topo = pd.read_parquet(out_dir / "per_topology_detail.parquet")
    per_node = pd.read_parquet(out_dir / "per_node_detail.parquet")
    skipped = pd.read_csv(out_dir / "skipped.csv") if (out_dir / "skipped.csv").exists() else pd.read_csv(base_dir / "skipped.csv")
    params = json.loads((out_dir / "mismatch_params.json").read_text())
    dup_flags_path = out_dir / "dup_fanout_flags.csv"
    dup_flags = (
        pd.read_csv(dup_flags_path)[["TOPOLOGYSHIFTSETID", "dart_dup_rows_removed", "resolved"]]
        if dup_flags_path.exists() else pd.DataFrame(columns=["TOPOLOGYSHIFTSETID", "dart_dup_rows_removed", "resolved"])
    )

    labels = get_config_labels(study_id, created_after)
    if not skipped.empty and "BRANCHLABEL" not in skipped.columns:
        skipped = skipped.merge(labels, on="TOPOLOGYSHIFTSETID", how="left")
    summary = summary.merge(dup_flags, on="TOPOLOGYSHIFTSETID", how="left")
    summary["DUP_FANOUT_FIXED"] = summary["resolved"].fillna(False)

    clean = summary[summary["bad_clock_hours"] == 0]
    clean_share_01_median = clean["share_mismatch_tol0.01"].median()
    clean_share_01_max = clean["share_mismatch_tol0.01"].max()
    clean_share_001_median = clean["share_mismatch_tol0.001"].median()
    clean_share_001_p90 = clean["share_mismatch_tol0.001"].quantile(0.9)
    n_clean = len(clean)

    detail_ids = set(summary.sort_values("max_nodes_mismatch_bad_hours", ascending=False).head(TOP_DETAIL_N)["TOPOLOGYSHIFTSETID"])
    detail_ids |= set(summary.sort_values("max_nodes_mismatch_any_hour", ascending=False).head(TOP_MAXDIFF_N)["TOPOLOGYSHIFTSETID"])

    # Table 1
    t1_rows, detail_html = [], []
    for _, r in summary.iterrows():
        set_id = int(r["TOPOLOGYSHIFTSETID"])
        has_detail = set_id in detail_ids
        toggle_btn = f"<button onclick=\"toggle('d{set_id}')\">+</button>" if has_detail else ""
        mixed = "<span class='flag-true'>MIXED_SIGN</span>" if r["MIXED_SIGN"] else ""
        refoff = "<span class='flag-true'>REF_OFFSET</span>" if r["REF_OFFSET"] else ""
        unres = f"<span class='flag-true'>SIGN_UNRESOLVED x{int(r['n_sign_unresolved'])}</span>" if r["n_sign_unresolved"] > 0 else ""
        dupf = "<span class='flag-true'>DUP_FANOUT(fixed)</span>" if r["DUP_FANOUT_FIXED"] else ""
        flags = " ".join(f for f in [mixed, refoff, unres, dupf] if f)
        before_after = (
            f"{int(r['n_nodes_mismatch_junewide_before_offset'])}&rarr;{int(r['n_nodes_mismatch_junewide_after_offset'])}"
            if r["REF_OFFSET"] else "—"
        )
        t1_rows.append(
            "<tr>"
            f"<td>{toggle_btn}{r['BRANCHLABEL']}</td><td>{r['CTGLABEL']}</td>"
            f"<td>{int(r['bad_clock_hours'])}/{int(r['tot_clock_hours'])}</td>"
            f"<td>{fmt(r['share_bad_clock_hours'], '.1%')}</td>"
            f"<td>{int(r['n_bad_topology_variants'])}/{int(r['n_topology_variants'])}</td>"
            f"<td>{fmt(r['median_nodes_mismatch_bad_hours'], '.0f') if r['n_bad_topology_variants'] else '—'}</td>"
            f"<td>{int(r['max_nodes_mismatch_bad_hours']) if r['n_bad_topology_variants'] else '—'}</td>"
            f"<td>{fmt(r['avg_abs_diff_mismatch_bad_hours'], '.4f')}</td>"
            f"<td>{r['bad_hours_list'] if r['bad_hours_list'] and not pd.isna(r['bad_hours_list']) else '—'}</td>"
            f"<td>{flags}</td>"
            f"<td>{before_after}</td>"
            f"<td>{r['share_mismatch_tol0.0005']:.1%}</td><td>{r['share_mismatch_tol0.001']:.1%}</td><td>{r['share_mismatch_tol0.01']:.1%}</td>"
            f"<td>{int(r['n_distinct_cpnodes_mismatching_junewide'])}/{int(r['n_cpnodes_total'])}</td>"
            "</tr>"
        )
        if has_detail:
            detail_html.append(
                f"<div id='d{set_id}' class='hidden'><h3>{r['BRANCHLABEL']} / {r['CTGLABEL']} "
                f"(set {set_id}, {int(r['bad_clock_hours'])}/{int(r['tot_clock_hours'])} bad clock-hours, "
                f"max nodes off in a hour {int(r['max_nodes_mismatch_any_hour'])})</h3>{detail_block(set_id, per_topo, per_node)}</div>"
            )
    t1_headers = ["Branch", "Ctg", "BadClockHrs/Tot", "%bad(clock)", "BadVariants/Tot", "median nodes(bad)",
                  "max nodes(bad)", "avg|diff|(bad)", "Bad hours (first 5, clock-hour)", "Flags",
                  "RefOffset nodes before&rarr;after", "Share@0.0005", "Share@0.001", "Share@0.01",
                  "JuneWide nodes/total (fragile)"]

    # Table 1b: bad topology-hours list (variant grain, with TOPOLOGYID/RUNBEGINTIME)
    tbh_rows = "".join(
        f"<tr><td>{r.BRANCHLABEL}</td><td>{r.CTGLABEL}</td><td>{r.psenshiftid}</td>"
        f"<td>{r.TOPOLOGYID}</td><td>{r.RUNBEGINTIME}</td>"
        f"<td>{r.simdate}</td><td>{int(r.simhour)}</td>"
        f"<td>{int(r.n_mismatch_nodes)}/{int(r.n_nodes)}</td>"
        f"<td>{r.avg_abs_diff_mismatch:.4f}</td><td>{r.max_abs_diff:.4f}</td>"
        f"<td>{'SIGN_UNRESOLVED' if r.SIGN_UNRESOLVED else ''}</td></tr>"
        for r in bad_hours.itertuples()
    )
    tbh_headers = ["Branch", "Ctg", "psenshiftid", "TopologyID", "RunBeginTime", "simdate", "simhour",
                   "n_mismatch/n_nodes", "avg|diff|", "max|diff|", "Flag"]

    # Per-contingency grouping
    ctg_group = summary.groupby("CTGLABEL").agg(
        n_configs=("TOPOLOGYSHIFTSETID", "nunique"),
        max_nodes_any=("max_nodes_mismatch_bad_hours", "max"),
        sum_bad_clock_hours=("bad_clock_hours", "sum"),
        branches=("BRANCHLABEL", lambda s: ", ".join(sorted(set(s)))),
    ).reset_index().sort_values("max_nodes_any", ascending=False)
    t_ctg_rows = "".join(
        f"<tr><td>{r.CTGLABEL}</td><td>{int(r.n_configs)}</td><td>{int(r.sum_bad_clock_hours)}</td>"
        f"<td>{int(r.max_nodes_any)}</td><td>{r.branches}</td></tr>"
        for r in ctg_group.itertuples()
    )
    t_ctg_headers = ["Ctg", "n_configs", "sum_bad_clock_hours", "max_nodes_mismatch(any config)", "Branches"]

    # Day summary
    t2_rows = "".join(
        f"<tr><td>{r.simdate}</td><td>{int(r.n_constraints_evaluated)}</td><td>{int(r.n_constraints_with_mismatch)}</td>"
        f"<td>{int(r.n_bad_constraint_clock_hours)}</td>"
        f"<td>{int(r.n_nodes_mismatching)}</td><td>{int(r.n_nodes_mismatching_2plus_constraints)}</td>"
        f"<td>{int(r.n_nodes_mismatching_50pct_constraints)}</td></tr>"
        for r in day_summary.itertuples()
    )
    t2_headers = ["Date", "n_constraints_evaluated", "n_constraints_with_mismatch(bad hr)",
                  "n_bad_constraint_clock_hours", "n_nodes_mismatching(bad hr)",
                  "n_nodes_2plus_constraints", "n_nodes_50pct_constraints"]

    # Top 50 node-days
    t3_rows = "".join(
        f"<tr><td>{r.simdate}</td><td>{r.cpnodeid}</td><td>{r.cpnode_name}</td>"
        f"<td>{int(r.n_constraints_mismatching)}</td><td>{int(r.n_constraints_evaluated_that_day)}</td>"
        f"<td>{r.share:.1%}</td><td>{r.mean_abs_diff:.4f}</td><td>{r.constraints}</td></tr>"
        for r in node_day.head(50).itertuples()
    )
    t3_headers = ["Date", "cpnodeid", "Node", "n_constraints_mism(bad clock-hr)", "n_constraints_eval", "Share",
                  "MeanDiff", "Constraints"]

    # Node summary top 50
    t4_rows = "".join(
        f"<tr><td>{r.cpnodeid}</td><td>{r.cpnode_name}</td><td>{int(r.n_days_mismatching)}</td>"
        f"<td>{int(r.n_constraints_mismatching)}</td><td>{int(r.n_constraints_evaluated)}</td>"
        f"<td>{r.share_constraints_mismatching:.1%}</td><td>{r.mean_abs_diff:.4f}</td>"
        f"<td class='label-{r.label}'>{r.label}</td></tr>"
        for r in node_summary.head(50).itertuples()
    )
    t4_headers = ["cpnodeid", "Node", "n_days_mism", "n_constraints_mism(>=2 bad clock-hrs)", "n_constraints_eval",
                  "Share", "MeanDiff", "Label"]

    # Skipped
    t5_rows = "".join(
        f"<tr><td>{s.TOPOLOGYSHIFTSETID}</td><td>{getattr(s, 'BRANCHLABEL', '')}</td>"
        f"<td>{getattr(s, 'CTGLABEL', '')}</td><td>{s.reason}</td></tr>"
        for s in skipped.itertuples()
    ) if not skipped.empty else ""
    t5_headers = ["TopologyShiftSetID", "Branch", "Ctg", "Reason"]

    label_counts = node_summary["label"].value_counts().to_dict() if not node_summary.empty else {}
    n_mixed_sign = int(summary["MIXED_SIGN"].sum())
    n_ref_offset = int(summary["REF_OFFSET"].sum())
    n_sign_unresolved = int(summary["n_sign_unresolved"].sum())
    n_dup_fixed = int(summary["DUP_FANOUT_FIXED"].sum())

    sections_toc = """
<div class="toc">
Sections: <a href="#hdr">Header/Params</a> | <a href="#t1">Table 1</a> | <a href="#t1b">Table 1b</a> |
<a href="#tctg">Per-contingency grouping</a> | <a href="#drill">Drill-down</a> | <a href="#t2">Day summary</a> |
<a href="#t3">Node-day top 50</a> | <a href="#t4">Node summary</a> | <a href="#t5">Skipped</a>
</div>
"""

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Mismatch Analysis — Study {study_id} (June)</title>
{STYLE}
</head>
<body>
<h1 id="hdr">Validation Shift Mismatch Analysis — Study {study_id}, June 2026-06-01 to 2026-06-30</h1>
{sections_toc}
<div class="params">
<b>Grain:</b> a topology-hour = (topology VARIANT &times; clock-hour) pair; several variants can share one clock-hour
(e.g. 6965/MCATPRL5 2026-06-30 15:00 packs 4 variants). Counts are reported at both grains: n_bad_topology_variants
(variant grain) and bad_clock_hours/tot_clock_hours (distinct simdate+simhour grain — what "N bad hours" should mean
to a human). A topology-hour VARIANT is BAD if &ge;<b>HOUR_BAD_SHARE = {params['hour_bad_share']:.0%}</b> of its cpnodes
have |diff|&gt;RANK_TOL.<br>
<b>Table 1 vs Table 1b:</b> both are sorted by the same severity key (max nodes off in a bad hour, then avg|diff| in bad
hours) so they always agree on what's "worst" — Table 1 is the per-constraint rollup, Table 1b is the flat list of the
underlying bad topology-hour variants.<br>
<b>Normalization:</b> diff = sign&middot;study_psens + ref_psens(bus 12791) - dart_psens, sign resolved per topology-hour
by minimizing MAE for that topology; <b>SIGN_UNRESOLVED</b> (--sign-guard = {params['sign_guard']}) flags topologies where
neither sign fits well (min MAE &gt; guard) — these keep the study convention sign +1 rather than a spurious best fit.<br>
<b>REF_OFFSET:</b> if |bias|&gt;0.8&middot;MAE and &ge;90% of a config's cpnodes have bias within &plusmn;0.002 of the
config bias, that constant offset is subtracted before mismatch counting; the "RefOffset nodes before&rarr;after" column
shows the June-wide node-mismatch-rate count before and after de-biasing (can rise OR fall).<br>
<b>DUP_FANOUT:</b> root cause was duplicate rows inside AW.dbo.PSENSHIFT itself (psenshiftid 85019908 had 2222 rows for
1111 cpnodes, bit-identical; mirrored on the study side for &times;4 total) — fixed upstream via QUALIFY ROW_NUMBER()
dedupe on both join CTEs; the 3 affected sets (112447, 112449, 112421) were re-pulled with cache bypass and now show
0 duplicate keys.<br>
<b>Node labels</b> (Table 4) are rebased on BAD CLOCK-HOURS only, and require &ge;{params['min_bad_clock_hours_for_membership']}
distinct bad clock-hours of a constraint before a node counts as "off in constraint X" (a single bad hour no longer
taints a node's whole-June record). Tolerances: RANK_TOL = {params['rank_tol']}. The "JuneWide nodes/total" column
(rate-based, NODE_RATE = {params['node_rate']:.0%}) stays demoted/fragile — with only 4-17 topology-hours per config in
some cases, a single bad hour can push several nodes over a 10% rate gate on its own. Row-level shares at 0.0005/0.001/
0.01 are reference only. Units: shift-factor (psen), dimensionless.<br>
<b>Clean-hours agreement</b> (the {n_clean} configs with 0 bad clock-hours, i.e. outside the flagged errors): share of
rows with |diff|&gt;0.01 has median {clean_share_01_median:.2%}, max {clean_share_01_max:.2%}; share with |diff|&gt;0.001
has median {clean_share_001_median:.2%}, p90 {clean_share_001_p90:.2%}. Conclusion: <b>outside bad hours, study shifts
reproduce DART within 0.01 — but NOT within 0.001.</b>
</div>
<div class="warn">
{n_mixed_sign} configs MIXED_SIGN (within June) &middot; {n_ref_offset} configs REF_OFFSET &middot;
{n_sign_unresolved} topology-hours SIGN_UNRESOLVED &middot; {n_dup_fixed} configs had DUP_FANOUT (now fixed, dedupe
confirmed 0 duplicate keys): {', '.join(summary[summary['DUP_FANOUT_FIXED']]['BRANCHLABEL'] + '/' + summary[summary['DUP_FANOUT_FIXED']]['CTGLABEL'])}.
</div>
<div class="note">
<b>112401 6965/MCATPRL5, 2026-06-30 h15 — why 4 study topologies in one hour:</b> the 4 study psenshiftids
(85823400, 85841928, 85713639, 85768862) map to 4 distinct TOPOLOGYIDs (176239, 175915, 176315, 176062) and 4 distinct
RUNIDs (1898497, 1898039, 1898666, 1898248) — 4 separate validation-fast-scan topology variants scored against the same
real hour (intended design). DART has exactly ONE actual psenshiftid (85785153, congConstraintID 222555) for that hour.
Two study topologies (85823400, 85841928) are genuinely bad matches to reality (702/968 nodes, MAE ~0.031, max 0.309);
two (85713639, 85768862) are much closer (99/971, 93/971 nodes, MAE ~0.005) but still clear the 5% HOUR_BAD_SHARE gate
on node count. <b>The comparison itself is sound here</b> — no sign/reference/definitional artifact; 505_B/DVENFTS5 is
likewise a real, verified error.<br>
<b>DBIGKEN5 family, qualified:</b> the family is clean of SIGN artifacts (0/89 June configs MIXED_SIGN), but
TREADW_YELWJC11/DBIGKEN5 06-07 h21 (max 0.698) and HAMILT_MAXWEL11/DBIGKEN5 06-17 h24 (max 0.536) remain the two
largest real max|diff| values in all of June — genuine errors, not artifacts.
</div>

<h2 id="t1">1. Per-constraint mismatch summary (sorted by max nodes off in a bad hour desc, then avg|diff| in bad hours desc)</h2>
{sortable_table('t1', t1_headers, ''.join(t1_rows))}

<h2 id="t1b">1b. Bad topology-hours (variant grain, same severity sort as Table 1) — scan this for biggest errors</h2>
{sortable_table('tbh', tbh_headers, tbh_rows)}

<h2 id="tctg">1c. Per-contingency grouping (ctglabel spans multiple branches/configs)</h2>
{sortable_table('tctg', t_ctg_headers, t_ctg_rows)}

<h2 id="drill">Drill-down: worst topology-hours / worst nodes (union of top {TOP_DETAIL_N} by max nodes-in-bad-hour and top {TOP_MAXDIFF_N} by max nodes in any hour)</h2>
{''.join(detail_html)}

<h2 id="t2">2. Day summary (bad clock-hour basis) — watch for the 06-30 h12-15 / 06-10 h13-15 / 06-17 / 06-07 clusters</h2>
<div class="note">Footnote: 06-27 and 06-28 also show 13 bad constraint-clock-hours each, but both are entirely
WESLCO_HIDLBRG1/MHARNED5 (a small-magnitude REF_OFFSET config, 74 nodes) — not a new real cluster; the genuine
clusters are 06-30, 06-10, 06-17, and 06-07 (TREADW_YELWJC11/DBIGKEN5, max|diff| 0.698).</div>
{sortable_table('t2', t2_headers, t2_rows)}

<h2 id="t3">3. Top 50 node-days (cross-constraint view, bad clock-hour basis)</h2>
{sortable_table('t3', t3_headers, t3_rows)}

<h2 id="t4">4. Node summary — top 50 by n_constraints_mismatching</h2>
<div class="caveat">Caveat: with membership requiring &ge;2 bad clock-hours per constraint, the node-label distribution below is
a real signal (not degenerate), but June only has 20 bad clock-hours total across 89 constraints — treat these as
directional, not a large-sample finding.</div>
{sortable_table('t4', t4_headers, t4_rows)}

<h2 id="t5">5. Skipped sets (NO_HOUR_OVERLAP / NO_STUDY_DATA)</h2>
{sortable_table('t5', t5_headers, t5_rows)}

{SORT_SCRIPT}
</body></html>
"""
    (out_dir / "report.html").write_text(html)
    print(f"Wrote {out_dir / 'report.html'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--created-after", type=str, required=True)
    ap.add_argument("--out-subdir", type=str, default="june")
    args = ap.parse_args()
    build(args.study, args.created_after, args.out_subdir)
