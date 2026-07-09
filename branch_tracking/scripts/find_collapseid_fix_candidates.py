"""
Identify BRANCH rows that look like a duplicate re-insertion of the same
physical element under a shared teid, with no collapseId link recording
that the older row was superseded -- i.e. candidates for a real DB fix
(set collapseId on the old row(s) to point at the current one).

Scope: dbo.BRANCH rows where DeviceType IN ('Line', 'Transformer')
(isomarketid=6, collapseId IS NULL, teid NOT NULL) -- switching devices
(breaker/disconnector, ~78% of the table) and other equipment types (load,
endcap, shunt, staticVarCompensator, Generator) are excluded, both because
bus-pair matching is a much weaker signal for switching devices and
because the confidence calibration here (ckt-matching, etc.) was only
built and tested against Line/Transformer examples. Not limited to the
CIM-relevant teid subset build_teid_branchid_map.py works with though --
this is a standalone BRANCH data-quality question.

Two confidence tiers, since "same element, never linked" is only provable
with real evidence, not guessed:
  - confirmed_exact_duplicate: 2+ rows share a teid AND an exact OP_EQCODE
    match. Same named equipment, entered more than once. High confidence --
    the OLDER row(s) (all but the highest branch_id) should get
    collapseId = the highest branch_id.
  - probable_renamed_duplicate: 2+ rows share a teid AND an exact FromName/
    ToName bus pair (order-independent) AND the same ckt value, but
    DIFFERENT OP_EQCODE -- i.e. the same physical circuit, renamed (e.g. a
    station upgrade), never linked. The ckt match matters: verified against
    teid=70 ('6429_C' -> '6437_C', both ckt='1', a real rename) that
    bus-pair alone isn't enough -- two GENUINELY DISTINCT parallel circuits
    between the same two buses normally carry different ckt values, and an
    earlier version of this script without the ckt check produced 22 false
    positives (e.g. a transformer-leg case wrongly bucketed here, several
    breaker-named rows) out of 761 candidates. Still lower confidence than
    exact match; worth a human look before applying.

Explicitly NOT flagged (would be wrong to collapse):
  - Real 2-winding-transformer H/L leg pairs (different OP_EQCODE by design
    AND different bus pair) -- see transformer_leg_map.csv for those; they
    are two legitimately distinct rows, not a duplicate.
  - "teid collision" cases where unrelated equipment coincidentally shares
    a teid (confirmed via PTOBRANCH bus numbers in
    analyze_duplicate_teids.py) -- those need the teid value itself
    corrected, not a collapseId link, and are a different kind of fix.

Read-only. Writes only to branch_tracking/output/.
"""
from pathlib import Path

import awconnect
import pandas as pd
from awconnect import db

ISOMARKETID_ERCOT = 6

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_CSV = REPO_ROOT / "output" / "collapseid_fix_candidates.csv"


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


def bus_pair_and_ckt(row):
    a, b = row["FromName"], row["ToName"]
    if pd.isna(a) or pd.isna(b):
        return None
    # ckt distinguishes real parallel circuits between the same bus pair --
    # without it, two genuinely different circuits (e.g. teid=70's
    # '6429_C'/'6437_C', which DO share ckt='1' and are a real rename; but
    # other bus pairs carry multiple distinct ckt values for distinct
    # circuits) would be wrongly flagged as the same renamed element.
    ckt = str(row["ckt"]).strip() if pd.notna(row["ckt"]) else ""
    return (frozenset([str(a), str(b)]), ckt)


def main():
    awconnect.configure("read_only")
    branch = load_branch()
    branch["opeq_norm"] = branch["OP_EQCODE"].astype(str).str.strip().str.upper()
    branch["pair"] = branch.apply(bus_pair_and_ckt, axis=1)

    dup_teids = branch.groupby("teid").filter(lambda g: len(g) > 1)

    rows = []
    for teid, g in dup_teids.groupby("teid"):
        # Tier 1: exact OP_EQCODE match within the group.
        for _, sub in g.groupby("opeq_norm"):
            if len(sub) < 2:
                continue
            winner = sub.sort_values("branchID", ascending=False).iloc[0]
            for _, old in sub.iterrows():
                if old["branchID"] == winner["branchID"]:
                    continue
                rows.append({
                    "teid": teid,
                    "old_branch_id": old["branchID"], "old_branch_name": old["branchName"],
                    "old_op_eqcode": old["OP_EQCODE"],
                    "recommended_collapseid": winner["branchID"],
                    "new_branch_name": winner["branchName"], "new_op_eqcode": winner["OP_EQCODE"],
                    "confidence": "confirmed_exact_duplicate",
                })

        # Tier 2: exact bus-pair match but different OP_EQCODE (rename),
        # skip pairs already covered by tier 1.
        already = {r["old_branch_id"] for r in rows if r["teid"] == teid} | {
            r["recommended_collapseid"] for r in rows if r["teid"] == teid
        }
        remaining = g[~g["branchID"].isin(already)]
        paired = remaining.dropna(subset=["pair"])
        for _, sub in paired.groupby("pair"):
            if len(sub) < 2:
                continue
            if sub["opeq_norm"].nunique() == 1:
                continue  # would've been caught by tier 1
            winner = sub.sort_values("branchID", ascending=False).iloc[0]
            for _, old in sub.iterrows():
                if old["branchID"] == winner["branchID"]:
                    continue
                rows.append({
                    "teid": teid,
                    "old_branch_id": old["branchID"], "old_branch_name": old["branchName"],
                    "old_op_eqcode": old["OP_EQCODE"],
                    "recommended_collapseid": winner["branchID"],
                    "new_branch_name": winner["branchName"], "new_op_eqcode": winner["OP_EQCODE"],
                    "confidence": "probable_renamed_duplicate",
                })

    out = pd.DataFrame(rows)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_CSV, index=False)

    print(f"BRANCH rows scanned: {len(branch)}")
    print(f"Duplicate-teid groups examined: {dup_teids['teid'].nunique()}")
    print(f"Fix candidates found: {len(out)}")
    print(out["confidence"].value_counts().to_string() if len(out) else "(none)")
    print(f"Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
