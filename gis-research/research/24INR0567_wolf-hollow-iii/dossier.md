# Dossier — Wolf Hollow III (24INR0567)

Researched 2026-07-19 · site 32.434, -97.862 · verdict **real_early**

## 1. Verdict

- **real_early** — TCEQ air permit 175173 (8× GE 6B CTG, 352 MW SC) issued [2025-12-19](sources/2026-07-19_tceq_turbine-list-findings.md); no IA, no construction, no financing
- Construction: **no_activity** — imagery Jan 2025 and Jul 2026 show existing Wolf Hollow I+II complex unchanged; no laydown yard, grading, or turbine hall prep ([Jul 2026 frame](imagery/key/s2_2026-07-01_xwide.png))
- Site: 32.434, -97.862 — confirmed address [8787 Wolf Hollow Court, Granbury TX 76048](sources/2026-07-19_constellation_wolf-hollow-ii-iii-page.html) + S2 industrial footprint match ([satellite view](https://www.google.com/maps/@32.434,-97.862,5000m/data=!3m1!1e3))
- COD: reported 2027-05-31 → independent **2029-Q2**, drift risk **high** (no IA; 2 prior 18-mo slips; construction not started)

## 2. Site identification

- Derivation: confirmed street address 8787 Wolf Hollow Court, Granbury TX 76048 ([Constellation page](sources/2026-07-19_constellation_wolf-hollow-ii-iii-page.html)); industrial footprint (turbine buildings + Bitcoin mine container arrays) identified in S2 chip centered at 32.4390N, 97.8415W
- **Stated project area: unknown** — no abatement, IA, or CAD parcel document obtained; Hood CAD portal blocked; imagery footprint consistent with expansion at existing ~100-acre plant site
- Cross-checks: confirmed address (Constellation) + POI "Mitchell Bend 345KV" (Oncor; Comanche Peak–Wolf Hollow/Mitchell Bend 345kV line) + S2 industrial complex agree within <1 km
- Not obtainable: exact Mitchell Bend substation coordinates (no public geo source); gmaps 429 throughout; Nominatim returned empty for address

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Wolf Hollow II Power, LLC | TCEQ permit applicant / expansion SPV | [TCEQ turbine list](sources/2026-07-19_tceq_turbine-list-findings.md) |
| Constellation Energy Generation, LLC | developer/owner/operator | [Constellation page](sources/2026-07-19_constellation_wolf-hollow-ii-iii-page.html) |
| Constellation Energy Corporation | ultimate parent | [Constellation page](sources/2026-07-19_constellation_wolf-hollow-ii-iii-page.html) |

- Financing: **none confirmed** — TEF loan withdrawn March 2025 (Constellation cited permitting delays); no replacement financing or PPA announced ([Public Citizen Jan 2026](sources/2026-01-06_publiccitizen_tceq-approves-wolf-hollow-iii-permit.html))
- Note: ERCOT queue shows "Wolf Hollow III, LLC" as putative SPV — not confirmed in TX SOS or TX Comptroller search; TCEQ permit filed under Wolf Hollow II Power LLC

## 4. Land & county records

- Tenure: **owned** — expansion at existing Constellation-owned Wolf Hollow site (8787 Wolf Hollow Ct)
- Abatements/agreements: none — post-2022 project; Ch.313 expired; no JETI found; Hood County commissioners voted against project (Aug 2024) but have no permit veto power
- CAD: Hood CAD portal returned 403; no parcel data obtained for Wolf Hollow III expansion area specifically; existing plant parcels under Constellation/predecessors

## 5. Interconnection & contractual schedule

- No IA found — PUCT Interchange returned HTTP 402 throughout; ERCOT queue confirms `iaSigned = null` as of Jun 2026
- No PUCT docket for Wolf Hollow III IA identified

| IA document | Signed | Financial security posted |
|---|---|---|
| — (no IA) | — | — |

| Milestone | Status |
|---|---|
| Screening complete | 2023-09-01 |
| FIS requested | 2023-05-30 |
| FIS approved | — |
| IA signed | — |
| Scheduled COD | 2027-05-31 (ungrounded) |

- Queue-history COD drift ([timeline.md](timeline.md)): **2 slips** — 2024-11 → 2026-05 → 2027-05; each slip ~18 months; in reports since 2023-05 (38 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-01 | Existing Wolf Hollow I+II complex; no new construction or site prep | [2025-01](imagery/key/s2_2025-01-15_xwide.png) |
| 2026-07 | Same footprint; no change; no laydown yard, grading, or turbine hall visible | [2026-07](imagery/key/s2_2026-07-01_xwide.png) |

- Verdict: **no_activity** — 18 months between frames; existing plant unchanged; no construction commenced. Note: tight 2-km chips blocked (CDSE 403); 6-km resolution is the available baseline

## 7. COD assessment

- Reported 2027-05-31 is **not grounded** in any IA (no IA signed); it is ERCOT's internal claim only
- Two prior slips of ~18 months each (2024-11 → 2026-05 → 2027-05) already consumed >30 months
- Permit only issued Dec 2025; typical gas peaker pre-construction (IA finalization, equipment procurement, civil permits) takes 6-12 months before construction start; 18-month build thereafter
- TEF financing withdrawn; no replacement announced; capital uncertainty adds further risk
- GE 6B turbines (older simple-cycle model) have shorter lead times than HA/7F-class, but procurement to commissioning still requires ~18 months
- No EPC contract, no groundbreaking, no construction in imagery through Jul 2026
- **Independent estimate: 2029-Q2, drift risk high** — assumes IA signed late 2026, construction starts Q1 2027, 18-month build; could slip further if financing remains unresolved

## 8. Could not determine

- Exact Mitchell Bend 345kV substation coordinates (no public geo source; PUCT Interchange blocked)
- Wolf Hollow III, LLC registration details (TX SOS behind paywall; TX Comptroller search form requires interactive submission)
- Hood CAD parcel data for the expansion area (portal blocked)
- PUCT Interchange IA or any signed schedule documents (HTTP 402 throughout)
- Exact permit issue date disambiguation (Public Citizen cites "Dec 17, 2024"; TCEQ turbine list shows "2025-12-19" — treating turbine list as authoritative)
- EPC contractor or turbine order status
- Replacement financing structure post-TEF withdrawal
