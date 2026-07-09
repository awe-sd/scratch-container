"""
First-cut in_service_date / retirement_date inference per teid, using
toChangesAllIsos outage records classified by ReasonID.

Discovery (explore_outage_schema.py / explore_outage_lookups.py): the
outageTypeID/toOutageTypeId columns the user originally pointed at are
NULL for every ERCOT (isomarketId=6) row -- but dbo.toReason has exactly
the two codes needed:
    ReasonID = 4  "New Equipment Energization"
    ReasonID = 9  "Retirement of Old Equipment"
toAllIsos was ruled out by the user (hourly-snapshot dump, duplicate-heavy).
toChangesAllIsos is used here instead -- it has a `teid` column directly.

BranchId cross-check (added after inspecting teid=70365 in detail): a
single outage ticket can bundle TWO physically different devices into one
combined clearance (e.g. a new line + a related device commissioned
together), and both rows get stamped with the same `teid` even though only
one of the two `BranchId`s is what that `teid` actually resolves to in
`teid_branch_id_map.csv`. Filtering `toChangesAllIsos` by `teid` alone can
therefore pull in events that don't belong to the mapped equipment -- see
step 4a below.

Method:
  1. Pull every toChangesAllIsos row with ReasonID IN (4, 9), isomarketid=6.
  2a. Sticky actual dates (fixes a real bug found via teid=1743): once a
      revision of a (toOutageIdentifierId, BranchId) ticket records
      actualStartDate/actualEndDate, forward-fill it across that ticket's
      later revisions. Without this, collapsing to the highest toStateId
      (step 2b) could land on a later, purely-administrative revision
      (e.g. status='RatE') whose actual-date fields are blank even though
      an earlier revision genuinely recorded them -- confirmed via
      teid=1743's "Red Gate" energization ticket, whose real 2016-08-05
      actualEndDate was on an earlier revision than its final RatE-status
      revision (which had no actual dates at all). That made the ticket
      look unconfirmed/short when it was really an 8-month, fully-executed
      commissioning -- and caused the wrong device to be picked entirely
      (see the device-name cross-check below).
  2b. A single outage request (toOutageIdentifierId) can appear multiple
      times as it's revised -- collapse to one row per
      (toOutageIdentifierId, BranchId) by keeping the highest toStateId (a
      surrogate that increases with each revision, same pattern as
      ptoBranchID in build_branch_default_status.py). This also surfaces
      the terminal state of that request (a cancellation is itself a later
      revision). BranchId is part of the dedup key, not just
      toOutageIdentifierId, because a bundled-clearance ticket (step 4a)
      can have two BranchId rows sharing the same toStateId -- deduping on
      toOutageIdentifierId alone would arbitrarily keep only one device's
      row (confirmed via teid=70365: an earlier version of this dedup
      sometimes kept the WRONG device's row for a bundled ticket, and
      because load_reason_events() has no ORDER BY, which one "won" wasn't
      even stable across runs).
  3. Drop invalid/cancelled outage requests per the user's explicit
     instruction: exclude any row where CancellationDate IS NOT NULL, or
     where `status`/`ReqStatus` indicates a terminal negative outcome
     (cancelled/withdrawn/rejected/denied/retracted/recalled/annulled/
     terminated -- see INVALID_STATUS_KEYWORDS). A project that got
     cancelled and resubmitted later isn't evidence of anything on its
     own cancelled date.
  4. ERCOT convention (per the user's explicit correction): the boundary
     date that matters differs by ReasonID. For energization (4), the
     equipment isn't actually back in service until the outage that was
     taken to install/commission it CONCLUDES -- so the relevant date is
     the outage's END (actualEndDate, falling back to plannedEndDate).
     For retirement (9), the equipment is considered retired from the
     moment the retirement outage BEGINS -- so the relevant date is the
     outage's START (actualStartDate, falling back to plannedStartDate).
     Prefer rows with real evidence for whichever boundary is relevant
     (actualEndDate populated for energization, actualStartDate populated
     for retirement) over planned-only rows that never actually executed.
  4a. BranchId cross-check: join against teid_branch_id_map.csv's
      confirmed (teid, branch_id) pairs and drop any event row whose
      BranchId doesn't match the mapped branch_id (rows with a NULL
      BranchId pass through unfiltered -- nothing to check them against).
      Confirmed via teid=70365: a combined outage clearance tagged BOTH
      CEDH_OAKC11 (branch_id 60003752) and CEDRHI_OAKC11 (branch_id
      60008059, the one this teid actually maps to) with the same teid.
  4b. Device-name cross-check (added after inspecting teid=1743 and
      teid=317479 in detail, then hardened after teid=113628): the SAME
      BranchId can be referenced under DIFFERENT informal EquipmentName
      strings across different outage tickets/years (unlike the
      bundled-clearance case above, so the BranchId check alone doesn't
      catch it). teid=317479's CIM-confirmed device is a normalized match
      to a 1-minute outage ticket ("6520_G"), while a much longer,
      unrelated chain ("PS0") shares the same teid -- "longest duration
      wins" alone would pick the wrong one. Each event's `EquipmentName`
      is normalized (strip to uppercase alphanumeric only, literal
      placeholders like "BLANK" treated as unknown/NULL) and compared
      against the teid's normalized `OpEqName` and `branch_name` from
      teid_branch_id_map.csv using SUBSTRING containment (`names_relate`),
      not exact equality -- the outage system very commonly records only
      the short device tag (e.g. "T1", "MR2H", "XT4") while CIM's name is
      the full Substation+Device string (e.g. "BKSLESST1", "EXCSWMR2H").
      An initial exact-equality version of this check was validated
      against a sample of 1,104 initially-dropped teids: 88% (977) were
      exactly this abbreviation pattern, a false positive that would have
      discarded the large majority of genuinely correct energization
      evidence -- exact equality was far too strict. A CONFIRMED mismatch
      (both names known, and neither contains the other) is dropped
      outright, the same way a BranchId mismatch is -- confirmed via
      teid=113628, whose CIM device is "AT2H" (a transformer winding) but
      EVERY one of its "Retirement of Old Equipment" tickets tags
      EquipmentName="CB_1814" (a circuit breaker): a breaker being
      swapped/retired doesn't mean the transformer position it protects
      was retired. No matching evidence should mean no evidence, not
      "trust whatever's left" (an earlier version fell back to using
      everything when nothing matched). When there IS remaining evidence
      after this filter and multiple genuinely separate chains exist
      (step 6), chains with a confirmed name match are still preferred as
      a secondary tie-break.
  5. Chain detection (added after inspecting teid=527244 in detail): a
     single real-world energization/retirement often spans MULTIPLE
     outage tickets, not because it was cancelled and resubmitted, but
     because each ticket has a duration limit and expires while work
     (commissioning, etc.) is still ongoing. Consecutive events (sorted by
     their start date, regardless of which boundary step 4 reports) whose
     gap is <= CHAIN_GAP_TOLERANCE are collapsed into one chain. For
     energization, the chain's OVERALL END is used; confirmed via
     teid=552333 (the user identified the equipment as coming into
     service in December 2022, the chain's END, not its January START).
     For retirement, the chain's FIRST start is used.
  6. For GENUINELY separate CHAINS (a real gap between them, not just
     ticket-expiry churn within one): first restrict to chains with a
     device-name match (step 4b) if any exist. Among the remaining
     candidates -- for energization, pick the LONGEST-duration chain
     (confirmed via teid=552333); for retirement, take the LATEST chain
     (a later valid attempt supersedes an earlier one).
  7. Per teid: in_service_date = resolved ReasonID=4 date; retirement_date
     = resolved ReasonID=9 date. Default to 1990-01-01 / 2099-12-31 (the
     user's stated defaults) when no valid matching event exists.
  7a. Mis-tag correction (added after inspecting teid=821 and teid=654439
      in detail, per the user's explicit read): if the resolved retirement
      predates the resolved energization AND they resolve to the SAME
      device (normalized EquipmentName match), the retirement was never
      real -- it's an outage that got incorrectly tagged "Retirement of
      Old Equipment" and was corrected by submitting a proper
      energization ticket for the same equipment shortly after (both
      teid=821 and teid=654439 show the outage's own EquipmentName
      matching exactly between the "retirement" and the energization that
      immediately followed it). The retirement_date is reverted to the
      2099-12-31 default in this case. When the devices DIFFER instead
      (confirmed via teid=121320/185126/198761/207211/317479: the
      retirement's device name is a clearly different, old piece of
      equipment -- e.g. literally named "DELETE" or "OLD1303_SW" -- while
      the energization's device matches the teid's current CIM name),
      that's a genuine sequential asset replacement, not an error --
      surfaced as the informational `teid_reused_after_retirement` flag
      rather than corrected or treated as a data-quality problem.
  7b. Retirement-vs-status contradiction correction (added after digging
      into teid=1019/teid=3830, then the 2026 cohort broadly): joins
      branch_default_status.csv's `implied_default_status` (recent
      PTOBRANCH auction-snapshot evidence, far more direct/recent than a
      loosely-coded outage reason). 83% of all resolved retirements
      initially contradicted a Closed status -- including single-ticket
      retirements dated a full DECADE before still showing 100% Closed in
      2025-2026 snapshots, and clusters of different teids sharing the
      exact same retirement timestamp in tight name-related groups (one
      transformer's H/L legs, several circuits at the same substation) --
      a signature of coordinated substation-wide maintenance/equipment-
      replacement work being tagged "Retirement of Old Equipment," not
      individual permanent decommissioning. When status evidence is
      CONFIDENT (`status_review_flag='clear_majority'`, Closed, backed by
      >= STATUS_CONTRADICTION_MIN_ROWS recent snapshots), the retirement
      is reverted to the default. Weaker contradictions (a "mixed" status
      split, or too few status rows) are left as-is but flagged
      `retirement_status_uncertain` rather than silently corrected.
  8. review_flag surfaces cases that still need a human look after all of
     the above: multiple surviving CHAINS with real evidence (genuinely
     ambiguous), events found but all planned-only (no actual dates,
     weaker evidence), a retirement event with no corresponding
     energization (expected for most of the grid, built before this
     outage history), `teid_reused_after_retirement` (informational,
     not an error -- see step 7a), or `evidence_dropped_wrong_device`
     (also informational: zero surviving evidence in either direction,
     but only because real outage evidence existed and was correctly
     dropped by step 4b for describing a different device -- distinct
     from a teid that simply never had any raw ReasonID=4/9 records at
     all, even though both land on the same default dates). Per the
     user's guidance, the pipeline still resolves a best-guess date for
     every flagged case rather than blocking on it -- the flagged subset
     is also written out separately to inservice_retirement_review_flags.csv
     as a manual-review worklist.

Special case NOT modeled here (per the user, re: teid=555249): a unit that
was generating, went out of service, and is later coming back can have its
return-to-service tracked via a NEW "energization" outage ticket even
though the equipment isn't literally brand-new -- ERCOT/TSP practice
reuses the energization reason code for restorations, not just true new
construction. This looks identical to a genuine second energization in
this data and isn't distinguished; flagged for review like any other
multi-chain case rather than guessed at.

Known limitations (not solved here, a stopgap for the user to refine):
  - Only as complete as toChangesAllIsos' history -- for the vast
    majority of teids (built decades ago), there's no ReasonID=4 event in
    this data at all, so in_service_date falls back to the 1990-01-01
    default. This does NOT mean the equipment came into service in 1990;
    it means we have no outage-based evidence either way.
  - The cancelled/terminated keyword list is derived from dbo.toStatus's
    contents (see explore_outage_lookups.py) and applied as a substring
    match on `status`/`ReqStatus` -- if ERCOT starts using new status
    text not covered by these keywords, a cancelled outage could slip
    through as valid evidence.
  - The BranchId cross-check only catches a mismatch when the event's own
    BranchId is populated; the device-name cross-check only catches a
    mismatch when EquipmentName is populated and normalizes to something
    comparable -- both pass rows through unfiltered when there's nothing
    to check against.
  - Events for teids NOT in teid_branch_id_map.csv at all (rather than a
    BranchId/name mismatch within a mapped teid) are dropped with a
    warning count, not silently lost -- see out_of_scope_count in output.
  - multiple_confirmed_retirement_events is not yet investigated as
    deeply as the energization side (see investigate_retirement_flags.py
    for a first pass -- multi-step decommissioning processes, not
    mis-tagging or bundling, based on a sample of 5 of the 11 teids).

Read-only. Writes only to branch_tracking/output/.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from branch_tracking.pipeline.config import (  # noqa: E402
    ISOMARKETID_ERCOT, REASON_NEW_EQUIPMENT, REASON_RETIREMENT,
)
from branch_tracking.pipeline.dates import resolve_dates  # noqa: E402

import awconnect
import pandas as pd
from awconnect import db

REPO_ROOT = Path(__file__).resolve().parents[1]
TEID_MAP_CSV = REPO_ROOT / "output" / "teid_branch_id_map.csv"
STATUS_CSV = REPO_ROOT / "output" / "branch_default_status.csv"
OUTPUT_CSV = REPO_ROOT / "output" / "teid_inservice_retirement_dates.csv"
REVIEW_CSV = REPO_ROOT / "output" / "inservice_retirement_review_flags.csv"


def load_reason_events():
    return db.getDfFromAwDb(
        f"""
        SELECT teid, BranchId, EquipmentName, ReasonID, toOutageIdentifierId,
               toStateId, plannedStartDate, plannedEndDate, actualStartDate,
               actualEndDate, CancellationDate, CancellationReason,
               status, ReqStatus
        FROM AW.dbo.toChangesAllIsos
        WHERE isoMarketId = {ISOMARKETID_ERCOT}
          AND ReasonID IN ({REASON_NEW_EQUIPMENT}, {REASON_RETIREMENT})
          AND teid IS NOT NULL
        """
    )


def main():
    awconnect.configure("read_only")

    teid_map = pd.read_csv(TEID_MAP_CSV)
    status = pd.read_csv(STATUS_CSV)
    events = load_reason_events()

    # All inference logic lives in branch_tracking.pipeline.dates (moved
    # there verbatim -- see this module's docstring for the method). This
    # wrapper owns only I/O: the DB pull above, the CSV writes and the
    # diagnostic/summary prints below.
    resolved = resolve_dates(events, teid_map, status)
    result = resolved["result"]
    mismatch_dump = resolved["mismatch_dump"]
    counts = resolved["counts"]
    diagnostics = resolved["diagnostics"]

    n_missing_end = counts["n_missing_end"]
    if n_missing_end:
        affected_teids = diagnostics["missing_end_teids"]
        print(
            f"WARNING: {n_missing_end} events (teids: {len(affected_teids)}) have neither "
            f"actualEndDate nor plannedEndDate populated -- event_end_date is NaT for these."
        )
        print(f"Sample affected teids: {affected_teids.head(20).tolist()}")
        print()

    print("=== status/ReqStatus diagnostic (raw events, before dedup/filtering) ===")
    print("status value_counts:")
    print(diagnostics["status_value_counts"].to_string())
    print("ReqStatus value_counts:")
    print(diagnostics["reqstatus_value_counts"].to_string())
    print()

    mismatch_dump.to_csv(REPO_ROOT / "output" / "device_name_mismatches.csv", index=False)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_CSV, index=False)

    review = result[result["review_flag"] != "ok"].copy()
    review.to_csv(REVIEW_CSV, index=False)

    print(f"Reason-coded events pulled (ReasonID 4 or 9, isomarketid=6): {counts['n_before_status_filter']}")
    print(f"Dropped as cancelled/terminated (CancellationDate set or status keyword match): {counts['n_cancelled']}")
    print(f"Distinct teids in valid events, not in teid_branch_id_map (dropped): {counts['out_of_scope_count']}")
    print(f"Dropped as BranchId mismatch (event's BranchId != teid's mapped branch_id): {counts['n_branch_mismatch']}")
    print(f"Dropped as confirmed device-name mismatch (event's EquipmentName != teid's mapped device): {counts['n_device_name_mismatch']}")
    print(f"Retirements corrected as same-device mis-tags (reverted to default): {counts['n_mistag_corrected']}")
    print(f"Retirements corrected as status-contradicted (confident Closed, reverted to default): {counts['n_status_corrected']}")
    print(f"Retirements left flagged as status-uncertain (weaker contradiction, not auto-corrected): {int(result['retirement_status_uncertain'].sum())}")
    print(f"Teids in scope: {len(result)}")
    print(f"  with a valid energization event: {(result['in_service_date_source'] == 'energization_outage').sum()}")
    print(f"  with a valid retirement event: {(result['retirement_date_source'] == 'retirement_outage').sum()}")
    print()
    print(result["review_flag"].value_counts().to_string())
    print(f"Wrote {OUTPUT_CSV}")
    print(f"Wrote {REVIEW_CSV} ({len(review)} flagged teids for manual review)")


if __name__ == "__main__":
    main()
