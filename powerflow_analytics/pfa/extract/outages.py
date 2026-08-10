"""Targeted outage-ticket lookups in SQL Server AW.dbo.toAllIsos.

The SQL Server box must not receive bulk queries from this pipeline —
every call here is a small, parameterized, single-entity lookup.
"""
from __future__ import annotations

import pandas as pd

from .. import config


def _query_awdb(sql: str) -> pd.DataFrame:
    config.configure()
    from awconnect import db

    return db.getDfFromAwDb(sql, database="AW")


def lookup_branch_tickets(branch_id: int, window_start: str, window_end: str) -> pd.DataFrame:
    """Outage tickets for one BranchId overlapping [window_start, window_end] (YYYY-MM-DD)."""
    sql = f"""
        SELECT toElementId, BranchId, teid, EquipmentName, FacilityName, CommonName, KV,
               plannedStartDate, plannedEndDate, actualStartDate, actualEndDate,
               statusID, ReasonID, outageIdentifier, Notes
        FROM AW.dbo.toAllIsos
        WHERE isoMarketId = {config.ISO_MARKET_ID}
          AND BranchId = {int(branch_id)}
          AND plannedStartDate <= '{window_end}'
          AND (plannedEndDate >= '{window_start}' OR plannedEndDate IS NULL)
    """
    return _query_awdb(sql)
