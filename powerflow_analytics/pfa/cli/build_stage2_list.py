"""Shortlist of CRR candidates for one study: screening (pfa.analysis.screening) + month valuation -> CSVs + HTML.

Usage:
    uv run pfa shortlist --study 14431 --cutoff 2026-09-15 --month 2026-09
"""
from __future__ import annotations

import argparse

from pfa import config
from pfa.analysis.screening import Thresholds, screen_study
from pfa.analysis.shortlist_value import shortlist_rows, value_shortlist
from pfa.report import shortlist as shortlist_report


# ---------------------------------------------------------------------------
def main(argv=None) -> None:
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

    res = screen_study(study, args.cutoff, th)

    res.dirs.to_frame().to_csv(f"{outdir}/constraint_dirs.csv")
    print("-> constraint_dirs.csv | direction distribution:", res.dirs.value_counts().to_dict())

    fl = res.flips
    fl.to_csv(f"{outdir}/step1_flips.csv", index=False)
    print("FUNNEL:", res.universe["class"].value_counts().to_dict(), "| universe:", len(res.universe))
    print()
    print("=== FLIP PAIRS (baseline fades -> new binder emerges, shared bus) ===")
    print(fl.head(15).to_string(index=False) if not fl.empty else "(none)")

    res.universe.to_csv(f"{outdir}/step1_screen.csv")
    print()
    print(f"-> {outdir}/step1_screen.csv + step1_flips.csv")

    gated = value_shortlist(res, args.month)
    gated.to_csv(f"{outdir}/stage2_list.csv")

    print()
    print(f"STAGE-2 LIST — {len(gated)} constraints")
    show = [
        "FROMNAME", "TONAME", "share", "pre_binds", "post_binds", "post_days", "lam_p50_gate",
        "intensity", "NQUAL", "RENT_POST", "flip_exempt", "thin_intensity",
        "DRIVER_TICKET", "DRIVER_TICKET_STATUS",
    ]
    print(gated[show].round(2).to_string())

    dropped = res.intensity_dropped
    print()
    print("=== rows dropped by the hard intensity floor ===")
    if not dropped.empty:
        print(dropped[["FROMNAME", "TONAME", "post_binds", "lam_p50_gate", "intensity"]].round(2).to_string())
    else:
        print("(none)")

    out = shortlist_rows(study, gated, res.dirs, args.cutoff, args.month)
    (outdir / "stage2_list.html").write_text(shortlist_report.render(out, study, args.cutoff, args.month, th))
    print()
    print(f"-> {outdir}/stage2_list.html | {outdir}/stage2_list.csv | {len(out)} rows")

