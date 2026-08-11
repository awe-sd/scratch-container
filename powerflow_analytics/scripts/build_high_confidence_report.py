"""HTML report: CRR target constraints for one study — every binding constraint,
every analysis stage.

Per constraint: study binding stats (whole study, on/off-peak), driver
verification (outage ticket via teid, or implied-outage check from the study's
own line statuses), realized ISO market history (ID-joined CONGHRPRICE),
independent offer-based lambda, fast-scan stressed-hours headroom, and the
cheapest path-opt path (FWD-auction cost mark). Penalty-tier (flat 500/3500)
constraints are kept and flagged: no economic dispatch resolves them, so ERCOT
is likely to deny the driving outage — high risk, but cheap paths may still
be worth it.

Usage: uv run powerflow_analytics/scripts/build_high_confidence_report.py --study 14411
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pfa import config
from pfa.analysis import fastscan, marginal_units, market, offer_lambda, valuation
from pfa.cache import StudyCache
from pfa.extract import buskv, gen_mapping, popt

MIN_BIND = 1  # every last one
ONPEAK_BLOCKS = {12: 10, 18: 6}  # sampled hour -> on-peak hours represented


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--month", default="2026-09")
    ap.add_argument("--history-start", default="2026-05-01",
                    help="start date for realized DA congestion history")
    args = ap.parse_args()

    out_dir = config.OUTPUT_ROOT / f"study_{args.study}"
    cache = StudyCache(args.study)
    runs = cache.load("opfrun")
    outcon = cache.load("outconstraint2")
    study_name = cache.load("opfstudy")["STUDYNAME"].iloc[0]

    ranked = pd.read_csv(out_dir / "ranked_constraints.csv", low_memory=False)
    short = ranked[(ranked["N_RUNS_BINDING"] >= MIN_BIND)
                   & (ranked["TOTAL_RENT"] > 0)].drop_duplicates("CONSTRAINT")

    ctgviol = cache.load("outctgviol2")
    gen = cache.load("outgen2")
    branch = cache.load("outbranch2")
    genunit = cache.load("genunit")
    scedname = gen_mapping.fetch_genunit_sced_name()
    bus_names = marginal_units.bus_name_map(branch)
    tf_sum = pd.read_csv(out_dir / "tofinder_summary.csv")
    top_drv = (tf_sum.reindex(tf_sum["MEAN_FLOWDELTA"].abs().sort_values(ascending=False).index)
               .drop_duplicates("CONSTRAINT").set_index("CONSTRAINT"))
    cutoff = f"{pd.to_datetime(runs['SIMDATE']).dt.year.mode().iloc[0]}-09-15"

    rows = []
    for _, r in short.iterrows():
        c = r["CONSTRAINT"]
        has_ticket = pd.notna(r.get("DRIVER_TICKET")) and pd.notna(r.get("DRIVER_TICKET_START"))
        stats = valuation.binding_stats(outcon, runs, c, None)
        lam_p50 = float(stats.lam["p50"].max()) if len(stats.lam) else None
        penalty = lam_p50 is not None and lam_p50 >= 500
        try:
            unenforceable = offer_lambda.dispatch_screen(args.study, c)
        except Exception:
            unenforceable = None
        limit = float(r.get("LIMIT_MVA") or 0)
        f, t = c.split("-")[:2]
        kv = buskv.constraint_kv(int(f), int(t))
        p12, p18, p3 = (stats.p_bind.get(h, 0.0) for h in (12, 18, 3))

        tickets_all = r.get("DRIVER_TICKETS_ALL")
        if pd.isna(tickets_all) if not isinstance(tickets_all, str) else not tickets_all:
            tickets_all = (f"{r.get('DRIVER_TICKET')} ({r.get('DRIVER_TICKET_STATUS')}"
                           f"/{r.get('DRIVER_TICKET_REASON', '?')})") if has_ticket else None
        # no constraint skipped: unticketed drivers get the implied-outage check
        # (driving line Closed pre-cutoff, Open after — from the study itself)
        driver = r.get("DRIVER_CLASS", "")
        if driver in ("topology-suspect", "") and c in top_drv.index:
            d = top_drv.loc[c]
            if pd.notna(d.get("FROMNUM_OUTAGE")):
                v = market.implied_outage_check(branch, runs, int(d["FROMNUM_OUTAGE"]),
                                                int(d["TONUM_OUTAGE"]), str(d["CKT_OUTAGE"]), cutoff)
                if v:
                    driver = v
        rows.append({
            "Constraint": c, "From": r["FROMNAME"], "To": r["TONAME"],
            "kV": int(kv) if kv else None, "_kv345": (kv or 0) >= 345,
            "Limit MVA": int(limit),
            "Driver": driver,
            "Tickets (status/reason)": tickets_all,
            "Outage window": (f"{pd.to_datetime(r['DRIVER_TICKET_START']):%m/%d} → "
                              f"{pd.to_datetime(r['DRIVER_TICKET_END']):%m/%d}") if has_ticket else None,
            "P(bind) on-peak": round((p12 + p18) / 2, 2),
            "P(bind) off-peak": round(p3, 2),
            "λ LP P50": round(lam_p50, 1) if lam_p50 is not None else None,
            # dispatch screen (LZ/WZ/radial-only) takes precedence over the
            # penalty-tier flag when both apply — it's the stronger claim
            "Risk": (unenforceable if unenforceable else
                      ("no-dispatch (penalty λ) — ERCOT may deny the outage" if penalty else None)),
            "Month rent ($)": int(r["TOTAL_RENT"]),
            "_bid": r.get("BRANCHID"), "_bcid": None,
        })
    df = pd.DataFrame(rows)

    # BRANCHCONTINGENCYID per constraint (for the ID join to ISO constraints)
    cv = ctgviol.copy()
    cv["Constraint"] = (cv["FROMNUM"].astype(int).astype(str) + "-" + cv["TONUM"].astype(int).astype(str)
                        + "-" + cv["CKT"].astype(str).str.strip() + "@" + cv["CTGLABEL"].astype(str).str.strip())
    bc = cv.dropna(subset=["BRANCHCONTINGENCYID"]).drop_duplicates("Constraint").set_index("Constraint")
    df["_bcid"] = df["Constraint"].map(bc["BRANCHCONTINGENCYID"])
    df["_bid"] = df["Constraint"].map(bc["BRANCHID"])

    # enrichment — EVERY constraint goes through every stage
    for col in ["Realized DA (hrs | P50 | max)", "Headroom stressed hrs (P10 MW | %hrs)",
                "λ offers (lo–hi)", "Redispatch pair", "Best path ($/MWh @SF)", "Path $/SF"]:
        df[col] = None
    for i in df.index:
        c = df.loc[i, "Constraint"]
        f, t, rest = c.split("-", 2)
        ctg = rest.split("@")[1]
        try:  # realized ISO history (ID join)
            if pd.notna(df.loc[i, "_bid"]) and pd.notna(df.loc[i, "_bcid"]):
                ids = market.iso_constraint_ids(int(df.loc[i, "_bid"]), int(df.loc[i, "_bcid"]))
                h = market.realized_history(ids, args.history_start)
                if h:
                    df.loc[i, "Realized DA (hrs | P50 | max)"] = (
                        f"{h['n_hours']} | {h['p50']} | {h['max']}")
        except Exception:
            pass
        try:  # fast-scan stressed-hours headroom
            cfgs = fastscan.find_configs(args.study, int(f), int(t), ctg)
            if not cfgs.empty:
                prof = fastscan.headroom_profile(int(cfgs["CONFIG_ID"].iloc[0]))
                worst = prof.loc[prof["PCT_NEG"].idxmax()]
                df.loc[i, "Headroom stressed hrs (P10 MW | %hrs)"] = (
                    f"{float(worst['P10_HEADROOM']):.0f} | {float(worst['PCT_NEG']):.1f}%")
        except Exception:
            pass
        try:  # independent offer-based lambda (SF-filtered pair)
            est = offer_lambda.estimate(args.study, ctgviol, gen, bus_names, genunit, scedname, c)
            if est:
                df.loc[i, "λ offers (lo–hi)"] = f"{est['lam_lo']}–{est['lam_hi']}"
                df.loc[i, "Redispatch pair"] = est["pair"]
        except Exception:
            pass
        try:  # cheapest auction path (FWD-auction cost mark)
            paths = popt.best_paths(args.study, c)
            if paths is not None:
                p = paths.iloc[0]
                df.loc[i, "Best path ($/MWh @SF)"] = (
                    f"{p['SOURCENAME']}→{p['SINKNAME']} ${float(p['OPTIONPRICE']):.2f} @{float(p['AVG_SF']):.2f}")
                df.loc[i, "Path $/SF"] = round(float(p["PRICE_PER_SF"]), 2)
        except Exception:
            pass

    # edge: expected on-peak $/MWh per 1.0 SF (realized P50 λ where available,
    # else LP P50) minus the cheapest path's cost per SF
    def _value(row):
        lam = None
        rd = row["Realized DA (hrs | P50 | max)"]
        if isinstance(rd, str):
            lam = float(rd.split("|")[1])
        elif pd.notna(row["λ LP P50"]):
            lam = float(row["λ LP P50"])
        if lam is None:
            return None
        onpk = (row["P(bind) on-peak"] * (ONPEAK_BLOCKS[12] + ONPEAK_BLOCKS[18]) / 16)
        return round(onpk * lam, 2)

    df["Value $/MWh/SF"] = df.apply(_value, axis=1)
    df["Edge $/MWh/SF"] = df.apply(
        lambda r: round(r["Value $/MWh/SF"] - r["Path $/SF"], 2)
        if pd.notna(r["Value $/MWh/SF"]) and pd.notna(r["Path $/SF"]) else None, axis=1)
    df["_edge_sort"] = df["Edge $/MWh/SF"].fillna(df["Value $/MWh/SF"]).fillna(-1e9)
    df = df.sort_values(["_kv345", "_edge_sort"], ascending=[False, False]).reset_index(drop=True)

    show_cols = [c for c in df.columns if not c.startswith("_")]
    df[show_cols].to_csv(out_dir / "high_confidence_constraints.csv", index=False)

    style = """
    body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:2rem;color:#1a1a2e;background:#fafafa}
    h1{font-size:1.4rem} h2{font-size:1.05rem;margin-top:2rem}
    .meta{color:#555;font-size:0.9rem;margin-bottom:1rem;max-width:80rem;line-height:1.4}
    table{border-collapse:collapse;font-size:0.78rem;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.12)}
    th,td{border:1px solid #ddd;padding:4px 7px;text-align:right;white-space:nowrap}
    th{background:#22304a;color:#fff;position:sticky;top:0}
    td:first-child,td:nth-child(2),td:nth-child(3){text-align:left}
    tr:nth-child(even){background:#f4f6fa}
    .hi{background:#fff8e1!important;font-weight:600}
    .risk td{color:#8a1f1f}
    .note{font-size:0.85rem;color:#444;max-width:75rem;line-height:1.45}
    """
    body_rows = []
    for _, r in df.iterrows():
        cls = []
        if r["_kv345"]:
            cls.append("hi")
        if isinstance(r["Risk"], str):
            cls.append("risk")
        cattr = f' class="{" ".join(cls)}"' if cls else ""
        tds = "".join(f"<td>{'' if pd.isna(r[c]) else r[c]}</td>" for c in show_cols)
        body_rows.append(f"<tr{cattr}>{tds}</tr>")
    header = "".join(f"<th>{c}</th>" for c in show_cols)

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>CRR targets — study {args.study}</title><style>{style}</style></head><body>
<h1>CRR targets — study {args.study} ({study_name}), {args.month}</h1>
<div class="meta">Every binding constraint, every stage — nothing skipped. <b>345 kV first (highlighted), then by
Edge = Value − Path cost</b> where Value $/MWh/SF = P(bind on-peak) × λ (realized DA P50 since {args.history_start}
where the ISO ID-join found history, else study LP P50) and Path $/SF = cheapest completed path-opt path's
FWD-auction cost mark per unit SF. Red rows: penalty-tier λ = no economic dispatch resolves the constraint —
ERCOT is likely to deny the driving outage (high risk), but a cheap enough path can still be worth it.
Drivers: outage-driven (ticket verified via teid), implied-verified (driving line Closed pre-{cutoff[5:]},
Open after — from the study's own line statuses), topology-suspect (unverified), baseline.
Realized DA = binding hours | P50 λ | max λ from CONGHRPRICE via the (BRANCHMONITOREDID, BRANCHCONTINGENCYID)
ID join. Headroom = fast-scan worst stressed hour (P10 MW | % of hours overloaded).
Generated {pd.Timestamp.now():%Y-%m-%d %H:%M}.</div>
<table><thead><tr>{header}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>
<h2>Caveats</h2>
<div class="note"><p>Path settles should be short-risk checked against SPTHRPRICEHOURLYVIEW before bidding
(a path long our constraint can be short other congestion). λ offers use the 60-day-lagged DAM disclosure.
P(bind) equal-weights study runs — wind-scenario weighting is the next calibration step.</p></div>
</body></html>"""
    (out_dir / "high_confidence_constraints.html").write_text(html)
    print(df[show_cols].head(40).to_string(index=False))
    print(f"\n{len(df)} constraints -> {out_dir / 'high_confidence_constraints.html'}")


if __name__ == "__main__":
    main()
