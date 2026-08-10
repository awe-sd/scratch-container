"""HTML report: high-confidence CRR target constraints for one study.

Shortlist = outage-driven constraints whose driving ticket is Approved,
lambda below the solver cap, binding in >= MIN_BIND runs. Each gets the 5x16
$/MWh valuation (per 1.0 SF on the flowgate) and, where a fast-scan config
exists, the historical-injection stress check.

Usage: uv run powerflow_analytics/scripts/build_high_confidence_report.py --study 14411
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pfa import config
from pfa.analysis import fastscan, valuation
from pfa.cache import StudyCache

MIN_BIND = 10
LAM_CAP_FILTER = 3499  # exclude solver-cap (3500-flat) constraints


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--month", default="2026-09")
    args = ap.parse_args()

    out_dir = config.OUTPUT_ROOT / f"study_{args.study}"
    upside = pd.read_csv(out_dir / "post_sep15_outage_upside.csv")
    cache = StudyCache(args.study)
    runs = cache.load("opfrun")
    outcon = cache.load("outconstraint2")
    study_name = cache.load("opfstudy")["STUDYNAME"].iloc[0]
    year, month = (int(x) for x in args.month.split("-"))

    short = upside[
        (upside["DRIVER_TICKET_STATUS"].str.strip() == "Apprv")
        & (upside["MAX_SHADOW"] < LAM_CAP_FILTER)
        & (upside["N_RUNS_BINDING"] >= MIN_BIND)
    ].drop_duplicates("CONSTRAINT")

    rows = []
    for _, r in short.iterrows():
        window = (str(pd.to_datetime(r["DRIVER_TICKET_START"]).date()),
                  str(pd.to_datetime(r["DRIVER_TICKET_END"]).date()))
        stats = valuation.binding_stats(outcon, runs, r["CONSTRAINT"], window)
        vals = {c: valuation.dollars_per_mwh(stats, year, month, window, c)["dollars_per_mwh"]
                for c in ("p25", "p50", "p75")}
        fs_peak = None
        try:
            f, t, rest = r["CONSTRAINT"].split("-", 2)
            ckt, ctg = rest.split("@")
            cfgs = fastscan.find_configs(args.study, int(f), int(t), ctg)
            if not cfgs.empty:
                prof = fastscan.headroom_profile(int(cfgs["CONFIG_ID"].iloc[0]))
                fs_peak = float(prof["PCT_NEG"].max())
        except Exception:
            pass
        lam_p50_all = float(stats.lam["p50"].max()) if len(stats.lam) else 0.0
        flag = ""
        if lam_p50_all >= 500:
            flag = "λ at penalty tier — $/MWh is an upper bound, verify vs offers"
        rows.append({
            "Flag": flag,
            "Constraint": r["CONSTRAINT"],
            "From": r["FROMNAME"], "To": r["TONAME"],
            "Ticket": r["DRIVER_TICKET"], "Outage window": f"{window[0]} → {window[1]}",
            "P(bind) HE12": round(stats.p_bind.get(12, 0), 2),
            "P(bind) HE18": round(stats.p_bind.get(18, 0), 2),
            "λ P50": round(float(stats.lam["p50"].get(18, stats.lam["p50"].max() if len(stats.lam) else 0)), 1),
            "$/MWh P25": vals["p25"], "$/MWh P50": vals["p50"], "$/MWh P75": vals["p75"],
            "Rent post-9/15 ($)": int(r["RENT_POST"]),
            "Fast-scan max %neg": round(fs_peak, 1) if fs_peak is not None else None,
            "Outage group": str(r.get("DRIVER_OUTAGE_GROUP", ""))[:120],
        })

    df = pd.DataFrame(rows).sort_values("$/MWh P50", ascending=False)
    df = df[df["$/MWh P50"] > 0]  # outage window entirely outside the settlement month
    csv_path = out_dir / "high_confidence_constraints.csv"
    df.to_csv(csv_path, index=False)

    style = """
    body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:2rem;color:#1a1a2e;background:#fafafa}
    h1{font-size:1.4rem} h2{font-size:1.05rem;margin-top:2rem}
    .meta{color:#555;font-size:0.9rem;margin-bottom:1rem}
    table{border-collapse:collapse;font-size:0.82rem;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.12)}
    th,td{border:1px solid #ddd;padding:5px 8px;text-align:right;white-space:nowrap}
    th{background:#22304a;color:#fff;position:sticky;top:0}
    td:first-child,td:nth-child(2),td:nth-child(3),td:nth-child(4),td:nth-child(5),td:last-child{text-align:left}
    tr:nth-child(even){background:#f4f6fa}
    .hi{background:#e8f5e9!important;font-weight:600}
    .note{font-size:0.85rem;color:#444;max-width:70rem;line-height:1.45}
    td.grp{white-space:normal;max-width:26rem;font-size:0.75rem;color:#555}
    """
    hi_cut = df["$/MWh P50"].quantile(0.7)
    body_rows = []
    for _, r in df.iterrows():
        cls = ' class="hi"' if r["$/MWh P50"] >= hi_cut else ""
        tds = "".join(
            f'<td class="grp">{r[c]}</td>' if c == "Outage group" else f"<td>{'' if pd.isna(r[c]) else r[c]}</td>"
            for c in df.columns)
        body_rows.append(f"<tr{cls}>{tds}</tr>")
    header = "".join(f"<th>{c}</th>" for c in df.columns)

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>High-confidence CRR targets — study {args.study}</title><style>{style}</style></head><body>
<h1>High-confidence CRR targets — study {args.study} ({study_name}), {args.month}</h1>
<div class="meta">Shortlist: outage-driven, ticket <b>Approved</b>, λ &lt; solver cap (3500), binding in ≥ {MIN_BIND} runs.
Valuation = expected congestion rent per on-peak MWh (5x16, M-F, NERC holidays excluded) per <b>1.0 shift factor</b> on the flowgate,
binding stats conditioned on each ticket's own outage window. Multiply by a CRR path's SF for path $/MWh.
Generated {pd.Timestamp.now():%Y-%m-%d %H:%M}.</div>
<table><thead><tr>{header}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>
<h2>How to read this</h2>
<div class="note">
<p><b>λ / $/MWh percentiles</b> come from the study LP's shadow prices (OUTCONSTRAINT2.OPFCNLAMBDA) across binding runs —
cross-checked against marginal-unit DAM offer spreads ÷ ΔSF for the Parker–Hicks case (both land $30–55 in normal binding).
The tail regime (relief units at curve tops) runs $300–600, per the April 2026 HCKSW analog — treat P75 as conservative for stress.</p>
<p><b>Fast-scan max %neg</b> = worst hour-of-day share of historical injection patterns that would overload the branch on this topology
(negative headroom). Higher = the constraint binds on flows we have actually seen, not just modeled dispatch.</p>
<p><b>Risks:</b> outage reschedule/cancel (all tickets here are Approved — monitor revisions via ticket_history), RUC/mitigation capping λ,
and 3-hour study sampling (HE 3/12/18) mapped to 10h/6h on-peak blocks.</p>
<p>Green rows = top ~30% by P50 $/MWh. Rows sorted by P50.</p></div>
</body></html>"""
    html_path = out_dir / "high_confidence_constraints.html"
    html_path.write_text(html)
    print(df.drop(columns=["Outage group"]).to_string(index=False))
    print(f"\n-> {html_path}\n-> {csv_path}")


if __name__ == "__main__":
    main()
