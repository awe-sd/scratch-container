"""Which units resolve each binding constraint.

Fallback method (shift-factor views not yet authorized): for a constraint's
binding runs vs. non-binding runs, compare each unit's SCOPF redispatch
(LPDELTAMW). Units whose redispatch systematically moves when the constraint
binds are the ones the OPF leans on — the marginal units. Once
SHIFT_FACTORS views open up, the differential redispatch gets weighted by the
unit's shift factor on the constraint to remove cross-constraint bleed.
"""
from __future__ import annotations

import pandas as pd

from .constraints import BINDING_PCT, constraint_key


def bus_name_map(branch: pd.DataFrame) -> pd.DataFrame:
    """BUSNUM -> bus name, harvested from OUTBRANCH2 endpoints."""
    f = branch[["FROMNUM", "FROMNAME"]].rename(columns={"FROMNUM": "BUSNUM", "FROMNAME": "BUSNAME"})
    t = branch[["TONUM", "TONAME"]].rename(columns={"TONUM": "BUSNUM", "TONAME": "BUSNAME"})
    return pd.concat([f, t]).dropna().drop_duplicates("BUSNUM")


def marginal_units_for_constraint(
    ctgviol: pd.DataFrame,
    gen: pd.DataFrame,
    constraint: str,
    bus_names: pd.DataFrame | None = None,
    genunit: pd.DataFrame | None = None,
    top_n: int = 20,
) -> pd.DataFrame:
    """Rank units by differential redispatch for one constraint key string."""
    cv = ctgviol.copy()
    cv["CONSTRAINT"] = constraint_key(cv)
    binding_runs = set(
        cv[(cv["CONSTRAINT"] == constraint) & (cv["LIMVIOLPCT"] >= BINDING_PCT)]["RUNID"]
    )
    if not binding_runs:
        raise ValueError(f"constraint {constraint!r} has no binding runs")

    # GENSTATUS is uniformly 0 in current studies — not a usable online flag.
    # Units that never move (LPDELTAMW always 0) drop out via DIFF_MW ranking.
    g = gen.copy()
    g["is_binding_run"] = g["RUNID"].isin(binding_runs)

    piv = g.groupby(["BUSNUM", "ID", "is_binding_run"])["LPDELTAMW"].mean().unstack()
    piv = piv.rename(columns={True: "LPDELTA_BINDING", False: "LPDELTA_OTHER"}).reset_index()
    for c in ["LPDELTA_BINDING", "LPDELTA_OTHER"]:
        if c not in piv.columns:
            piv[c] = 0.0
    piv = piv.fillna({"LPDELTA_BINDING": 0.0, "LPDELTA_OTHER": 0.0})
    piv["DIFF_MW"] = piv["LPDELTA_BINDING"] - piv["LPDELTA_OTHER"]

    meta = g.groupby(["BUSNUM", "ID"]).agg(
        LABEL=("LABEL", "first"), FUELTYPE=("FUELTYPE", "first"),
        UNITTYPE=("UNITTYPE", "first"), ZONENAME=("ZONENAME", "first"),
        MEAN_MW=("MW", "mean"), MWMAX=("MWMAX", "max"),
    ).reset_index()
    out = piv.merge(meta, on=["BUSNUM", "ID"], how="left")

    if bus_names is not None:
        out = out.merge(bus_names, on="BUSNUM", how="left")
    if genunit is not None:
        # OUTGENREF has no rows for current ERCOT studies; LABEL -> UNITCODE is the
        # only direct bridge into the gen master, populated for ~12% of units.
        bridge = genunit[["UNITCODE", "GENUNITID", "UNITNAME", "RESOURCE_TYPE"]].dropna(
            subset=["UNITCODE"]
        ).drop_duplicates("UNITCODE")
        out = out.merge(bridge, left_on="LABEL", right_on="UNITCODE", how="left").drop(
            columns="UNITCODE"
        )

    out["ABS_DIFF"] = out["DIFF_MW"].abs()
    out = out.sort_values("ABS_DIFF", ascending=False).drop(columns="ABS_DIFF")
    out.insert(0, "CONSTRAINT", constraint)
    out.insert(1, "N_BINDING_RUNS", len(binding_runs))
    return out.head(top_n).reset_index(drop=True)
