"""
Identify BRANCH rows that share a teid with something they clearly aren't
the same physical element as -- i.e. the teid VALUE on one of the rows
looks wrong, not a missing collapseId link (that's find_collapseid_fix_candidates.py).

Scope: DeviceType IN ('Line', 'Transformer'), isomarketid=6, collapseId IS
NULL, same restriction as find_collapseid_fix_candidates.py and for the
same reasons.

Method: take every duplicate-teid group and remove rows already explained
by a known-legitimate pattern, in order:
  1. confirmed_exact_duplicate / probable_renamed_duplicate rows from
     find_collapseid_fix_candidates.py's output -- these should get a
     collapseId fix, not a teid fix.
  2. Legitimate Transformer H/L leg pairs from build_transformer_leg_map.py's
     output (pairing_method same_teid_hl_suffix or
     same_teid_bus_pair_no_suffix) -- these are two real, distinct rows
     that correctly share a teid by design, not a collision.

Whatever's left in a duplicate-teid group is a genuine collision candidate:
run this file AFTER the other two, since it depends on their output.

This can't be fully automatic-confidence the way the other two scripts are
-- "unexplained" just means "doesn't fit a pattern we've already validated,"
not "definitely wrong." Treat this as a manual-review worklist, not a
ready-to-apply fix list.

Read-only. Writes only to branch_tracking/output/.
"""
from pathlib import Path

import awconnect
import pandas as pd
from awconnect import db

ISOMARKETID_ERCOT = 6

REPO_ROOT = Path(__file__).resolve().parents[2]
COLLAPSEID_FIX_CSV = REPO_ROOT / "output" / "collapseid_fix_candidates.csv"
LEG_MAP_CSV = REPO_ROOT / "output" / "transformer_leg_map.csv"
OUTPUT_CSV = REPO_ROOT / "output" / "teid_collision_candidates.csv"


def load_branch():
    return db.getDfFromAwDb(
        f"""
        SELECT branchID, branchName, OP_EQCODE, FromName, ToName, ckt, DeviceType, teid
        FROM dbo.BRANCH
        WHERE isomarketid = {ISOMARKETID_ERCOT}
          AND collapseId IS NULL
          AND teid IS NOT NULL
          AND DeviceType IN ('Line', 'Transformer')
        """
    )


def explained_branch_ids():
    """branch_ids already accounted for by a validated legitimate pattern."""
    ids = set()

    fix = pd.read_csv(COLLAPSEID_FIX_CSV)
    ids |= set(fix["old_branch_id"].dropna())
    ids |= set(fix["recommended_collapseid"].dropna())

    legs = pd.read_csv(LEG_MAP_CSV)
    legit = legs[legs["pairing_method"].isin(
        ["same_teid_hl_suffix", "same_teid_bus_pair_no_suffix"]
    )]
    ids |= set(legit["high_side_branch_id"].dropna())
    ids |= set(legit["low_side_branch_id"].dropna())

    return ids


def main():
    awconnect.configure("read_only")
    branch = load_branch()
    dup_teids = branch.groupby("teid").filter(lambda g: len(g) > 1)

    explained = explained_branch_ids()
    # A row is a collision candidate if it's unexplained, REGARDLESS of how
    # many other unexplained rows remain in its teid group -- even a single
    # stray row sitting alongside an already-explained legitimate pair is
    # still wrongly sharing that teid (e.g. teid=2290: a Line coexisting
    # with a confirmed real H/L transformer-leg pair).
    unexplained = dup_teids[~dup_teids["branchID"].isin(explained)]

    # For context, attach the full original group (including explained
    # rows) so a reviewer can see what each candidate collides with.
    out_rows = []
    for teid, g in unexplained.groupby("teid"):
        full_group = dup_teids[dup_teids["teid"] == teid]
        for _, row in g.iterrows():
            other = full_group[full_group["branchID"] != row["branchID"]]
            out_rows.append({
                "teid": teid,
                "branch_id": row["branchID"], "branch_name": row["branchName"],
                "op_eqcode": row["OP_EQCODE"], "device_type": row["DeviceType"],
                "from_name": row["FromName"], "to_name": row["ToName"], "ckt": row["ckt"],
                "other_branch_ids_sharing_teid": ", ".join(str(x) for x in other["branchID"]),
                "other_branch_names_sharing_teid": ", ".join(str(x) for x in other["branchName"]),
            })

    out = pd.DataFrame(out_rows)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_CSV, index=False)

    print(f"Duplicate-teid groups (Line/Transformer): {dup_teids['teid'].nunique()}")
    print(f"Rows already explained (collapseId fix or legit H/L pair): {len(explained)}")
    print(f"Unexplained collision-candidate rows: {len(unexplained)}")
    print(f"Distinct teids involved: {out['teid'].nunique() if len(out) else 0}")
    print(f"Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
