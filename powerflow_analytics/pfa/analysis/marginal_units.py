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


def marginal_units_for_constraint(
    ctgviol: pd.DataFrame,
    gen: pd.DataFrame,
    constraint: str,
    genref: pd.DataFrame | None = None,
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

    g = gen[gen["GENSTATUS"].astype(str).str.lower().isin(["closed", "1", "true", "on"])
            | gen["GENSTATUS"].isna()].copy()
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

    if genref is not None:
        out = out.merge(
            genref[["BUSNUM", "ID", "GENUNITID"]].drop_duplicates(["BUSNUM", "ID"]),
            on=["BUSNUM", "ID"], how="left",
        )
        if genunit is not None:
            out = out.merge(
                genunit[["GENUNITID", "UNITNAME", "BUSNAME", "RESOURCE_TYPE"]],
                on="GENUNITID", how="left",
            )

    out["ABS_DIFF"] = out["DIFF_MW"].abs()
    out = out.sort_values("ABS_DIFF", ascending=False).drop(columns="ABS_DIFF")
    out.insert(0, "CONSTRAINT", constraint)
    out.insert(1, "N_BINDING_RUNS", len(binding_runs))
    return out.head(top_n).reset_index(drop=True)
