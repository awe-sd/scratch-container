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
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
TEID_MAP_CSV = REPO_ROOT / "output" / "teid_branch_id_map.csv"
DATES_CSV = REPO_ROOT / "output" / "teid_inservice_retirement_dates.csv"
STATUS_CSV = REPO_ROOT / "output" / "branch_default_status.csv"
DAMPSSE_CSV = REPO_ROOT / "output" / "dampsse_default_status.csv"
OUTPUT_CSV = REPO_ROOT / "output" / "branch_tracking_table.csv"

DEFAULT_IN_SERVICE_DATE = "1990-01-01"
DEFAULT_RETIREMENT_DATE = "2099-12-31"


def main():
    teid_map = pd.read_csv(TEID_MAP_CSV)
    dates = pd.read_csv(DATES_CSV)
    status = pd.read_csv(STATUS_CSV)

    base = teid_map[["teid", "branch_id", "FromName", "ToName", "ckt",
                      "DeviceType", "match_status"]].copy()

    table = base.merge(
        dates[["teid", "in_service_date", "retirement_date",
               "in_service_date_source", "retirement_date_source", "review_flag"]]
        .rename(columns={"review_flag": "dates_review_flag"}),
        on="teid", how="left",
    )
    table = table.merge(
        status[["teid", "default_status_majority", "pct_closed", "review_flag"]]
        .rename(columns={"review_flag": "status_review_flag"}),
        on="teid", how="left",
    )

    # DAM PSSE linkage + inService-derived status (per the user: the DAM
    # hourly model's inService is a better status indicator than the
    # auction snapshots, and ercotDampsseId completes the identity mapping
    # alongside teid/branch_id). Two sources, no teid overlap by
    # construction: the exact-name tier (build_dampsse_default_status.py)
    # and the fallback tiers (map_unmapped_dampsse_teids.py).
    if DAMPSSE_CSV.exists():
        dampsse = pd.read_csv(DAMPSSE_CSV)[
            ["teid", "ercotDampsseId", "dampsse_default_status", "pct_inservice"]
        ]
        fallback_csv = DAMPSSE_CSV.parent / "dampsse_default_status_fallback.csv"
        if fallback_csv.exists():
            fb = pd.read_csv(fallback_csv)[
                ["teid", "ercotDampsseId", "dampsse_default_status", "pct_inservice"]
            ]
            dampsse = pd.concat([dampsse, fb], ignore_index=True).drop_duplicates(
                subset="teid", keep="first"
            )
        dampsse = dampsse.rename(columns={"pct_inservice": "dampsse_pct_inservice"})
        table = table.merge(dampsse, on="teid", how="left")
    else:
        table["ercotDampsseId"] = pd.NA
        table["dampsse_default_status"] = pd.NA
        table["dampsse_pct_inservice"] = pd.NA

    # Defaults where missing (per the user): a teid with no outage evidence
    # (e.g. the ~516 unmatched teids, which never get processed by
    # build_inservice_retirement_dates.py at all) still gets the standard
    # 1990-01-01 in-service / 2099-12-31 retirement defaults -- this is
    # NOT confirmed evidence, just "no information either way," same
    # meaning as everywhere else in the pipeline.
    n_missing_dates = int(table["in_service_date"].isna().sum())
    table["in_service_date"] = table["in_service_date"].fillna(DEFAULT_IN_SERVICE_DATE)
    table["retirement_date"] = table["retirement_date"].fillna(DEFAULT_RETIREMENT_DATE)
    table["in_service_date_source"] = table["in_service_date_source"].fillna("default")
    table["retirement_date_source"] = table["retirement_date_source"].fillna("default")

    # implied_default_status is left blank when missing (no branch_id, or
    # no recent PTOBRANCH coverage) -- Closed/Open is a genuine fact that
    # shouldn't be guessed at without any evidence, unlike the date
    # defaults above which have an explicit, stated fallback convention.
    table = table.rename(columns={
        "FromName": "from_bus",
        "ToName": "to_bus",
        "default_status_majority": "implied_default_status",
    })

    # Resolved default_status (per the user): DAM PSSE inService dominant
    # status is the primary indicator; the auction-based value is only a
    # fallback where DAM has no coverage; blank when neither knows.
    table["default_status"] = table["dampsse_default_status"].fillna(
        table["implied_default_status"]
    )
    table["default_status_source"] = pd.NA
    table.loc[table["dampsse_default_status"].notna(), "default_status_source"] = "dampsse_inservice"
    table.loc[
        table["dampsse_default_status"].isna() & table["implied_default_status"].notna(),
        "default_status_source",
    ] = "auction_fallback"

    column_order = [
        "teid", "branch_id", "ercotDampsseId", "from_bus", "to_bus", "ckt",
        "default_status", "default_status_source",
        "in_service_date", "retirement_date",
        "DeviceType", "match_status", "in_service_date_source",
        "retirement_date_source", "dates_review_flag", "status_review_flag",
        "dampsse_default_status", "dampsse_pct_inservice",
        "implied_default_status", "pct_closed",
    ]
    table = table[column_order]

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
