"""
First-cut approximation of `default_status` (normally closed vs normally
open) for each branch_id in the mapping, using PTOBRANCH (the auction
network model's branch snapshot) status across the last ~20 months of
ERCOT Monthly Auction cases.

Method (explicitly a first cut -- the user is separately working out a
proper in-service-date-based approach using outage data; this is a stopgap
until that lands):
  1. Get the recent case list from ptoFile (Monthly Auction, non-CIM,
     2025-2026 -- the user's exact query).
  2. Pull every ptoBranch row for those cases, for the branch_ids in our
     confirmed teid<->branch_id map (teid_branch_id_map.csv).
  3. Tally branchStatus ('Closed' / 'Open') per branch_id across those
     snapshots. default_status_majority is whichever status appears more
     often.

Known limitations (per the user, not solved here):
  - A branch_id can appear more than once within a single ptoID snapshot
    if its from/to bus is split in that case's model -- this script tallies
    every row as one vote without deduplicating that, so a heavily-split
    branch's status count is weighted by how many split-rows it produced,
    not by how many snapshots it appeared in. `n_snapshots` (distinct
    ptoID count) is reported alongside `n_status_rows` (total row count)
    so this is at least visible.
  - PTOBRANCH coverage is sparse to begin with (~12.7% of BRANCH branch_ids
    ever appear in it at all -- see analyze_duplicate_teids.py). Branches
    with zero rows in the recent-case window get default_status = None
    and are flagged `no_pto_data`.
  - This can't distinguish "genuinely normally open" (e.g. a bypass around
    a series reactor/capacitor, a phase-shifting transformer) from "closed
    most of the time but happened to be on outage a lot in the sample
    window" -- a branch with a roughly even Closed/Open split is flagged
    `mixed` for manual review rather than guessed at.
  - ERCOT avoids scheduling outages between ~May 15 and Sep 15, so a
    branch that's Open only outside that window is more likely a real
    seasonal outage pattern than a "normally open" device -- not modeled
    here, just noted as a manual-review consideration.

Read-only. Writes only to branch_tracking/output/.
"""
from pathlib import Path

import awconnect
import pandas as pd
from awconnect import db

ISOMARKETID_ERCOT = 6
MIXED_LOW = 0.2  # pct_closed between this and MIXED_HIGH -> flag as "mixed"
MIXED_HIGH = 0.8

REPO_ROOT = Path(__file__).resolve().parents[1]
TEID_MAP_CSV = REPO_ROOT / "output" / "teid_branch_id_map.csv"
OUTPUT_CSV = REPO_ROOT / "output" / "branch_default_status.csv"


def load_recent_case_ptoids():
    cases = db.getDfFromAwDb(
        """
        SELECT ptoID, caseName
        FROM AW.dbo.ptoFile
        WHERE isomarketid = 6
          AND (caseName like '%2026 Monthly%' or caseName like '%2025 Monthly%')
          AND caseName not like '%CIM%'
        ORDER BY ptoID desc
        """
    )
    return cases


def load_ptobranch_status(ptoids):
    ptoid_list = ",".join(str(int(p)) for p in ptoids)
    return db.getDfFromAwDb(
        f"""
        SELECT ptoID, branchID, branchStatus
        FROM AW.dbo.ptoBranch
        WHERE isomarketid = {ISOMARKETID_ERCOT}
          AND ptoID IN ({ptoid_list})
        """
    )


def main():
    awconnect.configure("read_only")

    teid_map = pd.read_csv(TEID_MAP_CSV)
    legit_branch_ids = (
        teid_map[teid_map["match_status"] != "unmatched"][["teid", "branch_id"]]
        .drop_duplicates()
    )
    legit_branch_ids["branch_id"] = legit_branch_ids["branch_id"].astype(int)

    cases = load_recent_case_ptoids()
    status_rows = load_ptobranch_status(cases["ptoID"].tolist())

    merged = legit_branch_ids.merge(
        status_rows, left_on="branch_id", right_on="branchID", how="left"
    )

    def summarize(g):
        has_data = g["branchStatus"].notna()
        n_status_rows = int(has_data.sum())
        n_snapshots = int(g.loc[has_data, "ptoID"].nunique())
        n_closed = int((g["branchStatus"] == "Closed").sum())
        n_open = int((g["branchStatus"] == "Open").sum())
        if n_status_rows == 0:
            return pd.Series({
                "n_snapshots": 0, "n_status_rows": 0, "n_closed": 0, "n_open": 0,
                "pct_closed": None, "default_status_majority": None, "review_flag": "no_pto_data",
            })
        pct_closed = n_closed / n_status_rows
        majority = "Closed" if n_closed >= n_open else "Open"
        flag = "mixed" if MIXED_LOW <= pct_closed <= MIXED_HIGH else "clear_majority"
        return pd.Series({
            "n_snapshots": n_snapshots, "n_status_rows": n_status_rows,
            "n_closed": n_closed, "n_open": n_open, "pct_closed": round(pct_closed, 3),
            "default_status_majority": majority, "review_flag": flag,
        })

    summary = merged.groupby(["teid", "branch_id"]).apply(summarize, include_groups=False).reset_index()

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUTPUT_CSV, index=False)

    print(f"Recent Monthly Auction cases used: {len(cases)}")
    print(f"Branch_ids in scope: {len(legit_branch_ids)}")
    print(summary["review_flag"].value_counts(dropna=False).to_string())
    print()
    print("Of branches with PTO data, default_status_majority breakdown:")
    print(summary["default_status_majority"].value_counts(dropna=False).to_string())
    print(f"Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
