"""Binding-constraint identification and ranking.

A constraint is (FROMNUM, TONUM, CKT, CTGLABEL): a monitored branch under a
contingency. OUTCTGVIOL2 reports post-contingency loading (LIMVIOLPCT) for
flagged constraints; in SCOPF a constraint held at its limit sits at ~100%,
so LIMVIOLPCT >= BINDING_PCT counts as binding. Rows above 100 are unresolved
violations. Base-case binders come from OUTBRANCH2.MARGCOSTMVA (populated only
where the branch is pinned at 100% pre-contingency).
"""
from __future__ import annotations

import pandas as pd

BINDING_PCT = 99.5
KEY = ["FROMNUM", "TONUM", "CKT", "CTGLABEL"]


def constraint_key(df: pd.DataFrame) -> pd.Series:
    return (
        df["FROMNUM"].astype(int).astype(str)
        + "-" + df["TONUM"].astype(int).astype(str)
        + "-" + df["CKT"].astype(str).str.strip()
        + "@" + df["CTGLABEL"].astype(str).str.strip()
    )


def rank_constraints(ctgviol: pd.DataFrame, runs: pd.DataFrame) -> pd.DataFrame:
    """One row per constraint with binding frequency and severity metrics."""
    n_runs = runs["RUNID"].nunique()
    df = ctgviol.copy()
    df["binding"] = df["LIMVIOLPCT"] >= BINDING_PCT
    df["excess"] = (df["LIMVIOLPCT"] - 100.0).clip(lower=0)

    g = df.groupby(KEY, dropna=False)
    out = g.agg(
        FROMNAME=("FROMNAME", "first"),
        TONAME=("TONAME", "first"),
        BRANCHNAME=("BRANCHNAME", "first"),
        BRANCHID=("BRANCHID", "first"),
        LIMIT_MVA=("LIMVIOLLIMIT", "median"),
        N_RUNS_FLAGGED=("RUNID", "nunique"),
        N_RUNS_BINDING=("RUNID", lambda s: 0),  # replaced below
        MAX_PCT=("LIMVIOLPCT", "max"),
        MEAN_PCT=("LIMVIOLPCT", "mean"),
        MEAN_EXCESS=("excess", "mean"),
    ).reset_index()

    binding_runs = (
        df[df["binding"]].groupby(KEY, dropna=False)["RUNID"].nunique().rename("N_RUNS_BINDING")
    )
    out = out.drop(columns=["N_RUNS_BINDING"]).merge(binding_runs, on=KEY, how="left")
    out["N_RUNS_BINDING"] = out["N_RUNS_BINDING"].fillna(0).astype(int)
    out["PCT_RUNS_BINDING"] = 100.0 * out["N_RUNS_BINDING"] / n_runs
    # transparent composite: how often it binds x how hard it binds when it does
    out["SCORE"] = out["N_RUNS_BINDING"] * (1.0 + out["MEAN_EXCESS"])
    out["CONSTRAINT"] = constraint_key(out)
    return out.sort_values(["SCORE", "N_RUNS_BINDING", "MAX_PCT"], ascending=False).reset_index(drop=True)


def binding_hours(ctgviol: pd.DataFrame, runs: pd.DataFrame) -> pd.DataFrame:
    """Per-constraint binding profile by SIMDATE/SIMHOUR (for drill-down plots)."""
    df = ctgviol[ctgviol["LIMVIOLPCT"] >= BINDING_PCT].merge(
        runs[["RUNID", "SIMDATE", "SIMHOUR"]], on="RUNID", how="left"
    )
    df["CONSTRAINT"] = constraint_key(df)
    return df[["CONSTRAINT", "RUNID", "SIMDATE", "SIMHOUR", "LIMVIOLPCT"]]


def base_case_binders(branch: pd.DataFrame) -> pd.DataFrame:
    """Branches pinned at their normal limit pre-contingency (MARGCOSTMVA set)."""
    df = branch[branch["MARGCOSTMVA"].notna()].copy()
    if df.empty:
        return df
    g = df.groupby(["FROMNUM", "TONUM", "CKT"], dropna=False)
    return g.agg(
        LABEL=("LABEL", "first"),
        FROMNAME=("FROMNAME", "first"),
        TONAME=("TONAME", "first"),
        N_RUNS_BINDING=("RUNID", "nunique"),
        MEAN_SHADOW=("MARGCOSTMVA", "mean"),
        MAX_SHADOW=("MARGCOSTMVA", "max"),
    ).reset_index().sort_values("MEAN_SHADOW", ascending=False)
