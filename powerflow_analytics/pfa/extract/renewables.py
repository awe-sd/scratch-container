"""Historical wind and solar actuals (SQL Server, read via pfa.mssql).

Wind: AW.dbo.ercotWindRegionHourly, hourly per ERCOT wind region. avgHSLPct is a
PERCENT (0-100), not a fraction; MW = avgHSLPct/100 * totalInstalledCapacityMW.
Solar: AW.dbo.solarGenAct (hourly-ending HE per iso zone, MW) joined to AW.dbo.awDate for the calendar date.
"""
from __future__ import annotations

import pandas as pd

from .. import mssql

SYSTEM_SOLAR_ISO_ZONE = 67


def wind_region_hourly(start: str, end: str, region: str | None = None) -> pd.DataFrame:
    """TimeStamp, windRegion, avgHSLPct, totalInstalledCapacityMW for start <= TimeStamp < end;
    one region if `region` is given (e.g. 'West'), else all regions."""
    region_sql = f"\n              AND windRegion = '{region}'" if region else ""
    return mssql.query(
        f"""SELECT TimeStamp, windRegion, avgHSLPct, totalInstalledCapacityMW
            FROM AW.dbo.ercotWindRegionHourly
            WHERE TimeStamp >= '{start}' AND TimeStamp < '{end}'{region_sql}""",
    )


def solar_hourly(start: str, end: str, iso_zone: int = SYSTEM_SOLAR_ISO_ZONE) -> pd.DataFrame:
    """TimeStampDate (calendar date), HE (1-24), solarGen, solarMax for start <= date < end."""
    return mssql.query(
        f"""SELECT d.date AS TimeStampDate, s.HE, s.solarGen, s.solarMax
            FROM AW.dbo.solarGenAct s
            JOIN AW.dbo.awDate d ON d.awDateID = s.awDateID
            WHERE s.isoZoneID = {int(iso_zone)}
              AND d.date >= '{start}' AND d.date < '{end}'""",
    )
