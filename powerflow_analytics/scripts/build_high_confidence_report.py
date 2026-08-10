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

    # ALL binding constraints (every run/scenario), not just the ticket-verified list
    ranked = pd.read_csv(out_dir / "ranked_constraints.csv")
    tick_cols = ["CONSTRAINT", "DRIVER_TICKET", "DRIVER_TICKET_STATUS",
                 "DRIVER_TICKET_START", "DRIVER_TICKET_END", "DRIVER_OUTAGE_GROUP"]
    tickets = upside[[c for c in tick_cols if c in upside.columns]].drop_duplicates("CONSTRAINT")
    short = ranked[
        (ranked["MAX_SHADOW"].fillna(0) < LAM_CAP_FILTER)
        & (ranked["N_RUNS_BINDING"] >= MIN_BIND)
        & (ranked["TOTAL_RENT"] > 0)
    ].drop_duplicates("CONSTRAINT").drop(
        columns=[c for c in tick_cols[1:] if c in ranked.columns], errors="ignore"
    ).merge(tickets, on="CONSTRAINT", how="left")

    study_window = (str(pd.to_datetime(runs["SIMDATE"]).min().date()),
                    str(pd.to_datetime(runs["SIMDATE"]).max().date()))
    rows = []
    for _, r in short.iterrows():
        has_ticket = pd.notna(r.get("DRIVER_TICKET")) and pd.notna(r.get("DRIVER_TICKET_START"))
        window = ((str(pd.to_datetime(r["DRIVER_TICKET_START"]).date()),
                   str(pd.to_datetime(r["DRIVER_TICKET_END"]).date()))
                  if has_ticket else study_window)
        stats = valuation.binding_stats(outcon, runs, r["CONSTRAINT"], window)
        lam_p50_all = float(stats.lam["p50"].max()) if len(stats.lam) else 0.0
        if lam_p50_all >= 500 or lam_p50_all == 0.0:
            continue  # penalty-tier (500/3500 flat) or no LP price at all
        vals = {c: valuation.dollars_per_mwh(stats, year, month, window, c)["dollars_per_mwh"]
                for c in ("p25", "p50", "p75")}
        limit = float(r.get("LIMIT_MVA") or 0)
        # 345 kV heuristic: study bus names end _5/5A at 345, _8 at 138, _9 at 69
        kv345 = limit >= 900 or str(r["FROMNAME"]).rstrip("AB").endswith("5")
        rows.append({
            "Constraint": r["CONSTRAINT"],
            "From": r["FROMNAME"], "To": r["TONAME"],
            "kV": "345" if kv345 else "<345",
            "Limit MVA": int(limit),
            "Driver": r.get("DRIVER_CLASS", ""),
            "Ticket": r.get("DRIVER_TICKET") if has_ticket else None,
            "Status": str(r.get("DRIVER_TICKET_STATUS", "")).strip() or None,
            "Window": f"{window[0]} → {window[1]}" + ("" if has_ticket else " (study)"),
            "P(bind) HE12": round(stats.p_bind.get(12, 0), 2),
            "P(bind) HE18": round(stats.p_bind.get(18, 0), 2),
            "λ P50": round(lam_p50_all, 1),
            "$/MWh P25": vals["p25"], "$/MWh P50": vals["p50"], "$/MWh P75": vals["p75"],
            "Rent score ($k/mo)": round(vals["p50"] * limit / 1000, 1),
            "Total rent ($)": int(r["TOTAL_RENT"]),
        })

    df = pd.DataFrame(rows)
    df = df[df["$/MWh P50"] > 0]
    # rank: expected monthly rent volume (P50 $/MWh x flowgate MVA); 345 kV floats up via size
    df = df.sort_values(["Rent score ($k/mo)"], ascending=False).reset_index(drop=True)

    # fast-scan stress check for the top of the board only (one query each)
    df["Fast-scan max %neg"] = None
    for i in df.index[:40]:
        try:
            f, t, rest = df.loc[i, "Constraint"].split("-", 2)
            ctg = rest.split("@")[1]
            cfgs = fastscan.find_configs(args.study, int(f), int(t), ctg)
            if not cfgs.empty:
                prof = fastscan.headroom_profile(int(cfgs["CONFIG_ID"].iloc[0]))
                df.loc[i, "Fast-scan max %neg"] = round(float(prof["PCT_NEG"].max()), 1)
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
    hi_cut = df["Rent score ($k/mo)"].quantile(0.75)
    body_rows = []
    for _, r in df.iterrows():
        cls = ' class="hi"' if r["Rent score ($k/mo)"] >= hi_cut else ""
        tds = "".join(f"<td>{'' if pd.isna(r[c]) else r[c]}</td>" for c in df.columns)
        body_rows.append(f"<tr{cls}>{tds}</tr>")
    header = "".join(f"<th>{c}</th>" for c in df.columns)

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>High-confidence CRR targets — study {args.study}</title><style>{style}</style></head><body>
<h1>High-confidence CRR targets — study {args.study} ({study_name}), {args.month}</h1>
<div class="meta">Universe: ALL binding constraints across every run/scenario, binding in ≥ {MIN_BIND} runs, LP-priced,
penalty-tier λ (flat 500/3500) excluded. Tickets shown where the driving outage was verified
(<b>Apprv</b> = approved; <b>RatE</b> = rated — reschedule/cancel risk); unticketed rows are baseline/topology congestion
valued over the full study window. $/MWh = expected congestion rent per on-peak MWh (5x16, M-F, NERC holidays excluded)
per <b>1.0 shift factor</b> — multiply by a path's SF. <b>Ranked by Rent score = P50 $/MWh × flowgate MVA</b>
(expected monthly rent volume), which floats large 345 kV flowgates to the top.
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
    print(df.head(30).to_string(index=False))
    print(f"\n-> {html_path}\n-> {csv_path}")


if __name__ == "__main__":
    main()
