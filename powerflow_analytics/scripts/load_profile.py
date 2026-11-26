"""Median ERCOT system load per hour-of-day, compared across years.

Usage:
    uv run powerflow_analytics/scripts/load_profile.py --start 09-16 --end 09-30 --years 2021-2025

Pulls (cache-first) via pfa.extract.load.get_load_window / median_load_profile
and writes an HTML plot with one trace per year to
powerflow_analytics/output/sep_load_hourly_median_5yr.html.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import plotly.graph_objects as go

from pfa import config
from pfa.extract.load import median_load_profile


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


def build_figure(df, start_mmdd: str, end_mmdd: str, zone: str = "ERCOT") -> go.Figure:
    fig = go.Figure()
    for year in sorted(df["year"].unique()):
        sub = df[df["year"] == year].sort_values("he")
        fig.add_trace(
            go.Scatter(
                x=sub["he"],
                y=sub["median_load_gw"],
                mode="lines+markers",
                name=str(year),
            )
        )
    zone_label = "ERCOT system" if zone == "ERCOT" else f"{zone} LZ"
    fig.update_layout(
        title=f"{zone_label} median load by hour, Sep {start_mmdd[3:]}-{end_mmdd[3:]}",
        xaxis_title="Hour Ending (HE)",
        yaxis_title="Median load (GW)",
        hovermode="x unified",
        xaxis=dict(dtick=1, range=[0.5, 24.5]),
        template="plotly_white",
    )
    return fig


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="09-16", help="MM-DD, default 09-16")
    ap.add_argument("--end", default="09-30", help="MM-DD, default 09-30")
    ap.add_argument("--years", default="2021-2025", help="e.g. 2021-2025 or 2021,2023,2025")
    ap.add_argument("--zone", default="ERCOT",
                     help="ERCOT (system total, default) or a weather zone: "
                          "COAST/EAST/FWEST/NORTH/NCENT/SOUTH/SCENT/WEST")
    ap.add_argument(
        "--out",
        default=None,
        help="output HTML path (default: output/sep_load_hourly_median_5yr.html, "
             "or output/sep_load_hourly_median_5yr_<zone>.html for a non-ERCOT zone)",
    )
    args = ap.parse_args()

    years = parse_years(args.years)
    df = median_load_profile(years, args.start, args.end, zone=args.zone)

    print(df.pivot(index="he", columns="year", values="median_load_gw").round(2))

    fig = build_figure(df, args.start, args.end, zone=args.zone)
    if args.out is None:
        suffix = "" if args.zone == "ERCOT" else f"_{args.zone}"
        args.out = str(config.OUTPUT_ROOT / f"sep_load_hourly_median_5yr{suffix}.html")
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
