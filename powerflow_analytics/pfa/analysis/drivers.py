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
    out["_impact"] = out["MEAN_FLOWDELTA"].abs()
    return out.sort_values(["CONSTRAINT", "_impact"], ascending=[True, False]).drop(columns="_impact")


def classify_constraints(
    ranked: pd.DataFrame,
    tofinder_sum: pd.DataFrame,
    ticket_lookup=None,
    window: tuple[str, str] | None = None,
    ticket_top_n: int = 25,
    bus_names: pd.DataFrame | None = None,
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
    ticket_cache: dict[int, pd.DataFrame] = {}
    rows = []
    for i, (_, r) in enumerate(ranked.iterrows()):
        c = r["CONSTRAINT"]
        cls, evidence, ticket, ticket_status = "baseline", None, None, None
        tk = {}
        if c in top.index:
            t = top.loc[c]
            frac = t["FLOW_FRAC"]
            if pd.notna(frac) and frac >= DRIVER_FLOWDELTA_FRAC:
                evidence = t["OUTAGE_GROUP"]
                cls = "topology-suspect"
                # SQL Server lookups only for the head of the ranking, memoized per branch
                if (ticket_lookup is not None and window is not None
                        and i < ticket_top_n and pd.notna(t["BRANCHID_OUTAGE"])):
                    bid = int(t["BRANCHID_OUTAGE"])
                    if bid not in ticket_cache:
                        from ..extract.outages import teid_for_branch, teids_for_endpoints

                        try:
                            teid = teid_for_branch(bid)
                        except Exception:
                            teid = None
                        found = ticket_lookup(bid, *window, teid=teid)
                        if not len(found) and teid is None and bus_names is not None:
                            # id not in the map (e.g. an internal winding):
                            # resolve via the outage's endpoint bus names
                            nm = bus_names.set_index("BUSNUM")["BUSNAME"]
                            names = [nm.get(int(t[k])) for k in
                                     ("FROMNUM_OUTAGE", "TONUM_OUTAGE") if pd.notna(t.get(k))]
                            for cand in teids_for_endpoints(names):
                                found = ticket_lookup(bid, *window, teid=cand)
                                if len(found):
                                    break
                        ticket_cache[bid] = found
                    tickets = ticket_cache[bid]
                    if len(tickets):
                        cls = "outage-driven"
                        t0 = tickets.iloc[0]
                        ticket = str(t0.get("outageIdentifier", ""))
                        status = t0.get("statusName")
                        ticket_status = str(status).strip() if pd.notna(status) else None
                        tk = {f"DRIVER_TICKET_{k}": t0.get(src) for k, src in [
                            ("CURRENT_STATUS", "currentStatusName"),
                            ("START", "currentStartDate"), ("END", "currentEndDate"),
                            ("CANCELLED", "cancellationDate"),
                            ("OC", "OC"), ("REV", "revNum"), ("REASON", "reasonName"),
                        ]}
                        # every ticket on the driving device, when there are several
                        tk["DRIVER_TICKETS_ALL"] = "; ".join(
                            f"{row.get('outageIdentifier')}"
                            f" ({str(row.get('statusName') or '').strip()}"
                            f"/{str(row.get('reasonName') or '?').strip()})"
                            for _, row in tickets.iterrows())
        rows.append({"CONSTRAINT": c, "DRIVER_CLASS": cls,
                     "DRIVER_OUTAGE_GROUP": evidence, "DRIVER_TICKET": ticket,
                     "DRIVER_TICKET_STATUS": ticket_status, **tk})
    return ranked.merge(pd.DataFrame(rows), on="CONSTRAINT", how="left")
