# Dossier — Echols Grove Solar (25INR0368)

Researched 2026-07-20 · site 33.6114, -95.4451 · verdict **real_early**

## 1. Verdict

- **real_early** — two CONFIRMED IAs on disk, LC escalating from $8.6M → $11.7M, Google Places pin at site, EIA plant record at matching coords ([IA original](sources/2026-07-20_puct_35077-2030_standard-generation-interconnection-agreement-be.pdf), [Amendment 1](sources/2026-07-20_puct_35077-2335_amendment-no-1-to-the-standard-generation-interc.pdf))
- Construction: **pre_construction** — EIA status "(L) Regulatory approvals pending. Not under construction" as of May 2026; no imagery obtained (CDSE unavailable)
- Site: 33.6114, -95.4451 — Google Places pin + EIA plant record convergence, high confidence ([satellite view](https://www.google.com/maps/@33.6114,-95.4451,5000m/data=!3m1!1e3))
- COD: reported 2027-04-03 → independent **2028-Q1–Q2**, drift risk **high** (EIA says 2028-12, no construction start, 5 prior slips)

## 2. Site identification

- Derivation: Google Places pin "Echols Grove Solar" at **3018 U.S. Hwy 271 S, Paris TX 75462** (33.611368, -95.445060) — delivery/gate pin on US-271 south of Paris; corroborated independently by EIA-860M plant 68902 "Echols Creek Solar" @ 33.61647, -95.45837 (~1.3 km)
- **Stated project area: not found** — no abatement doc, no CAD results obtained; Lamar CAD not queried
- Cross-checks: Google pin ↔ EIA-860M agree within 1.3 km on US-271 S corridor; IA POI names Hawk Hollow #11768 – Lamar Blossom #11770 line (Lamar County) — consistent with site 5 km south of Paris TX
- Not obtainable: exact Click Creek Switch coordinates (CEII-redacted in IA Exhibit C), exact parcel boundaries

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Echols Grove, LLC (fka BT Ferguson Solar, LLC) | SPV | party on [IA Amendment 1](sources/2026-07-20_puct_35077-2335_amendment-no-1-to-the-standard-generation-interc.pdf); rename from BT Ferguson Solar per Amendment item 2 |
| BT Ferguson Solar, LLC | Original SPV (renamed) | party on [original IA](sources/2026-07-20_puct_35077-2030_standard-generation-interconnection-agreement-be.pdf); [EIA plant 68902](eia_history.json) entity name |
| Ignacio Fuentes, VP | Amendment signatory | [Amendment No. 1 p3](sources/2026-07-20_puct_35077-2335_amendment-no-1-to-the-standard-ge_p3.png) |
| Developer | unknown | zero web presence; all search.py queries failed |

- Financing: no public financing announcement found; LC posted ($8.6M → $11.7M) confirms financial commitment

## 4. Land & county records

- Tenure: **unknown** — no CAD parcel query; IA Exhibit C references land conveyance to TSP for Click Creek Switch but no land ownership detail visible
- Abatements/agreements: **none found** — Ch.313 ineligible (post-2022); ch313.py 0 hits; JETI search failed
- CAD: not queried

## 5. Interconnection & contractual schedule

- POI per signed IA: "Click Creek Switch … Hawk Hollow Switch – Lamar Blossom Sub – Tenaska Switch 138 kV line … Lamar County, Texas" ([Amendment Exhibit C](sources/2026-07-20_puct_35077-2335_amendment-no-1-to-the-standard-ge_p7.png)) — matches queue POI exactly
- Equipment: 64× SUNGROW SG3600UD-MV inverters, 201.15 MW net ([Amendment Exhibit C](sources/2026-07-20_puct_35077-2335_amendment-no-1-to-the-standard-ge_p7.png)); co-located storage 25INR0369 (100.57 MW) REMOVED in Amendment

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-20_puct_35077-2030_standard-generation-interconnection-agreement-be.pdf)) | 2024-12-05 | **$8,596,091** Irrevocable Standby LC (due 2024-12-06) |
| Amendment No. 1 ([pdf](sources/2026-07-20_puct_35077-2335_amendment-no-1-to-the-standard-generation-interc.pdf)) | 2025-12-07 | **$11,711,125** Irrevocable Standby LC (due 2025-12-09) — +36%; storage removed |

| Milestone | Original IA (2024) | Amendment 1 (2025) |
|---|---|---|
| In-Service | 2026-12-03 | 2026-12-03 |
| Trial Operation | 2027-01-03 | 2027-01-03 |
| Scheduled COD | 2027-04-03 | 2027-04-03 |

- Queue-history COD drift ([timeline.md](timeline.md)): **5 changes** — 2025-12-09 → 2025-12-31 → 2026-04-15 → 2026-12-31 → 2027-10-13 → 2027-04-03; in reports since 2023-03 (40 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07 | No imagery obtained — CDSE openEO returned 402 (no compute credits) on all attempts | — |

- Verdict: **pre_construction** — confirmed by EIA-860M status "(L) Regulatory approvals pending. Not under construction" as of May 2026; no visual confirmation available

## 7. COD assessment

- Reported 2027-04-03 = contractual Scheduled COD in both original IA and Amendment No. 1 — dates unchanged across the amendment; grounded in a signed Oncor agreement
- **EIA divergence**: EIA-860M plant 68902 reports planned COD **2028-12** for 12 consecutive months (Jun 2025 → May 2026), vs queue 2027-04 — **8-month gap**; EIA status "not under construction" throughout ([eia_history.json](eia_history.json))
- FIS approved only **2026-06-18** (very recent) — procurement, permitting, and all construction remain; In-Service date Dec 3, 2026 is ~5 months from research date with no ground broken
- COD history shows 5 slips over 3 years (2025-12 → 2027-04); each slip 3–9 months; pattern of slippage to continue
- LC escalation ($8.6M → $11.7M) and fresh Amendment show developer remains committed; project is real but schedule is aspirational
- **Independent estimate: 2028-Q1–Q2**, drift risk **high**

## 8. Could not determine

- Developer parent company / ultimate owner (zero web presence; all search backends failed)
- Exact Click Creek Switch / TIF coordinates (CEII-redacted)
- Project acreage (no abatement doc, no CAD query)
- EPC contractor
- Offtake/PPA counterparty
- Satellite construction status (CDSE unavailable this run)
- Lamar CAD parcel records (no query performed)
