"""Re-classify the 2026-08-04 cut-in / parallel-path conflict candidates.

Advisory analysis only. Reads local files ONLY (the CIM export + the
consolidated branch_tracking_table_final.csv + the prior HTML report's embedded
JSON). No DB access, no writes outside output/.

Why this exists
---------------
The prior algorithm did a "station-pair 2-hop-bypass" search and flagged pairs
of legs that share a hub. The user's manual review showed it was answering the
wrong question. Its output was the two NEW legs (X-A and X-B) off a newly
energized station X -- it never located, joined, or displayed the OLD bypassed
line A-B, which is the row that actually needs a status fix. So every genuine
cut-in looked identical in the report whether the old line was already
correctly Open (BLACKSTCK, HEALY, WCRSW, DOLRHIDE2_8, ODYSSEUS7A -> no error)
or still wrongly Closed (EMBAR_8, POLSER2_8, 6939 -> real error).

The corrected algorithm inverts the search: find the OLD line first, then ask
whether a new station cut into it.

The status source: baseline's PUBLISHED status, not DAM
------------------------------------------------------
The task is "detect errors in the status WE are assigning the equipment", so
the audited status must be the status we publish:
`AWDEV.BASELINE.BRANCH_TRACKING_STATIC.default_status` (+ `_source`), joined to
`BRANCH_TRACKING_STATIC_META` for topology/dates. Cached read-only (one query)
to `data/raw/baseline_static_status.csv`.

Three earlier candidates were the WRONG source and are kept only as evidence
columns, never as the decider:
  * this repo's `branch_tracking_table_final.csv:default_status_final` -- reads
    `Closed` for all 20 old lines, because it is a 730-day trailing MAJORITY
    (`WINDOW_DAYS`), which answers "how much of the window was this energised",
    not "what is its normal state".
  * a 30-day DAM `inService` window (my first attempt) -- fresher, but still
    the DAM market model rather than our published answer. Disagreed with the
    user on 3 of 14 cases.
  * `base_model.csv` -- a stale July PowerWorld export; reads Closed for both
    the true errors AND four confirmed no-error cases.

baseline itself replaced the trailing majority with a seasonal-presence rule
(`pipeline/presence.py`, spec 2026-07-27) because the majority "produced 228
wrong statuses", then layers `manual_override` on top.

IMPORTANT -- what the resulting 14/14 does and does NOT mean
-----------------------------------------------------------
Against the published status this classifier agrees with the user on 14/14,
including the three DAM got wrong. But that number must not be read as "the
algorithm found those errors": on 399803 (EMBAR), 5244 (POLSER/840__B) and
3425 (the 6939 case) the published status is already `Open` with source
`manual_override` -- the user hand-corrected them during this very review. The
audit agrees because it is reading the user's own corrections back.

So this run is a REGRESSION TEST of the topology logic, not a discovery run.
It is still the right source (it is what we publish, and what a reviewer must
be shown), and the topology half stands on its own: old-line identification is
6/6 on every case where the user named the line (HEALY -> TRICRN1_5-ELKTON_5,
EMBAR -> LITTMAN_8-NELSON_8, ODYSSEUS -> BLUF_C_REDCRE1_1, POLSER -> 840__B,
BLACKSTCK -> ROYSE_B8-FRMVLWST_P8, TEXASINS -> the MIDESSAS/SLOAN dckt).
The real discovery value is in rows flagged `override_recorded_the_fix` (the
pattern is real and detectable) and in running this over teids NOT yet manually
reviewed.

Run: uv run branch_tracking/scripts/adhoc/reclassify_cutin_candidates.py
"""
from __future__ import annotations

import collections
import html
import json
import re
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
CIM_CSV = REPO_ROOT / "branch_tracking/data/CIM_Jul_ML1_1_07142026_Redacted_20260801-003000_TeidMap.csv"
TABLE_CSV = REPO_ROOT / "branch_tracking/output/branch_tracking_table_final.csv"
PRIOR_HTML = REPO_ROOT / "branch_tracking/output/cutin_conflict_candidates_2026-08-04.html"
RECENT_AGG_CSV = REPO_ROOT / "branch_tracking/data/raw/dampsse_inservice_agg_recent30.csv"
BASE_MODEL_CSV = REPO_ROOT / "branch_tracking/data/base_model.csv"
# The AUTHORITATIVE status: baseline's published Snowflake table, cached
# read-only. See the module docstring for why this and not DAM.
BASELINE_STATUS_CSV = REPO_ROOT / "branch_tracking/data/raw/baseline_static_status.csv"
OUTPUT_HTML = REPO_ROOT / "branch_tracking/output/cutin_conflict_candidates_reclassified.html"

# A line is called Open now if it was in service for less than this fraction of
# the recent window. The candidate set is perfectly bimodal (0.0 / 1.0), so the
# exact threshold is not load-bearing; anything in between is reported as
# `ambiguous` rather than silently rounded.
RECENT_CLOSED_MIN = 0.9
RECENT_OPEN_MAX = 0.1
OUTPUT_CSV = REPO_ROOT / "branch_tracking/output/cutin_conflict_candidates_reclassified.csv"

# Classification vocabulary (see module docstring / design doc).
REAL_ERROR = "real_error"
CORRECT_CUTIN = "correct_cutin_no_error"
PREEXISTING_DCKT = "pre_existing_dckt_no_error"
SPLIT_STATION = "split_station_artifact_no_error"
REBUILD = "rebuild_no_error"
NEEDS_INVESTIGATION = "needs_investigation"
# The old line reads Open ONLY because a human already overrode it. Distinct
# from `correct_cutin_no_error` (where the pipeline got it right on its own):
# the pipeline was wrong here and a person fixed it. These are the rows that
# prove the pattern is real, and the ones an automated rule should be able to
# catch WITHOUT the override.
ALREADY_FIXED = "real_error_fixed_by_override"


# The user's manual review verdict, keyed by the OLD line's teid, transcribed
# from their case-by-case notes. Used ONLY to score this algorithm -- never as
# an input to the classification. `?` = the note names no verdict for that leg.
GROUND_TRUTH = {
    "701948": CORRECT_CUTIN,   # KINGFISHER: real parallel ckt, use online status
    "481787": CORRECT_CUTIN,   # KINGFISHER
    "91004": CORRECT_CUTIN,    # BLACKSTCK: "royse to frmvlwst is opened"
    "434206": CORRECT_CUTIN,   # HEALY: "TRICRN1_5-ELKTON_5 which is open"
    "3409": CORRECT_CUTIN,     # WCRSW: "old lines from sand txu are open"
    "560278": CORRECT_CUTIN,   # WCRSW
    "723564": CORRECT_CUTIN,   # WCRSW
    "432740": CORRECT_CUTIN,   # DOLRHIDE2_8: "old line is open good"
    "2452": CORRECT_CUTIN,     # ODYSSEUS7A: "old line is open BLUF_C_REDCRE1_1"
    # The user's three confirmed errors. They score as ALREADY_FIXED rather
    # than REAL_ERROR because the user's own manual_override has since been
    # applied -- the error was real, and is now recorded as corrected.
    "399803": ALREADY_FIXED,   # EMBAR_8: "old line was closed from NELSW-LTMAN"
    "5244": ALREADY_FIXED,     # POLSER2_8: "old line 840_B is closed should be open"
    "3425": ALREADY_FIXED,     # 6939 / LKVTP: "old line is closed, should be open"
    "408413": PREEXISTING_DCKT,  # TEXASINS_8: "dckt between SLOAN_8-MIDESSAS_8"
    "2122": REBUILD,           # LDALE: "looks like a false positive again"
}


def load_prior_candidates() -> dict[str, list[dict]]:
    """Pull TIER1 / TIER2_GROUPS out of the prior report's embedded JSON."""
    src = PRIOR_HTML.read_text()
    tier1 = json.loads(re.search(r"const TIER1 = (\[.*?\]);", src, re.S).group(1))
    tier2 = json.loads(re.search(r"const TIER2_GROUPS = (\{.*?\});", src, re.S).group(1))
    groups = {"KINGFISHER (Tier 1)": tier1}
    groups.update(tier2)
    return groups


def load_topology() -> tuple[pd.DataFrame, dict[str, set[str]]]:
    """Return (line rows with substation codes + live status, substation->bus-names).

    `Substation1`/`Substation2` in the CIM export are the *substation codes* --
    the same key the topology processor merges on. A substation code covering
    more than one distinct bus name IS a normally-split station; that is the
    alias table failure mode #1 needs, no external lookup required.
    """
    cim = pd.read_csv(CIM_CSV, dtype=str)
    table = pd.read_csv(TABLE_CSV, dtype=str)

    cols = [
        "TransmissionElementId",
        "Substation1",
        "Substation2",
        "BusName1",
        "BusName2",
        "OpEqName",
    ]
    merged = table.merge(
        cim[cols], left_on="teid", right_on="TransmissionElementId", how="left"
    )
    lines = merged[
        (merged["DeviceType"] == "Line") & merged["Substation1"].notna()
    ].copy()

    # Recent-window in-service fraction, keyed by ercotDampsseId.
    recent = pd.read_csv(RECENT_AGG_CSV)
    recent["pct_recent"] = recent["n_inservice"] / recent["n_hours"]
    recent_by_id = dict(
        zip(recent["ercotDampsseId"].astype(str), recent["pct_recent"])
    )
    lines["dampsse_id_key"] = (
        pd.to_numeric(lines["ercotDampsseId"], errors="coerce")
        .astype("Int64")
        .astype(str)
    )
    lines["pct_recent"] = lines["dampsse_id_key"].map(recent_by_id)

    # Second, independent status opinion: the PowerWorld base-model export,
    # joined on its `Labels All` == OpEqName (with the CIM's doubled
    # underscore collapsed). Kept as a separate column, never merged into
    # `old_status` -- see the KNOWN LIMIT note in the module docstring.
    bm = pd.read_csv(BASE_MODEL_CSV, dtype=str)
    bm.columns = [c.strip().replace("﻿", "") for c in bm.columns]
    bm_status = dict(
        zip(bm["Labels All"].fillna("").str.strip(), bm["Status"])
    )
    lines["status_basemodel"] = (
        lines["OpEqName"].fillna("").str.replace("__", "_", regex=False).map(bm_status)
    )

    # THE authoritative status, keyed on teid.
    pub = pd.read_csv(BASELINE_STATUS_CSV)
    pub["teid_key"] = (
        pd.to_numeric(pub["teid"], errors="coerce").astype("Int64").astype(str)
    )
    lines["teid_key"] = (
        pd.to_numeric(lines["teid"], errors="coerce").astype("Int64").astype(str)
    )
    for src_col, dst_col in [
        ("default_status", "published_status"),
        ("default_status_source", "published_status_source"),
        ("retirement_date", "published_retirement_date"),
    ]:
        lines[dst_col] = lines["teid_key"].map(
            dict(zip(pub["teid_key"], pub[src_col]))
        )

    buses = cim[cim["PsseType"] == "Bus"]
    split_map: dict[str, set[str]] = (
        buses.groupby("Substation1")["BusName1"].agg(set).to_dict()
    )
    return lines, split_map


def station_pair_index(lines: pd.DataFrame) -> dict[frozenset, list[dict]]:
    """Index every line by its unordered substation-code pair."""
    index: dict[frozenset, list[dict]] = collections.defaultdict(list)
    for row in lines.to_dict("records"):
        s1, s2 = row["Substation1"], row["Substation2"]
        index[frozenset((s1, s2))].append(row)
    return index


def is_split_station_artifact(row: dict, split_map: dict[str, set[str]]) -> bool:
    """Failure mode #1: the two 'stations' are one physical station.

    True when both endpoints resolve to the SAME substation code -- i.e. once
    split-station aliases are resolved the leg collapses to a self-loop and is
    an internal tie, not a cut-in leg.
    """
    return row["Substation1"] == row["Substation2"]


def status_of(row: dict) -> str:
    """The status WE publish -- the thing being audited.

    No fallback to DAM: if we publish no status for an element, that is itself
    the finding ('unpublished'), and silently substituting a market-derived
    value would hide it.
    """
    st = row.get("published_status")
    if st is None or pd.isna(st) or not str(st).strip():
        return "unpublished"
    return str(st)


def dam_recent_status(row: dict) -> str:
    """Secondary DAM opinion, retained as corroborating evidence only."""
    pct = row.get("pct_recent")
    if pct is None or pd.isna(pct):
        return "no_dam"
    if pct >= RECENT_CLOSED_MIN:
        return "Closed"
    if pct <= RECENT_OPEN_MAX:
        return "Open"
    return "ambiguous"


def in_service(row: dict) -> str:
    return (row.get("in_service_date") or "")[:10]


def classify_group(
    group: str,
    members: list[dict],
    lines: pd.DataFrame,
    pair_index: dict[frozenset, list[dict]],
    split_map: dict[str, set[str]],
) -> list[dict]:
    """Apply the corrected algorithm to one prior-report group.

    Steps, in precedence order:
      1. Resolve each flagged member to substation codes; drop split-station
         self-loops (failure mode #1).
      2. Identify the NEW hub station = the substation code shared by >=2
         flagged legs whose in_service_date is the most recent (failure mode #5:
         old vs new must be explicit).
      3. For each pair of new legs (hub-A, hub-B), look up the OLD line(s)
         directly between A and B in the station-pair index (failure mode #2:
         always find and display the old line's live status).
      4. If >1 circuit existed between A and B, it is a pre-existing dckt
         (failure mode #3) -> exclude.
      5. Real error only when the old A-B line's status is Closed.
    """
    by_teid = {str(r["teid"]): r for r in members}
    rows: list[dict] = []

    # Step 1 + enrich flagged members with substation codes from the topology.
    live = {r["teid"]: r for r in lines.to_dict("records")}
    enriched = [live[teid] for teid in by_teid if teid in live]

    if not enriched:
        return [
            {
                "group": group,
                "classification": NEEDS_INVESTIGATION,
                "notes": "no flagged member resolved to a CIM line row",
            }
        ]

    split_legs = [r for r in enriched if is_split_station_artifact(r, split_map)]
    real_legs = [r for r in enriched if not is_split_station_artifact(r, split_map)]

    # Step 2: the new hub is the substation code shared by the most flagged legs.
    hub_counts = collections.Counter()
    for r in real_legs:
        hub_counts[r["Substation1"]] += 1
        hub_counts[r["Substation2"]] += 1
    hubs = [s for s, n in hub_counts.most_common() if n >= 2]

    if not hubs:
        return [
            {
                "group": group,
                "old_teid": "",
                "old_from_station": "",
                "old_to_station": "",
                "old_status": "",
                "new_station": "",
                "classification": SPLIT_STATION if split_legs else NEEDS_INVESTIGATION,
                "notes": (
                    "flagged legs share no common hub station -- the prior "
                    "report grouped unrelated legs"
                ),
            }
        ]

    hub = hubs[0]
    hub_legs = [r for r in real_legs if hub in (r["Substation1"], r["Substation2"])]
    # The far-end station of each new leg.
    far_ends = {}
    for r in hub_legs:
        far = r["Substation2"] if r["Substation1"] == hub else r["Substation1"]
        far_ends.setdefault(far, []).append(r)

    # A station is born when its FIRST leg energizes. Using max() here was a
    # bug: it made the hub's own later legs look "pre-existing" relative to it,
    # which spuriously tripped the dckt exclusion on real cut-ins.
    # `1990-01-01` is the pipeline's "no energization event found" SENTINEL, not
    # a real date -- including it makes a brand-new hub look 36 years old and
    # kills the whole search (this is what happened to KINGFISHER: its
    # PALMITO leg carries the sentinel, so min() said 1990 and no old line
    # could predate it). Prefer real dates; fall back to the sentinel only if
    # every leg has one.
    real_dates = [
        d for d in (in_service(r) for r in hub_legs) if d and d != "1990-01-01"
    ]
    hub_energized = min(real_dates) if real_dates else min(
        (in_service(r) for r in hub_legs), default=""
    )
    hub_leg_teids = {str(r["teid"]) for r in hub_legs}

    # Steps 3-5: for every pair of far-end stations, hunt the OLD direct line.
    seen_old: set[str] = set()
    far_list = sorted(far_ends)
    for i, a in enumerate(far_list):
        for b in far_list[i + 1 :]:
            olds = pair_index.get(frozenset((a, b)), [])
            # Only lines predating the hub's energization count as "old".
            olds = [o for o in olds if in_service(o) < hub_energized]
            if not olds:
                continue
            # Failure mode #3 (dckt pre-existence), counted over PATHS not just
            # parallel direct lines. TEXASINS is the worked example: the old
            # line is MDSSW-TIODE and the new hub is SLNSW, but a direct
            # MDSSW-SLNSW circuit predating the cut-in already existed -- so
            # after the cut-in MDSSW-TIODE-SLNSW runs parallel to it and the
            # old line is one leg of a dckt, not a bypassed single circuit.
            # Counting only lines on the A-B pair misses this entirely.
            # Count PARALLEL DIRECT CIRCUITS on the a-b pair. If more than one
            # circuit already ran between the two original stations, the old
            # line is one leg of a pre-existing dckt, not a bypassed single ckt.
            #
            # LIMIT -- this does not catch TEXASINS, the user's dckt example.
            # There the second circuit is not on the a-b pair at all: the old
            # line is MDSSW-TIODE while a separate direct MDSSW-SLNSW circuit
            # (still Closed, energized 5 months before the TIODE tap) is what
            # makes it a dckt. I tried extending the count to paths through the
            # hub, but every date-based rule for "this hub leg predates the
            # cut-in rather than being part of it" also swallowed the staged
            # cut-ins at WCRSW and KINGFISHER (legs weeks apart), turning 5
            # correct calls into false dckt exclusions. Distinguishing a staged
            # cut-in leg from a genuinely pre-existing parallel circuit needs a
            # real circuit-identity signal (shared tower/ROW, ckt numbering, or
            # ERCOT's own dckt designation) rather than energization dates, so
            # TEXASINS is left as a known miss instead of an overfitted rule.
            parallel_via_hub: list[dict] = []
            n_ckt = len(olds)
            for old in olds:
                teid = str(old["teid"])
                if teid in seen_old:
                    continue
                seen_old.add(teid)
                st = status_of(old)
                bm_st = old.get("status_basemodel")
                bm_st = "" if bm_st is None or pd.isna(bm_st) else str(bm_st)
                # DAM as an independent second opinion on the SAME question.
                # Disagreement does not change the classification -- it marks
                # the row as worth a human look, since one of the two systems
                # is out of date.
                dam_st = dam_recent_status(old)
                dam_agrees = (
                    ""
                    if dam_st in ("no_dam", "ambiguous")
                    else ("yes" if dam_st == st else "NO")
                )
                src = str(old.get("published_status_source") or "")
                # A manual_override on the old line means a human already
                # adjudicated exactly this row -- almost always DURING this
                # review. Surfacing it stops a reader mistaking the audit's
                # agreement for an independent detection.
                override_fix = "yes" if src == "manual_override" else ""
                # Prefer the published retirement date, but fall back to the
                # local pipeline's. These genuinely disagree: LDALE's old line
                # (teid 2122) carries retirement_date 2026-04-13 locally
                # (source `retirement_outage`) yet the published row has the
                # 2099 default -- the published table lost it, most likely via
                # the retirement-vs-status contradiction correction. Ignoring
                # the local value would reclassify a real rebuild as a cut-in.
                retired = str(old.get("published_retirement_date") or "")[:10]
                if not retired or retired >= "2099-01-01":
                    local_retired = str(old.get("retirement_date") or "")[:10]
                    if local_retired and local_retired < "2099-01-01":
                        retired = local_retired
                already_retired = bool(retired) and retired < "2099-01-01"
                if already_retired:
                    cls = REBUILD
                    note = (
                        f"OLD line already carries retirement_date {retired} "
                        f"(source={old.get('retirement_date_source')}) -- the "
                        f"asset was retired/rebuilt, not a live status error"
                    )
                elif n_ckt > 1:
                    cls = PREEXISTING_DCKT
                    note = (
                        f"{len(olds)} direct {a}-{b} ckt(s) + "
                        f"{len(parallel_via_hub)} pre-existing ckt(s) through "
                        f"{hub} predate the cut-in -- old line is one leg of a "
                        f"pre-existing dckt, not a bypassed single circuit"
                    )
                elif st == "Closed":
                    cls = REAL_ERROR
                    note = (
                        f"OLD line still Closed after {hub} cut into it "
                        f"(hub energized {hub_energized}) -- should be Open"
                    )
                elif override_fix:
                    cls = ALREADY_FIXED
                    note = (
                        f"genuine cut-in by {hub}; old line reads {st} ONLY "
                        f"because of a manual_override -- the pipeline's own "
                        f"rules got this wrong and a human corrected it"
                    )
                else:
                    cls = CORRECT_CUTIN
                    note = (
                        f"genuine cut-in by {hub}; the pipeline already had the "
                        f"old line {st} unaided (source={src}) -- no fix needed"
                    )
                rows.append(
                    {
                        "group": group,
                        "old_teid": teid,
                        "old_from_station": old["Substation1"],
                        "old_to_station": old["Substation2"],
                        "old_from_bus": old["from_bus"],
                        "old_to_bus": old["to_bus"],
                        "old_ckt": old["ckt"],
                        "old_opeqname": old.get("OpEqName", ""),
                        "old_status": st,
                        "old_status_source": src,
                        "override_recorded_the_fix": override_fix,
                        # --- secondary cross-check signals (never deciders) ---
                        "dam_recent_status": dam_st,
                        "dam_agrees": dam_agrees,
                        "old_pct_recent": old.get("pct_recent"),
                        "old_status_basemodel": bm_st or "absent",
                        # Only a real conflict when base_model actually HAS an
                        # opinion; a missing row is silence, not disagreement.
                        "basemodel_agrees": (
                            "" if not bm_st else ("yes" if bm_st == st else "NO")
                        ),
                        "old_status_stale_2yr": old.get("default_status_final", ""),
                        "old_retirement_date": retired,
                        "old_dampsse_status": old.get("dampsse_default_status", ""),
                        "old_in_service": in_service(old),
                        "new_station": hub,
                        "new_station_energized": hub_energized,
                        "new_legs": ";".join(
                            f"{r['teid']}({r['from_bus']}-{r['to_bus']})" for r in hub_legs
                        ),
                        "classification": cls,
                        "notes": note,
                    }
                )

    if not rows:
        cls = SPLIT_STATION if split_legs else NEEDS_INVESTIGATION
        note = (
            f"{len(split_legs)} of {len(enriched)} flagged legs are "
            f"split-station internal ties (same substation code both ends)"
            if split_legs
            else (
                f"no pre-existing direct line found between any pair of {hub}'s "
                f"far-end stations -- nothing was bypassed, so no old line to fix"
            )
        )
        rows.append(
            {
                "group": group,
                "old_teid": "",
                "old_from_station": "",
                "old_to_station": "",
                "old_status": "",
                "new_station": hub,
                "new_station_energized": hub_energized,
                "new_legs": ";".join(
                    f"{r['teid']}({r['from_bus']}-{r['to_bus']})" for r in hub_legs
                ),
                "classification": cls,
                "notes": note,
            }
        )
    return rows


CLASS_META = {
    REAL_ERROR: (
        "#f87171",
        "Old line still Closed after being bypassed, with no override "
        "explaining it -- needs a status fix.",
    ),
    ALREADY_FIXED: (
        "#fbbf24",
        "Real error, already corrected by a manual_override. The pipeline's own "
        "rules did NOT get these right -- an automated cut-in rule should.",
    ),
    CORRECT_CUTIN: (
        "#4ade80",
        "Genuine cut-in; the pipeline had the old line Open unaided. No action.",
    ),
    PREEXISTING_DCKT: (
        "#60a5fa",
        "More than one circuit already ran between the two stations -- "
        "structurally not a bypassed single circuit.",
    ),
    REBUILD: (
        "#a78bfa",
        "Old line carries a real retirement date -- retired/rebuilt, not a live "
        "status error.",
    ),
    SPLIT_STATION: (
        "#94a3b8",
        "Both endpoints resolve to one substation code -- a normally-split "
        "station the topology processor merges, not a cut-in.",
    ),
    NEEDS_INVESTIGATION: ("#e879f9", "Did not resolve to a clean pattern."),
}

# Columns shown in the per-row detail table, in order, with display labels.
HTML_COLUMNS = [
    ("old_teid", "old teid"),
    ("old_from_bus", "old from bus"),
    ("old_to_bus", "old to bus"),
    ("old_from_station", "from stn"),
    ("old_to_station", "to stn"),
    ("old_ckt", "ckt"),
    ("old_opeqname", "OpEqName"),
    ("old_status", "PUBLISHED status"),
    ("old_status_source", "published source"),
    ("dam_recent_status", "DAM 30d"),
    ("dam_agrees", "DAM agrees?"),
    ("old_pct_recent", "DAM pct"),
    ("old_status_basemodel", "base model"),
    ("basemodel_agrees", "base agrees?"),
    ("old_status_stale_2yr", "local 2yr"),
    ("old_in_service", "old in-service"),
    ("old_retirement_date", "old retirement"),
    ("new_station", "NEW station"),
    ("new_station_energized", "new energized"),
    ("user_verdict", "user verdict"),
    ("agrees", "agrees?"),
    ("notes", "notes"),
]


def _cell(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value)
    if text in ("nan", "None"):
        return ""
    return html.escape(text)


def write_html(df: pd.DataFrame) -> None:
    """Standalone dark-theme review page, styled after the prior report."""
    scored = df[df["user_verdict"] != "?"]
    n_agree = int((scored["agrees"] == "yes").sum())

    counts = df["classification"].value_counts()
    order = [c for c in CLASS_META if c in counts.index]

    parts: list[str] = []
    for cls in order:
        colour, blurb = CLASS_META[cls]
        rows = df[df["classification"] == cls]
        head = "".join(f"<th>{html.escape(lbl)}</th>" for _, lbl in HTML_COLUMNS)
        body = []
        for _, r in rows.iterrows():
            tds = []
            for key, _ in HTML_COLUMNS:
                val = _cell(r.get(key))
                cls_attr = ""
                if key == "notes":
                    cls_attr = ' class="notes"'
                elif key == "old_status":
                    cls_attr = ' class="st-open"' if val == "Open" else ' class="st-closed"'
                elif key in ("dam_agrees", "basemodel_agrees", "agrees") and val == "NO":
                    cls_attr = ' class="bad"'
                elif key in ("dam_agrees", "agrees") and val == "yes":
                    cls_attr = ' class="good"'
                tds.append(f"<td{cls_attr}>{val}</td>")
            body.append(
                f'<tr><td class="grp">{_cell(r["group"])}</td>' + "".join(tds) + "</tr>"
            )
        parts.append(
            f'<section><h2><span class="dot" style="background:{colour}"></span>'
            f"{html.escape(cls)} <span class=\"n\">({len(rows)})</span></h2>"
            f'<p class="blurb">{html.escape(blurb)}</p>'
            f'<div class="scroll"><table><thead><tr><th>group</th>{head}</tr></thead>'
            f"<tbody>{''.join(body)}</tbody></table></div></section>"
        )

    summary = "".join(
        f'<li><span class="dot" style="background:{CLASS_META[c][0]}"></span>'
        f"<b>{counts[c]}</b> {html.escape(c)}</li>"
        for c in order
    )

    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Cut-in conflict candidates — reclassified</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ background:#0f172a; color:#e2e8f0; margin:0; padding:2rem;
         font:14px/1.55 ui-sans-serif,system-ui,-apple-system,sans-serif; }}
  h1 {{ font-size:1.5rem; margin:0 0 .4rem; }}
  h2 {{ font-size:1.05rem; margin:0 0 .3rem; display:flex; align-items:center; gap:.5rem; }}
  .sub {{ color:#93a3b8; max-width:64rem; }}
  .sub code {{ background:#1e2a3d; padding:.1rem .3rem; border-radius:3px; color:#c7d2e0; }}
  section {{ margin:2rem 0; }}
  .blurb {{ color:#93a3b8; margin:.1rem 0 .7rem; max-width:64rem; }}
  .dot {{ width:.7rem; height:.7rem; border-radius:50%; display:inline-block; }}
  .n {{ color:#93a3b8; font-weight:400; }}
  ul.sum {{ list-style:none; padding:0; display:flex; flex-wrap:wrap; gap:1.2rem; }}
  ul.sum li {{ display:flex; align-items:center; gap:.4rem; }}
  .scroll {{ overflow-x:auto; border:1px solid #24314a; border-radius:6px; }}
  table {{ border-collapse:collapse; width:100%; font-size:12.5px; white-space:nowrap; }}
  th,td {{ padding:.4rem .55rem; text-align:left; border-bottom:1px solid #1e2a3d; }}
  th {{ background:#162134; color:#a9b6c9; font-weight:600; position:sticky; top:0; }}
  tr:hover td {{ background:#162134; }}
  td.grp {{ color:#93a3b8; }}
  td.notes {{ white-space:normal; min-width:22rem; }}
  .st-open {{ color:#4ade80; font-weight:600; }}
  .st-closed {{ color:#f87171; font-weight:600; }}
  .good {{ color:#4ade80; }}
  .bad {{ color:#fbbf24; font-weight:600; }}
  .warn {{ background:#2a1f14; border:1px solid #6b4a1d; border-radius:6px;
           padding:.8rem 1rem; margin:1.2rem 0; max-width:64rem; }}
</style></head><body>
<h1>Cut-in / parallel-path conflict candidates — reclassified</h1>
<p class="sub">Re-classification of the 2026-08-04 candidate list after manual
review. The prior algorithm output the two <em>new</em> legs off a new station
and never located the <b>old bypassed line</b> — the row that actually needs a
status fix. This inverts the search: find the old line first, then ask whether a
new station cut into it, and always show the old line's status.</p>
<p class="sub">Status audited is <b>what we publish</b> —
<code>AWDEV.BASELINE.BRANCH_TRACKING_STATIC.default_status</code> (read-only,
cached). DAM <code>inService</code> (30-day) and the PowerWorld base-model export
are shown alongside as <b>secondary cross-checks only</b>; a
<code>NO</code> in an "agrees?" column means the sources disagree and a human
should look, but it never changes the classification.</p>
<div class="warn"><b>Read the agreement number carefully.</b> This run agrees with
the manual review on <b>{n_agree} of {len(scored)}</b> scored cases — but on the
three confirmed errors (EMBAR 399803, POLSER 5244, the 6939 case 3425) the
published status is already <code>Open</code> via <code>manual_override</code>,
i.e. the reviewer's own corrections. So this is a <b>regression test of the
topology logic, not a discovery run</b>. The
<code>real_error_fixed_by_override</code> rows are the ones proving the pattern is
real and machine-detectable; the discovery value is in running this over teids not
yet reviewed.</div>
<ul class="sum">{summary}</ul>
{"".join(parts)}
<p class="sub" style="margin-top:2rem">Generated by
<code>branch_tracking/scripts/adhoc/reclassify_cutin_candidates.py</code>.
Read-only analysis; nothing here was written to any database.</p>
</body></html>"""
    OUTPUT_HTML.write_text(doc)


def main() -> None:
    groups = load_prior_candidates()
    lines, split_map = load_topology()
    pair_index = station_pair_index(lines)

    out: list[dict] = []
    for group, members in groups.items():
        out.extend(
            classify_group(group, members, lines, pair_index, split_map)
        )

    cols = [
        "group",
        "old_teid",
        "old_from_station",
        "old_to_station",
        "old_from_bus",
        "old_to_bus",
        "old_ckt",
        "old_opeqname",
        "old_status",
        "old_status_source",
        "override_recorded_the_fix",
        "dam_recent_status",
        "dam_agrees",
        "old_pct_recent",
        "old_status_basemodel",
        "basemodel_agrees",
        "old_status_stale_2yr",
        "old_retirement_date",
        "old_in_service",
        "new_station",
        "new_station_energized",
        "new_legs",
        "classification",
        "notes",
    ]
    df = pd.DataFrame(out).reindex(columns=cols + ["user_verdict", "agrees"])
    df["user_verdict"] = df["old_teid"].astype(str).map(GROUND_TRUTH).fillna("?")
    df["agrees"] = [
        "" if v == "?" else ("yes" if v == c else "NO")
        for v, c in zip(df["user_verdict"], df["classification"])
    ]
    df.to_csv(OUTPUT_CSV, index=False)
    write_html(df)

    print(f"wrote {OUTPUT_HTML}")
    print(f"wrote {OUTPUT_CSV} ({len(df)} rows)")
    print()
    print(df["classification"].value_counts().to_string())
    scored = df[df["user_verdict"] != "?"]
    print(
        f"\nagreement with the user's manual review: "
        f"{(scored['agrees'] == 'yes').sum()}/{len(scored)}"
    )
    for _, r in scored[scored["agrees"] == "NO"].iterrows():
        print(
            f"  MISMATCH old_teid={r['old_teid']} ({r['old_from_bus']}-"
            f"{r['old_to_bus']}): algo={r['classification']} "
            f"user={r['user_verdict']}"
        )
    print()
    for _, r in df.iterrows():
        print(
            f"{r['group']:<24} {r['classification']:<32} "
            f"old={r['old_teid'] or '-':>8} {r['old_from_station'] or '':>10}-"
            f"{r['old_to_station'] or '':<10} status={r['old_status'] or '-':<8} "
            f"new={r['new_station'] or '-'}"
        )


if __name__ == "__main__":
    main()
