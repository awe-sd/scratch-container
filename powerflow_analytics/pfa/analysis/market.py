"""Market calibration: map study constraints to ISO constraints by ID and pull
realized DA/RT congestion history.

House method (sdalvi): study BRANCHID = CONGDEFMONITOR.BRANCHMONITOREDID
-> CONGMONTID; study BRANCHCONTINGENCYID = CONGDEFCONTINGENCY.BRANCHCONTINGENCYID
-> CONGCONTID; (CONGMONTID, CONGCONTID) -> CONGDEFCONSTRAINT.CONGCONSTRAINTID
-> CONGHRPRICE realized shadow prices. Never match by name.
"""
from __future__ import annotations

import pandas as pd

from .. import sf


def iso_constraint_ids(branch_id: int, branch_contingency_id: int) -> list[int]:
    """CONGCONSTRAINTIDs for one study (monitor, contingency) pair."""
    df = sf.query("AW", f"""
        SELECT DISTINCT cc.CONGCONSTRAINTID
        FROM AW.DBO.CONGDEFMONITOR m
        JOIN AW.DBO.CONGDEFCONSTRAINT cc ON cc.CONGMONTID = m.CONGMONTID
        JOIN AW.DBO.CONGDEFCONTINGENCY ct ON ct.CONGCONTID = cc.CONGCONTID
        WHERE m.BRANCHMONITOREDID = {int(branch_id)}
          AND ct.BRANCHCONTINGENCYID = {int(branch_contingency_id)}
        LIMIT 20""")
    return [int(x) for x in df["CONGCONSTRAINTID"]] if len(df) else []


def realized_history(cong_ids: list[int], start: str, price_type: int = 1) -> dict:
    """Binding hours and lambda stats since `start` (price_type 1=DA, 2=RT)."""
    if not cong_ids:
        return {}
    ids = ",".join(map(str, cong_ids))
    df = sf.query("AW", f"""
        SELECT COUNT(*) N_HOURS, AVG(p.PRICE) MEAN_LAM, MAX(p.PRICE) MAX_LAM,
               MEDIAN(p.PRICE) P50_LAM, MIN(d.DATE) FIRST_D, MAX(d.DATE) LAST_D
        FROM AW.DBO.CONGHRPRICE p JOIN AW.DBO.AWDATE d ON d.AWDATEID = p.AWDATEID
        WHERE p.CONGCONSTRAINTID IN ({ids}) AND p.PRICE <> 0
          AND p.PRICETYPEID = {int(price_type)} AND d.DATE >= '{start}'""")
    r = df.iloc[0]
    if not r["N_HOURS"]:
        return {}
    return {"n_hours": int(r["N_HOURS"]), "mean": round(float(r["MEAN_LAM"]), 1),
            "p50": round(float(r["P50_LAM"]), 1), "max": round(float(r["MAX_LAM"]), 1),
            "first": str(r["FIRST_D"]), "last": str(r["LAST_D"])}


def implied_outage_check(branch_df: pd.DataFrame, runs: pd.DataFrame,
                         fromnum: int, tonum: int, ckt: str, cutoff: str) -> str | None:
    """Verify an implied (breaker) outage from the study itself: the driving
    line is Closed in pre-cutoff runs and Open after. Returns
    'implied-verified' / 'implied-partial' / None (line status unchanged)."""
    b = branch_df[(branch_df["FROMNUM"] == fromnum) & (branch_df["TONUM"] == tonum)
                  & (branch_df["CKT"].astype(str).str.strip() == str(ckt).strip())]
    if b.empty or "LINESTATUS" not in b.columns:
        return None
    b = b.merge(runs[["RUNID", "SIMDATE"]], on="RUNID")
    post = pd.to_datetime(b["SIMDATE"]) >= pd.to_datetime(cutoff)
    pre_open = (b.loc[~post, "LINESTATUS"].astype(str).str.strip() == "Open").mean() if (~post).any() else None
    post_open = (b.loc[post, "LINESTATUS"].astype(str).str.strip() == "Open").mean() if post.any() else None
    if pre_open is None or post_open is None:
        return None
    if pre_open < 0.05 and post_open > 0.95:
        return "implied-verified"
    if post_open - pre_open > 0.3:
        return "implied-partial"
    return None
