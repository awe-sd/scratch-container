"""Analyze a cached study: ranked binding constraints, marginal units, drivers.

Usage: uv run pfa summary --study 14411 --cutoff 2026-09-15 [--top 15] [--tickets]
"""
from __future__ import annotations

import argparse

from pfa import config
from pfa.analysis import summary
from pfa.report import summary as summary_report


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--top", type=int, default=15, help="constraints to detail")
    ap.add_argument("--tickets", action="store_true",
                    help="verify drivers against toAllIsos (small SQL Server lookups)")
    ap.add_argument("--cutoff", required=True,
                    help="outage-season cutoff YYYY-MM-DD for rent split")
    args = ap.parse_args(argv)

    out_dir = config.OUTPUT_ROOT / f"study_{args.study}"
    out_dir.mkdir(parents=True, exist_ok=True)
    result = summary.summarize_study(args.study, args.cutoff, args.top, args.tickets)
    result.ranked.to_csv(out_dir / "ranked_constraints.csv", index=False)
    result.base.to_csv(out_dir / "base_case_binders.csv", index=False)
    result.marginal_units.to_csv(out_dir / "marginal_units.csv", index=False)
    result.tofinder.to_csv(out_dir / "tofinder_summary.csv", index=False)
    print(summary_report.console(result, args.study, args.cutoff, args.top, out_dir))
