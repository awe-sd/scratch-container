# branch_tracking production refactor — design spec

Date: 2026-07-09. Status: approved-in-dialogue, pending final user review.

## Purpose

Turn `branch_tracking/` from a pile of session-grown investigation scripts
into a production pipeline that maintains a longitudinal dataset of every
ERCOT transmission branch (`branch_tracking_table.csv`: identity
`teid`/`branch_id`/`ercotDampsseId`, buses, ckt, resolved `default_status`,
`in_service_date`, `retirement_date`) and updates it incrementally as new
information arrives, with production-grade gates, tests, and review trails.

Constraints carried over unchanged (hard rules):
- `teid` is the grain; cumulative across CIM models (see Data model).
- Read-only DB access. The pipeline NEVER writes to the live DB. The
  product is the versioned CSV; the user uploads manually. A `CREATE
  TABLE` DDL is delivered so the upload target is formally defined.
- All Python via `uv run`; scripts never in `/tmp`.

## Decisions (from brainstorm Q&A)

| Question | Decision |
|---|---|
| Run model | Incremental updates (not scheduled full refresh) |
| Teid universe on new CIM export | Cumulative union; first-seen/last-seen model recorded; disappearance is a signal, not a deletion |
| Verification standard | Fresh-eyes code review + regression test suite + in-pipeline invariants (no separate DB reconciliation audit) |
| Output gates | Pipeline stages outputs + `.prev` + diff report; **user reviews and commits manually** |
| Dataset home | CSV-in-git artifact, manual DB upload; DDL delivered now |
| Update inputs watched | New CIM exports, new outage tickets, new auction cases, BRANCH changes (all four) |
| Base-model comparison | One-off adhoc tool, not a recurring pipeline stage |
| Status source hierarchy | DAM PSSE hourly `inService` (2-yr dominant) primary → auction snapshot majority fallback → blank; base model & outage cross-check as validation |

## Architecture (Approach A: package + staged pipeline)

```
branch_tracking/
  pipeline/
    __init__.py
    config.py        # ISOMARKETID_ERCOT, thresholds (CHAIN_GAP_TOLERANCE,
                     # STATUS_CONTRADICTION_MIN_ROWS, windows), defaults
                     # (1990-01-01 / 2099-12-31), paths
    sources.py       # every DB query in one place + data/raw/ cache +
                     # incremental watermarks (see Incremental updates)
    naming.py        # normalize_name, names_relate, unit_and_leg —
                     # today duplicated across 4+ scripts
    mapping.py       # teid→branch_id resolution (from build_teid_branchid_map)
    legs.py          # transformer H/L pairing (from build_transformer_leg_map)
    dates.py         # in_service/retirement — the 673-line monolith
                     # decomposed into named, individually-testable steps:
                     # drop_cancelled(), sticky_actual_dates(),
                     # crosscheck_branchid(), crosscheck_device_name(),
                     # collapse_chains(), resolve_chain(boundary),
                     # correct_same_device_mistags(),
                     # correct_status_contradictions()
                     # composed in order by resolve_dates()
    dampsse.py       # DAM PSSE mapping tiers (exact name, substring,
                     # station-pair, leg-aware, psseCktId, consensus) +
                     # inService dominant-status computation
    status.py        # multi-source default_status resolver:
                     # DAM primary, auction fallback, per-source columns,
                     # default_status_source, agreement flags
    assemble.py      # final-table join + cumulative teid-universe merge
    invariants.py    # runtime sanity checks (see Verification)
    gates.py         # .prev copies, diff computation, staging report
  run_update.py      # the one entrypoint (see Update workflow)
  ddl/branch_tracking_table.sql
  scripts/adhoc/     # investigation scripts move here UNCHANGED (explore_*,
                     # analyze_*, inspect_*, review_*, investigate_*,
                     # find_*, compare_base_model_status.py)
  tests/
    fixtures/        # small frozen CSV slices for the marquee teids
    test_naming.py, test_mapping.py, test_dates.py, test_dampsse.py,
    test_status.py, test_assemble.py, test_gates.py, test_invariants.py
  data/              # inputs the user drops in (CIM exports, base_model*.csv)
  data/raw/          # parquet/CSV cache of DB pulls — GITIGNORED
  output/            # gated artifacts — git-tracked
  docs/findings.md   # the investigation narrative moves here from CLAUDE.md
```

`branch_tracking/CLAUDE.md` is rewritten as a lean working guide (hard
rules, module map, run instructions); the accumulated investigation
narrative moves to `docs/findings.md`. `output/README.md` stays the
artifact index. `output/PINNED_unmapped_dampsse.md` stays the parked
worklist.

## Data model of the tracking table

One row per teid ever seen in any ingested CIM export (cumulative union).
Columns as today (identity, buses/ckt, resolved `default_status` +
`default_status_source`, per-source status columns, dates + sources +
review flags) plus universe-tracking columns:
- `first_seen_model`, `last_seen_model` (CIM export identifier, e.g.
  `CIM_Jul_ML1_1`), derived from an ingest registry of processed exports.
- A teid absent from the latest export keeps its row; `last_seen_model`
  goes stale, which feeds a `dropped_from_model` review flag (candidate
  retirement signal — cross-checked against DAM dormancy, which the
  residue analysis showed is itself a real status signal).

### DB-side versioning (per the user: track changes, revert, back-cast)

The DDL delivers an APPEND-ONLY SNAPSHOT design, not a flat table:
- `branch_tracking_snapshot` — all final-table columns plus
  `snapshot_id int`, `snapshot_date datetime`, `git_commit char(40)`
  (ties every DB snapshot to the exact repo commit that produced it).
- `branch_tracking_snapshot_registry` — one row per upload:
  `snapshot_id`, `snapshot_date`, `git_commit`, `note`, `is_current bit`.
- View `branch_tracking_current` — the rows of the registry's current
  snapshot; consumers query the view.
Upload flow (manual, as always): INSERT the new snapshot's rows + one
registry row; flip `is_current`. Nothing is ever UPDATEd or DELETEd in
place. Revert = flip `is_current` back to an older snapshot. Back-cast
validation = query a historical `snapshot_id` (or date) directly and
compare against known-correct topology for that period. At ~11k rows per
snapshot, storage is negligible for years of uploads.

## Incremental updates (sources.py)

Every DB pull is cached under `data/raw/` with a watermark; an update run
fetches only deltas and upserts into the cache. The pure-logic modules
read ONLY from the cache — this is what makes tests fast, reruns cheap,
and the DB's slowness irrelevant to iteration.

| Source | Watermark | Delta pull |
|---|---|---|
| `toChangesAllIsos` (outage tickets) | `max(toStateId)` | rows with larger toStateId; re-resolve only affected teids' dates |
| `ptoFile`/`ptoBranch` (auction cases) | `max(ptoID)` ingested | new cases; recompute auction majority on the rolling window |
| `ercotDampsseTimeseries` (DAM hourly) | `max(awDateID)` | new day-hours into the inService aggregate (rolling 2-yr window); Def/Station dims re-pulled cheaply (small) |
| `dbo.BRANCH` | none reliable — snapshot compare | full re-pull only when requested (`--refresh-branch`; it's the slowest source and changes rarely); diff vs cached snapshot drives re-mapping only for changed rows |
| CIM exports | file registry (filename/RunRefId) | new file in `data/` → full re-map for that export + universe merge |
| `ercotRtDynamicRating*` | `max(createTime)` | deferred — corroboration source, not yet in the pipeline |

Full rebuild (`run_update.py --full`) always available; incremental
correctness is testable against it (invariant: incremental result ==
full-rebuild result on the same cache).

## Update workflow (run_update.py)

1. **Pull** — refresh caches per watermarks (skippable with `--offline`).
2. **Resolve** — mapping → legs → dates → dampsse → status → assemble,
   all pure functions over the cache.
3. **Invariants** — hard-fail stops before any output is touched;
   soft-warn goes into the run report.
4. **Gate** — for every output file: copy current → `<name>.prev`, write
   new, compute diff (row counts, per-flag/status distribution shifts,
   changed-row samples, added/removed teids).
5. **Report** — one staging report (markdown, printed + written to
   `output/last_run_report.md`): what was pulled, what changed, invariant
   warnings, diff summaries.
6. **User reviews and commits.** The pipeline never runs `git commit`.
   `.prev` files are gitignored (git history is the real archive; `.prev`
   exists for immediate same-run diffing).

## Verification

**Regression tests** (pytest, fixtures from hand-verified cases): the
marquee teids pin every resolution rule — 527244 (chain collapse),
70365 (dedup key + bundled clearance), 1743 (sticky dates + teid reuse),
821/654439 (same-device mistag), 113628 (wrong-device drop), 1019/3830
(status-contradiction correction), 552333 (longest-chain wins),
SNDSW L/H legs (leg-aware mapping), LINE_1_1 vs LINE1_1 (name collision),
LOTEBUSH/MULBERRY (ambiguity must NOT auto-resolve). Fixtures are small
frozen slices of the raw cache, not DB calls.

**Invariants** (every run): teid count never shrinks (cumulative
universe); no teid loses its branch_id/ercotDampsseId vs prior run
without an explicit re-mapping reason; dates within [1990-01-01,
2099-12-31]; retirement >= in_service unless flagged; review-flag
distribution shift vs prior run bounded (warn); default_status flip
count vs prior run bounded (warn, listed); incremental==full on demand.

**Fresh-eyes review**: during migration each module gets an independent
subagent review hunting the class of bugs found this session (dedup keys,
fallback fallthroughs, stale masks, silent drops), findings adjudicated
by the user. The review happens against the decomposed modules, not the
monolith.

## Logic improvements folded into the refactor

1. **Auction snapshot discounting**: ignore auction snapshots predating
   the teid's `in_service_date` when computing the auction majority
   (fixes the recently-energized lag — 229 of 267 current DAM-vs-auction
   disagreements; also fixes most of the base=Closed/ours=Open class).
2. **DAM-primary status** (done in prototype, formalized in status.py):
   `default_status` = DAM 2-yr dominant `inService`, auction fallback,
   `default_status_source` recorded.
3. **DAM dormancy as signal**: mapped-but-dormant elements feed the
   `dropped_from_model` flag rather than silently keeping stale status.
4. Carry-through of all session fixes as named functions (see dates.py).

## Post-refactor follow-ons (explicitly out of scope, tracked in PINNED doc)

- Outage cross-check: Open hours vs logged outages to confirm
  default-Closed (target: borderline pct_inservice 0.4–0.6).
- Tier-4 impedance (r/x/b) matching; RT-rating crosswalk as an
  independent mapping check; GSU status inheritance from
  `ercotDampsseGnTimeseries`.
- Resolving the 20 pinned no-status teids / 73 identity-ambiguous ones.
- Energization-vs-status cross-validation (mirror of the retirement fix).

## Migration plan (phases; each ends with tests green + gated outputs unchanged)

0. **Baseline**: `.gitignore` (data/raw/, .prev, __pycache__, .venv),
   initial commit of the repo as-is (the repo currently has ZERO commits).
1. **Skeleton + verbatim move**: create `pipeline/`, move logic without
   behavior change, shim adhoc scripts' imports; pin current outputs as
   golden files; tests assert byte-identical outputs.
2. **Fresh-eyes review + improvements**: module-by-module review;
   apply the logic improvements above; update goldens deliberately.
3. **Gates + invariants + run_update.py** (full-rebuild mode only).
4. **Incremental sources** + incremental==full invariant.
5. **DDL + docs restructure** (CLAUDE.md slim-down, findings.md).
