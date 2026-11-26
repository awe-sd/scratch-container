"""
Read-only schema/data exploration for the outage-related tables that will
drive in_service_date / retirement_date inference:
  - dbo.toChangesAllIsos -- per-revision outage change history, all-ISO table
  - dbo.toState          -- per-outage-request state record (toOutageTypeId,
                            toCauseId, planned/actual dates)

NOTE: dbo.toAllIsos was in scope initially but the user confirmed it's just
an hourly-snapshot dump (one row per teid per hour an outage was active,
duplicated across its whole duration) -- not useful for this analysis.
toChangesAllIsos and toState are the correct sources; toAllIsos is dropped
here entirely (an unfiltered GROUP BY against it also hung/timed out,
consistent with it being a much larger, duplicate-heavy table).

Companion to explore_branch_sqlserver.py -- same investigation style, just a
different set of source tables. Never inserts, never creates tables.
"""
import awconnect
from awconnect import db

ISOMARKETID_ERCOT = 6  # always ERCOT going forward
SAMPLE_TEID = 519  # user-provided example teid


def show_schema(table_name):
    print(f"=== {table_name} SCHEMA ===")
    schema, name = table_name.split(".")
    cols = db.getDfFromAwDb(
        f"""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE,
               NUMERIC_PRECISION, NUMERIC_SCALE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{name}'
        ORDER BY ORDINAL_POSITION
        """
    )
    print(cols.to_string())
    print()


# Trimmed column set for samples -- the full tables are ~60 columns wide and
# printing every row x every column blows past output limits for no benefit.
TAI_SAMPLE_COLS = (
    "toElementId, EquipmentName, BranchId, teid, outageTypeID, emsKey, "
    "toOutageIdentifierId, outageIdentifier, revNum, toStateId, "
    "submitTime, insertDate, plannedStartDate, plannedEndDate, "
    "actualStartDate, actualEndDate, ReasonID, GroupLabel, "
    "CancellationDate, CancellationReason, modelStatusToState"
)


def main():
    awconnect.configure("read_only")

    show_schema("dbo.toChangesAllIsos")
    show_schema("dbo.toState")

    print("=== Tables with 'OutageType' or 'Cause' in the name (looking for a code->label lookup) ===")
    lookups = db.getDfFromAwDb(
        """
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME LIKE '%OutageType%' OR TABLE_NAME LIKE '%Cause%'
           OR TABLE_NAME LIKE '%toReason%' OR TABLE_NAME LIKE '%toStatus%'
        """
    )
    print(lookups.to_string())
    print()

    print(f"=== toChangesAllIsos: distinct outageTypeID values (isoMarketId = {ISOMARKETID_ERCOT}) ===")
    types = db.getDfFromAwDb(
        f"""
        SELECT outageTypeID, COUNT(*) AS n
        FROM AW.dbo.toChangesAllIsos WHERE isoMarketId = {ISOMARKETID_ERCOT} AND teid = {SAMPLE_TEID}
        GROUP BY outageTypeID ORDER BY outageTypeID
        """
    )
    print(types.to_string())
    print()

    print(f"=== toChangesAllIsos SAMPLE (isoMarketId = {ISOMARKETID_ERCOT}, teid = {SAMPLE_TEID}) ===")
    tcai = db.getDfFromAwDb(
        f"""
        SELECT {TAI_SAMPLE_COLS} FROM AW.dbo.toChangesAllIsos
        WHERE isoMarketId = {ISOMARKETID_ERCOT} AND teid = {SAMPLE_TEID}
        ORDER BY toOutageIdentifierId, revNum
        """
    )
    print(f"({len(tcai)} rows)")
    print(tcai.to_string())
    print()

    print(f"=== toState SAMPLE (TOP 20, isoMarketId = {ISOMARKETID_ERCOT}) ===")
    ts = db.getDfFromAwDb(
        f"""
        SELECT TOP 20 toStateId, isoMarketId, toOutageTypeId, toCauseId,
               plannedStartDate, plannedEndDate, actualStartDate, actualEndDate,
               prevStatusId, lastUpdate
        FROM AW.dbo.toState WHERE isoMarketId = {ISOMARKETID_ERCOT}
        """
    )
    print(ts.to_string())
    print()

    print(f"=== toState: distinct toOutageTypeId values (isoMarketId = {ISOMARKETID_ERCOT}) ===")
    state_types = db.getDfFromAwDb(
        f"""
        SELECT toOutageTypeId, COUNT(*) AS n
        FROM AW.dbo.toState WHERE isoMarketId = {ISOMARKETID_ERCOT}
        GROUP BY toOutageTypeId ORDER BY toOutageTypeId
        """
    )
    print(state_types.to_string())


if __name__ == "__main__":
    main()
