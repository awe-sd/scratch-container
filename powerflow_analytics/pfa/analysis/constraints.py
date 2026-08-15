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
        MAX_PCT=("LIMVIOLPCT", "max"),
        MEAN_PCT=("LIMVIOLPCT", "mean"),
        MEAN_EXCESS=("excess", "mean"),
    ).reset_index()

    binding_runs = (
        df[df["binding"]].groupby(KEY, dropna=False)["RUNID"].nunique().rename("N_RUNS_BINDING")
    )
    out = out.merge(binding_runs, on=KEY, how="left")
    out["N_RUNS_BINDING"] = out["N_RUNS_BINDING"].fillna(0).astype(int)
    out["PCT_RUNS_BINDING"] = 100.0 * out["N_RUNS_BINDING"] / n_runs
    # transparent composite: how often it binds x how hard it binds when it does
    out["SCORE"] = out["N_RUNS_BINDING"] * (1.0 + out["MEAN_EXCESS"])
    out["CONSTRAINT"] = constraint_key(out)
    return out.sort_values(["SCORE", "N_RUNS_BINDING", "MAX_PCT"], ascending=False).reset_index(drop=True)


def add_shadow_prices(ranked: pd.DataFrame, outcon: pd.DataFrame) -> pd.DataFrame:
    """Join OUTCONSTRAINT2 LP shadow prices onto the ranked constraint table.

    OUTCONSTRAINT2 keys constraints by (FROMNUM, TONUM, CKT, LPOPFCTGID) where
    LPOPFCTGID is the contingency label; OPFCNLAMBDA is the shadow price and
    LPBASICVARID the marginal control variable (usually a gen).
    """
    oc = outcon.rename(columns={"LPOPFCTGID": "CTGLABEL"})
    oc["CONSTRAINT"] = constraint_key(oc)
    g = oc.groupby("CONSTRAINT")
    shadow = g.agg(
        N_RUNS_SHADOW=("RUNID", "nunique"),
        MEAN_SHADOW=("OPFCNLAMBDA", "mean"),
        MAX_SHADOW=("OPFCNLAMBDA", "max"),
        TOP_MARGINAL_VAR=("LPBASICVARID", lambda s: s.mode().iloc[0] if len(s.mode()) else None),
    ).reset_index()
    out = ranked.merge(shadow, on="CONSTRAINT", how="left")
    out["N_RUNS_SHADOW"] = out["N_RUNS_SHADOW"].fillna(0).astype(int)
    return out


def congestion_rent(
    ctgviol: pd.DataFrame,
    outcon: pd.DataFrame,
    runs: pd.DataFrame,
    cutoff_date: str | None = None,
) -> pd.DataFrame:
    """Per-constraint congestion rent: sum over runs of lambda x limit MW.

    Rent (lambda x binding flow, and binding flow ~= limit) is the CRR payout
    proxy — a constraint with a huge shadow price in two hours can matter less
    than a moderate one binding all month. cutoff_date (YYYY-MM-DD) splits the
    rent into RENT_PRE/RENT_POST (ERCOT allows outages after Sep 15, so
    post-cutoff congestion depends on outages that may still move or cancel).
    """
    oc = outcon.rename(columns={"LPOPFCTGID": "CTGLABEL"})
    oc["CONSTRAINT"] = constraint_key(oc)
    cv = ctgviol.copy()
    cv["CONSTRAINT"] = constraint_key(cv)
    limits_run = cv.groupby(["CONSTRAINT", "RUNID"])["LIMVIOLLIMIT"].median().rename("LIMIT_RUN")
    limits_all = cv.groupby("CONSTRAINT")["LIMVIOLLIMIT"].median().rename("LIMIT_ALL")

    r = oc.merge(limits_run, on=["CONSTRAINT", "RUNID"], how="left")
    r = r.merge(limits_all, on="CONSTRAINT", how="left")
    r["LIMIT_MW"] = r["LIMIT_RUN"].fillna(r["LIMIT_ALL"])
    r["RENT"] = r["OPFCNLAMBDA"] * r["LIMIT_MW"]

    r = r.merge(runs[["RUNID", "SIMDATE"]], on="RUNID", how="left")
    if cutoff_date is not None:
        post = pd.to_datetime(r["SIMDATE"]) >= pd.to_datetime(cutoff_date)
    else:
        post = pd.Series(False, index=r.index)
    r["RENT_PRE"] = r["RENT"].where(~post, 0.0)
    r["RENT_POST"] = r["RENT"].where(post, 0.0)

    out = r.groupby("CONSTRAINT").agg(
        TOTAL_RENT=("RENT", "sum"),
        RENT_PRE=("RENT_PRE", "sum"),
        RENT_POST=("RENT_POST", "sum"),
    ).reset_index()
    out["POST_RENT_SHARE"] = (out["RENT_POST"] / out["TOTAL_RENT"]).where(out["TOTAL_RENT"] > 0)
    return out


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
