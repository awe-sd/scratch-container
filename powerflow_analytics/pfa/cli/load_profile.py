"""Median ERCOT system load per hour-of-day, compared across years.

Usage:
    uv run pfa load-profile --start 09-16 --end 09-30 --years 2021-2025

Pulls (cache-first) via pfa.extract.load.get_load_window / median_load_profile
and writes an HTML plot with one trace per year to
powerflow_analytics/output/<mon>_load_hourly_median_5yr.html (e.g. sep_...).
"""
from __future__ import annotations

import argparse
from pathlib import Path


from pfa import config
from pfa.extract.load import median_load_profile
from pfa.report import load_profile as load_report


def parse_years(spec: str) -> list[int]:
    """'2021-2025' -> [2021,...,2025]; also accepts comma lists like '2021,2023'."""
    years: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-")
            years.extend(range(int(lo), int(hi) + 1))
        else:
            years.append(int(part))
    return years


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="MM-DD")
    ap.add_argument("--end", required=True, help="MM-DD")
    ap.add_argument("--years", default="2021-2025", help="e.g. 2021-2025 or 2021,2023,2025")
    ap.add_argument("--zone", default="ERCOT",
                     help="ERCOT (system total, default) or a weather zone: "
                          "COAST/EAST/FWEST/NORTH/NCENT/SOUTH/SCENT/WEST")
    ap.add_argument(
        "--out",
        default=None,
        help="output HTML path (default: output/<mon>_load_hourly_median_5yr.html, "
             "or output/<mon>_load_hourly_median_5yr_<zone>.html for a non-ERCOT zone)",
    )
    args = ap.parse_args(argv)

    years = parse_years(args.years)
    df = median_load_profile(years, args.start, args.end, zone=args.zone)

    print(load_report.table(df))

    fig = load_report.build_figure(df, args.start, args.end, zone=args.zone)
    if args.out is None:
        suffix = "" if args.zone == "ERCOT" else f"_{args.zone}"
        args.out = str(config.OUTPUT_ROOT / f"{load_report.mon(args.start)}_load_hourly_median_5yr{suffix}.html")
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(load_report.render(fig))
    print(f"wrote {out_path}")

