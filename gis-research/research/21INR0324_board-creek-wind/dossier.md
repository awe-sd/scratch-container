# Dossier — Board Creek Wind / Limestone Wind (21INR0324)

Researched 2026-07-20 · site 31.82707, -96.66834 · verdict **real_active**

## 1. Verdict

- **real_active** — EIA-860M shows Operating since 2022-12 (plant 65306); 88 turbines mapped in OSM under "Limestone Wind"; ERCOT approved for synchronization 2022-10-06 ([timeline.md](timeline.md))
- Construction: **operating**, first ERCOT energization approval **2022-09-19** ([timeline.md](timeline.md))
- Site: 31.82707, -96.66834 — OSM turbine centroid (88 turbines tagged "Limestone Wind") + EIA plant coords 31.85346,-96.62446 ([OSM turbines](sources/2026-07-20_osm_overpass_limestone-wind-turbines.json)) ([satellite view](https://www.google.com/maps/@31.8271,-96.6683,5000m/data=!3m1!1e3))
- COD: reported 2026-07-01 (STALE queue entry) → independent **2022-Q4**, drift risk **none** (already operating since ~Nov–Dec 2022)

## 2. Site identification

- Derivation: OSM Overpass query returned 88 turbines tagged `name=Limestone Wind` in Navarro Co TX; centroid 31.82707,-96.66834; lat range 31.77–31.88 (~12 km N-S spread) ([OSM data](sources/2026-07-20_osm_overpass_limestone-wind-turbines.json))
- **Stated project area: not found** — no Ch.313/JETI application, IA exhibits do not state acreage; CAD search not run
- Cross-checks agree within ~2 km: EIA plant 31.85346,-96.62446; OSM "Limestone Wind Substation" 31.8534,-96.6219; PUCT PGC address 803 SW CR 4260, Dawson TX 76639 ([PGC filing](sources/2026-07-20_puct_53424-1_filing.pdf))
- IA POI: Outlaw Switch, Navarro County, ~6 mi SE of Richland TX ([IA](sources/2026-07-19_puct_35077-1306_interconnection-agreement-between-oncor-electric.pdf))
- Not obtainable: Outlaw Switch exact coords (CEII); FAA OE/AAA turbine coordinates (live sources blocked 2026-07, no local cache hit)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Limestone Wind Project, LLC (Delaware) | SPV | party on [IA](sources/2026-07-19_puct_35077-1306_interconnection-agreement-between-oncor-electric.pdf) + [PGC filing](sources/2026-07-20_puct_53424-1_filing.pdf) |
| ENGIE IR Holdings, LLC | Holding company (100% owner of SPV) | [PGC filing](sources/2026-07-20_puct_53424-1_filing.pdf) Part C §3 |
| ENGIE North America Inc. | Parent (Houston TX, 1360 Post Oak Blvd #400) | [PGC filing](sources/2026-07-20_puct_53424-1_filing.pdf); declared long-term owner + operator |
| ENGIE S.A. | Ultimate parent (Paris, France) | [triage.md](triage.md) |
| LyondellBasell | VPPA offtaker | [ENGIE PR 2023-03-20](https://www.engie-na.com/engie-adds-more-than-650-mw-to-u-s-operations/) |
| Stanley Black & Decker | VPPA offtaker | [triage.md](triage.md) (Business Wire 2021-08-03) |
| Whirlpool Corporation | VPPA offtaker | [ENGIE PR 2023-03-20](https://www.engie-na.com/engie-adds-more-than-650-mw-to-u-s-operations/) |

- Financing: ENGIE NA self-financed (no third-party project finance announcement found; three VPPAs provide revenue certainty)

## 4. Land & county records

- Tenure: **unknown** — no CAD parcel search run (JS-blocked portals); PUCT PGC lists a physical address (803 SW CR 4260 Dawson TX) suggesting site control; IA Exhibit C §12c/d indicates land rights to be negotiated — likely leased ranchland
- Abatements: no Ch.313/JETI application found for Limestone Wind in Navarro County (wind farms generally do not pursue Ch.313 in TX; absence expected, not evidence of paper project)
- CAD: not searched (Navarro County CAD portal is JS-rendered; blocked in agent environment)

## 5. Interconnection & contractual schedule

- POI per signed IA: "Outlaw Switch within TSP's west circuit of TSP's Navarro Switch – Limestone SES 345 kV double-circuit transmission line, Navarro County, TX — ~6.0 mi SE of Richland" ([IA](sources/2026-07-19_puct_35077-1306_interconnection-agreement-between-oncor-electric.pdf))
- Equipment (Exhibit C): 99 × GE 3.03-140 turbines (3.367 MVA each), 333.30 MVA gross, dispatched 301 MW at 345 kV
- No amendments filed in PUCT docket 35077

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077-1306_interconnection-agreement-between-oncor-electric.pdf)) | 2021-08-19 | Irrevocable LC (amount not extracted from PDF Exhibit E) |

| Milestone | Original IA 2021 |
|---|---|
| In-Service | 2022-05-19 |
| Trial Operation | 2022-09-23 |
| Scheduled COD | 2022-11-04 |

- Queue-history COD drift ([timeline.md](timeline.md)): **22 changes**, 2021-10-15 → 2026-07-01; all pre-construction/pre-energization slippage; ERCOT sync approved 2022-10-06, energization 2022-09-19 — project achieved operational milestones on the IA schedule

## 6. Satellite timeline

| Date | Observation | Source |
|---|---|---|
| 2022-09-19 | ERCOT approved for energization | [timeline.md](timeline.md) |
| 2022-10-06 | ERCOT approved for synchronization | [timeline.md](timeline.md) |
| 2022-12 | EIA reports Operating status; operating date 2022-12 | [eia_history.json](eia_history.json) |
| 2023-01 → 2026-05 | EIA status: Operating continuously (40 monthly reports) | [eia_history.json](eia_history.json) |
| 2026-07-20 | 88 turbines in OSM tagged "Limestone Wind" | [OSM](sources/2026-07-20_osm_overpass_limestone-wind-turbines.json) |

- Sentinel-2 imagery: **unavailable** — CDSE identity endpoint (identity.dataspace.copernicus.eu) returning RemoteDisconnected on all chip attempts; service outage on 2026-07-20. No satellite frames obtained.
- Verdict: **operating** — EIA + ERCOT milestones + OSM turbine mapping are conclusive without imagery

## 7. COD assessment

- Queue COD 2026-07-01 is a **stale placeholder** — ERCOT GIS has no `approvedForCommercialOperation` date for this project; the queue entry was never formally closed, causing the system to show a future COD
- ERCOT approved for energization 2022-09-19; approved for synchronization 2022-10-06 — both ~6 weeks ahead of IA's 2022-11-04 scheduled COD
- EIA-860M reports Operating from 2023-01 with operating date 2022-12; planned COD 2022-12 in the last pre-operating report — consistent with on-schedule completion
- ENGIE press release (2023-03-20) explicitly states "COD end-2022" with three named commercial VPPA customers
- 22 queue COD slips reflect pre-construction delays only (project entered queue Oct 2019, IA signed Aug 2021); no post-synchronization stall evidence
- **Independent COD: 2022-Q4** (most likely November–December 2022; drift risk **none**)

## 8. Could not determine

- Financial security LC dollar amount (Exhibit E text did not contain a dollar figure in the extractable PDF text)
- Exact COD date within 2022-Q4 (EIA shows 2022-12; IA scheduled 2022-11-04; likely ~Nov–Dec 2022)
- Navarro County CAD parcel details (JS-blocked portal; ownership/acreage unknown)
- FAA OE/AAA exact turbine coordinates (live sources blocked 2026-07; no Navarro Co cache hit)
- Satellite imagery confirmation (CDSE service outage 2026-07-20)
- Financing structure (no third-party project finance announcement found)
