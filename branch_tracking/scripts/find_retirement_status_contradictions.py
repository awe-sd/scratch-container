"""
Flags teids where the outage-derived retirement_date is likely FALSE: a
retirement was resolved from a "Retirement of Old Equipment" outage, but
implied_default_status (from recent PTOBRANCH auction snapshots) says the
branch is still Closed -- i.e. actually in service, contradicting the
claimed retirement.

NOTE: as of this pass, build_inservice_retirement_dates.py itself applies
this same cross-check and auto-reverts CONFIDENT contradictions
(status_review_flag='clear_majority', >= STATUS_CONTRADICTION_MIN_ROWS
recent snapshots) to the default retirement_date -- see its module
docstring step 7b. So teid_inservice_retirement_dates.csv's
retirement_date is already corrected for the strong cases (confirmed via
teid=1019 and teid=3830, both of which now show retirement_date_source=
'default'). What THIS script surfaces now is narrower: the remaining
weaker contradictions (a "mixed" status split, or too few status rows to
trust) that got left as retirement_status_uncertain rather than
auto-corrected -- a genuine manual-review worklist, not a duplicate of
the main pipeline's correction.

Original finding (teid=1019, before the fix): resolved
retirement_date=2021-10-18, but implied_default_status=Closed at
pct_closed=1.0 (100% closed across the last ~20 Monthly Auction cases,
2025-2026), and the device still appeared in the current July 2026 CIM
model. Broadening the check found 83% of all resolved retirements (131 of
158) initially contradicted a Closed status, including clusters of
different teids sharing the exact same retirement timestamp (a signature
of coordinated substation maintenance/equipment-replacement work being
tagged "Retirement of Old Equipment," not real decommissioning) -- see
the module docstring in build_inservice_retirement_dates.py and
investigate_retirement_flags.py for the broader pattern.

Method: join teid_inservice_retirement_dates.csv (retirement_date,
retirement_date_source) with branch_default_status.csv
(default_status_majority, pct_closed, n_status_rows) on teid. Flag any
teid with a real (non-default) retirement AND a Closed majority status.
pct_closed and n_status_rows indicate how strong the contradicting
evidence is (higher pct_closed / more status rows = more confident the
"retirement" is bogus).

Known caveat (not modeled): PTOBRANCH auction cases model 12+ months
forward, so a genuinely very recent retirement might not show up as
"Open" yet if the model hasn't caught up, or conversely a planned future
retirement could already show as Open before the physical event happens.

Pure local-file join -- no DB query, no awconnect needed.
"""
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DATES_CSV = REPO_ROOT / "output" / "teid_inservice_retirement_dates.csv"
STATUS_CSV = REPO_ROOT / "output" / "branch_default_status.csv"
TEID_MAP_CSV = REPO_ROOT / "output" / "teid_branch_id_map.csv"
OUTPUT_CSV = REPO_ROOT / "output" / "retirement_status_contradictions.csv"
TABLE_CSV = REPO_ROOT / "output" / "branch_tracking_table.csv"


def main():
    dates = pd.read_csv(DATES_CSV)
    status = pd.read_csv(STATUS_CSV)
    teid_map = pd.read_csv(TEID_MAP_CSV)[
        ["teid", "branch_id", "FromName", "ToName", "ckt", "DeviceType"]
    ]

    merged = (
        dates[["teid", "retirement_date", "retirement_date_source",
               "retirement_device_name", "n_retirement_events",
               "n_retirement_actual_events", "n_retirement_chains"]]
        .merge(status[["teid", "default_status_majority", "pct_closed",
                       "n_status_rows", "n_closed", "n_open"]], on="teid", how="inner")
        .merge(teid_map, on="teid", how="left")
    )

    contradiction = (
        (merged["retirement_date_source"] == "retirement_outage")
        & (merged["default_status_majority"] == "Closed")
    )
    flagged = merged[contradiction].sort_values("pct_closed", ascending=False)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    flagged.to_csv(OUTPUT_CSV, index=False)

    print(f"Teids with a real retirement_date: {(dates['retirement_date_source'] == 'retirement_outage').sum()}")
    print(f"Of those, flagged as likely-false (implied status still Closed): {len(flagged)}")
    print()
    print("pct_closed distribution among flagged:")
    print(flagged["pct_closed"].describe().to_string())
    print(f"Wrote {OUTPUT_CSV}")

    # Also surface the flag inline in the consolidated table, if it exists.
    if TABLE_CSV.exists():
        table = pd.read_csv(TABLE_CSV)
        table["retirement_status_contradiction"] = table["teid"].isin(flagged["teid"])
        table.to_csv(TABLE_CSV, index=False)
        print(f"Added retirement_status_contradiction column to {TABLE_CSV}")


if __name__ == "__main__":
    main()
