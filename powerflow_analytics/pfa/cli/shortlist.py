"""Shortlist of CRR candidates for one study: screening (pfa.analysis.screening) + month valuation -> CSVs + HTML.

Usage:
    uv run pfa shortlist --study 14431 --cutoff 2026-09-15 --month 2026-09
"""
from __future__ import annotations

import argparse
import sys

from pfa import config
from pfa.analysis.screening import Thresholds, screen_study
from pfa.analysis.shortlist_value import shortlist_rows, value_shortlist, valuation_summary
from pfa.report import shortlist as shortlist_report


# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    d = Thresholds()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--cutoff", required=True, help="pre/post split date YYYY-MM-DD")
    ap.add_argument("--month", required=True, help="settlement month YYYY-MM to value the shortlist for")
    ap.add_argument("--share-min", type=float, default=d.share_min)
    ap.add_argument("--post-days-min", type=int, default=d.post_days_min)
    ap.add_argument("--rent-min", type=float, default=d.rent_min)
    ap.add_argument("--nqual-min", type=int, default=d.nqual_min)
    ap.add_argument("--intensity-min-hard", type=float, default=d.intensity_min_hard)
    ap.add_argument("--intensity-min-full", type=float, default=d.intensity_min_full)
    ap.add_argument("--penalty-share-max", type=float, default=d.penalty_share_max)
    args = ap.parse_args(argv)

    th = Thresholds(
        share_min=args.share_min, post_days_min=args.post_days_min, rent_min=args.rent_min,
        nqual_min=args.nqual_min, intensity_min_hard=args.intensity_min_hard,
        intensity_min_full=args.intensity_min_full, penalty_share_max=args.penalty_share_max,
    )
    study = args.study
    outdir = config.OUTPUT_ROOT / f"study_{study}"

    try:
        res = screen_study(study, args.cutoff, th)
    except FileNotFoundError as e:
        print(f"pfa shortlist: {e}", file=sys.stderr)
        return 2

    res.dirs.to_frame().to_csv(outdir / "constraint_dirs.csv")
    print("-> constraint_dirs.csv | direction distribution:", res.dirs.value_counts().to_dict())
    res.flips.to_csv(outdir / "step1_flips.csv", index=False)
    res.universe.to_csv(outdir / "step1_screen.csv")
    print(shortlist_report.console_screen(res))
    print()
    print(f"-> {outdir}/step1_screen.csv + step1_flips.csv")

    gated = value_shortlist(res, args.month)
    gated.to_csv(outdir / "stage2_list.csv")
    print()
    print(shortlist_report.console_shortlist(gated, res.intensity_dropped))

    out = shortlist_rows(study, gated, res.dirs, args.cutoff, args.month)
    (outdir / "stage2_list.html").write_text(shortlist_report.render(out, study, args.cutoff, args.month, th))
    print()
    print(f"-> {outdir}/stage2_list.html | {outdir}/stage2_list.csv | {len(out)} rows")
    summary = valuation_summary(gated, args.month)
    print()
    print(shortlist_report.console_valuation_summary(summary))
    return 1 if summary["failed"] else 0
