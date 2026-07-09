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
from functools import partial
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from branch_tracking.pipeline.naming import (  # noqa: E402
    normalize_name, names_relate,
)

import awconnect
import pandas as pd
from awconnect import db

ISOMARKETID_ERCOT = 6
REASON_NEW_EQUIPMENT = 4
REASON_RETIREMENT = 9

DEFAULT_IN_SERVICE_DATE = pd.Timestamp("1990-01-01")
DEFAULT_RETIREMENT_DATE = pd.Timestamp("2099-12-31")

# Consecutive events (sorted by date) whose gap is within this tolerance are
# treated as one continuous process re-ticketed on expiry, not separate
# events. teid=527244's chain had 0-1 minute gaps between tickets; a few
# days of buffer covers a crew resubmitting after a weekend without risking
# false-chaining of genuinely unrelated events months/years apart.
CHAIN_GAP_TOLERANCE = pd.Timedelta(days=3)

# Substring match (case-insensitive) against `status`/`ReqStatus` -- derived
# from dbo.toStatus's contents (Cancelled/Canceled/Cancl/Cancelled by
# Company, Withdrawn/Withd, Rejct, Denied, Retracted, Recalled, Annulled,
# Terminated). CancellationDate IS NOT NULL is checked separately/additionally.
INVALID_STATUS_KEYWORDS = (
    "cancel", "cancl", "withdraw", "withd", "reject", "rejct", "denied",
    "retract", "recall", "annul", "terminat",
)

# Minimum recent PTOBRANCH status rows required to trust a Closed-status
# contradiction enough to auto-revert a retirement_date -- a single
# snapshot (n_status_rows=1) showing Closed isn't strong enough evidence
# on its own, even if pct_closed=1.0 for that one row.
STATUS_CONTRADICTION_MIN_ROWS = 5

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


def is_invalid_status(row):
    if pd.notna(row["CancellationDate"]):
        return True
    for col in ("status", "ReqStatus"):
        val = row[col]
        if pd.notna(val) and any(kw in str(val).lower() for kw in INVALID_STATUS_KEYWORDS):
            return True
    return False


def assign_chain_ids(tier):
    """Sorted-by-date events get grouped into chains: a new chain starts
    only when the gap since the running chain's furthest end exceeds
    CHAIN_GAP_TOLERANCE. Returns a chain_id array aligned to `tier`'s
    (date-sorted) row order, monotonically increasing (chain_id=1 is
    chronologically earliest)."""
    chain_ids = []
    current_chain_id = 0
    current_chain_end = None
    for _, row in tier.iterrows():
        if current_chain_end is not None and (row["event_date"] - current_chain_end) <= CHAIN_GAP_TOLERANCE:
            current_chain_end = max(current_chain_end, row["event_end_date"])
        else:
            current_chain_id += 1
            current_chain_end = row["event_end_date"]
        chain_ids.append(current_chain_id)
    return chain_ids


def resolve_by_chain(group, boundary):
    """boundary='end' for energization (ERCOT convention: in service once
    the commissioning outage CONCLUDES), boundary='start' for retirement
    (retired from the moment the retirement outage BEGINS). Prefer rows
    with real evidence for that boundary over planned-only rows. Collapse
    consecutive events into chains using the ticket timeline. Among
    genuinely separate chains, prefer ones with a device-name match (see
    module docstring step 4b) before applying the reason-specific
    tie-break: longest duration for energization, latest chain for
    retirement. Also returns the chosen chain's representative device
    name, used by main()'s mis-tag correction step."""
    if boundary == "end":
        strong_tier = group[group["actualEndDate"].notna()]
    else:
        strong_tier = group[group["actualStartDate"].notna()]
    tier = strong_tier if len(strong_tier) else group
    tier = tier.sort_values("event_date")

    tier = tier.assign(chain_id=assign_chain_ids(tier))
    chain_has_name_match = tier.groupby("chain_id")["device_name_match"].any()
    matching_chain_ids = set(chain_has_name_match[chain_has_name_match].index)

    if boundary == "end":
        chain_summary = tier.groupby("chain_id").agg(
            chain_start=("event_date", "min"), chain_end=("event_end_date", "max")
        )
        chain_summary["duration"] = chain_summary["chain_end"] - chain_summary["chain_start"]
        candidates = chain_summary.loc[list(matching_chain_ids)] if matching_chain_ids else chain_summary
        chosen_chain_id = candidates["duration"].idxmax()
        chosen_date = chain_summary.loc[chosen_chain_id, "chain_end"]
    else:
        chain_dates = tier.groupby("chain_id")["event_date"].min().sort_index()
        candidate_ids = [cid for cid in chain_dates.index if cid in matching_chain_ids] or list(chain_dates.index)
        chosen_chain_id = max(candidate_ids)
        chosen_date = chain_dates.loc[chosen_chain_id]

    chosen_rows = tier[tier["chain_id"] == chosen_chain_id]
    device_names = chosen_rows["equip_name_norm"].dropna()
    device_name = device_names.mode().iloc[0] if len(device_names) else None

    return pd.Series({
        "event_date": chosen_date,
        "n_valid_events": len(group),
        "n_actual_tier_events": len(strong_tier),
        "n_chains": len(chain_has_name_match),
        "device_name": device_name,
    })


def main():
    awconnect.configure("read_only")

    teid_map = pd.read_csv(TEID_MAP_CSV)
    legit_map = (
        teid_map[teid_map["match_status"] != "unmatched"]
        [["teid", "branch_id", "OpEqName", "branch_name"]]
        .drop_duplicates()
    )
    legit_map["branch_id"] = legit_map["branch_id"].astype(int)
    legit_map["cim_opeqname_norm"] = legit_map["OpEqName"].apply(normalize_name)
    legit_map["cim_branchname_norm"] = legit_map["branch_name"].apply(normalize_name)
    legit_map = legit_map[["teid", "branch_id", "cim_opeqname_norm", "cim_branchname_norm"]]
    legit_teids = set(legit_map["teid"].unique())

    status = pd.read_csv(STATUS_CSV)[
        ["teid", "default_status_majority", "pct_closed", "n_status_rows", "review_flag"]
    ].rename(columns={"review_flag": "status_review_flag"})

    events = load_reason_events()

    # Sticky actual dates (see module docstring step 2a): forward-fill
    # actualStartDate/actualEndDate within each (toOutageIdentifierId,
    # BranchId) ticket, sorted by toStateId, so a later purely-
    # administrative revision can't erase an earlier revision's real
    # evidence. dropna=False so NULL-BranchId tickets still get grouped
    # (as their own group) instead of being excluded from the fill.
    events = events.sort_values(["toOutageIdentifierId", "BranchId", "toStateId"])
    events[["actualStartDate", "actualEndDate"]] = events.groupby(
        ["toOutageIdentifierId", "BranchId"], dropna=False
    )[["actualStartDate", "actualEndDate"]].ffill()

    events["equip_name_norm"] = events["EquipmentName"].apply(normalize_name)
    events["event_date"] = events["actualStartDate"].fillna(events["plannedStartDate"])
    # Fallback chain: actualEndDate -> plannedEndDate. No further fallback
    # to the event's own start -- a ticket with neither an actual nor a
    # planned end date has no real evidence of when it concluded, and
    # silently treating it as zero-duration would fabricate a boundary
    # date. Left as NaT instead; skipna in the chain-max/min aggregations
    # naturally handle it, and a teid whose only evidence has no planned
    # end falls through to the 1990-01-01/2099-12-31 default.
    events["event_end_date"] = events["actualEndDate"].fillna(events["plannedEndDate"])
    events = events.dropna(subset=["event_date"])

    n_missing_end = int(events["event_end_date"].isna().sum())
    if n_missing_end:
        affected_teids = events.loc[events["event_end_date"].isna(), "teid"].drop_duplicates()
        print(
            f"WARNING: {n_missing_end} events (teids: {len(affected_teids)}) have neither "
            f"actualEndDate nor plannedEndDate populated -- event_end_date is NaT for these."
        )
        print(f"Sample affected teids: {affected_teids.head(20).tolist()}")
        print()

    print("=== status/ReqStatus diagnostic (raw events, before dedup/filtering) ===")
    print("status value_counts:")
    print(events["status"].value_counts(dropna=False).to_string())
    print("ReqStatus value_counts:")
    print(events["ReqStatus"].value_counts(dropna=False).to_string())
    print()

    # Collapse revisions of the same outage request to its latest toStateId
    # -- also surfaces the terminal state (a cancellation is itself a later
    # revision, so this keeps the row that shows it). Dedup key is
    # (toOutageIdentifierId, BranchId), NOT toOutageIdentifierId alone -- see
    # module docstring step 2b.
    events = (
        events.sort_values("toStateId", ascending=False)
        .drop_duplicates(subset=["toOutageIdentifierId", "BranchId"], keep="first")
    )

    n_before_status_filter = len(events)
    events["invalid"] = events.apply(is_invalid_status, axis=1)
    n_cancelled = int(events["invalid"].sum())
    valid_events = events[~events["invalid"]].copy()

    in_teid_scope = valid_events[valid_events["teid"].isin(legit_teids)]
    out_of_scope_count = valid_events["teid"].nunique() - in_teid_scope["teid"].nunique()

    # BranchId cross-check (module docstring step 4a): only drop a row when
    # BOTH BranchIds are known and they disagree.
    merged = in_teid_scope.merge(legit_map, on="teid", how="left")
    branch_mismatch = (
        merged["BranchId"].notna() & merged["branch_id"].notna()
        & (merged["BranchId"] != merged["branch_id"])
    )
    n_branch_mismatch = int(branch_mismatch.sum())
    in_scope = merged[~branch_mismatch].copy()

    # Device-name cross-check (module docstring step 4b): does this event's
    # own EquipmentName match the teid's CIM-confirmed OpEqName/branch_name?
    # A CONFIRMED mismatch (both names known and they disagree) is dropped
    # outright, the same way a BranchId mismatch is above -- confirmed via
    # teid=113628: EVERY one of its "Retirement of Old Equipment" tickets
    # tags EquipmentName="CB_1814" (a circuit breaker), never the teid's
    # actual CIM device "AT2H" (a transformer winding). A breaker being
    # swapped/retired doesn't mean the transformer position it protects
    # was retired -- the earlier version of this check only PREFERRED a
    # name-matching chain when one existed, but fell back to using
    # everything (including confirmed-wrong-device evidence) when nothing
    # matched, which is exactly backwards: no matching evidence should
    # mean no evidence, not "trust whatever's left."
    cim_name_known = in_scope["cim_opeqname_norm"].notna() | in_scope["cim_branchname_norm"].notna()
    device_name_match = in_scope.apply(
        lambda row: names_relate(row["equip_name_norm"], row["cim_opeqname_norm"])
        or names_relate(row["equip_name_norm"], row["cim_branchname_norm"]),
        axis=1,
    )
    device_name_confirmed_mismatch = (
        in_scope["equip_name_norm"].notna() & cim_name_known & ~device_name_match
    )
    n_device_name_mismatch = int(device_name_confirmed_mismatch.sum())

    # Persist what got dropped -- per the user, "ok" mixes verified-good
    # teids with ones that simply have zero evidence (e.g. because their
    # only outage evidence was a confirmed wrong-device mismatch, like
    # teid=113628's breaker), and those two cases shouldn't be silently
    # indistinguishable. This lets a teid's dropped evidence be traced
    # and cross-checked against the CIM model file directly.
    mismatch_dump = in_scope[device_name_confirmed_mismatch][
        ["teid", "ReasonID", "BranchId", "EquipmentName", "equip_name_norm",
         "cim_opeqname_norm", "cim_branchname_norm", "plannedStartDate",
         "actualStartDate", "actualEndDate"]
    ]
    mismatch_dump.to_csv(REPO_ROOT / "output" / "device_name_mismatches.csv", index=False)
    mismatch_teids = set(mismatch_dump["teid"].unique())

    in_scope = in_scope[~device_name_confirmed_mismatch].copy()
    in_scope["device_name_match"] = device_name_match[~device_name_confirmed_mismatch]

    energization = in_scope[in_scope["ReasonID"] == REASON_NEW_EQUIPMENT]
    retirement = in_scope[in_scope["ReasonID"] == REASON_RETIREMENT]

    energization_agg = energization.groupby("teid").apply(
        partial(resolve_by_chain, boundary="end"), include_groups=False
    )
    energization_agg = energization_agg.rename(columns={
        "event_date": "in_service_date",
        "n_valid_events": "n_energization_events",
        "n_actual_tier_events": "n_energization_actual_events",
        "n_chains": "n_energization_chains",
        "device_name": "energization_device_name",
    })
    retirement_agg = retirement.groupby("teid").apply(
        partial(resolve_by_chain, boundary="start"), include_groups=False
    )
    retirement_agg = retirement_agg.rename(columns={
        "event_date": "retirement_date",
        "n_valid_events": "n_retirement_events",
        "n_actual_tier_events": "n_retirement_actual_events",
        "n_chains": "n_retirement_chains",
        "device_name": "retirement_device_name",
    })

    result = pd.DataFrame({"teid": sorted(legit_teids)}).set_index("teid")
    result = result.join(energization_agg).join(retirement_agg).join(status.set_index("teid"))

    for col in ("n_energization_events", "n_energization_actual_events", "n_energization_chains",
                "n_retirement_events", "n_retirement_actual_events", "n_retirement_chains"):
        result[col] = result[col].fillna(0).astype(int)

    result["in_service_date_source"] = result["in_service_date"].notna().map(
        {True: "energization_outage", False: "default"}
    )
    result["retirement_date_source"] = result["retirement_date"].notna().map(
        {True: "retirement_outage", False: "default"}
    )
    result["in_service_date"] = result["in_service_date"].fillna(DEFAULT_IN_SERVICE_DATE)
    result["retirement_date"] = result["retirement_date"].fillna(DEFAULT_RETIREMENT_DATE)

    # Mis-tag correction (module docstring step 7a): a retirement before its
    # own teid's energization, for the SAME device, means the retirement was
    # never real -- confirmed via teid=821/654439. Revert it to the default.
    same_device_before_energization = (
        (result["retirement_date_source"] == "retirement_outage")
        & (result["in_service_date_source"] == "energization_outage")
        & (result["retirement_date"] < result["in_service_date"])
        & result["retirement_device_name"].notna()
        & (result["retirement_device_name"] == result["energization_device_name"])
    )
    n_mistag_corrected = int(same_device_before_energization.sum())
    result.loc[same_device_before_energization, "retirement_date"] = DEFAULT_RETIREMENT_DATE
    result.loc[same_device_before_energization, "retirement_date_source"] = "default"

    # Retirement-vs-status contradiction correction (added after digging
    # into teid=1019 and teid=3830 in detail, then confirming the pattern
    # across the 2026 cohort): ReasonID=9 ("Retirement of Old Equipment")
    # is used far more loosely in ERCOT's outage data than "this branch
    # was permanently decommissioned" -- 83% of all resolved retirements
    # initially contradicted implied_default_status (recent PTOBRANCH
    # auction snapshots showing the branch still Closed). Digging into
    # the 2026 cohort specifically showed clusters of DIFFERENT teids
    # sharing the exact same retirement timestamp in tight name-related
    # groups (e.g. teid=280078/280216 = one transformer's H/L legs, both
    # retired at the same minute; teid=104/120/100 all at the same
    # substation) -- a signature of coordinated substation-wide
    # maintenance/equipment-replacement work, not individual permanent
    # retirements. When status evidence is CONFIDENT (a clear majority,
    # not a roughly-even mixed split, backed by at least
    # STATUS_CONTRADICTION_MIN_ROWS recent snapshots) that the branch is
    # still Closed, the retirement is reverted to the default -- status
    # evidence from recent, direct auction-model snapshots is far more
    # reliable than a loosely-coded outage reason on its own. Weaker
    # contradictions (a "mixed" status split, or too few status rows to
    # trust) are left as-is but flagged `retirement_status_uncertain`
    # for manual review rather than silently corrected or ignored.
    status_confidently_closed = (
        (result["default_status_majority"] == "Closed")
        & (result["status_review_flag"] == "clear_majority")
        & (result["n_status_rows"] >= STATUS_CONTRADICTION_MIN_ROWS)
    )
    retirement_contradicted_by_status = (
        (result["retirement_date_source"] == "retirement_outage") & status_confidently_closed
    )
    n_status_corrected = int(retirement_contradicted_by_status.sum())
    result.loc[retirement_contradicted_by_status, "retirement_date"] = DEFAULT_RETIREMENT_DATE
    result.loc[retirement_contradicted_by_status, "retirement_date_source"] = "default"

    result["retirement_status_uncertain"] = (
        (result["retirement_date_source"] == "retirement_outage")
        & (result["default_status_majority"] == "Closed")
        & ~status_confidently_closed
    )

    # Per the user: a teid with zero surviving evidence in either direction
    # (both dates defaulted) is not homogeneous -- most never had any raw
    # ReasonID=4/9 records at all (equipment older than this outage
    # history), but some (confirmed via a CIM cross-check: all 102 sampled
    # exist in the current July 2026 model, split ~evenly Line/Transformer
    # across 60-345kV) had REAL outage evidence that got correctly dropped
    # because it described a different device (e.g. teid=113628's breaker).
    # Both groups keep the same default dates (that assumption is still
    # right), but the latter gets its own flag rather than blending into
    # generic `ok`, so it stays traceable back to device_name_mismatches.csv.
    result["had_dropped_evidence"] = result.index.isin(mismatch_teids)

    def flag(row):
        if row["retirement_date"] < row["in_service_date"]:
            return "teid_reused_after_retirement"
        if row["n_energization_chains"] > 1:
            return "multiple_confirmed_energization_events"
        if row["n_retirement_chains"] > 1:
            return "multiple_confirmed_retirement_events"
        if row["retirement_status_uncertain"]:
            return "retirement_status_uncertain"
        if row["in_service_date_source"] == "energization_outage" and row["n_energization_actual_events"] == 0:
            return "energization_planned_not_actualized"
        if row["retirement_date_source"] == "retirement_outage" and row["n_retirement_actual_events"] == 0:
            return "retirement_planned_not_actualized"
        if row["retirement_date_source"] == "retirement_outage" and row["in_service_date_source"] == "default":
            return "retirement_found_no_energization"
        if (
            row["in_service_date_source"] == "default"
            and row["retirement_date_source"] == "default"
            and row["had_dropped_evidence"]
        ):
            return "evidence_dropped_wrong_device"
        return "ok"

    result["review_flag"] = result.apply(flag, axis=1)
    result = result.reset_index()

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_CSV, index=False)

    review = result[result["review_flag"] != "ok"].copy()
    review.to_csv(REVIEW_CSV, index=False)

    print(f"Reason-coded events pulled (ReasonID 4 or 9, isomarketid=6): {n_before_status_filter}")
    print(f"Dropped as cancelled/terminated (CancellationDate set or status keyword match): {n_cancelled}")
    print(f"Distinct teids in valid events, not in teid_branch_id_map (dropped): {out_of_scope_count}")
    print(f"Dropped as BranchId mismatch (event's BranchId != teid's mapped branch_id): {n_branch_mismatch}")
    print(f"Dropped as confirmed device-name mismatch (event's EquipmentName != teid's mapped device): {n_device_name_mismatch}")
    print(f"Retirements corrected as same-device mis-tags (reverted to default): {n_mistag_corrected}")
    print(f"Retirements corrected as status-contradicted (confident Closed, reverted to default): {n_status_corrected}")
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
