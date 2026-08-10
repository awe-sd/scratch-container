"""Value one constraint in $/MWh over the 5x16 on-peak block.

Usage:
  uv run powerflow_analytics/scripts/value_constraint.py --study 14411 \
      --constraint "1436-2081-1@DWCSRAM5" --month 2026-09 \
      --window 2026-09-16 2026-10-02 [--sf 0.31] [--fastscan]

Window = the driving outage's dates (from post_sep15_outage_upside.csv /
ticket lookup). --sf scales flowgate $/MWh to a CRR path's exposure.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pfa.analysis import valuation
from pfa.cache import StudyCache


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--constraint", required=True, help='e.g. "1436-2081-1@DWCSRAM5"')
    ap.add_argument("--month", required=True, help="YYYY-MM settlement month")
    ap.add_argument("--window", nargs=2, required=True, metavar=("START", "END"),
                    help="outage window YYYY-MM-DD YYYY-MM-DD")
    ap.add_argument("--sf", type=float, default=1.0, help="path shift factor on the flowgate")
    ap.add_argument("--fastscan", action="store_true", help="also query fast-scan headroom")
    args = ap.parse_args()

    cache = StudyCache(args.study)
    runs = cache.load("opfrun")
    outcon = cache.load("outconstraint2")
    year, month = (int(x) for x in args.month.split("-"))

    stats = valuation.binding_stats(outcon, runs, args.constraint, tuple(args.window))
    print(f"{args.constraint} — window {args.window[0]}..{args.window[1]} "
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
        from pfa.analysis import fastscan

        f, t, rest = args.constraint.split("-", 2)
        ckt_ctg = rest.split("@")
        cfgs = fastscan.find_configs(args.study, int(f), int(t), ckt_ctg[1])
        if cfgs.empty:
            print("\nfast-scan: no config found for this constraint/study")
        else:
            cid = int(cfgs["CONFIG_ID"].iloc[0])
            print(f"\nfast-scan config {cid} headroom profile:")
            print(fastscan.headroom_profile(cid).round(1).to_string(index=False))


if __name__ == "__main__":
    main()
