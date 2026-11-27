"""ERCOT DAM gen-resource energy offer curves (AW.DBO.ERCOT60DDAMGENRESOURCE).

The 60-day disclosure carries one row per (resource GENID, delivery date, hour
ending) with up to 10 (MW, price) offer-segment pairs stored WIDE
(CURVEMW1/CURVEPRICE1 .. CURVEMW10/CURVEPRICE10). `AW.DBO.ERCOTDAMPSSEGNTIMESERIES`
was inspected and does NOT carry offer segments — it is an in-service flag
table (AWDATEID, HE, ERCOTDAMPSSEGENID, PSSEBUSNUMBER, PSSEGENID, INSERVICE),
so this module reads ERCOT60DDAMGENRESOURCE only.

Resource identity: GENID is the correct join key into ERCOT60DDAMGENRESOURCE,
but it is not itself a resource name. Resource names live in
AW.DBO.ERCOT60DDAMGEN (GENID, RESOURCENAME, RESOURCETYPE) — resolve GENIDs
there first via RESOURCENAME ILIKE '<pattern>', then join those GENIDs into
ERCOT60DDAMGENRESOURCE. Naming does not always match plant colloquial names —
e.g. the Forney Energy Center's confirmed resource code is FRNYPP (pattern
'FRNYPP%'), which resolves to 12 CCGT90 GENIDs
(81,366,386,573,574,1367,1567,1761,1762,1971,2140,2160).
"""
from __future__ import annotations

import re
from datetime import date
from typing import Iterable, Optional

import pandas as pd

from .. import sf

_SEGMENTS = range(1, 11)

CAPACITY_ROW_LIMIT = 200000
_CURVE_COLS = ",".join(f"CURVEMW{i},CURVEPRICE{i}" for i in _SEGMENTS)

_CURVE_COLUMNS = ["RESOURCE", "DELIVERYDATE", "HOURENDING", "SEGMENT", "MW", "PRICE"]
_SUMMARY_COLUMNS = [
    "RESOURCE",
    "MONTH",
    "SEGMENT",
    "MEDIAN_PRICE",
    "P25_PRICE",
    "P75_PRICE",
    "AVG_MW",
    "N_OBS",
]


def _resolve_genids(resource_like: str) -> list[int]:
    """Look up GENID(s) for a resource name pattern (SQL ILIKE, e.g. 'FRNYPP%').

    Resource names live in AW.DBO.ERCOT60DDAMGEN, not on ERCOT60DDAMGENRESOURCE
    directly. Returns an empty list if no resource matches.
    """
    sql = f"""
        SELECT DISTINCT GENID, RESOURCENAME
        FROM AW.DBO.ERCOT60DDAMGEN
        WHERE RESOURCENAME ILIKE {sf.quote(resource_like)}
    """
    df = sf.query("AW", sql)
    df.columns = [c.upper() for c in df.columns]
    if df.empty:
        return []
    return sorted(int(g) for g in df["GENID"].tolist())


def _resource_names(genids: Iterable[int]) -> dict[int, str]:
    """GENID -> RESOURCENAME map, for attaching a readable column post-aggregation."""
    genids = list(genids)
    if not genids:
        return {}
    genid_list = ",".join(str(g) for g in genids)
    sql = f"""
        SELECT DISTINCT GENID, RESOURCENAME
        FROM AW.DBO.ERCOT60DDAMGEN
        WHERE GENID IN ({genid_list})
    """
    df = sf.query("AW", sql)
    df.columns = [c.upper() for c in df.columns]
    return dict(zip(df["GENID"], df["RESOURCENAME"]))


def _offer_data_exists(
    genids: Iterable[int],
    start: Optional[date] = None,
    end: Optional[date] = None,
) -> tuple[bool, Optional[tuple[str, str]]]:
    """Cheap existence/date-range check before pulling curves for `genids`.

    Returns (exists_in_window, (min_date, max_date) or None). The date range
    reflects whatever filter is applied (window if given, else all data for
    these GENIDs) -- callers use this to report the true available range when
    a requested window comes back empty (60-day disclosure lag).
    """
    genids = list(genids)
    if not genids:
        return False, None
    genid_list = ",".join(str(g) for g in genids)
    date_filter = ""
    if start is not None:
        date_filter += f" AND DELIVERYDATE >= '{start}'"
    if end is not None:
        date_filter += f" AND DELIVERYDATE < '{end}'"
    sql = f"""
        SELECT COUNT(*) AS N, MIN(DELIVERYDATE) AS MINDATE, MAX(DELIVERYDATE) AS MAXDATE
        FROM AW.DBO.ERCOT60DDAMGENRESOURCE
        WHERE GENID IN ({genid_list}) {date_filter}
    """
    df = sf.query("AW", sql)
    df.columns = [c.upper() for c in df.columns]
    n = int(df["N"].iloc[0])
    if n == 0:
        return False, None
    return True, (str(df["MINDATE"].iloc[0]), str(df["MAXDATE"].iloc[0]))


def _warn_no_data(resource_like: str, genids: list[int], start: date, end: date) -> None:
    if not genids:
        print(
            f"WARNING: dam_offers: no GENIDs matched RESOURCENAME ILIKE '{resource_like}' "
            f"in AW.DBO.ERCOT60DDAMGEN."
        )
        return
    exists_any, date_range = _offer_data_exists(genids)
    if exists_any:
        print(
            f"WARNING: dam_offers: no offer rows for GENIDs {genids} in window "
            f"[{start}, {end}); actual available range for these GENIDs is "
            f"{date_range[0]} to {date_range[1]}."
        )
    else:
        print(
            f"WARNING: dam_offers: no offer rows exist at all for GENIDs {genids} "
            f"(resolved from '{resource_like}')."
        )


def get_offer_curves(resource_like: str, start: date, end: date) -> pd.DataFrame:
    """Per resource x delivery date/hour x segment: MW, price.

    `resource_like` is an ILIKE pattern matched against RESOURCENAME in
    AW.DBO.ERCOT60DDAMGEN (e.g. 'FRNYPP%'). GENIDs resolved there are then
    joined into ERCOT60DDAMGENRESOURCE. Unpivots the wide CURVEMW/CURVEPRICE
    columns server-side via UNION ALL so the result comes back already in
    long form.
    """
    genids = _resolve_genids(resource_like)
    exists, _ = _offer_data_exists(genids, start, end) if genids else (False, None)
    if not exists:
        _warn_no_data(resource_like, genids, start, end)
        return pd.DataFrame(columns=_CURVE_COLUMNS)

    genid_list = ",".join(str(g) for g in genids)
    unions = "\nUNION ALL\n".join(
        f"""SELECT GENID, DELIVERYDATE, HOURENDING,
                   {i} AS SEGMENT, CURVEMW{i} AS MW, CURVEPRICE{i} AS PRICE
            FROM AW.DBO.ERCOT60DDAMGENRESOURCE
            WHERE GENID IN ({genid_list})
              AND DELIVERYDATE >= '{start}' AND DELIVERYDATE < '{end}'
              AND CURVEMW{i} IS NOT NULL"""
        for i in _SEGMENTS
    )
    df = sf.query("AW", unions + "\nORDER BY GENID, DELIVERYDATE, HOURENDING, SEGMENT")
    if df.empty:
        return pd.DataFrame(columns=_CURVE_COLUMNS)
    df.columns = [c.upper() for c in df.columns]
    names = _resource_names(genids)
    df["RESOURCE"] = df["GENID"].map(names)
    return df[_CURVE_COLUMNS]


def summarize_offers(resource_like: str, start: date, end: date) -> pd.DataFrame:
    """Per resource x month x segment: median/p25/p75 price, avg MW.

    `resource_like` is an ILIKE pattern matched against RESOURCENAME in
    AW.DBO.ERCOT60DDAMGEN (e.g. 'FRNYPP%'). Aggregated server-side
    (APPROX_PERCENTILE) so no raw offer rows are pulled into pandas. RESOURCE
    is attached per-GENID after aggregation; if a name pattern spans multiple
    resource names (e.g. multiple CCGT units under one plant code), rows are
    aggregated per-GENID's resource name, not merged across resources.
    """
    genids = _resolve_genids(resource_like)
    exists, _ = _offer_data_exists(genids, start, end) if genids else (False, None)
    if not exists:
        _warn_no_data(resource_like, genids, start, end)
        return pd.DataFrame(columns=_SUMMARY_COLUMNS)

    genid_list = ",".join(str(g) for g in genids)
    unions = "\nUNION ALL\n".join(
        f"""SELECT GENID, DELIVERYDATE, HOURENDING,
                   {i} AS SEGMENT, CURVEMW{i} AS MW, CURVEPRICE{i} AS PRICE
            FROM AW.DBO.ERCOT60DDAMGENRESOURCE
            WHERE GENID IN ({genid_list})
              AND DELIVERYDATE >= '{start}' AND DELIVERYDATE < '{end}'
              AND CURVEMW{i} IS NOT NULL"""
        for i in _SEGMENTS
    )
    sql = f"""
        WITH raw AS (
            {unions}
        )
        SELECT GENID,
               DATE_TRUNC('month', DELIVERYDATE) AS MONTH,
               SEGMENT,
               APPROX_PERCENTILE(PRICE, 0.5) AS MEDIAN_PRICE,
               APPROX_PERCENTILE(PRICE, 0.25) AS P25_PRICE,
               APPROX_PERCENTILE(PRICE, 0.75) AS P75_PRICE,
               AVG(MW) AS AVG_MW,
               COUNT(*) AS N_OBS
        FROM raw
        GROUP BY GENID, MONTH, SEGMENT
        ORDER BY GENID, MONTH, SEGMENT
    """
    df = sf.query("AW", sql)
    if df.empty:
        return pd.DataFrame(columns=_SUMMARY_COLUMNS)
    df.columns = [c.upper() for c in df.columns]
    names = _resource_names(genids)
    df["RESOURCE"] = df["GENID"].map(names)
    return df[_SUMMARY_COLUMNS]


def _quoted_points(settlement_points: Iterable) -> str:
    return ",".join(f"'{re.sub(chr(39), '', s)}'" for s in set(settlement_points) if isinstance(s, str))


def latest_curves_at_hours(settlement_points: Iterable, hours=(12, 18)) -> pd.DataFrame:
    """Wide offer rows (SETTLEMENTPOINTNAME, CURVEMW1..10, CURVEPRICE1..10) for the listed
    settlement points at the listed hour-endings, last 14 days of the disclosure (LIMIT 5000)."""
    names = _quoted_points(settlement_points)
    if not names:
        return pd.DataFrame()
    return sf.query("AW", f"""
        SELECT SETTLEMENTPOINTNAME, {_CURVE_COLS}
        FROM AW.DBO.ERCOT60DDAMGENRESOURCE
        WHERE DELIVERYDATE >= DATEADD(day, -14, (SELECT MAX(DELIVERYDATE) FROM AW.DBO.ERCOT60DDAMGENRESOURCE))
          AND HOURENDING IN ({','.join(map(str, hours))})
          AND SETTLEMENTPOINTNAME IN ({names})
        LIMIT 5000""")


def latest_capacity_rows(settlement_points: Iterable, first_hour: int = 7, last_hour: int = 22) -> pd.DataFrame:
    """Wide offer rows plus HSL, LSL, AWARDEDQUANTITY for the settlement points over HE first..last,
    last 14 days of the disclosure. Raises if the LIMIT is hit (truncated)."""
    names = _quoted_points(settlement_points)
    if not names:
        return pd.DataFrame()
    df = sf.query("AW", f"""
        SELECT SETTLEMENTPOINTNAME, HSL, LSL, AWARDEDQUANTITY, {_CURVE_COLS}
        FROM AW.DBO.ERCOT60DDAMGENRESOURCE
        WHERE DELIVERYDATE >= DATEADD(day, -14, (SELECT MAX(DELIVERYDATE) FROM AW.DBO.ERCOT60DDAMGENRESOURCE))
          AND HOURENDING BETWEEN {first_hour} AND {last_hour}
          AND SETTLEMENTPOINTNAME IN ({names})
        LIMIT {CAPACITY_ROW_LIMIT}""")
    if len(df) >= CAPACITY_ROW_LIMIT:
        raise RuntimeError(
            f"latest_capacity_rows: hit the {CAPACITY_ROW_LIMIT}-row LIMIT — results are truncated; "
            "narrow the hour window or settlement-point set"
        )
    return df
