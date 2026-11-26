# JCK / LON_HILL generation investigation (2026-08-26)

Read-only Snowflake investigation (`AW.DBO`, warehouse `AI_READ_ONLY`, via
`pfa.sf.query`). No pipeline built, no existing source file modified. Three
rounds of queries, each responding to a mid-task reframe from the
coordinator; all three rounds' exact SQL is in the Appendix. Scratch scripts
and parquet snapshots: `/tmp/claude-1000/.../scratchpad/investigate_v2.py`,
`investigate_v3.py` (not checked in, per instructions).

## Headline answers

- **JCK: RESOLVED, not investigated further here.** sdalvi's ruling stands —
  Jones Creek, a genuine private-use network (PUN), family's estimate is
  correct. Use as a known-good reference case (one paragraph below).
- **LON_HILL: it is a real, grid-facing generator, not a JCK-style pure
  PUN.** Three independent lines of evidence converge (persistence,
  independent cross-source signal, same-day shape correlation) — see below.
  The original "reads zero generation" framing was measuring the wrong
  column (`TOTAL_EST_GENERATION_MW` was in fact checked correctly and
  legitimately read ~0 on 2026-02-20 specifically — LON_HILL's generator
  simply wasn't dispatched that week; February is not summer).
- **Station-code variant sweep: negative result for both stations, closes
  that hypothesis.** No sibling code carries hidden generation for either
  station under any tested spelling.
- **A correction that reaches beyond these two stations:** the task's own
  premise — that JCK/LON_HILL were "ruled generator stations based on
  `ercotStationLoad` evidence" — rests on a column that is entirely absent.
  See below; this is the most consequential finding in this report.

---

## 1. `ercotStationLoad.GenMW` is NULL for both stations, the full 74-month history — not zero, unmeasured

```sql
SELECT NMMSSTATIONCODE AS STATION, DATE_TRUNC('month', DATE) AS MONTH,
       SUM(GENMW) AS SUM_GEN, AVG(GENMW) AS AVG_GEN, MAX(GENMW) AS MAX_GEN, COUNT_IF(GENMW<>0) AS N_NZ_GEN,
       AVG(WITHDRAWMW) AS AVG_WITHDRAW, MIN(WITHDRAWMW) AS MIN_WITHDRAW, MAX(WITHDRAWMW) AS MAX_WITHDRAW,
       COUNT(*) AS N_ROWS
FROM AW.dbo.ercotStationLoad
WHERE NMMSSTATIONCODE IN ('JCK','LON_HILL')
  AND DATE >= '2020-01-01' AND DATE < '2026-03-05'
GROUP BY STATION, MONTH
ORDER BY STATION, MONTH
```

Every one of the 150 station-months returned `SUM_GEN = NaN` (SQL `NULL`,
not `0` — a `SUM` over an all-zero column returns `0`, a `SUM` over an
all-`NULL` column returns `NULL`) and `N_NZ_GEN = 0`. **`GenMW` has never
been populated for JCK or LON_HILL, in any month from 2020-01 through
2026-03.** `WithdrawMW`, by contrast, is fully populated and used below.

This directly contradicts the premise in the task prompt that these
stations were "ruled generator stations based on `ercotStationLoad`
evidence" — there was no `GenMW` signal available to rule from. It is
consistent with `docs/pun_audit_top25.md`'s own note that **GBY is "the
only control station with a populated `GenMW` column"** among the
generator-like stations reviewed in that audit. Any reasoning anywhere in
this repo that treats a station's `ercotStationLoad.GenMW` reading as
evidence about its generation should be re-examined — for most stations
that column is not "small," it is absent. The generator evidence for
LON_HILL assembled below comes entirely from (a) the family's own
`TOTAL_EST_GENERATION_MW` and (b) `WithdrawMW` going negative — never from
`GenMW`.

---

## 2. LON_HILL is a real, seasonally-dispatched grid-facing generator

### 2.1 Persistence: generation every month, strongly seasonal

```sql
SELECT STATION, DATE_TRUNC('month', SE_TIMESTAMP) AS MONTH,
       COUNT(*) AS N_ROWS, COUNT(DISTINCT KV) AS N_KV,
       SUM(TOTAL_EST_GENERATION_MW) AS SUM_TOT_GEN, MAX(TOTAL_EST_GENERATION_MW) AS MAX_TOT_GEN,
       COUNT_IF(TOTAL_EST_GENERATION_MW <> 0) AS N_NZ_TOT_GEN,
       AVG(TOTAL_EST_LOAD_MW) AS AVG_TOT_LOAD, AVG(TOTAL_NET_LOAD_MW) AS AVG_TOT_NET,
       MIN(TOTAL_NET_LOAD_MW) AS MIN_TOT_NET, MAX(TOTAL_NET_LOAD_MW) AS MAX_TOT_NET,
       AVG(PUN_TOTAL_EST_LOAD_MW) AS AVG_PUN_LOAD, AVG(PUN_TOTAL_EST_GENERATION_MW) AS AVG_PUN_GEN,
       AVG(PUN_TOTAL_NET_LOAD_MW) AS AVG_PUN_NET,
       MAX(PUN_TOTAL_EST_GENERATION_MW) AS MAX_PUN_GEN, COUNT_IF(PUN_TOTAL_EST_GENERATION_MW <> 0) AS N_NZ_PUN_GEN
FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE STATION IN ('JCK','LON_HILL') AND SE_TIMESTAMP >= '2020-01-01' AND SE_TIMESTAMP < '2026-03-05'
GROUP BY STATION, MONTH ORDER BY STATION, MONTH
```

`TOTAL_EST_GENERATION_MW` (the grid-facing / non-PUN column) is **nonzero
in every single one of LON_HILL's 74 months**, 2020-01 through 2026-02, with
a clear summer-peaking shape:

| Month type | Example | `SUM_TOT_GEN` (MW-hrs/mo) | `N_NZ_TOT_GEN` (of ~2200 hourly×kv rows) |
|---|---|---:|---:|
| Summer peak | 2024-08 | 84,362 | 739 |
| Summer peak | 2020-08 | 62,475 | 676 |
| Summer peak | 2020-07 | 50,567 | 655 |
| Shoulder | 2021-04 | 691 | 34 |
| Shoulder | 2022-05 | 2,755 | 97 |
| Probe day's own month | 2026-02 | 361 | 23 |

This is the classic signature of a **dispatchable (gas) plant that runs
mostly in summer peak** — consistent with sdalvi's "generator" ruling and
the mapper's "Lon C Hill gas plant" guess in `pun_unknowns_map.md`, and
recurring identically in **every year** of the 6+-year window (not a
one-time commissioning or retirement transition — see §2.4).

Contrast with **JCK**, the resolved reference: `TOTAL_EST_GENERATION_MW` is
exactly `0.0` in 65 of JCK's 74 months. The other 9 months are not
seasonal — they are isolated, ~24-observation single events (roughly a
half/full day at JCK's 2 kv levels), e.g. 2021-07 (804.2 MW max), 2022-03
(838.9), 2022-06 (918.6), 2023-06 (825.98 MW), 2026-01 (877.8 MW). JCK
therefore is not *literally* zero-generation 100% of history either, but
its pattern (rare, single-day spikes) is qualitatively different from
LON_HILL's (persistent, monthly, seasonally-modulated) — reinforcing that
these are genuinely different kinds of stations, not just different
magnitudes of the same thing.

### 2.2 Independent cross-source confirmation: `ercotStationLoad.WithdrawMW` goes negative in the same summer months, across multiple years

`WithdrawMW` is signed (negative = net injection into the grid) and is
**not** derived from the state-estimator family — it comes from ERCOT
branch-flow reconstruction, a genuinely separate measurement path. From the
same QF query as §1:

| Month | LON_HILL `AVG_WITHDRAW` (MW) |
|---|---:|
| 2020-08 | **-21.5** |
| 2021-08 | **-19.2** |
| 2023-07 | **-3.2** |
| 2023-08 | **-12.2** |
| 2024-06 | **-1.0** |
| 2024-08 | **-32.0** |
| 2025-08 | **-16.1** |
| 2025-09 | **-6.6** |

Negative `WithdrawMW` (net injection) recurs in **August of five separate
years** (2020/2021/2023/2024/2025) and nowhere in JCK's history (JCK's
`AVG_WITHDRAW` is positive every single month, 2020-2026, ranging ~0.03 MW
in 2020 to ~6-12 MW from mid-2021 on, no seasonal sign flip). Two
independently-built data products — one state-estimator-based, one
branch-flow-based — agree that LON_HILL exports power to the grid
specifically in summer. This is not circular: neither source is derived
from the other, and neither uses `GenMW` (which is NULL for both, §1).

### 2.3 Same-day shape correlation, r=0.97, on the single highest-generation day in the record

Picked the peak day objectively (highest `SUM(TOTAL_EST_GENERATION_MW)` in
Aug 2024, LON_HILL's single highest-generation month):

```sql
SELECT TO_DATE(SE_TIMESTAMP) AS DAY, SUM(TOTAL_EST_GENERATION_MW) AS DAY_SUM_GEN
FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE STATION = 'LON_HILL' AND SE_TIMESTAMP >= '2024-08-01' AND SE_TIMESTAMP < '2024-09-01'
GROUP BY DAY ORDER BY DAY_SUM_GEN DESC LIMIT 5
-- top hit: 2024-08-04, DAY_SUM_GEN=4193.78
```

Then, for 2024-08-04→06:

```sql
SELECT SE_TIMESTAMP, SUM(TOTAL_EST_LOAD_MW) LOAD_MW, SUM(TOTAL_EST_GENERATION_MW) GEN_MW, SUM(TOTAL_NET_LOAD_MW) NET_MW
FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE STATION = 'LON_HILL' AND SE_TIMESTAMP >= '2024-08-04 00:00:00' AND SE_TIMESTAMP < '2024-08-06 00:00:00'
GROUP BY SE_TIMESTAMP ORDER BY SE_TIMESTAMP
```
```sql
SELECT DATE, HOUR, GENMW AS GEN_MW, WITHDRAWMW AS WITHDRAW_MW
FROM AW.dbo.ercotStationLoad
WHERE NMMSSTATIONCODE = 'LON_HILL' AND DATE >= '2024-08-04' AND DATE < '2024-08-06'
ORDER BY DATE, HOUR
```

Both series, hour by hour, for 48 hours: family `TOTAL_NET_LOAD_MW`
(kv-summed) runs **-133 to -253 MW**; `ercotStationLoad.WithdrawMW` runs
**-32 to -87 MW**. Both are net-injection (negative) at every one of the 48
hours, both trace the same intraday shape — deepest overnight and in the
evening ramp (hour ~19-20), shallowest at midday (hour ~10-12, consistent
with solar pushing a gas unit down in ERCOT's merit order) — **Pearson
r = 0.97**.

**Join validity, checked explicitly** (flagged as a risk by the reviewing
pass before writing this up, since the two frames were combined
positionally): extracted the hour-of-day from each `SE_TIMESTAMP` and
compared to the paired `ercotStationLoad.HOUR` for all 48 rows — **48/48
match**, including the one off-cadence snapshot at `2024-08-05 07:59:00`
(three minutes later than the usual `:57`, but still hour 7, matching
`sl_HOUR=7`). The r=0.97 is not a join artifact.

**What this confirms, and what it does not.** Direction and dispatch
*pattern* (both deeply negative, same hours, same shape) are confirmed by
two independent sources. **Magnitude is not** — the family reads roughly
3x higher than `ercotStationLoad` on this day (e.g. hour 0: -192 MW vs -66
MW). Reasons for the scale gap were not determined (possible candidates,
**all INFERRED, none confirmed**: different metering/settlement boundary,
different treatment of station-service load, one source capturing a wider
plant footprint than the other) — reported as an open discrepancy, not
resolved here. **Do not read "~200 MW" as LON_HILL's confirmed output** —
only "real, summer-seasonal, grid-facing injection, order of tens to
~250 MW depending on source" is supported.

### 2.4 No retirement/commissioning transition visible — a recurring annual pattern instead

LON_HILL's **monthly average** `pun_score` (station_bal, full history)
stays in a stable **0.047-0.10** band across all 74 months, with no trend
and no month where the average drops near zero. Four months show a higher
`MAX_PUN_SCORE` of `1.0` within the month (isolated single-hour
excursions: 2022-04, 2022-06, 2025-02, 2026-01 — monthly averages only
rise to 0.0817-0.0839 in those months, i.e. one or a few hours spike while
the rest of the month sits at baseline) — unlike JCK (see §4), whose
*average* was `0.0` for nearly all of 2020-2025 and only became
persistently elevated in the final two months of available data. `TOTAL_EST_GENERATION_MW`
likewise never disappears for a sustained multi-month stretch — it recurs
every summer, 2020 through 2025 (last full summer in the window), each
time at broadly comparable scale (`MAX_TOT_GEN` 200-600+ MW most summers,
higher in Aug-2024/Jan-2026). **This reads as an operating plant dispatched
seasonally throughout the visible history, not a unit that came online or
retired partway through it.**

### 2.5 Which column carries the 441.3 MW figure, and identity/variant checks

Direct query against the exact `pun_audit_top25.md` window
(2026-02-19→26) reproduces **441.317479 MW** as the mean of
`PUN_TOTAL_EST_LOAD_MW` (kv-summed) — confirming the 441.3 MW figure lives
in the `PUN_TOTAL_*` family, structurally identical in form to JCK's 799.6
MW (see §3 for why that family should not be read as literal MW).

**Station-code variant sweep — negative, closes the hypothesis for
LON_HILL specifically:**
```sql
SELECT DISTINCT STATION FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE SE_TIMESTAMP >= '2026-02-20 00:00:00' AND SE_TIMESTAMP < '2026-02-21 00:00:00'
  AND (STATION ILIKE 'LCH%' OR STATION ILIKE '%LONC%' OR STATION ILIKE 'LONHILL%'
       OR STATION ILIKE 'LON_HILL_%' OR STATION = 'LONHILL')
-- 2 rows: MELONCRE, PILONCIL -- both false-positive substring hits
--  (contain "LONC" as ME-LON-CRE / PI-LON-CIL), not real siblings
```
Same patterns against `ercotStationLoad.NMMSSTATIONCODE`: identical 2
false-positive hits, no sibling. No station spelled `LONHILL` (no
underscore — sdalvi's own uncertainty about the spelling) exists in either
table on the probe day. A broader sweep of **85 named NUECES-county
stations** (86 distinct `NmmsStationCode` values including one row with a
null code, counted directly from the cached parquet) in the cached
`ercotDataDictionary` snapshot (`fileDateMonth 2026-07-01`) turned up no
obviously-better-fitting generator identity for
LON_HILL itself, though it does show the area hosts other
generation-suggestive codes (`CCEC` → bus name `CCEC_GT1`; `OXY_CC` → bus
name `OXY_OXY_CCG1`, i.e. "gas turbine" / "combined-cycle gas" naming) —
consistent with Corpus Christi being an industrial/generation-heavy
corridor, supporting the general plausibility of a real plant in this
area without confirming LON_HILL's specific identity beyond what
`pun_unknowns_map.md` already had (NUECES county, "Lon C Hill" guess,
**GUESS**, not verified further here).

**Bottom line for LON_HILL:** real generator, not resolved by the
JCK-style "PUN with tiny net" explanation. sdalvi's original ruling stands
and is now backed by two independent, non-`GenMW` data sources.

---

## 3. Column-family semantics (established empirically; the pipeline's source was not available)

This section covers what the earlier `docs/load_estimation_schema.md`
investigation did not connect: `EXT_*`, `TOTAL_*`, `PUN_EXT_*`, and
`PUN_TOTAL_*` are not "the same thing at different scopes" — they measure
structurally different things. Dumped all of them together, kv-summed,
hourly, for JCK and LON_HILL over the pun_audit week (2026-02-19→26):

```sql
SELECT STATION, SE_TIMESTAMP,
       SUM(EXT_EST_LOAD_MW) AS EXT_LOAD, SUM(EXT_EST_GENERATION_MW) AS EXT_GEN, SUM(EXT_NET_LOAD_MW) AS EXT_NET,
       SUM(TOTAL_EST_LOAD_MW) AS TOT_LOAD, SUM(TOTAL_EST_GENERATION_MW) AS TOT_GEN, SUM(TOTAL_NET_LOAD_MW) AS TOT_NET,
       SUM(PUN_EXT_EST_LOAD_MW) AS PUNEXT_LOAD, SUM(PUN_EXT_EST_GENERATION_MW) AS PUNEXT_GEN, SUM(PUN_EXT_NET_LOAD_MW) AS PUNEXT_NET,
       SUM(PUN_TOTAL_EST_LOAD_MW) AS PUNTOT_LOAD, SUM(PUN_TOTAL_EST_GENERATION_MW) AS PUNTOT_GEN, SUM(PUN_TOTAL_NET_LOAD_MW) AS PUNTOT_NET,
       SUM(EXT_IMPORT_MW) AS EXT_IMPORT, SUM(EXT_EXPORT_MW) AS EXT_EXPORT,
       SUM(INT_IMPORT_MW) AS INT_IMPORT, SUM(INT_EXPORT_MW) AS INT_EXPORT,
       SUM(TOTAL_IMPORT_MW) AS TOTAL_IMPORT, SUM(TOTAL_EXPORT_MW) AS TOTAL_EXPORT,
       COUNT(DISTINCT KV) AS N_KV
FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE STATION IN ('JCK','LON_HILL') AND SE_TIMESTAMP >= '2026-02-19 00:00:00' AND SE_TIMESTAMP < '2026-02-26 00:00:00'
GROUP BY STATION, SE_TIMESTAMP ORDER BY STATION, SE_TIMESTAMP
```

### 3.1 `PUN_TOTAL_EST_LOAD_MW` and `PUN_TOTAL_EST_GENERATION_MW` are an exact identity — the net is tautologically zero

Computed `PUN_TOTAL_LOAD − PUN_TOTAL_GEN` per hour:

| Station | mean | min | max | std |
|---|---:|---:|---:|---:|
| JCK | 0.0 | 0.0 | 0.0 | **0.0** |
| LON_HILL | 5.95e-9 | -1e-6 | 1e-6 | **4.58e-7** |

This holds to float precision, not "approximately." **Consequence:
`PUN_TOTAL_NET_LOAD_MW` is always ≈0 by construction — it is not a
physical measurement that happens to be small, it cannot ever be anything
else.** This was checked at two sampled windows only (JCK+LON_HILL,
Feb-2026 week; LON_HILL again, Aug-2024 2-day window in §2.3's `QJ`) — not
the full history — but held without exception in every window tested,
including a window where LON_HILL was actively, substantially generating
(§2.3), so it is not an artifact of a quiet period.

**Practical rule for any future use of this family (binding
recommendation):**
- **Never use `PUN_TOTAL_NET_LOAD_MW` as evidence that a PUN's net
  exchange with the grid is small** — it says nothing; it is zero
  regardless of the station's true net.
- **Never read `PUN_TOTAL_EST_LOAD_MW` / `PUN_TOTAL_EST_GENERATION_MW` as
  literal load or generation MW.** They are a large, mutually-canceling
  bookkeeping construct. The 799.6 MW (JCK) and 441.3 MW (LON_HILL)
  headline figures from `pun_audit_top25.md` are both this construct, not
  gross physical load or gross physical generation.
- **Use `TOTAL_NET_LOAD_MW` (or `EXT_NET_LOAD_MW`, empirically equal or
  very close — see §3.2) as the net-injection quantity.** This is the
  column that reconciled, in sign and shape, against the independent
  `ercotStationLoad.WithdrawMW` series in §2.2-2.3.

### 3.2 What the mirrored PUN quantity appears to represent (INFERRED from the kv breakdown, not confirmed from source)

```sql
SELECT STATION, KV, AVG(TOTAL_EST_GENERATION_MW) AVG_TOT_GEN, AVG(TOTAL_EST_LOAD_MW) AVG_TOT_LOAD,
       AVG(PUN_TOTAL_EST_LOAD_MW) AVG_PUN_LOAD, AVG(PUN_TOTAL_EST_GENERATION_MW) AVG_PUN_GEN
FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE STATION IN ('JCK','LON_HILL') AND SE_TIMESTAMP >= '2026-02-20 00:00:00' AND SE_TIMESTAMP < '2026-02-21 00:00:00'
GROUP BY STATION, KV ORDER BY STATION, KV
```

| Station | kV | `AVG_PUN_LOAD` | `AVG_PUN_GEN` |
|---|---:|---:|---:|
| JCK | 138 | 839.13 | 0 |
| JCK | 345 | 0 | 839.13 |
| LON_HILL | 69 | 86.87 | 0 |
| LON_HILL | 138 | 309.72 | 0 |
| LON_HILL | 345 | 0 | 396.59 |

For JCK, the PUN "load" books entirely at the 138 kV terminal and PUN
"generation" books entirely at the 345 kV terminal, in the identical
amount. For LON_HILL, PUN "load" splits across 69+138 kV (86.87+309.72 =
396.59) and PUN "generation" books at 345 kV in that same summed amount.
**Reading:** this looks like an internal, cross-voltage-level transfer
inside the station (high-side ↔ low-side through a transformer) being
booked as "generation" on the high side and "load" on the low side when
the pipeline cannot resolve it any more granularly. On the Aug-2024
peak-generation window (§2.3), this mirrored pair coexists at the *same*
kV level as LON_HILL's real generation (138 kV: `TOTAL_EST_GENERATION_MW`
≈193.7 MW alongside `PUN_TOTAL_EST_GENERATION_MW` ≈224.1 MW at the same
row) — correlated but not identical, so the mirror construct and the real
grid-facing reading are not cleanly separable signals; they overlap at the
same terminal. **This mechanism explanation is INFERRED from the pattern
in the data; it was not confirmed against pipeline source and should not
be treated as certain.**

Separately, `station_bal.PUN_COMPONENT_*` groups stations into
multi-station connected components and is a **different** mechanism from
the above (station grain, not term/kv grain):

```sql
SELECT STATION, PUN_COMPONENT_ID, PUN_COMPONENT_STATIONS, PUN_COMPONENT_NET_LOAD_MW, PUN_COMPONENT_REPRESENTATIVE
FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
WHERE STATION IN ('JCK','LON_HILL') AND SE_TIMESTAMP = '2026-02-20 00:57:00'
```
JCK: component 31 = `BST,DOC,FRANKC,JCK,WTR`, representative `BST`,
component net ≈38 MW (broadcast identically to all 5 members' rows).
LON_HILL: component 72 = `EQUISTAR,LON_HILL,MCKENZIE,OXY_CC`, representative
`EQUISTAR`, component net ≈0 MW. Neither of these component-level numbers
is the 799.6/441.3 MW figure — a third distinct "PUN" quantity, small,
representing the whole tied-together group's net exchange with the grid.

### 3.3 The schema doc's `TOTAL = EXT + INT` inference is empirically contradicted

`docs/load_estimation_schema.md` §2 infers "`TOTAL_* = EXT_* + INT_*`"
(explicitly marked INFERRED there, not verified). Kv-summed, `INT_IMPORT_MW`
and `INT_EXPORT_MW` are exactly `0.0` for both JCK and LON_HILL every
hour sampled (expected — internal cross-kv transfers cancel when summed
over a station's kv levels). If the inferred formula held for
`TOTAL_EST_LOAD_MW` specifically, `TOTAL_EST_LOAD_MW` should then equal
`EXT_EST_LOAD_MW`. It does not: JCK's weekly mean `TOTAL_EST_LOAD_MW` is
28.5 MW against `EXT_EST_LOAD_MW` of 818.9 MW. **The inference does not
hold and should be corrected** — flagging here per scope (this task did
not modify `load_estimation_schema.md`).

What was observed instead (exact, from the weekly means, JCK):
`EXT_EST_LOAD_MW = TOTAL_EST_LOAD_MW + EXT_EST_GENERATION_MW`
(28.513172 + 790.433453 = 818.946625, matches to the reported precision),
and separately `TOTAL_IMPORT_MW − EXT_IMPORT_MW = TOTAL_EXPORT_MW −
EXT_EXPORT_MW = PUN_TOTAL_EST_LOAD_MW = PUN_TOTAL_EST_GENERATION_MW`
(2734.129 − 1934.503 = 799.626 = 2705.616 − 1905.990, matching
`PUN_TOTAL_*`'s 799.626 mean exactly). These are reported as observed
arithmetic facts only — a full mechanistic explanation of the pipeline's
`EXT`/`TOTAL`/`PUN` computation was not attempted (would need source
access, out of scope for a read-only data investigation) and should not be
inferred beyond what's stated here.

---

## 4. JCK — resolved reference case (one paragraph, per sdalvi's ruling)

JCK is Jones Creek, Brazoria County (confirmed via `ercotDataDictionary`:
bus names `JONCRK__B345`/`JONCRK__B138`/etc., all Brazoria — the county
gloss uncertainty flagged in `pun_unknowns_map.md` is resolved: it is a
real place name, not "Jack County"). It is a genuine PUN and the family's
estimate is correct, per sdalvi. `TOTAL_NET_LOAD_MW` ≈ `EXT_NET_LOAD_MW`
≈ 25-30 MW average (probe week), small and positive (net load), consistent
in sign and order of magnitude with `ercotStationLoad.WithdrawMW`'s ~8.6
MW average over the same week (no `GenMW`-based comparison possible, §1).
The 799.6 MW headline figure lives in the tautologically-mirrored
`PUN_TOTAL_*` family (§3) and should not be read as JCK's gross internal
load or generation. `pun_score`'s **monthly average** was `0.0` for nearly all of 2020-2025
(with the same isolated single-hour 1.0 excursions as LON_HILL, in
2022-04, 2022-06, 2025-02, and 2026-01 — the two stations are symmetric
here, not JCK being "cleaner") and only became persistently elevated in
the final two months of available data (2026-02/03) — the large
`PUN_TOTAL_*` figure that drove the original
"799.6 MW, 168/168 hours flagged" audit line is a **recent** feature of
the record, not a 6-year-long pattern. None of this changes sdalvi's
ruling; it only clarifies which numbers are safe to quote.

---

## Appendix — variant sweep results (both stations, full text)

```sql
SELECT DISTINCT STATION FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE SE_TIMESTAMP >= '2026-02-20 00:00:00' AND SE_TIMESTAMP < '2026-02-21 00:00:00'
  AND (STATION ILIKE '%LON%' OR STATION ILIKE '%HILL%' OR STATION ILIKE '%JCK%' OR STATION ILIKE '%JACK%' OR STATION ILIKE '%SPRUCE%')
-- 57 rows: BHILL, BLCKJACK, CALONPTR, CEDRHILL, CHILL, CHILLICO, CLAYHILL, FRPHILLT, HILLCITY,
--   HILLCTRY, HILLJE, HILLTO, HILL_CO, HI_LONE, HI_LONEB, JACKCNTY, JACKFU, JACKR, JACKRABT,
--   JACKSNTP, JACKSONS, JCK, JCKCNTY2, JCKSW, KLONDIKE, LON, LONESTAR, LONESTR, LONETREE,
--   LONETRS, LONEWOLF, LONE_OAK, LONE_STR, LONG, LONGLO, LONGNECK, LONGWRTH, LONSW, LON_HILL,
--   MALONE, MALONEY, MELONCRE, OAKHILL, PHILLIPS, PHILLPS2, PHILLWND, PILONCIL, PRCHHILL,
--   PUMPJACK, ROCKHILL, ROSEHILL, RUSTHILL, SHELLLON, SHELONTP, S_HILLS, YELWJCKT, ZIONHILL
-- (identical result set against AW.dbo.ercotStationLoad.NMMSSTATIONCODE, DATE='2026-02-20')
```

None of these are a JCK or LON_HILL sibling under any of sdalvi's suspected
variant spellings (`LONHILL`, `LON_HILL_G`, `JCKG`, `JCK_1` — none exist;
neither does `LCH%` or `LONC%`, checked separately in §2.5). The
station-code-variant hypothesis is closed for both stations.

## Files

- This report: `/workspaces/scratch-workspace/load-forecast/docs/jck_lonhill_generation.md`
- Scratch scripts (not checked in): `investigate_v2.py`, `investigate_v3.py`
  under `/tmp/claude-1000/-workspaces-scratch-workspace/42f42055-457d-4044-a2ff-deac470ca995/scratchpad/`
- Parquet snapshots of every query result saved alongside the scripts above
  for reproducibility, also not checked in.
