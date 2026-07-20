# Dossier — Pintail Pass BESS (24INR0302)

Researched 2026-07-19 · site 28.04441, -97.43821 · verdict **real_active**

## 1. Verdict

- **real_active** — compact gravel pad + white structures at Angstrom substation visible in [2026-07-01 Sentinel-2](imagery/key/s2_2026-07-01_xwide.png); all ERCOT late-stage gates cleared
- Construction: **substantially_complete**, first activity date not determinable (only 2026-07 imagery available; substation built 2022 per [OSM](sources/2026-07-19_osm_angstrom-substation.json))
- Site: 28.04441, -97.43821 — OSM polygon centroid of Angstrom Substation ([way 1089997597](https://www.openstreetmap.org/way/1089997597)), confirmed AEP-operated 345 kV switching substation, San Patricio County. ([map](https://google.com/maps/@28.04441,-97.43821,3000m/data=!3m1!1e3))
- COD: reported 2026-07-24 → independent **2026-Q3**, drift risk **med** (9 prior slips; 5-day window extremely tight but all gates cleared)

## 2. Site identification

- Derivation: OSM way 1089997597 — "Angstrom Substation", AEP operator, 345 kV switching, start_date 2022 ([OSM API JSON](sources/2026-07-19_osm_angstrom-substation.json)); POI description "8249 ANGSTROM 345KV" matches exactly
- **Stated project area: not determinable** — no IA document, CAD, or abatement retrieved; imagery footprint ~10-15 acres (1 km chip); consistent with 207 MW BESS spec (10-80 acres)
- Cross-checks: OSM substation name matches ERCOT POI field exactly; [3 km chip](imagery/key/s2_2026-07-01_xwide.png) shows pad immediately adjacent to substation footprint; agree within 0.1 km
- Not obtainable: CAD parcel owner (JS portal); PUCT IA document (HTTP 402 on all attempts); exact POI switch coords (CEII)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Pintail Pass BESS, LLC | SPV | [ERCOT Jun 2026 GIS xlsx](../../data/RPT.00015933.0000000000000000.20260701.151514224.GIS_Report_Jun2026.xlsx) |
| Black Mountain Energy Storage | Developer / originator | [ERCOT parquet (2022-04-01 record)](../../data/ercot_generation_interconnect.parquet) / [bmenergystorage.com](https://www.bmenergystorage.com) |
| Black Mountain | Parent of BMES | [blackmtn.com](https://www.blackmtn.com) (Fort Worth TX, 2007) |
| EEC Pintail | Unknown — brief holder Oct 2023–Jan 2024 | [ERCOT parquet intermediate record](../../data/ercot_generation_interconnect.parquet) |
| Cypress Creek Renewables / Recurrent | Likely buyers (BMES portfolio) | [bmenergystorage.com/projects](https://www.bmenergystorage.com/projects) — 24 ERCOT sites sold totaling 3.6 GW |

- Financing: financial security posted = **Yes** (ERCOT queue 2026-06-01 record); amount not obtainable (IA document blocked)

## 4. Land & county records

- Tenure: **unknown** — CAD portal (sanpatricio.prodigycad.com) is JavaScript SPA, no owner search possible; no deed/lease record found
- Abatements/agreements: none found — expected (Ch.313 expired 2022, JETI rarely used for BESS; no commissioners court minutes accessible)
- CAD: 0 results extractable — portal blocked for automated queries

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: "8249 ANGSTROM 345KV" — IA signed 2023-05-16 per queue record; document not retrieved (PUCT interchange.puc.texas.gov returns HTTP 402)
- Equipment: not available (IA not retrieved)

| IA document | Signed | Financial security posted |
|---|---|---|
| IA (document not retrieved) | 2023-05-16 (queue) | Yes (ERCOT queue; amount unknown) |

| Milestone | ERCOT queue (latest) |
|---|---|
| Approved for energization | 2026-02-10 |
| Approved for synchronization | 2026-03-25 |
| Scheduled COD | 2026-07-24 (reported) |

- Queue-history COD drift (from [timeline.md](timeline.md)): **10 changes**, 2024-06-01 → 2026-07-24 (2-year total slip; most recent slip: Jun 9 → Jul 24)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | Pale gravel pad (~10-15 acres) + white structures (container rows) at Angstrom substation — substantially complete; farmland surroundings undisturbed | [1km chip](imagery/key/s2_2026-07-01_1km.png) / [3km xwide](imagery/key/s2_2026-07-01_xwide.png) |

- Verdict: **substantially_complete** — graded pad and white structures consistent with BESS containers at 10 m/px; no pre-construction comparison available (CDSE auth failed for historical chips)
- Note: industrial complex NW in xwide chip is separate existing facility (Voestalpine/LNG area), not part of BESS

## 7. COD assessment

- **All ERCOT gates cleared**: energization (2026-02-10) + synchronization (2026-03-25) + financial security posted + meetsAllSection69 (2024-11-01) — nothing structurally blocking commercial operation
- **Imagery corroborates**: site appears substantially complete as of 2026-07-01; consistent with 5-day COD from research date
- **10 COD slips** over 2 years (2024-06-01 → 2026-07-24) show a chronically delayed project; however, the acceleration is real — the last three slips were each <6 weeks
- **5-day window** (research date 2026-07-19, reported COD 2026-07-24) is extremely tight; another minor slip is plausible (e.g. testing, paperwork)
- **Independent estimate: 2026-Q3** — if July 24 slips again, August–September 2026 is the most likely landing zone; outside-Q3 risk is LOW given sync approval is 4 months old
- Drift risk: **med** — high chance commercial operation happens in July–September; meaningful chance the July 24 date slips by days/weeks but not months

## 8. Could not determine

- EEC Pintail identity (Oct 2023–Jan 2024 ERCOT record) — TX SOS blocked; no web trace
- IA document contents (signed 2023-05-16) — PUCT Interchange 402 blocked
- Exact project acreage from official documents
- Land tenure (leased vs. purchased) — CAD JS portal inaccessible
- First construction activity date — CDSE historical chips unavailable (auth failure)
- Current EPC contractor
- Offtaker / PPA counterparty
