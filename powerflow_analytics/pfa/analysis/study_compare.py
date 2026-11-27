"""Cross-study constraint comparison data (e.g. 14411 vs 14412).

Study B typically adds implied/breaker outages. For every binding, LP-priced, non-penalty constraint:
  - PERSISTING: binds in both studies (confidence up - robust to topology set)
  - NEW in B: binds only with implied outages - no ticket to verify, so the evidence columns are
    fast-scan stress and path-opt cheap paths
  - DROPPED: binds in A only
Ranked by rent score (P50 $/MWh x limit MVA); 345 kV floats up on size.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from pfa import config
from pfa.analysis import valuation
from pfa.cache import StudyCache
from pfa.constraint_id import ConstraintId
from pfa.extract import fastscan, popt

MIN_BIND = 5  # lower than single-study report: catching movers matters more here


def study_frame(study_id: int, month: tuple[int, int]) -> pd.DataFrame:
    """Per-constraint valuation over the full study window."""
    cache = StudyCache(study_id)
    runs = cache.load("opfrun")
    outcon = cache.load("outconstraint2")
    ranked = pd.read_csv(config.OUTPUT_ROOT / f"study_{study_id}" / "ranked_constraints.csv")
    window = (str(pd.to_datetime(runs["SIMDATE"]).min().date()),
              str(pd.to_datetime(runs["SIMDATE"]).max().date()))
    short = ranked[(ranked["N_RUNS_BINDING"] >= MIN_BIND)
                   & (ranked["TOTAL_RENT"] > 0)].drop_duplicates("CONSTRAINT")
    rows = []
    for _, r in short.iterrows():
        stats = valuation.binding_stats(outcon, runs, r["CONSTRAINT"], window)
        lam = float(stats.lam["p50"].max()) if len(stats.lam) else 0.0
        if lam >= 500 or lam == 0.0:
            continue
        v = valuation.dollars_per_mwh(stats, *month, window, "p50")["dollars_per_mwh"]
        limit = float(r.get("LIMIT_MVA") or 0)
        rows.append({
            "CONSTRAINT": r["CONSTRAINT"], "FROMNAME": r["FROMNAME"], "TONAME": r["TONAME"],
            "KV345": limit >= 900 or str(r["FROMNAME"]).rstrip("AB").endswith("5"),
            "LIMIT_MVA": int(limit), "LAM_P50": round(lam, 1),
            "P_BIND_18": round(stats.p_bind.get(18, 0), 2),
            "USD_MWH_P50": v, "RENT_SCORE": round(v * limit / 1000, 1),
            "TOTAL_RENT": int(r["TOTAL_RENT"]), "N_RUNS_BINDING": int(r["N_RUNS_BINDING"]),
            "DRIVER": r.get("DRIVER_CLASS"), "TICKET": r.get("DRIVER_TICKET"),
            "TICKET_STATUS": r.get("DRIVER_TICKET_STATUS"),
        })
    return pd.DataFrame(rows)


def enrich_new(new: pd.DataFrame, study_b: int, top_new: int) -> pd.DataFrame:
    """Fast-scan stress + cheapest path-opt path for the top new constraints; a database error in one
    lookup becomes a visible 'lookup failed: ...' cell for that row, an empty result stays empty."""
    new["FASTSCAN_MAX_NEG"] = None
    new["BEST_PATH"] = None
    for i in new.index[:top_new]:
        c = new.loc[i, "CONSTRAINT"]
        cid = ConstraintId.parse(c)
        try:
            cfgs = fastscan.find_configs(study_b, int(cid.fromnum), int(cid.tonum), cid.ctglabel)
            if not cfgs.empty:
                prof = fastscan.headroom_profile(int(cfgs["CONFIG_ID"].iloc[0]))
                new.loc[i, "FASTSCAN_MAX_NEG"] = round(float(prof["PCT_NEG"].max()), 1)
        except Exception as e:
            new.loc[i, "FASTSCAN_MAX_NEG"] = f"lookup failed: {e}"
        try:
            paths = popt.best_paths(study_b, c)
            if paths is not None and len(paths):
                p = paths.iloc[0]
                new.loc[i, "BEST_PATH"] = (f"{p['SOURCENAME']}→{p['SINKNAME']} "
                                           f"${p['OPTIONPRICE']:.2f} @SF {p['AVG_SF']:.2f}")
        except Exception as e:
            new.loc[i, "BEST_PATH"] = f"lookup failed: {e}"
    return new


@dataclass
class Comparison:
    persist: pd.DataFrame
    new: pd.DataFrame
    dropped: pd.DataFrame


def compare_studies(study_a: int, study_b: int, month: tuple[int, int], top_new: int = 20) -> Comparison:
    """Persisting / new (enriched for the top `top_new`) / dropped constraints between two studies."""
    a = study_frame(study_a, month)
    b = study_frame(study_b, month)
    a_keys, b_keys = set(a["CONSTRAINT"]), set(b["CONSTRAINT"])
    persist = b[b["CONSTRAINT"].isin(a_keys)].merge(
        a[["CONSTRAINT", "USD_MWH_P50", "RENT_SCORE", "TICKET", "TICKET_STATUS", "DRIVER"]],
        on="CONSTRAINT", suffixes=("", "_A"))
    persist = persist.sort_values("RENT_SCORE", ascending=False)
    new = b[~b["CONSTRAINT"].isin(a_keys)].sort_values("RENT_SCORE", ascending=False)
    dropped = a[~a["CONSTRAINT"].isin(b_keys)].sort_values("RENT_SCORE", ascending=False)
    return Comparison(persist, enrich_new(new.reset_index(drop=True), study_b, top_new), dropped)
