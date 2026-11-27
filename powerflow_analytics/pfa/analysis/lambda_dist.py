"""Shadow-price (lambda) distribution for one constraint from the full DAM-offer relief set and fast-scan headroom."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from pfa.analysis import marginal_units, shadow_price as lam
from pfa.cache import StudyCache
from pfa.constraint_id import ConstraintId
from pfa.extract import fastscan, gen_mapping

DEPTH_CHECKPOINTS = (25, 50, 100, 200, 400)


@dataclass
class LambdaDist:
    study: int
    constraint: str
    stage: str = "relief"           # relief | offers | no_config | no_need | done  (where the analysis stopped)
    display: pd.DataFrame | None = None
    n_up: int = 0
    n_down: int = 0
    n_curtail: int = 0
    checkpoints: list = field(default_factory=list)   # (depth MW, lambda or None)
    config_id: int | None = None
    paired_mw: float = 0.0
    cov: dict | None = None
    pct: dict | None = None
    regimes: list | None = None     # (label, percentiles or None) per solar regime


def analyze(study: int, constraint: str) -> LambdaDist:
    cache = StudyCache(study)
    gen = cache.load("outgen2", columns=["BUSNUM", "ID", "FUELTYPE", "MW", "MWMAX"])
    branch = cache.load("outbranch2", columns=["FROMNUM", "FROMNAME", "TONUM", "TONAME"])
    genunit = gen_mapping.with_cpnode_names(cache.load("genunit"))
    bus_names = marginal_units.bus_name_map(branch)
    scedname = gen_mapping.fetch_genunit_sced_name()

    r = LambdaDist(study, constraint)
    rs = lam.relief_set(study, constraint, gen, bus_names, genunit, scedname)
    relief, cap = rs.units, rs.capacity
    if relief.empty:
        return r
    if cap.empty:
        r.stage = "offers"
        return r
    r.display = relief.merge(cap, left_on="SCED", right_index=True, how="left")
    up, down = rs.up, rs.down
    r.n_up, r.n_down = len(up), len(down)
    r.n_curtail = sum(1 for b in down if b["price"] == lam.CURTAIL_PRICE)
    curve = rs.curve()
    r.checkpoints = [(d, lam.lambda_at_depth(curve, d)) for d in DEPTH_CHECKPOINTS]

    cid = ConstraintId.parse(constraint)
    configs = fastscan.find_configs(study, int(cid.fromnum), int(cid.tonum), cid.ctglabel)
    if configs.empty:
        r.stage = "no_config"
        return r
    r.config_id = int(configs.iloc[0]["CONFIG_ID"])
    need = lam.fastscan_need(r.config_id)
    if need.empty:
        r.stage = "no_need"
        return r
    dist = lam.lambda_distribution(curve, need)
    r.cov = lam.coverage(dist, curve)
    r.paired_mw = sum(s["depth_hi"] - s["depth_lo"] for s in curve)
    r.pct = lam.percentiles(dist["LAMBDA"])
    regime = fastscan.solar_impact(r.config_id)
    if not regime.empty:
        merged = dist.merge(regime, on="TIMESTAMP", how="left")
        r.regimes = [(label, lam.percentiles(sub["LAMBDA"])) for label, sub in
                     (("solar", merged[merged["SOLAR_IMPACT"] > 1.0]), ("dark", merged[merged["SOLAR_IMPACT"] <= 1.0]))]
    r.stage = "done"
    return r
