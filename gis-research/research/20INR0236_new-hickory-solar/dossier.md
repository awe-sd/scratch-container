# Dossier — New Hickory Solar (20INR0236)

Researched 2026-07-19 · site unknown (Jackson County TX) · verdict **real_active**

## 1. Verdict

- **real_active** — [Ch.313 CDR 2023 actuals](sources/2026-07-19_comptroller_ch313_1460_cdr_2023.xlsx) show $175.1M total investment completed; Jackson CAD appraised qualified property at $114.1M in 2024, consistent with a completed 209 MW solar facility
- Construction: **substantially_complete** — full investment confirmed through 2023; [Amendment No.1](sources/2026-07-19_comptroller_ch313_1460_amended_agreement_1.pdf) states construction commenced Q4 2022; no imagery run (site not pinpointed)
- Site: Jackson County TX, Edna ISD — **county-level only**, no coordinates established; POI OLD_HCKRY_5 bus 5323 345 kV
- COD: reported 2026-10-26 → independent **2026-Q3 to 2027-Q2**, drift risk **med** (ERCOT commissioning queue blank despite full investment completed)

## 2. Site identification

- Derivation: county-level only — Jackson County TX, Edna ISD per [Ch.313 application](sources/2026-07-19_comptroller_ch313_1460_application.pdf) p.1,8
- **Stated project area: not obtained** — Ch.313 Tab 9 "Not Applicable"; no parcel IDs filed
- Application maps pp.23–24 show site layout (Pattern Energy, 11/25/2019) but are image-only, no coordinates
- Cross-checks: none — Google Maps 429 rate-limited; Overpass rate-limited; Nominatim no results; CAD owner search returned 0 hits for "solar"
- Not obtainable: parcel IDs, GPS coordinates, OLD_HCKRY_5 substation location (CEII-restricted), PUCT IA document (HTTP 402)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| New Hickory Solar LLC (f/k/a Old Hickory Solar LLC) | SPV (Delaware; TX SOS 0804475641) | [TX SOS cert](sources/2026-07-19_comptroller_ch313_1460_form772_2024.pdf) p.5 |
| Pattern Energy Group 2 LP (San Francisco) | Original developer | [Ch.313 App](sources/2026-07-19_comptroller_ch313_1460_application.pdf) p.14, dyann.blaine@patternenergy.com |
| Bridgelind Investments / Cole Johnson (Fort Worth TX) | Intermediate owner 2022 | [Biennial 2022](sources/2026-07-19_comptroller_ch313_1460_biennial_2022.xlsx) Tab #2 |
| Crayhill Capital Management (280 Park Ave, New York NY) | Current owner (dshlomi@crayhill.com) | [Amendment No.1](sources/2026-07-19_comptroller_ch313_1460_amended_agreement_1.pdf) p.3; [Biennial 2023](sources/2026-07-19_comptroller_ch313_1460_biennial_2023.xlsx) |

- Financing: unknown — no PPA or financing announcement found; Pattern Energy sold to CDPQ/CPP Investments in 2020; project changed hands at least twice since

## 4. Land & county records

- Tenure: **leased** — "option to lease the proposed project site from the current landowner" ([App](sources/2026-07-19_comptroller_ch313_1460_application.pdf) p.16)
- Abatements/agreements: Ch.313 App #1460 with Edna ISD, applied 2020-01-06, agreement executed 2022-03-21; limitation period 2026–2035; $142,200/yr supplemental payments ([Amendment No.1](sources/2026-07-19_comptroller_ch313_1460_amended_agreement_1.pdf))
- CAD: No parcel IDs returned under "solar" or "hickory" owner search — property may be registered under different entity name in Jackson CAD, or exempt parcels not surfaced by API

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: OLD_HCKRY_5 bus 5323 345 kV (no IA document retrieved; PUCT Interchange HTTP 402)
- Other projects on same 345kV line: Cachena Solar (23INR0027, Wilson Co.), Stockdale Solar (23INR0193, Wilson Co.) — confirms line is active corridor
- IA signed date per ERCOT queue: 2020-06-30

| IA document | Signed | Financial security |
|---|---|---|
| Original Agreement Edna ISD / Old Hickory Solar LLC ([pdf](sources/2026-07-19_comptroller_ch313_1460_agreement.pdf)) | 2022-03-21 | $25M limitation amount |
| Amendment No.1 Edna ISD / New Hickory Solar LLC ([pdf](sources/2026-07-19_comptroller_ch313_1460_amended_agreement_1.pdf)) | 2025-10-20 | $142,200/yr supplemental 2025–2033 |

| Milestone | Original (2020 app) | Amendment No.1 (Oct 2025) |
|---|---|---|
| Construction start | Q1 2021 | Q4 2022 |
| Commercial operations | June 2022 | Q1 2026 |
| Limitation period start | 2023-01-01 | 2026-01-01 |

- Queue-history COD drift (from [timeline.md](timeline.md)): 13 changes, 2021-05-21 → 2026-10-26 (~5.5yr slip)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| Not run | Site not pinpointed — no imagery acquired | — |

- Verdict: **no_imagery_run** — GPS coordinates not established; Google Maps and Overpass API both rate-limited during this session

## 7. COD assessment

- **Full investment ($175.1M) confirmed in 2023 CDR actuals** ([CDR 2023](sources/2026-07-19_comptroller_ch313_1460_cdr_2023.xlsx)); Jackson CAD appraised project at $114M in 2024 — strongest evidence of physical completion
- Amendment No.1 (Oct 2025) cites COO = Q1 2026; ERCOT queue as of Jun 2026 still shows all construction milestones blank — likely a commissioning/energization queue lag, not a construction failure
- Reported COD 2026-10-26 is plausible given evidence; real risk is ERCOT commissioning queue delay pushing to 2027
- 13 historical COD slips over 7 years; capacity bounced 4 times; project changed owners 3 times — structural instability but physical facility appears built
- Independent estimate: **2026-Q3 to 2027-Q2** — project is built but ERCOT commissioning status uncertain

## 8. Could not determine

- Site GPS coordinates (no parcel IDs, Google Maps rate-limited, Overpass rate-limited, substation location CEII-restricted)
- Satellite construction stage (imagery not run — depends on site coordinates)
- PUCT/ERCOT Interconnection Agreement document (PUCT Interchange returns HTTP 402)
- Current operational status in ERCOT (all ERCOT construction/COD milestones blank as of Jun 2026 despite $175.1M investment + $114M CAD appraisal)
- PPA counterparty and financing structure
- Acreage / exact lease area (Ch.313 Tab 9 "Not Applicable")
