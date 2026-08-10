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
from pfa.analysis import fastscan, marginal_units, offer_lambda, valuation
from pfa.cache import StudyCache

MIN_BIND = 10
LAM_CAP_FILTER = 3499  # exclude solver-cap (3500-flat) constraints


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--month", default="2026-09")
    args = ap.parse_args()

    out_dir = config.OUTPUT_ROOT / f"study_{args.study}"
    cache = StudyCache(args.study)
    runs = cache.load("opfrun")
    outcon = cache.load("outconstraint2")
    study_name = cache.load("opfstudy")["STUDYNAME"].iloc[0]
    year, month = (int(x) for x in args.month.split("-"))

    # ALL binding constraints (every run/scenario), not just the ticket-verified list
    # ranked_constraints.csv carries the DRIVER_* ticket columns from build_report --tickets
    ranked = pd.read_csv(out_dir / "ranked_constraints.csv", low_memory=False)
    short = ranked[
        (ranked["MAX_SHADOW"].fillna(0) < LAM_CAP_FILTER)
        & (ranked["N_RUNS_BINDING"] >= MIN_BIND)
        & (ranked["TOTAL_RENT"] > 0)
    ].drop_duplicates("CONSTRAINT")

    ctgviol = cache.load("outctgviol2")
    gen = cache.load("outgen2")
    branch = cache.load("outbranch2")
    genunit = cache.load("genunit")
    bus_names = marginal_units.bus_name_map(branch)

    rows = []
    for _, r in short.iterrows():
        has_ticket = pd.notna(r.get("DRIVER_TICKET")) and pd.notna(r.get("DRIVER_TICKET_START"))
        # binding stats across the WHOLE study (no window conditioning)
        stats = valuation.binding_stats(outcon, runs, r["CONSTRAINT"], None)
        lam_p50_all = float(stats.lam["p50"].max()) if len(stats.lam) else 0.0
        if lam_p50_all >= 500 or lam_p50_all == 0.0:
            continue  # penalty-tier (500/3500 flat) or no LP price at all
        limit = float(r.get("LIMIT_MVA") or 0)
        # 345 kV heuristic: study bus names end _5/5A at 345, _8 at 138, _9 at 69
        kv345 = limit >= 900 or str(r["FROMNAME"]).rstrip("AB").endswith("5")
        # on-peak = sampled HE12/HE18 pooled; off-peak = sampled HE3
        p12, p18, p3 = (stats.p_bind.get(h, 0.0) for h in (12, 18, 3))
        tickets_all = r.get("DRIVER_TICKETS_ALL")
        if pd.isna(tickets_all) if not isinstance(tickets_all, str) else not tickets_all:
            tickets_all = (f"{r.get('DRIVER_TICKET')} ({r.get('DRIVER_TICKET_STATUS')}"
                           f"/{r.get('DRIVER_TICKET_REASON', '?')})") if has_ticket else None
        rows.append({
            "Constraint": r["CONSTRAINT"],
            "From": r["FROMNAME"], "To": r["TONAME"],
            "kV": "345" if kv345 else "<345",
            "Limit MVA": int(limit),
            "Driver": r.get("DRIVER_CLASS", ""),
            "Tickets (status/reason)": tickets_all,
            "Outage window": (f"{pd.to_datetime(r['DRIVER_TICKET_START']):%m/%d} → "
                              f"{pd.to_datetime(r['DRIVER_TICKET_END']):%m/%d}") if has_ticket else None,
            "P(bind) on-peak": round((p12 + p18) / 2, 2),
            "P(bind) off-peak": round(p3, 2),
            "λ LP P50": round(lam_p50_all, 1),
            "Month rent ($)": int(r["TOTAL_RENT"]),
        })

    df = pd.DataFrame(rows)
    # 345 kV targets first, then by whole-month congestion rent
    df = df.sort_values(["kV", "Month rent ($)"], ascending=[True, False]).reset_index(drop=True)

    # top of the board: fast-scan potential headroom + independent offer-based lambda
    df["Potential headroom (MW med | %hrs stressed)"] = None
    df["λ offers (lo–hi)"] = None
    df["Redispatch pair"] = None
    for i in df.index[:35]:
        c = df.loc[i, "Constraint"]
        try:
            f, t, rest = c.split("-", 2)
            ctg = rest.split("@")[1]
            cfgs = fastscan.find_configs(args.study, int(f), int(t), ctg)
            if not cfgs.empty:
                prof = fastscan.headroom_profile(int(cfgs["CONFIG_ID"].iloc[0]))
                df.loc[i, "Potential headroom (MW med | %hrs stressed)"] = (
                    f"{prof['MED_HEADROOM'].median():.0f} | {prof['PCT_NEG'].max():.1f}%")
        except Exception:
            pass
        try:
            est = offer_lambda.estimate(args.study, ctgviol, gen, bus_names, genunit, c)
            if est:
                df.loc[i, "λ offers (lo–hi)"] = f"{est['lam_lo']}–{est['lam_hi']}"
                df.loc[i, "Redispatch pair"] = est["pair"]
        except Exception:
            pass
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
    body_rows = []
    for _, r in df.iterrows():
        cls = ' class="hi"' if r["kV"] == "345" else ""
        tds = "".join(f"<td>{'' if pd.isna(r[c]) else r[c]}</td>" for c in df.columns)
        body_rows.append(f"<tr{cls}>{tds}</tr>")
    header = "".join(f"<th>{c}</th>" for c in df.columns)

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>High-confidence CRR targets — study {args.study}</title><style>{style}</style></head><body>
<h1>High-confidence CRR targets — study {args.study} ({study_name}), {args.month}</h1>
<div class="meta">Universe: ALL binding constraints across every run/scenario, binding in ≥ {MIN_BIND} runs, LP-priced,
penalty-tier λ (flat 500/3500) excluded. <b>345 kV targets listed first (highlighted), then by whole-month
congestion rent ($)</b>. P(bind) is across the whole study: on-peak = sampled HE12/HE18 pooled, off-peak = HE3.
"λ offers" is the <b>independent</b> shadow-price estimate — DAM bid curves of the actual redispatch pair ÷ their
shift-factor spread (60-day disclosure lag; lo = cheapest pair, hi = deepest pair). "λ LP" is the study's own price,
shown for cross-check only. Potential headroom = fast-scan of historical injections on this topology
(median headroom MW | worst-hour % of stressed hours). Tickets: all tickets on the driving device with status
(Apprv/RatE) and outage reason. Generated {pd.Timestamp.now():%Y-%m-%d %H:%M}.</div>
<table><thead><tr>{header}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>
<h2>How to read this</h2>
<div class="note">
<p><b>λ offers (lo–hi)</b> is the independent estimate: the OPF's actual redispatch pair, each unit's DAM offer curve
(latest 60-day disclosure) and their shift-factor spread. lo ≈ first redispatch leg (often ~0 in mild conditions);
hi ≈ pairs exhausted — the binding-regime price. The stress regime beyond that (April 2026 HCKSW analog) ran $300–600.</p>
<p><b>Potential headroom</b>: fast-scan replays historical injections on this study's topology — median headroom MW and
the worst hour-of-day share of hours that would overload the branch. Low headroom / high % = binds on flows actually seen.</p>
<p><b>Risks:</b> ticket reschedule/cancel (RatE &gt; Apprv risk; reasons shown — breaker/maintenance reasons move more easily),
RUC/mitigation capping λ, 3-hour study sampling.</p>
<p>Highlighted rows = 345 kV. Sort: 345 kV first, then whole-month rent.</p></div>
</body></html>"""
    html_path = out_dir / "high_confidence_constraints.html"
    html_path.write_text(html)
    print(df.head(30).to_string(index=False))
    print(f"\n-> {html_path}\n-> {csv_path}")


if __name__ == "__main__":
    main()
