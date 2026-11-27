"""Deep-dive report for one or more binding constraints: wind/solar binding
thresholds, dispatch profile, price formation, and (with 2+ constraints)
flip attribution between them.

Usage:
    uv run pfa deep-dive --study 14412 \
        --constraint 35045 --constraint 35055_A \
        --history-start 2026-04-01 --history-end 2026-09-28 --month 2026-09 \
        --out /path/to/report.md

--constraint accepts either a full key "FROMNUM-TONUM-CKT@CTGLABEL" or a
line LABEL from the cached outbranch2 table (e.g. "35045"); a bare label is
resolved to (FROMNUM, TONUM, CKT) via outbranch2 and to its dominant binding
CTGLABEL via outctgviol2 (most binding-run count at LIMVIOLPCT>=99.5).

Reuses pfa.extract.fastscan / shadow_price / gen_mapping —
this script only orchestrates and writes markdown.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from pfa import config
from pfa.analysis import deep_dive
from pfa.report import deep_dive as dd_report


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--constraint", action="append", required=True,
                    help="'FROMNUM-TONUM-CKT@CTGLABEL' or a line LABEL (repeatable)")
    ap.add_argument("--history-start", required=True)
    ap.add_argument("--history-end", required=True)
    ap.add_argument("--month", required=True, help="target calendar month YYYY-MM for the on/off-peak hit rate")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    tables = deep_dive.load_tables(args.study)
    resolved = [deep_dive.resolve_constraint(tables.cache, spec) for spec in args.constraint]
    print("Resolved constraints:")
    for c in resolved:
        print(f"  {c['key']}  {c['label']}  {c['fromname']}->{c['toname']}  "
              f"direction={c['direction']}  binding_runs={c['n_binding_runs']}")

    results = [deep_dive.analyze_constraint(args.study, c, tables, args.history_start, args.history_end, args.month)
               for c in resolved]
    flip_df = deep_dive.flip_attribution(tables.cache, resolved)
    md = dd_report.render_markdown(args.study, results, flip_df, deep_dive.flip_synthesis_facts(results, flip_df))
    out_path = Path(args.out) if args.out else (
        config.OUTPUT_ROOT / f"study_{args.study}" / f"deep_dive_{'_'.join(c['label'] for c in resolved)}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md)
    print(f"\nReport written to {out_path}")
