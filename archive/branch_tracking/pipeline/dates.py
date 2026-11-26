"""in_service_date / retirement_date inference per teid, from reason-coded
outage events.

Pure functions extracted verbatim from
scripts/build_inservice_retirement_dates.py:main -- see that script's
module docstring for the full method rationale (steps 1-8: sticky actual
dates, revision dedup, invalid-status filter, BranchId + device-name
cross-checks, chain detection, boundary conventions, mis-tag and
status-contradiction corrections, review flags). Inline comments below
that reference "module docstring step N" refer to THAT docstring. No
logic here should diverge from the original script; the real-slice test
in tests/test_dates.py (marquee teids 821/654439/1743/113628) is the
regression pin.

resolve_dates() composes everything in main()'s original order and
returns frames + counts; it prints nothing and writes nothing -- the
script wrapper owns all I/O.
"""
from functools import partial

import pandas as pd

from .config import (
    CHAIN_GAP_TOLERANCE,
    DEFAULT_IN_SERVICE_DATE,
    DEFAULT_RETIREMENT_DATE,
    INVALID_STATUS_KEYWORDS,
    REASON_NEW_EQUIPMENT,
    REASON_RETIREMENT,
    STATUS_CONTRADICTION_MIN_ROWS,
)
from .naming import names_relate, normalize_name


def is_invalid_status(row):
    if pd.notna(row["CancellationDate"]):
        return True
    for col in ("status", "ReqStatus"):
        val = row[col]
        if pd.notna(val) and any(kw in str(val).lower() for kw in INVALID_STATUS_KEYWORDS):
            return True
    return False


def sticky_actual_dates(events):
    """Sticky actual dates (see module docstring step 2a): forward-fill
    actualStartDate/actualEndDate within each (toOutageIdentifierId,
    BranchId) ticket, sorted by toStateId, so a later purely-
    administrative revision can't erase an earlier revision's real
    evidence. dropna=False so NULL-BranchId tickets still get grouped
    (as their own group) instead of being excluded from the fill."""
    events = events.sort_values(["toOutageIdentifierId", "BranchId", "toStateId"])
    events[["actualStartDate", "actualEndDate"]] = events.groupby(
        ["toOutageIdentifierId", "BranchId"], dropna=False
    )[["actualStartDate", "actualEndDate"]].ffill()
    return events


def dedupe_revisions(events):
    """Collapse revisions of the same outage request to its latest toStateId
    -- also surfaces the terminal state (a cancellation is itself a later
    revision, so this keeps the row that shows it). Dedup key is
    (toOutageIdentifierId, BranchId), NOT toOutageIdentifierId alone -- see
    module docstring step 2b."""
    return (
        events.sort_values("toStateId", ascending=False)
        .drop_duplicates(subset=["toOutageIdentifierId", "BranchId"], keep="first")
    )


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
    name, used by resolve_dates()'s mis-tag correction step."""
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


def crosscheck_branchid(events, legit_map):
    """BranchId cross-check (module docstring step 4a): only drop a row when
    BOTH BranchIds are known and they disagree. Also merges legit_map's
    cim_opeqname_norm/cim_branchname_norm columns onto the kept rows (used
    by the device-name cross-check next). Returns (kept, n_dropped)."""
    merged = events.merge(legit_map, on="teid", how="left")
    branch_mismatch = (
        merged["BranchId"].notna() & merged["branch_id"].notna()
        & (merged["BranchId"] != merged["branch_id"])
    )
    n_branch_mismatch = int(branch_mismatch.sum())
    in_scope = merged[~branch_mismatch].copy()
    return in_scope, n_branch_mismatch


def crosscheck_device_name(events, legit_map):
    """Device-name cross-check (module docstring step 4b): does this event's
    own EquipmentName match the teid's CIM-confirmed OpEqName/branch_name?
    A CONFIRMED mismatch (both names known and they disagree) is dropped
    outright, the same way a BranchId mismatch is above -- confirmed via
    teid=113628: EVERY one of its "Retirement of Old Equipment" tickets
    tags EquipmentName="CB_1814" (a circuit breaker), never the teid's
    actual CIM device "AT2H" (a transformer winding). A breaker being
    swapped/retired doesn't mean the transformer position it protects
    was retired -- the earlier version of this check only PREFERRED a
    name-matching chain when one existed, but fell back to using
    everything (including confirmed-wrong-device evidence) when nothing
    matched, which is exactly backwards: no matching evidence should
    mean no evidence, not "trust whatever's left."

    `legit_map` is accepted for interface symmetry with crosscheck_branchid
    but is not consulted directly: the CIM name columns it contributes
    (cim_opeqname_norm/cim_branchname_norm) are already merged onto
    `events` by crosscheck_branchid, and re-merging would duplicate them.

    Returns (kept-with-device_name_match-column, mismatch_dump, n_dropped).
    """
    cim_name_known = events["cim_opeqname_norm"].notna() | events["cim_branchname_norm"].notna()
    device_name_match = events.apply(
        lambda row: names_relate(row["equip_name_norm"], row["cim_opeqname_norm"])
        or names_relate(row["equip_name_norm"], row["cim_branchname_norm"]),
        axis=1,
    )
    device_name_confirmed_mismatch = (
        events["equip_name_norm"].notna() & cim_name_known & ~device_name_match
    )
    n_device_name_mismatch = int(device_name_confirmed_mismatch.sum())

    # Persist what got dropped -- per the user, "ok" mixes verified-good
    # teids with ones that simply have zero evidence (e.g. because their
    # only outage evidence was a confirmed wrong-device mismatch, like
    # teid=113628's breaker), and those two cases shouldn't be silently
    # indistinguishable. This lets a teid's dropped evidence be traced
    # and cross-checked against the CIM model file directly. (The wrapper
    # script writes this dump to device_name_mismatches.csv.)
    mismatch_dump = events[device_name_confirmed_mismatch][
        ["teid", "ReasonID", "BranchId", "EquipmentName", "equip_name_norm",
         "cim_opeqname_norm", "cim_branchname_norm", "plannedStartDate",
         "actualStartDate", "actualEndDate"]
    ]

    kept = events[~device_name_confirmed_mismatch].copy()
    kept["device_name_match"] = device_name_match[~device_name_confirmed_mismatch]
    return kept, mismatch_dump, n_device_name_mismatch


def correct_same_device_mistags(result):
    """Mis-tag correction (module docstring step 7a): a retirement before its
    own teid's energization, for the SAME device, means the retirement was
    never real -- confirmed via teid=821/654439. Revert it to the default.
    Returns (result, n_corrected)."""
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
    return result, n_mistag_corrected


def correct_status_contradictions(result):
    """Retirement-vs-status contradiction correction (added after digging
    into teid=1019 and teid=3830 in detail, then confirming the pattern
    across the 2026 cohort): ReasonID=9 ("Retirement of Old Equipment")
    is used far more loosely in ERCOT's outage data than "this branch
    was permanently decommissioned" -- 83% of all resolved retirements
    initially contradicted implied_default_status (recent PTOBRANCH
    auction snapshots showing the branch still Closed). Digging into
    the 2026 cohort specifically showed clusters of DIFFERENT teids
    sharing the exact same retirement timestamp in tight name-related
    groups (e.g. teid=280078/280216 = one transformer's H/L legs, both
    retired at the same minute; teid=104/120/100 all at the same
    substation) -- a signature of coordinated substation-wide
    maintenance/equipment-replacement work, not individual permanent
    retirements. When status evidence is CONFIDENT (a clear majority,
    not a roughly-even mixed split, backed by at least
    STATUS_CONTRADICTION_MIN_ROWS recent snapshots) that the branch is
    still Closed, the retirement is reverted to the default -- status
    evidence from recent, direct auction-model snapshots is far more
    reliable than a loosely-coded outage reason on its own. Weaker
    contradictions (a "mixed" status split, or too few status rows to
    trust) are left as-is but flagged `retirement_status_uncertain`
    for manual review rather than silently corrected or ignored.

    Returns (result, n_corrected, status_confidently_closed) -- the mask
    is returned so resolve_dates() can derive retirement_status_uncertain
    from it, exactly as main() originally did."""
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
    return result, n_status_corrected, status_confidently_closed


def flag_rows(result):
    """review_flag per teid (module docstring step 8). Verbatim `flag`
    closure from main()."""
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

    return result.apply(flag, axis=1)


def resolve_dates(events, legit_map, status):
    """Full composition, in main()'s original order: sticky ffill ->
    event_date/event_end_date derivation -> revision dedup ->
    invalid-status filter -> teid scope -> BranchId cross-check ->
    device-name cross-check -> ReasonID 4/9 split -> per-teid chain
    resolution -> status join -> count fills -> date sources/defaults ->
    same-device mis-tag correction -> status-contradiction correction ->
    retirement_status_uncertain -> had_dropped_evidence -> review_flag.

    `legit_map` is teid_branch_id_map.csv's frame (pre-filtering to
    match_status != "unmatched" is optional -- it's re-applied here);
    `status` is branch_default_status.csv's frame (raw column names,
    incl. review_flag).

    Prints nothing, writes nothing. Returns a dict:
      result        -- the per-teid output frame (one row per legit teid)
      mismatch_dump -- dropped device-name-mismatch rows (for
                       device_name_mismatches.csv)
      counts        -- scalar drop/correction counts for the wrapper's
                       summary prints
      diagnostics   -- mid-pipeline frames/series the wrapper needs to
                       reproduce main()'s original warning + value_counts
                       prints (they were computed between steps, so they
                       can't be recomputed from `result`)
    """
    # Production input is already restricted to ReasonID IN (4, 9) by
    # load_reason_events()'s SQL WHERE clause -- re-applying the filter
    # here is a no-op for production input and makes resolve_dates safe
    # for raw event slices that carry other ReasonIDs (e.g. the frozen
    # test fixture, an all-ReasonID revision dump).
    events = events[events["ReasonID"].isin((REASON_NEW_EQUIPMENT, REASON_RETIREMENT))]

    legit_map = (
        legit_map[legit_map["match_status"] != "unmatched"]
        [["teid", "branch_id", "OpEqName", "branch_name"]]
        .drop_duplicates()
    )
    legit_map["branch_id"] = legit_map["branch_id"].astype(int)
    legit_map["cim_opeqname_norm"] = legit_map["OpEqName"].apply(normalize_name)
    legit_map["cim_branchname_norm"] = legit_map["branch_name"].apply(normalize_name)
    legit_map = legit_map[["teid", "branch_id", "cim_opeqname_norm", "cim_branchname_norm"]]
    legit_teids = set(legit_map["teid"].unique())

    status = status[
        ["teid", "default_status_majority", "pct_closed", "n_status_rows", "review_flag"]
    ].rename(columns={"review_flag": "status_review_flag"})

    events = sticky_actual_dates(events)

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
    missing_end_teids = events.loc[events["event_end_date"].isna(), "teid"].drop_duplicates()

    # status/ReqStatus diagnostic (raw events, before dedup/filtering) --
    # captured here, printed by the wrapper.
    status_value_counts = events["status"].value_counts(dropna=False)
    reqstatus_value_counts = events["ReqStatus"].value_counts(dropna=False)

    events = dedupe_revisions(events)

    n_before_status_filter = len(events)
    events["invalid"] = events.apply(is_invalid_status, axis=1)
    n_cancelled = int(events["invalid"].sum())
    valid_events = events[~events["invalid"]].copy()

    in_teid_scope = valid_events[valid_events["teid"].isin(legit_teids)]
    out_of_scope_count = valid_events["teid"].nunique() - in_teid_scope["teid"].nunique()

    in_scope, n_branch_mismatch = crosscheck_branchid(in_teid_scope, legit_map)

    in_scope, mismatch_dump, n_device_name_mismatch = crosscheck_device_name(in_scope, legit_map)
    mismatch_teids = set(mismatch_dump["teid"].unique())

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

    result, n_mistag_corrected = correct_same_device_mistags(result)

    result, n_status_corrected, status_confidently_closed = correct_status_contradictions(result)

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

    result["review_flag"] = flag_rows(result)
    result = result.reset_index()

    return {
        "result": result,
        "mismatch_dump": mismatch_dump,
        "counts": {
            "n_missing_end": n_missing_end,
            "n_before_status_filter": n_before_status_filter,
            "n_cancelled": n_cancelled,
            "out_of_scope_count": out_of_scope_count,
            "n_branch_mismatch": n_branch_mismatch,
            "n_device_name_mismatch": n_device_name_mismatch,
            "n_mistag_corrected": n_mistag_corrected,
            "n_status_corrected": n_status_corrected,
        },
        "diagnostics": {
            "missing_end_teids": missing_end_teids,
            "status_value_counts": status_value_counts,
            "reqstatus_value_counts": reqstatus_value_counts,
        },
    }
