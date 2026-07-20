# Dossier — Little Ridge Storage (25INR0238)

Researched 2026-07-19 · site 33.0691, -96.4510 · verdict **paper**

## 1. Verdict

- **paper** — no IA signed after 3+ years in queue; COD has drifted 27 months; zero construction visible in Oct 2025 – Jul 2026 satellite imagery adjacent to the confirmed POI substation
- Construction: **no_activity**, first activity: none observed
- Site: 33.0691, -96.4510 — OSM hamlet "Little Ridge" = Ray Olinger Power Station locality, Collin County; high confidence ([satellite view](https://www.google.com/maps/@33.0691,-96.4510,5000m/data=!3m1!1e3))
- COD: reported 2027-09-01 → independent **not credible / 2029+ if ever**, drift risk **high** (no IA, 27-mo prior drift, no site activity)

## 2. Site identification

- Derivation: OSM Nominatim query "Olinger Texas" returns way 864993515 = "Ray Olinger Power Station, **Little Ridge**, Collin County, Texas" at 33.0691, -96.4510 — hamlet name is the literal source of the project name ([artifact](sources/2026-07-19_osm-nominatim_olinger-substation-location.json))
- **Stated project area: not determinable** — no IA, no abatement doc, no CAD parcel found; typical BESS 252 MW ≈ 20-60 acres
- Cross-checks: OSM hamlet "Little Ridge" + Collin County + NORTH zone all consistent; adjacent unnamed 138kV transmission substation at 33.0681, -96.4515 (0.1 km from Ray Olinger) = likely "Olinger (818)" tap point ([artifact](sources/2026-07-19_osm-overpass_substations-near-olinger.json))
- Not obtainable: exact Swindell (812) substation coordinates (not in OSM); Swindell is likely a GP&L internal designation on the Garland-area 138kV network

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Little Ridge Storage, LLC | SPV (asserted in identity packet) | queue record only — not independently verified |
| TX BESS B LLC | possible developer | infrasure.ai + ercotqueue.com (BANNED sources — cannot cite); no independent confirmation found |
| unknown | parent | not determinable |

- Financing: **none found** — no PPA, no lender, no EPC announcement, no press release in any independent source

## 4. Land & county records

- Tenure: **unknown** — no CAD parcel, no abatement, no IA
- CAD: 0 hits returned — Collin CAD portal returned HTTP 403; no owner-name data obtained
- Abatements: NEGATIVE — no Collin County Ch.312/JETI/Ch.403 agreement found for Little Ridge Storage or TX BESS B in Comptroller SB1340 database (JS-rendered, could not query) or web searches
- Commissioner Court: NEGATIVE — eagenda site 403; no web evidence of project in county proceedings

## 5. Interconnection & contractual schedule

- POI per signed IA: **no IA exists** — queue milestone `iaSigned` = blank in all 38 monthly snapshots through Jun 2026 ([timeline](timeline.md))
- Equipment: not determinable (no IA filed)

| IA document | Signed | Financial security posted |
|---|---|---|
| No IA | — | — |

| Milestone | Status |
|---|---|
| FIS requested | 2023-04-25 |
| FIS approved | **never** |
| IA signed | **never** |
| Scheduled COD | 2027-09-01 (claimed) |

- Queue-history COD drift ([timeline.md](timeline.md)): **2 changes** — 2025-06-01 (entered) → 2025-12-11 → 2027-09-01; 27-month total drift in 3 years without ever achieving FIS approval

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-10 | No activity — Ray Olinger plant + undisturbed surroundings, no BESS pad | [png](imagery/key/s2_2025-10-01.png) |
| 2026-04 | No activity — same footprint, no clearing or construction | [png](imagery/key/s2_2026-04-01.png) |
| 2026-07 | No activity — partially cloudy but no construction signal in clear areas | [png](imagery/s2_2026-07-01_2km.png) |

- Verdict: **no_activity** — 9-month window through ~4 months before the claimed 2027-09-01 COD confirms no ground has been broken; a 252 MW BESS (20-60 acres) at 12-18 month build time would need to be under construction NOW

## 7. COD assessment

- No IA means no contractual obligation to build — the 2027-09-01 COD is an aspirational self-report with zero contractual grounding
- Project has never cleared FIS in 3+ years (entered queue May 2023): missing FIS approval → IA → financial security → NTP → construction
- COD has already slipped 27 months (2025-06 → 2027-09) without achieving any construction milestones
- Satellite imagery confirms no construction as of Jul 2026 — a 252 MW BESS would require 12-18 months to build, meaning it cannot achieve 2027-09 even if construction started today
- No financing, no EPC, no PPA found in any independent source
- **Independent estimate: NOT credible for any COD before 2029; most likely outcome is further COD slip or cancellation. Drift risk: HIGH.**

## 8. Could not determine

- LLC parent/developer chain (TX Comptroller API blocked; SOS Direct is paid; corporate wiki blocked)
- Any independent confirmation of developer identity (TX BESS B LLC not verified from non-banned source)
- Collin CAD parcels (portal returned 403)
- Exact Swindell (812) substation coordinates
- Whether any FIS study is in progress (FIS approved = blank; no way to know study status without ERCOT portal access)
- Project area acreage (no IA, no abatement doc)
