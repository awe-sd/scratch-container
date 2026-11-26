# Ask for the SWE team — ERCOT load-estimation tables (2026-08-26)

Prepared for sdalvi after he offered to request a refresh. Everything below is
verified against the live databases on 2026-08-26; the supporting evidence is
in `load_estimation_schema.md`, `genmw_coverage.md`, and `kv_aggregation_test.md`.

Ordered by how much it blocks us. Items 1 and 2 are the asks; 3–6 are
questions whose answers change what we build.

---

## 1. Refresh the `ercotLoadEstimation_*` family — it stopped ~6 months ago

| Platform | Database / schema | Last `se_timestamp` | Gap to today |
|---|---|---|---|
| **Snowflake** | `AW.DBO` | **2026-03-04** | ~5.7 months |
| **SQL Server** | `AWDev.dbo` | **2026-02-26** | ~6.0 months |

All six Snowflake tables were created **2026-04-28/29**, which reads as a
one-time backfill campaign rather than a scheduled pipeline. For comparison,
`ercotStationLoad` runs current to **2026-06-15**, so the estimation family is
currently *more* stale than the source it would supplement.

**Ask:** backfill from each platform's last timestamp above through present,
and put it on a recurring schedule.

**The question behind the ask:** is this intended to be a live pipeline at all,
or was it a one-off study deliverable? That answer decides whether we build on
it or treat it as a fixed historical reference. Please get this answered
explicitly rather than inferred.

Affected tables (Snowflake `AW.DBO` row counts as of 2026-08-26):

| Table | Rows |
|---|---|
| `ERCOTLOADESTIMATION_AUDIT` | 496.2M |
| `ERCOTLOADESTIMATION_TERM_BAL` | 325.5M |
| `ERCOTLOADESTIMATION_STATION_BAL` | 283.4M |
| `ERCOTLOADESTIMATION_RUN_AUDIT` | 54,047 |
| `ERCOTLOADESTIMATION_BAD_INTERVALS` | 618 |
| `ERCOTLOADESTIMATION_BRANCH_MAPPING` | **0** ← see item 2 |

## 2. `BRANCH_MAPPING` is empty on Snowflake but populated on SQL Server

`ERCOTLOADESTIMATION_BRANCH_MAPPING` has **0 rows on Snowflake** and **7,544
rows on SQL Server** (all `AUTO_MATCHED`). That is a replication gap, not a
table that was never built.

**Ask:** sync it to Snowflake along with the refresh.

Note this does *not* by itself unblock bus-level work — see item 3.

## 3. Is there any path from this family to a bus identifier?

**This is the one that decides whether "net injection by bus" is possible at
all.** Right now it is not. There is no bus-number column anywhere in the
family, and even the populated SQL Server `BRANCH_MAPPING` only maps
branch → station/terminal, never to `SswgBusNumber`. The finest grain we can
reach is `(station, kv)`.

**Ask:** is there an existing or planned mapping from the estimation family's
`station`/`TERMINAL` to `SswgBusNumber` (or to `MRIDLOAD`, which is our only
durable cross-source key candidate)? If one exists somewhere we have not
found, we need the table name. If not, is producing one feasible?

## 4. Why is `ercotStationLoad.GenMW` NULL for so many generators?

Measured over Feb-2026, restricted to stations the estimation family reports as
material generators (`TOTAL_EST_GENERATION_MW` monthly max > 20 MW):

- **191 of 650 stations (29.4% by count, 14.1% by MW weight)** have `GenMW`
  entirely **NULL** — not zero, never populated.
- Jul-2023 control window: 99 of 490 (20.2% count, 9.9% MW weight).
- The stations are *present* in the table with populated `WithdrawMW`; only
  `GenMW` is absent. JCK and LON_HILL are confirmed instances.

**Ask:** is this a known limitation of the branch-flow derivation, a data-feed
gap, or something fixable? If `GenMW` could be populated for these stations,
`ercotStationLoad` alone would cover our net-injection need and we would not
need a hybrid.

## 5. Two smaller schema questions

- **The Snowflake copy has no `run_id` column**; SQL Server does. Intentional
  (only one run replicated) or an omission? A same-instant row count differs
  between the two copies (6,676 Snowflake vs 6,729 SQL Server `run_id='1'`),
  so they are not byte-identical — we would like to know which is canonical.
- **`ERCOTLOADESTIMATION_BAD_INTERVALS` (618 rows) exists on Snowflake only.**
  We would like it on SQL Server too. It supersedes the hand-rolled
  `HAVING ABS(SUM(pun_total_est_load_mw)) <= 50` failed-interval filter that
  our reference queries currently use.

## 6. Semantics questions only the pipeline author can settle

We reverse-engineered these from data. Confirmation would be worth more than
more of our sampling:

- **What do the `EXT_*` / `TOTAL_*` / `PUN_*` column prefixes mean?** We infer
  `TOTAL_*`/`EXT_*` are grid-facing and `PUN_*` is a behind-the-meter or
  internal-transfer construct, but this is inference. At JCK the two differ by
  ~32× in the same row, so guessing wrong is a 32× error.
- **Are `PUN_TOTAL_EST_LOAD_MW` and `PUN_TOTAL_EST_GENERATION_MW` set equal by
  construction?** They match to float precision at every station-hour we
  sampled, which would make `PUN_TOTAL_NET_LOAD_MW` structurally zero. We only
  tested two stations, and this is currently disputed internally.
- **Why are the plain `STATION_EST_*` / `STATION_NET_LOAD_MW` columns zeroed
  for PUN-scored station-hours** while `RAW_STATION_*` carries the real value?
  Deliberate masking or a defect? (SNDSW @2026-02-20 00:57: plain reads 0.0,
  `RAW_` reads 685.46 MW.)
- **What is `pun_score` actually measuring**, and is `> 0` the intended
  exclusion threshold? It is continuous on [0, 1] and only 3.8% of rows exceed
  0. Separately, **2.2% of rows have NULL `pun_score`** (exactly coinciding
  with `COVERAGE_FLAG IS NULL`) — what does that state mean? Our reference
  queries `COALESCE(pun_score, 0)`, which silently calls those rows clean.
