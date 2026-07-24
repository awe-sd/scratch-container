"""
Build a simple teid -> branch_id mapping CSV.

Source of the teid list: the CIM July model export (data/CIM_..._TeidMap.csv),
filtered to PsseType in ('Branch', 'Transformer'), excluding NodeType in
('Breaker', 'Disconnector') -- PsseType 'Branch' lumps together
ACLineSegment, SeriesCompensator, Breaker, and Disconnector CIM elements,
but breakers/disconnectors are switching devices, not the lines/transformers
the tracking table is meant to cover.

Source of the branch_id lookup: SQL Server dbo.BRANCH (awconnect.db),
isomarketid = 6 (ERCOT, always). Rows with a non-NULL collapseId are
excluded before the join -- collapseId points at the branchID that
superseded this row (confirmed via scripts/analyze_duplicate_teids.py), so
a populated collapseId means "this row is stale, use the newer branchID
instead." This alone doesn't resolve all BRANCH.teid duplicates (only
~12% of duplicate-teid groups have a collapseId link at all -- see
analyze_duplicate_teids.py), but it's a clean, unambiguous first pass
before dealing with the rest.

BRANCH.teid is still NOT enforced unique even after that filter, so a
single CIM teid can match zero, one, or multiple branch_id rows -- all
matches are kept and flagged rather than silently picking one.

Secondary check / disambiguator: the CIM CSV's OpEqName and BRANCH's
OP_EQCODE both identify the equipment element and are directly comparable
(92.6% exact-match rate on the already-1:1 rows, confirming the teid join
is sound). Two uses:
  1. QA flag (`opeq_agrees`) on every row, including 1:1 matches -- a
     mismatch on a "matched" row is worth a manual look even though the
     teid join was unambiguous.
  2. Duplicate resolver -- for a duplicate_match teid, if exactly ONE of
     the candidate branch_ids has OP_EQCODE == OpEqName, that's almost
     certainly the correct one. Resolves ~79% of the remaining duplicates
     (880/1116 as of the collapseId-filtered baseline).
  3. Exact-duplicate resolver -- if MORE THAN ONE candidate agrees with
     OpEqName, they all necessarily share the same OP_EQCODE as each other
     (since OpEqName is a single value per CIM teid) -- i.e. the same
     physical element was entered into BRANCH more than once with no
     collapseId link between the copies. Any non-agreeing candidate in
     that group is dropped as clearly wrong first; among the remaining
     (agreeing) copies, the highest branch_id is kept as a "latest
     surrogate id" tiebreak (same convention used for PTOBRANCH dedup in
     analyze_duplicate_teids.py).
  4. Fuzzy-match resolver -- for the remaining zero-agree groups, exact
     string equality fails but the strings are still often clearly the
     same element under a different naming convention (e.g. 'AXFMR' vs
     'MR', a trailing '_H'/'-H' side marker). Calibrated using the 725
     already-1:1-matched rows where OP_EQCODE != OpEqName exactly but the
     teid join is known correct: their SequenceMatcher ratio has median
     ~0.87, with only 8/725 below 0.5. A group is resolved when the top
     candidate's ratio is >= 0.6 AND beats the runner-up by >= 0.15 --
     both a quality floor and a separation requirement, since a high but
     closely-tied ratio between two candidates means the fuzzy match isn't
     actually discriminating between them. This is a naming-similarity
     signal, not a recency one -- unlike step 3, the winning candidate is
     NOT necessarily the higher branch_id, because here the candidates are
     genuinely different elements and the point is picking the *correct*
     one, not the newest copy of the same one.
  5. High-side + latest-id catch-all -- teid is ERCOT's authoritative
     per-component id (confirmed by the user), so the grain here is teid:
     1:1, always. Everything still duplicate_match after steps 2-4 turned
     out to be Transformer rows (100% of the 176 as of the prior baseline):
     the two legs of one 2-winding transformer, either literally named
     '..._H'/'..._L' or using a numeric leg suffix instead (e.g.
     'AXFMR11'/'AXFMR12', 'XFMR21'/'XFMR22' -- verified via matching
     FromName/ToName bus pairs on both rows, same physical asset, NOT
     separate parallel-unit transformers as first suspected).
     Rule: keep the high-side ('_H'/'-H'/'HIGH'/'HISIDE') row where the
     group has one -- this only fires for the literal H/L naming style,
     since the numeric-suffix style has nothing for the regex to match.
     Whatever's left after that (a single high-side row, or -- for the
     numeric-suffix style and any other unresolved case -- the full
     original candidate set) is resolved by keeping the highest (latest)
     branch_id. This was verified against all 176 by checking whether
     every candidate in a group shares the same From/To bus pair: 159/176
     do outright; 17 more differ only because of a station/bus rename
     (e.g. 'ABSO'->'SOUTHABI', 'RADM'->'RADIUM') where the latest row is
     correctly the post-rename one. A handful (teid 2290, 39798, 279187,
     280262) don't fit even that -- see thoughts.md Investigation Findings
     for the manual-review detail on those.

Read-only. Writes only to branch_tracking/output/ -- never touches the
live database beyond a SELECT.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from branch_tracking.pipeline.mapping import resolve_duplicates  # noqa: E402
from branch_tracking.pipeline.config import ISOMARKETID_ERCOT  # noqa: E402

import awconnect
import pandas as pd
from awconnect import db

REPO_ROOT = Path(__file__).resolve().parents[1]
CIM_CSV = REPO_ROOT / "data" / "CIM_Jul_ML1_1_07142026_Redacted_20260801-003000_TeidMap.csv"
OUTPUT_CSV = REPO_ROOT / "output" / "teid_branch_id_map.csv"


def load_cim_branch_elements():
    df = pd.read_csv(CIM_CSV)
    branch_like = df[
        df["PsseType"].isin(["Branch", "Transformer"])
        & ~df["NodeType"].isin(["Breaker", "Disconnector"])
    ].copy()
    branch_like = branch_like.rename(columns={"TransmissionElementId": "teid"})
    return branch_like[
        [
            "teid",
            "RdfId",
            "PsseType",
            "NodeType",
            "CircuitIdentifier",
            "Name",
            "BusNumber1",
            "BusName1",
            "Substation1",
            "BusNumber2",
            "BusName2",
            "Substation2",
            "EquipmentName",
            "OpEqName",
        ]
    ]


def load_branch_table():
    return db.getDfFromAwDb(
        f"""
        SELECT teid, branchID, branchName, b1, b2, ckt, DeviceType,
               FromName, ToName, OP_EQCODE, EQNAME
        FROM dbo.BRANCH
        WHERE isomarketid = {ISOMARKETID_ERCOT}
          AND collapseId IS NULL
        """
    )


def main():
    awconnect.configure("read_only")

    cim = load_cim_branch_elements()
    branch = load_branch_table().rename(
        columns={
            "branchID": "branch_id",
            "branchName": "branch_name",
        }
    )

    merged = cim.merge(branch, on="teid", how="left", indicator=True)

    match_counts = merged.groupby("teid")["branch_id"].transform(
        lambda s: s.notna().sum()
    )
    merged["match_status"] = "matched"
    merged.loc[merged["_merge"] == "left_only", "match_status"] = "unmatched"
    merged.loc[match_counts > 1, "match_status"] = "duplicate_match"
    merged = merged.drop(columns=["_merge"])

    merged["opeq_agrees"] = merged["OP_EQCODE"].astype(str).str.strip() == merged[
        "OpEqName"
    ].astype(str).str.strip()

    # Layered duplicate-resolution passes (opeqcode-exact -> exact-duplicate
    # collapse -> fuzzy -> high-side + latest-id) live in
    # pipeline/mapping.py:resolve_duplicates; see its module docstring.
    merged = resolve_duplicates(merged)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUTPUT_CSV, index=False)

    # Report per distinct input teid, not per output row -- an unresolved
    # duplicate_match teid produces multiple output rows (one per candidate
    # branch_id), which inflates row counts and isn't the number that
    # matters here.
    status_by_teid = merged.groupby("teid")["match_status"].first()
    counts = status_by_teid.value_counts()
    total = len(status_by_teid)

    print(f"CIM branch/transformer rows (distinct teid): {total}")
    for status in (
        "matched",
        "duplicate_resolved_by_opeqcode",
        "duplicate_resolved_exact_duplicate",
        "duplicate_resolved_by_fuzzy_match",
        "duplicate_resolved_by_latest_id",
        "unmatched",
    ):
        n = counts.get(status, 0)
        print(f"  {status}: {n} ({n / total:.1%})")
    print(f"Wrote {OUTPUT_CSV} ({len(merged)} output rows, unresolved duplicate_match teids expand to >1 row)")


if __name__ == "__main__":
    main()
