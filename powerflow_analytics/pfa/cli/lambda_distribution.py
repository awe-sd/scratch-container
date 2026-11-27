"""Realistic shadow-price (lambda) DISTRIBUTION for a constraint, built from
the full DAM-offer relief set instead of a single redispatch pair.

Usage:
    uv run pfa lambda-dist \
        --study 14412 --constraint "1436-2081-1@DWCSRAM5"
"""
from __future__ import annotations

import argparse


import pandas as pd

from pfa.analysis import marginal_units, shadow_price as lam
from pfa.cache import StudyCache
from pfa.constraint_id import ConstraintId
from pfa.extract import fastscan, gen_mapping

DEPTH_CHECKPOINTS = (25, 50, 100, 200, 400)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--constraint", required=True)
    args = ap.parse_args(argv)

    cache = StudyCache(args.study)
    gen = cache.load("outgen2", columns=["BUSNUM", "ID", "FUELTYPE", "MW", "MWMAX"])
    branch = cache.load("outbranch2", columns=["FROMNUM", "FROMNAME", "TONUM", "TONAME"])
    genunit = cache.load("genunit")
    bus_names = marginal_units.bus_name_map(branch)
    scedname = gen_mapping.fetch_genunit_sced_name()

    print(f"Relief set for study {args.study}, constraint {args.constraint}")
    rs = lam.relief_set(args.study, args.constraint, gen, bus_names, genunit, scedname)
    relief, cap = rs.units, rs.capacity
    if relief.empty:
        print("  no relief-set units found (SF band empty or unmapped)")
        return

    if cap.empty:
        print("  no DAM offer/capacity data for mapped resources")
        return

    display = relief.merge(cap, left_on="SCED", right_index=True, how="left")
    print(display[["BUSNUM", "ID", "SIDE", "SF", "SCED", "IS_RENEWABLE",
                   "P60", "HSL", "AWARDED", "LSL"]].to_string(index=False))

    up, down = rs.up, rs.down
    print(f"\nUP stack: {len(up)} units, DOWN stack: {len(down)} units "
          f"({sum(1 for b in down if b['price'] == lam.CURTAIL_PRICE)} curtailment)")

    curve = rs.curve()
    print("\nlambda(depth):")
    for d in DEPTH_CHECKPOINTS:
        val = lam.lambda_at_depth(curve, d)
        print(f"  D={d:>4} MW  lambda={'n/a' if val is None else f'${val:,.1f}'}")

    cid = ConstraintId.parse(args.constraint)
    f, t, ctg = cid.fromnum, cid.tonum, cid.ctglabel
    configs = fastscan.find_configs(args.study, int(f), int(t), ctg)
    if configs.empty:
        print("\nno fast-scan config found for this constraint — skipping distribution")
        return
    config_id = int(configs.iloc[0]["CONFIG_ID"])
    need = lam.fastscan_need(config_id)
    if need.empty:
        print("\nfast-scan config has no negative-headroom hours — no distribution")
        return
    dist = lam.lambda_distribution(curve, need)
    cov = lam.coverage(dist, curve)
    print(f"\nrelief set exhausts at D={cov['exhaustion_depth_mw']} MW of flow "
          f"({sum(s['depth_hi'] - s['depth_lo'] for s in curve):.0f} MW of paired capacity)")
    print(f"of {cov['n_hours']} negative-headroom hours (config {config_id}): "
          f"{cov['n_priced']} priced by this relief set, "
          f"{cov['n_unpriceable']} need more relief than the set can supply")

    pct = lam.percentiles(dist["LAMBDA"])
    if pct:
        print(f"\nlambda distribution (priced hours only):")
        print(f"  P25={pct.get('P25')}  P50={pct.get('P50')}  P75={pct.get('P75')}  "
              f"P90={pct.get('P90')}  max={pct.get('max')}  n={pct.get('n')}")

    regime = fastscan.solar_impact(config_id)
    if not regime.empty:
        merged = dist.merge(regime, on="TIMESTAMP", how="left")
        solar_hrs = merged[merged["SOLAR_IMPACT"] > 1.0]
        dark_hrs = merged[merged["SOLAR_IMPACT"] <= 1.0]
        print("\nby solar regime (SOLAR_IMPACT > 1 MW = solar hour):")
        for label, sub in (("solar", solar_hrs), ("dark", dark_hrs)):
            p = lam.percentiles(sub["LAMBDA"])
            if p:
                print(f"  {label:>5}: P50=${p['P50']}  P90=${p['P90']}  n={p['n']}")
            else:
                print(f"  {label:>5}: no priced hours")

