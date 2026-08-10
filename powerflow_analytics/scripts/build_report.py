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
    ap.add_argument("--cutoff", default=None,
                    help="outage-season cutoff YYYY-MM-DD for rent split "
                         "(default: Sep 15 of the study's sim year — ERCOT allows outages after Sep 15)")
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

    outcon = cache.load("outconstraint2")
    cutoff = args.cutoff or f"{pd.to_datetime(runs['SIMDATE']).dt.year.mode().iloc[0]}-09-15"

    ranked = constraints.rank_constraints(ctgviol, runs)
    ranked = constraints.add_shadow_prices(ranked, outcon)
    rent = constraints.congestion_rent(ctgviol, outcon, runs, cutoff_date=cutoff)
    ranked = ranked.merge(rent, on="CONSTRAINT", how="left")
    ranked[["TOTAL_RENT", "RENT_PRE", "RENT_POST"]] = ranked[
        ["TOTAL_RENT", "RENT_PRE", "RENT_POST"]].fillna(0.0)
    # rank by congestion rent (lambda x limit summed over runs) — the CRR payout proxy
    ranked = ranked.sort_values("TOTAL_RENT", ascending=False).reset_index(drop=True)
    tf_sum = drivers.tofinder_summary(tofinder)

    ticket_lookup, window = None, None
    if args.tickets:
        from pfa.extract.outages import lookup_branch_tickets

        simdates = pd.to_datetime(runs["SIMDATE"])
        window = (str(simdates.min().date()), str(simdates.max().date()))
        ticket_lookup = lookup_branch_tickets

    ranked = drivers.classify_constraints(ranked, tf_sum, ticket_lookup, window,
                                          ticket_top_n=60, bus_names=bus_names)
    ranked.to_csv(out_dir / "ranked_constraints.csv", index=False)

    base = constraints.base_case_binders(branch)
    base.to_csv(out_dir / "base_case_binders.csv", index=False)

    mu_frames = []
    for c in ranked[(ranked["N_RUNS_BINDING"] > 0) & (ranked["TOTAL_RENT"] > 0)].head(args.top)["CONSTRAINT"]:
        mu_frames.append(
            marginal_units.marginal_units_for_constraint(ctgviol, gen, c, bus_names, genunit)
        )
    mu = pd.concat(mu_frames, ignore_index=True) if mu_frames else pd.DataFrame()
    mu.to_csv(out_dir / "marginal_units.csv", index=False)

    tf_sum.to_csv(out_dir / "tofinder_summary.csv", index=False)

    n_bind = (ranked["N_RUNS_BINDING"] > 0).sum()
    n_rent = (ranked["TOTAL_RENT"] > 0).sum()
    print(f"study {args.study}: {len(ranked):,} flagged constraints, {n_bind} ever binding, "
          f"{n_rent} with LP rent; cutoff {cutoff}")
    cols = ["CONSTRAINT", "FROMNAME", "TONAME", "TOTAL_RENT", "RENT_PRE", "RENT_POST",
            "POST_RENT_SHARE", "MEAN_SHADOW", "MAX_SHADOW", "N_RUNS_BINDING",
            "DRIVER_CLASS", "DRIVER_TICKET", "DRIVER_TICKET_STATUS"]
    print(ranked[ranked["TOTAL_RENT"] > 0].head(args.top)[cols].round(1).to_string(index=False))
    print(f"\nbase-case binders (MARGCOSTMVA): {len(base)}")
    if len(base):
        print(base.head(10).to_string(index=False))
    print(f"\noutputs -> {out_dir}")


if __name__ == "__main__":
    main()
