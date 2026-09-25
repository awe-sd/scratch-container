# Deploy runbook: Fast-scan V2 (snapshot-grain rewrite)

Pre-deployment compile check done 2026-09-25 under role `AI_READ_ONLY` (read-only,
cannot run DDL/DML on `FLOW_ANALYSIS` tables). This runbook is for **sdalvi, role
`AW_ACCESS`**. See Appendix A for the full `EXPLAIN` results and Appendix B for what
could not be compile-checked in this role.

**No SQL-compile defects were found** in any of the three files -- every extracted
statement compiles (Appendix A). Two things below are **not** compile defects but do
need sdalvi's attention before/while running the deploy: a by-eye finding on the
`FAST_SCAN_RT_CONSTRAINTS` NOT NULL columns (Task 2, item 3), and a real operational
blocker in the originally-specified V2 smoke test (step 6).

Files (all in `stationinjection/`): `sp_fast_scan_v2.sql`, `sp_load_fast_scan_rt_constraints.sql`,
`validation_spV2.sql`.

## Deployment is partially in progress -- check state before running anything

A **later** check in this same session (after the compile-check facts quoted in this
file's brief were established) found the DB had already moved. This was a single
point-in-time snapshot while another actor (sdalvi or a concurrent process) was
apparently working through this same deploy in parallel -- treat it as "what one
snapshot showed," not as settled fact, and **re-verify every row below immediately
before running the corresponding step**:

| Object | Observed 2026-09-25 (re-verify before acting) |
|---|---|
| `FAST_SCAN_RESULTS.RT_INTERVAL` | Present (`TIMESTAMP_NTZ(9)`, nullable) -- `DESCRIBE TABLE AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS` and check for this column before running step 1's `ALTER` |
| `FAST_SCAN_RT_CONSTRAINTS` (table) | Present (0 rows, created 2026-09-25 07:22:52 by `AW_ACCESS`) -- check `SHOW TABLES LIKE 'FAST_SCAN_RT_CONSTRAINTS' IN SCHEMA AW.FLOW_ANALYSIS` before step 2 (its `CREATE TABLE IF NOT EXISTS` is safe either way) |
| `AI_READ_ONLY` can `SELECT` from `FAST_SCAN_RT_CONSTRAINTS` | Worked (returned 0 rows, no privilege error) -- either an explicit GRANT already ran, or the schema has a future-grant policy; step 5's GRANT is safe to run regardless (idempotent) |
| `SP_LOAD_FAST_SCAN_RT_CONSTRAINTS`, `SP_RUN_FAST_SCAN_TEST_V2`, `SP_RUN_VALIDATION_FAST_SCAN_TEST_V2` | None existed yet (`SHOW PROCEDURES IN SCHEMA AW.FLOW_ANALYSIS` listed only the old `SP_RUN_VALIDATION_FAST_SCAN` V1) -- re-check before steps 2-4 in case they've since been created |
| `FAST_SCAN_CONFIG` CONFIG_ID 256501 | New row, created 2026-09-25 07:34:44 by SDALVI: `PSENSHIFTID=104716921`, `BRANCH_LABEL='651_B'`, `CTG_LABEL='DMBDRKC5'`, `DEFAULT_RATE_B=179.0` -- same branch/contingency/default as 254330, `SOURCE_TYPE='STUDY'`, zero `FAST_SCAN_RESULTS` rows at observation time |

**Snowflake's `ADD COLUMN` has no `IF NOT EXISTS` guard** -- if `RT_INTERVAL` is present
when you check, running the `ALTER` again errors `column 'RT_INTERVAL' already exists`
and (if run as part of a single multi-statement script) can abort before reaching the
`CREATE OR REPLACE PROCEDURE` further down the same file.

## Deploy order

1. **`ALTER TABLE AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS ADD COLUMN RT_INTERVAL
   TIMESTAMP_NTZ;`** (line 19 of `sp_fast_scan_v2.sql`) -- first run
   `DESCRIBE TABLE AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS` and check whether `RT_INTERVAL`
   is already listed. Observed present at 2026-09-25 (see table above); if still present
   when you check, **skip this statement** (comment out line 19 before running
   `sp_fast_scan_v2.sql` as one script, or the whole script aborts before reaching
   `CREATE OR REPLACE PROCEDURE`). If absent, run it -- existing rows get NULL for this
   column, as intended.

2. **Run `sp_load_fast_scan_rt_constraints.sql`** end to end. Its `CREATE TABLE IF NOT
   EXISTS FAST_SCAN_RT_CONSTRAINTS` is safe regardless of whether the table already
   exists (its shape was verified by eye against the live table, Task 2). First check
   `SHOW PROCEDURES IN SCHEMA AW.FLOW_ANALYSIS` for `SP_LOAD_FAST_SCAN_RT_CONSTRAINTS` --
   absent at 2026-09-25; if still absent, run the file.

3. **Run `sp_fast_scan_v2.sql`** (skipping line 19's `ALTER` if step 1 determined it's
   already applied). Check `SHOW PROCEDURES` for `SP_RUN_FAST_SCAN_TEST_V2` first --
   absent at 2026-09-25.

4. **Run `validation_spV2.sql`.** Check `SHOW PROCEDURES` for
   `SP_RUN_VALIDATION_FAST_SCAN_TEST_V2` first -- absent at 2026-09-25.

5. **Grant read access to the new table** (idempotent if already granted):
   ```sql
   GRANT SELECT ON TABLE AW.FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS TO ROLE AI_READ_ONLY;
   ```

6. **Smoke tests -- V2 needs a config with no existing rows, NOT config 254330.**
   `SP_RUN_FAST_SCAN_TEST_V2`'s step 0 is an unconditional, date-range-blind guard:
   `SELECT COUNT(*) ... WHERE CONFIG_ID = :P_CONFIG_ID; IF (count > 0) THEN RETURN
   'EXISTING_CONFIG_ID'`. Verified: **config 254330 already has 39,262 rows** in
   `FAST_SCAN_RESULTS` (2022-01-01 through 2026-07-12, all on-the-hour V1 rows) -- *any*
   call with `CONFIG_ID=254330`, any date range, returns `EXISTING_CONFIG_ID` immediately
   and inserts nothing. Picking a different date range does not help; the guard is keyed
   on `CONFIG_ID` alone. Use the freshly-created config **256501** instead (same branch
   `651_B` / contingency `DMBDRKC5` as 254330, `PSENSHIFTID=104716921`, zero existing
   rows):
   ```sql
   CALL AW.FLOW_ANALYSIS.SP_RUN_FAST_SCAN_TEST_V2(256501, '2026-06-01', '2026-06-14', TRUE, 6);
   CALL AW.FLOW_ANALYSIS.SP_RUN_VALIDATION_FAST_SCAN_TEST_V2(256315, '2026-06-02', '2026-06-08', TRUE, 6);
   ```
   The validation proc has **no such guard** -- it uses `already_present`/`NOT EXISTS`
   on exact `TIMESTAMP`, and V2's new rows carry `:57` stamps that never collide with
   V1's existing `:00` stamps, so config 256315 (which already has 972 V1 rows in this
   exact range) is fine to reuse as-is; new V2 rows will be added alongside the old V1
   ones. This asymmetry (V2 blocks on any existing row for the config; validation V2
   does not) is a property of the deployed code, not a bug -- just don't reuse 254330 for
   the V2 smoke test.
   Both calls should return `'status': 'SUCCESS'`.

7. **Read-only verification queries**, expected numbers adapted from the dry run in
   `SESSION_HANDOFF.md` §"Fast-scan V2" / §"Validation fast-scan V2" (which used 254330;
   256501 is a fresh config on the same branch/contingency so row-count magnitudes should
   be comparable for the same date range, not necessarily identical -- treat the dry-run
   numbers as a sanity ballpark, not an exact target, since 256501's `PSENSHIFTID` is
   newer than 254330's). All seven queries below were `EXPLAIN`ed against the real
   `FAST_SCAN_RESULTS`/`FAST_SCAN_RT_CONSTRAINTS` tables in this session and compile
   cleanly (Appendix A).

   **Row count for the smoke-test range:**
   ```sql
   SELECT COUNT(*) AS n
   FROM AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS
   WHERE CONFIG_ID = 256501 AND TIMESTAMP >= '2026-06-01' AND TIMESTAMP < '2026-06-15';
   ```

   **DAM_RATE_B matches V1 at the next hour** -- not directly checkable for 256501 (it
   has no pre-existing V1 rows to compare against, by construction). Instead compare
   against 254330's existing V1 rows on the same branch for the same range. This is valid
   because 254330 and 256501 share the same `BRANCH_NAME` (`651_B`) and the same
   `DEFAULT_RATE_B` (179.0, verified via `FAST_SCAN_CONFIG` 2026-09-25) -- `DAM_RATE_B`
   is sourced purely from `ercotDampsseLnView` keyed on `branchname`/hour (with the same
   fallback default for both configs), not from anything config-specific. Expect 0.0000
   max diff:
   ```sql
   SELECT COUNT(*) AS n_compared, MAX(ABS(v2.DAM_RATE_B - v1.DAM_RATE_B)) AS max_diff
   FROM AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS v2
   JOIN AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS v1
     ON v1.CONFIG_ID = 254330
    AND v1.TIMESTAMP = DATE_TRUNC('HOUR', DATEADD('MINUTE', 30, v2.TIMESTAMP))
   WHERE v2.CONFIG_ID = 256501
     AND v2.TIMESTAMP >= '2026-06-01' AND v2.TIMESTAMP < '2026-06-15'
     AND MINUTE(v2.TIMESTAMP) != 0;  -- V2 rows only -- without this filter a 256501 row
   -- that happens to land on-the-hour would self-join to a V1 row at the SAME hour
   -- (not the next hour) and silently pass a comparison that isn't the one intended.
   ```

   **RT_INTERVAL non-null (new column populated) -- expect > 0 rows:**
   ```sql
   SELECT COUNT(*) AS n_with_rt_interval
   FROM AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS
   WHERE CONFIG_ID = 256501 AND RT_INTERVAL IS NOT NULL
     AND TIMESTAMP >= '2026-06-01' AND TIMESTAMP < '2026-06-15';
   ```

   **RT_CONSTRAINT_VALUE non-null only for the config's own contingency** (some NULLs
   expected -- other contingencies binding instead, by design; those live in the detail
   table):
   ```sql
   SELECT COUNT(*) AS n_total, COUNT(RT_CONSTRAINT_VALUE) AS n_non_null
   FROM AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS
   WHERE CONFIG_ID = 256501 AND TIMESTAMP >= '2026-06-01' AND TIMESTAMP < '2026-06-15';
   ```

   **Validation, config 256315, 2026-06-02..2026-06-08 -- expect ~157 new V2 rows**
   (dry-run number; may shift slightly once `ERCOTSTATIONINJECTION` is rebuilt, see item 9):
   ```sql
   SELECT COUNT(*) AS n
   FROM AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS
   WHERE CONFIG_ID = 256315 AND TIMESTAMP >= '2026-06-02' AND TIMESTAMP < '2026-06-09'
     AND MINUTE(TIMESTAMP) != 0;  -- V2 rows only, excludes the 972 pre-existing V1 rows
   ```

   **PSENSHIFTID 100% match to V1 rows on the same hour bucket** (same-bucket join,
   `V2.HOUR_BUCKET == V1.TIMESTAMP`, per the floor-vs-nearest note in
   `SESSION_HANDOFF.md` -- convention-invariant, should match exactly):
   ```sql
   SELECT COUNT(*) AS n_compared,
          SUM(IFF(v2.PSENSHIFTID = v1.PSENSHIFTID, 1, 0)) AS n_match
   FROM AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS v2
   JOIN AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS v1
     ON v1.CONFIG_ID = v2.CONFIG_ID
    AND v1.TIMESTAMP = DATE_TRUNC('HOUR', DATEADD('MINUTE', 30, v2.TIMESTAMP))
   WHERE v2.CONFIG_ID = 256315
     AND v2.TIMESTAMP >= '2026-06-02' AND v2.TIMESTAMP < '2026-06-09'
     AND MINUTE(v2.TIMESTAMP) != 0;  -- V2 rows only
   -- n_compared should equal n_match
   ```

   **Detail table: for every (TIMESTAMP, CONTINGENCY) with IS_CONFIG_CTG = TRUE, the
   value equals FAST_SCAN_RESULTS.RT_CONSTRAINT_VALUE at the nearest interval:**
   ```sql
   SELECT COUNT(*) AS mismatches
   FROM AW.FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS c
   JOIN AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS r
     ON r.CONFIG_ID = c.CONFIG_ID AND r.TIMESTAMP = c.TIMESTAMP
   WHERE c.IS_CONFIG_CTG
     AND c.CONFIG_ID IN (256501, 256315)
     AND (r.RT_CONSTRAINT_VALUE IS DISTINCT FROM c.RT_CONSTRAINT_VALUE
          OR r.RT_INTERVAL IS DISTINCT FROM c.RT_INTERVAL);
   -- expect 0
   ```

8. **`ERCOTSTATIONINJECTION` must be rebuilt before V2 goes to production.** Verified
   2026-09-25: the table still contains rollout-night stub snapshots (34 rows at
   `2026-06-02 23:52:00`) and 5 nearest-hour buckets in June 2026 with more than one
   snapshot -- it has not yet been rebuilt with the one-snapshot-per-hour proc
   (`SP_LOAD_ERCOT_STATION_INJECTION` per §7 "One snapshot per nearest-hour bucket" in
   `SESSION_HANDOFF.md`). Until that rebuild runs:
   - V2 (snapshot-grain) will pick up the stub/duplicate rows as extra, spurious
     snapshots -- this is the root cause already diagnosed for the 2026-06-02 23:52:00
     outlier in the validation dry run (flow -0.01, CPSES bus shifts otherwise normal).
   - Once rebuilt, expect V2 row counts to drop slightly (duplicate/stub snapshots
     removed) and the near-zero-flow outlier rows to disappear. Re-run the row-count and
     RT_INTERVAL verification queries above after the rebuild to confirm counts shift
     as expected -- do not treat a small row-count drop post-rebuild as a regression.

9. **Rollback:** if any smoke test or verification query fails,
   ```sql
   DROP PROCEDURE AW.FLOW_ANALYSIS.SP_RUN_FAST_SCAN_TEST_V2(NUMBER, DATE, DATE, BOOLEAN, NUMBER);
   DROP PROCEDURE AW.FLOW_ANALYSIS.SP_RUN_VALIDATION_FAST_SCAN_TEST_V2(NUMBER, DATE, DATE, BOOLEAN, NUMBER);
   DROP PROCEDURE AW.FLOW_ANALYSIS.SP_LOAD_FAST_SCAN_RT_CONSTRAINTS(NUMBER, DATE, DATE, NUMBER);
   ```
   The `RT_INTERVAL` column and the `FAST_SCAN_RT_CONSTRAINTS` table (and any rows
   already written into either) can stay -- the added column is nullable and additive,
   and the detail table is additive and only read by these three procs.

---

## Task 2: DDL review by eye

`AI_READ_ONLY` cannot `EXPLAIN` or execute DDL, so this is a manual read against what
each proc actually writes.

**`CREATE TABLE IF NOT EXISTS AW.FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS`** (already
created in this account -- current live shape confirmed via `SHOW TABLES` /
`DESCRIBE TABLE`, matches the file):

| Column | Declared type | Fed by (in `SP_LOAD_FAST_SCAN_RT_CONSTRAINTS`) | Source type | Match? |
|---|---|---|---|---|
| `CONFIG_ID` | `NUMBER` (=`NUMBER(38,0)`) | `:P_CONFIG_ID` | `FAST_SCAN_CONFIG.CONFIG_ID NUMBER(38,0)` | OK |
| `TIMESTAMP` | `TIMESTAMP_NTZ NOT NULL` | `b.TIMESTAMP` <- `Snapshots.TIMESTAMP` <- `FAST_SCAN_RESULTS.TIMESTAMP` | `TIMESTAMP_NTZ(9) NOT NULL` | OK |
| `RT_INTERVAL` | `TIMESTAMP_NTZ NOT NULL` | `b.RT_INTERVAL` <- `cfp.DATETIME` (`CONGFQPRICEVIEW`) | `TIMESTAMP_NTZ(9)`, inner-joined (never NULL here) | OK |
| `CONTINGENCY` | `VARCHAR NOT NULL` | `b.CONTINGENCY` <- `cdc.CONGCONTNAME` (`CONGDEFCONSTRAINTVIEW`) | `VARCHAR(16777216)`, **nullable in the view's schema** | see item 3 below |
| `IS_CONFIG_CTG` | `BOOLEAN NOT NULL` | `REPLACE(UPPER(b.CONTINGENCY),' ','') = REPLACE(UPPER(:v_ctg_label),' ','')` | evaluates to `NULL` (not `TRUE`/`FALSE`) if either side is `NULL` | see item 3 below |
| `CONSTRAINT_NAME` | `VARCHAR` (nullable) | `b.CONSTRAINT_NAME` <- `cdc.ISOCONSTRAINTNAME` | `VARCHAR(16777216)`, nullable | OK (target nullable) |
| `RT_CONSTRAINT_VALUE` | `FLOAT` (nullable) | `ROUND(b.RT_VALUE, 2)` | numeric | OK |
| `RT_CONSTRAINT_LIMIT` | `FLOAT` (nullable) | `ROUND(b.RT_LIMIT, 2)` | numeric | OK |
| `RT_ACTUAL_HEADROOM` | `FLOAT` (nullable) | `ROUND(b.RT_LIMIT - b.RT_VALUE, 2)` | numeric | OK |
| `COMPUTED_AT` | `TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()` | not in the INSERT column list | defaults correctly | OK |

INSERT column list (9) matches the `SELECT` list (9) 1:1 in count and order.

**Item 3 -- real finding, not a compile defect:** `CONGDEFCONSTRAINTVIEW.CONGCONTNAME`
is declared nullable (`DESCRIBE VIEW` confirms `null? = Y`), but the table declares
`CONTINGENCY NOT NULL` and `IS_CONFIG_CTG NOT NULL` (which is itself computed from
`CONTINGENCY`). If a binding row ever has `CONGCONTNAME IS NULL`, the `INSERT` into
`FAST_SCAN_RT_CONSTRAINTS` fails a NOT NULL constraint at *run* time -- a failure mode
`EXPLAIN` cannot catch since it's a data condition, not a syntax error. **Checked
empirically 2026-09-25:** `SELECT COUNT(*) FROM AW.DBO.CONGDEFCONSTRAINTVIEW WHERE
CONGCONTNAME IS NULL` returns **0 of 234,964 rows**. So today's data will not trip this,
but the constraint is not structurally guaranteed by the source view's own schema --
flag as a low-probability, real latent risk rather than an active bug. No code change
recommended pre-deploy (the empirical check is clean and re-running it is cheap); if it
ever does trip, the fix is either `COALESCE(cdc.CONGCONTNAME, 'UNKNOWN')` in the SELECT
or dropping the NOT NULL on those two columns.

**`ALTER TABLE AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS ADD COLUMN RT_INTERVAL
TIMESTAMP_NTZ;`** -- syntax is valid Snowflake DDL (already executed successfully, per
the live `DESCRIBE TABLE` in the "Deployment is partially in progress" section above).
Type matches `cfp.DATETIME` (`TIMESTAMP_NTZ(9)`), the only expression written into it by
both `sp_fast_scan_v2.sql` and `validation_spV2.sql`.

**GRANT needed:** `GRANT SELECT ON TABLE AW.FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS TO
ROLE AI_READ_ONLY;` -- already effectively in place (verified empirically, see the state
table above); re-running it is harmless.

---

## Appendix A: EXPLAIN results

All statements run as `EXPLAIN USING TEXT <literal-bound statement>` under
`AI_READ_ONLY`, warehouse `READ_ONLY_WH`, database `AW`. Binds: V2/RT sub-proc used
`CONFIG_ID=254330`, `2026-06-01..2026-06-03`, `ISO=6`; validation V2 used
`CONFIG_ID=256315`, `2026-06-02..2026-06-04`, `ISO=6`. `v_*` locals populated from
`FAST_SCAN_CONFIG` via inline scalar subqueries (equivalent to the procs' own
`SELECT ... INTO`); `TMP_VAL_MEMBER_HOURS` inlined as a CTE built from its own defining
`SELECT` (`TOPOLOGYSHIFTSET` x `PSENSHIFTDEF` x `OPFRUN`, dedup + date-filtered per the
proc's own logic) since it cannot be materialized as a real temp table without `CREATE`
privilege.

| File | # | Statement (first 60 chars) | Result |
|---|---|---|---|
| sp_fast_scan_v2.sql | V2-1 | `SELECT COUNT(*) FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS WHERE C` | OK |
| sp_fast_scan_v2.sql | V2-2 | `SELECT PSENSHIFTID, FROM_NUM, TO_NUM, CKT, CTG_LABEL, DIRECT` | OK |
| sp_fast_scan_v2.sql | V2-3 | `SELECT COALESCE(DATE_TRUNC('DAY', MAX(TIMESTAMP)) + INTERVAL` | OK |
| sp_fast_scan_v2.sql | V2-4 | Main `INSERT...SELECT` (as bare SELECT), unauth objects unstubbed | ERROR: `Object 'AW.DBO.PARERCOTVIEW' does not exist or not authorized` (expected) |
| sp_fast_scan_v2.sql | V2-4b | Same, with `PARERCOTVIEW`/`ERCOT_RESOURCE_ADEQUACY_REPORT_VIEW` stubbed to empty `VALUES`-shaped subqueries (same column names) | **OK** |
| sp_fast_scan_v2.sql | V2-4-TRUE | The real `INSERT INTO FAST_SCAN_RESULTS (...) SELECT ...` (target table, at the time still pre-ALTER), unauth objects stubbed | ERROR: `Insufficient privileges ... must have INSERT granted on TABLE AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS` -- privilege check fires before column resolution, so this role cannot independently confirm the "RT_INTERVAL missing" failure mode; verified by eye instead (Task 2) |
| sp_load_fast_scan_rt_constraints.sql | RT-1 | `SELECT FROM_NUM, TO_NUM, CKT, PTOID, CTG_LABEL FROM FLOW_ANA` | OK |
| sp_load_fast_scan_rt_constraints.sql | RT-2 | `DELETE FROM FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS WHERE CON` | ERROR: `Insufficient privileges ... must have DELETE granted on TABLE AW.FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS` (expected -- role has no DELETE grant regardless of the table's existence) |
| sp_load_fast_scan_rt_constraints.sql | RT-3 | Main `INSERT...SELECT` (as bare SELECT) -- target table not read, only written, so no stub needed | **OK** |
| sp_load_fast_scan_rt_constraints.sql | RT-3-TRUE | The real `INSERT INTO FAST_SCAN_RT_CONSTRAINTS (...) SELECT ...` | ERROR: `Insufficient privileges ... must have INSERT granted on TABLE AW.FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS` (expected -- no INSERT grant) |
| validation_spV2.sql | VAL-1 | `SELECT SOURCE_TYPE, TOPOLOGYSHIFTSETID, STUDY_ID, FROM_NUM, ` | OK |
| validation_spV2.sql | VAL-2 | Member-hours defining `SELECT` (the `INSERT INTO TMP_VAL_MEMBER_HOURS SELECT ...` body, as bare SELECT) | OK |
| validation_spV2.sql | VAL-3 | `members_total` count, `TMP_VAL_MEMBER_HOURS` inlined pre-dedup | OK |
| validation_spV2.sql | VAL-4 | `dupes_dropped` count (`WHERE RN > 1`) | OK |
| validation_spV2.sql | VAL-5 | `DELETE FROM TMP_VAL_MEMBER_HOURS WHERE RN > 1` | NOT CHECKABLE (temp table; see Appendix B) -- by eye: `RN` is a declared column, syntax correct |
| validation_spV2.sql | VAL-6 | `MIN(TS)::DATE` date-range default, post-dedup | OK |
| validation_spV2.sql | VAL-7 | `MAX(TS)::DATE` date-range default, post-dedup | OK |
| validation_spV2.sql | VAL-8 | `DELETE FROM TMP_VAL_MEMBER_HOURS WHERE TS::DATE < ... OR > ...` | NOT CHECKABLE (temp table) -- by eye: `TS` is a declared column, syntax correct |
| validation_spV2.sql | VAL-9 | `members_in_range` count, post date-filter | OK |
| validation_spV2.sql | VAL-10 | `already_present` count (join to `FAST_SCAN_RESULTS`) | OK |
| validation_spV2.sql | VAL-11 | Main `INSERT...SELECT` (as bare SELECT), unauth objects unstubbed | ERROR: `AW.DBO.PARERCOTVIEW` not authorized (expected) |
| validation_spV2.sql | VAL-11b | Same, unauth objects stubbed | **OK** |
| validation_spV2.sql | VAL-11-TRUE | The real `INSERT INTO FAST_SCAN_RESULTS (...) SELECT ...`, unauth objects stubbed | ERROR: `Object 'TMP_VAL_MEMBER_HOURS' does not exist or not authorized` -- confirms the temp table (not a permanent object) is the only reason this exact statement can't run standalone; the CTE-inlined equivalent (VAL-11b) already validates the query logic |
| validation_spV2.sql | VAL-12 | `hours_missing` count | OK |
| deploy runbook §7, query 1 | -- | Row count for CONFIG_ID 256501 | OK |
| deploy runbook §7, query 2 | -- | DAM_RATE_B self-join (256501 vs 254330) | OK |
| deploy runbook §7, query 3 | -- | RT_INTERVAL non-null count | OK |
| deploy runbook §7, query 4 | -- | RT_CONSTRAINT_VALUE non-null count | OK |
| deploy runbook §7, query 5 | -- | Row count for CONFIG_ID 256315 | OK |
| deploy runbook §7, query 6 | -- | PSENSHIFTID self-join match rate | OK |
| deploy runbook §7, query 7 | -- | Detail-table mismatch check (`FAST_SCAN_RT_CONSTRAINTS` join) | OK |

**No SQL-compile defects found.** Every non-expected-failure statement returned OK on
first or second attempt (after stubbing the two known-unauthorized views). No SQL edits
were needed in any of the three files. This is a narrower claim than "nothing is wrong
with this deploy": two real, non-compile findings exist and both require sdalvi's
attention --
(a) the `CONGDEFCONSTRAINTVIEW.CONGCONTNAME` nullability vs. `FAST_SCAN_RT_CONSTRAINTS`
NOT NULL coupling (Task 2, item 3 -- empirically clean today, structurally unguaranteed);
(b) the brief's own literal V2 smoke-test call, `CALL SP_RUN_FAST_SCAN_TEST_V2(254330,
...)`, is a genuine operational defect in the deploy plan as specified -- 254330 already
has 39,262 `FAST_SCAN_RESULTS` rows, so that exact call returns `EXISTING_CONFIG_ID` and
inserts nothing, regardless of date range (deploy step 6 above uses config 256501
instead, for this reason).

**Column-list / target-table alignment, verified by eye** (since the true `INSERT`
statements are blocked by privilege errors rather than reaching column resolution):
- `sp_fast_scan_v2.sql` / `validation_spV2.sql`: INSERT column list (17 columns,
  `CONFIG_ID` .. `PSENSHIFTID`) matches the final `SELECT` list 1:1 in count, order, and
  implied type in both files. `RT_INTERVAL` (position 11 in both) is sourced from
  `r.RT_INTERVAL` <- `cfp.DATETIME`, which `DESCRIBE VIEW AW.DBO.CONGFQPRICEVIEW`
  confirms is `TIMESTAMP_NTZ(9)` -- matches the (now-applied) `RT_INTERVAL
  TIMESTAMP_NTZ` column exactly.
- `sp_load_fast_scan_rt_constraints.sql`: INSERT column list (9 columns) matches the
  `SELECT` list 1:1; types checked against the `CREATE TABLE` (Task 2).

## Appendix B: not checkable in this role

- **Snowflake Scripting control flow** (`DECLARE`/`LET`/`IF`/`EXCEPTION`/`RETURN`,
  `CREATE OR REPLACE PROCEDURE` itself) cannot be compiled without `CREATE PROCEDURE`
  privilege -- `AI_READ_ONLY` can only `EXPLAIN` the individual DML statements extracted
  from the procedure bodies, not the procedures as executable units. This covers all
  three `CREATE OR REPLACE PROCEDURE ... AS '...'` blocks in full.
- **`DELETE FROM TMP_VAL_MEMBER_HOURS ...`** (two statements in `validation_spV2.sql`,
  VAL-5 and VAL-8): a session-scoped temporary table cannot be materialized without
  `CREATE TABLE` privilege, so these `DELETE`s cannot be `EXPLAIN`ed against a real
  object. Verified by eye instead: both reference columns (`RN`, `TS`) that are declared
  in the `CREATE OR REPLACE TEMPORARY TABLE TMP_VAL_MEMBER_HOURS` statement immediately
  above them in the same proc, and the `WHERE` clause syntax is unremarkable.
- **`DELETE FROM FAST_SCAN_RT_CONSTRAINTS ...`** (RT-2) and the two true `INSERT`
  statements against `FAST_SCAN_RESULTS`/`FAST_SCAN_RT_CONSTRAINTS` (V2-4-TRUE,
  RT-3-TRUE): `AI_READ_ONLY` has no `INSERT`/`DELETE` grant on `FLOW_ANALYSIS` schema
  tables at all, so Snowflake's access-control check fires before it would confirm or
  deny the target table's existence or the target column's presence -- these statements
  return a privilege error regardless of the underlying object/column state. This means
  the specific "RT_INTERVAL column missing" failure mode named in the task brief could
  not be observed directly via EXPLAIN; column alignment was instead verified by eye
  (Task 2, Appendix A).
- **`PARERCOTVIEW`, `ERCOT_RESOURCE_ADEQUACY_REPORT_VIEW`**: confirmed not readable by
  `AI_READ_ONLY` (consistent with `SESSION_HANDOFF.md`). All statements referencing them
  were re-run with a same-column-name `VALUES`-shaped stub (`(SELECT NULL::DATE AS
  DATE, NULL::NUMBER AS HE, NULL::NUMBER AS PARSTATIONID, NULL::NUMBER AS FROMTAP WHERE
  FALSE)` for `PARERCOTVIEW`; `(SELECT NULL::VARCHAR AS UNIT_CODE, NULL::VARCHAR AS
  FUEL, NULL::DATE AS report_date WHERE FALSE)` for the resource-adequacy view) to
  confirm the rest of the query compiles.
- **`CREATE TABLE FAST_SCAN_RT_CONSTRAINTS`, the `ALTER TABLE ... ADD COLUMN`, and the
  three `CREATE OR REPLACE PROCEDURE` statements**: all DDL, not executable or
  `EXPLAIN`able under `AI_READ_ONLY`. Reviewed by eye only (Task 2).
