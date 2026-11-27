"""Value one constraint: a fact sheet, then the monthly on-peak $/MWh mark.

Usage:
  uv run powerflow_analytics/scripts/value_constraint.py --study 14412 \
      --constraint "1436-2081-1@DWCSRAM5" [--month 2026-09 --window 2026-09-16 2026-10-02] \
      [--sf 0.31] [--fastscan]

--constraint is a full key or a line label (resolved to its dominant binding contingency).
Window = the driving outage's dates; the mark needs --month and --window, otherwise only the
fact sheet is printed. --sf scales flowgate $/MWh to a CRR path's exposure.
The two sections define "binding" differently (each is labelled): fact sheet = LIMVIOLPCT >= 99.5
in OUTCTGVIOL2; monthly mark = runs with a row for the constraint in OUTCONSTRAINT2.
"""
from __future__ import annotations

import argparse
import json

import pandas as pd

from pfa import periods
from pfa.analysis import valuation
from pfa.cache import StudyCache
from pfa.constraint_id import resolve


def print_fact_sheet(result: dict) -> None:
    print(f"constraint {result['constraint']} (study {result['study_id']})")
    print(f"  binding cases: {result['n_binding_cases']} / {result['n_total_cases']} rows flagged "
          f"in OUTCTGVIOL2 ({result['n_total_study_runs']} total study runs)")
    print("  lambda ($/MWh) over binding runs:")
    for k, v in result["lambda_stats"].items():
        print(f"    {k}: {v}")
    print(f"  top marginal units ({len(result['marginal_units'])}):")
    for u in result["marginal_units"]:
        print(f"    {json.dumps(u, default=str)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--constraint", required=True, help='full key "1436-2081-1@DWCSRAM5" or a line label')
    ap.add_argument("--month", help="YYYY-MM settlement month (for the monthly mark)")
    ap.add_argument("--window", nargs=2, metavar=("START", "END"),
                    help="outage window YYYY-MM-DD YYYY-MM-DD (for the monthly mark)")
    ap.add_argument("--sf", type=float, default=1.0, help="path shift factor on the flowgate")
    ap.add_argument("--fastscan", action="store_true", help="also query fast-scan headroom")
    args = ap.parse_args()
    if args.window and not args.month:
        ap.error("--window needs --month")

    cache = StudyCache(args.study)
    cid = resolve(cache, args.constraint)
    key = str(cid)

    print("== Fact sheet (binding = LIMVIOLPCT >= 99.5 in OUTCTGVIOL2) ==")
    print_fact_sheet(valuation.fact_sheet(args.study, cid.fromnum, cid.tonum, cid.ckt, cid.ctglabel))

    if not args.window:
        print("\n== Monthly on-peak mark skipped: no --window given ==")
    else:
        print("\n== Monthly on-peak mark (binding = runs with a row for the constraint in OUTCONSTRAINT2) ==")
        runs = cache.load("opfrun")
        outcon = cache.load("outconstraint2")
        year, month = periods.parse_month(args.month)

        stats = valuation.binding_stats(outcon, runs, key, tuple(args.window))
        print(f"{key} — window {args.window[0]}..{args.window[1]} "
              f"({stats.n_window_runs} runs in window)")
        print("P(bind | sim hour):", {h: round(p, 2) for h, p in stats.p_bind.items()})
        print("lambda ($/MWh):")
        print(stats.lam.round(1).to_string())
        print()
        rows = [valuation.dollars_per_mwh(stats, year, month, tuple(args.window), col, args.sf)
                for col in ("p25", "p50", "p75", "mean")]
        print(pd.DataFrame(rows)[["lam_col", "sf", "outage_onpeak_days",
                                  "rent_per_mw_month", "dollars_per_mwh"]].to_string(index=False))

    if args.fastscan:
        from pfa.extract import fastscan

        cfgs = fastscan.find_configs(args.study, cid.fromnum, cid.tonum, cid.ctglabel)
        if cfgs.empty:
            print("\nfast-scan: no config found for this constraint/study")
        else:
            config_id = int(cfgs["CONFIG_ID"].iloc[0])
            print(f"\nfast-scan config {config_id} headroom profile:")
            print(fastscan.headroom_profile(config_id).round(1).to_string(index=False))


if __name__ == "__main__":
    main()
