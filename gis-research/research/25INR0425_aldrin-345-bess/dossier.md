# Dossier — Aldrin 345 BESS (25INR0425)

Researched 2026-07-19 · site 29.4602, -95.2580 · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed Jun-2024 + FIS approved Apr-2025 = real institutional milestones from CenterPoint Energy (TSP); no construction evidence as of Jul-2026
- Construction: **pre-groundbreaking**, no activity date (imagery unavailable — CDSE not configured)
- Site: 29.4602, -95.2580 — OSM way 583408103 (Meadow Substation, CenterPoint, 345kV/138kV), high confidence ([satellite view](https://www.google.com/maps/@29.4602,-95.2580,5000m/data=!3m1!1e3))
- COD: reported 2028-03-01 → independent **2028-Q4 to 2029-Q2**, drift risk **high** (no construction, no financing, 20-month window already tight)

## 2. Site identification

- Derivation: POI text "(Bus: 43030) Meadow 345kV substation" → Overpass API query → [OSM way 583408103](sources/2026-07-19_osm_meadow_substation.md): center 29.4602°N, 95.2580°W
- **Stated project area: <12 acres** per developer website ([aldrinenergystorage.com](sources/aldrin_energy_storage_website.md)) — no imagery to verify footprint; consistent with BESS adjacent to substation
- Cross-checks: OSM substation centroid ↔ POI text ↔ developer county (Brazoria) — all consistent; no parcel or news photo cross-check available
- Adjacent facility: North Alvin Substation ([OSM 174401064](sources/2026-07-19_osm_meadow_substation.md), TNMP, 138kV) immediately south-southeast
- Not obtainable: exact street address / parcel boundary; satellite imagery (CDSE blocked); Brazoria CAD parcel record (JS form, not accessible via WebFetch)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Aldrin Energy Storage LLC | SPV | copyright footer on [aldrinenergystorage.com](sources/aldrin_energy_storage_website.md) |
| Vesper Energy | developer/owner | [website](sources/aldrin_energy_storage_website.md) + [news page](sources/2026-07-19_vesperenergy_news_page.md) |
| Magnetar Capital | ultimate owner (2020 acquisition) | [vesperenergy.com/about](https://www.vesperenergy.com/about) |
| GCM Grosvenor | equity co-owner (2023) | vesperenergy.com/about |
| EPC contractor | unknown | not named anywhere |
| Offtaker / PPA | unknown | not announced |

- Financing: **not announced** — Vesper's most recent financing (Nazareth Solar, $236M, Jun 2026) makes no mention of Aldrin; [news page](sources/2026-07-19_vesperenergy_news_page.md) has zero BESS/Aldrin references

## 4. Land & county records

- Tenure: **owned** — website states "privately owned land" ([aldrinenergystorage.com](sources/aldrin_energy_storage_website.md))
- Abatements/agreements: none found. Ch.313 expired 2022; JETI registry not accessible. Expected for small BESS on owned parcel.
- CAD: 0 parcels found under "Aldrin" or "Vesper Energy" — Brazoria CAD (esearch.brazoriacad.org) requires JS form not accessible via WebFetch; negative search cannot be confirmed as exhaustive

## 5. Interconnection & contractual schedule

- POI per queue: "(Bus: 43030) Meadow 345kV substation" — CenterPoint Energy TSP
- IA signed 2024-06-15 per ERCOT queue milestone; PUCT Interchange blocked (HTTP 402), IA PDF text not retrieved
- Sibling project: **25INR0421 (Aldrin 138 BESS)** also in ERCOT queue at same Meadow substation (138kV level) — two interconnection requests submitted at same POI, suggesting ongoing configuration evaluation

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2024-06-15 (queue milestone only) | unknown — IA PDF not retrieved |

| Milestone | Queue record |
|---|---|
| In-Service | not obtainable (IA exhibits blocked) |
| Trial Operation | not obtainable |
| Scheduled COD | 2028-03-01 (ERCOT queue) |

- Queue-history COD drift ([timeline.md](timeline.md)): **2 changes** — 2025-07-15 (held 2023-05 → 2024-07) → 2027-12-01 (held 2024-08 → 2026-05) → 2028-03-01 (latest); total slip 2.7 years

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07 | no imagery obtained (CDSE credentials unavailable) | — |

- Verdict: **unknown** — CDSE blocked; no visual evidence of any construction stage; website and milestones suggest pre-groundbreaking

## 7. COD assessment

- Reported 2028-03-01 has drifted 2.7 years since first queue entry; two prior COD resets in 38 monthly snapshots
- BESS build time is 12-18 months; groundbreaking needed by ~Sep 2026 to reach 2028-03-01. No construction, no EPC named, no financing closed as of Jul-2026 — makes reported COD implausible without immediate action
- No public project profile: Vesper's news page has zero mentions of Aldrin; project absent from Vesper's portfolio page ([news source](sources/2026-07-19_vesperenergy_news_page.md))
- Meets all 6.9 conditions NOT achieved as of Jun-2026 despite 6.9(1) met Feb-2025 — unknown blocking condition
- Capacity discrepancy (550 MW website vs 362 MW queue) and stale "end 2025" target suggest developer has not actively updated project communications
- Positive signals: IA signed, FIS approved, 6.9(1) met — institutional process progressed; Vesper is credible developer (Hornet Solar operational, Nazareth financed)
- **Independent estimate: 2028-Q4 to 2029-Q2, drift risk high** — barring an unannounced financing close and immediate mobilization

## 8. Could not determine

- Satellite/imagery evidence of site (CDSE credentials not functional in this environment)
- IA PDF contents (PUCT Interchange 402-blocked; POI text, milestone exhibits, financial security amount unknown)
- EPC contractor or offtake agreement
- TX SOS / Comptroller entity details (paid portal)
- Brazoria CAD parcel record (JS form inaccessible)
- Exact trigger for "Meets all 6.9" not yet achieved
- Whether 25INR0421 (Aldrin 138 BESS) will proceed in parallel or one project will be abandoned
