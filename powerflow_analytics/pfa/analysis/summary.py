"""Study summary: ranked binding constraints with rent, drivers, base-case binders and marginal units."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from pfa.analysis import constraints, drivers, marginal_units
from pfa.cache import StudyCache


@dataclass
class StudySummary:
    ranked: pd.DataFrame
    base: pd.DataFrame
    marginal_units: pd.DataFrame
    tofinder: pd.DataFrame


def summarize_study(study: int, cutoff: str, top: int, tickets: bool) -> StudySummary:
    cache = StudyCache(study)
    runs = cache.load("opfrun")
    ctgviol = cache.load("outctgviol2")
    gen = cache.load("outgen2")
    tofinder = cache.load("outtofindermax2")
    branch = cache.load("outbranch2")
    genunit = cache.load("genunit")
    bus_names = marginal_units.bus_name_map(branch)
    outcon = cache.load("outconstraint2")

    ranked = constraints.rank_constraints(ctgviol, runs)
    ranked = constraints.add_shadow_prices(ranked, outcon)
    rent = constraints.congestion_rent(ctgviol, outcon, runs, cutoff_date=cutoff)
    ranked = ranked.merge(rent, on="CONSTRAINT", how="left")
    ranked[["TOTAL_RENT", "RENT_PRE", "RENT_POST"]] = ranked[["TOTAL_RENT", "RENT_PRE", "RENT_POST"]].fillna(0.0)
    ranked = ranked.sort_values("TOTAL_RENT", ascending=False).reset_index(drop=True)
    tf_sum = drivers.tofinder_summary(tofinder)

    ticket_lookup, window = None, None
    if tickets:
        from pfa.extract.outages import lookup_branch_tickets

        simdates = pd.to_datetime(runs["SIMDATE"])
        window = (str(simdates.min().date()), str(simdates.max().date()))
        ticket_lookup = lookup_branch_tickets

    ranked = drivers.classify_constraints(ranked, tf_sum, ticket_lookup, window, ticket_top_n=60, bus_names=bus_names)
    base = constraints.base_case_binders(branch)
    mu_frames = [marginal_units.marginal_units_for_constraint(ctgviol, gen, c, bus_names, genunit)
                 for c in ranked[(ranked["N_RUNS_BINDING"] > 0) & (ranked["TOTAL_RENT"] > 0)].head(top)["CONSTRAINT"]]
    mu = pd.concat(mu_frames, ignore_index=True) if mu_frames else pd.DataFrame()
    return StudySummary(ranked, base, mu, tf_sum)
