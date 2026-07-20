# Dossier — NRG Greens Bayou 6 (TEF-Due Diligence) (24INR0410)

Researched 2026-07-19 · site 29.82052, -95.22032 · verdict **real_active**

## 1. Verdict

- **real_active** — NRG Energy 10-K FY2025 (SEC) explicitly: "NRG Greens Bayou 6 LLC…entered into the Third TEF Loan to support the development of Greens Bayou 6, which is currently under construction"; $112M drawn on $370M TEF loan as of Q1 2026 ([10-K excerpts](sources/2026-07-19_sec_nrg-2025-10k-greens-bayou-excerpts.txt))
- Construction: **under_construction**, first activity date not pinned (brownfield addition; compact CT footprint invisible at S2 10m)
- Site: 29.82052, -95.22032 — Google Places pin "NRG Energy - Greens Bayou Plant, 12070 Old Beaumont Hwy, Houston TX 77049"; brownfield addition to existing 327 MW NRG plant ([satellite view](https://www.google.com/maps/@29.82052,-95.22032,5000m/data=!3m1!1e3))
- COD: reported 2028-05-01 → independent **2028-Q2**, drift risk **medium** (3 prior slips; active TEF disbursements constrain schedule)

## 2. Site identification

- Derivation: Google Places pin for existing "NRG Energy - Greens Bayou Plant" — Unit 6 is a brownfield addition to this site ([contact sheet](imagery/contact_sheet.png))
- **Stated project area: not obtainable** — HCAD search blocked; no abatement filed; brownfield CT footprint ~10-30 acres within existing plant boundary (unverified)
- Cross-checks: Google Places pin 29.82052, -95.22032 matches NRG 10-K plant asset table "Greens Bayou, ERCOT, Fossil, Natural Gas, TX, 327 MW" — same site; Sentinel-2 June 2026 shows large industrial complex consistent with active power plant
- Not obtainable: exact substation/POI tap coordinates (CEII); parcel boundaries; TCEQ facility number

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| NRG Greens Bayou 6 LLC | SPV/project entity | [10-K excerpts](sources/2026-07-19_sec_nrg-2025-10k-greens-bayou-excerpts.txt) |
| NRG Energy, Inc. (NYSE: NRG) | indirect parent + guarantor | [10-K excerpts](sources/2026-07-19_sec_nrg-2025-10k-greens-bayou-excerpts.txt) |
| GE Vernova (GEV) | turbine supplier (strategic partner) | [Q3 2025 10-Q](https://www.sec.gov/Archives/edgar/data/1013871/000101387125000025/nrg-20250930.htm) |
| Kiewit/TIC | EPC contractor | [Q3 2025 10-Q](https://www.sec.gov/Archives/edgar/data/1013871/000101387125000025/nrg-20250930.htm) |
| PUCT (Texas Energy Fund) | lender | [10-K excerpts](sources/2026-07-19_sec_nrg-2025-10k-greens-bayou-excerpts.txt) |

- Financing: $370M TEF loan signed 2025-11-20 at 3.000% fixed, due 2045; NRG corporate equity contribution agreement and guaranty. $112M drawn by Q1 2026 (~30% of total loan).

## 4. Land & county records

- Tenure: **existing plant site** — Unit 6 is a brownfield addition to existing NRG Greens Bayou plant (327 MW NRG-owned facility per 10-K plant table)
- Abatements/agreements: no Ch.313 or JETI found (expected — new gas units ineligible for Ch.313 post-2022 expiry; JETI not confirmed)
- CAD: HCAD search blocked (HTTP 403); parcel records not retrieved. Underlying land is NRG-owned/controlled (existing plant)

## 5. Interconnection & contractual schedule

- POI per queue data: "Greens Bayou Substation, 138 kV" — PUCT IA filing not retrieved (portal blocked); IA signed 2025-02-07 per ERCOT queue
- Equipment: 443 MW natural gas-fueled peaker (simple-cycle); turbine vendor GE Vernova (specific model unconfirmed for peaker)

| IA document | Signed | Financial security posted |
|---|---|---|
| Interconnection Agreement (Greens Bayou Sub, 138 kV) | 2025-02-07 | Not retrieved (PUCT blocked) |
| PUCT TEF Loan Agreement ([excerpt](sources/2026-07-19_sec_nrg-2025-10k-greens-bayou-excerpts.txt)) | 2025-11-20 | $370M loan at 3%; NRG equity guaranty |

| Milestone | Status |
|---|---|
| IA signed | 2025-02-07 |
| FIS approved | 2025-08-14 |
| TEF due diligence approved | 2025-03-13 |
| TEF loan signed | 2025-11-20 |
| Commercial operation (NRG guidance) | mid-2028 |

- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** — 2024-12-31 → 2025-06-01 → 2026-06-02 → 2028-05-01; in reports since 2022-08 (47 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-06 | Existing large industrial complex; no new earthworks/cranes visible at 10m | [center chip](imagery/s2_center_2026-06-01.png) |
| 2026-06 | Contact sheet (5-panel): dense urban-industrial area; no clearing signature | [contact sheet](imagery/contact_sheet.png) |

- Verdict: **construction not visible** — brownfield peaker CT addition; compact footprint (≤30 acres) within existing plant boundary is below the reliable detection threshold at Sentinel-2 10m resolution; confirmed under construction by SEC filings

## 7. COD assessment

- Reported 2028-05-01 is consistent with NRG's own public guidance ("mid-2028") repeated across 10-K, Q3 2025, and Q1 2026 10-Q — stable, not drifting further as of most recent filing
- TEF loan disbursement pace ~$22M/month (Jan–Mar 2026) on a $370M total = roughly 18-month draw schedule, consistent with mid-2028 target
- TEF loan due 2045 with NRG corporate guaranty — strong financial commitment; abandonment cost is high
- Risk factors: NRG 10-K cites "elevated inflation, supply chain disruption and changing tariff and trade policies" as construction cost risks; 3 prior COD slips before construction start signal historical schedule optimism
- No construction-start milestone reported in ERCOT queue (as of 2026-06 snapshot) — minor flag; SEC evidence overrides queue silence
- **Independent estimate: 2028-Q2, drift risk medium** — NRG guidance matches contracted schedule, financing disbursing on track, but tariff/supply risk and brownfield site complexity could push to 2028-Q3/Q4

## 8. Could not determine

- TCEQ NSR air permit number or status (portals session-gated; permit must exist for active construction)
- PUCT IA document details (portal blocked; financial security amount, exact POI bus, milestone schedule in IA)
- HCAD parcel records / project acreage (portal blocked)
- Specific turbine model for the peaker unit (GEV is NRG's primary turbine partner; model unspecified)
- Satellite construction start date (brownfield CT below S2 detection threshold; CDSE credentials unavailable)
