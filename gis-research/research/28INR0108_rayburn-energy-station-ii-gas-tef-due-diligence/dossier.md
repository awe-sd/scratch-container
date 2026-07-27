# Dossier — Rayburn Energy Station II Gas (28INR0108)

Researched 2026-07-19 · site 33.5750, -96.6155 · verdict **real_active**

## 1. Verdict

- **real_active** — groundbreaking June 9 2026 confirmed ([PR](sources/2026-07-19_rayburnelectric_groundbreaking-pr.html) + [photo](sources/2026-07-19_rayburnelectric_groundbreaking-photo.jpg)); Siemens SGT-800 turbines (10 units) ordered; EPC Primoris mobilized; TEF loan executed June 4 2026 ([PR](sources/2026-07-19_rayburnelectric_tef-loan-pr.html))
- Construction: **clearing/early**, first activity **2026-06-09** ([groundbreaking photo](sources/2026-07-19_rayburnelectric_groundbreaking-photo.jpg))
- Site: 33.5750, -96.6155 — OSM RES I node (33.57772) + photo orientation (camera toward RES I → construction site immediately south), medium confidence ([satellite view](https://www.google.com/maps/@33.5750,-96.6155,2000m/data=!3m1!1e3))
- COD: reported 2028-02-26 → independent **2028-Q1**, drift risk **medium** (FIS + NSR permit still outstanding; tight 20-month build schedule)

## 2. Site identification

- Derivation: OSM places "Rayburn Energy Station" at 33.57772, -96.61547 (Hilton, Sherman TX); [groundbreaking photo](sources/2026-07-19_rayburnelectric_groundbreaking-photo.jpg) shows camera facing RES I CCGT plant as backdrop → construction site is immediately south, estimate 33.573–33.575
- **Stated project area: unknown** — no abatement, IA exhibit, or CAD parcel acreage obtained; PUCT Interchange is JS-only and could not be queried
- Cross-checks: OSM industrial node; PR/photo confirm Sherman TX; POI "Haggerty 138 kV" is consistent with existing Oncor transmission near Sherman; Sherman City Council approval May 19 2026 ([PR](sources/2026-07-19_rayburnelectric_sherman-expansion-pr.html))
- Not obtainable: exact street address; IA document with POI coordinates (PUCT Interchange JS-only); Grayson CAD parcel (SPA portal, API blocked)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Rayburn Energy Station II LLC | SPV | [TX Comptroller](sources/2026-07-19_comptroller_api_rayburn.json) taxpayer 32097231602 |
| Rayburn Country Electric Cooperative, Inc. | developer/owner | [Groundbreaking PR](sources/2026-07-19_rayburnelectric_groundbreaking-pr.html), [TEF loan PR](sources/2026-07-19_rayburnelectric_tef-loan-pr.html) |
| Primoris Services Corporation | EPC | [Groundbreaking PR](sources/2026-07-19_rayburnelectric_groundbreaking-pr.html) |
| Siemens Energy | Turbine supplier (10× SGT-800) | [Groundbreaking PR](sources/2026-07-19_rayburnelectric_groundbreaking-pr.html) |
| PUCT (Texas Energy Fund) | Lender | [TEF loan PR](sources/2026-07-19_rayburnelectric_tef-loan-pr.html) — Rayburn only cooperative among 17 TEF gas projects |

- Financing: Texas Energy Fund (TEF) loan executed June 4 2026; Dentons + Eversheds Sutherland (legal), Jefferies (financial advisor); loan amount not disclosed in PR ([TEF PR](sources/2026-07-19_rayburnelectric_tef-loan-pr.html))

## 4. Land & county records

- Tenure: **unknown** — no deed/lease confirmed; adjacent to RES I (758 MW CCGT acquired by Rayburn in 2021); Sherman City Council approved expansion May 2026 ([PR](sources/2026-07-19_rayburnelectric_sherman-expansion-pr.html))
- Abatements/agreements: none found — TX Comptroller Ch.312/313/JETI search not performed (gas plants rarely seek Chapter 313; cooperative ownership makes abatement less common)
- CAD: Grayson CAD portal (esearch.graysonappraisal.org) is JS-only SPA; no parcel confirmed under LLC or cooperative name — negative

## 5. Interconnection & contractual schedule

- POI per IA: "Double Tap 138 kV Haggerty (12677) - Progress Park (#12678) & Haggerty - Winding Oaks Switch" (from identity packet; IA document not retrieved — PUCT Interchange JS-only)
- IA signed **2025-12-22** per queue timeline ([timeline.md](timeline.md))
- Equipment: Siemens SGT-800 (10 units, simple-cycle peaking) per [groundbreaking PR](sources/2026-07-19_rayburnelectric_groundbreaking-pr.html)

| IA document | Signed | Financial security posted |
|---|---|---|
| Interconnection Agreement (Oncor) | 2025-12-22 | Not obtained (PUCT Interchange inaccessible) |

| Milestone | Queue record | Source |
|---|---|---|
| Screening complete | 2025-04-08 | [timeline.md](timeline.md) |
| IA signed | 2025-12-22 | [timeline.md](timeline.md) |
| Meets 6.9(1) | 2026-06-02 | [timeline.md](timeline.md) |
| FIS approved | — (outstanding) | [timeline.md](timeline.md) |
| Scheduled COD | 2028-02-26 | [timeline.md](timeline.md) |

- Queue-history COD drift ([timeline.md](timeline.md)): **0 changes** — 2028-02-26 held across all 18 monthly snapshots (Jan 2025 → Jun 2026)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-05 | RES I visible; land south undisturbed pre-groundbreaking | [png](imagery/key/s2_pre-groundbreaking_2026-05-01.png) |
| 2026-07-09 | Groundbreaking photo: crushed gravel pad active, equipment mobilized | [photo](sources/2026-07-19_rayburnelectric_groundbreaking-photo.jpg) |
| 2026-07 | Sentinel-2 consistent with very early site work (10m resolution cannot resolve 6-week-old civil activity) | [png](imagery/key/s2_post-groundbreaking_2026-07-01.png) |
| 2026-07 | Xwide 6km view: RES I industrial complex confirmed at 33.577 | [png](imagery/key/s2_xwide_2026-07-01.png) |

- Verdict: **clearing** — groundbreaking confirmed June 9 2026 by primary source; Sentinel-2 at 10 m cannot yet detect concrete pours or turbine pad work started <6 weeks ago

## 7. COD assessment

- Reported COD 2028-02-26 held perfectly stable — no drift across all 18 snapshots in the dataset (Jan 2025 to Jun 2026), suggesting a grounded contractual schedule
- TEF loan obligation provides a hard financial incentive to meet COD — PUCT loans typically carry milestone penalties
- Schedule is tight: groundbreaking June 2026, COD Feb 2028 = ~20 months. SGT-800 simple-cycle peaking units are factory-assembled and erect faster than CCGT; 10 units in ~20 months is achievable but requires no major delays
- Risks: (1) FIS approval still outstanding — needed before commercial operation; (2) TCEQ NSR air permit not found in public database under any Rayburn entity name in Grayson County — mandatory before COO, current status unknown; (3) first TEF loan project for this cooperative = execution risk
- For: institutional cooperative developer (not speculative merchant), Siemens turbine orders placed, Primoris EPC mobilized, state loan with COD obligations, Sherman City Council approval secured
- **Independent estimate: 2028-Q1, drift risk medium**

## 8. Could not determine

- Exact street address for RES II site (all PRs say "adjacent to RES I, Sherman TX")
- TCEQ NSR air permit number/status (not found under Rayburn Energy / Rayburn Country in Grayson County — may be pending under cooperative entity name or RN, or not yet in public system)
- IA document financial security amounts (PUCT Interchange portal is JS-only, cannot retrieve documents without browser)
- Grayson CAD parcels / land tenure (SPA portal, API blocked)
- TEF loan amount (not disclosed in press releases)
- Project acreage (no abatement, IA exhibit, or CAD source obtained)
