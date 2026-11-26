# CLAUDE.md — gis-research

Guidance for working in this subproject. See `README.md` for source/schema/scripts.

**`PROGRESS.md` is the live project-progress file — read it first when resuming, and
UPDATE it at every milestone** (tracks finishing, decisions, gates cleared), same duty
as the memory-before-compaction rule. Memory holds the durable long-form record;
PROGRESS.md is the at-a-glance state (in-flight tracks, relaunch gate, backlog).

## Data model gotchas (non-obvious, discovered the hard way)

- **Grain is `(INR, fileDate)`** — one row per project *per monthly snapshot*, 2014-05 →
  2026-06. "The queue" = a **single `fileDate`**, not last-seen-per-project. The latest
  fileDate (2026-06-01) = projects currently in the queue.
- **Milestone columns are dates-or-null, not booleans**: `screeningStudyComplete`,
  `fisApproved`, `iaSigned`, `meetsSection691` (Guide 6.9(1)), `meetsAllSection69`
  (all 6.9). "Achieved" = date present. `financialSecurityAndNoticeToProceedProvided`
  is the odd one out — it's `"Yes"`/`"No"`. Milestones are **independent gates, not a
  strict funnel** (e.g. a project can have `iaSigned` without `fisApproved`).
- **Terminal / online states** (exclude for an "active queue" view): `cancelDate`,
  `inActiveDate`, `approvedForCommercialOperation` — these three reproduce ERCOT's own
  *Project Details* active list exactly (latest snapshot 2,024 → **1,828**, 434.0 GW,
  verified against the official xlsx). The report tool ALSO excludes
  `approvedForSynchronization` / `ApprovedForEnergization` ("approved-for-sync ≈ online"),
  trimming further to **1,683**. That extra pair is beyond ERCOT's definition — a
  deliberate "not-yet-online" refinement.
- **This IS the ERCOT GIS monthly report.** `data/RPT.*GIS_Report_*.xlsx` is the official
  single-month workbook; its *Project Details – Large/Small Gen* sheets match the parquet
  snapshot 1:1 (INR set + per-fuel capacity). Parquet is preferred (all months); xlsx is
  the validation reference. `capacityMw` sums are big for Battery (~150-180 GW) and that is
  REAL speculative queue — confirmed by the report's own `data_GIM Trends_2` sheet.
- **`fuel`/`technology` are messy** across the 12-year history (`SOL`/`Solar`/`SOLAR`,
  `WIN`/`Wind`, `GAS`/`Gas`). The *active latest snapshot* is mostly clean code forms;
  word-form duplicates cluster in the terminal-state rows. Normalize via
  `normalize_fuel_tech()` in `build_queue_report.py`. Batteries are usually
  `fuel=OTH, technology=BA`.
- Key measure = `capacityMw`; project count = distinct `INR`; zone = `cdrReportingZone`
  (null → "Unassigned"); expected COD = `projectCod` (0 nulls in the active latest snapshot).
- These objects are **SQL Server `AW.dbo` only** — not in Snowflake for the read-only role.
- **`data/ercot_generation_interconnect.parquet` + `data/ercot_generation_interconnect_view.parquet`
  are intentionally tracked in git** — the only two exceptions to the "parquet lives on S3,
  not in git" rule (`.gitignore`'s `gis-research/data/*.parquet`). A fresh clone needs the
  live queue snapshot on disk to bootstrap `factsheet.py`/`run_agent.py`/the report builder
  without an S3 pull first; re-commit them after a monthly queue refresh.

## Report tool

`build_queue_report.py` is the primary deliverable: `--report-date` (default latest)
produces a self-contained interactive HTML (client-side filter/aggregate, no server).
- Capacity shown in **GW**; COD range filter defaults start = **today**.
- Table: rows = zone (+TOTAL); column groups = milestone gates × (GW, #). Clicking a cell
  (zone × milestone) drives the county map.
- Map: TX county choropleth on a **MapLibre tile basemap** (plotly `choroplethmap` trace,
  carto-darkmatter/positron by theme; needs internet for basemap tiles, choropleth still
  renders offline). Native pan/zoom; fills its box (no projection letterboxing — the earlier
  `choropleth`+geo approach letterboxed and was replaced). Hover = county + GW + project
  names; click county → side list (name, GW, COD, status=`ginrStudyPhase`). Next planned:
  OpenInfraMap power-line raster layer via `layout.map.layers`.
- **Mistake to not repeat:** the first map used `choropleth`+`layout.geo`, which structurally
  letterboxes (fits the projection inside the box, pads the rest). Three rounds of
  aspect-ratio guessing/measuring made the dead space *worse* and the map smaller. Don't
  patch container geometry against a fitted geo projection — use the tile traces
  (`choroplethmap`/`scattermap`). And since no browser runs in this container, ask for a
  user screenshot after any visual change instead of iterating blind.
- Assets inlined from `assets/`: `plotly.min.js` (v2.35.2), `tx_counties.geojson` (STATE=48
  subset of plotly's US-counties FIPS geojson), `tx_county_fips.json` (alnum-normalized
  name→FIPS; queue counties join 198/198, no aliases needed).
- Cross-check any aggregation change against a pandas re-aggregation before shipping; the
  map JS mirrors the table JS aggregation.

## Research agent system (Workstream B — `scripts/research_tools/`)

Per-project OSINT research: is a queued project **real or paper**, and what is a defensible
**independent COD**? Replaces the old `reserach-agent-poor.py`. Two tiers, headless Claude
Code (`claude -p`) on **Bedrock**. Full running-system spec:
`docs/superpowers/specs/2026-07-18-research-agent-system-spec.md`.

**Entry points**
- `run_agent.py <INR> --mode triage|deep [--model …]` — one project. `--mode triage`
  (default): Sonnet, follows `research/TRIAGE_CHECKLIST.md` (T1–T7 budgeted steps), 60-turn
  cap, 120k fresh-token budget → `triage_findings.json` + `triage.md` with
  `deep_scan_recommended`. `--mode deep`: Sonnet (Opus via `--model us.anthropic.claude-opus-4-7`),
  follows `research/PLAYBOOK.md` (5 stages), 120-turn cap, **400k** budget → `findings.json`
  + `dossier.md` + `log.md` (+ `brief.html`). Reads any triage handoff first.
- `run_batch.py` — a cohort: parquet filter (`--cod-from/--cod-to/--fuel/--min-mw/--limit`
  or `--inrs/--inrs-file`), active-queue-only, `--concurrency` (default 3), resumable.
  Writes `research/_batches/<name>/summary.{json,csv}` + `deep_queue.txt`.
- `deep_worker.py [--model sonnet|opus]` — a serial deep-scan loop over the flagged queue
  (largest-MW first). **Safe to run several in parallel**: an atomic claim (`.deep_claim`
  via `O_EXCL`, stale >1h stolen) keeps workers off each other's INRs; `findings.json` is
  the done-gate; bounded retries (`MAX_ATTEMPTS=2`, then `.deep_failed`). This is how the
  deep phase scales — launch N of them.
- `make_deep_queue.py` — rebuild the live deep queue (all triage dirs) → `deep_queue_all.txt`.
- `puct.py` — PUCT Interchange search/download (throttled 2s shared interval, backoff on
  the portal's 402 rate-limit, system CA bundle for TLS). THE domain fact: every ERCOT TSP
  files executed IAs in ONE central docket, control **35077** (Subst. R. §25.195(e)) — search
  **FilingDescription**; `FilingParty=<project>` always returns 0. Primary flow is
  SYSTEMATIC, no dates (queue iaSigned is self-reported/stale), no fuzzy scores:
  `puct.py index` snapshots all docket filings locally (2 requests, 2000 rows/page,
  ItemMatch 3 = greater-than); `puct.py match <INR> --dir <sources/> [--key "<SPV>"]`
  matches exact name keys (queue name + deterministic generic-tail stripping + triage
  spv_name/developer) and VERIFIES each PDF: INR-in-text = CONFIRMED, county+MW-in-text =
  PROBABLE, else renamed `unverified_*`. `ia`/`search`/`filings`/`fetch` remain for manual
  follow-up (variant spellings: queue "Shepard" was filed as "Sheppard", TSP TNMP not
  CenterPoint).
- `ia_backfill.py` — deterministic no-LLM sweep: pull IA PDFs via puct.py for
  already-researched dirs missing them → `research/_batches/ia_backfill.csv`.
- `spv.py resolve <INR>` — systematic SPV/developer candidates (the GIS report does NOT
  publish the interconnecting entity; queue names are often codenames). Sources:
  **EIA-860M** `data/reference/eia860m_latest.xlsx` (deterministic county+prime-mover+MW
  join or plant-name substring → Entity Name, plant lat/lon, EIA status, planned COD —
  doubles as a site + COD cross-check) and the **local PUCT docket index** (non-TSP party
  of matching filings). Bulk table pre-computed: `research/_reference/spv_candidates.csv`
  (772 triaged: 293 w/ 860M hit, 221 w/ docket hit, 376 neither → SOS/registry work).
  Verify candidates via `puct.py match --key` (INR-in-PDF), never cite unverified.
- `eia_history.py <INR> [--write]` — the **EIA-860M second source**: monthly history of
  what the entity reports to EIA (planned COD / status / capacity) vs the developer's
  queue claims; divergence = stale queue COD (e.g. Red Egret: queue 2026-08-31, EIA said
  "2027-05, under construction ≤50%" for 7 straight months). Data:
  `data/eia_generator_tx.parquet` (TX slice of **AW.dbo.eiaGenerator** joined w/
  eiaPlant/eiaEntity/eiaStatus/eiaTechnology; monthly 2022-04→; **refresh via
  `eia_snapshot.py`** — the snapshot SQL lives there; the slice DOES carry county/lat/lon
  + `nameplateEnergyCapacity` MWh, fully populated) + `data/eia_plant_tx.parquet`
  (AW.dbo.eia860plant TX, annual). Plant match = name (dominates) else
  county(860M xlsx map)+prime-mover+MW≤5%; multiple candidates are LISTED never guessed
  (--plant-id). Emits **DROPPED_FROM_860M** (unit/plant vanished from newest snapshot =
  withdrawal/cancellation signal; deterministic key presence, date-vs-date only —
  `reportDate` is object dtype, string equality silently all-False). Schema verdicts for
  all ~11 eia* DB tables: `docs/eia_db_reference.md`. Deep wrap-up step 2 runs it;
  build_brief renders the tables + drop warning card when eia_history.json exists.
- **Registry resolvers** (SPV leads by fuel; same conventions as puct.py; `resolve` is
  read-only/agent-safe; every candidate is a LEAD — verify via `puct.py match --key`):
  `ch313.py resolve <INR>` (Comptroller Ch.313 static 740 rows + JETI API; keys on SCHOOL
  DISTRICT not county), `ch312.py resolve <INR>` (Comptroller Ch.312 county/city abatement
  registry ~1,400 rows via the same open-data API family; owner=SPV + reinvestment-zone
  name + DIRECT county field + per-year %s; THE abatement rung for post-2022 entries since
  Ch.313 expired — but CAD-submitted annually with gaps, so a miss is WEAK negative
  evidence), `faa.py resolve <INR>` (wind OE/AAA per-turbine cases → sponsor,
  ASN block, turbine centroid; live FAA sources blocked 2026-07: Socrata private + oeaaa
  shutdown — runs off cached pulls, self-heals on `refresh`), `tceq.py resolve <INR>`
  (data.texas.gov Central Registry, 5 regional tables, county-routed live SoQL; AIRNSR
  permit + owner names; same-named facility may be a co-located predecessor).
- `inr_harvest.py` → `research/_reference/puct_inr_join.json` — THE permanent docket↔INR
  join: every docket-35077 PDF ≥2018 downloaded once (data/reference/puct_docket_pdfs/),
  INR strings extracted (1,743 items → 1,201 with INRs, 897 distinct, 22 image-only).
  Resumable; re-run after monthly queue refresh.
- `search.py "<query>"` — the ONE search entrypoint (agents must not scrape ddg/bing).
  Backend ladder: AgentCore Gateway when `AGENTCORE_GATEWAY_URL` is set (admin approval
  pending) → **OAuth bridge** (headless `claude -p` on the container seat, Haiku +
  WebSearch only — temporary) → DDG HTML. 7-day cache, 3s throttle, 120/h fleet cap,
  banned queue-tracker domains suppressed at the tool layer.

**Bedrock env** (set by `run_agent.py`): `CLAUDE_CODE_USE_BEDROCK=1`, `AWS_PROFILE=read_only`,
`AWS_REGION=us-east-1`, `ANTHROPIC_SMALL_FAST_MODEL=sonnet` (Haiku 403s on this account).
`WebSearch` is **dead on Bedrock** (server-side tool, no Bedrock backend) — agents use
`search.py`, never raw search-engine scraping (log forensics: 7,260 wasted scrapes).

**RE-RUN POLICY (user, 2026-07-20): every user-ordered re-run/refresh gets
`--token-budget 1000000`** and a `sources/REFRESH_DIRECTIVE.md` with pre-computed
systematic leads (spv/ch313/eia/storm/rung-0) before launch.

**PIPELINE V2 (spec approved 2026-07-19)**: `docs/superpowers/specs/2026-07-19-pipeline-v2-design.md`
— factsheet.py deterministic pre-stage, INVERTED gating (triage kills paper; deep = precision
on real projects, ranked MW × COD-nearness), checkpointed deep stages, domain blocklist.
Live state: `PROGRESS.md`. Preservation: git = code/JSONs/briefs; S3 mirror =
**s3://gis-research** us-east-1 (append-only sync, same relative tree, dated parquet
snapshots) — MinimalReadOnlyUser still needs s3:ListBucket + Get/PutObject on the bucket
(policy pending with admin, probe 2026-07-19 AccessDenied).

**Budget system** (headless has no stdin, so budgeting is out-of-band). Fresh tokens =
`input + cache_creation + output` (cache **reads excluded** — they're cheap re-reads).
`budget_hook.py` (PostToolUse, stdlib on bare `python3`) reads `<dir>/.budget_state.json`
and feeds the agent a **warning at 80%** and a **wrap-up order at 100%**; the runner
hard-kills at **budget + 10k grace**. `max-turns` hit **with** required artifacts on disk =
exit 0 (a usable partial run, not a failure). Sonnet deep ≈ **$4.64/scan** mean; triage ≈ $1.

**Operating the fleet — hard-won rules**
- **Concurrency ≤ 15.** ~20 concurrent agents crashed the *Claude Code session* (event
  volume), NOT container RAM/disk (47 GB / ~450 GB free — ample). True agent count is
  `pgrep -fc 'claude [-]p'` — each agent shows as a `zsh→uv→python→claude` chain, so process
  listings over-count ~3–4×.
- **Launch background workers with an ABSOLUTE script path.** The session cwd can drift into
  `gis-research/`, and a relative `gis-research/scripts/...` path then fails to spawn
  (exit 2). The scripts' internal paths are absolute (`parents[2]`), so only `uv` needs the
  full path.
- `pkill -f "run_batch.py"` matches its **own** cmdline and self-kills — use the bracket
  trick `pkill -f "run_batch[.]py"`, parents first.
- **Do NOT poll background tasks** — wait for the completion notification or a user command.
- A `container_watchdog.sh` pattern (60s loop, hard-exit on low mem/disk/high swap) is the
  way to get notified before a resource wall.

**Security (do not weaken)**
- Real creds live ONLY in `~/.config/gis-research.env` (chmod 600, outside the repo) — never
  committed, printed, or pasted. Loaded by `cdse.py`/`gmaps.py` themselves.
- Agents write ONLY inside their assigned `research/<dir>/` and are blocked from
  `data/**` and `output/**` via `--disallowedTools`.
- **Banned sources** — queue aggregators (interconnection.fyi, cleanview.co, gridinfo.com,
  energyacuity, infrasure.ai, futuregrid.io, any queue tracker). Citing one = failed run. Enforced three
  ways: blocklist_hook (fetch denied), search.py (results suppressed), playbook rule 1.

**Known issues**
- **CDSE 403s were rate-limiting, not expired creds**: every chip call did a fresh
  password-grant login; concurrent agents tripped the identity endpoint (23% of deep scans
  ended imagery-less). Fixed 2026-07-19: `cdse.py get_token()` now uses a shared token
  cache (`$TMPDIR/.cdse_token_cache.json`, 0600, atomic replace, refresh 60s before
  expiry) + 10s/30s backoff on 403/429. If imagery-less runs recur, check that cache first.
- Deterministic wrap-up tools agents should call (don't hand-write these outputs):
  `queue_history.py <INR>` (COD drift from parquet), `build_brief.py`, `build_index.py`.

## Deferred / TODO

- SCED operational exclusion: cross-ref Snowflake `GenUnit`/`GenUnitGenQueue` (units with a
  SCED name / `seGenDeviceName` are online) to drop already-operational units the GIS report
  still lists. Not visible to the read-only role at `AWDEV.DBO.*`; needs the right db/role.
  Parked by user; the "approved-for-sync" exclusion is the interim proxy.
