"""Why does the constraint bind — outage-driven, topology-suspect, or baseline.

OUTTOFINDERMAX2 ranks, per (target constraint, run), the outage groups whose
removal changes flow on the target most (FLOWDELTA). Constraints whose flow is
mostly created by a modeled outage are then verified against real outage
tickets (AW.dbo.toAllIsos, targeted lookups only):
  outage-driven    — big tofinder impact and a matching ticket in the window
  topology-suspect — big tofinder impact but no ticket found (model artifact?)
  baseline         — no material tofinder impact
"""
from __future__ import annotations

import pandas as pd

from .constraints import constraint_key

# share of pre-outage flow that must come from an outage group to call it a driver
DRIVER_FLOWDELTA_FRAC = 0.25


def tofinder_summary(tofinder: pd.DataFrame) -> pd.DataFrame:
    """Per (constraint, outage group): impact stats across runs."""
    df = tofinder.copy()
    df = df.rename(columns={
        "FROMNUM_TARGET": "FROMNUM", "TONUM_TARGET": "TONUM", "CKT_TARGET": "CKT",
    })
    df["CONSTRAINT"] = constraint_key(df)
    g = df.groupby(["CONSTRAINT", "OUTAGE_GROUP_ID"], dropna=False)
    out = g.agg(
        OUTAGE_GROUP=("OUTAGE_GROUP", "first"),
        OUTBRANCHLABEL=("OUTBRANCHLABEL", "first"),
        BRANCHID_OUTAGE=("BRANCHID_OUTAGE", "first"),
        FROMNUM_OUTAGE=("FROMNUM_OUTAGE", "first"),
        TONUM_OUTAGE=("TONUM_OUTAGE", "first"),
        CKT_OUTAGE=("CKT_OUTAGE", "first"),
        N_RUNS=("RUNID", "nunique"),
        MEAN_FLOWDELTA=("FLOWDELTA", "mean"),
        MAX_FLOWDELTA=("FLOWDELTA", "max"),
        MEAN_PREFLOW=("PREGROUPOUTLINEFLOW", "mean"),
    ).reset_index()
    out["FLOW_FRAC"] = (out["MEAN_FLOWDELTA"].abs() / out["MEAN_PREFLOW"].abs()).where(
        out["MEAN_PREFLOW"].abs() > 1e-6
    )
    return out.sort_values(["CONSTRAINT", "MEAN_FLOWDELTA"], key=abs, ascending=False)


def classify_constraints(
    ranked: pd.DataFrame,
    tofinder_sum: pd.DataFrame,
    ticket_lookup=None,
    window: tuple[str, str] | None = None,
) -> pd.DataFrame:
    """Attach DRIVER_CLASS + top outage evidence to the ranked constraint table.

    ticket_lookup(branch_id, start, end) -> DataFrame of tickets; pass
    pfa.extract.outages.lookup_branch_tickets to enable ticket verification
    (None keeps classification purely topological: outage-impact vs baseline).
    """
    top = (
        tofinder_sum.reindex(tofinder_sum["MEAN_FLOWDELTA"].abs().sort_values(ascending=False).index)
        .drop_duplicates("CONSTRAINT")
        .set_index("CONSTRAINT")
    )
    rows = []
    for _, r in ranked.iterrows():
        c = r["CONSTRAINT"]
        cls, evidence, ticket = "baseline", None, None
        if c in top.index:
            t = top.loc[c]
            frac = t["FLOW_FRAC"]
            if pd.notna(frac) and frac >= DRIVER_FLOWDELTA_FRAC:
                evidence = t["OUTAGE_GROUP"]
                cls = "topology-suspect"
                if ticket_lookup is not None and window is not None and pd.notna(t["BRANCHID_OUTAGE"]):
                    tickets = ticket_lookup(int(t["BRANCHID_OUTAGE"]), *window)
                    if len(tickets):
                        cls = "outage-driven"
                        ticket = str(tickets.iloc[0].get("outageIdentifier", ""))
        rows.append({"CONSTRAINT": c, "DRIVER_CLASS": cls,
                     "DRIVER_OUTAGE_GROUP": evidence, "DRIVER_TICKET": ticket})
    return ranked.merge(pd.DataFrame(rows), on="CONSTRAINT", how="left")
