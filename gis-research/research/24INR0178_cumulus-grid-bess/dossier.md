# Dossier — Cumulus Grid BESS (24INR0178)

Researched 2026-07-19 · site 32.4440, -97.0727 · verdict **real_early**

## 1. Verdict

- **real_early** — construction staging (container rows + gravel pad) visible at Venus Switch Substation in tile imagery ([z17 mosaic](imagery/venus_substation_mosaic_z17.jpg)); baseline Jan 2024 chip shows no activity; Meets All 6.9 not yet satisfied as of Jun 2026 snapshot
- Construction: **clearing/staging**, first activity visible in tile mosaic (undated; estimated 2025 based on IA signed Jun 2025)
- Site: 32.4440, -97.0727 — OSM substation pin + tile imagery confirmation, high confidence ([satellite view](https://www.google.com/maps/@32.4440,-97.0727,1500m/data=!3m1!1e3))
- COD: reported 2028-01-01 → independent **2028-Q1**, drift risk **high** (Meets All 6.9 open; 5 prior slips; opaque developer)

## 2. Site identification

- Derivation: POI "1906 Venus Switch Substation 345kV" → OSM lookup → Venus Switch Substation (Oncor 345/138 kV) at 32.44401°N, 97.07272°W, 2121 E County Road 109, Venus TX 76084 ([OSM note](sources/2026-07-19_osm_venus-switch-substation.txt))
- **Stated project area: not obtained** — IA PDF not retrieved; no abatement docs; expected ~15-40 acres for 210 MW BESS
- Cross-checks: Tile imagery ([z17](imagery/venus_substation_mosaic_z17.jpg)) shows Venus Switch Substation with BESS staging SE of fence, confirming POI-site alignment; S2 2024-01-01 baseline ([chip](imagery/s2_2024-01-01.png)) shows undisturbed ground at coords
- Not obtainable: exact POI switch tie-point (CEII); parcel geometry (BESS on utility-adjacent leased land, 0 CAD hits expected); IA PDF (PUCT Interchange requires JavaScript)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Cumulus Grid BESS, LLC | SPV | ERCOT queue party; 988 Howard Ave Ste 200, Burlingame CA 94010 ([triage log](log.md)) |
| Cumulus Grid LLC | developer/owner | Same Burlingame CA address; no parent identified ([log](log.md)) |
| Unknown | EPC | Not found — 0 press releases, 0 SEC filings, 0 news coverage |
| Unknown | Offtaker/PPA | Not found |

- Financing: not announced; no project finance PR, no Reg D filing (SEC EDGAR: 0 results for "Cumulus Grid")

## 4. Land & county records

- Tenure: **unknown** — no CAD parcels found under LLC name (expected: BESS sites are compact and typically leased utility-adjacent land with no CAD record under project LLC)
- Abatements: none — Ch.313 expired Dec 2022; no JETI application found for Ellis County BESS project
- Ellis County commissioners court agendas/minutes (2025-2026, 34+ meetings scanned): no Cumulus Grid, battery storage, or BESS items
- CAD: 0 parcels returned for "cumulus", "battery storage" queries (SSL failures on Ellis CAD portal; consistent with no record existing)

## 5. Interconnection & contractual schedule

- POI per signed IA: "1906 Venus Switch Substation 345kV", Ellis County — IA signed 2025-06-03 per queue milestone; PDF not retrieved (PUCT Interchange portal JS-only)
- Equipment: not obtained

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2025-06-03 | Unknown — IA PDF not retrieved |

| Milestone | Queue data (latest) |
|---|---|
| FIS approved | 2025-01-27 |
| IA signed | 2025-06-03 |
| Meets 6.9(1) | 2026-03-24 |
| Meets All 6.9 | — (not yet as of 2026-06) |
| Reported COD | 2028-01-01 |

- Queue-history COD drift ([timeline.md](timeline.md)): **5 changes** — 2025-05 → 2026-06 → 2025-06 → 2026-03 → 2027-06 → 2028-01; in queue since 2022-10 (45 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2024-01 | Undisturbed agricultural land at Venus substation coords | [S2 chip](imagery/s2_2024-01-01.png) |
| ~2025 (tile mosaic) | Construction staging SE of Venus Switch Substation: parallel container rows on gravel pad, active laydown yard | [z17 mosaic](imagery/venus_substation_mosaic_z17.jpg) |
| ~2025 (z18 zoom) | Substation detail + cleared gravel area outside fence SE corner | [z18 zoom](imagery/venus_substation_z18.jpg) |
| 2026-06 | S2 10m chip — Venus area visible; construction signal not resolvable at 10m pixels | [S2 chip](imagery/s2_2026-06-01.png) |

- Verdict: **clearing/staging** — baseline undisturbed in Jan 2024; tile mosaic shows BESS container rows/staging at Venus substation. Monthly timelapse not completed (CDSE 403 auth error). First activity date not precisely bracketed.

## 7. COD assessment

- Reported 2028-01-01 is plausible on the IA timeline: IA signed Jun 2025, ~18 months to Jan 2028 is within BESS norms (12-18 months post-NTP)
- **Blocker**: Meets All 6.9 not achieved as of Jun 2026 snapshot — open conditions must be cleared before NTP; each month of slip narrows the already-tight schedule
- 5 prior COD slips in 3.5 years demonstrates high schedule volatility — earliest COD claim was 2025-05, now 2028-01 (+31 months)
- For: IA signed, FIS approved, construction staging visible, capacity stable at 210.74 MW for 3 years
- Against: developer completely opaque (no press, no financing PR, no EPC), Meets All 6.9 open, repeat slip history
- **Independent estimate: 2028-Q1, drift risk high** — reported date is contractually anchored but the open 6.9 condition + 5-slip history make a further 3-6 month slip plausible; barring that, site is real and advancing

## 8. Could not determine

- Parent company / sponsor behind Cumulus Grid LLC (no SEC filings, no press, no OpenCorporates access)
- IA financial security amount (PDF not retrievable)
- Exact acreage / project area (IA not obtained; no abatement docs)
- First activity date with precision (CDSE timelapse blocked by 403 auth error)
- EPC contractor, offtaker, or financing status
- Exact Meets All 6.9 conditions remaining open
