"""Final branch_tracking table: pure join of the upstream deliverables.

Pure function extracted verbatim from build_final_branch_table.py:main --
joins + date defaults + renames + dampsse concat + column order. See that
script's module docstring for the full rationale. Writes nothing; the
script wrapper handles I/O.
"""
from typing import Optional

import pandas as pd

from .status import resolve_default_status

DEFAULT_IN_SERVICE_DATE = "1990-01-01"
DEFAULT_RETIREMENT_DATE = "2099-12-31"


def build_table(
    teid_map: pd.DataFrame,
    dates: pd.DataFrame,
    status: pd.DataFrame,
    dampsse: Optional[pd.DataFrame],
    dampsse_fallback: Optional[pd.DataFrame],
) -> pd.DataFrame:
    """Full join + date defaults + renames + dampsse concat + column
    order. From build_final_branch_table.py:main. Returns the frame;
    writes nothing."""
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
    # construction: the exact-name tier and the fallback tiers.
    if dampsse is not None:
        dampsse = dampsse[
            ["teid", "ercotDampsseId", "dampsse_default_status", "pct_inservice"]
        ].copy()
        if dampsse_fallback is not None:
            fb = dampsse_fallback[
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
    table = resolve_default_status(table)

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

    return table
