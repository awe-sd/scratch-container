"""Cross-study constraint comparison report (e.g. 14411 vs 14412): persisting, new and dropped constraints.

Usage: uv run pfa compare \
    --study-a 14411 --study-b 14412 --month 2026-09
"""
from __future__ import annotations

import argparse

import pandas as pd

from pfa import config, periods
from pfa.analysis import study_compare
from pfa.report import compare as compare_report


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study-a", type=int, required=True)
    ap.add_argument("--study-b", type=int, required=True)
    ap.add_argument("--month", required=True, help="settlement month YYYY-MM")
    ap.add_argument("--top-new", type=int, default=20, help="new constraints to enrich")
    args = ap.parse_args(argv)

    cmp = study_compare.compare_studies(args.study_a, args.study_b, periods.parse_month(args.month), args.top_new)
    out_dir = config.OUTPUT_ROOT / f"study_{args.study_b}"
    out_dir.mkdir(parents=True, exist_ok=True)
    cmp.persist.to_csv(out_dir / f"persisting_vs_{args.study_a}.csv", index=False)
    cmp.new.to_csv(out_dir / f"new_vs_{args.study_a}.csv", index=False)

    html_path = out_dir / f"comparison_{args.study_b}_vs_{args.study_a}.html"
    html_path.write_text(compare_report.render(args.study_a, args.study_b, args.month, study_compare.MIN_BIND,
                                               cmp.persist, cmp.new, cmp.dropped, f"{pd.Timestamp.now():%Y-%m-%d %H:%M}"))
    print(f"persisting {len(cmp.persist)}, new {len(cmp.new)}, dropped {len(cmp.dropped)}")
    print(compare_report.console_new(cmp.new, args.top_new))
    print(f"-> {html_path}")
