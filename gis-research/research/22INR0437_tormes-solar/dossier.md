# Dossier — Tormes Solar (22INR0437)

Researched 2026-07-19 · site 32.06334, -96.59314 · verdict **real_active**

## 1. Verdict

- **real_active** — groundbreaking May 19, 2026 ([CRO article](sources/2026-07-19_constructionreviewonline_tormes-solar-groundbreaking.html)); $1.3B portfolio financing closed with MUFG/HSBC/Nomura/Santander ([financing article](sources/2026-07-19_constructionreviewonline_matrix-renewables-financing.html))
- Construction: **clearing** (early civil works), first activity **2026-05-19** ([groundbreaking photo](sources/2026-07-19_matrix-renewables_tormes-groundbreaking-photo.jpg))
- Site: 32.06334, -96.59314 — OSM generation substation on Oncor Navarro–Watermill 345kV line, med confidence ([satellite view](https://www.google.com/maps/@32.06334,-96.59314,5000m/data=!3m1!1e3))
- COD: reported 2027-03-31 → independent **2027-Q2**, drift risk **medium** (3 prior slips; FIS just approved Jun 2026)

## 2. Site identification

- Derivation: OSM way 1087366819 (generation substation, 345kV) at 32.06334, -96.59314 on Oncor Navarro–Watermill line; consistent with article "two miles SE of Barry" (~3 km SE of Barry centroid 32.099, -96.636)
- **Stated project area: not obtained** — no CAD or abatement doc retrieved; 457 MWdc implies ~2,300–4,100 acres
- Cross-checks: OSM substation lat/lon ↔ "SE of Barry" description — agree within ~1 km; POI "tap 345kV 1906 Venus - 68091 Navarro" matches Navarro terminal on this line
- Not obtainable: exact POI tap coordinates (CEII); parcel IDs/acreage (Navarro CAD portal inaccessible); Sentinel-2 imagery (CDSE credentials invalid); Google Places pin (quota exhausted)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Tormes Solar, LLC | SPV | ERCOT GIS queue; PUCT docket 207063 (IA, signed 2024-04-10) |
| Matrix Renewables | developer/owner | [CRO groundbreaking article](sources/2026-07-19_constructionreviewonline_tormes-solar-groundbreaking.html) |
| TPG Rise | parent/backer of Matrix Renewables | [CRO groundbreaking article](sources/2026-07-19_constructionreviewonline_tormes-solar-groundbreaking.html) |
| SOLV Energy | EPC contractor | [CRO groundbreaking article](sources/2026-07-19_constructionreviewonline_tormes-solar-groundbreaking.html) |
| First Solar | module supplier | [CRO financing article](sources/2026-07-19_constructionreviewonline_matrix-renewables-financing.html) |
| MUFG, HSBC, Nomura, Santander | construction-to-term lenders | [CRO financing article](sources/2026-07-19_constructionreviewonline_matrix-renewables-financing.html) |
| DESRI | preferred equity | [CRO financing article](sources/2026-07-19_constructionreviewonline_matrix-renewables-financing.html) |

- Financing: non-recourse portfolio financing closed ~Jun 2026 — $470M+ construction-to-term, ~$400M tax equity bridge, ~$100M LCs, $210M DESRI preferred equity; domestic content qualification via First Solar ([financing article](sources/2026-07-19_constructionreviewonline_matrix-renewables-financing.html))
- PPA offtaker: not identified in available sources

## 4. Land & county records

- Tenure: **likely leased** — article references "landowner lease income" ([CRO](sources/2026-07-19_constructionreviewonline_tormes-solar-groundbreaking.html)); no deed purchase found
- Abatements/agreements: not found — Navarro CAD portal DNS not resolving; TX Comptroller Ch.313/JETI JSON endpoint returned no data; county commissioners court website non-responsive
- CAD: 0 hits — Navarro CAD portal inaccessible via automated fetch (navarro-cad.org DNS failure; navarro.prodigycad.com SPA API authentication required)

## 5. Interconnection & contractual schedule

- POI per queue: "tap 345kV 1906 Venus - 68091 Navarro" — Oncor Navarro–Watermill 345kV line; OSM confirms generation substation at 32.063, -96.593
- IA: PUCT docket 207063, signed **2024-04-10** (from queue timeline); document text not retrieved (PUCT Interchange returned 402)
- FIS approved: **2026-06-23** (very recently, per queue timeline)

| IA document | Signed | Financial security posted |
|---|---|---|
| IA (PUCT 207063) | 2024-04-10 | Unknown — doc not retrieved |

| Milestone | Queue-reported |
|---|---|
| Scheduled COD | 2027-03-31 |
| IA signed | 2024-04-10 |
| FIS approved | 2026-06-23 |

- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** — 2023-12-15 → 2025-09-04 → 2027-05-31 → 2027-03-31; in reports since 2021-07 (60 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-05-19 | Groundbreaking ceremony — open farmland visible | [photo](sources/2026-07-19_matrix-renewables_tormes-groundbreaking-photo.jpg) |
| 2026-07 | Satellite imagery unavailable (CDSE credentials invalid) | — |

- Verdict: **clearing** inferred — groundbreaking May 2026 with EPC mobilized; no satellite confirmation of grading extent; Sentinel-2 and Google Static Maps API unavailable this session

## 7. COD assessment

- Reported 2027-03-31 is consistent with Matrix Renewables' publicly stated **H1 2027** target ([financing article](sources/2026-07-19_constructionreviewonline_matrix-renewables-financing.html))
- Financing closed ~Jun 2026 is a strong commitment signal: four arranging banks, DESRI equity, domestic content qualification via First Solar
- FIS approved only **2026-06-23** — just 6 weeks before today; interconnection build-out clock now running; ~10 months to Mar 2027 COD is tight for a 457 MWdc project
- Three prior COD slips (2023-12 → 2025-09 → 2027-03) show ~3-year total history of delay; most recent slip was 7 months
- Risk: construction start was May 2026; 457 MWdc with First Solar modules is a large build; 10 months is compressed; Q2 2027 (Jun 2027) is the more likely endpoint
- **Independent estimate: 2027-Q2, drift risk medium** — financing closed, EPC on site, but compressed schedule and recently-approved FIS

## 8. Could not determine

- PPA offtaker (not mentioned in any retrieved source)
- Exact parcel IDs/acreage (Navarro CAD inaccessible)
- Ch.313/JETI abatement agreement details (TX Comptroller JSON unavailable)
- IA financial security amount (PUCT doc not retrieved — 402 error)
- Satellite-confirmed construction stage (CDSE credentials invalid; Google Maps quota exhausted)
- Registered agent / mailing address for Tormes Solar, LLC (TX SOS requires paid login; TX Comptroller search needs JavaScript)
- Exact POI tap coordinates (CEII-redacted)
