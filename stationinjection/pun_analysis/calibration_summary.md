# SE-derived station net injection vs SCED generator telemetry — June 2026 calibration

## Scope
- 445 NMMS stations had ≥1 SCED-mapped generating unit AND matched SE + SCED rows in June 2026.
- Each SE hourly snapshot (stamped :52/:57/:59) was paired with the nearest 5-min SCED run (deterministic: :57→:55, :59→:00, :52→:50), always within the required ±10 min window. 720 paired hours per station.

## Mapping methodology (revised after a validation pass — read this before trusting any single station's row)
Neither `GENUNIT` nor `GENUNITSCEDNAME` carries a literal NMMS-station-code column, so the join to `ERCOTSTATIONINJECTION.NMMSSTATIONCODE` had to be derived and validated in two stages:

1. **First pass (SCED-name prefix heuristic)**: `SPLIT_PART(GENUNITSCEDNAME.NAME, '_', 1)` matched against `NMMSSTATIONCODE`. Matched 1,165/1,605 GEN-kind units (72.6%) and looked fine for large plants (STP, CPSES, LOSTPI) — but it also produced **coincidental wrong-station matches** for smaller assets whose abbreviated prefix happened to equal an unrelated real station code (e.g. `CBEC_GT11/12` prefix `CBEC` collided with an unrelated small station also coded `CBEC`; the real Colorado Bend station is `DYN`).
2. **Second pass (authoritative busname join)**: `GENUNIT.BUSNAME → AW.DBO.ERCOTDATADICTIONARY.SSWGBUSNAME → NMMSSTATIONCODE` (latest `FILEDATEMONTH`). This is a real, documented join and recovered coverage to 1,411/1,605 units (87.9%) and fixed the CBEC-style false positives — but introduced a **different, systematic failure**: for many wind/solar projects, `GENUNIT.BUSNAME` is the shared 345kV collector/POI bus, and the dictionary resolves that bus to an **upstream switching station** with ~0 net injection (pure pass-through — flow in equals flow out, so `NETINJECTIONMW ≈ 0` at that node by construction even though hundreds of MW transit it). This produced 87 stations (20% of the busname-derived set) with `mean SE ≈ 0` against `mean SCED` telemetry in the hundreds of MW (station codes ending in `SW` are a visible tell — `BAKESW`, `GRVSW`, `CBFSW`, etc.).
3. **Reconciliation**: every station was checked with `|mean SE| / |mean SCED| < ~8%` (a real generating station's net injection should track its output, not sit at zero). Flagged "phantom pass-through" stations were re-mapped to their SCED-name-prefix candidate instead (recovering e.g. `CANYONWD`, `TORR`, `BORDAS`, `BIGSAMWD`); a manual check on the two largest ratio-test flags found **Forney Energy Center** (busname resolved to switching station `FORSW`, ~0 net injection) whose true code is `FRNYPP` — after correction, FRNYPP tracks SCED almost exactly (corr 0.9995, median |Δ| 1.7 MW).
4. **The ratio test is necessary but not sufficient.** Two "recovered" prefix-fallback stations, `CHIL` and `PEARSALL`, initially looked like legitimate solar+storage hybrids (mean SE near zero, explainable by battery charge/discharge symmetry). A direct check killed that story: their mapped SCED units show a **clean solar diurnal curve** (0 MW overnight → 130–150 MW midday), but SE net injection at both station codes is **flat at −2 to −5 MW at every hour of the day**, with no midday bump whatsoever. That is not a hybrid station netting to zero — it is a coincidental prefix collision with an unrelated small station. Both are marked `MAPPING CONFIRMED WRONG` in the CSV and **excluded from all headline statistics below** (443 of 445 stations used). Because this cohort's failure signature (near-zero/flat mean, no correlation with a resource that should have obvious structure) can hide in stations without solar's convenient tell, **every `PREFIX_FALLBACK` station with correlation < 0.3 is flagged `MAPPING UNVERIFIED`** in the CSV notes rather than attributed to "wind volatility" — a month of hourly data at corr ≈ 0 or negative is at least as consistent with "these are two different physical objects" as with timing noise, and this analysis did not have budget to spot-check each one the way CHIL/PEARSALL were checked. Only 3 of 1,607 units were entirely unmappable (no usable candidate) and excluded outright.
- **Evidence for the "partial-fleet capture" failure mode**: `AW.DBO.ISOERCOTSCEDGEN` has 1,798 distinct registered `RESOURCENAME`s, but `AWDEV.DBO.GENUNITSCEDNAME` (`KIND='GEN'`) tracks only 1,605 — i.e. ERCOT/SCED knows about ~193 more generation resources (12%) than our unit table does. This directly supports (not just infers) that some stations' true generation fleet exceeds what we could map, consistent with the high-correlation-but-scaled-wrong pattern seen in `LACY_CRK`, `HRNT_SLR`, `CANYONWD`, `BORDAS`, `TORR`, `RELOJ`. Importantly, the pure-gen bias check below (median mean-Δ ≈ 0, sign split ~50/50) shows this effect is **confined to a tail of stations**, not a systematic drag on the whole population.
- **Duplicate `ISOERCOTSCEDGEN.RESOURCENAME` check**: 16 resource names have two `GENID`s (old + re-registered). Verified the older `GENID` in every case has zero telemetry rows in June — no double-counting risk in the `SUM(TELEMETEREDOUTPUT)` aggregation.
- **NEEDS_CONTEXT**: no single authoritative "unit → NMMS station code" column/table exists in `AWDEV.DBO` or `AW.DBO`; the reconciled busname+prefix+ratio-test procedure above is the best available and should be treated as a first cut, not ground truth, for any individual station not spot-checked here — especially the 143 stations (of 445) still on the `PREFIX_FALLBACK` method, and above all the low-correlation ones flagged `MAPPING UNVERIFIED`.

## Headline accuracy (443 matched stations, corrected mapping, excludes the 2 confirmed-mismapped stations)
| Metric | Value |
|---|---|
| Median of per-station median \|Δ\| | **1.78 MW** |
| 10th/25th/75th/90th/95th/99th pct | 0.39 / 0.92 / 5.20 / 25.5 / 54.7 / 128.2 MW |
| Share of stations with median \|Δ\| ≤ 2 / 5 / 20 MW | 54.9% / 74.5% / 87.6% |

## "Pure generation" stations (mean SE > 10 MW AND corr > 0.95) — 333 of 445
| Metric | Value |
|---|---|
| Median of per-station median \|Δ\| | **1.65 MW** |
| Share within 2 / 5 / 20 MW | 61.3% / 82.0% / 92.8% |
| Mean / median of station mean Δ (bias check) | +2.05 MW / **−0.11 MW** |
| Share with negative mean Δ | 56.8% (no systematic sign) |

**Size-stratified view — this is the number that matters for PUN-scale stations.** Error grows in absolute MW with station size but *shrinks* as a percentage of output:

| Size band (mean SE MW) | N stations | Median \|Δ\| (MW) | Median \|Δ\| (% of output) |
|---|---|---|---|
| <50 MW | 92 | 0.81 | 2.40% |
| 50–250 MW | 192 | 1.78 | 2.04% |
| 250–1000 MW | 42 | 3.19 | 0.67% |
| >1000 MW | 7 | 10.59 | **0.65%** |

**Lead conclusion on the 250–1000 MW band (n=42, 0.67% median error)** — that is the largest well-populated sample closest to typical PUN-scale industrial co-gen size, and it is backed up directly by named plants: FRNYPP (1,512 MW, corr 0.9995, 1.7 MW = 0.1%), LOSTPI CC (469 MW, corr 0.999, 2.5 MW = 0.5%). The >1000 MW band (STP 2,166 MW corr 0.997 = 0.5%, CPSES 2,383 MW corr 0.912 = 0.7%) is consistent with the same conclusion but rests on only **n=7** stations, so treat it as confirmatory, not the primary evidence. **For PUN-scale industrial co-gen sites, expect the SE/SCED gap to be under 1% of station throughput at a well-mapped station** — tighter than the all-station headline number suggests, because the headline is pulled down by small, volatile renewable stations.

## Basepoint vs telemetered output
No material difference: station-level median \|Δ\| correlates 0.999 between the two choices (mean-of-medians 10.5 MW telemetered vs 10.8 MW basepoint overall; 1.65 vs 1.80 MW for the pure-gen subset). Telemetered output remains the right choice as the physically-measured quantity.

## SE-vs-SCED timing check (confirms nearest-tick pairing)
For STP, CPSES, and LOSTPI (steady baseload/CC), Δ = SE − SCED barely changes across candidate ticks (:50/:55/:00/:05) — e.g. STP on 2026-06-15 00:57 SE=2613.2 MW vs SCED at :50/:55/:00/:05 = 2606.2/2606.0/2605.7/2605.6 MW (Δ range 7.0–7.6 MW, <0.03% spread). Confirms the pairing rule (:55 nearest a :57 snapshot, :00 nearest a :59 snapshot) is not a meaningful error source for stable plants. Full table: `timing_check_stp_cpses_lostpi.csv`.

## 15 worst stations by |mean Δ| (full list + notes in `calibration_by_station.csv`)
1. **DOW** (−263 MW, corr 0.71, 12 units) — large industrial co-gen/load complex: SE shows a large **net withdrawal**, mapped SCED generation is small. This is the exact PUN-style gen+load pattern the back-out method targets, not a mapping defect.
2. **LACY_CRK** (+178 MW, corr 0.97, 1 unit) — high correlation but SE >> SCED; single mapped unit likely covers only part of the station's true capacity.
3. **CANYONWD** (+154 MW, corr 0.94, 1 unit) — same partial-turbine-mapping pattern as several single-resource wind stations below.
4. **HRNT_SLR** (+152 MW, corr 0.994, 1 unit) — near-perfect shape match but SE ≈ 3× SCED; likely only a fraction of the plant's inverter blocks are captured under the one matched SCED resource.
5. **WL** (−137 MW, corr 0.04, 1 unit) — Wilson Ranch wind; uncorrelated, consistent with fast wind ramps + snapshot timing offset (prefix-derived code used after busname resolved to an unrelated switching station).
6. **BLSUMMIT** (−123 MW, corr 0.72, 8 units) — moderate correlation, negative bias → co-located load/curtailment/RAS most likely.
7. **COYOTE** (−119 MW, corr −0.26, 3 units) — `MAPPING UNVERIFIED` (prefix-fallback, low correlation, not individually confirmed) — could be wind volatility/timing, or the same wrong-station problem confirmed for CHIL/PEARSALL below.
8. **CHIL** — *removed from the ranked list*: confirmed via hourly-diurnal check to be a **wrong station match** (SCED shows a clean solar curve, SE is flat all day) — excluded from headline stats, see Mapping methodology above. (Would have ranked #8 at −119 MW, corr −0.43.)
9. **MAVCRK_W** (−107 MW, corr 0.99, 9 units) — very high correlation with a persistent offset → curtailment/RAS or a systematic accounting difference, worth a manual look.
10. **EL** (−102 MW, corr −0.58, 2 units) — wind volatility/timing.
11. **BORDAS** (+96 MW, corr 0.91, 1 unit) — likely additional unmapped turbine strings.
12. **AVIATOR** (−95 MW, corr 0.96, 3 units) — same co-located-load/curtailment pattern as BLSUMMIT/MAVCRK_W.
13. **PIONR_DJ** (+84 MW, corr 0.69, 1 unit) — partial turbine mapping + wind volatility.
14. **TORR** (+80 MW, corr 0.99, 2 units) — high correlation despite bias → likely a real, consistent under-count.
15. **RELOJ** (+71 MW, corr 0.97, 1 unit) — same partial-turbine-mapping pattern as TORR/BORDAS.

## Main failure modes
1. **Partial/incomplete unit mapping** — a station's true generation fleet isn't fully captured under the matched SCED name(s) (missing inverter blocks, turbine strings, or sibling CTGs). Shows up as **persistent, same-sign bias with high correlation** (LACY_CRK, HRNT_SLR, CANYONWD, TORR, RELOJ, MAVCRK_W, AVIATOR). Backed by direct evidence, not just inference: ERCOT/SCED (`ISOERCOTSCEDGEN`) registers 1,798 distinct generation resources vs. only 1,605 tracked in `GENUNITSCEDNAME` — a 12% fleet gap. The pure-gen bias check (median mean-Δ ≈ 0) shows this is confined to a tail of stations, not a system-wide drag.
2. **Wrong-station mapping that isn't caught by the zero-injection ratio test** — confirmed for `CHIL` and `PEARSALL`: both looked like plausible solar+storage hybrids (mean SE near zero) but a hourly-diurnal check showed SE at those codes is flat all day/night while the mapped SCED resources show a textbook solar curve — proof of a coincidental prefix collision, not a hybrid netting to zero. Any `PREFIX_FALLBACK` station with correlation below ~0.3 (`WL`, `COYOTE`, `EL`, `CN`, and others — see CSV `MAPPING UNVERIFIED` notes) is at real risk of the same problem and was **not** individually confirmed here; treat those rows as unreliable pending a spot-check like the one that caught CHIL/PEARSALL.
3. **Fast-ramping/volatile resources + timing offset** — wind, solar, and peaking-gas units can move tens of MW within the ~2-3 minute SE-to-SCED gap, producing large absolute error even at correctly-mapped stations (GBY, high-corr wind stations with real bias).
4. **Busname-to-switching-station collisions** — the single biggest mapping risk found in this exercise: `GENUNIT.BUSNAME` often names a shared collector bus that the ERCOT data dictionary resolves to an upstream switching station with ~0 net injection, not the generator's own station. Caught and corrected for 87+ stations via a ratio-based sanity check (`|mean SE| / |mean SCED|` too small to be real) — but that same test cannot distinguish "wrong station, coincidentally near zero" (correctable) from "wrong station, coincidentally non-zero" (mode #2 above, silent). Any calibration workflow reusing this join **must** repeat both checks, not just the ratio test.
5. **Co-located industrial load** (DOW) — a real, not-a-bug pattern directly relevant to the PUN use case: net injection substantially below (or negative relative to) visible generation telemetry because of large on-site load.

## Headline for the PUN back-out method
- At well-mapped generation stations sized like typical PUN sites (250–1000 MW, n=42), SE-vs-SCED agreement is **~0.67% of station throughput** — consistent with (and reinforced by, though not primarily proven by) the smaller n=7 sample of >1000 MW plants at ~0.65%. This is the relevant number for PUN-scale sites, not the all-station 1.78 MW median (pulled down by small, volatile wind/solar stations).
- No systematic bias at well-mapped pure-gen stations (median mean-Δ ≈ 0, sign splits roughly 50/50), and this is a tail-confined effect (the partial-fleet-capture evidence above bounds it), not a population-wide drag.
- Real co-located-load stations (DOW) behave exactly as the back-out method assumes: SE net injection reflects gen minus load, with decent (not perfect, ~0.7) correlation to the visible generation telemetry — this is the closest analog in the June data to an actual PUN gen+load site.
- The single biggest risk to this method in production is **mapping error, not measurement noise** — and it comes in two flavors that require two different checks: (a) busname-to-switching-station collisions, caught by the ratio test (|mean SE| too small relative to |mean SCED|), and (b) coincidental wrong-station matches that are *not* near zero, which the ratio test misses entirely and which requires a structural check like the hourly-diurnal comparison that caught CHIL/PEARSALL. Any station used for PUN back-out should pass **both** checks, not just the ratio test, before being trusted — 143 of the 445 stations here are still on the unverified `PREFIX_FALLBACK` path and a subset of those (flagged `MAPPING UNVERIFIED` in the CSV) have not cleared check (b).
