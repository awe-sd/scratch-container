# Dossier — Juno 3 Solar (26INR0621)

Researched 2026-07-19 · site 32.749, -101.625 · verdict **real_active**

## 1. Verdict

- **real_active** — Sentinel-2 imagery confirms active construction since Nov 2025; substantial racking installed by Dec 2025 ([frame](imagery/key/s2_2025-12-15_construction_active.png))
- Construction: **racking → approaching substantially_complete**, first activity ~2025-11 ([pre-construction Oct 2025](imagery/key/s2_2025-10-15_pre_construction.png) vs [active Dec 2025](imagery/key/s2_2025-12-15_construction_active.png))
- Site: 32.749, -101.625 — OSM operating-plant anchor (32.779°N, 101.625°W for Juno I+II) + imagery-derived south shift; high confidence ([map](https://google.com/maps/@32.749,-101.625,5000m/data=!3m1!1e3))
- COD: reported 2027-11-30 → independent **2027-Q4**, drift risk **med** (FIS unapproved, Buck Canyon substation under construction)

## 2. Site identification

- Derivation: OSM relation 14474033 — operating Juno Solar I+II plant (operator=SE Juno, LLC, 300 MW, 2021-06) at 32.765–32.792°N, 101.598–101.652°W; Juno 3 expansion visible in imagery south of this footprint, center ~32.749°N ([OSM query](https://overpass-api.de/api/interpreter?data=[out:json];relation["name"~"Juno+Solar"](32.6,-102.0,33.0,-101.2);out+geom;))
- **Stated project area: unknown** — CAD portal (esearch.bordencad.org) inaccessible via automated fetch; IA PDF not retrieved; imagery footprint consistent with ~2,000–3,500 acres for 500 MW
- Cross-checks: OSM pin (32.779N, 101.625W) ↔ imagery construction footprint (south of operating plant) — agree; POI "Buck Canyon 345kV" substation construction visible in Jun 2026 frame ~32.735N, 101.635W
- Not obtainable: exact POI switch coords (not in OSM); IA exhibit maps (PUCT 402-blocked)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Juno 3 Solar, LLC (presumed) | SPV | [Queue data](gis-research/data/ercot_generation_interconnect.parquet) — projectName "Juno 3 Solar" |
| SE Juno, LLC | Developer/operator (predecessor) | [Queue data](gis-research/data/ercot_generation_interconnect.parquet) — 21INR0026/21INR0501 interconnectingFacility; [OSM](https://overpass-api.de/api/interpreter?data=[out:json];relation["name"~"Juno+Solar"](32.6,-102.0,33.0,-101.2);out+geom;) — operator=SE Juno, LLC |
| EPC | Unknown | — |
| Offtaker | Unknown | — |

- Financing: NTP issued (financialSecurityAndNoticeToProceedProvided=Yes in queue data) — financial security posted; no debt/equity financing info available

## 4. Land & county records

- Tenure: **unknown** — CAD portal (esearch.bordencad.org) not accessible via automated fetch; consistent with leased ranchland (typical for West Texas solar)
- Abatements/agreements: none found — Ch.313 expired 2022; JETI portal not searchable; expected for a 2025/2026 queue entry; Borden County commissioners court minutes not retrieved
- CAD: 0 hits retrieved (portal dynamic, inaccessible); prior Juno I+II project at same site implies existing land control

## 5. Interconnection & contractual schedule

- POI per queue data: `#59916 Buck Canyon 345kV` — new/planned substation, not yet in OSM; visible under construction in [Jun 2026 imagery](imagery/key/s2_2026-06_substantially_complete.png) (~32.735N, 101.635W)
- IA signed 2025-07-01 per queue; financial security + NTP provided; FIS not approved
- IA PDF not retrieved (PUCT Interchange 402-blocked throughout research)

| IA document | Signed | Financial security posted |
|---|---|---|
| IA (queue-inferred) | 2025-07-01 | Yes (amount unknown — IA PDF not retrieved) |

| Milestone | Queue data |
|---|---|
| IA signed | 2025-07-01 |
| Financial security + NTP | Yes |
| FIS approved | Not yet |
| Construction start (reported) | Not yet in queue |
| Scheduled COD | 2027-11-30 |

- Queue-history COD drift (from [timeline.md](timeline.md)): 0 changes, held 2027-11-30 since 2025-03-01 (16 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-01 | Undisturbed terrain south of operating Juno I+II | [png](imagery/key/s2_2025-01-15_pre_construction.png) |
| 2025-10 | Undisturbed — no construction activity | [png](imagery/key/s2_2025-10-15_pre_construction.png) |
| 2025-12 | **Active construction** — multiple racking/module block sections installed; substation yard emerging | [png](imagery/key/s2_2025-12-15_construction_active.png) |
| 2026-06 | Further progress — more module sections; substation pad active; bifacial tracker row pattern | [png](imagery/key/s2_2026-06_substantially_complete.png) |

- Verdict: **racking** (approaching substantially_complete in southern sections) — Dec 2025 shows significant racking installed; Jun 2026 shows expansion and active substation construction; 10 m/px Sentinel-2 confirms module rows but cannot confirm individual panel energization

## 7. COD assessment

- Construction started ~Nov 2025; 25 months to reported COD (2027-11-30) is tight but feasible given developer's experience at this exact site (Juno I+II completed 2021)
- Positive signals: NTP issued, IA signed, developer track record at site, active visible construction 7+ months before research date
- Risk: FIS not yet approved — if FIS requires transmission upgrades (Borden County is heavily loaded in WEST zone), timeline could slip 3–6 months → 2028-Q1
- Risk: Buck Canyon 345kV is a new substation build — utility (likely Oncor or AEP Texas) build schedule could delay interconnection
- Antila Solar (27INR0500, same POI Buck Canyon 345kV, 500 MW, NTP also provided) at same POI — shared substation build; either both make it or both slip
- Independent estimate: **2027-Q4** (matches reported COD; construction pace supports it if no FIS slip)
- Drift risk: **med** — zero historical drift but two pending milestones (FIS + new substation) not yet achieved

## 8. Could not determine

- Exact developer identity beyond "SE Juno, LLC" (TX SOS requires $1 fee; no web presence for Juno 3 Solar LLC)
- IA exhibit details: milestones, equipment schedule, financial security amount (PUCT Interchange 402-blocked)
- Land tenure: CAD parcels not retrieved (dynamic portal); project area in acres unknown
- EPC contractor and offtaker/PPA details
- FIS approval status timeline and whether transmission upgrades are required
- Whether Antila Solar (27INR0500) is same developer or a different party at same POI
