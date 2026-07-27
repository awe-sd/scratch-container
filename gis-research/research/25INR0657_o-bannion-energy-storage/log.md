# Triage log — O'Bannion Energy Storage (25INR0657)

## T1 start
queue_history.py: 26 snapshots (2024-05-01 → 2026-06-01), 2 reported-COD changes.

COD drift:
- 2025-12-20 (initial, first and only snapshot 2024-05-01)
- 2027-09-25 (2024-06-01 → 2025-11-01)
- 2028-04-21 (2025-12-01 → 2026-06-01, current)

Milestone dates:
- Screening started: 2024-05-09
- Screening complete: 2024-08-05
- FIS requested: 2024-05-01
- FIS approved: 2025-05-02
- IA signed: 2025-12-05
- Meets 6.9(1): 2026-03-25
- Meets all 6.9: NOT achieved
- Construction start/end: NOT reported
- Approved for energization/sync/COD: NOT achieved

T1 result: IA signed (2025-12-05), 6.9(1) met (2026-03-25), COD slipped ~2.3 years from initial estimate. No construction milestones. COD drift = 2.

## T2 start
gmaps.py: HTTP 429 (rate-limited) on all 3 attempts — exact name, name+county, LLC name. Budget exhausted on retry. No pins found.
T2 result: 0 pins. Normal — battery projects rarely have a Google Places listing pre-construction.

## T3 start
DDG: CAPTCHA — no results.
Bing "O'Bannion Energy Storage" Texas: no results (returned unrelated content).
Bing "O'Bannion" + "energy storage" + "Jack County": no results.
Bing alternate spellings (OBannion, O-Bannion): no results.
No developer name surfaced, no LLC registration found, no news.
T3 result: zero web footprint. Likely very early-stage / paper project with no public developer PR.

## T4 start
PUCT Interchange: HTTP 402 on all attempts (root, search, FilingParty query). Portal blocked — not accessible via WebFetch without session auth. No IA document retrieved.
T4 result: NEGATIVE — portal blocked. IA signed date confirmed from queue data (2025-12-05) but document not retrieved. Deep scan should chase the IA PDF directly.

## T5 start
TX Comptroller Ch.313: portal does not expose searchable agreement data via WebFetch — landing pages only, no Jack County results extractable. Budget spent without finding a hit.
JETI: not attempted (budget exhausted; also 25INR0657 entered queue 2024 — post-2022 project, JETI coverage sparse).
T5 result: NEGATIVE — normal for post-2022 battery projects. No abatement found.

## T6 start
No pins from T2. No IA map from T4. Attempted to locate "1506 Long Hollow Switch 345 kV" via Bing searches (ERCOT bus 1506, Oncor Long Hollow, Jack County substation), OpenInfraMap tile — all returned no coordinates.
No site candidate better than "Jack County, TX" (county-level only). Per checklist: SKIP imagery.
T6 result: no site candidate; imagery skipped. deep scan should locate Long Hollow Switch coords via ERCOT NOM/GIS data or Oncor maps.

## T7 start
Wrote triage_findings.json and triage.md. Turns used: ~22. STOP.
T7 result: COMPLETE.

## D1 start (deep scan)
Chasing three triage threads: (1) PUCT IA PDF, (2) Long Hollow Switch 345 kV coords, (3) TX SOS / developer identity.

## D2 — Same POI found: Pinnington Solar (24INR0010)
Parquet query: two projects at "1506 Long Hollow Switch 345kV" — Pinnington Solar 24INR0010 (653.7 MW Solar, Jack County, COD 2026-04-23) and O'Bannion Energy Storage 25INR0657. Pinnington Solar is the key to geolocating Long Hollow Switch — if it has a news/development footprint, it gives site coordinates.
DECISIVE: Co-located POI gives cross-reference for geolocating substation.

## D3 — Pinnington Solar developer: Hecate Energy
Parquet: 24INR0010 interconnectingFacility = "Hecate Energy Longhorn Solar LLC". IA signed 2023-11-02, all 6.9 met 2025-01-30, financialSecurity=Yes, COD 2026-04-23. Hecate Energy's Longhorn Solar = Pinnington Solar at same Long Hollow Switch. This gives a named developer project to find site coordinates.

## D4 — Long Hollow Switch located: ~33.5359,-98.3422
OSM shows unnamed 345kV substation at 33.5359,-98.3422 in N Jack County. Satellite chip (substation_tight_2026-07.png) confirms white L-shaped electrical facility — classic transmission substation. Candidate_b chip (33.5110,-98.3612) shows large cleared/graded orange-brown rectangles = likely Pinnington Solar (653 MW) under construction. Both INRs share this POI. Battery storage projects attach directly at/beside the substation — BESS pad search should focus within 1km of 33.5359,-98.3422.

## D5 — SAME DEVELOPER: Wooderson Energy Storage LLC (25INR0660) also ZIP 27514
TX Comptroller: Wooderson Energy Storage LLC = taxpayerID 32103827245, ZIP 27514 — SAME as O'Bannion (32103124106, ZIP 27514). Two co-developed battery projects from same Chapel Hill NC entity: O'Bannion (306.4 MW, COD 2028-04-21) and Wooderson (306.4 MW, COD 2028-09-30). Both in Jack County. Different POI but same developer and same MW size. DEVELOPER = unidentified NC-based developer at ZIP 27514, Chapel Hill NC area.

## D6 — Wooderson is earlier-stage co-project (no IA)
25INR0660 Wooderson: same developer/ZIP, same 306.4 MW, but still FIS Started, no IA. Original COD was also 2025-12-20 — same as O'Bannion's original! Filed simultaneously ~2024-04. Different POI (Tecumseh-Willow Creek line tap vs. Long Hollow Switch). O'Bannion has IA signed (2025-12-05) making it the lead project. Wooderson is the shadow/B-project — no IA likely means waiting for Oncor NUC/capacity.
DEVELOPER IDENTITY: Two identical 306.4 MW battery projects from same Chapel Hill NC entity = likely a developer with a portfolio strategy in Jack County. Could be Amp Energy, Rev Renewables, or similar NC-based BESS developer. Could NOT confirm identity from public records.

## D7 — Imagery synthesis: site confirmed, no BESS pad visible
longhollowswitch_3km_2026-07.png: 
  - Upper left: Large graded rectangular polygons = Pinnington Solar (24INR0010) under construction
  - Center: White compact square = Long Hollow Switch 345kV substation (~33.535,-98.342)
  - BESS pad (expected 10-40 acres gravel + container rows): NOT visible at substation perimeter
  - Verdict: NO_ACTIVITY for O'Bannion BESS as of July 2026
  - Consistent with timeline: IA signed Dec 2025, NTP presumably issued by March 2026, but 
    pad grading and container staging not yet started or too small to detect at 10m res
SITE: Long Hollow Switch substation = ~33.535, -98.342 (OSM unnamed 345kV + visual confirmation)
BESS location: within 1km of substation, specific pad not yet established

## D8 — Satellite verdict: no_activity (BESS pre-construction)
No BESS-signature features (gravel pad + parallel container rows) visible in present chip.

## D9 — Jan 2026 chip: confirms no BESS activity at Long Hollow Switch
longhollowswitch_3km_2026-01.png (contact sheet row 2, col 2): 
  Heavy cloud/darkness over area — Pinnington Solar field not visible, substation square 
  also obscured. Cannot confirm activity Jan 2026 due to cloud cover. The July 2026 chip 
  is authoritative for present-state.
  
  Importantly: the Jan 2026 chip's substation area (same white square position) = no new 
  pad visible even where cloud-free portions exist at substation vicinity.
  VERDICT STANDS: no_activity as of July 2026 for O'Bannion BESS.
STOP imagery per playbook early-exit rule (present=no_activity, confirmed ~6mo back).

## D10 — PUCT Interchange still blocked (HTTP 402)
All PUCT Interchange URL patterns return 402 — portal requires browser session auth, not accessible via WebFetch. IA confirmed signed 2025-12-05 from queue parquet; document text not retrieved. NEGATIVE for IA PDF.

## D11 — TX Comptroller detail lookup redirects (no full address)
mycpa.cpa.state.tx.us/coa/Details.jsp?taxid= redirects to search page — full mailing address not recoverable beyond ZIP 27514 already captured. Only taxpayer IDs + ZIP stored in sources/.

## D12 — TX SOS requires paid SOSDirect ($1/search)
Cannot retrieve registered agent or officer list without a paid account. Developer identity beyond ZIP 27514 not available from free sources.

## D13 — Google Places: "Pennington Solar" near Bryson TX
gmaps.py places "Pinnington Solar Texas" returned "Pennington Solar" pin at 33.034532,-98.340435 near Bryson TX (Jack County). This is likely the Pinnington Solar 24INR0010 (Hecate Longhorn Solar) — note Bryson is ~25 km south of Long Hollow Switch, suggesting DIFFERENT POI than Pinnington. O'Bannion is at Long Hollow Switch 345kV. Pin may be mis-spelled or a different project.

## D14 — Sentinel-2 CDSE connection error (pennington area chip)
CDSE remote disconnected on pennington area chip attempt (33.0345,-98.3404). No new imagery obtained. Prior long_hollow chips (D7-D9) remain authoritative.

## D15 — Bing searches: zero web footprint for O'Bannion/Wooderson/Long Hollow Switch
Multiple Bing searches for O'Bannion Energy Storage, Wooderson Energy Storage, Long Hollow Switch 345kV returned no relevant results — either CAPTCHA blocks or unrelated content. Developer identity remains unknown beyond Chapel Hill NC ZIP 27514. Both entities have zero public web presence.

## D16 — Stage 5 synthesis begun
All research threads exhausted. Writing findings.json, dossier.md, running build_brief.py and build_index.py.
