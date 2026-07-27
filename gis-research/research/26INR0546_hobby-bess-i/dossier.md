# Dossier — Hobby BESS I (26INR0546)

Researched 2026-07-19 · site 29.6510, -95.3144 · verdict **unclear**

## 1. Verdict

- **unclear** — FIS approved (Jan 2026) but no IA signed in 23 monthly snapshots; no PUCT filing; no construction in imagery ([timeline](timeline.md))
- Construction: **no_activity** — dense urban SE Houston, no graded pad or container rows at Garden Villas substation ([2km frame](imagery/s2_2026-07-01_gv_2km.png))
- Site: 29.6510, -95.3144 — OSM Garden Villas 138kV substation node (CenterPoint facility #42680), high confidence ([satellite view](https://www.google.com/maps/@29.6510,-95.3144,5000m/data=!3m1!1e3))
- COD: reported 2027-10-15 → independent **2028-Q4+**, drift risk **high** (no IA = no contractual grounding; prior +15-month slip)

## 2. Site identification

- Derivation: POI text "Double Tap 138kV 42680 Garden Villas" → OSM Overpass query for CenterPoint 138kV substations → Garden Villas node at 29.6510, -95.3144 ([artifact](sources/2026-07-19_openstreetmap_garden-villas-substation.json))
- **Stated project area: not obtainable** — no IA, no abatement, no CAD parcel found
- Cross-checks: POI names CenterPoint facility #42680 explicitly; OSM voltage tag 138000;69000;12000 matches; SE Houston Harris County consistent with HOUSTON CDR zone; imagery shows urban residential fabric around substation, no BESS pad
- Not obtainable: exact BESS parcel (no IA exhibit, no CAD hit under any LLC variant)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Hobby BESS I, LLC | SPV (presumed) | project name in ERCOT queue; unverified at TX Comptroller (AJAX portal blocked) |
| Airport Storage II LLC (unverified) | possible developer | surfaced from DDG via banned aggregators only — **not independently confirmed** |

- Financing: **unknown** — 0 SEC EDGAR hits for "Hobby BESS" or "Airport Storage II"; no press releases; no news

## 4. Land & county records

- Tenure: **unknown** — no HCAD parcel found under "Hobby BESS", "Airport Storage", or any LLC variant
- Abatements/agreements: none found — TX Comptroller Ch.313/JETI search not executed (portal blocked); no Harris County commissioners minutes surfaced
- CAD: HCAD search.hcad.org portal returned 403; AJAX-only HCAD search inconclusive — 0 confirmed parcels

## 5. Interconnection & contractual schedule

- POI per queue: "Double Tap 138kV 42680 Garden Villas – 48250 Hall & 42680 Garden Villas – 48013 Chocolate Bayou" (CenterPoint, Harris Co.)
- **No signed IA** — PUCT Interchange search for "Hobby BESS I" and "Airport Storage" both returned "Control number not found"

| IA document | Signed | Financial security posted |
|---|---|---|
| — | none | none |

| Milestone | Status |
|---|---|
| FIS approved | 2026-01-20 |
| IA signed | — (not signed as of 2026-06-01) |
| Scheduled COD | 2027-10-15 (ungrounded, no IA) |

- Queue-history COD drift ([timeline.md](timeline.md)): **1 change** — 2026-07-31 → 2027-10-15 (+15 months); in reports since 2024-08 (23 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07 | Dense residential SE Houston; no BESS pad, no cleared ground, no container rows at/near Garden Villas substation | [gv_1km](imagery/s2_2026-07-01_gv_1km.png) / [gv_2km](imagery/s2_2026-07-01_gv_2km.png) |
| 2026-07 | Chocolate Bayou substation area (29.6279, -95.3527): residential/commercial; no activity | [cb_1km](imagery/s2_2026-07-01_cb_1km.png) |

- Verdict: **no_activity** — no construction signatures anywhere in 1–2 km buffer around either POI substation; urban density around Garden Villas leaves limited open land for a 10-80 acre BESS pad

## 7. COD assessment

- Reported 2027-10-15 has **no contractual grounding** — no signed IA as of latest queue snapshot (2026-06-01), no PUCT filing
- Without IA: no NTP issued, no build start; BESS builds run 12-18 months after NTP
- Optimistic path: IA signed H2 2026 → NTP Q4 2026 → BESS build 14 months → commercial operation Q2-Q3 2028
- Risk factors: no developer identity confirmed; no financing signal; no news; dense urban site may have land assembly challenges; one prior 15-month COD slip already
- **Independent estimate: 2028-Q4, drift risk high**

## 8. Could not determine

- Developer identity (LLC chain beyond SPV name; "Airport Storage II LLC" not independently verified)
- Land/parcel (no HCAD hit; no IA exhibit)
- Project area (no abatement, no IA, no CAD)
- Exact substation parcel where BESS would sit (BESS in dense urban area — may be adjacent industrial parcel)
- Financing, EPC, offtake — no news or announcements found
- TX Comptroller franchise tax search (AJAX portal not accessible via direct API)
