# Dossier — Priddy Wind (16INR0085)

Researched 2026-07-19 · site 31.5767, -98.4846 · verdict **real_active**

## 1. Verdict

- **real_active** — EIA-860M (May 2026, Plant 64165) confirms 302.4 MW Onshore Wind Turbine, status OP, operating since January 2022 ([EIA-860M](sources/2026-07-19_eia860m_may2026_operating.xlsx))
- Construction: **operating**, COD January 2022 ([EIA-860 annual](sources/2026-07-19_eia860_plant_2023.xlsx))
- Site: 31.5767, -98.4846 — USWTDB turbine centroid (63 FAA-filed turbines, conf_loc=3) ([satellite view](https://www.google.com/maps/@31.5767,-98.4846,5000m/data=!3m1!1e3))
- COD: reported 2026-12-31 → independent **already operating since 2022-Q1**, drift risk **N/A** (queue COD is a bookkeeping artifact — plant is live)

## 2. Site identification

- Derivation: USWTDB turbine dataset (63 records, EIA ID 64165, FAA ASNs 2020-WTW-8779-OE et al., conf_loc=3 = GPS/image verified) ([USWTDB JSON](sources/2026-07-19_uswtdb_priddy_turbines_all.json))
- **Stated project area: ~35,240 acres** per Ch.313 application Tab 7 ([Ch.313 app](sources/2026-07-19_comptroller_ch313_1502-priddy-wind-app.pdf)); imagery footprint consistent — turbines span 18km N-S × 13km E-W per USWTDB coords
- Cross-checks agree within ~2 km: Google Places pin "Priddy Wind Project" at 500 FM-575 Goldthwaite TX (31.5626, -98.4802) ([gmaps.py output]); EIA-860 annual plant address 500 FM-575, Goldthwaite TX, lat 31.5481, lon -98.4949 ([EIA plant](sources/2026-07-19_eia860_plant_2023.xlsx)); Ch.313 app states "between Goldthwaite TX and Priddy TX, Mills County"
- Not obtainable: exact POI switch coordinates (CEII, PUCT 402-blocked); IA PDF (PUCT interchange 402-blocked throughout research)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Priddy Wind Project, LLC | SPV | [Ch.313 app](sources/2026-07-19_comptroller_ch313_1502-priddy-wind-app.pdf) party + IGNR 16INR0085 explicit |
| ENGIE Holdings Inc. / ENGIE North America | Developer/operator | [Ch.313 app Tab 3](sources/2026-07-19_comptroller_ch313_1502-priddy-wind-app.pdf) combined-group; [EIA-860M](sources/2026-07-19_eia860m_may2026_operating.xlsx) operator name |
| Nordex SE | Turbine supplier (N149/4.8) | [EIA-860 Wind](sources/2026-07-19_eia860_wind_2023.xlsx) + [USWTDB](sources/2026-07-19_uswtdb_priddy_turbines_all.json) |

- Financing: closed pre-COD (plant online Jan 2022); specific lenders not retrieved (PUCT IA blocked)

## 4. Land & county records

- Tenure: **leased** — Ch.313 Tab 9 "Land not applicable" (no land as qualified property); turbines on leased ranchland
- **Ch.313 #1502** (Priddy Wind Project LLC / Goldthwaite ISD): Agreement executed Feb 2021, limitation period 2022–2031, qualified investment $149.6M, 69 turbines within Goldthwaite ISD ([app](sources/2026-07-19_comptroller_ch313_1502-priddy-wind-app.pdf), [agmt](sources/2026-07-19_comptroller_ch313_1502-priddy-wind-agmt.pdf)); reports filed annually through 2025
- CAD: 0 direct-owner parcels retrieved (esearch.millscad.org — URL search returned 404; land on leased parcels expected)
- **Ch.313 #1511** (Bluebonnet Wind Power LLC = Aguayo Wind, INR 20INR0250): Separate project, 103.5 MW SE of Goldthwaite — NOT a Phase 2 of 16INR0085 ([Bluebonnet app](sources/2026-07-19_comptroller_ch313_1511-bluebonnet-app.pdf))

## 5. Interconnection & contractual schedule

- POI per queue: "tap 345kV 1444 Brown – 3422 Killeen", Oncor, CDR zone NORTH
- IA signed 2020-08-13 per ERCOT GIS ([timeline.md](timeline.md)); PDF retrieval blocked (PUCT 402)
- Original project scope per Ch.313: 118 turbines planned; actual build = 63 Nordex N149/4.8 (302.4 MW) — fewer, larger turbines achieving target MW

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([PUCT — blocked](https://interchange.puc.texas.gov)) | 2020-08-13 | Not retrieved (PDF blocked) |

| Milestone | ERCOT GIS |
|---|---|
| IA signed | 2020-08-13 |
| Meets 6.9(1) | 2021-03-29 |
| Meets all 6.9 | 2021-04-30 |
| Approved for energization | 2021-10-13 |
| Approved for synchronization | 2021-11-19 |
| Approved for commercial operation | — (not recorded in GIS) |

- Queue-history COD drift ([timeline.md](timeline.md)): **23 changes**, 2016-10-01 → 2026-12-31; drifting continuously even after plant went live — confirms queue record is a stale placeholder

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2021-10 to 2021-11 | ERCOT energization/sync approvals — plant under commissioning | (queue milestone) |
| 2022-01 | EIA operating date; USWTDB image confirms turbines from Maxar 2022-05-08 | [USWTDB](sources/2026-07-19_uswtdb_priddy_turbines_all.json) |
| 2026-07 | Wide S2 frame: rural landscape, no new construction, turbine pad dots consistent with 63 operating turbines | [xwide](imagery/key/s2_2026-07-01_xwide.png) |

- Verdict: **operating** — 63 Nordex N149/4.8 turbines confirmed by EIA, USWTDB (FAA-coordinated), and Google Places pin at operations facility

## 7. COD assessment

- Reported COD 2026-12-31 is **not a real construction target** — plant has been generating since January 2022 (EIA confirms)
- Queue record has `approvedForSynchronization` (2021-11-19) but missing `approvedForCommercialOperation` gate — this is the only reason the record stays open in ERCOT GIS
- 23 COD changes across a 10-year queue history (2016–2026) show pre-build drift; the post-2022 changes are pure bookkeeping slippage on an open record
- No Phase 2 expansion evidence: no EIA Planned entry, no second Google Places pin, no new Ch.313 filing under 16INR0085 (Bluebonnet #1511 = distinct INR 20INR0250)
- **Independent COD: 2022-Q1 (already achieved). Queue "COD" of 2026-12-31 is an artifact; no future build risk.**

## 8. Could not determine

- PUCT IA PDF and financial security amounts (PUCT interchange 402-blocked throughout)
- Specific PPA offtaker (not found in accessible sources)
- CAD parcel records under lessee names (esearch.millscad.org search URL 404; leased ranchland expected)
- Why ERCOT has not formally closed the GIS record with `approvedForCommercialOperation` (may require project's own filing/request to ERCOT)
