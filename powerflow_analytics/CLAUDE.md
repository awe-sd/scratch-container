# powerflow_analytics

Reads SCOPF study output (Snowflake AWOPF) and finds CRR trading opportunities:
binding constraints → marginal units → outage/topology driver → (later) fast-scan
headroom + path optimization. The design spec file no longer exists; see the tracking issue "Clean-up of powerflow_analytics and fast_scan" on awe-sd/scratch-container.

## Conventions

- All DB access via `awconnect` with profile `read_only`, Snowflake warehouse `AI_READ_ONLY` (`pfa/config.py`).
- Snowflake goes ONLY through `pfa.sf.query`; SQL Server ONLY through `pfa.mssql.query` — no other module imports `awconnect` (config aside).
- `pfa.mssql.query` enforces the house rules in code: one SQL Server query at a time (process-wide lock), and any `toAllIsos`/`to*` outage-table query without an `isoMarketId` and a `BranchId`/`teid` predicate is rejected before it is sent.
- One reader per market-data source, all in `pfa/extract/`: `fastscan.py` (FAST_SCAN_CONFIG/RESULTS), `shifts.py` (CPNODE_/BUS_SHIFTS_VIEW), `dam_offers.py` (ERCOT60DDAMGENRESOURCE), `renewables.py` (wind/solar actuals), `popt.py` (AW.POPT path costs).
- Table names and their SQL live ONLY in that source's reader module (plus tests and prose); analysis modules and scripts call the reader and never embed the table name.
- A new query against one of those sources is a new function in its reader, with a test that fakes `sf.query`/`mssql.query` and asserts the scoping predicates (see `tests/test_extract_*.py`).
- Extract once per study: `uv run powerflow_analytics/scripts/pull_study.py --study <id>` → parquet in `cache/study_<id>/` (gitignored). Analysis and Dash read the cache only — never Snowflake in callbacks.
- Analyze: `uv run powerflow_analytics/scripts/build_report.py --study <id> --cutoff <YYYY-MM-DD> [--tickets]` → CSVs in `output/study_<id>/`.
- SQL Server (`AW.dbo.toAllIsos`) gets ONLY targeted single-branch lookups (`pfa/extract/outages.py`) — never bulk queries, and strictly ONE query at a time (sequential).
- toAllIsos hygiene: every revision is a row — ALWAYS collapse to latest revision per outageIdentifier (`ROW_NUMBER() OVER (PARTITION BY outageIdentifier ORDER BY revNum DESC)=1`) and read current state from `toState`. ALWAYS read the `Notes` free text on candidate tickets — it carries the TSP's REQ/RAS/SUP narrative (mitigation intent, ERCOT TOAP directive ids, breaker-split handoffs) and is stronger evidence than timing/status inference (lesson: ERSKINE–MACKNZIE RAS TOAP041923-0 was spelled out in Notes). TSP ticket prefixes identify the submitter (e.g. `CLU%` = Lubbock LP&L); forced/as-operated mitigations show ~zero or negative submit-to-start gaps.
- 2026-11-27: FAST_SCAN_RESULTS.TIMESTAMP is hour-BEGINNING (DAM HE n is stored at hour n-1; verified config 81760: ercotDampsseLnView HE1 RATEB = TIMESTAMP 00:00 DAM_RATE_B; solar impact starts 07:00-08:00 and ends ~20:00), so HE7-22 = HOUR 6..21. Classify via `pfa.periods.fastscan_hour_class` (OnPeak / 2x16 / 7x8, NERC holidays excluded); never filter `.dt.hour` by hand.
- Constraint identity = (FROMNUM, TONUM, CKT, CTGLABEL). Use the `*2` output tables; v1 OUTBRANCH is empty for recent studies, and OUTGEN2.GENUNITID is NULL — gen identity routes (BUSNUM, ID) → OUTGENREF → AWDEV.DBO.GENUNIT.
- Binding = LIMVIOLPCT >= 99.5 in OUTCTGVIOL2 (SCOPF holds constraints at ~100). ">100" alone is NOT unresolved — solver tolerance overshoots by ~0.01 MW routinely (study 14492: 28 of 29 >100% rows were tolerance). Materially unresolved = real MW overshoot (≳0.5 MW / LIMVIOLPCT ≳ 100.5) — cross-check OUTCONSTRAINT2 for λ at the 3500 cap with OPFCNCUP=−3500/negative slack. OPFBINDING/MARGCOSTMVA in OUTBRANCH2 are only set for base-case (pre-ctg) binders.

## Planning studies vs auction studies (learned on 14492, 2026-08-19)

- ptoid identifies the family: **1504** = Sep-2026 auction models (14411/12/31...),
  **1316** = long-horizon planning runs (e.g. 14492 = 2028 vintage). Planning runs give
  NO directly tradable CRR read — frame results accordingly.
- Planning scenario grids are UNBALANCED (month×hour cells with different run counts,
  e.g. Jul/Aug HE17 doubled): always report the **cell-weighted** binding rate alongside
  the raw share, and never extrapolate 2-sampled-hour rates to peak hours.
- **Sibling contingencies**: two ctgs can bind the identical run set (14492: SMGIENW8 vs
  DENWSTE8, SF vectors corr 0.99999). OUTCONSTRAINT2 carries only the LP-active one
  (CTGRANK 1) — count ONE flowgate, or you double congestion rent.
- OUTCONSTRAINT2 λ rows can be MISSING for the slackest binders; the LP writes λ=0 for
  present-but-slack, so **zero-impute** missing binder rows for mean-type stats (report
  both bases). Ratings (LIMITMVANORMAL=LIMVIOLLIMIT=LIMITMVACTG) key on month AND hour.
- dispatch_screen's "unenforceable — no dispatchable relief pair" tag presumes a declinable
  planned outage; it does NOT apply to base-case N-1 ctgs in NoOutage studies (TOUTSETID
  all NULL) — those are enforced regardless; λ then = the lone mover's opportunity cost.

## Standing rule (sdalvi, 2026-08-12): reusable functions, not one-off queries

Every requested analysis must land as a reusable, parameterized function in `pfa/` (plus a
thin CLI in `scripts/` where useful) — e.g. constraint valuation, marginal-unit resolution,
DAM offer pulls. Answer the user's question BY running the function. Extend existing
modules before adding new scripts.

## Access status (updated 2026-08-11 — all grants LANDED)

- `SHIFT_FACTORS.DBO.CPNODE_SHIFTS_VIEW` / `BUS_SHIFTS_VIEW`, `AW.FLOW_ANALYSIS.*`,
  `AW.POPT.*`, and `AWVAL.DBO.*` are ALL readable by the read_only role. Do not treat any
  of them as blocked. Gotcha: `SHIFT_FACTORS.DBO.DEVICE_SHIFTS` simply has NO ROWS for
  recent studies (e.g. 14411) — use the CPNODE/BUS shift views instead; empty ≠ blocked.
- Fast-scan tables (FAST_SCAN_CONFIG/RESULTS/RT_CONSTRAINTS/RUN_LOG) live in `AW.FLOW_ANALYSIS`; `AWDEV.FLOW_ANALYSIS` was renamed `_DEPRECATED` (2026-11-26); schema name is `pfa.config.FLOW_ANALYSIS`.
- Container constraint: hard 8 GiB cgroup memory cap (~3 GB usable after IDE daemons) —
  report scripts must load parquet columns selectively and free frames aggressively.
- SQL Server: device-scoped, TOP-capped, SEQUENTIAL queries only (never parallel).

## OUTGEN2 schema drift (found 2026-09-11, study 14605)

There is **ONE** `AWOPF.DBO.OUTGEN2` table (not a per-study or per-vintage copy) — so when study
14605 (ptoid 1517) was found missing both `FUELZONE` and `RENEWZONE`, that means those columns are
now **gone from OUTGEN2 for every study**, including old ones. Studies 14411/12/25/31/14492 only
*appear* to still have both columns because their `cache/study_*/outgen2.parquet` files were
extracted before the schema changed and are read cache-first (no live Snowflake round trip on a
cache hit) — a fresh Snowflake pull of any of those studies today would hit the same missing
columns. This is a live schema change upstream, not a study-specific quirk.

`pfa/extract/results.py::fetch_gen()` now probes `AWOPF.INFORMATION_SCHEMA.COLUMNS` and selects
`NULL AS FUELZONE` / `NULL AS RENEWZONE` when either is absent, so the fetch no longer breaks — but
this **masks** the drift rather than surfacing it: any future analysis run today (or any cache
rebuild) silently gets NULL FUELZONE/RENEWZONE with no other tell than an empty column. Confirmed
non-regressive for the one place that could have depended on them: `IS_RENEWABLE` classification in
`pfa/analysis/lambda_engine.py::relief_set()` derives from `OUTGEN2.FUELTYPE` (e.g. "SUN (Solar)",
"WND (Wind)"), not FUELZONE/RENEWZONE, and correctly classified 171 renewable units on study 14605
under this fix. If a future analysis needs FUELZONE/RENEWZONE specifically (not just FUELTYPE), it
will get silent NULLs — check `fetch_gen()`'s docstring note before assuming those columns carry data.
