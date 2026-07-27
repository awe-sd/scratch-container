# Triage log — Lyra Solar (27INR0434)

## T1 start
**queue_history.py** — 16 snapshots (2025-03-01 → 2026-06-01)
- COD drift: 0 — 2027-09-15 held stable across all 16 snapshots
- FIS requested: 2025-03-20 | FIS approved: NOT achieved
- Screening complete: 2025-06-09
- IA signed: 2025-07-01 (appeared in 2025-07-01 snapshot)
- Meets 6.9(1) / all 6.9: NOT achieved
- Construction start/end: NOT reported
- Note: IA signed without FIS approved (independent gates per data model)

## T2 start
gmaps.py — HTTP 429 on all queries (rate-limited); one retry attempted, all failed.
- No pins found. Normal outcome.

## T3 start
Search 1 (DDG "Lyra Solar" "Borden County" Texas): strong hits
- Developer confirmed: **Juno Solar 4**
- PUCT Case 59183: WETT CCN amendment for "Muleshoe to Lyra Solar and Lyra BESS 345 kV transmission lines in Borden County"; filing dated 2026-01-07
- Companion project: **Lyra BESS** (battery storage, same POI area)
- Infrasure.ai and ercotqueue.com both list project; no additional corporate parent surfaced
Search 2 (DDG "Juno Solar 4" LLC): CAPTCHA — negative, no retry
Saved source notes to sources/infrasure_ercot_27INR0434.md

## T4 start
PUCT Interchange portal — HTTP 402 on all endpoints (case search, filing party search, direct PDF). Portal blocked; retried once, still 402.
- Indirect evidence from T3: PUCT Case 59183 (WETT CCN) references "Muleshoe to Lyra Solar and Lyra BESS 345 kV transmission lines in Borden County", filed 2026-01-07.
- IA signed date from queue: 2025-07-01. PUCT IA filing likely exists but not retrievable this pass.
- queue `iaSigned = 2025-07-01` is strong corroboration that IA was executed.
Result: IA confirmed via queue data; PUCT PDF not retrieved (portal blocked). ia_found = true (queue).

## T5 start
Ch.313 expired Dec 2022 — project entered queue 2025-03, so Ch.313 not applicable.
JETI registry: TX Comptroller site returned navigation page only (no searchable data); DDG search returned CAPTCHA. No abatement found.
Normal result for post-2022 project without JETI filing yet. abatement_found = false.

## T6 start
Site candidate assessment:
- T2 (gmaps): no pin (tool blocked 429)
- T4 (IA PDF): not retrieved (PUCT 402)
- T5 (abatement map): none
- POI: "345kV MULESHOE (#59922)" — PUCT filing says transmission lines "in Borden County" but substation precise coords not found. ERCOT naming convention suggests substation may be in Borden County, but city of Muleshoe is Bailey County (~170 mi away). Cannot narrow below county level.
DECISION: no site candidate better than "somewhere in the county" → SKIP imagery per checklist. Log: "no site candidate".
construction_visible = false (imagery not run)

## T7 start
Wrote triage_findings.json and triage.md. Turns used: ~22. STOP.
deep_scan_recommended: true

---
# Deep scan — 2026-07-19

## Stage 1 start — LLC → parent chain
Threads: (1) TX Comptroller taxable entity search for "Lyra Solar" / "Juno Solar", (2) web search for Juno Solar 4 parent, (3) LinkedIn / press releases

## Stage 3 start (concurrent with Stage 1) — delivery-pin trick
gmaps.py places queries: blocked 429, all attempts failed — negative, consistent with triage.

## Stage 3 — OSM/Overpass infrastructure analysis (decisive finding)
Overpass API: all power substations + lines in Borden County precise bbox (32.5,-101.78,33.0,-101.08).
WETT 345kV substations in Borden County:
  - Long Draw Substation: 32.7211, -101.6330 (WETT, 345kV)
  - Faraday Substation: 32.6481, -101.3958 (WETT, 345kV)
  - Unnamed WETT 345kV/138kV: 32.7189, -101.6329

DECISIVE: OSM shows "Borden County BESS" (way 1458653097) at lat=32.7223, lon=-101.6385
  operator="Borden County Battery Energy Storage System LLC", 150 MW battery
  This is adjacent to WETT Long Draw cluster — CONFIRMED companion BESS project in Borden County
  → Lyra Solar site is near 32.72, -101.64 (Long Draw cluster area)

"Muleshoe (#59922)" is ERCOT's internal bus name for the Long Draw substation complex at 32.72, -101.63.
Site candidate: ~32.72, -101.64 (±0.05° radius around Long Draw/BESS cluster) — HIGH CONFIDENCE for county but lat/lon still approximate.
Source: Overpass API query executed 2026-07-19, artifact: sources/2026-07-19_overpass_borden-county-substations.json

## Stage 1 continued — developer series identification (from local parquet)
Local ERCOT parquet query revealed 20 active projects in Borden County (latest snapshot 2026-06-01).
KEY FINDINGS:
- "Juno 3 Solar" (26INR0621): 500 MW solar, Borden County, IA signed 2025-07-01 → SAME DATE as Lyra Solar (27INR0434)
  - Developer name "Juno 3 Solar" confirms the naming series: Juno Solar 1, 2, 3, 4 = same developer portfolio
  - "Lyra Solar" reported developer = "Juno Solar 4" → Lyra Solar is "Juno Solar 4" project
- "Lyra Storage" (26INR0636): 500 MW BESS, Borden County, COD 2026-11-12, IA signed 2025-08-13
  - This is the Lyra BESS companion already listed in PUCT Case 59183 filing
  - Different INR = separate project but same POI cluster
- "Antila Solar" (27INR0500): 500 MW solar, Borden County, IA signed 2025-08-13
  - Another 500 MW project by likely same developer (same date as Lyra Storage)
- "Uva Creek Solar" (26INR0359): 302 MW, Borden County, IA signed 2024-10-30 — earlier project

The Borden County area is clearly a major solar development cluster. The "Juno Solar" numbering (1,2,3,4) strongly suggests this is a portfolio developer (likely with a parent company).

IMAGERY ANALYSIS — s2_2026-07-01_center.png (3km buffer, 32.7222, -101.6385):
- Center of frame: bright white/gray geometric pads = BESS/substation cluster (Long Draw area)
- Upper-right corner (NE, ~32.77, -101.59): large dark uniform rectangular blocks = active solar installation
- The solar installation appears COMPLETE or near-complete based on dark uniform texture
- Likely candidates: Juno Solar Phase I (166 MW, operating 2021), Juno Solar Phase II (147 MW, operating 2021), or Long Draw Solar (227 MW, operating 2021)
- Lyra Solar (this project) and Juno 3 Solar (26INR0621) are NOT YET OPERATING — the dark blocks are the existing operating fleet
- CDSE credentials expired (401 invalid_grant) — only one chip retrieved

## Stage 1 — Parent chain conclusion
- ENGIE North America confirmed developer of Long Draw Solar (ENGIE Long Draw Solar LLC, 225 MW ERCOT West, construction 2019, operating 2021)
  Source: HASI 8-K/A 2021-03-17, exhibit jupiterequityholding2019.htm — "ENGIE Long Draw Solar LLC (Long Draw) Solar ERCOT West Construction 225"
  Artifact: sources/2026-07-19_sec_hasi-engie-jupiter-holdings-2019.htm
- Juno Solar series naming: "Juno Solar (Phase I)" 21INR0026, "Juno Solar (Phase II)" 21INR0501, "Juno 3 Solar" 26INR0621, "Lyra Solar" 27INR0434 (developer = "Juno Solar 4")
  All in Borden County, all ERCOT WEST — ENGIE is the PROBABLE parent but not yet directly confirmed for the Juno Solar series
- Direct corporate name search: Lyra Solar LLC, Juno Solar 4 — NOT found in SEC EDGAR, OpenCorporates, or TX Comptroller (portal requires JS); SOSDirect requires login
- ENGIE <-> Juno Solar connection is inferred from: same site cluster, constellation naming pattern, same WETT POI area; NOT yet confirmed by primary source

## Stage 2 — County records conclusion
- Borden CAD: esearch.bordencad.org exists but search URL format not retrievable without browser
- Ch.313: N/A (project entered queue 2025, Ch.313 expired 2022)
- JETI: TX Comptroller JETI portal blocked (JS required)
- Commissioner's court: borden county website not resolvable
- CAD owner search: blocked/404
- PUCT Interchange: still 402 on all PDF endpoints
- IA confirmed only via queue milestone (iaSigned 2025-07-01) — no PDF retrieved
- Abatements: none found
- Negative evidence logged: TX Comptroller (JS-blocked), SOSDirect (auth-required), OpenCorporates (0 results), PUCT Interchange (402)

---
# Second-pass review — 2026-07-21

## Developer CORRECTION (primary source)
Pulled the four campaign IAs from PUCT central docket 35077 and read the parties:
- 35077-2184 = Juno Solar 3 Project | 35077-2185 = **Lyra Solar Project** | 35077-2225 = Lyra BESS | 35077-2227 = Antila Solar
- ALL four: WETT + **SE DC DevCo, LLC = SB Energy** (3 Lagoon Dr Suite 280, Redwood City CA).
- The 2026-07-19 "ENGIE North America (probable)" inference is WRONG. Root cause = the "Juno" name trap: Intersect Power (IP Juno LLC) owns the EXISTING Juno Solar Project (op 2021); SB Energy codenames its NEW projects "Juno Solar 3/4". ENGIE owns only the existing Long Draw Solar neighbor.
- Verified + renamed IA: sources/2026-07-19_puct_35077-2185_lyra-solar-IA.pdf.

## Site CORRECTION (map exhibit)
Prior anchor 32.7222,-101.6385 = the EXISTING Long Draw/Borden County BESS complex, NOT Lyra.
Pulled CCN 59183 (live): item -2 application + 310-pp EA, item -24 Pollio testimony.
- EA Appendix A **Figure 1-1 (Project Location Map)** + **Figure 2-1 (Property Owners, aerial)** rendered -> collector stations just N of US-180, ~7 mi W of Gail, on the "Juno DC, LLC" parcel; Muleshoe Switching Station (POI #59922) ~8 mi SOUTH, connected by a new ~8-mi 345kV line.
- New anchor **32.770,-101.555** (method ccn_59183_figure_1-1_2-1_map, conf medium-high; georeferenced vs Gail + Long Draw, ±~1 km).
- Pruned the 169 MB image-only figure appendix PDFs after rendering Fig 1-1/2-1 (re-fetch: puct.py fetch 59183 2). Removed banned-source artifact infrasure_ercot_27INR0434.md (infrasure.ai).

## IA schedule / security (35077-2185, Exhibit B)
In-Service 2027-05-15, Trial Op 2027-06-15, **COD 2027-11-15** (queue projectCod 2027-09-15 — ~2 mo earlier). Initial security **$18,000,000** at execution (<= 2025-07-16); LNTP at CCN filing/award; FNTP TBD on FIS. Lyra Solar = lead IA of the Muleshoe pair; Lyra Storage rides on it.

## Registries
- ch313.py / JETI: NEGATIVE (structural, post-2022). ch312.py: 4 Borden zones, all other/existing projects (Oxbow #3676, BNB Long Draw #4302, IP Juno #4303, Borden BESS #15389); none names Lyra/SE DC DevCo; none links a harvested PDF (pdf=None) -> nothing to render. eia_history.py --write: NOT in EIA-860M.
- Oxbow check: BNB Oxbow Solar Reinvestment Zone (Oxbow Ranch, submitted 2023-12-15, exp 2028-04-22) is a SEPARATE early "BNB" solar zone, NOT the SB Energy trio.

## Imagery (s2aws.py, 5.0 km buffer @ 32.770,-101.555, tile 14SKB) -> imagery/key/
Read all 3 frames. 2024-07-18 & 2025-07-20 (cloud 0.0%): collector site BARE rangeland; existing ENGIE Long Draw Solar array at W edge (attributed, NOT Lyra). 2026-07-20: NEW bright ~1 km graded/cleared rectangle at the collector complex, absent 2025 -> early site preparation. 2024 chip swath-clipped (SE), west+center clean. Construction verdict upgraded: early_site_preparation_observed.

## Rebuilt: build_brief.py (see below)

## Imagery UPDATE — denser 2026 time series (user request)
Added 5 chips to bracket the 2026 construction ramp (s2aws.py, same anchor/buffer):
2025-11-02, 2026-02-03, 2026-03-29, 2026-05-31, 2026-07-03 (filenames use nominal request dates; actual acquisition in findings.imagery_timeseries).
Read progression at the collector site (N of US-180, ~32.77,-101.555):
- 2025-07 / 2025-11 / 2026-02: BARE rangeland (baseline).
- 2026-03-29: cleared/plowed rectangle emerging.
- 2026-05-31: bright white graded pad established, expanding (cloud 0.0%).
- 2026-07-03 / 2026-07-20: ~1 km bright graded/cleared area.
Onset of generator-site grading ~Q1-Q2 2026 — AHEAD of the CCN 59183 transmission TIF window (Aug 2026-Apr 2027). Construction verdict -> active_site_construction_observed; project verdict -> real_active. Existing ENGIE Long Draw Solar array (W edge, all frames) attributed as neighbor, NOT Lyra.
