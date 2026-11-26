# Task 09 — station-level injection benchmark: LoadEstimation vs ercotStationLoad

Requested by sdalvi 2026-08-26. Two questions, in order:

1. Can `AW.DBO.ERCOTLOADESTIMATION_TERM_BAL` (+ `_STATION_BAL`) replace
   `ercotStationLoad` as the source for **net injection by station/bus**?
2. Benchmark station-level injection between the two sources and **flag every
   station-hour where the difference exceeds 10% relative to ercotStationLoad**.

Question 1 is answered by `docs/load_estimation_schema.md` (schema sweep).
This task is question 2. Do not start it until the schema doc exists and its
"generation leg: present / absent" verdict is recorded — the verdict decides
what quantity is even comparable (see §2).

## 1. Sources and where they live

| Source | Platform | Grain | Signed? |
|---|---|---|---|
| `AW.dbo.ercotStationLoad` | Snowflake `AW` (identical copy of SQL Server; Snowflake preferred for scans) | `NmmsStationCode` × `Date` × `Hour` (0–23, **hour-beginning**) | `GenMW`, `WithdrawMW` — WithdrawMW goes negative for generator station service, **never `abs()`** |
| `AW.DBO.ERCOTLOADESTIMATION_TERM_BAL` | Snowflake `AW.DBO` — **NOT `AWDev`**, which is empty on Snowflake | `run_id` × `se_timestamp` × `station` × `kv` | `pun_total_est_load_mw` — verify sign convention against the schema doc |
| `AW.DBO.ERCOTLOADESTIMATION_STATION_BAL` | Snowflake `AW.DBO` | `run_id` × `se_timestamp` × `station` | carries `pun_score`, `unresolved_xfmr_count` |
| `AW.DBO.ERCOTLOADESTIMATION_BAD_INTERVALS` | Snowflake `AW.DBO`, 618 rows | failed SE intervals | use this instead of hand-rolling the failed-interval filter |

`run_id = '1'` throughout unless the schema doc says a newer run exists.

## 2. What quantity to compare — RESOLVED by the schema sweep

**The generation leg EXISTS.** Every prior doc in this repo cited only
`pun_total_est_load_mw` because nobody had run `DESCRIBE TABLE`. The real
columns (`docs/load_estimation_schema.md` §0, §2):

| Quantity | `term_bal` (terminal grain) | `station_bal` (station grain) |
|---|---|---|
| Load / withdrawal | `TOTAL_EST_LOAD_MW` | `RAW_STATION_EST_LOAD_MW` |
| Generation | `TOTAL_EST_GENERATION_MW` | `RAW_STATION_EST_GENERATION_MW` |
| Signed net | `TOTAL_NET_LOAD_MW` | `RAW_STATION_NET_LOAD_MW` |

Verified: `NET = LOAD − GENERATION`. Load and generation never go negative;
only `NET` carries sign. Positive NET = net withdrawal (consumer), negative =
net injection (producer). This is the SAME orientation as
`ercotStationLoad.WithdrawMW`, so the comparison is:

```
ercotStationLoad :  net_withdrawal = WithdrawMW - GenMW
term_bal         :  net_withdrawal = SUM(TOTAL_NET_LOAD_MW) over kv
station_bal      :  net_withdrawal = RAW_STATION_NET_LOAD_MW
```

Compare all three legs separately — load vs load, generation vs generation,
net vs net. A disagreement that shows up only in the net is a different bug
from one that shows up in both legs, and sdalvi needs to be able to tell them
apart. State the sign orientation explicitly in the output doc; a sign flip
will masquerade as a 200% error.

### 2.1 MANDATORY: never use the plain `STATION_*` columns

`STATION_EST_LOAD_MW`, `STATION_EST_GENERATION_MW`, and `STATION_NET_LOAD_MW`
(the non-`RAW_` variants) are **zeroed by the pipeline itself** for PUN-scored
station-hours. This is baked into the stored value, not a filter you apply.
Proved at `2026-02-20 00:57:00`: `SNDSW` reads `STATION_EST_LOAD_MW = 0.0`
while `term_bal` summed over kv gives `685.46 MW` and
`RAW_STATION_EST_LOAD_MW` gives `685.46 MW` exactly.

Use `RAW_STATION_*` (station grain) or `SUM(TOTAL_*)` over kv (terminal grain).
Using the plain columns produces a benchmark where every PUN station reads as
a 100% disagreement — a silently-broken result that looks plausible.

### 2.2 Also mandatory

- **No `run_id` on the Snowflake copy.** Do not add `WHERE run_id = '1'` to a
  Snowflake query — the column does not exist. It exists only on SQL Server.
  The two copies are near-duplicates, not byte-identical (6,676 vs 6,729 rows
  at a matched instant). Use **Snowflake `AW.DBO`** and say so.
- **`COALESCE(pun_score, 0)` is unsafe.** 2.2% of `station_bal` rows have NULL
  `pun_score`, exactly coinciding with `COVERAGE_FLAG IS NULL` — unresolved
  topology. sdalvi's reference queries coalesce these to 0 and thereby call
  them clean. Carry NULL through as its own state and report the count.

## 3. Alignment rules (these are the traps — get them right)

1. **kv fan-out.** `term_bal` grain includes `kv`. `SUM(pun_total_est_load_mw)`
   over kv per `(station, se_timestamp)` **before** joining `station_bal`.
   Joining first fans out rows and understates MW. See `docs/pun_audit_top25.md:6-7`.
2. **Do NOT apply the `pun_score = 0` "clean" filter.** sdalvi's reference
   query in `docs/large_load_research.md` uses it for a *clean-load* product;
   it is wrong here. PUN stations are exactly the ones where net ≠ gross and
   where behind-the-meter generation lives — filtering them zeroes out the
   most interesting rows. Use the raw `pun_total_est_load_mw` and carry
   `pun_score` / `unresolved_xfmr_count` as **reported columns**, so a flagged
   disagreement can be read against whether the station is PUN-contaminated or
   has unresolved transformers. Same reasoning as `src/organic_load.py:127-131`.
3. **Time alignment — VERIFY EMPIRICALLY, DO NOT ASSERT.** This is the gap
   most likely to make the whole output untrustworthy. `term_bal` is hourly
   with exactly ONE snapshot per hour, stamped at **`:57` past the hour**
   (schema doc §3.4), so there is no intra-hour averaging to do — the only
   question is which hour label that snapshot belongs to.
   `ercotStationLoad.Hour` is 0–23 hour-beginning, shifted +1 to an
   hour-ending label (`pull_station_load.HOUR_SHIFT`). The natural reading is
   `se_timestamp 00:57` → `ercotStationLoad Hour=0` → hour-ending `01:00`, but
   **do not assume it.** Pick a high-ramp station-day (a morning or evening
   ramp at a large, well-behaved non-PUN station), test BOTH candidate offsets
   (0 and ±1 hour), and adopt the one that minimizes median absolute
   disagreement. Report the test and the winning offset in the findings doc.
   A one-hour misalignment manufactures large percentage errors on every ramp
   hour and is indistinguishable from a real data-quality finding.
4. **Keep it signed. No flooring.** `organic_load.py` floors station-hours at 0
   for its own product. Do not reuse that path. A benchmark on floored data
   hides exactly the sign disagreements worth finding.
5. **Bad intervals.** Exclude via `ERCOTLOADESTIMATION_BAD_INTERVALS`. If its
   schema does not support a direct join, fall back to the documented rule
   (`ABS(SUM(pun_total_est_load_mw)) <= 50` system-wide per timestamp → drop)
   and say which you used.
6. **Station namespace.** Direct text match `NmmsStationCode == station` only,
   per the schema doc's namespace finding. **Report the match rate as a
   headline number** — an unmatched station is a coverage finding, not a bug to
   chase with fuzzy matching. No fuzzy matching.

## 4. The 10% flag — define it so it is not garbage

A naive `|a-b| / |b| > 0.10` explodes on near-zero denominators, and station
hours near zero are common (station service, idle industrial). Required:

- Relative difference against the **ercotStationLoad** value as denominator
  (that is the reference sdalvi named) — **for the load and generation legs
  only**, where the quantity is documented non-negative.
- **The net leg needs a symmetric denominator.** Net (`WithdrawMW - GenMW`)
  crosses *through* zero at any station with both load and generation, so a
  plain ratio is uninterpretable exactly at the stations sdalvi cares most
  about. For the net leg use `|a - b| / max(|a|, |b|)` (symmetric percent
  difference) and say so in the output. Do not silently apply the same formula
  to all three legs.
- **AND an absolute MW floor** so trivial magnitudes cannot trip the flag.
  Start at `|diff| >= 5 MW`; report how many rows the floor suppresses so the
  choice is auditable and tunable.
- Report **both** legs separately: rows failing the relative test, and rows
  failing relative-AND-absolute. sdalvi decides the final threshold.
- Flag **sign disagreements** (one source positive, the other negative) as
  their own category regardless of magnitude. These are the highest-value
  findings and a pure percentage test buries them.
- Rows present in one source but missing in the other are a **third category**
  (`missing_in_term_bal` / `missing_in_station_load`), never silently dropped
  and never counted as 0 MW.

## 5. Scope

Bounded first pass, then widen only if it is cheap:

- Window: **2026-01-01 → 2026-03-04**. sdalvi's reference window ends 03-23,
  but the family's data **stops at 2026-03-04** (Snowflake; SQL Server stops
  2026-02-26). Querying past that returns nothing and would read as
  "missing_in_term_bal" for every station. Note the truncation in the output.
- **Freshness: a known gap, but NOT a blocker (sdalvi 2026-08-26).** The
  family stopped updating in early March 2026 — a one-time backfill campaign
  (tables created 2026-04-28/29), not a live pipeline. sdalvi has confirmed he
  can ask the SWE team to refresh it, so **do not let staleness drive the
  recommendation**. Judge the family on accuracy and coverage as if it were
  current; treat the refresh as an operational dependency to name, not a
  reason to reject. Do report the exact last-data timestamp per platform so
  sdalvi can tell the SWE team precisely what to backfill from.
- Stations: start with the 85 already cached under `data/raw/station_load/`
  (the NCL set) because they need no new pull, but **do not stop there** —
  the NCL set is biased toward exactly the PUN-contaminated stations. Add a
  random sample of ≥100 non-NCL stations so the error rate is not read off a
  worst-case subset. Report NCL and non-NCL error rates separately.
- **Force-include `JCK` and `LON_HILL`.** The schema sweep found both reading
  **zero generation all day** in `term_bal` despite being ruled generator
  stations from `ercotStationLoad` evidence. Also force-include `HCKSW` and
  `WTRML`, which run the other way — `pun_audit_top25.md:50` documents
  `ercotStationLoad` as blind to them while the state estimator sees real MW.
  **The highest-value question this benchmark can answer is whether these are
  isolated cases or a systematic pattern**: is this family blind to a class of
  generators the way `ercotStationLoad` is blind to a class of large loads? If
  so, neither source dominates and the answer to sdalvi is "use both, they
  have complementary blind spots." Address this explicitly in the findings —
  it matters more than the aggregate agreement rate.
- `term_bal` is 325M rows / 21 GB. Every query must be bounded by both the
  date window and an explicit station list. Never `SELECT *`.

## 6. Deliverable

- `output/task09_injection_benchmark.csv` — one row per compared station-hour
  that is flagged, with: `station`, `ts_local`, both source values, `diff_mw`,
  `pct_diff`, `flag_category` (relative / relative+absolute / sign / missing),
  `pun_score`, `unresolved_xfmr_count`, `kv_count`.
- `output/task09_station_summary.csv` — per station: hours compared, mean and
  median `pct_diff`, flagged-hour count and rate, worst hour, NCL flag.
- `docs/task09_benchmark_findings.md` — headline agreement rate, match rate,
  NCL vs non-NCL split, the sign-convention statement from §2, the worst
  offenders with a plausible cause for each, and an explicit recommendation on
  question 1: **can this family replace `ercotStationLoad` for net injection —
  yes / partially (which leg) / no**, with the bus-level answer called out
  separately (`BRANCH_MAPPING` is 0 rows, so bus-level is currently blocked
  unless the schema sweep found another bridge).

## 7. Gate

Per repo `CLAUDE.md`: this deliverable goes to an **Opus reviewer agent**
before it is shown to sdalvi. The reviewer gets this spec, the schema doc, and
the three output files, and is asked whole-output sanity questions — is the
comparison apples-to-apples, is the sign convention right, would a senior
analyst trust the flagged list, and is the "can it replace" verdict actually
supported by the numbers.
