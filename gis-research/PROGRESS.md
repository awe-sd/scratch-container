# gis-research — project progress

> Maintained by the main session at each milestone (user order 2026-07-19).
> Fresh-context resume: read this + `CLAUDE.md` + memory `gis_research_status.md`.

_Last updated: 2026-07-19 ~16:30 UTC_

## Where the project stands

- **Triage: DONE.** 779 projects, 4 cohorts, $732, 409 flagged for deep scan.
  Resumable no-findings fails: 24INR0453, 26INR0714, 25INR0237, 27INR0500,
  27INR0011, 25INR0164, 25INR0214.
- **Deep scans: ~130 done, ~380 queued. 7 Sonnet workers PAUSED (user order)**
  — relaunch only after in-flight tracks land and tools pass review.
  Economics: Sonnet + 400k budget ≈ $4.64/scan mean.
- **IA corpus picture (772 triaged):** 412 no-IA-signed (correct negatives) ·
  360 signed → 82 had PDFs → 187 matchable (sweep running) → 91 hard set
  (`research/_reference/ia_hard_set.txt`; INR harvest will resolve text PDFs).

## In-flight tracks (4)

| Track | Runner | Status | Output |
|---|---|---|---|
| IA match sweep (187 proj) | task `byd1ssct0`, no-LLM | running (80/187 @ 16:20) | `research/_batches/ia_match_sweep.csv` |
| INR harvest (1,743 PDFs) | task `b3twvo9av`, no-LLM | running (200/1,743 @ 16:20) | `research/_reference/puct_inr_join.json` |
| Registry tools ch313/faa/tceq | Opus subagent `a03b2fa559dd323f9` | **DONE + review-PASSED, in PLAYBOOK** | `scripts/research_tools/{ch313,faa,tceq}.py` |
| EIA DB integration | Opus subagent `a102d25ef7c02826b` | **DONE + review-PASSED** | `docs/eia_db_reference.md`, `eia_snapshot.py`, extended `eia_history.py`/`build_brief.py`, `research/_reference/eia_backfill.csv` |

Registry-tools review (2026-07-19): all ground truths re-run by main session and
passed (Hanson #1698 + 9 PDFs / Briggs #1676 / Monarch Creek 86 cases ASN
2024-WTW-8086..8171 centroid 33.20938,-99.46218 / Rayburn PSDTX1198+1468 owner
"Rayburn Energy Station LLC" / Tenaska-Aegle PSDTX1350 / negatives explicit).
One defect fixed by main: faa.py ASN dedupe preferred first-seen (unattributed
Socrata cache would beat sponsor-attributed local pulls once Socrata unblocks) —
now sponsor-attributed record wins; regression re-run passed. Known limitation:
FAA live sources blocked 2026-07 (Socrata rkqu-p2bk private + oeaaa shutdown);
faa.py runs off cached pulls, emits deep-links on miss, self-heals on refresh
once public again. ch313 requires one-time `refresh` (done, 740+38 rows cached);
tceq/faa degrade gracefully without.

Subagent progress files (they maintain, I read):
`$SCRATCHPAD/registry_tools_progress.md`, `$SCRATCHPAD/eia_db_progress.md`
where `$SCRATCHPAD = /tmp/claude-1000/-workspaces-scratch-workspace/f07f0766-08e4-46c8-9188-c0e2b33c332c/scratchpad`.
Container watchdog: task `b26jpixz4`.

## PIPELINE V2 (2026-07-19 evening) — spec committed 03d4f90, awaiting user spec review

Brainstormed with user; decisions: (1) triage = deterministic factsheet.py +
short LLM verdict; (2) GATING INVERTED — triage kills paper, deep scan only for
REAL-looking projects (reality signals / COD<18mo / big MW), ranked MW ×
COD-nearness; hybrid ±15 score adjust with citation; (3) preserve = git for
code+intelligence, S3 append-only sync mirror for binaries (bucket pending from
user); (4) search = AgentCore Gateway web-search ($7/1k, us-east-1, AWS_IAM
inbound — verified in SDK); setup_agentcore_gateway.py written for user's admin
profile (container = MinimalReadOnlyUser, AccessDenied on AgentCore).
Log forensics (scratchpad logmine/, to be copied into docs/analysis/): 51.3%
of 57,865 calls = web fetches; PUCT 3,012 @ 100% 402; SEC 1,196 @ 100% fail;
7,260 search scrapes; 39/75 failed runs lost all work; 26-deep retry storms.
Spec: docs/superpowers/specs/2026-07-19-pipeline-v2-design.md. Next after user
review: writing-plans → implement (factsheet.py, hooks, search.py, v2 prompts,
backfill 779, commit+S3 sync, process_v2.html, relaunch workers).
INR harvest DONE: 1,743 items, 1,201 w/ INRs, 897 distinct INRs, 22 image-only,
0 errors. IA sweep DONE: 162/187 projects gained verified IAs (273 PDFs) round 1
+ 1 round 2; 8 FileNotFoundError fixed (puct.py multi-PDF name collision).

## Gate before deep-worker relaunch

1. ~~Senior-dev review of registry tools~~ DONE — passed, one faa dedupe fix.
2. ~~Senior-dev review of EIA subagent deliverables~~ DONE — passed. Ground
   truths re-run by main: Red Egret exact (69364 / Red Egret, LLC / EIA COD
   2027-05 vs queue 2026-08-31, JSON on disk identical to fresh resolve);
   Rowdy Creek 24INR0186 partial drop (unit RDYBS, capacity 1050→700
   corroborates) renders as brief warning card; Garcitas 65973 whole-plant
   sentinel fires via --plant-id; backfill CSV = 53 ok / 63 not-in-EIA /
   14 ambiguous-skipped, 2 drop hits. Two defects fixed by main:
   (a) whole-plant status sentinel wrote "to": "DROPPED_FROM_860M" (string
   where date belongs) → now dataset_latest; (b) wrong --plant-id raised
   IndexError → now returns not_in_eia. Regressions re-run clean.
   Key schema facts: eiaGenerator DOES carry county/lat/lon (fully populated
   in TX slice — earlier "no county in DB" claim wrong) + nameplateEnergyCapacity
   (storage MWh); eiaEnergyStorage is net-generation NOT capacity;
   namEia860GridMap has no ERCOT rows; genUnitEIAPlant empty. Matching logic
   deliberately unchanged (Excel county map) for byte-exact reproducibility.
   Limitation: fully-vanished plants aren't auto-matchable (find_plant keys
   off latest snapshot) — verified zero missed withdrawals in the 130-dir cohort.
3. Wire `puct_inr_join.json` into `puct.py match` as first lookup rung
   (after INR harvest completes).
4. ~~Integrate registry tools into PLAYBOOK ladder~~ DONE (rung 2 fuel-specific
   tools + fuel paper-trails bullet now name the tools).
5. Relaunch 7 Sonnet deep workers (absolute script paths; ≤15 total agents).

## Recent decisions / findings (newest first)

- **2026-07-19 EPM rejected as source** (user asked re EPM tables 6.03/6.05):
  repackaged 860M, fewer columns, one month staler than our `eiaGenerator`
  DB snapshots. No scraper/archive. Side-find: **DROPPED_FROM_860M
  cancellation signal** — 11 TX unit-keys vanished Apr→May 2026 (Garcitas
  Creek, Cradle, Flag City, Ion Solar whole-plant; Hollow Branch/Middlebrook/
  Rowdy/Tehuacana BESS-unit-only). Requirement sent to EIA subagent.
  Gotcha: parquet `reportDate` is object dtype — string equality silently
  all-False; normalize first.
- **2026-07-19 systematic IA matching**: `puct.py` (central docket 35077 is
  THE fact), index/match with INR-in-PDF verification; no dates, no fuzz
  (iaSigned is stale/self-reported — never a join key).
- **2026-07-19 SPV resolver**: `spv.py` (860M join + docket party extraction);
  `research/_reference/spv_candidates.csv` — 293 via 860M, 221 via docket,
  376 neither (registry-ladder cases).
- **2026-07-19 EIA second source**: `eia_history.py` change-points + brief
  section; Red Egret divergence validated.

## Standing constraints

- Creds only in `~/.config/gis-research.env`; agents write only in their
  project dir; banned queue-aggregator sources; SQL read-only via awconnect;
  subagents never commit; ≤15 concurrent agents; never poll background tasks;
  absolute script paths for background launches.

## Backlog (not blocking)

- Schedule-exhibit extraction pass over backfilled IA PDFs (findings/briefs
  don't show contractual_schedule yet for those).
- 91-project hard set after INR harvest; scanned PDFs stay manual.
- Brief/dossier template freeze pending user review (Hanson exemplar).
- Monthly delta mode; TexasFile creds; Maps Static API 403.
- Large uncommitted work: research_tools scripts, playbook/checklist edits,
  research dirs.
