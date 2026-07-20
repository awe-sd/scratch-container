# Dossier — Blue Skies BESS (25INR0046)

Researched 2026-07-19 · site ~31.8750, -96.8750 · verdict **real_early**

## 1. Verdict

- **real_early** — NextEra Energy Resources confirmed as developer via [Hill County abatement notice](sources/2026-07-19_hillcounty_hubbard-energy-storage-II-30day.pdf) (applicant: Hubbard Energy Storage II, LLC, 700 Universe Blvd, Juno Beach FL 33408 = NextEra HQ); IA signed Jun 2024; $115M capital committed
- Construction: **unclear** — candidate structure visible in [2km chip](imagery/s2_2026-07-01_structure_2km.png); chip coordinates not confirmed against parcel; first activity date unestablished
- Site: ~31.8750, -96.8750 — abatement site map (p.2 project star) + parcel 121422 in eastern Hill County near County Road 2423; medium confidence ([satellite view](https://www.google.com/maps/@31.8750,-96.8750,5000m/data=!3m1!1e3))
- COD: reported 2028-04-01 → independent **2028-Q3**, drift risk **high** (4 slips in 4 yrs; FIS still blank)

## 2. Site identification

- Derivation: [abatement site map p.2](sources/2026-07-19_hillcounty_hubbard-energy-storage-II-30day.pdf) — project star placed NW of Hubbard TX; p.3 shows ~10-acre tilted rectangular parcel on County Road 2423; parcel 121422 "PT OF NAVARRO CO SCH LAND A-673 TR 1 152.00 AC" in eastern Hill County, Malone ISD
- **Stated project area: 10 acres** per [Hill County abatement notice Aug 2024](sources/2026-07-19_hillcounty_hubbard-energy-storage-II-30day.pdf) — consistent with 306 MW BESS (compact pad); imagery footprint: unverified (chip coordinates not matched to parcel)
- Cross-checks: Ash Creek waterway at 31.9186, -96.8449 (Nominatim) — original project name "Ash Creek BESS" suggests proximity; SAM Switch on Lone Star 345kV CREZ line in Hill County ([PUCT docket 51016](sources/2026-07-19_puct_51016-2_lonestartx-samswitch-ccn.pdf)) near Hubbard TX — consistent with eastern Hill County location
- Not obtainable: exact parcel centroid (Hill CAD JS-only, session auth required); SAM Switch GPS coordinates (not in public documents)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| ACTX BESS Project LLC | SPV (ERCOT interconnecting entity) | ERCOT queue parquet `interconnectingFacility`; [TX COA](https://mycpa.cpa.state.tx.us/coa/) zip 85254 Scottsdale AZ |
| Hubbard Energy Storage II, LLC | SPV (county filing) | [Hill County abatement notice](sources/2026-07-19_hillcounty_hubbard-energy-storage-II-30day.pdf) — same project, different shell |
| NextEra Energy Resources | developer/owner | 700 Universe Blvd, Juno Beach FL 33408 in [abatement notice](sources/2026-07-19_hillcounty_hubbard-energy-storage-II-30day.pdf) = NextEra HQ address |
| EPC | unknown | not found |
| Offtaker | unknown | not found |

- Financing: not publicly confirmed; >$115M capital investment per [abatement notice](sources/2026-07-19_hillcounty_hubbard-energy-storage-II-30day.pdf)

## 4. Land & county records

- Tenure: **leased** — abatement notice p.1: "Reinvestment Zone is made up of leased parcels" ([doc](sources/2026-07-19_hillcounty_hubbard-energy-storage-II-30day.pdf))
- Abatements: Ch.312 Tax Abatement, Hill County Reinvestment Zone 018, Malone ISD, public hearing Aug 27, 2024; parcel 121422 (152-ac parent tract, 10-ac sublease for BESS) ([notice](sources/2026-07-19_hillcounty_hubbard-energy-storage-II-30day.pdf))
- CAD: Hill CAD portal requires JS session auth — parcel 121422 owner name not independently confirmed; `esearch.hillcad.org` API returned 404 on direct search endpoints

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: "68090 SAM SW 345kV" — SAM Switch on Lone Star Transmission Central A-to-Navarro 345kV CREZ line in Hill County ([PUCT docket 51016](sources/2026-07-19_puct_51016-2_lonestartx-samswitch-ccn.pdf))
- IA text: not retrieved — PUCT Interchange search for all LLC name variants (Blue Skies BESS, ACTX BESS, Hubbard Energy Storage, Ash Creek BESS) returned 0 hits; IA likely filed under TSP (Lone Star Transmission) not yet indexed or filed separately

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (not retrieved) | 2024-06-20 (ERCOT queue data) | unknown |

| Milestone | ERCOT queue (latest) |
|---|---|
| IA signed | 2024-06-20 |
| Meets 6.9(1) | 2025-02-12 |
| FIS approved | — (blank through 2026-06) |
| Meets all 6.9 | — |
| Scheduled COD | 2028-04-01 |

- Queue-history COD drift ([timeline.md](timeline.md)): **4 changes** — 2024-05 → 2025-03 → 2027-12 → 2028-04; in reports since 2022-04 (51 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | Candidate structure: dark rectangular blocks in regular rows at ~31.875, -96.875 consistent with BESS containers | [2km chip](imagery/s2_2026-07-01_structure_2km.png) |
| 2026-07-01 | 6km wide view: agricultural land E Hill County; small rectangular grid in SW quadrant | [6km wide](imagery/s2_2026-07-01_ashcreek_6km.png) |
| 2026-07-01 | Ash Creek area 2km: undisturbed farmland near creek | [ashcreek 2km](imagery/s2_2026-07-01_ashcreek_2km.png) |

- Verdict: **unclear** — structure visible in chip is consistent with BESS containers but chip coordinates not confirmed against parcel 121422; could be existing structure (shed/barn) or early BESS installation; no graded pad perimeter or substation visible; timelapse not run (site not confirmed)

## 7. COD assessment

- Reported 2028-04-01 is the latest queue COD; no signed IA exhibit with contractual milestone schedule retrieved
- **4 prior slips** over project's queue life: initial COD was 2024-05-15 (2022); slipped ~4 years over 4 years — consistent pattern of schedule pressure
- FIS approval blank through Jun 2026 snapshot despite FIS requested Apr 2022 — this is the primary schedule blocker; FIS approval triggers the construction milestone chain
- For: IA signed (Jun 2024), Meets 6.9(1) (Feb 2025), $115M capital committed, NextEra (largest US BESS developer) behind it, abatement approved (Aug 2024) — all indicate project intent is real
- Against: FIS still pending, no EPC or PPA identified, no construction start reported, imagery inconclusive
- **Independent estimate: 2028-Q3, drift risk high** — project is real but FIS delay makes 2028-04-01 optimistic; assume 3-6 month slip from reported COD given pattern

## 8. Could not determine

- Exact parcel centroid / lat-lon with high confidence (Hill CAD JS-auth blocks; abatement map not georeferenced)
- Whether the structure in `s2_2026-07-01_structure_2km.png` is this project (chip coordinates not matched to parcel 121422)
- Signed IA text, financial security amounts, contractual milestone schedule (PUCT Interchange returned 0 hits for all name variants)
- EPC contractor and offtaker/PPA
- FIS approval status and expected resolution date
- Whether ACTX BESS Project LLC and Hubbard Energy Storage II LLC are co-registered under a single NextEra parent entity
