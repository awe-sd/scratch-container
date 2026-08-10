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
        SELECT t.toElementId, t.BranchId, t.teid, t.EquipmentName, t.FacilityName,
               t.CommonName, t.KV,
               t.plannedStartDate, t.plannedEndDate, t.actualStartDate, t.actualEndDate,
               t.statusID, s.status AS statusName, t.ReasonID, t.outageIdentifier, t.Notes
        FROM AW.dbo.toAllIsos t
        LEFT JOIN AW.dbo.toStatus s ON s.statusID = t.statusID
        WHERE t.isoMarketId = {config.ISO_MARKET_ID}
          AND t.BranchId = {int(branch_id)}
          AND t.plannedStartDate <= '{window_end}'
          AND (t.plannedEndDate >= '{window_start}' OR t.plannedEndDate IS NULL)
    """
    return _query_awdb(sql)
