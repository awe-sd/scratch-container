"""
One-time read-only fetch of everything the analytics-dev summer-constraint
study needs, cached to parquet under analytics/data/. Per the user's
direction: fetch ONCE, never write to the DB, run all analysis locally.

Windows fetched:
  - summer 2025 (Jun 1 - Sep 30 2025)  -> August-behavior priors
  - summer 2026 to date (May 1 - Jul 14 2026) -> "recent Summer"

Tables:
  congHrPrice        hourly constraint shadow prices (ERCOT, both windows)
  congDefConstraint  constraint dim (ERCOT, all)
  congDefMonitor     monitored-element dim (ERCOT, all)
  congDefContingency contingency dim (ERCOT, all)
  ercotCongConstRecord analyst constraint records/notes (all)
  ercotLoadView      hourly actual load by weather zone (2024+)
  ercotWindRegionHourly wind by geographic region (2024+, actuals+fcst rows)
  windGenAct/solarGenAct ERCOT_ALL actuals (isoZoneID=67, 2024+)
  priceType / congType lookups (printed + saved)
"""
from pathlib import Path

import awconnect
import pandas as pd
from awconnect import db

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# awDate anchor confirmed in branch_tracking work: awDateID 44926 == 2023-01-01
WINDOWS = [("2025-06-01", "2025-09-30"), ("2026-05-01", "2026-07-14")]


def fetch(name, sql):
    out = DATA_DIR / f"{name}.parquet"
    if out.exists():
        print(f"[skip] {name} already fetched ({out.stat().st_size/1e6:.1f} MB)")
        return
    print(f"[fetch] {name} ...")
    df = db.getDfFromAwDb(sql)
    # nchar columns come back space-padded; strip object cols
    for c in df.columns:
        if df[c].dtype == object:
            try:
                df[c] = df[c].str.strip()
            except AttributeError:
                pass
    df.to_parquet(out, index=False)
    print(f"        {len(df):,} rows -> {out.name} ({out.stat().st_size/1e6:.1f} MB)")


def main():
    awconnect.configure("read_only")

    # lookups first (tiny, also printed for the record)
    for lk in ["priceType", "congType", "congHrType", "weatherZone"]:
        try:
            df = db.getDfFromAwDb(f"SELECT * FROM dbo.[{lk}]")
            print(f"--- {lk} ---")
            print(df.head(30).to_string())
            df.to_parquet(DATA_DIR / f"lookup_{lk}.parquet", index=False)
        except Exception as e:
            print(f"lookup {lk} ERROR: {e}")

    win_clause = " OR ".join(
        f"(d.date BETWEEN '{a}' AND '{b}')" for a, b in WINDOWS
    )

    fetch(
        "congHrPrice_ercot_summers",
        f"""
        SELECT p.awDateID, d.date, p.HE, p.priceTypeID, p.congTypeID,
               p.congConstraintID, p.Price, p.MaxPrice,
               p.ConstraintLimit, p.ConstraintValue, p.ViolationAmount
        FROM dbo.congHrPrice p
        JOIN dbo.awDate d ON d.awDateID = p.awDateID
        WHERE p.isomarketid = 6 AND ({win_clause})
        """,
    )

    fetch(
        "congDefConstraint_ercot",
        """
        SELECT congConstraintID, congMontID, congContID, isoConstraintName,
               insertDate, branchConstraintId, congConstraintTypeId
        FROM dbo.congDefConstraint WHERE isomarketid = 6
        """,
    )
    fetch(
        "congDefMonitor_ercot",
        """
        SELECT congMontID, congMontName, branchMonitoredId, FromStation, FromKv,
               ToStation, ToKv, ConstraintType, insertDate
        FROM dbo.congDefMonitor WHERE isomarketid = 6
        """,
    )
    fetch(
        "congDefContingency_ercot",
        """
        SELECT congContID, congContName, congContDescription, insertDate
        FROM dbo.congDefContingency WHERE isomarketid = 6
        """,
    )
    fetch(
        "ercotCongConstRecord",
        "SELECT Date, congConstraintID, TransOutageId, IIRGenOutageId, Confidence, Status, Note FROM dbo.ercotCongConstRecord",
    )
    fetch(
        "ercot_sppCongConstRecord",
        "SELECT Date, congConstraintID, TransOutageId, IIRGenOutageId, Confidence, Status, Note, FacilityID FROM dbo.ercot_sppCongConstRecord",
    )
    fetch(
        "ercotLoadView",
        "SELECT * FROM dbo.ercotLoadView WHERE date >= '2024-01-01'",
    )
    fetch(
        "ercotWindRegionHourly",
        "SELECT TimeStamp, windRegion, avgHSLPct, totalInstalledCapacityMW, isActual FROM dbo.ercotWindRegionHourly WHERE TimeStamp >= '2024-01-01'",
    )
    fetch(
        "windGenAct_ercotAll",
        """
        SELECT w.awDateID, d.date, w.HE, w.priceTypeID, w.windGen
        FROM dbo.windGenAct w JOIN dbo.awDate d ON d.awDateID = w.awDateID
        WHERE w.isoMarketID = 6 AND w.isoZoneID = 67 AND d.date >= '2024-01-01'
        """,
    )
    fetch(
        "solarGenAct_ercotAll",
        """
        SELECT s.awDateID, d.date, s.HE, s.priceTypeID, s.solarGen
        FROM dbo.solarGenAct s JOIN dbo.awDate d ON d.awDateID = s.awDateID
        WHERE s.isoMarketID = 6 AND s.isoZoneID = 67 AND d.date >= '2024-01-01'
        """,
    )

    # regional wind/solar ACTUALS by weather zone — ercotWindRegionHourly's
    # isActual rows stop mid-May-2026, so this is the real actuals source
    fetch(
        "windGenActByWeatherZone",
        """
        SELECT w.awDateID, d.date, w.HE, w.weatherZoneID, w.windGen, w.dstFlag
        FROM dbo.windGenActByWeatherZone w JOIN dbo.awDate d ON d.awDateID = w.awDateID
        WHERE w.isoMarketID = 6 AND d.date >= '2024-01-01'
        """,
    )
    fetch(
        "solarGenActByWeatherZone",
        """
        SELECT s.awDateID, d.date, s.HE, s.weatherZoneID, s.solarGen, s.dstFlag
        FROM dbo.solarGenActByWeatherZone s JOIN dbo.awDate d ON d.awDateID = s.awDateID
        WHERE s.isoMarketID = 6 AND d.date >= '2024-01-01'
        """,
    )

    print("\nAll fetches complete.")


if __name__ == "__main__":
    main()
