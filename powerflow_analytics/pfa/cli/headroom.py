"""Fast-scan headroom scatter (wind/solar/load vs headroom) for one constraint, written as HTML."""
from __future__ import annotations

import argparse

from pfa.analysis.headroom_plots import plot_headroom_scatter
from pfa.extract import fastscan


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Fast-scan headroom scatter for one constraint (HTML).")
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--fromnum", type=int, required=True)
    ap.add_argument("--tonum", type=int, required=True)
    ap.add_argument("--ctglabel", required=True)
    ap.add_argument("--y", choices=["solar", "load"], default="load")
    ap.add_argument("--peak", choices=["onpeak", "offpeak"], default="onpeak")
    ap.add_argument("--hist-start", required=True)
    ap.add_argument("--hist-end", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    configs = fastscan.find_configs(args.study, args.fromnum, args.tonum, args.ctglabel)
    if configs.empty:
        raise SystemExit(f"no active fast-scan config for study={args.study} "
                          f"{args.fromnum}-{args.tonum}@{args.ctglabel}")
    config_id = int(configs.iloc[0]["CONFIG_ID"])
    label = configs.iloc[0]["BRANCH_LABEL"]

    plot_headroom_scatter(
        config_id, y=args.y, peak=args.peak,
        hist_start=args.hist_start, hist_end=args.hist_end,
        out_html=args.out,
        title_prefix=f"{label} @ {args.ctglabel} (config {config_id}) —",
    )
    print(f"wrote {args.out}")

