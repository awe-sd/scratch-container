"""
Reusable helpers for pulling ERCOT DAM energy offer curves from Snowflake (AW.DBO).

Authoritative tables:
  - AW.DBO.ERCOT60DDAMGEN          -- GENID -> RESOURCENAME / RESOURCETYPE lookup
  - AW.DBO.ERCOT60DDAMGENRESOURCE  -- 60-day DAM gen resource disclosure; one row per
                                       (DELIVERYDATE, HOURENDING, GENID) with up to 10
                                       (CURVEMWn, CURVEPRICEn) offer-curve segment pairs,
                                       plus HSL/LSL/RESOURCESTATUS/QSE/DME etc.

Notes:
  - This is the 60-day disclosure: data lags ~60 days behind "today". Always check
    MAX(DELIVERYDATE) before assuming recent months are populated.
  - AW.DBO.ERCOTDAMPSSEGNTIMESERIES is a *different*, PSSE-bus-scoped segment time
    series (AWDATEID/HE/PSSEBUSNUMBER/PSSEGENID) — it does NOT carry offer curve
    MW/price pairs or a resource name, so it is the wrong table for offer curves.
    Use ERCOT60DDAMGEN + ERCOT60DDAMGENRESOURCE instead.

Usage (run via `uv run` from the repo root so it picks up the project .venv):

    import awconnect
    awconnect.configure('read_only')
    from dam_offers.dam_bids import resolve_genids, bid_data_exists, get_offer_curve

    genids = resolve_genids('FRNYPP%')                       # Forney Energy Center units
    exists, date_range = bid_data_exists(genids)
    if exists:
        df = get_offer_curve(genids, start_date='2026-04-01', end_date='2026-06-30')
"""

from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd
from awconnect import snowflake

_WAREHOUSE = "AI_READ_ONLY"

# The offer curve is stored as 10 fixed (CURVEMWn, CURVEPRICEn) column pairs rather
# than a normalized table, so we unpivot them with a LATERAL FLATTEN over a literal
# array of OBJECT_CONSTRUCTs. Keep this in one place since every query below needs it.
_SEGMENT_UNPIVOT_SQL = """
LATERAL FLATTEN(input => ARRAY_CONSTRUCT(
  OBJECT_CONSTRUCT('seg',1,'mw',CURVEMW1,'price',CURVEPRICE1),
  OBJECT_CONSTRUCT('seg',2,'mw',CURVEMW2,'price',CURVEPRICE2),
  OBJECT_CONSTRUCT('seg',3,'mw',CURVEMW3,'price',CURVEPRICE3),
  OBJECT_CONSTRUCT('seg',4,'mw',CURVEMW4,'price',CURVEPRICE4),
  OBJECT_CONSTRUCT('seg',5,'mw',CURVEMW5,'price',CURVEPRICE5),
  OBJECT_CONSTRUCT('seg',6,'mw',CURVEMW6,'price',CURVEPRICE6),
  OBJECT_CONSTRUCT('seg',7,'mw',CURVEMW7,'price',CURVEPRICE7),
  OBJECT_CONSTRUCT('seg',8,'mw',CURVEMW8,'price',CURVEPRICE8),
  OBJECT_CONSTRUCT('seg',9,'mw',CURVEMW9,'price',CURVEPRICE9),
  OBJECT_CONSTRUCT('seg',10,'mw',CURVEMW10,'price',CURVEPRICE10)
)) seg
"""


def resolve_genids(resource_pattern: str) -> list[int]:
    """Look up GENID(s) for a resource name pattern (SQL ILIKE, e.g. 'FRNYPP%').

    Returns an empty list if no resource matches -- callers should treat that as
    "resource not found under this name" and try alternate spellings/abbreviations
    rather than assuming the table is broken.
    """
    sql = f"""
        SELECT DISTINCT GENID
        FROM AW.DBO.ERCOT60DDAMGEN
        WHERE RESOURCENAME ILIKE '{resource_pattern}'
    """
    df = snowflake.performQuery("AW", sql, warehouse=_WAREHOUSE, logInfo=False)
    df.columns = [c.upper() for c in df.columns]
    return sorted(df["GENID"].tolist())


def list_resource_names(resource_pattern: str) -> pd.DataFrame:
    """Return GENID/RESOURCENAME/RESOURCETYPE rows matching a name pattern, for
    disambiguating which units belong to a plant before pulling bids."""
    sql = f"""
        SELECT GENID, RESOURCENAME, RESOURCETYPE, INSERTDATE
        FROM AW.DBO.ERCOT60DDAMGEN
        WHERE RESOURCENAME ILIKE '{resource_pattern}'
        ORDER BY RESOURCENAME
    """
    return snowflake.performQuery("AW", sql, warehouse=_WAREHOUSE, logInfo=False)


def bid_data_exists(
    genids: Iterable[int],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> tuple[bool, Optional[tuple[str, str]]]:
    """Check whether any offer-curve rows exist for the given GENIDs (optionally
    restricted to a date window) BEFORE pulling the full curve.

    Returns (exists: bool, (min_date, max_date) or None).
    Use this from later agents to avoid re-querying/re-aggregating data that isn't
    there yet (remember: 60-day disclosure lag, so "today" data won't exist).
    """
    genids = list(genids)
    if not genids:
        return False, None
    genid_list = ",".join(str(g) for g in genids)
    date_filter = ""
    if start_date:
        date_filter += f" AND DELIVERYDATE >= '{start_date}'"
    if end_date:
        date_filter += f" AND DELIVERYDATE <= '{end_date}'"
    sql = f"""
        SELECT COUNT(*) AS n, MIN(DELIVERYDATE) AS mindate, MAX(DELIVERYDATE) AS maxdate
        FROM AW.DBO.ERCOT60DDAMGENRESOURCE
        WHERE GENID IN ({genid_list}) {date_filter}
    """
    df = snowflake.performQuery("AW", sql, warehouse=_WAREHOUSE, logInfo=False)
    df.columns = [c.upper() for c in df.columns]
    n = int(df["N"].iloc[0])
    if n == 0:
        return False, None
    return True, (str(df["MINDATE"].iloc[0]), str(df["MAXDATE"].iloc[0]))


def get_offer_curve(
    genids: Iterable[int],
    start_date: str,
    end_date: str,
    group_by: str = "month",
) -> pd.DataFrame:
    """Pull an aggregated (server-side) offer curve for the given GENIDs and date
    window, unpivoted to one row per (period, segment).

    group_by: 'month' or 'day' (DATE_TRUNC granularity). Do not pull raw hourly rows
    into pandas for wide date ranges -- aggregate here instead (median cap ~3GB).

    Returns columns: period, segment, n, median_price, p25_price, p75_price,
    max_price, avg_mw.
    """
    genids = list(genids)
    if not genids:
        raise ValueError("genids is empty -- resolve_genids() returned no matches")
    genid_list = ",".join(str(g) for g in genids)
    trunc = {"month": "month", "day": "day"}.get(group_by, "month")
    sql = f"""
        WITH base AS (
          SELECT DELIVERYDATE, GENID, HOURENDING, RESOURCESTATUS, HSL, LSL,
            CURVEMW1, CURVEPRICE1, CURVEMW2, CURVEPRICE2, CURVEMW3, CURVEPRICE3,
            CURVEMW4, CURVEPRICE4, CURVEMW5, CURVEPRICE5, CURVEMW6, CURVEPRICE6,
            CURVEMW7, CURVEPRICE7, CURVEMW8, CURVEPRICE8, CURVEMW9, CURVEPRICE9,
            CURVEMW10, CURVEPRICE10
          FROM AW.DBO.ERCOT60DDAMGENRESOURCE
          WHERE GENID IN ({genid_list})
            AND DELIVERYDATE >= '{start_date}' AND DELIVERYDATE <= '{end_date}'
        )
        SELECT
          DATE_TRUNC('{trunc}', DELIVERYDATE) AS period,
          seg.value:seg::int AS segment,
          COUNT(*) AS n,
          MEDIAN(seg.value:price::float) AS median_price,
          PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY seg.value:price::float) AS p25_price,
          PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY seg.value:price::float) AS p75_price,
          MAX(seg.value:price::float) AS max_price,
          AVG(seg.value:mw::float) AS avg_mw
        FROM base,
        {_SEGMENT_UNPIVOT_SQL}
        WHERE seg.value:price IS NOT NULL
        GROUP BY period, segment
        ORDER BY period, segment
    """
    df = snowflake.performQuery("AW", sql, warehouse=_WAREHOUSE, logInfo=False)
    df.columns = [c.upper() for c in df.columns]
    return df
