# Dossier — Chillingham Solar (23INR0070)

Researched 2026-07-20 · site 31.006, -97.262 · verdict **real_active**

## 1. Verdict

- **real_active** — plant is construction-complete and grid-synchronized; EIA status "Construction complete, not yet in commercial operation" for 8 consecutive months ([eia_history.json](eia_history.json))
- Construction: **substantially_complete** (EIA TS since Nov 2024; approved-for-synchronization Sep 4, 2024 per queue)
- Site: 31.006, -97.262 — EIA-860M coordinates, Bell County TX ([Google Maps](https://google.com/maps/@31.006,-97.262,5000m/data=!3m1!1e3)), confidence **medium** (satellite imagery not read this session — frame budget reserved)
- COD: reported 2026-08-31 → independent **2026-Q3**, drift risk **high** (10+ months post-sync with no COD approval; contractual deadline Sep 30, 2026)

## 2. Site identification

- Derivation: EIA-860M plant record (plant_id=68065, entity=Chillingham Solar LLC, Bell County, 350.0 MW) → [31.006, -97.262] ([factsheet.json](factsheet.json))
- **Stated project area: not obtained** — Ch.313 application for Academy ISD found but not read (frame budget); IA exhibits list no acreage explicitly
- Cross-checks: POI = Bell County East Switching Station, east side of Shaw Road, Bell County TX ([AR-SGIA Exhibit C](sources/2026-07-19_puct_35077-2251_amended-and-restated-standard-generation-interco.pdf)); Five Wells Solar Center (Operating, 30.99865, -97.25902) ~0.7 km away — same POI infrastructure region
- Not obtainable: exact switch coordinates (CEII); CAD parcel search not run

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Chillingham Solar LLC (fka 250LB 8ME LLC) | SPV | [AR-SGIA](sources/2026-07-19_puct_35077-2251_amended-and-restated-standard-generation-interco.pdf) |
| ENGIE North America | Operator/owner (current) | [AR-SGIA Exhibit D](sources/2026-07-19_puct_35077-2251_amended-and-restated-standard-generation-interco.pdf) — Eric Tarantino; assetman@engie.com |
| 8minute Solar Energy | Original developer (sold project) | [Original IA Exhibit D](sources/2026-07-19_puct_35077-1390_interconnection-agreement-between-oncor-electric.pdf) — Thomas Buttgenbach, President |
| Google | PPA offtaker | [saved html](sources/2026-07-19_engie-na_chillingham-google-ppa.html) (not read — artifact on disk) |

- Financing: irrevocable standby LCs — $3,088,904 posted by 2022-02-04; $6,979,820 posted by 2022-09-02; solar COD releases $6,793,389; remainder released on storage COD ([AR-SGIA §11.2](sources/2026-07-19_puct_35077-2251_amended-and-restated-standard-generation-interco.pdf))

## 4. Land & county records

- Tenure: **leased** (inferred — solar development standard; SPV is LLC shell)
- Abatements/agreements: Ch.313 application filed with Academy ISD, applicant "Chillingham Solar LLC f/k/a 250LB 8me LLC" ([factsheet.json](factsheet.json) ch313 hit) — application document not read
- CAD: not searched this session

## 5. Interconnection & contractual schedule

- POI: "Bell County East Switching Station on the east side of Shaw Road, Bell County, TX" at 345 kV dead-end structure; co-tenant transmission line jointly owned with Chillingham Storage LLC ([AR-SGIA Exhibit C](sources/2026-07-19_puct_35077-2251_amended-and-restated-standard-generation-interco.pdf))
- Equipment (AR-SGIA): 91 Sungrow SG4400UD-MV-US inverters × 4.4 MVA = 400.4 MVA gross, dispatched at 352.39 MW at 34.5 kV bus

| IA document | Signed | Financial security |
|---|---|---|
| Original SGIA ([pdf](sources/2026-07-19_puct_35077-1390_interconnection-agreement-between-oncor-electric.pdf)) | 2022-02-04 | $3,088,904 + $6,979,820 irrevocable LCs |
| Amendment No. 3 ([pdf](sources/2026-07-19_puct_35077-1985_amendment-no-3-to-the-standard-generation-interc.pdf)) | 2024-10-21 | Same amounts (unchanged) |
| Amended & Restated SGIA ([pdf](sources/2026-07-19_puct_35077-2251_amended-and-restated-standard-generation-interco.pdf)) | 2025-08-07 | Same amounts; ENGIE as operator |

| Milestone | Original IA (2022) | Amendment 3 (2024) | AR-SGIA (2025) |
|---|---|---|---|
| In-Service | 2023-05-11 | 2024-05-15 | 2024-05-15 |
| Trial Operation | 2023-05-22 | 2024-09-04 | 2024-09-06 |
| Scheduled COD | **2023-09-19** | **2024-12-31** | **2025-09-30** |

- Queue-history COD drift ([timeline.md](timeline.md)): 15 changes, 2023-06-01 → 2026-08-31

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | Not read (frame budget) | [s2_2026-07-01.png](imagery/s2_2026-07-01.png) |

- Verdict: **substantially_complete** (inferred from EIA TS status + sync approval Sep 2024 — satellite frame on disk, not read this session)

## 7. COD assessment

- Plant completed construction by late 2024 (EIA transitioned from ">50% complete" to "construction complete" Nov 2024); approved-for-synchronization Sep 4, 2024
- EIA planned COD has slipped 11 independent times Oct 2024 → Jun 2026 (latest) — diverges from queue's 2026-08-31 by ~2 months ([eia_history.json](eia_history.json))
- Contractual COD per controlling AR-SGIA (Aug 2025): **Sep 30, 2025** — plant is 10 months past its own contractual deadline
- Article 2.1.B termination trigger: Oncor may terminate if COD not achieved by **Sep 30, 2026** — 10 weeks away; creates material pressure to close
- Independent estimate: **2026-Q3** (Aug–Sep 2026). Rationale: ENGIE is a sophisticated operator with a live Google PPA; the plant is built and grid-synced; the Oncor termination trigger creates a hard forcing function. The pattern of sequential 1–3 month EIA slips suggests a protracted commissioning or regulatory holdout, not abandonment. Queue-reported 2026-08-31 is plausible given the Sep 30 Oncor deadline.
- Drift risk: **high** — 15 queue slips, 11 EIA slips, 10 months past contractual COD; however the Oncor termination trigger constrains the upside slip to Sep 2026 at most

## 8. Could not determine

- Exact reason for COD delay: construction is done and the plant is synced — what is blocking commercial operation (ERCOT testing, PPA commissioning, regulatory, internal ENGIE holdout)
- Satellite construction confirmation (frame on disk at imagery/s2_2026-07-01.png — not read due to token budget)
- Project area in acres (Ch.313 application on disk but not read)
- Whether Google PPA is active/fully executed (html source on disk, not read)
- Storage co-tenant COD status (23INR0079 — separate INR)
