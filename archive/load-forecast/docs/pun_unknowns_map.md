# PUN-flagged UNKNOWN station classification

Follow-up to `docs/pun_audit_top25.md`. That audit flagged 21 stations
(top-25 by avg `pun_total_est_load_mw`, week 2026-02-19->26, kv-summed,
`run_id='1'`) as UNKNOWN. Of those 21: **JCK is already ruled** (generator
station, sdalvi 2026-08-15), **RNKSW is already ruled** (no PUN load, sdalvi
2026-08-15), and **GBY is not actually unknown** -- it is already in
`data/derived/ncl_stations.csv` as a CONFIRMED sheet large load (provenance
`sheet`, site "ECL: TerraSite-TX1", HARRIS county -> COAST, bus 40710, max_mw
1000, online 2025-07-01). **That leaves 18 genuinely open unknowns.** All 21
are still mapped and profiled below (JCK/RNKSW/GBY included so their history
can be cross-checked against the existing rulings, not re-litigated).

Sources: `ercotDataDictionary` snapshot (fileDateMonth=2026-07-01, read from
the existing `data/raw/lookups/ercot_data_dictionary_latest.parquet` cache --
not re-queried, since force-refreshing it would mean deleting/overwriting a
pre-existing file, which this task's binding rules forbid) for county;
`data/raw/crosswalk/ercot_county_weatherzone.csv` (reusing
`build_crosswalk.SPLIT_OVERRIDES` exactly) for county->zone; ONE aggregated
Snowflake query on `AW.dbo.ercotStationLoad` (station IN the 21, 2019-01-01 to
2026-12-31, grouped by station/year, plus a Jan-May conditional aggregate --
see partial-2026 correction below) for load history, cached at
`data/raw/pun_audit/station_year_load_2019_2026.parquet`; the existing
`ercotManuallyUpdatedLoad` roster cache (119 rows, same-day pull) for the
non-conforming-load check; `data/derived/ncl_stations.csv` for the
already-confirmed-large-load cross-check; four already-cached per-station
`data/raw/station_load/*.parquet` files (DOW, SNDSW, HCKSW, WTRML) for the
coverage-gap control check below.

**Sign convention (binding):** `mw_avg_*` is signed. Negative = net
injection (station is a net generator at that bus/substation), never
`abs()`-ed.

**2026 is PARTIAL -- correction applied.** `AW.dbo.ercotStationLoad` ends
**2026-06-15** (verified: `MAX(DATE)` over all 21 stations = 2026-06-15, not
just asserted). Raw calendar-year 2026 therefore has no summer months and is
not comparable to a full year. Fix: every growth read below uses the
**Jan-May average**, comparable across all 8 years including 2026, rather
than raw calendar-year 2026 vs. full prior years. The CSV carries both:
`mw_avg_2026` (labeled `mw_avg_2026_coverage` = PARTIAL) and
`mw_avg_janmay_{2023..2026}` (the seasonally-matched series).

**Materiality yardstick (for calibrating "material" below):** closing
NCENT's 3pp growth gap needs **~432 MW of average continuous load**
(~3,781 GWh/yr). The entire confirmed NCENT NCL set today is only **~114 MW**
avg. So "material" here means an NCENT unknown adding **tens-to-hundreds of
MW** of new average load since 2023 -- not just "some" growth.

## Coverage-gap control check -- why "~0 in ercotStationLoad" is NOT proof of "no real load"

Four of the 18 open unknowns (SDMSW, LCSES, STEWART, GILLCR) read as
essentially **zero** average WithdrawMW across all 8 years. The first draft
of this analysis read that as "the PUN flag is spurious here, like RNKSW."
**That conclusion does not hold up and has been retracted below** -- caught
on internal review, then confirmed with a control check using four OTHER
top-25 stations with independently known identities and MW (already cached
locally, no new query needed):

| Station | Independent MW (source) | ercotStationLoad mean WithdrawMW, Jan-May 2025 |
|---|---|---:|
| DOW | ~536 MW (roster: DOW CHEMICAL) | 289.4 MW -- right order of magnitude |
| SNDSW | ~600 MW (sheet: Riot Rockdale) | 553.2 MW -- close match |
| **HCKSW** | **real datacenter** (sheet: CyrusOne DFW7) | **-0.02 MW -- essentially ZERO** |
| **WTRML** | **real datacenter** (sheet: Databank/Skybox) | **0.01 MW -- essentially ZERO** |

HCKSW and WTRML are **confirmed, real, substantial data-center loads**, yet
`ercotStationLoad` (branch-flow derived; sdalvi's own caveat in
`large_load_research.md`: "imperfect") shows essentially nothing for either
of them -- the identical signature SDMSW/LCSES/STEWART/GILLCR show. A true
PUN load (private-use network, invisible to the state estimator by
definition -- that's the entire reason `ercotManuallyUpdatedLoad` exists as a
manual fallback) would look exactly like this too. **"~0" in this table is
therefore consistent with BOTH "genuinely no load" AND "a real load this
branch-flow table simply doesn't see" -- it cannot adjudicate between them.**

This is retracted from the earlier draft: SDMSW, LCSES, STEWART, GILLCR are
**not** shown to be over-flagged. They are **open and unresolved**. This
matters most for **SDMSW**: NCENT zone, flagged at 136.1 MW -- **~31% of the
432 MW gap** -- and squarely in the "material" range if the flag turns out
to be real. It cannot be ruled in or out from this data source alone.

(RNKSW is a different, unrelated case: it has a *substantial, non-zero*
measured load (24-44 MW) that is simply much smaller than its inflated
711.8 MW estimate -- both numbers are real and comparable there. This
zero-vs-nonzero distinction is why RNKSW's ruling does not transfer to
SDMSW/LCSES/STEWART/GILLCR.)

**Zone pattern (n=4, a pattern to check further, not yet a finding):** the
two zero-readers are both **NCENT** (HCKSW: Tarrant/Denton county; WTRML:
Dallas county -- both DFW), and the two trackers are both **outside NCENT**
(DOW: Brazoria/COAST; SNDSW: Milam/SCENT). That is exactly the geography this
task cares about, and it raises (does not prove, n=4) the possibility that
`ercotStationLoad`'s branch-flow coverage has a specific NCENT/DFW blind
spot -- which would make SDMSW, LCSES, and even RYSSW's readings all
somewhat less trustworthy than a reading from, say, a HARRIS-county station
would be. Complication worth noting, though: JCK (COAST/Brazoria -- the SAME
county as tracker DOW) also reads near-zero, so the gap is not cleanly
zone-wide; it more likely sits at the station/meter/topology level, with
NCENT simply happening to be where this batch's zero-readers concentrate.
Flagging the pattern for sdalvi rather than asserting a mechanism.

**Downstream flag for the coordinator (report only, not fixed here --
out of scope for this task):** HCKSW and WTRML are not just controls -- they
are in the **confirmed** NCL set (that's why their per-station parquet files
already existed, pulled by `pull_station_load.py` for `ncl_stations.csv`).
If `organic_load.py`'s NCL subtraction uses `ercotStationLoad` MW for
confirmed non-conforming stations, it is very likely subtracting
**approximately nothing** for these two known, real, large datacenters.
That would mean the "~114 MW confirmed NCENT NCL" figure used as this
report's materiality denominator is itself understated by the same coverage
gap -- this may be a broader pipeline issue, not just a gap in identifying
new stations. Surfacing this for the coordinator/sdalvi to decide on; no
change made to `organic_load.py` or any other existing file.

## Table (sorted by flagged-week avg MW, matching the original audit rank)

| Station | Status | Zone | County | Avg MW (flagged wk) | Jan-May avg MW: 2023 | 2024 | 2025 | 2026(partial) | Real-load read | Identity |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|
| JCK | **ruled: generator** | COAST | BRAZORIA | 799.6 | 6.7 | 8.4 | 8.6 | 8.8 | tiny, ~flat 7-9 MW (coverage-gap caveat applies -- see above; not independent confirmation of the ruling, just uninformative) | GUESS: "Jones Creek" substation (Brazoria) -- **not** Jack County |
| RNKSW | **ruled: no PUN load** | **NCENT** | DENTON | 711.8 | 20.2 | 30.4 | 42.5 | 38.4 | real, +~20 MW since 2023 (non-zero -- different case, see above) | confirmed (dictionary) |
| LON_HILL | unknown_open | SOUTH | NUECES | 441.3 | 23.8 | 27.2 | 22.0 | 29.0 | noisy, no trend | GUESS: Lon C Hill / Lon Hill sub (AEP, Nueces) |
| GBY | **CONFIRMED (sheet)** | COAST | HARRIS | 428.4 | -20.3 | -45.0 | -73.4 | -91.9 | **sign-flipped**: net injection, deepening | CONFIRMED: ECL TerraSite-TX1 datacenter |
| STEWART | unknown_open | SOUTH | HIDALGO | 428.1 | 0.006 | 0.014 | 0.019 | 0.009 | reads ~zero -- **INCONCLUSIVE**, coverage-gap caveat applies | GUESS: Stewart Rd sub (AEP, Hidalgo) |
| BOG | unknown_open | COAST | HARRIS | 257.2 | 37.7 | 59.1 | 89.3 | 94.3 | real, growing (+~150%) | unresolved (no web match) |
| GILLCR | unknown_open | **SCENT** | TRAVIS | 167.0 | 0.02 | 0.01 | 0.01 | 0.01 | reads ~zero -- **INCONCLUSIVE**, coverage-gap caveat applies | GUESS: Gilleland Creek sub (Austin Energy/LCRA, Travis) |
| AZ | unknown_open | COAST | HARRIS | 161.9 | 44.8 | 41.9 | 53.0 | 56.2 | real, growing (+~25% since 2023; 2021 dip is Uri) | unknown ("Amazon" grep = discarded false positive, per audit doc) |
| FIRON | unknown_open | FWEST | MIDLAND | 155.2 | 54.4 | 100.1 | 113.0 | 90.6 | real, growing (no data before 2022) | unknown; Permian, fits "PUN loads concentrate in WEST" prior |
| **SDMSW** | **unknown_open -- material candidate, unresolved** | **NCENT** | FALLS | 136.1 | n/a | n/a | 0.005 | 0.006 | reads ~zero -- **INCONCLUSIVE, NOT ruled out** (~31% of NCENT gap if real) | unknown |
| STILES | unknown_open | zone ambiguous | REAGAN | 118.3 | 38.4 | 39.2 | 35.7 | 23.2 | real, flat/declining since 2024 | unknown; REAGAN is a split county (FWEST/WEST) unresolved by `SPLIT_OVERRIDES` |
| OYS | unknown_open | COAST | BRAZORIA | 96.4 | 38.6 | 46.1 | 83.8 | 88.1 | real, growing (+~128% since 2023) | unknown |
| DPW | unknown_open | COAST | HARRIS | 95.4 | -191.4 | -384.4 | -402.3 | -313.9 | **always negative**, deepening | unknown generator/cogen (not a load) |
| ATKINS | unknown_open | EAST | BRAZOS | 82.4 | 46.0 | 45.3 | 30.5 | 37.7 | real, stable/no trend | unknown |
| HUD | unknown_open | COAST | BRAZORIA | 61.9 | -35.5 | -57.8 | -115.5 | -110.3 | **always negative**, deepening | unknown generator/cogen (not a load) |
| CANAL_RD | unknown_open | FWEST | MIDLAND | 57.3 | 31.6 | 31.7 | 28.6 | 29.9 | real, stable | unknown; Permian |
| CL | unknown_open | COAST | HARRIS | 41.3 | 22.4 | 20.5 | 22.3 | 18.6 | real, stable | unknown |
| BST | unknown_open | COAST | BRAZORIA | 41.0 | 0.6 | 0.6 | 0.5 | 0.7 | small, shrinking (coverage-gap caveat applies in principle, low-stakes) | unknown |
| **LCSES** | **unknown_open -- unresolved** | **NCENT** | MCLENNAN | 38.9 | -0.02 | -0.01 | 0.02 | 0.09 | reads ~zero -- **INCONCLUSIVE** (~9% of NCENT gap if real) | unknown |
| MAINLAND | unknown_open | COAST | GALVESTON | 38.5 | 4.4 | 7.0 | 8.4 | 37.8 | real, **sharp recent ramp** (2025->2026 Jan-May: 8.4->37.8) | unknown; Galveston "mainland" area |
| RYSSW | unknown_open | **NCENT** | ROCKWALL | 37.4 | 26.1 | 25.5 | 27.8 | 28.8 | real, but flat (+2.7 MW since 2023) | unknown |

Full per-year 2019-2026 (both raw calendar and Jan-May), `manually_updated_rows`
/`is_conforming` (all 0/blank -- none of the 21 appear in the 119-row
`ercotManuallyUpdatedLoad` roster), `status`, and the full-length
`classification_hint` reasoning are in `data/derived/pun_unknowns_map.csv`.

## The question: which UNKNOWNs sit in NCENT and grew materially 2023->2026?

1. Four of the 21 are NCENT by county: RNKSW (Denton, **already ruled** no
   PUN load), SDMSW (Falls), LCSES (McLennan), RYSSW (Rockwall) -- the last
   three are open unknowns.
2. **SDMSW cannot be ruled out and is the one to watch.** It reads ~zero in
   `ercotStationLoad`, but the coverage-gap control check above shows that
   signature is uninformative -- confirmed real datacenters read the same
   way. SDMSW is flagged at 136.1 MW, ~31% of the 432 MW NCENT gap. This is
   an **open, potentially material NCENT candidate**, not a dismissed one.
   It needs a different data source to resolve (direct confirmation, DAM
   LDF, or a future `ercotManuallyUpdatedLoad` update) -- `ercotStationLoad`
   cannot adjudicate it either way.
3. LCSES has the same "reads ~zero, inconclusive" profile, at a smaller
   scale (38.9 MW flagged, ~9% of the gap) -- also open, lower priority than
   SDMSW.
4. RYSSW is real (~26-29 MW, Jan-May) but only drifted +2.7 MW since 2023 --
   not material by any reading; this one IS a clean read (non-zero, stable).
5. RNKSW has a real, moderate upward move: Jan-May avg 20.2 (2023) -> 30.4
   (2024) -> 42.5 (2025) -> 38.4 (2026, partial) -- a real **+~20 MW** rise,
   NCENT, growing, clearly measured (not a coverage-gap case). ~5% of the
   432 MW gap on its own; sdalvi's ruling (that the 711.8 MW *PUN estimate*
   is wrong) is untouched by this smaller, separately-metered number.
6. **Bottom line: this batch does NOT clear RNKSW, RYSSW, or LCSES as
   material NCENT growth -- but it does NOT clear SDMSW either.** SDMSW
   (136 MW, ~31% of the gap) is the one open thread worth chasing further;
   everything else in NCENT here is either confirmed small/flat or
   genuinely indeterminate at a much smaller scale.

## Flags vs sdalvi's two rulings (reported, not argued)

- **JCK** ("generator station, Jack County"): `ercotDataDictionary` places it
  in **Brazoria County**, not Jack County -- a real place called Jones Creek
  sits there, and a CenterPoint "Jones Creek Substation" (345 kV, energized
  2020) is well documented there. Likely a name/label mismatch, not a
  substantive error. Note: JCK's tiny real withdrawal is **not** independent
  confirmation of the generator ruling (per the coverage-gap check, a tiny
  reading is uninformative either way) -- the ruling stands on sdalvi's own
  authority, not on this data point.
- **RNKSW** ("no PUN load"): real withdrawal is not zero -- see point 5
  above. Doesn't contradict the ruling (which concerns the 711.8 MW PUN
  estimate specifically) but the station carries a real, moderate, growing
  NCENT load (+~20 MW since 2023) worth separate awareness.
- **GBY** (not previously ruled, but confirmed elsewhere as the "ECL:
  TerraSite-TX1" hydrogen-power datacenter, phased 50/120/830 MW
  2025/2026/2030): real `ercotStationLoad` withdrawal **sign-flips** from
  +55/+61 MW (2019-2020) to net injection, deepening to -73 to -92 MW
  (2025-2026 Jan-May). Reported as-is, not forced to look like a load: this
  is the opposite of what a ramping consuming load should show. GBY spans 15
  distinct dictionary buses, so station-level netting may be masking a small
  new consuming bus (40710, the datacenter's) against a much larger,
  separately-metered net-generation footprint at the same station -- an open
  tension, not resolved here.

## Other notable real-load findings (non-NCENT, for completeness)

- **DPW and HUD** are net generators/cogen, not loads: withdrawal is negative
  every year 2019-2026 and deepening (DPW -191->-402 MW, HUD -35->-115 MW,
  Jan-May) -- clean, non-zero readings, no coverage-gap ambiguity.
- **AZ, BOG, OYS, MAINLAND, FIRON** all show real, materially growing load
  on a Jan-May (seasonally matched) basis -- genuine large-load candidates,
  just not in NCENT (HARRIS/COAST x3, GALVESTON/COAST, MIDLAND/FWEST).
  MAINLAND's ramp is the sharpest and most recent (8.4 -> 37.8 MW, 2025->2026
  Jan-May). Worth their own identification pass if COAST/FWEST large-load
  tracking is ever in scope.

## NEEDS_CONTEXT

None in the formal sense (no missing table/column, no unexpectedly-empty
join). But flagging one open, unresolved item for sdalvi rather than
guessing further: **SDMSW's true load status cannot be determined from
`ercotStationLoad` or the sources available here** -- it reads ~zero, but
that reading is uninformative per the coverage-gap check. Given it's ~31% of
the NCENT gap, this is the one item in this batch that may warrant a
different data source or a direct ruling.

## Binding-rule compliance notes

- No existing file modified; only this file, `data/derived/pun_unknowns_map.csv`,
  and the new cache `data/raw/pun_audit/station_year_load_2019_2026.parquet`
  were written.
- `ercotDataDictionary` and `ercotManuallyUpdatedLoad` were read from their
  existing, same-project, same-day caches rather than re-queried -- both are
  full-table pulls that already cover all 21 stations, and force-refreshing
  either would require deleting a pre-existing file (forbidden).
- Exactly ONE aggregated Snowflake query pattern was used (station-list- and
  date-bounded, `AW.dbo.ercotStationLoad`, warehouse `AI_READ_ONLY`, via the
  repo's own `pfa.sf.query` wrapper -- same one `pull_station_load.py`
  uses); it was re-run once after the Opus grading gate caught the
  partial-2026 issue, to add the Jan-May conditional aggregate to the same
  query rather than issue a second, differently-scoped one.
- No SQL Server query was newly issued (see cache-reuse point above).
- The coverage-gap control check (DOW/SNDSW/HCKSW/WTRML) used only
  already-cached per-station parquet files from this project's own prior
  work -- no new query of any kind.
- Web search (step 5, optional) covered the top-5 by MW among the
  not-yet-ruled unknowns (LON_HILL, GBY, STEWART, BOG, GILLCR); GBY was
  already resolved from the internal sheet (not a guess). LON_HILL, STEWART,
  GILLCR got corroborated name matches (marked GUESS per instructions); BOG's
  identity is still unresolved (no fuzzy-matching, per repo convention).

## Post-mapper updates (2026-08-15, main session)

sdalvi rulings: DOW = real PUN; LCSES, LON_HILL, GBY = generators; rest
unclear to sdalvi. (Earlier: JCK generator, RNKSW no PUN load.)

Coverage-gap claim VERIFIED by direct cache reads: HCKSW ~0.1 MW and WTRML
~0 MW in ercotStationLoad every year 2021–2026 vs SE 389/150 MW (Feb-2026
week); SNDSW/Riot is seen fine (143→612 MW). GBY is the only control with a
populated GenMW column (generator, per ruling). Consequence: Task 07's NCENT
subtraction missed ≈539 MW of confirmed datacenter draw — "hybrid v2"
(SE series for stationLoad-blind stations) is the proposed fix, sdalvi
ruling pending. SDMSW remains THE open NCENT unknown (~31% of gap,
inconclusive by construction here).
