"""Cross-study constraint comparison report (e.g. 14411 vs 14412).

Study B typically adds implied/breaker outages. For every binding, LP-priced,
non-penalty constraint:
  - PERSISTING: binds in both studies (confidence up — robust to topology set)
  - NEW in B: binds only with implied outages — no ticket to verify, so the
    evidence columns are fast-scan stress and path-opt cheap paths
Ranked by rent score (P50 $/MWh x limit MVA); 345 kV floats up on size.

Usage: uv run powerflow_analytics/scripts/build_study_comparison_report.py \
    --study-a 14411 --study-b 14412 [--month 2026-09]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pfa import config, sf
from pfa.analysis import fastscan, valuation
from pfa.cache import StudyCache

MIN_BIND = 5  # lower than single-study report: catching movers matters more here


def study_frame(study_id: int, month: tuple[int, int]) -> pd.DataFrame:
    """Per-constraint valuation over the full study window."""
    cache = StudyCache(study_id)
    runs = cache.load("opfrun")
    outcon = cache.load("outconstraint2")
    ranked = pd.read_csv(config.OUTPUT_ROOT / f"study_{study_id}" / "ranked_constraints.csv")
    window = (str(pd.to_datetime(runs["SIMDATE"]).min().date()),
              str(pd.to_datetime(runs["SIMDATE"]).max().date()))
    short = ranked[(ranked["N_RUNS_BINDING"] >= MIN_BIND)
                   & (ranked["TOTAL_RENT"] > 0)].drop_duplicates("CONSTRAINT")
    rows = []
    for _, r in short.iterrows():
        stats = valuation.binding_stats(outcon, runs, r["CONSTRAINT"], window)
        lam = float(stats.lam["p50"].max()) if len(stats.lam) else 0.0
        if lam >= 500 or lam == 0.0:
            continue
        v = valuation.dollars_per_mwh(stats, *month, window, "p50")["dollars_per_mwh"]
        limit = float(r.get("LIMIT_MVA") or 0)
        rows.append({
            "CONSTRAINT": r["CONSTRAINT"], "FROMNAME": r["FROMNAME"], "TONAME": r["TONAME"],
            "KV345": limit >= 900 or str(r["FROMNAME"]).rstrip("AB").endswith("5"),
            "LIMIT_MVA": int(limit), "LAM_P50": round(lam, 1),
            "P_BIND_18": round(stats.p_bind.get(18, 0), 2),
            "USD_MWH_P50": v, "RENT_SCORE": round(v * limit / 1000, 1),
            "TOTAL_RENT": int(r["TOTAL_RENT"]), "N_RUNS_BINDING": int(r["N_RUNS_BINDING"]),
            "DRIVER": r.get("DRIVER_CLASS"), "TICKET": r.get("DRIVER_TICKET"),
            "TICKET_STATUS": r.get("DRIVER_TICKET_STATUS"),
        })
    return pd.DataFrame(rows)


def popt_best_paths(study_id: int, constraint: str, top_n: int = 3) -> pd.DataFrame | None:
    """Cheapest completed path-opt paths per unit exposure for one constraint."""
    f, t, rest = constraint.split("-", 2)
    ctg = rest.split("@")[1]
    batches = sf.query("AW", f"""
        SELECT PATHOPTRUNID FROM AW.POPT.PATHOPT_BATCH_INPUT
        WHERE STUDYID = {study_id} AND CTGLABEL = '{ctg}' AND PATHOPTRUNID IS NOT NULL
          AND (BRANCHLABEL ILIKE '%{f} %' OR BRANCHLABEL ILIKE '%{f}-%' OR BRANCHLABEL ILIKE '%_A%'
               OR BRANCHLABEL ILIKE '%{t}%')
        LIMIT 5""")
    if batches.empty:
        return None
    run_ids = ",".join(str(int(x)) for x in batches["PATHOPTRUNID"].unique())
    return sf.query("AW", f"""
        WITH d AS (
          SELECT SOURCENAME, SINKNAME, OPTIONPRICE, AVG_SF,
                 OPTIONPRICE / NULLIF(AVG_SF,0) AS PRICE_PER_SF
          FROM AW.POPT.PATHOPTDETAIL
          WHERE PATHOPTRUNID IN ({run_ids}) AND AVG_SF >= 0.05
        )
        SELECT * FROM d ORDER BY PRICE_PER_SF ASC LIMIT {top_n}""")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study-a", type=int, required=True)
    ap.add_argument("--study-b", type=int, required=True)
    ap.add_argument("--month", default="2026-09")
    ap.add_argument("--top-new", type=int, default=20, help="new constraints to enrich")
    args = ap.parse_args()
    month = tuple(int(x) for x in args.month.split("-"))

    a = study_frame(args.study_a, month)
    b = study_frame(args.study_b, month)
    a_keys, b_keys = set(a["CONSTRAINT"]), set(b["CONSTRAINT"])

    persist = b[b["CONSTRAINT"].isin(a_keys)].merge(
        a[["CONSTRAINT", "USD_MWH_P50", "RENT_SCORE", "TICKET", "TICKET_STATUS", "DRIVER"]],
        on="CONSTRAINT", suffixes=("", "_A"))
    persist = persist.sort_values("RENT_SCORE", ascending=False)
    new = b[~b["CONSTRAINT"].isin(a_keys)].sort_values("RENT_SCORE", ascending=False)
    dropped = a[~a["CONSTRAINT"].isin(b_keys)].sort_values("RENT_SCORE", ascending=False)

    # enrich top new constraints: fast-scan stress + cheapest path-opt path
    new = new.reset_index(drop=True)
    new["FASTSCAN_MAX_NEG"] = None
    new["BEST_PATH"] = None
    for i in new.index[: args.top_new]:
        c = new.loc[i, "CONSTRAINT"]
        f, t, rest = c.split("-", 2)
        ctg = rest.split("@")[1]
        try:
            cfgs = fastscan.find_configs(args.study_b, int(f), int(t), ctg)
            if not cfgs.empty:
                prof = fastscan.headroom_profile(int(cfgs["CONFIG_ID"].iloc[0]))
                new.loc[i, "FASTSCAN_MAX_NEG"] = round(float(prof["PCT_NEG"].max()), 1)
        except Exception:
            pass
        try:
            paths = popt_best_paths(args.study_b, c)
            if paths is not None and len(paths):
                p = paths.iloc[0]
                new.loc[i, "BEST_PATH"] = (f"{p['SOURCENAME']}→{p['SINKNAME']} "
                                           f"${p['OPTIONPRICE']:.2f} @SF {p['AVG_SF']:.2f}")
        except Exception:
            pass

    out_dir = config.OUTPUT_ROOT / f"study_{args.study_b}"
    out_dir.mkdir(parents=True, exist_ok=True)
    persist.to_csv(out_dir / f"persisting_vs_{args.study_a}.csv", index=False)
    new.to_csv(out_dir / f"new_vs_{args.study_a}.csv", index=False)

    def table(df, cols):
        head = "".join(f"<th>{c}</th>" for c in cols)
        body = "".join(
            "<tr class='hi345'>" + "".join(
                f"<td>{'' if pd.isna(r[c]) else r[c]}</td>" for c in cols) + "</tr>"
            if r.get("KV345") else
            "<tr>" + "".join(f"<td>{'' if pd.isna(r[c]) else r[c]}</td>" for c in cols) + "</tr>"
            for _, r in df.iterrows())
        return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"

    pcols = ["CONSTRAINT", "FROMNAME", "TONAME", "KV345", "LIMIT_MVA", "LAM_P50", "P_BIND_18",
             "USD_MWH_P50", "RENT_SCORE", "USD_MWH_P50_A", "RENT_SCORE_A",
             "DRIVER_A", "TICKET_A", "TICKET_STATUS_A"]
    persist = persist.rename(columns={"DRIVER": "DRIVER_B", "TICKET": "TICKET_B"})
    pcols = [c for c in pcols if c in persist.columns]
    ncols = ["CONSTRAINT", "FROMNAME", "TONAME", "KV345", "LIMIT_MVA", "LAM_P50", "P_BIND_18",
             "USD_MWH_P50", "RENT_SCORE", "N_RUNS_BINDING", "FASTSCAN_MAX_NEG", "BEST_PATH"]
    dcols = ["CONSTRAINT", "FROMNAME", "TONAME", "KV345", "RENT_SCORE", "TICKET", "TICKET_STATUS"]

    style = """
    body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:2rem;color:#1a1a2e;background:#fafafa}
    h1{font-size:1.35rem} h2{font-size:1.1rem;margin-top:2.2rem}
    .meta,.note{color:#444;font-size:0.88rem;max-width:75rem;line-height:1.45}
    table{border-collapse:collapse;font-size:0.8rem;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.12);margin-top:.6rem}
    th,td{border:1px solid #ddd;padding:4px 7px;text-align:right;white-space:nowrap}
    th{background:#22304a;color:#fff}
    td:first-child,td:nth-child(2),td:nth-child(3),td:last-child{text-align:left}
    tr:nth-child(even){background:#f4f6fa}
    tr.hi345 td{background:#fff8e1;font-weight:600}
    """
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Study {args.study_b} vs {args.study_a} — constraint comparison</title><style>{style}</style></head><body>
<h1>Study {args.study_b} vs {args.study_a} — CRR constraint comparison ({args.month})</h1>
<div class="meta">Study {args.study_b} includes implied (breaker) outages. Binding ≥ {MIN_BIND} runs, LP-priced,
penalty-tier λ excluded. $/MWh per 1.0 SF over the 5x16 block; Rent score = P50 $/MWh × limit MVA.
<b>345 kV rows highlighted.</b> Generated {pd.Timestamp.now():%Y-%m-%d %H:%M}.</div>

<h2>Persisting constraints ({len(persist)}) — bind in BOTH studies (highest confidence)</h2>
<div class="note">_A columns = study {args.study_a} values; tickets were verified in study {args.study_a}.</div>
{table(persist, pcols)}

<h2>New in study {args.study_b} ({len(new)}) — implied/breaker-outage driven</h2>
<div class="note">No outage ticket exists to verify (drivers are implied breaker states).
Evidence: fast-scan max % of historical hours with negative headroom on this topology, and the
cheapest completed path-opt path (option $/MWh @ avg SF) where a run exists.</div>
{table(new, ncols)}

<h2>Dropped vs study {args.study_a} ({len(dropped)}) — bound in {args.study_a} only</h2>
{table(dropped, dcols)}
</body></html>"""
    html_path = out_dir / f"comparison_{args.study_b}_vs_{args.study_a}.html"
    html_path.write_text(html)
    print(f"persisting {len(persist)}, new {len(new)}, dropped {len(dropped)}")
    print(new.head(args.top_new)[[c for c in ncols if c in new.columns]].to_string(index=False))
    print(f"-> {html_path}")


if __name__ == "__main__":
    main()
