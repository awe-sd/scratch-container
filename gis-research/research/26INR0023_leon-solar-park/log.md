# Triage log — Leon Solar Park (26INR0023)

T1 start

## T1 — queue history (budget 2, used 2)
- 46 monthly snapshots: 2022-09-01 → 2026-06-01
- COD drift count: **0** — held at 2026-07-01 since first appearance (2022-09-01)
- IA signed: 2024-05-21
- Meets 6.9(1): 2025-02-12
- Meets all 6.9: 2025-10-30
- Construction start (reported): 2024-12-06 (first appeared in 2026-04-01 report — backdated)
- Approved for energization: 2026-05-13
- Approved for synchronization: 2026-06-01
- Commercial operation approved: — (not yet in queue data; last report 2026-06-01)
- Capacity stable at ~210 MW (minor fluctuations, settled at 210.11 MW)
- **Assessment**: Extremely mature. All pre-COD milestones achieved. COD 2026-07-01 was 17 days ago; likely already online or imminent. Zero COD drift = strong developer confidence throughout.

T2 start

## T2 — delivery pins (budget 4, used 2)
- gmaps.py "Leon Solar Park" → HTTP 429 Too Many Requests
- gmaps.py "Leon Solar Park Leon County Texas" → HTTP 429 Too Many Requests
- Budget exhausted; no pins found (rate-limited, not a content miss)
- **Result**: 0 pins

T3 start

## T3 — web sweep (budget 5, used 4)
- DDG search "Leon Solar Park Texas solar project" → aggregator summaries via infrasure.ai/ercotqueue.com/interconnection.fyi
- Developer: **Misae Solar IV LLC** (consistent across multiple trackers)
- Ferrovial link: press release about "construction and operation of a 257 MWdc solar PV plant in Leon County, Texas" — likely same project (210 MWac ≈ 257 MWdc)
- DDG follow-up on Ferrovial → CAPTCHA blocked; Ferrovial newsroom → newsletters only, no article text
- LLC registration search → CAPTCHA blocked
- Notes saved to sources/web_sweep_notes.md
- **Result**: news_found=true, developer=Misae Solar IV LLC, Ferrovial possible acquirer/EPC

T4 start

## T4 — PUCT Interchange (budget 6, used 4)
- interchange.puc.texas.gov → HTTP 402 on all URL variants (/, /Documents/search, /search/filings, puc.texas.gov/industry/electric/filings/)
- One retry attempted per rule; all returned 402 (not CAPTCHA — hard block)
- Could not confirm IA filing or download documents
- Note: IA signed date IS in queue data (2024-05-21) — IA exists, just can't access document via PUCT portal
- **Result**: ia_found=false (document not retrieved), portal blocked

T5 start

## T5 — abatements (budget 4, used 4)
- TX Comptroller Ch.313 page: no searchable database served — static overview page only; no Leon County entries retrievable
- Ch.313 program expired 2022-12-31; project entered queue 2022-09-15 (too early in development for a Ch.313 filing to have been approved)
- JETI registry (gov.texas.gov/business/page/jeti) → HTTP 404
- **Result**: abatement_found=false — normal for post-2022 project at early queue stage; JETI eligibility possible but unconfirmable in triage

T6 start

## T6 — imagery (budget 8, used 3)
- Site candidate derived from POI: "Jewett-Crockett 138kV Line" tap near Pleasant Springs
  - Pleasant Springs, TX: lat ~31.315, lon ~95.902 (Nominatim lookup)
  - Midpoint between Jewett (31.36, -96.14) and Grapeland (31.49, -95.48) consistent with Leon County location
- CDSE chip (3×3 grid + 1 retry on center): all returned HTTP 401 Unauthorized (token endpoint failing)
- Per rule: one retry attempted, still 401 — logging negative, not engineering around
- **Result**: construction_visible=false (imagery not retrieved); site_candidate from POI infrastructure, confidence=low
- Note for deep scan: try CDSE auth again or use alternative imagery source; site estimate (31.315, -95.902) is worth verifying

T7 start

## T7 — write and stop (budget 6, used 2)
- triage_findings.json written
- triage.md written (10 lines)
- Total turns used: 18 of 35
- **Run complete.**

## Deep scan start — 2026-07-19

### D1 — CDSE auth fix
- cdse.py get_token() was URL-encoding @ in username as %40; CDSE token endpoint rejects this
- Fixed: username sent raw, only password percent-encoded
- Token now works; imagery pipeline unblocked

### D2 — Present-day chip at triage candidate (31.315, -95.902)
- Chip: imagery/s2_2026-07-01_center.png (2026-07-01 ±15d, 6km buffer)
- **NO SOLAR FARM VISIBLE** — dense mixed forest/pasture East Texas terrain, no graded polygons, no module rows
- Triage site candidate was derived from Nominatim "Pleasant Springs TX" (low confidence) — confirmed wrong
- Must grid-search Leon County for true site; 210 MW ≈ 500-900 acres, unmistakable when in frame

### D3 — PUCT Interchange
- All PUCT interchange.puc.texas.gov URLs return HTTP 402 — portal requires subscription
- IA document not retrievable this route; IA signed date (2024-05-21) from queue data only

### D4 — TX Comptroller search
- mycpa.cpa.state.tx.us redirects to static search form — no GET-based entity lookup available
- Need to use API endpoint or alternate method for LLC search

### D5 — Ferrovial press release
- ferrovial.com newsroom 404 for direct press release URL (newsroom appears restructured)
- ferrovial.com/en/press-room/ shows Webber newsletters only — no solar project content retrievable
- power-technology.com direct URL 404
- Ferrovial link not confirmed yet; will try news search


## D6 — Ferrovial press release (KEY FINDING)
- URL: https://newsroom.ferrovial.com/en-us/press-releases/ferrovial-acquires-a-257mwdc-pv-project-in-texas/
- Date: 2024-05-28
- Saved: sources/2026-07-19_ferrovial_acquires_257mwdc_pv_texas.html
- **Ferrovial ACQUIRED the project** (from Misae Solar IV LLC); paid $72M; owner+operator
- Capacity confirmed: 257 MWdc (= 210 MWac queue data)
- Location confirmed: Leon County, Texas
- Construction start: Q2 2024 ("starting this quarter", May 2024 PR)
- COD: "2026" (consistent with queue report July 1, 2026)
- EPC not named; Ferrovial manages separate Houston EPC project (72 MW + 60 MW BESS for X-Elio)

## D7 — OSM substation data (SITE ANCHOR)
- OSM confirms: **Pleasant Springs Tap** at **31.3292N, -95.8886W** (bus #3355 analog)
- OSM confirms: **Pleasant Springs Substation** at **31.1748N, -95.8525W** (bus #3357 analog)
- The project POI is a NEW tap point on the Jewett-Crockett 138kV line between these nodes
- Site is somewhere along the S-SW corridor from 31.329N,-95.889W toward 31.175N,-95.853W
- Best estimate for project centroid: ~31.25N, -95.87W (south Leon County)

## D8 — Imagery grid sweep results (NEGATIVE EVIDENCE)
- 17 chips covering full Leon County plus corridor at various scales: NO solar visible
- July 2026 east Texas: heavy summer cloud cover + dense pine forest = poor composite quality
- NO definitive absence conclusion warranted; east Texas solar below canopy is harder to detect
- Oct 2025 chip at center also clear/dry: no graded polygons visible at triage candidate location
- The July 2026-07 center chip shows undisturbed forest — confirmed wrong location for triage estimate

## D9 — TX Comptroller / JETI / County records
- Leon CAD: under server maintenance, not accessible
- PUCT Interchange: HTTP 402 (subscription required) — IA document not retrieved
- JETI: Ch.313 expired 2022-12-31 (pre-dates this project's queue entry 2022-09-15);
  JETI registry inaccessible; no abatement document found — EXPECTED for this project type/vintage
- TX SOS SOSDirect: requires $1 fee + account; not accessible via WebFetch
- Leon County Clerk publicsearch.us: JavaScript-rendered, returns nothing via WebFetch

## D10 — Site lat/lon best estimate (revised)
- Queue data: county = Leon, TX
- OSM: Pleasant Springs Tap (bus #3355) = 31.3292N, -95.8886W
- Project POI "Pleasant Springs POI bus #3357" = new tap between 31.329N,-95.889W and 31.175N,-95.853W
- **Best site estimate: 31.329N, -95.889W** (at or near tap point; actual array within ~5-10 km)
- Confidence: **medium-low** — infrastructure anchor confirmed; array centroid uncertain
- 210 MW solar needs ~600-900 acres — would span 3-5 km; site cannot be confirmed without imagery
