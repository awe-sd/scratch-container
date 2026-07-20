# Dossier — Wake Wind Energy Repower (26INR0647)

Researched 2026-07-19 · site 33.8250, -101.0997 · verdict **real_active**

## 1. Verdict

- **real_active** — Southern Power committed repower in Q2 2025; $432M CWIP at Mar 31, 2026; PPAs contracted ([Q1 2026 10-Q](sources/2026-07-19_sec_so_q1_2026_10q_wake_wind_repower_excerpts.md))
- Construction: **pre_construction**, no new activity in Jun 2026 imagery ([frame](imagery/key/s2_2026-06-01.png)); sequenced 4th of 5 Southern Power repowers
- Site: 33.8250, -101.0997 — EIA-860M centroid for existing 257 MW plant ([map](https://www.google.com/maps/@33.825,-101.0997,5000m/data=!3m1!1e3))
- COD: reported 2027-05-01 → independent **2027-Q2**, drift risk **medium** (already slipped once; FIS not yet approved)

## 2. Site identification

- Derivation: EIA-860M/Wikidata centroid for existing Wake Wind Energy Center (33°49'30"N, 101°5'58.92"W)
- **Stated project area: not quantified** — plant spans Crosby & Floyd Counties across ~15 km; Ch.313 doc covers 116.62 MW portion in Crosbyton CISD ([amendment](sources/2026-07-19_ch313_crosbyton_isd_wake_wind_amendment1.pdf))
- Cross-checks: existing plant coords (EIA-860M) agree with ERCOT queue county (Crosby) and SEC filing ("Crosby & Floyd Counties, TX" per [Q1 2026 10-Q](sources/2026-07-19_sec_so_q1_2026_10q_wake_wind_repower_excerpts.md)); PUCT Docket 55029 names WETT Cottonwood 345 kV station in Dickens County as POI — within ~10–15 km, consistent
- Not obtainable: exact POI switch coordinates (CEII); individual turbine lat/lon (FAA OE portal inaccessible under government shutdown)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Wake Wind Energy, LLC (Delaware; TX ID: 32050567323) | Original SPV | [Ch.313 amendment](sources/2026-07-19_ch313_crosbyton_isd_wake_wind_amendment1.pdf) |
| Southern Power Company (majority) | Developer/owner since Oct 2016 | [SEC Q3 2025 10-Q](sources/2026-07-19_sec_so_q3_2025_10q_wake_wind_repower_excerpts.md) |
| Invenergy Services LLC (minority) | Co-owner | [SEC Q3 2025 10-Q](sources/2026-07-19_sec_so_q3_2025_10q_wake_wind_repower_excerpts.md) |
| Invenergy Wind LLC (Chicago) | Original developer | [SEC EDGAR search](sources/2026-07-19_sec_edgar_southern_power_wake_wind_repower.md) |

- Financing: PPAs contracted ("new and amended PPAs" per [Q3 2025 10-Q](sources/2026-07-19_sec_so_q3_2025_10q_wake_wind_repower_excerpts.md)); Kay Wind tax equity partnership interests acquired in 2025 (pattern likely shared)

## 4. Land & county records

- Tenure: **leased** (presumed; wind farms in TX are typically lease-based; existing plant leases in Crosby & Floyd Counties)
- Abatements/agreements: existing plant holds Ch.313 App No. 308 (Crosbyton CISD, 116.62 MW in Crosby, 140.63 MW in Floyd) ([agreement](sources/2026-07-19_ch313_crosbyton_isd_wake_wind_amendment1.pdf)); no JETI repower abatement found — normal since Ch.313 expired 2022-12-31
- CAD: Crosby CAD portals not accessible via WebFetch; no parcel records retrieved

## 5. Interconnection & contractual schedule

- POI: "59904 Cottonwood 345" (ERCOT queue); confirmed WETT Cottonwood 345 kV station, Dickens County per PUCT Docket 55029 (DDG snippet)
- Equipment: full repower of 257 MW; existing GE 1.7 MW turbines (~150) to be replaced; new turbine model not disclosed
- No signed IA found (PUCT Interchange HTTP 402 blocked)

| IA document | Signed | Financial security posted |
|---|---|---|
| No IA found (PUCT portal blocked) | — | — |

| Milestone | Southern Power schedule (Q3 2025 10-Q) | Updated (Q1 2026 10-Q) |
|---|---|---|
| Committed to develop | Q2 2025 | Q2 2025 |
| Projected COD | Q4 2026 | **Q2 2027** |

- Queue-history COD drift (from [timeline.md](timeline.md)): 1 change, 2026-12-01 → 2027-05-01

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-10 | Existing turbine pads (~150 white arrow shadows); no new grading | [png](imagery/key/s2_2025-10-01.png) |
| 2026-03 | No change; existing plant only; no foundation/staging work | [png](imagery/key/s2_2026-03-01.png) |
| 2026-06 | Same; ~150 existing turbines visible across 12 km span; no construction | [png](imagery/key/s2_2026-06-01.png) |

- Verdict: **pre_construction** — plant is operating as-is; Southern Power hasn't broken ground yet; expected start ~H2 2026 based on Q2 2027 target

## 7. COD assessment

- Southern Power's own Q1 2026 10-Q schedules Wake Wind at **Q2 2027**, exactly matching ERCOT queue COD 2027-05-01 — the two sources corroborate each other
- Schedule already slipped once: Q4 2026 (per Sep 2025 10-Q) → Q2 2027 (per Mar 2026 10-Q) — before construction even started
- $432M CWIP at Mar 2026 (all 5 repowers combined) proves active spend; but Wake Wind is the 4th of 5 to complete — Kay Wind goes first (Q3 2026), then Grant Wind & Grant Plains (Q4 2026), then Wake Wind
- Remaining risk: FIS not yet approved (as of Jun 2026 queue snapshot); no signed IA confirmed; interconnection approval still needed
- Independent estimate: **2027-Q2** (May/Jun 2027). A further 1–2 quarter slip is possible if FIS/IA delays, but Q3 2027 is the outer bound given Southern Power's accelerated depreciation burn schedule
- Financial commitment is real and large; PPAs are contracted; Southern Power has executed on Kay Wind already — project will be built, timing is the only variable

## 8. Could not determine

- Signed IA or financial security amount (PUCT Interchange blocked; no PUCT docket filed for this repower yet)
- New turbine model/manufacturer (not disclosed in SEC filings)
- Exact project acreage (CAD portals inaccessible)
- FAA OE/AAA filings for individual turbine coordinates (portal inaccessible)
- JETI abatement filing (if any — none found, likely not pursuing)
- Exact construction start date (imaging shows pre-construction through Jun 2026)
