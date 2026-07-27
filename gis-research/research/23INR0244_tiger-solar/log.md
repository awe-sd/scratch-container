# Triage log — Tiger Solar (23INR0244)

## T1 start
- queue_history.py ran: 63 snapshots 2021-04-01 → 2026-06-01
- Milestones: Screening started 2021-04-29, complete 2021-07-22; FIS requested 2021-04-29; FIS approved 2025-12-15; IA signed 2024-10-30; Meets 6.9(1) 2025-02-12; Meets all 6.9 2026-01-30
- No construction start/end, no energization/synchronization/commercial operation dates
- COD drift (3 changes): 2023-12-01 → 2026-10-15 → 2028-03-15 → 2027-06-30 (current)
- Capacity trimmed: 306.24 MW → 255.0 MW → 250.9 MW
- Reported COD 2027-06-30 is ~18 months out from triage date; project has all pre-construction milestones (IA, FIS, full 6.9) but no construction dates yet
## T1 result: IA signed, all 6.9 milestones met, project plausible but no construction evidence in queue data

## T2 result: gmaps.py 429 (rate-limited) on all 4 calls — no pins found, API key exhausted

## T3 result: Developer = Vaca Del Sol LLC (NextEra Energy affiliate); PUCT Docket 58405 (Lone Star Transmission CCN for dedicated 345-kV spur to project); news found on Global Energy Monitor + ercotqueue.com + halcyon.io; no construction news; DDG CAPTCHA on query 3 (one retry used, failed)

## T4 result: PUCT Interchange returns 402 on all URL patterns (blocked portal, retried once, still blocked). Docket 58405 known from T3 (Lone Star Transmission CCN amendment for 345-kV spur). IA signed date 2024-10-30 confirmed from queue data. IA PDF not retrieved — deep scan should access interchange.puc.texas.gov directly or via authenticated tool.

## T5 result: No Ch.313 or JETI abatement found for Tiger Solar / Vaca Del Sol / Jones County. TX Comptroller Ch.313 search page did not return filterable county data; DDG search returned no results. Normal for post-2022 project (Ch.313 expired 2022-12-31; JETI launched 2023 but no hit found).

## T6 result: Site candidate = Phantom Hill 345kV substation area (~32.583°N, 99.685°W), method=POI infrastructure, confidence=medium. 3×3 grid run; 7/9 chips failed (CDSE RemoteDisconnected — API instability); 2 chips retrieved (south row: 32.553°N, -99.655 and -99.715). Contact sheet read: southern chips show agricultural land + Lake Fort Phantom Hill, no construction visible. Center/north rows (closest to substation) all failed — coverage insufficient to clear the site. construction_visible=false (but incomplete coverage). Deep scan should retry imagery.

## T7 result: triage_findings.json + triage.md written. Turns used: ~26. STOP.

## Deep scan — Stage 1 (LLC chain)
- Developer confirmed: Vaca Del Sol, LLC, indirect wholly owned subsidiary of NextEra Energy Resources, LLC
  - Source: PUCT CCN docket 58405, item 2 application text (sources/2026-07-19_puct_58405-2_ccn-app-p1-100.pdf)
  - Also confirmed in IA Exhibit D (sources/2026-07-19_puct_35077-1966_tiger-solar-IA.pdf): 700 Universe Blvd, Juno Beach FL 33408 = NextEra HQ
- Lone Star Transmission LLC (TSP) is also a NextEra affiliate (same Juno Beach FL address in Exhibit D)

## Deep scan — Stage 2 (county records / IA)
- PUCT docket 35077 item 1966: ERCOT Standard Generation Interconnection Agreement, Lone Star Transmission LLC & Vaca Del Sol LLC for Tiger Solar Project, signed Oct 30, 2024
  - PDF saved: sources/2026-07-19_puct_35077-1966_tiger-solar-IA.pdf
  - Exhibit B schedule: TIF In-Service Date Nov 6, 2026; Trial Operation Nov 14, 2026; COD June 30, 2027
  - Exhibit C equipment: 72 × PE FS4105M inverters × 4.105 MVA = 255 MW total
  - Exhibit E financial security: $32,710,000 (Corporate Guaranty or Irrevocable Standby LC)
  - NTP Need Date: November 1, 2024
- PUCT docket 58405 = Lone Star Transmission CCN amendment for dedicated 345-kV spur ("Phantom Hill Station to Tiger Solar 345-kV Transmission Line"), Jones County, filed Aug 11, 2025
  - Application confirmed: ~4.55-mile, single-circuit 345-kV line from Phantom Hill Station to Tiger Solar collector station
  - CCN application PDF saved: sources/2026-07-19_puct_58405-2_ccn-app-p1-100.pdf
  - CCN route map (aerial imagery + transmission line route): sources/2026-07-19_puct_58405_ccn-route-map.jpg
  - Construction schedule per CCN: Start May 2026, energize Oct 2026, complete Dec 2026
  - ENGIE contested the CCN (intervened); SOAH hearing completed Jun 2026; SOAH issued Proposal for Decision May 2026; no-exceptions letter Jun 2026 (CCN likely approved)
- Jones County CAD: 0 hits for Vaca Del Sol or Tiger Solar (JavaScript-rendered portal; data loads via API not accessible; expected for leased land)
- JETI/Ch.313: No hit found. JETI portal 404; no comptroller hit for Jones County/Tiger Solar. Normal for post-2022 project.

## Deep scan — Stage 3 (site pinpoint)
- Site method: dual cross-check from two independent descriptions in CCN application (docket 58405)
  - Description A: "4.55-mile line from Phantom Hill Station (NW corner of CR 185 & CR 186) to Tiger Solar collector station"
  - Description B: "collector station located along CR 195 approximately 2.3 miles north of intersection of CR 195 and U.S. Highway 277"
  - Phantom Hill Switchyard (Fort Phantom Switchyard) confirmed via OSM Overpass: 32.5826, -99.6823
  - US-277 in Jones County crosses at approximately 32.51N (from OSM way data)
  - 2.3 miles north of 32.51N = 32.543N ✓
  - 4.55 miles from Phantom Hill at bearing ~128° = (32.543, -99.620) ✓ — two methods agree
- BEST ESTIMATE: Tiger Solar collector station at 32.543, -99.619 (medium-high confidence, ±0.5 km)
- Route map (sources/2026-07-19_puct_58405_ccn-route-map.jpg) confirms: line runs SE from Phantom Hill to lower-right corner where "Proposed Substation" is labeled; Tiger Solar array footprint visible in lower half of map
- Google Places (429 rate-limited) and OSM: no existing Tiger Solar pin
- CCN overview map from IA (Attachment C-3) shows Tiger Solar project footprint with county roads

## Deep scan — Stage 4 (imagery)
- CDSE 401 auth error on all chip attempts (deep scan). Could not retrieve Sentinel-2 imagery.
- Triage coverage (partial): 2/9 chips succeeded; southern grid showed undisturbed agriculture + Lake Fort Phantom Hill; no panels/earthwork. Coverage insufficient (7/9 failed in triage too).
- CCN route map (ESRI 2023 aerial base): undisturbed agricultural fields visible at Tiger Solar footprint area. No cleared ground or construction activity in 2023 imagery.
- NEGATIVE: no satellite imagery for 2024-2026 obtained at confirmed site coordinates.
- construction verdict: no_activity (evidence: queue no construction dates; CCN 2023 aerial; triage southern chips)

## Deep scan — Stage 5 (synthesis)
- dossier.md written
- findings.json written (real_early, no_activity, COD 2027-Q3, drift med)
- queue_history.py: OK (timeline already existed, 63 snapshots, 3 COD changes)
- build_brief.py: OK → brief.html written
- build_index.py: OK → 94 projects indexed

## Second-pass user review (2026-07-21): Ch.313 found, RZ map, wide imagery

- User flagged missing Ch.312/JETI + no parcel map + imagery cropped to the substation.
- ch313.py resolve --name "Vaca Del Sol" (SPV legal name): DIRECT HIT — App #1995, Anson
  ISD, applied 2022-05-26, executed agreement + amendment + annual MCA reports 2023-2025.
  Original scan missed it by searching the queue codename. 4 documents downloaded.
- The application carries the only boundary drawing in any filing: p24 'TIGER -
  REINVESTMENT ZONE' map (Neely Clay Energy). Also names the pre-NextEra chain: Segue
  Neely Clay Holdco I LLC (job-waiver letter, 2022-05-04) -> NextEra (CCN).
- Ch.312 registry: weak negative (Jones is a non-reporting county), but the app embeds
  Jones County's own CC tax-abatement guidelines — county machinery existed; minutes.py
  is the follow-up rung.
- Imagery: stale 2-tile triage set deleted; new series = RZ-centered 12x9km
  (2022/2024/2025/2026-07-20) + substation/lake-centered 9x9km (2024, 2026). No
  construction anywhere in the RZ through 2026-07-20. One name-collision mishap during
  fetching (substation chips briefly overwrote two RZ frames — caught and re-fetched;
  final set verified on disk with distinct names).

## Site correction + verdict flip (user-driven, 2026-07-21)

User rejected the stat images: "no lake close to the site based on the parcel boundary."
Correct on all counts — full re-derivation:
- The deep scan anchored on the WRONG substation (Fort Phantom Switchyard). The IA
  exhibit's substation is next to the ANSON SOLAR plant, ~20km NNW near the town of Anson.
- All previous imagery deleted (wrong location). EIA-860M now lists 'Tiger Solar, LLC'
  directly: 32.79692,-99.88089, 250MW, (V) UNDER CONSTRUCTION >50% since 2026-03,
  planned COD 2026-12 (eia_history.py --write run; the prior scan's 'not in EIA' was
  stale/missed).
- Neighborhood mapped to avoid mis-attribution (5 projects): Anson 1 operating; Anson 2
  UC (sync-approved 2025-11); Jones City 1+2 (Lightsource/Crowded Star) = the separate
  SW complex at -100.00; Funston 15km E. Tiger = the eastern extension of the Anson
  complex, racking grid visible spreading east through 2026-07-20.
- VERDICT FLIPPED: real_early/no_activity -> real_active / under_construction_gt50.
  Drift risk lowered (EIA COD 2026-12 runs AHEAD of the queue's 2027-06-30).
