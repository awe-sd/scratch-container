# Dossier — Briggs Storage (24INR0058)

Researched 2026-07-19 · site 33.0014, -99.6055 · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed by Intersect Power (Google-owned), Clear Crossing 345kV POI confirmed at [OSM Way 453376936](https://www.openstreetmap.org/way/453376936); sister projects at same developer already online; no BESS construction started
- Construction: **pre_construction**, no ground activity confirmed at BESS site ([2026-07 tight chip](imagery/chip_sub_tight_2026-07.png))
- Site: 33.0014, -99.6055 — OSM substation geometry, high confidence ([map](https://google.com/maps/@33.0014,-99.6055,5000m/data=!3m1!1e3))
- COD: reported 2028-04-15 → independent **2029-Q2**, drift risk **high** (FIS never approved, 4x upsize pending restudy)

## 2. Site identification

- Derivation: OSM Way 453376936 centroid (33.0013738°N, 99.6054944°W) = Clear Crossing 345kV substation, Haskell County TX; operator AEP/ETT; voltage 345kV ([OSM](https://www.openstreetmap.org/way/453376936))
- **Stated project area: unknown** — IA PDF 402-blocked; CAD not searched; imagery footprint: unverified (BESS pad not yet identifiable)
- Cross-checks: OSM substation matches ERCOT POI element ID 60515; imagery confirms large solar compound at these coords; prior triage had wrong coords (Haskell town center, 17 km NW — all prior chips missed site)
- Not obtainable: exact tap-line coords (CEII); IA PDF milestone exhibit (PUCT 402-blocked)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| IP Quantum III, LLC | SPV (TX entity 0802381611) | [PUCT CN 35077](https://interchange.puc.texas.gov/Documents/35077_2235_1533641.PDF) (blocked) |
| Intersect Power, LLC | Developer/owner | [OpenCorporates](https://opencorporates.com/companies/us_tx/0802381611); "IP" naming convention across portfolio |
| Google/Alphabet | Parent (pending close) | Dec 2025 acquisition announcement |
| Sheldon Kimber | CEO, Intersect Power | Company filings |
| EPC | Unknown | — |
| Offtaker | Likely Google (pattern from Quantum Solar campus) | — |

- Financing: Intersect Power $837M close Jul 2024 (included IP Lumina II BESS, same LLC family); no Briggs-specific announcement

## 4. Land & county records

- Tenure: **unknown** — IA PDF not retrieved; CAD parcel search not conducted
- Abatements/agreements: none found — normal for post-2022 battery project (Ch.313 expired 2022; JETI apparently unapplied)
- CAD: not searched

## 5. Interconnection & contractual schedule

- POI per IA filing: "tap 345kV 60515 Clear Crossing - 60507 Pendulo" ([PUCT CN 35077](https://interchange.puc.texas.gov/Documents/35077_2235_1533641.PDF) — PDF 402-blocked, POI from ERCOT GIS report)
- Equipment: unknown (IA PDF not retrieved)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original SGIA | 2025-03-15 | unknown (PDF blocked) |
| First Amended & Restated SGIA ([PUCT CN 35077 Item 2235](https://interchange.puc.texas.gov/Documents/35077_2235_1533641.PDF)) | 2025-08-21 | unknown (PDF blocked) |

| Milestone | Status |
|---|---|
| FIS approved | — (never approved) |
| IA signed | 2025-03-15 |
| Meets 6.9(1) | 2025-03-24 |
| Meets all 6.9 | — |
| Construction start (reported) | — |
| Contractual COD | unknown (PDF blocked) |

- Queue-history COD drift ([timeline.md](timeline.md)): 2 changes — 2024-12-31 → 2027-09-15 → 2028-04-15

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07 (2km) | Massive solar arrays substantially complete at Clear Crossing sub; substation compound visible | [png](imagery/chip_33.001_-99.605_2026-07.png) |
| 2026-07 (1km tight) | Pale compound adjacent to substation (possible BESS/sub yard) — no container rows identifiable | [png](imagery/chip_sub_tight_2026-07.png) |
| 2026-07 (4km wide) | Full extent: solar fills NW and NE quadrants; Clear Crossing sub compound at center | [png](imagery/chip_wide_2026-07.png) |

- Verdict: **pre_construction for BESS** — solar at this site is substantially complete (likely Briggs Solar 23INR0059 or Quantum Solar 21INR0207 at adjacent Kilby Station); no BESS container rows confirmed at 10m/px; pale compound beside sub is sub yard or early pad, cannot confirm BESS build started

## 7. COD assessment

- FIS was requested 2022-03-04 but never approved through Jun 2026 — the 4x capacity upsize (70→336 MW, Jul 2025) almost certainly requires a new full interconnection study before NTP can issue
- IA was amended Aug 2025 to reflect upsize and developer transfer; "Meets All Guide 6.9" (financial security + NTP) still blank in Jun 2026 report — NTP has not issued
- Best case if FIS/restudy clears late 2026, NTP issues Q1 2027: BESS build 12-18 months → COD Q1-Q2 2028 (barely on reported target)
- Base case: FIS approval + restudy takes until mid-2027, NTP Q3 2027 → COD 2028-Q4 to 2029-Q2 (one more COD slip)
- Developer capability is established — Intersect Power has completed Quantum Solar + Quantum Storage and Solace Solar + Solace Storage at nearby substations; risk is regulatory/study delay not developer quality
- Independent estimate: **2029-Q2**, range 2028-Q4 to 2030-Q1, drift risk **high**

## 8. Could not determine

- PUCT IA PDF content (milestone schedule, financial security amounts, CEII status) — HTTP 402 blocks all retrieval attempts
- Whether FIS was waived or is genuinely outstanding after upsize
- BESS pad location / acreage (project area unknown)
- EPC contractor, PPA/offtaker for this specific project
- Whether solar in 2026-07 imagery is Briggs Solar (23INR0059) or a different Intersect Power project at adjacent substation
- 2023-06 and 2024-01 historical chips downloaded but not read (budget exhausted before construction dating)
