"""
Consolidated first-cut of the branch_tracking table itself: one row per
CIM teid (ALL 11,443, including the ~516 unmatched ones -- per the user,
3rd-winding/generation-step-up stubs etc. are less important but must
still appear as rows, just without a branch_id/bus/ckt to hang off of),
joining together the three deliverables built so far:
  - teid_branch_id_map.csv    -> branch_id, from/to bus, ckt
  - teid_inservice_retirement_dates.csv -> in_service_date, retirement_date
  - branch_default_status.csv -> implied_default_status

Pure local-file join -- no DB query, no awconnect needed.

Known open issues (per the user, tracked here rather than solved in this
script -- this table is a starting point for further iteration):
  - Retirement dates derived from outages haven't been cross-validated
    against implied_default_status yet (e.g. teid=1019: a resolved
    retirement_date of 2021-10-18, but the device still appears in the
    current July 2026 CIM model -- the "retirement" was likely a
    mis-tagged short maintenance outage, not a real decommissioning).
    Same validation is needed for in_service_date against outage-derived
    energization evidence.
  - implied_default_status itself needs validation, particularly the
    normally-open cases -- is a device really normally open (e.g. a
    reactor/capacitor bypass) or just heavily sampled during outages?
  - Missing in_service_date/retirement_date are defaulted to
    1990-01-01/2099-12-31 (the user's stated defaults) -- this does NOT
    mean confirmed evidence, just no information either way. Missing
    implied_default_status (no branch_id, or no recent PTOBRANCH
    coverage) is left blank rather than guessed at.

Read-only. Writes only to branch_tracking/output/.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from branch_tracking.pipeline import assemble  # noqa: E402

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
TEID_MAP_CSV = REPO_ROOT / "output" / "teid_branch_id_map.csv"
DATES_CSV = REPO_ROOT / "output" / "teid_inservice_retirement_dates.csv"
STATUS_CSV = REPO_ROOT / "output" / "branch_default_status.csv"
DAMPSSE_CSV = REPO_ROOT / "output" / "dampsse_default_status.csv"
DAMPSSE_FALLBACK_CSV = REPO_ROOT / "output" / "dampsse_default_status_fallback.csv"
OUTPUT_CSV = REPO_ROOT / "output" / "branch_tracking_table.csv"


def main():
    teid_map = pd.read_csv(TEID_MAP_CSV)
    dates = pd.read_csv(DATES_CSV)
    status = pd.read_csv(STATUS_CSV)
    dampsse = pd.read_csv(DAMPSSE_CSV) if DAMPSSE_CSV.exists() else None
    dampsse_fallback = pd.read_csv(DAMPSSE_FALLBACK_CSV) if DAMPSSE_FALLBACK_CSV.exists() else None

    n_missing_dates = int((~teid_map["teid"].isin(dates["teid"])).sum())

    table = assemble.build_table(
        teid_map=teid_map,
        dates=dates,
        status=status,
        dampsse=dampsse,
        dampsse_fallback=dampsse_fallback,
    )

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUTPUT_CSV, index=False)

    print(f"Total rows (all CIM teids): {len(table)}")
    print(f"  with a branch_id: {table['branch_id'].notna().sum()}")
    print(f"  without a branch_id (unmatched -- e.g. 3rd-winding/GSU stubs): {table['branch_id'].isna().sum()}")
    print(f"Teids that had no in_service_date/retirement_date row at all (defaulted here): {n_missing_dates}")
    print(f"implied_default_status populated: {table['implied_default_status'].notna().sum()}")
    print(f"implied_default_status blank (no branch_id or no recent PTOBRANCH coverage): {table['implied_default_status'].isna().sum()}")
    print(f"ercotDampsseId mapped: {table['ercotDampsseId'].notna().sum()}")
    print(f"dampsse_default_status populated: {table['dampsse_default_status'].notna().sum()}")
    print("default_status (resolved) breakdown:")
    print(table.groupby(["default_status", "default_status_source"], dropna=False).size().to_string())
    print()
    print("DeviceType breakdown:")
    print(table["DeviceType"].value_counts(dropna=False).to_string())
    print(f"Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
