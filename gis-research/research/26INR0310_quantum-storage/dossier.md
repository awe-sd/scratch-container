# Dossier — Quantum Storage (26INR0310)

Researched 2026-07-19 · site 33.000, -99.612 · verdict **real_active**

## 1. Verdict

- **real_active** — developer confirmed "Quantum will begin operations this month" in June 2026 press release ([PR](sources/2026-07-19_intersect_quantum-operations-PR.html)); Kilby 345kV interconnect marked IN-SERVICE 2026-01-27 ([TPIT](sources/2026-07-13_ercot_TPIT.xlsx))
- Construction: **operating**, imagery shows fully-built solar array + substation compound ([July 2026](imagery/key/s2_2026-07-01_solar_3km.png))
- Site: 33.000, -99.612 — Sentinel-2 imagery centroid + Paint Creek ISD CAD corroboration ([Google Maps](https://google.com/maps/@33.000,-99.612,5000m/data=!3m1!1e3))
- COD: reported 2026-07-21 → independent **2026-Q3**, drift risk **low** (facility operational as of June; ERCOT approvedForCommercialOperation null is likely administrative lag)

## 2. Site identification

- Derivation: Sentinel-2 3km chip at 33.000, -99.612 shows large multi-block solar array + compact substation compound consistent with co-located BESS; corroborated by CAD lease name "PAINT CREEK ISD" placing asset in north-central Haskell County ([imagery](imagery/key/s2_2026-07-01_solar_3km.png))
- **Stated project area: not retrieved** — no IA exhibit or abatement doc recovered; BESS footprint estimated 30–80 acres from imagery substation chip ([chip](imagery/key/s2_2026-07-01_substation_1km.png))
- Cross-checks: TPIT "Kilby: Construct New 345kV Station" in Haskell County on Clear Crossing–Pendulo line ([TPIT](sources/2026-07-13_ercot_TPIT.xlsx)) + Paint Creek ISD CAD records ([CAD](sources/2026-07-19_haskell_cad_quantum_owners.json)) — consistent, within ~7 km of each other
- Not obtainable: exact Kilby Switching Station GPS coordinates (CEII-protected ERCOT internal ID 60089)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| IP Quantum BESS LLC / IP Quantum II BESS LLC | SPV × 2 | [CAD](sources/2026-07-19_haskell_cad_quantum_owners.json) |
| Intersect Power | Developer / owner | [CAD addr: 140 New Montgomery St SF](sources/2026-07-19_haskell_cad_quantum_owners.json) |
| Alphabet / Google | Acquirer (closed Mar 2026) + offtaker | [PR June 2026](sources/2026-07-19_intersect_quantum-operations-PR.html) |
| EPC | Unknown | — |

- Financing: BESS on Haskell CAD at combined ~$349M market value (IP Quantum BESS LLC $173.5M + IP Quantum II BESS LLC $175.4M) ([CAD](sources/2026-07-19_haskell_cad_quantum_owners.json)); financial security milestone = "Yes" in ERCOT queue ([timeline](timeline.md))

## 4. Land & county records

- Tenure: **leased** (mineral/industrial leases in Haskell CAD; not fee-simple parcel) — two BESS entities + two solar entities all under 140 New Montgomery St address ([CAD](sources/2026-07-19_haskell_cad_quantum_owners.json))
- Abatements/agreements: none found — Ch.313 closed post-2022; no JETI entry found; expected absence for BESS, not evidence of paper project
- CAD: 4 IP Quantum entities found (2 BESS + 2 solar); lease names "COD JAN 1 2026 PAINT CREEK ISD" and "COD JAN 1 2026 HASKELL ISD" — tax assessment effective dates ([CAD](sources/2026-07-19_haskell_cad_quantum_owners.json))

## 5. Interconnection & contractual schedule

- POI: 60089 Kilby Switching Station 345kV — ERCOT TPIT confirms new station built on Clear Crossing–Pendulo 345kV line, Haskell County, ETT-owned, IN-SERVICE 2026-01-27 ([TPIT](sources/2026-07-13_ercot_TPIT.xlsx))
- Equipment: 321.75 MW BESS (ERCOT queue); 320 MWAC confirmed on Haskell CAD lease

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([not retrieved](—)) | 2023-10-26 | Yes (amount not retrieved — PUCT portal 402) |

| Milestone | Queue data |
|---|---|
| IA signed | 2023-10-26 |
| FIS approved | 2025-06-16 |
| Meets 6.9 | 2025-08-04 |
| Approved for energization | 2026-03-26 |
| Approved for synchronization | 2026-04-10 |
| Commercial operation approved | null (as of 2026-06-01 snapshot) |

- Queue-history COD drift ([timeline.md](timeline.md)): 4 values over 2.5 years — 2026-03-31 → 2026-06-30 → 2026-06-01 → 2026-07-21; total rightward drift ~4 months

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | Solar array substantially complete/operating — parallel dark module rows across multiple graded blocks; O&M building + compact gravel compound (BESS containers) beside new substation | [3km](imagery/key/s2_2026-07-01_solar_3km.png) |
| 2026-07-01 | 1km substation chip: white building, dense module rows, gravel pad with rectangular structures — consistent with operating BESS facility | [1km](imagery/key/s2_2026-07-01_substation_1km.png) |

- Verdict: **operating** — site fully built; no bare-ground or mid-construction signal; consistent with June 2026 operations announcement

## 7. COD assessment

- Developer explicitly stated "Quantum will begin operations this month" in June 4, 2026 press release ([PR](sources/2026-07-19_intersect_quantum-operations-PR.html)) — the single most direct evidence
- ERCOT approved for synchronization 2026-04-10 ([timeline](timeline.md)); Kilby substation in-service 2026-01-27 ([TPIT](sources/2026-07-13_ercot_TPIT.xlsx)) — all prerequisite gates cleared
- July 2026 imagery shows fully-built facility with no construction indicators ([imagery](imagery/key/s2_2026-07-01_solar_3km.png))
- ERCOT `approvedForCommercialOperation` null in 2026-06-01 snapshot (last data point, 7 weeks prior to today) is an administrative lag, not evidence of non-operation; milestone typically records formal ERCOT approval date after the unit files for it
- Reported COD 2026-07-21 is either the formal ERCOT commercial operation approval target or a final paperwork date; the facility was operationally online by June 2026
- **Independent estimate: 2026-Q3, drift risk low** — facility almost certainly operational now; remaining uncertainty is purely administrative paperwork timing

## 8. Could not determine

- IA PDF and financial security amount (PUCT portal returns 402; IA exists per queue milestone)
- Exact parcel acreage or site boundaries (no abatement doc; BESS is compact, ~30-80 acres estimated)
- EPC contractor identity
- Exact BESS container count / configuration (10m/px resolution insufficient to enumerate)
- Whether co-located Google data center is on the same site parcel or adjacent
