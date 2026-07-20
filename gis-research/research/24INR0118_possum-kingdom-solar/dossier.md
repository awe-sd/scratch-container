# Dossier — Possum Kingdom Solar (24INR0118)

Researched 2026-07-19 · site unresolved · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed 2025-07-25, FIS approved 2025-03-18, Meets 6.9(1) achieved 2026-06-09; companion [Possum Kingdom BESS (24INR0375)](sources/2026-07-19_ercot-gis-jun2026_pk-solar-rows.csv) under same LLC at same POI; milestones consistent with real intent
- Construction: **unknown** — no imagery obtained (CDSE creds expired; no delivery pin); reported construction-end 2026-05-08 has passed with zero energization milestones
- Site: unresolved — best anchor is [Willow Creek Switch (bus 1421)](sources/2026-07-19_osm-overpass_jack-county-substations.json) at 33.0562°N, 97.9103°W (Wise/Jack border); project taps Willow Creek–Thomas Price line segment traversing eastern Jack County
- COD: reported 2027-10-29 → independent **2028-Q3**, drift risk **high** (35-month cumulative slip, construction-end already passed)

## 2. Site identification

- Derivation: POI triangulation only — Willow Creek Switch (ERCOT bus 1421) reverse-geocoded via OSM Nominatim to 33.0562°N, 97.9103°W, Wise County; Jacksboro substation (bus 1429) at 33.2772°N, 98.1068°W, Jack County ([substation data](sources/2026-07-19_osm-overpass_jack-county-substations.json))
- **Stated project area: unknown** — no IA PDF, no CAD parcels, no abatement application retrieved
- No lat/lon reported — derivation method insufficient per playbook (no parcel, no pin, no imagery feature)
- Not obtainable: IA PDF (PUCT 402), CAD parcel (form-based portal), delivery pin (gmaps 429), satellite imagery (CDSE 401, Google Static API 403)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| PK Solar, LLC | SPV | [ERCOT GIS Jun-2026 row](sources/2026-07-19_ercot-gis-jun2026_pk-solar-rows.csv) |
| Unknown | developer/parent | not found — zero web/news presence |
| Unknown | EPC | not found |
| Unknown | PPA/offtaker | not found |

- Financing: unknown — no press release, no financing announcement found
- Note: "PK Solar" returns no web results; developer is either a private equity shell or early-stage developer with no public footprint

## 4. Land & county records

- Tenure: **unknown** — no parcel records retrieved
- Abatements/agreements: none expected (post-2022; Ch.313 expired Sept 2023); none found
- CAD: Jack County CAD search not completed — portal form-based, no GET/POST endpoint exposed; 0 results confirmed

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: "Tap 345kV 1421 Willow Creek Switch – 11523 Thomas Price" ([GIS row](sources/2026-07-19_ercot-gis-jun2026_pk-solar-rows.csv))
- IA PDF: **not retrieved** (PUCT interchange.puc.texas.gov HTTP 402 on all search attempts)
- Financial security: unknown

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2025-07-25 | unknown (PDF not retrieved) |

| Milestone | Reported in queue |
|---|---|
| Construction start | 2025-05-01 |
| Construction end (passed) | 2026-05-08 |
| Reported COD | 2027-10-29 |

- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** — 2024-11-22 → 2026-05-08 → 2026-10-30 → 2027-10-29; in reports since 2022-05 (50 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| — | No imagery obtained | CDSE 401 Unauthorized; Google Static API 403 |

- Verdict: **unknown** — no imagery available; reported construction-end passed without energization milestones

## 7. COD assessment

- 4 reported-COD changes over 4 years: original 2024-11 → current 2027-10 = **~35 months cumulative slippage before construction confirmed**
- Reported construction-end date 2026-05-08 has **already passed** with no energization or synchronization milestones — schedule is running late
- IA signed 2025-07-25: for 262 MW solar, 18-24 months to commercial operation → earliest realistic COD ~2027-Q1–Q3; history of slippage implies further delay
- Companion Possum Kingdom BESS (200 MW, same COD) adds commissioning complexity — co-located solar+BESS projects typically take longer to reach commercial operation
- No external corroborators (developer press releases, EPC mobilization, financing close) — without these, reported Oct-2027 COD unsupported
- **Independent estimate: 2028-Q3, drift risk high**

## 8. Could not determine

- Developer / parent company (PK Solar LLC untraceable online)
- IA PDF — schedule exhibit, financial security, parties (PUCT 402)
- Site lat/lon — no delivery pin, CAD parcel, or imagery available
- Project acreage
- Construction activity status
- EPC, PPA offtaker, financing
