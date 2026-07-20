# Dossier — Baird North Wind / Mesquite Sky (20INR0083)

Researched 2026-07-19 · site 32.4538, -99.4474 · verdict **real_active**

## 1. Verdict

- **real_active** — Project (BMP Wind LLC = Mesquite Sky) confirmed fully operational in January 2022 per [Clearway 10-K FY2021](sources/2022-02-28_sec_clearway_10k_2021_cwen.htm): "340 MW utility scale wind project…which achieved commercial operations in December 2021"
- Construction: **operating**, first activity ~2021-03 (road traces), full construction activity by 2021-05/06 ([frame](imagery/key/s2_2021-06_construction-active.png)), full COD January 2022
- Site: 32.4538, -99.4474 — thewindpower.net Mesquite Sky listing + SEC filings confirm Callahan County TX ([Google Maps](https://google.com/maps/@32.4538,-99.4474,5000m/data=!3m1!1e3))
- COD: reported 2026-12-31 → independent **already operational (2022-Q1)**, drift risk **not_applicable** (queue entry is an orphaned stale record)

## 2. Site identification

- Derivation: thewindpower.net Mesquite Sky listing (32°27'13.5"N, 99°26'50.5"W = 32.4538, -99.4474); Clearway SEC filings confirm Callahan County, TX
- **Stated project area: not obtained** — Callahan CAD portal JS-rendered (no static access); PUCT paywalled; area estimated ~2,000–5,000+ acres based on 23-turbine layout visible in imagery
- Cross-checks: [SEC 10-K](sources/2022-02-28_sec_clearway_10k_2021_cwen.htm) names Callahan County TX ✓; imagery shows wind farm strings centered near coordinate ✓; POI "68008 Latimer 345kV" is consistent with west Texas 345kV network
- Not obtainable: exact turbine coordinates (FAA OE portal returned 404); PUCT IA content (paywalled)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| BMP Wind LLC | SPV / ERCOT queue project company | [MIPA original](sources/2020-12-22_sec_clearway_ex10-3_mesquite-sky-mipa-original.htm) |
| Mesquite Sky TE Holdco LLC | Tax equity fund holding BMP Wind LLC | [MIPA original](sources/2020-12-22_sec_clearway_ex10-3_mesquite-sky-mipa-original.htm) |
| Mesquite Sky Holding LLC | Parent holding entity | [8-K 2022-01-18](sources/2022-01-18_sec_clearway_8k_mesquite-sky-mipa-amend1.htm) |
| Clearway Renew LLC | Original developer / seller | [8-K 2022-01-18](sources/2022-01-18_sec_clearway_8k_mesquite-sky-mipa-amend1.htm) |
| Clearway Energy, Inc. (CWEN) | 50% Class B buyer / current operator | [10-K FY2021](sources/2022-02-28_sec_clearway_10k_2021_cwen.htm) |
| Third-party investor | 50% Class A (undisclosed) | [10-K FY2021](sources/2022-02-28_sec_clearway_10k_2021_cwen.htm) |

- Financing: Class B: ~$62M; Class A: ~$2.4M per [First MIPA Amendment](sources/2022-01-18_sec_clearway_8k_mesquite-sky-mipa-amend1.htm); tax equity structure (Mesquite Sky TE Holdco LLC)
- PPAs: "Various" counterparties, 12-year weighted average contract life through 2033–2036 per [10-K FY2021](sources/2022-02-28_sec_clearway_10k_2021_cwen.htm)

## 4. Land & county records

- Tenure: **leased** — wind turbine lease agreements typical for utility-scale TX wind; no direct title search obtained
- Abatements: Ch.313 eligible (pre-2022); portal inaccessible — not confirmed or denied
- CAD: Callahan CAD portal JS-rendered — owner-name search for BMP Wind / Mesquite Sky returned no data via static fetch

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: 68008 Latimer 345kV; IA signed 2019-05-31
- IA content: not obtained (PUCT paywalled)

| IA document | Signed | Financial security posted |
|---|---|---|
| Interconnection Agreement | 2019-05-31 | not obtained |
| MIPA — Original ([pdf](sources/2020-12-22_sec_clearway_ex10-3_mesquite-sky-mipa-original.htm)) | 2020-12-21 | N/A (acquisition agreement) |
| MIPA — Amendment 1 ([8-K](sources/2022-01-18_sec_clearway_8k_mesquite-sky-mipa-amend1.htm)) | 2021-12-17 | $62M Class B + $2.4M Class A |

| Milestone | Actual |
|---|---|
| IA signed | 2019-05-31 |
| FIS approved | 2020-10-30 |
| Approved for energization | 2021-08-09 |
| Approved for synchronization | 2021-08-20 |
| Partial COD (14/23 turbines) | 2021-12 |
| Full COD (all 23 turbines) | 2022-01 |
| Commercial-operation-approved (ERCOT) | **never issued** (queue stale) |

- Queue-history COD drift (from [timeline.md](timeline.md)): 12 changes, 2020-12-15 → 2026-12-31 (current)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2020-06 | Pre-construction — undisturbed farmland/pasture, no roads or pads | [png](imagery/key/s2_2020-06_preconstruction.png) |
| 2021-03 | First faint road traces emerging (contact sheet) | [contact sheet](imagery/contact_sheet.png) |
| 2021-06 | Active construction — full road network + ~20 turbine pads, orange disturbed soil | [png](imagery/key/s2_2021-06_construction-active.png) |
| 2021-08–11 | Network complete, turbine installation progressing (contact sheet) | [contact sheet](imagery/contact_sheet.png) |
| 2022-01+ | Operational — roads and turbines mature, no active disturbance | [contact sheet](imagery/contact_sheet.png) |
| 2026-07 | Fully operational wind farm | [png](imagery/key/s2_2026-07_operational.png) |

- Verdict: **operating** — monthly timelapse (Jan 2020 → May 2022) shows clean baseline through 2020, first road traces ~2021-03, full construction 2021-05/06, infrastructure complete by late 2021 — exactly matching SEC-confirmed COD December 2021 / January 2022

## 7. COD assessment

- **Project is already fully operational** — COD occurred in January 2022 (final 45 MW / 9 turbines) per Clearway 10-K FY2021
- **Queue stale record**: ERCOT never issued `commercial-operation-approved` milestone, causing the queue to treat the project as pending. The 2026-12-31 reported COD is an administrative artifact drifted through 12 changes since original 2020-12-15 target
- **No construction risk**: 23 turbines operational; PPAs with investment-grade counterparties running to 2033–2036; project still in Clearway operating portfolio as of FY2025 ([10-K FY2025](sources/2026-02-24_sec_clearway_10k_2025_cwen.htm))
- **Independent estimate**: 2022-Q1 (actual); reported COD of 2026-12-31 has zero evidential basis
- **Drift risk**: not applicable — the drift reflects queue administration, not construction uncertainty

## 8. Could not determine

- Exact turbine coordinates / FAA OE ASN numbers (portal returned 404)
- PUCT IA content — milestone schedule, POI details, financial security amount (paywalled)
- Callahan County CAD parcel records — acreage, lease parcels (JS-rendered portal, no static access)
- Ch.313 tax abatement status (portal inaccessible, project predates JETI)
- Identity of the 50% Class A interest holder (undisclosed third party in SEC filings)
- Why ERCOT never issued commercial-operation-approved for an otherwise fully-milestoned project
