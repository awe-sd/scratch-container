# Dossier — Space City Solar (21INR0341)

Researched 2026-07-20 · site 29.01384, -96.28571 · verdict **real_early**

## 1. Verdict

- **real_early** — signed SGIA (PUCT 35077-2398) with $34.66M LC and two PPAs (BASF + Enterprise Products); pre-construction as of 2026-07-01 with GIF energization target Oct 2026 ([SGIA Exhibit B](sources/2026-07-19_puct_35077-2398_ercot-standard-generation-interconnection-agreem.pdf))
- Construction: **pre_construction** — no clearing/grading visible in available imagery; no ERCOT construction start milestone; MIDANE substation not yet in OSM
- Site: 29.01384, -96.28571 — MIDANE Substation POI from signed SGIA Exhibit C, medium-high confidence ([satellite view](https://www.google.com/maps/@29.01384,-96.28571,5000m/data=!3m1!1e3))
- COD: reported 2027-06-01 → independent **2027-Q3 to 2028-Q1**, drift risk **high** (6 prior slips; no construction start yet; 9 months from SGIA signing to Phase 2 COD)

## 2. Site identification

- Derivation: SGIA Exhibit C states MIDANE Substation "located at or near 29°0'49.82"N 96°17'08.57"W in Wharton County, Texas" = 29.01384°N, -96.28571°W ([SGIA](sources/2026-07-19_puct_35077-2398_ercot-standard-generation-interconnection-agreem.pdf))
- **Stated project area: unknown** — no Ch.313 application found; WCAD search unavailable; acreage not in SGIA Exhibit C (size consistent with ~1,200–1,800 acres for 366+ MW but unconfirmed)
- Cross-checks: POI ~3.1 km WSW of CenterPoint Hillje Substation (OSM way/100064466, 29.030, -96.237) consistent with PUCT CCN 51568 "3.5-mile Route 3" transmission line; study area boundary from CCN testimony (FM441/CR330/CR307/SH71) encloses 29.01°N, -96.29°W; MIDANE not yet in OSM (consistent with pre-construction)
- Imagery at correct coordinates unavailable (CDSE credits exhausted); imagery at adjacent wrong center (29.030,-96.236) shows undisturbed agricultural fields at southern extent where MIDANE should be
- Warning: Aktina Solar (Hecate Energy, OSM way/1465121535, 29.068,-96.270) is a **different** 500 MW project also at Hillje — prior triage run confused the two; Aktina is confirmed operating since Dec 2023
- Not obtainable: exact parcel boundary, acreage; CEII-redacted substation drawings

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Apollo Solar Ranch, LLC | SPV (current) | party on [SGIA 2025](sources/2026-07-19_puct_35077-2398_ercot-standard-generation-interconnection-agreem.pdf); assigned Feb 22, 2024 |
| Space City Solar, LLC | SPV (original) | original SGIA Dec 15, 2020 ([PUCT 51568](sources/2026-07-19_puct_51568_32_1116825_IA.PDF)) |
| EDF Renewables Development, Inc. | Developer/operator | SGIA Exhibit D contacts: Jay Temple, 601 Travis St, Houston TX; operational contact OCCSupervisors@edf-re.com |
| BASF | PPA offtaker | 55 MWac PPA ~Dec 2020 ([t3_web_sweep](sources/t3_web_sweep.md)) |
| Enterprise Products Partners | VPPA offtaker | 100 MWac VPPA ([t3_web_sweep](sources/t3_web_sweep.md)) |

- Financing: not confirmed closed; $34.66M LC for TIF posted per [SGIA Exhibit E](sources/2026-07-19_puct_35077-2398_ercot-standard-generation-interconnection-agreem.pdf); factsheet shows `financial_security = "Yes"` as of 2026-06-01

## 4. Land & county records

- Tenure: **unknown** — no CAD parcels found (WCAD search.wcad.org returned 503); no deed/easement records obtained
- Abatements: **none found** — ch313.py returned no Ch.313 or JETI match for any variant of project/SPV name; absence may indicate direct county deal or unrecognized name variant
- CAD: 0 hits — WCAD offline; expected that leased land would show under landowner names, not the SPV
- Press reported "up to $30M in tax revenue" for EDF's Wharton projects, suggesting some county arrangement exists but not confirmed via public docs

## 5. Interconnection & contractual schedule

- POI per signed SGIA: MIDANE Substation (ERCOT site code MDN) at 29°0'49.82"N 96°17'08.57"W, 345kV interconnect to CenterPoint Hillje Substation ([SGIA Exhibit C](sources/2026-07-19_puct_35077-2398_ercot-standard-generation-interconnection-agreem.pdf))
- Equipment (Exhibit C): 175× SMA SC4200UP-US inverters, 3.484 MW each, 609.74 MW total planned; 34.5-345kV step-up transformers
- TIF security: $34,660,000 LC

| IA document | Signed | Financial security |
|---|---|---|
| Original SGIA ([pdf](sources/2026-07-19_puct_51568_32_1116825_IA.PDF)) | 2020-12-15 | unknown — doc not extracted |
| SGIA + Amendment One ([pdf](sources/2026-07-19_puct_35077-2398_ercot-standard-generation-interconnection-agreem.pdf)) | 2025-12-11 | $34,660,000 LC for TIF |

| Milestone | SGIA 2025 (Exhibit B) |
|---|---|
| GIF Energization | 2026-10-15 |
| Phase 1 COD (~260 MW) | 2027-01-15 (or +3mo after TIF In-Service) |
| Phase 2 COD (~350 MW) | 2027-06-30 |

- Queue-history COD drift ([timeline.md](timeline.md)): **6 changes**, 2021-12-01 → 2027-06-01; in reports since 2019-10-01 (81 snapshots)
- Capacity reduced from 609.74 MW → 366 MW in April 2025 queue update; SGIA Exhibit C still shows full 609.74 MW (likely reflects CenterPoint TIF sizing, not the reduced ERCOT queue figure)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | Undisturbed agricultural fields at MIDANE site coordinates; Aktina Solar array visible ~5km NE (different project, wrong center) | [xwide frame wrong center](imagery/s2_2026-07-01_array_xwide.png) |
| — | CDSE credits exhausted — no imagery at correct coordinates (29.014, -96.286) | — |

- Verdict: **pre_construction** — no grading, no clearing visible in available imagery; consistent with no ERCOT construction start milestone through June 2026

## 7. COD assessment

- Contractual Phase 2 COD June 30, 2027 matches the queue claim of 2027-06-01 — grounded in signed [SGIA Amendment One](sources/2026-07-19_puct_35077-2398_ercot-standard-generation-interconnection-agreem.pdf)
- **Against on-time delivery:** 6 prior COD slips (average ~6 months each); no construction start milestone triggered through June 2026; SGIA signed only Dec 2025 — leaves 9 months from IA execution to Phase 2 COD; FIS was never approved (non-standard queue path); no CAD/abatement records confirming land secured; project absent from EIA-860M (notable for a 366 MW project 17 months from claimed COD)
- **For:** $34.66M LC posted; two signed offtake agreements (BASF + Enterprise Products); EDF Renewables is an active developer with Wharton County presence; multi-phase project with earlier phases reportedly operating — precedent for site execution
- Comparison: GIF energization Oct 15, 2026 contractually requires TIF completion ~15 months from IA signing — aggressive but not impossible; 100 MW solar can break ground and COD in ~18 months under ideal conditions
- **Independent estimate: 2027-Q3 (optimistic) to 2028-Q1 (base case), drift risk HIGH**

## 8. Could not determine

- EPC contractor (no pins, no press release found; search backend down)
- Project area / acreage (no Ch.313 application, WCAD offline)
- Whether any land parcels have been acquired/leased under Apollo Solar Ranch (CAD offline)
- Financing close (no press release confirming project finance)
- Construction start date or any pre-NTP site preparation
- Exact parcel boundaries (no IA boundary exhibit; CEII)
- Whether earlier EDF phases at Hillje are under 21INR0341 or separate INRs (queue shows only 366 MW since April 2025)
- EIA-860M registration for Space City Solar / Apollo Solar Ranch (absent from current snapshot — may not yet have reported)
