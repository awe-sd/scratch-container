# Dossier — Goodnight Wind II (23INR0637)

Researched 2026-07-19 · site 34.937162, -101.4339 · verdict **real_active**

## 1. Verdict

- **real_active** — EIA Form 860M (May 2026) status: "Under construction, ≤50% complete"; Planned Operation May 2027 ([EIA 860M](sources/2026-07-19_eia860m_may2026_goodnight-wind-ii.xlsx))
- Construction: **clearing/early construction**, first activity unknown (CDSE unavailable this session)
- Site: 34.937162, -101.4339 — EIA 860M primary regulatory filing by owner FGE Goodnight II LLC, **high** confidence ([map](https://google.com/maps/@34.937162,-101.4339,5000m/data=!3m1!1e3))
- COD: reported 2027-06-06 → independent **2027-Q3**, drift risk **high** (7 slips in 3.5 yrs; Amendment 3 de-risked 2028 start)

## 2. Site identification

- Derivation: EIA Form 860M May 2026 — Plant ID 69403, filed by project owner FGE Goodnight II LLC ([EIA 860M](sources/2026-07-19_eia860m_may2026_goodnight-wind-ii.xlsx))
- **Stated project area: not retrieved** — Armstrong CAD portal JS-blocked; original Ch.313 agreement (App 1507) returned HTTP 403
- Cross-checks: EIA coordinate (34.937, -101.434) at Palo Duro Canyon escarpment edge; turbine array extends onto flat plateau to north. Sister project Goodnight I (EIA Plant 59246) at 35.094, -101.326 — operating April 2024, ~17 km NNE. Both in Armstrong County, consistent with Ch.313 App 1507 and PR Newswire.
- Not obtainable: exact POI switch coords for 345kV Alibates–Tule Canyon CKT2; FAA OE/AAA turbine coord filings (portal shutdown)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| FGE Goodnight II, LLC (TX TIN 32064194957) | SPV | [Ch.313 Amend 3](sources/2026-07-19_comptroller_ch313_1507-fge-goodnight-ii-amend3.pdf) |
| FGE Power LLC (Austin TX; Emerson G. Farrell, Founder) | Original developer | [PR Newswire 2022-07-18](sources/2026-07-19_prnewswire_fge-goodnight-sale-to-omega.html) |
| Omega Energia / Serena Energia (São Paulo, Brazil; CEO Antonio Bastos Filho) | Current owner (acquired July 2022) | [PR Newswire 2022-07-18](sources/2026-07-19_prnewswire_fge-goodnight-sale-to-omega.html) |
| IEA (Infrastructure and Energy Alternatives) | EPC (Phase I; Phase II unconfirmed) | [PR Newswire](sources/2026-07-19_prnewswire_fge-goodnight-sale-to-omega.html) |

- Turbines: Vestas V136-4.5MW (confirmed for Phase I; Phase II unconfirmed from available sources)
- Financing: Acquisition by Omega enabled "simultaneous construction commencement" on Phase I; Phase II is follow-on. Tax equity/debt structure unknown.

## 4. Land & county records

- Tenure: **unknown** — Armstrong CAD JS-blocked; Armstrong County deed records not retrieved
- Abatements/agreements: Ch.313 App 1507 (Claude ISD / FGE Goodnight II LLC), original Dec 10 2020, amended 3× ([Amend 3](sources/2026-07-19_comptroller_ch313_1507-fge-goodnight-ii-amend3.pdf)) — $20M appraisal limitation for 10 years starting Jan 1 2028; project area in Armstrong County (no acreage stated in Amendment 3)
- CAD: owner-name search for "Goodnight" and "FGE" — 404 errors on direct URL; portal requires JS-driven form submission. No parcel IDs retrieved.

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: tap 345kV 23900 Alibates – 23914 Tule Canyon CKT2 (identity packet; no signed IA retrieved — PUCT Interchange returned HTTP 402)
- ERCOT queue IA signed date: 2019-08-18 (anomalous — predates 2023 INR by ~4 years; possibly legacy IA from predecessor filing; unresolved)

| IA document | Signed | Financial security posted |
|---|---|---|
| Ch.313 Agreement App 1507 — Original ([503 Access Denied — not retrieved](sources/)) | 2020-12-10 | not retrieved |
| Ch.313 Amendment 1 | 2023-03-20 | not retrieved |
| Ch.313 Amendment 2 | 2024-10-21 | not retrieved |
| Ch.313 Amendment 3 ([pdf](sources/2026-07-19_comptroller_ch313_1507-fge-goodnight-ii-amend3.pdf)) | 2026-03-24 | not stated |

| Milestone | Amendment 3 (Mar 2026) |
|---|---|
| Tax Limitation Period starts | January 1, 2028 |
| Tax Limitation Period ends | December 31, 2037 |
| Final Termination | December 31, 2042 |

- Queue-history COD drift (from [timeline.md](timeline.md)): 7 changes, 2023-12-30 → 2027-06-06 (3.5-year rightward slide)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-06 | Phase II EIA coord at canyon escarpment edge; flat plateau visible but no turbine pads confirmed at 6km res | [png](imagery/s2_2026-06-15.png) |
| 2026-06 | Phase I (operating) comparison: turbine access road network clearly visible across farmland | [png](imagery/s2_phaseI_2026-06-15.png) |

- Verdict: **early construction** per EIA 860M ("≤50% complete"); satellite chips show correct terrain but turbine pads not resolved at available resolution. CDSE auth failed mid-session; additional plateau chips not obtained.

## 7. COD assessment

- Ch.313 Amendment 3 (March 2026) extended Tax Limitation start to **Jan 1, 2028** — the parties themselves built in a post-2027 buffer, treating the 2027 COD as the floor, not the ceiling
- EIA 860M (May 2026) reports "Planned Operation May 2027" with "≤50% complete" status — leaves 12 months to cross ≥50%, install turbines, energize and test
- 7 COD slips averaging ~6 months each; the most recent target (2027-06-06) has drifted from an original 2023-12-30
- FIS was approved only 2026-06-15 — less than 13 months before claimed COD
- No ERCOT construction start milestone; no turbine delivery announcements found
- Independent estimate: **2027-Q3** at earliest; 2028-Q1 more defensible given amendment buffer and pace of slippage
- Drift risk: **HIGH** — pattern of consistent delay, recent amendment de-risking a 2028 start

## 8. Could not determine

- Project acreage (Armstrong CAD portal blocked; original Ch.313 agreement inaccessible)
- Exact turbine layout / FAA OE/AAA filings (portal government-shutdown notice)
- PUCT signed IA (Interchange portal returned HTTP 402)
- Land tenure (lease vs. purchase)
- EPC contractor for Phase II (Phase I was IEA; Phase II unconfirmed)
- IA anomaly resolution (2019-08-18 IA date vs. 2023 INR)
- Construction start date / first grading visible (CDSE auth failure)
