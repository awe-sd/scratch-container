import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "powerflow_analytics"))
from pfa.sf import query  # noqa: E402

PATTERN_COLOR = {
    "OK": "#1a7f37",
    "DIFFUSE": "#9a6700",
    "LOCALIZED_NODES": "#8250df",
    "LOCALIZED_TOPOLOGIES": "#0969da",
    "SYSTEMATIC": "#bf3989",
}

TOP_N_DETAIL = 20


def get_config_labels(study_id: int, created_after: str) -> pd.DataFrame:
    sql = f"""
    SELECT TOPOLOGYSHIFTSETID, BRANCHLABEL, CTGLABEL
    FROM AW.POPT.TOPOLOGYSHIFTSETDEF
    WHERE STUDYID={study_id} AND CREATEDATE >= '{created_after}'
    """
    return query("AW", sql)


def detail_block(set_id: int, per_topo: pd.DataFrame, per_cpnode: pd.DataFrame) -> str:
    pt = per_topo[per_topo["set_id"] == set_id].sort_values("mae", ascending=False).head(5)
    pc = per_cpnode[per_cpnode["set_id"] == set_id].sort_values("mae", ascending=False).head(5)

    topo_rows = "".join(
        f"<tr><td>{r['psenshiftid']}</td><td>{pd.Timestamp(r['simdate']).date()}</td>"
        f"<td>{int(r['simhour'])}</td><td>{int(r['n'])}</td><td>{r['mae']:.4f}</td><td>{r['max_abs']:.4f}</td></tr>"
        for _, r in pt.iterrows()
    )
    cp_rows = "".join(
        f"<tr><td>{r['cpnodeid']}</td><td>{r['cpnode_name']}</td><td>{int(r['n'])}</td>"
        f"<td>{r['mae']:.4f}</td><td>{r['max_abs']:.4f}</td></tr>"
        for _, r in pc.iterrows()
    )
    return f"""
<div class="detail">
<div><b>Worst topologies</b>
<table class="mini"><thead><tr><th>psenshiftid</th><th>simdate</th><th>hr</th><th>n</th><th>MAE</th><th>Max</th></tr></thead>
<tbody>{topo_rows}</tbody></table></div>
<div><b>Worst cpnodes</b>
<table class="mini"><thead><tr><th>cpnodeid</th><th>name</th><th>n</th><th>MAE</th><th>Max</th></tr></thead>
<tbody>{cp_rows}</tbody></table></div>
</div>
"""


def build(study_id: int, created_after: str, out_subdir: str | None = None):
    base_dir = Path(__file__).resolve().parent / "output" / "validation_shift_compare" / str(study_id)
    out_dir = base_dir / out_subdir if out_subdir else base_dir

    summary = pd.read_csv(out_dir / "summary.csv")
    skipped = pd.read_csv(out_dir / "skipped.csv")
    per_topo = pd.read_parquet(out_dir / "per_topology.parquet")
    per_cpnode = pd.read_parquet(out_dir / "per_cpnode.parquet")
    summary = summary.sort_values("mae", ascending=False)

    labels = get_config_labels(study_id, created_after)
    skipped = skipped.merge(labels, on="TOPOLOGYSHIFTSETID", how="left")

    date_min = pd.to_datetime(summary["simdate_min"]).min()
    date_max = pd.to_datetime(summary["simdate_max"]).max()

    rows_html = []
    detail_html = []
    top_detail_ids = set(summary.head(TOP_N_DETAIL)["TOPOLOGYSHIFTSETID"])
    for _, r in summary.iterrows():
        color = PATTERN_COLOR.get(r["error_pattern"], "#57606a")
        set_id = int(r["TOPOLOGYSHIFTSETID"])
        has_detail = set_id in top_detail_ids
        toggle = f"<button onclick=\"document.getElementById('d{set_id}').classList.toggle('hidden')\">+</button>" if has_detail else ""
        rows_html.append(
            "<tr>"
            f"<td>{toggle}{r['BRANCHLABEL']}</td><td>{r['CTGLABEL']}</td><td>{int(r['DIRECTION'])}</td>"
            f"<td>{int(r['best_sign'])}</td><td>{r['other_sign_mae']:.4f}</td>"
            f"<td>{int(r['n_topologies_matched'])}</td><td>{int(r['n_topologies_total'])}</td>"
            f"<td>{r['coverage']:.1%}</td><td>{int(r['n_cpnodes'])}</td>"
            f"<td>{pd.Timestamp(r['simdate_min']).date()}</td><td>{pd.Timestamp(r['simdate_max']).date()}</td>"
            f"<td>{r['mae']:.4f}</td><td>{r['bias']:.4f}</td><td>{r['p95_abs']:.4f}</td>"
            f"<td>{r['max_abs']:.4f}</td><td>{r['share_gt_02']:.2%}</td>"
            f"<td>{r['corr']:.3f}</td>"
            f"<td><span style='color:{color};font-weight:600'>{r['error_pattern']}</span></td>"
            "</tr>"
        )
        if has_detail:
            detail_html.append(
                f"<div id='d{set_id}' class='hidden'><h3>{r['BRANCHLABEL']} / {r['CTGLABEL']} "
                f"(set {set_id}, MAE {r['mae']:.4f}, max {r['max_abs']:.4f})</h3>"
                f"{detail_block(set_id, per_topo, per_cpnode)}</div>"
            )

    skip_rows = "".join(
        f"<tr><td>{s['TOPOLOGYSHIFTSETID']}</td><td>{s.get('BRANCHLABEL', '')}</td>"
        f"<td>{s.get('CTGLABEL', '')}</td><td>{s['reason']}</td></tr>"
        for _, s in skipped.iterrows()
    )

    counts = summary["error_pattern"].value_counts()
    counts_html = "".join(f"<li>{k}: {v}</li>" for k, v in counts.items())

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Validation Shift Compare — Study {study_id}</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 24px; background: #fff; color: #1f2328; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
th, td {{ border: 1px solid #d0d7de; padding: 4px 8px; text-align: right; }}
th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) {{ text-align: left; }}
th {{ background: #f6f8fa; cursor: pointer; position: sticky; top: 0; }}
tr:nth-child(even) {{ background: #f6f8fa; }}
h1, h2, h3 {{ font-weight: 600; }}
.summary-box {{ display: flex; gap: 24px; margin-bottom: 16px; }}
ul {{ margin: 0; }}
.hidden {{ display: none; }}
.detail {{ display: flex; gap: 24px; margin: 8px 0 16px 0; }}
table.mini {{ font-size: 12px; width: auto; min-width: 320px; }}
button {{ cursor: pointer; }}
</style>
</head>
<body>
<h1>Validation Shift Compare — Study {study_id}</h1>
<p>Date window (matched rows, min-max across all configs): {date_min.date()} to {date_max.date()}</p>
<div class="summary-box">
<div><h2>Pattern counts</h2><ul>{counts_html}</ul></div>
<div><h2>Skipped ({len(skipped)})</h2></div>
</div>
<h2>Per-config summary (sorted by MAE desc, best sign)</h2>
<table id="summary-table">
<thead><tr>
<th>Branch</th><th>Ctg</th><th>Dir</th><th>Sign</th><th>OtherSignMAE</th>
<th>n_matched</th><th>n_total</th><th>Coverage</th><th>n_cpnode</th>
<th>simdate min</th><th>simdate max</th>
<th>MAE</th><th>Bias</th><th>P95</th><th>Max</th>
<th>Share&gt;0.02</th><th>Corr</th><th>Pattern</th>
</tr></thead>
<tbody>{''.join(rows_html)}</tbody>
</table>
<h2>Top {TOP_N_DETAIL} configs — worst topologies / worst cpnodes</h2>
{''.join(detail_html)}
<h2>NO_DART_MATCH / skipped configs</h2>
<table><thead><tr><th>TopologyShiftSetID</th><th>Branch</th><th>Ctg</th><th>Reason</th></tr></thead>
<tbody>{skip_rows}</tbody></table>
<script>
document.querySelectorAll('#summary-table th').forEach((th, idx) => {{
  th.addEventListener('click', () => {{
    const tbody = th.closest('table').querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const asc = th.dataset.asc !== 'true';
    th.dataset.asc = asc;
    rows.sort((a, b) => {{
      const av = a.children[idx].innerText, bv = b.children[idx].innerText;
      const an = parseFloat(av.replace('%','')), bn = parseFloat(bv.replace('%',''));
      if (!isNaN(an) && !isNaN(bn)) return asc ? an - bn : bn - an;
      return asc ? av.localeCompare(bv) : bv.localeCompare(av);
    }});
    rows.forEach(r => tbody.appendChild(r));
  }});
}});
</script>
</body></html>
"""
    (out_dir / "report.html").write_text(html)
    print(f"Wrote {out_dir / 'report.html'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--created-after", type=str, required=True)
    ap.add_argument("--out-subdir", type=str, default=None)
    args = ap.parse_args()
    build(args.study, args.created_after, args.out_subdir)
