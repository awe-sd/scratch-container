"""Targeted outage-ticket lookups in SQL Server AW.dbo.toAllIsos.

The SQL Server box must not receive bulk queries from this pipeline —
every call here is a small, parameterized, single-entity lookup.
"""
from __future__ import annotations

import pandas as pd

from .. import config, mssql, sf



def _query_awdb(sql: str) -> pd.DataFrame:
    return mssql.query(sql)


def lookup_branch_tickets(
    branch_id: int, window_start: str, window_end: str, teid: int | None = None
) -> pd.DataFrame:
    """Latest revision of each outage ticket for one device overlapping
    [window_start, window_end] (YYYY-MM-DD).

    Device filter: teid when provided (authoritative id, map branch_id->teid
    via network_ref.teid_for_branch), else BranchId — never unscoped.
    Tickets are revised over time (revNum); only the newest row per
    outageIdentifier reflects the current status/state/dates, so older
    revisions are dropped via ROW_NUMBER. toState tracks the lifecycle
    (e.g. rated -> approved), toStatus the submission status.
    """
    device = f"teid = {int(teid)}" if teid is not None else f"BranchId = {int(branch_id)}"
    sql = f"""
        WITH t AS (
            SELECT TOP 100 toElementId, BranchId, teid, EquipmentName, FacilityName,
                   CommonName, KV,
                   plannedStartDate, plannedEndDate, actualStartDate, actualEndDate,
                   statusID, toStateId, ReasonID, outageIdentifier, revNum,
                   ReportTime, OC, Notes,
                   ROW_NUMBER() OVER (
                       PARTITION BY outageIdentifier
                       ORDER BY revNum DESC, ReportTime DESC
                   ) AS rn
            FROM AW.dbo.toAllIsos
            WHERE isoMarketId = {config.ISO_MARKET_ID}
              AND {device}
              AND plannedStartDate <= '{window_end}'
              AND (plannedEndDate >= '{window_start}' OR plannedEndDate IS NULL)
            ORDER BY revNum DESC, ReportTime DESC
        )
        SELECT t.*, s.status AS statusName, rs.Reason AS reasonName,
               cs.status AS currentStatusName,
               st.plannedStartDate AS currentStartDate,
               st.plannedEndDate AS currentEndDate,
               st.actualStartDate AS currentActualStart,
               st.CancellationDate AS cancellationDate,
               st.lastUpdate AS stateLastUpdate
        FROM t
        LEFT JOIN AW.dbo.toState st ON st.toStateId = t.toStateId
        LEFT JOIN AW.dbo.toStatus s ON s.statusID = t.statusID
        LEFT JOIN AW.dbo.toStatus cs ON cs.statusID = st.statusID
        LEFT JOIN AW.dbo.toReason rs ON rs.ReasonID = t.ReasonID
        WHERE t.rn = 1
        ORDER BY t.plannedStartDate
    """
    return _query_awdb(sql)


def ticket_history(outage_identifier: str, branch_id: int) -> pd.DataFrame:
    """All revisions of one ticket (for monitoring status/date changes).

    branch_id is required to keep the query on the indexed BranchId path —
    a bare outageIdentifier scan is slow on this table.
    """
    sql = f"""
        SELECT TOP 100 t.outageIdentifier, t.revNum, t.ReportTime, t.statusID,
               s.status AS statusName, t.toStateId, cs.status AS currentStatusName,
               t.plannedStartDate, t.plannedEndDate, t.actualStartDate, t.actualEndDate,
               t.OC, t.CancellationDate, t.CancellationReason,
               st.CancellationDate AS stateCancellationDate, st.lastUpdate AS stateLastUpdate
        FROM AW.dbo.toAllIsos t
        LEFT JOIN AW.dbo.toStatus s ON s.statusID = t.statusID
        LEFT JOIN AW.dbo.toState st ON st.toStateId = t.toStateId
        LEFT JOIN AW.dbo.toStatus cs ON cs.statusID = st.statusID
        WHERE t.isoMarketId = {config.ISO_MARKET_ID}
          AND t.BranchId = {int(branch_id)}
          AND t.outageIdentifier = {sf.quote(outage_identifier)}
        ORDER BY t.revNum DESC, t.ReportTime DESC
    """
    return _query_awdb(sql)
