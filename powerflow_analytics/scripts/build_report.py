"""Analyze a cached study: ranked binding constraints, marginal units, drivers.

Usage: uv run powerflow_analytics/scripts/build_report.py --study 14411 [--top 15] [--tickets]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pfa import config
from pfa.analysis import constraints, drivers, marginal_units
from pfa.cache import StudyCache


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--top", type=int, default=15, help="constraints to detail")
    ap.add_argument("--tickets", action="store_true",
                    help="verify drivers against toAllIsos (small SQL Server lookups)")
    args = ap.parse_args()

    cache = StudyCache(args.study)
    runs = cache.load("opfrun")
    ctgviol = cache.load("outctgviol2")
    gen = cache.load("outgen2")
    tofinder = cache.load("outtofindermax2")
    branch = cache.load("outbranch2")
    genunit = cache.load("genunit")
    bus_names = marginal_units.bus_name_map(branch)

    out_dir = config.OUTPUT_ROOT / f"study_{args.study}"
    out_dir.mkdir(parents=True, exist_ok=True)

    ranked = constraints.rank_constraints(ctgviol, runs)
    tf_sum = drivers.tofinder_summary(tofinder)

    ticket_lookup, window = None, None
    if args.tickets:
        from pfa.extract.outages import lookup_branch_tickets

        simdates = pd.to_datetime(runs["SIMDATE"])
        window = (str(simdates.min().date()), str(simdates.max().date()))
        ticket_lookup = lookup_branch_tickets

    ranked = drivers.classify_constraints(ranked, tf_sum, ticket_lookup, window)
    ranked.to_csv(out_dir / "ranked_constraints.csv", index=False)

    base = constraints.base_case_binders(branch)
    base.to_csv(out_dir / "base_case_binders.csv", index=False)

    mu_frames = []
    for c in ranked[ranked["N_RUNS_BINDING"] > 0].head(args.top)["CONSTRAINT"]:
        mu_frames.append(
            marginal_units.marginal_units_for_constraint(ctgviol, gen, c, bus_names, genunit)
        )
    mu = pd.concat(mu_frames, ignore_index=True) if mu_frames else pd.DataFrame()
    mu.to_csv(out_dir / "marginal_units.csv", index=False)

    tf_sum.to_csv(out_dir / "tofinder_summary.csv", index=False)

    n_bind = (ranked["N_RUNS_BINDING"] > 0).sum()
    print(f"study {args.study}: {len(ranked):,} flagged constraints, {n_bind} ever binding")
    cols = ["CONSTRAINT", "FROMNAME", "TONAME", "N_RUNS_BINDING", "PCT_RUNS_BINDING",
            "MAX_PCT", "MEAN_EXCESS", "SCORE", "DRIVER_CLASS", "DRIVER_TICKET"]
    print(ranked[ranked["N_RUNS_BINDING"] > 0].head(args.top)[cols].to_string(index=False))
    print(f"\nbase-case binders (MARGCOSTMVA): {len(base)}")
    if len(base):
        print(base.head(10).to_string(index=False))
    print(f"\noutputs -> {out_dir}")


if __name__ == "__main__":
    main()
