#!/usr/bin/env python3
"""PathOpt scatter: find paths that are LONG both constraints and CHEAP.

Usage:
    uv run --with "pyopenssl>=26.4" pfa paths \\
        --study 14835 --run-x 10008060 --run-y 10008041 \\
        --date 2026-11-10 --hour 18 --top 100000 --min-sf 0.05

N-run mode (overlap of several PathOpt runs, pair search; --study = context study for binding stats):
    ... pfa paths --study 14966 --out-dir output/pathopt/14966_dblbywf5 --min-sf 0.02 --holidays 2026-12-25 \\
        --runs JCKSTP18A=10023193,JCKREF27A=10023204,BLESSING1382=10023214,BLESSI_PAVLOV11=10023147 \\
        --required JCKSTP18A,JCKREF27A,BLESSING1382 \\
        --constraints JCKSTP18A=5915-42530-18@DBLBYWF5,JCKREF27A=42400-42530-27@DBLBYWF5,BLESSING1382=8121-8123-1@DBLBYWF5,BLESSI_PAVLOV11=8121-8614-1@DBLBYWF5
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from pfa import config
from pfa.analysis import path_search
from pfa.report import path_search as report


def _write_frames(out, csvs: dict) -> None:
    for name, frame in csvs.items():
        frame.to_csv(out / name, index=False)


def run_multi(args, command: str) -> None:
    out = config.OUTPUT_ROOT / "pathopt" / f"{args.study}_multi" if not args.out_dir else Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    result = path_search.run_multi(_spec(args), log=print)
    _write_frames(out, result.csvs)
    result.paths_all().to_parquet(out / "paths_all.parquet", index=False)
    stale = out / "candidates_pairs_any.csv"
    if stale.exists():
        stale.unlink()
    (out / "report.html").write_text(report.multi_html(result))
    (out / "README.md").write_text(report.multi_readme(result, command))
    print("wrote", out)


def run_spread(args, command: str) -> None:
    out = config.OUTPUT_ROOT / "pathopt" / f"{args.study}_spread" if not args.out_dir else Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    result = path_search.run_spread(_spec(args), log=print)
    _write_frames(out, result.csvs)
    (out / "report.html").write_text(report.spread_html(result))
    (out / "README.md").write_text(report.spread_readme(result, command))
    print("wrote", out)


def run_pair(args) -> None:
    spec = path_search.PairSpec(args.study, args.run_x, args.run_y, args.date, args.hour, args.top, args.min_sf)
    print(f"\n{'='*80}")
    print(f"PathOpt Scatter: Study {args.study}, Date {args.date} HE{args.hour}")
    print(f"X-axis: Run {args.run_x} | Y-axis: Run {args.run_y}")
    print(f"Scatter: top {args.top:,} cheapest | Candidates: full universe, MIN_SF floor ≥ {args.min_sf}")
    print(f"{'='*80}\n")
    try:
        r = path_search.run_pair(spec, log=print)
    except path_search.PairInputError as e:
        print(f"\n  ERROR: {e}")
        sys.exit(1)
    print("\nStep 12: Writing output files...")
    out = config.OUTPUT_ROOT / "pathopt" / f"{args.study}_{args.date}"
    out.mkdir(parents=True, exist_ok=True)
    stale = out / "paths_100k.parquet"
    if stale.exists():
        stale.unlink()
        print(f"  ✓ Deleted stale: {stale.name}")
    (out / "scatter.html").write_text(report.pair_scatter_html(report.pair_scatter(r.paths_deduped, r.candidates, spec, r.run_x, r.run_y)))
    print("  ✓ Scatter plot: scatter.html")
    r.candidates[report.PAIR_OUTPUT_COLS].to_csv(out / "candidates.csv", index=False)
    print(f"  ✓ Candidates CSV (top {args.top:,} cut): candidates.csv ({len(r.candidates):,} rows)")
    r.candidates_full[report.PAIR_FULL_COLS].to_csv(out / "candidates_full.csv", index=False)
    print(f"  ✓ Candidates FULL CSV (full universe): candidates_full.csv ({len(r.candidates_full):,} rows)")
    r.near_miss[report.PAIR_FULL_COLS].to_csv(out / "near_miss.csv", index=False)
    print(f"  ✓ Near-miss CSV: near_miss.csv ({len(r.near_miss):,} rows)")
    r.paths_deduped.to_parquet(out / "paths_deduped.parquet", index=False)
    print(f"  ✓ Deduped paths parquet: paths_deduped.parquet ({len(r.paths_deduped):,} paths)")
    (out / "README.md").write_text(report.pair_readme(r))
    print("  ✓ README: README.md")
    print(report.pair_console(r))
    print(f"  - Output: {out}\n")


def _spec(args) -> path_search.PathSpec:
    return path_search.PathSpec.from_strings(
        study=args.study, runs=args.runs, value_only=args.value_only, required=args.required, short=args.short,
        constraints=args.constraints, floor=args.min_sf_each, pool=args.pool, holidays=args.holidays,
        long_basis=args.long_basis, short_basis=args.short_basis)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="PathOpt scatter: long-both + cheap paths by MIN_SF robustness")
    parser.add_argument("--study", type=int, required=True, help="Study ID")
    parser.add_argument("--run-x", type=int, help="X-axis PathOpt run ID")
    parser.add_argument("--run-y", type=int, help="Y-axis PathOpt run ID")
    parser.add_argument("--date", help="Simulation date (YYYY-MM-DD)")
    parser.add_argument("--hour", type=int, help="Simulation hour (1-24)")
    parser.add_argument("--runs", help="N-run mode: LABEL=RUNID,... (PathOpt runs)")
    parser.add_argument("--required", help="N-run mode: labels that must all be long (default: all but last)")
    parser.add_argument("--constraints", help="N-run mode: LABEL=FROM-TO-CKT@CTG,... for study binding/SP context")
    parser.add_argument("--out-dir", help="N-run mode: output directory")
    parser.add_argument("--value-only", help="N-run mode: LABEL=RUNID,... co-binder legs valued (signed) but not required long")
    parser.add_argument("--short", help="Spread mode: SHORT leg label(s); --required is the single LONG leg; runs both directions when one short")
    parser.add_argument("--short-basis", choices=["binding", "live"], default="binding",
                        help="Spread mode: short leg tested on MAX_SF over its binding periods (default) or all live periods")
    parser.add_argument("--long-basis", choices=["binding", "live"], default="live",
                        help="Spread mode: long leg tested on MIN_SF over all live periods (default) or its binding periods only")
    parser.add_argument("--min-sf-each", type=float, default=0.05, help="N-run mode: live-period MIN_SF floor on every required constraint")
    parser.add_argument("--holidays", help="N-run/spread mode (required there): comma-separated dates for holiday sensitivity, '' for none")
    parser.add_argument("--pool", type=int, default=300, help="N-run mode: pair-search pool per constraint")
    parser.add_argument("--top", type=int, default=100000, help="Top N cheapest paths for scatter (default: 100000)")
    parser.add_argument("--min-sf", type=float, default=0.05, help="Min SF floor on both MIN_SFs (default: 0.05)")
    args = parser.parse_args(argv)
    command = report.invocation(list(sys.argv[1:] if argv is None else argv))
    if args.runs and args.holidays is None:
        parser.error("--holidays is required with --runs (comma-separated dates, or '' for none)")
    if args.runs and args.short and not args.required:
        parser.error("--short (spread mode) needs --required naming the single long leg")
    if args.runs and args.short:
        return run_spread(args, command)
    if args.runs:
        return run_multi(args, command)
    if None in (args.run_x, args.run_y, args.date, args.hour):
        parser.error("either --runs or all of --run-x --run-y --date --hour are required")
    try:
        args.date = pd.Timestamp(args.date).strftime("%Y-%m-%d")
    except ValueError:
        parser.error(f"--date must be a date (YYYY-MM-DD), got {args.date!r}")
    return run_pair(args)
