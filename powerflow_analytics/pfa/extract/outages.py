"""Targeted outage-ticket lookups in SQL Server AW.dbo.toAllIsos.

The SQL Server box must not receive bulk queries from this pipeline —
every call here is a small, parameterized, single-entity lookup.
"""
from __future__ import annotations

import pandas as pd

from .. import config


BRANCH_MAP_CSV = (
    config.PROJECT_ROOT.parent / "branch_tracking" / "output" / "branch_tracking_table_final.csv"
)
_branch_map: pd.DataFrame | None = None


def branch_map() -> pd.DataFrame:
    """Local branch_id -> teid / bus-name map from the branch_tracking table.

    branch_id there shares the 60M id-space with AWOPF BRANCHID columns, and
    teid is the authoritative device id for outage lookups — so the mapping
    never needs a DB query.
    """
    global _branch_map
    if _branch_map is None:
        df = pd.read_csv(
            BRANCH_MAP_CSV,
            usecols=["teid", "branch_id", "from_bus", "to_bus", "ckt", "default_status_final"],
        )
        df = df.dropna(subset=["branch_id"])
        df["branch_id"] = df["branch_id"].astype("int64")
        _branch_map = df.drop_duplicates("branch_id").set_index("branch_id")
    return _branch_map


def teid_for_branch(branch_id: int) -> int | None:
    m = branch_map()
    if int(branch_id) in m.index:
        t = m.loc[int(branch_id), "teid"]
        return int(t) if pd.notna(t) else None
    return None


def _query_awdb(sql: str) -> pd.DataFrame:
    config.configure()
    from awconnect import db

    return db.getDfFromAwDb(sql, database="AW")


def lookup_branch_tickets(
    branch_id: int, window_start: str, window_end: str, teid: int | None = None
) -> pd.DataFrame:
    """Latest revision of each outage ticket for one device overlapping
    [window_start, window_end] (YYYY-MM-DD).

    Device filter: teid when provided (authoritative id, map branch_id->teid
    via branch_tracking_table_final.csv), else BranchId — never unscoped.
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
    ident = str(outage_identifier).replace("'", "''")
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
          AND t.outageIdentifier = '{ident}'
        ORDER BY t.revNum DESC, t.ReportTime DESC
    """
    return _query_awdb(sql)
