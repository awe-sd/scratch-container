# Dossier — Samson Solar 3 (21INR0491)

Researched 2026-07-19 · site unknown (stages 3-4 incomplete) · verdict **real_early**

## 1. Verdict

- **real_early** — Phase 3 of a real, actively-developed 1,310 MW complex (Phases 1 & 2 operating); however 18 COD changes over 4+ years, blank construction fields in Jun 2026 GIS, and a 5.75-year cumulative slip make the Sep 2026 reported COD non-credible ([timeline.md](timeline.md))
- Construction: **unclear** — no satellite imagery acquired; ERCOT GIS construction start/end blank as of Jun 2026
- Site: unknown — gmaps.py rate-limited; site pinpoint not completed; POI is "tap both 345kV 1685 FarmersVl - 1695 Moses ckts" in Lamar County TX (Oncor territory, NORTH zone)
- COD: reported 2026-09-30 → independent **2027-Q2 or later**, drift risk **high** (18 slips, last slip May 2026, blank construction progress)

## 2. Site identification

- Derivation: not completed — gmaps.py 429 error; no Places pin, no CAD parcels, no imagery
- **Stated project area:** unknown — no Ch.313/JETI or CAD records obtained; estimated ~1,000–1,200 acres for 250 MW phase (unverified)
- Cross-checks: POI text "FarmersVille – Moses 345kV" locates the tap in Lamar County, consistent with county assignment
- Not obtainable (this session): lat/lon, parcel IDs, exact POI switch coordinates

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Samson Solar Energy III LLC | SPV | [ERCOT GIS Jun 2026](https://www.ercot.com/gridinfo/resource) + [constructionreviewonline.com](https://constructionreviewonline.com/major-solar-projects-under-construction-in-texas/) |
| Invenergy LLC | Developer/operator | [samsonsolarenergycenter.com](https://samsonsolarenergycenter.com) (One S Wacker Dr, Suite 1500, Chicago IL) |
| WEC Infrastructure / WEC Energy Group | 80% owner (Dec 2025) | [infrasure.ai](https://infrasure.ai/project/ercot-21inr0491-samson-solar-3); WEC acquired Phase 1 80% Feb 2023 per [monarchprivate.com Sep 2024](https://monarchprivate.com) |

- Financing: WEC acquired 80% of Phase 3 from Invenergy Dec 2025 per infrasure.ai (no primary press release confirmed). Phase 2 had Monarch tax equity Sep 2024.

## 4. Land & county records

- Tenure: **unknown** — no CAD parcel search completed; complex spans Franklin, Lamar, Red River Counties
- Abatements/agreements: not searched (budget exhausted)
- CAD: 0 searches performed for Lamar County

## 5. Interconnection & contractual schedule

- POI per ERCOT GIS: "tap both 345kV 1685 FarmersVl - 1695 Moses ckts" — Oncor territory, NORTH zone
- IA signed: 2020-08-27 (from ERCOT GIS iaSigned field); PUCT filing not retrieved (402 paywall)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2020-08-27 | unknown (PUCT not retrieved) |

| Milestone | ERCOT GIS (Jun 2026) |
|---|---|
| FIS Approved | 2020-06-09 |
| IA Signed | 2020-08-27 |
| Approved for Energization | 2021-06-30 |
| Approved for Synchronization | 2021-10-26 |
| Commercial Operation Approved | — (never) |
| Projected COD | 2026-09-30 |

**ANOMALY:** Sync/energization approvals from 2021 with no subsequent COD across 4+ years. Construction start/end blank. Possible data bleed from Phase 1, or partial commissioning that halted.

- Queue-history COD drift ([timeline.md](timeline.md)): **18 changes** — 2021-12-31 → 2026-09-30; ~5.75-year total slip; last change May 2026

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| — | No imagery acquired (budget exhausted before Stage 4) | — |

- Verdict: **unclear** — no visual ground truth obtained

## 7. COD assessment

- Reported 2026-09-30 is the current contractual COD per ERCOT GIS Jun 2026 — but this is the 19th version of the COD since 2020
- 18 prior slips averaging ~3-4 months each; latest slip (2026-06-30 → 2026-09-30) occurred just May 2026 — two months ago
- ERCOT construction_start and construction_end fields remain blank in Jun 2026, indicating no construction progress data filed with ERCOT
- For: developer is real (Phases 1 & 2 operating in same county cluster); WEC 80% acquisition Dec 2025 signals continued commitment
- Against: relentless drift pattern, blank construction progress, sync/energization anomaly unexplained
- **Independent estimate: 2027-Q2 or later, drift risk HIGH**

## 8. Could not determine

- Site lat/lon (gmaps.py rate-limited; no parcel/CAD search completed)
- Project acreage / land tenure (no CAD or Ch.313/JETI records obtained)
- Signed IA details and financial security amounts (PUCT interchange behind paywall)
- Satellite construction stage (no imagery acquired)
- Explanation of 2021 sync/energization approvals with no subsequent COD (data anomaly unresolved)
- TX Comptroller entity details for Samson Solar Energy III LLC (JS-gated search portal)

*Research incomplete: Stages 2 (county records), 3 (site pinpoint), and 4 (satellite) not completed due to token budget exhaustion at Stage 1/queue-history. The findings above represent best available synthesis from LLC chain research and queue history only.*
