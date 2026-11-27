"""Historical realized congestion lookup for a monitored element, independent of
contingency label.

House method (sdalvi): CONGDEFMONITOR carries the monitored branch's readable
name (CONGMONTNAME) plus FROMSTATION/TOSTATION and BRANCHMONITOREDID (which,
for ERCOT, equals the study's branch teid). CONGDEFCONSTRAINT joins a monitor
to every (contingency) constraint definition ever created for it; CONGHRPRICE
carries the realized DA/RT shadow price per hour. A monitored element can pick
up several CONGMONTID rows over time (re-created defs, alternate contingency
tags on the same line) -- this function unions all of them so "has this ever
bound" isn't understated by matching a single stale CONGMONTID.

Do not match by study CTGLABEL text against ISO contingency naming -- they use
unrelated vocabularies. Match on the monitored element (name/station ILIKE),
optionally narrowed by an ILIKE filter on the *ISO* contingency name.
"""
from __future__ import annotations

import pandas as pd

from .. import sf


def find_monitors(monitored_like: str) -> pd.DataFrame:
    """CONGDEFMONITOR rows (ISOMARKETID=6) whose name/station text matches."""
    df = sf.query("AW", f"""
        SELECT CONGMONTID, CONGMONTNAME, BRANCHMONITOREDID, FROMSTATION, FROMKV,
               TOSTATION, TOKV, INSERTDATE
        FROM AW.DBO.CONGDEFMONITOR
        WHERE ISOMARKETID = 6
          AND (CONGMONTNAME ILIKE {sf.quote(monitored_like)}
               OR FROMSTATION ILIKE {sf.quote(monitored_like)}
               OR TOSTATION ILIKE {sf.quote(monitored_like)})
        ORDER BY CONGMONTID
    """)
    return df


def lookup_constraint_history(
    monitored_like: str,
    contingency_like: str | None = None,
    start: str | None = None,
    end: str | None = None,
    price_type: int = 1,
) -> pd.DataFrame:
    """Monthly realized-congestion history for a monitored element.

    monitored_like: SQL ILIKE pattern against CONGDEFMONITOR.CONGMONTNAME /
        FROMSTATION / TOSTATION (e.g. '%SARDIS%', 'SARDIS%STERT%').
    contingency_like: optional ILIKE pattern against CONGDEFCONTINGENCY's
        contingency label column; None = any contingency (recommended default
        per the house method -- a monitored element that binds under a
        different contingency than the one a study flagged still counts as
        "has bound before").
    start/end: 'YYYY-MM-DD' bounds on AWDATE.DATE; either may be None.
    price_type: CONGHRPRICE.PRICETYPEID (1=DA, 2=RT).

    Returns one row per (CONGMONTID, month) with hours bound, mean/max shadow
    price, and the list of contingencies observed that month. Aggregation is
    done server-side (GROUP BY in Snowflake); only the aggregated rows come
    back into pandas.
    """
    mon = find_monitors(monitored_like)
    if mon.empty:
        return pd.DataFrame(columns=[
            "CONGMONTID", "CONGMONTNAME", "MONTH", "N_HOURS", "MEAN_PRICE",
            "MAX_PRICE", "CONTINGENCIES",
        ])
    mont_ids = ",".join(str(int(x)) for x in mon["CONGMONTID"])

    ctg_filter = ""
    if contingency_like:
        ctg_filter = f"AND ct.CONGCONTNAME ILIKE {sf.quote(contingency_like)}"

    date_filter = ""
    if start:
        date_filter += f" AND d.DATE >= '{start}'"
    if end:
        date_filter += f" AND d.DATE < '{end}'"

    sql = f"""
        SELECT
            m.CONGMONTID,
            m.CONGMONTNAME,
            DATE_TRUNC('month', d.DATE) AS MONTH,
            COUNT(*) AS N_HOURS,
            AVG(p.PRICE) AS MEAN_PRICE,
            MAX(p.PRICE) AS MAX_PRICE,
            ARRAY_AGG(DISTINCT ct.CONGCONTNAME) AS CONTINGENCIES
        FROM AW.DBO.CONGDEFMONITOR m
        JOIN AW.DBO.CONGDEFCONSTRAINT cc ON cc.CONGMONTID = m.CONGMONTID
        JOIN AW.DBO.CONGDEFCONTINGENCY ct ON ct.CONGCONTID = cc.CONGCONTID
        JOIN AW.DBO.CONGHRPRICE p ON p.CONGCONSTRAINTID = cc.CONGCONSTRAINTID
        JOIN AW.DBO.AWDATE d ON d.AWDATEID = p.AWDATEID
        WHERE m.CONGMONTID IN ({mont_ids})
          AND p.PRICE <> 0
          AND p.PRICETYPEID = {int(price_type)}
          {ctg_filter}
          {date_filter}
        GROUP BY m.CONGMONTID, m.CONGMONTNAME, DATE_TRUNC('month', d.DATE)
        ORDER BY MONTH
    """
    df = sf.query("AW", sql)
    if not df.empty:
        df["MEAN_PRICE"] = df["MEAN_PRICE"].round(2)
        df["MAX_PRICE"] = df["MAX_PRICE"].round(2)
    return df
