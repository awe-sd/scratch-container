"""Value one constraint: a fact sheet, then the monthly on-peak $/MWh mark.

Usage:
  uv run pfa value --study 14412 \
      --constraint "1436-2081-1@DWCSRAM5" [--month 2026-09 --window 2026-09-16 2026-10-02] \
      [--sf 0.31] [--fastscan]

--constraint is a full key or a line label (resolved to its dominant binding contingency).
Window = the driving outage's dates; the mark needs --month and --window, otherwise only the
fact sheet is printed. The cache-only mark prints first, the fact sheet (database) second; a failed fact sheet exits 1. --sf scales flowgate $/MWh to a CRR path's exposure.
The two sections define "binding" differently (each is labelled): fact sheet = LIMVIOLPCT >= 99.5
in OUTCTGVIOL2; monthly mark = runs with a row for the constraint in OUTCONSTRAINT2.
"""
from __future__ import annotations

import argparse

from pfa import periods
from pfa.analysis import valuation
from pfa.cache import StudyCache
from pfa.constraint_id import resolve
from pfa.report import value as value_report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--constraint", required=True, help='full key "1436-2081-1@DWCSRAM5" or a line label')
    ap.add_argument("--month", help="YYYY-MM settlement month (for the monthly mark)")
    ap.add_argument("--window", nargs=2, metavar=("START", "END"),
                    help="outage window YYYY-MM-DD YYYY-MM-DD (for the monthly mark)")
    ap.add_argument("--sf", type=float, default=1.0, help="path shift factor on the flowgate")
    ap.add_argument("--fastscan", action="store_true", help="also query fast-scan headroom")
    args = ap.parse_args(argv)
    if args.window and not args.month:
        ap.error("--window needs --month")

    cache = StudyCache(args.study)
    cid = resolve(cache, args.constraint)
    key = str(cid)

    # cache-only mark first: it must still print when the database is unavailable
    if not args.window:
        print("== Monthly on-peak mark skipped: no --window given ==")
    else:
        print("== Monthly on-peak mark (binding = runs with a row for the constraint in OUTCONSTRAINT2) ==")
        runs = cache.load("opfrun")
        outcon = cache.load("outconstraint2")
        year, month = periods.parse_month(args.month)

        window = tuple(args.window)
        stats = valuation.binding_stats(outcon, runs, key, window)
        print(value_report.monthly_mark(key, window, stats, valuation.mark_table(stats, year, month, window, args.sf)))

    print("\n== Fact sheet (binding = LIMVIOLPCT >= 99.5 in OUTCTGVIOL2) ==")
    try:
        print(value_report.fact_sheet(valuation.fact_sheet(args.study, cid.fromnum, cid.tonum, cid.ckt, cid.ctglabel)))
    except Exception as e:
        print(f"fact sheet failed: {type(e).__name__}: {e}")
        return 1

    if args.fastscan:
        from pfa.extract import fastscan

        cfgs = fastscan.find_configs(args.study, cid.fromnum, cid.tonum, cid.ctglabel)
        if cfgs.empty:
            print("\nfast-scan: no config found for this constraint/study")
        else:
            config_id = int(cfgs["CONFIG_ID"].iloc[0])
            print("\n" + value_report.headroom_profile(config_id, fastscan.headroom_profile(config_id)))
    return 0
