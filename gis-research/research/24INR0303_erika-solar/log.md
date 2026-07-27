# Deep scan log — Erika Solar (24INR0303)

Started: 2026-07-20

## Triage handoff
- IA confirmed (PUCT 35077), all 6.9 milestones complete, 4 COD slips, companion BESS project (27INR0531)
- 3 IA PDFs already on disk: original (1691), Amend 2 (2197), Amend 3 (2293)
- EIA factsheet: Kaufman Solar, LLC "under construction >50%" at 32.5367,-96.22112, planned COD 2026-12
- SPV: Kaufman Solar, LLC (confirmed PUCT docket index)
- Focus threads: (1) pull IA schedules from PDFs, (2) identify parent/developer, (3) site from IA exhibit, (4) imagery

## D0
- findings.json skeleton written

## D1 — IA schedule extraction

### Original IA (PUCT 35077, item 1691, signed 2023-10-12, filed 2023-10-30)
- Exhibit B: In-Service 2025-04-17, Trial Op 2025-04-30, COD 2026-02-24
- Exhibit C: POI = "Healy Switching Station to be constructed within TSP's Elkton Switch to Tri Corner Switch 345 kV transmission line… approximately 6.5 miles south east of Kaufman, TX, on FM 1836"
- Equipment: 57 × Power Electronics HEM 4105M inverters, 233.99 MVA gross, dispatched at 203.5 MW
- Exhibit E security: $14,109,499 Irrevocable Standby LC, effective on or before 2023-10-17
- Artifact: sources/2026-07-19_puct_35077-1691_interconnection-agreement-between-oncor-electric.pdf

### Amendment No. 1 (signed 2023-12-27 per Amend 3 recital) — NOT ON DISK
- Not fetched during triage; puct.py match needed to identify item number
- Negative: no amend-1 PDF in sources/

### Amendment No. 2 (PUCT 35077, item 2197, signed 2025-07-14, filed 2025-07-22)
- Exhibit B: In-Service 2026-05-07, Trial Op 2026-10-01, COD 2027-06-30
- Security adjusted: $14,109,499 → $19,899,031 (effective on or before 2026-05-07)
- Schedule slipped ~14 months from original IA
- Artifact: sources/2026-07-19_puct_35077-2197_amendment-no-2-to-the-standard-generation-interc.pdf

### Amendment No. 3 (PUCT 35077, item 2293, signed 2025-10-17, filed 2025-11-04)
- Equipment change only: 52 × GE LV5+ FLEX 1566 inverters, 238.16 MVA gross, 200.53 MW at 34.5 kV bus, limited to 200 MW at POI
- No schedule change (Amend 2 schedule still governs)
- Inverter switch Power Electronics → GE: active procurement signal
- Artifact: sources/2026-07-19_puct_35077-2293_amendment-no-3-to-the-standard-generation-interc.pdf

## D1 — SPV/developer research
- NEED: run puct.py match, spv.py, ch313.py for parent developer identity
- EIA: entity = Kaufman Solar, LLC (matches IA parties)
- Parent company: unknown from triage

## D2 — Site
- EIA coords: 32.5367, -96.22112 (Kaufman Solar, "under construction >50%" — strong candidate)
- IA Exhibit C: "6.5 miles SE of Kaufman, TX on FM 1836" — consistent with EIA coords
- gmaps.py places "Erika Solar": no pin; "Kaufman Solar construction": no match; "Erika Solar Kaufman Texas": no match; "FM 1836 Kaufman Texas solar": no match; "Healy Switching Station Kaufman": no results
- gmaps.py staticmap: HTTP 403 (Maps Static API not enabled for key)
- CDSE imagery: RemoteDisconnected on all chip/timelapse attempts — CDSE network outage, no satellite imagery obtained

## D3 — Gap-fill

### Developer/parent identity
- search.py: ALL 6 searches failed (backends down): "Kaufman Solar LLC parent company developer Texas solar", "Erika Solar 24INR0303 Kaufman County Texas solar project", "Erika Solar OR Kaufman Solar Texas solar developer", "Kaufman County Texas solar project 200 MW FM 1836", "Kaufman Solar Erika solar Texas", "Kaufman Solar LLC Texas"
- TX Comptroller franchise search (mycpa.cpa.state.tx.us): redirects, form results not accessible
- TX SOS: paid account required
- Parent developer: UNKNOWN — negative evidence logged

### Kaufman County CAD parcels
- Kaufman CAD (esearch.kaufman-cad.org): 404 on all owner-search attempts; requires interactive session
- No parcels found for "Kaufman Solar" or "Erika Solar" — CAD not accessible via WebFetch

### Kaufman County Commissioners Court
- kaufmancountytexas.gov: DNS not found — website inaccessible

### EIA-860M history (eia_history.py --plant-id 69585)
- EIA plant 69585 'Kaufman Solar', entity 'Kaufman Solar, LLC'
- Status: (U) Under construction ≤50% (2026-01 → 2026-02); (V) Under construction >50% (2026-03 → 2026-05)
- EIA planned COD: 2026-12 — 6 months ahead of queue claim 2027-06-30
- EIA coords confirmed: 32.5367, -96.22112 — this is the site
- Artifact: eia_history.json (written)

### Ch.313 / JETI
- ch313.py: no match for Erika Solar / Kaufman Solar in Kaufman County — negative evidence (post-2022 project, JETI absence is normal)

## D4 — Synthesis
- Verdict: real_active — EIA >50% construction + 3 CONFIRMED IA amendments + $19.9M LC posted
- Site: 32.5367, -96.22112 (EIA-860M + IA Exhibit C consistent) — med confidence
- COD: independent 2027-Q3; reported 2027-06-30; EIA says 2026-12; drift risk med
- dossier.md written

## D5 — Deterministic wrap-up
- queue_history.py: ran, wrote timeline.md (48 snapshots, 4 COD changes) — already existed, refreshed
- eia_history.py --plant-id 69585 --write: wrote eia_history.json; EIA planned COD 2026-12; status ≤50% Jan-Feb 2026 → >50% Mar-May 2026
- build_brief.py: wrote brief.html (13 KB, 39 sources)
- build_index.py: indexed 146 projects
