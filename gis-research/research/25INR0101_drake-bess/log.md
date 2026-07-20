# Triage log — Drake BESS (25INR0101)

## T1 start
- queue_history.py ran OK: 49 snapshots 2022-06-01 → 2026-06-01
- COD drift count: 5 (2025-02-17 → 2026-04-01 → 2026-03-16 → 2026-04-02 → 2026-07-14 → 2027-01-29)
- Key milestones: Screening complete 2022-08-29; FIS approved 2025-06-18; IA signed 2025-05-06; Meets 6.9(1) 2025-07-16; Meets all 6.9 2025-07-17
- No construction start/end dates, no approval for energization/sync/COD
- Capacity history: 100.8 → 151.2 → 154.42 → 256.18 → 251.0 → 257.3 MW (notable upward jump 2024-04)
- POI: #833 Wylie Switch 138kV, Collin County, NORTH zone

## T2 start
- gmaps.py: 429 rate-limited on both attempts (1 retry used) — no pins from gmaps
- WebFetch DDG: developer identified as **Mallard Energy Storage LLC**; one tracker rates build probability 86% ("IA + FIS complete"); no physical coords found
- WebFetch Bing "Drake BESS Wylie": no results — name collides with musician
- Pins found: 0. Developer name: Mallard Energy Storage LLC

## T3 start
- DDG "Mallard Energy Storage Drake BESS": confirmed developer Mallard Energy Storage LLC; trackers ercotqueue.com + interconnection.fyi list it; no news/PR found
- DDG "Mallard Energy Storage Texas ERCOT": parent company identified as **Peregrine Energy Solutions**; tech partner Wärtsilä; tolling agreement with undisclosed Fortune 500; EWG registration with PUCT; press release URL surfaced (peregrineenergysolutions.com); PUCT filing PDF found (interchange.puc.texas.gov/Documents/54974_393_1564609.PDF)
- DDG "Peregrine Energy Solutions Drake BESS Wärtsilä": no results
- News: no press-release pages successfully fetched within budget
- Developer chain: Drake BESS LLC → Mallard Energy Storage LLC → Peregrine Energy Solutions (parent)
- PUCT docket apparently 54974 based on URL

## T4 start
- PUCT interchange.puc.texas.gov: 402 on filings search (Drake BESS), 402 on filings search (Mallard Energy Storage), 402 on direct PDF (54974_393_1564609.PDF), 402 on case search for docket 54974 — portal blocked, one retry used
- DDG site:puc.texas.gov search: no results indexed
- IA existence: CONFIRMED via queue data (iaSigned = 2025-05-06) but PDF not retrievable during triage
- Docket 54974 surfaced from T3 tracker URL — not verified via portal
- PUCT IA content: not retrieved; milestone schedule unknown

## T5 start
- TX Comptroller Ch.313 page: no searchable data table — redirects to database links not directly accessible
- JETI (HB 5) registry: same page, no direct data table
- Ch.313 program expired 2022; post-2022 application unlikely; no JETI hit surfaced in any prior web results
- Abatement: not found (expected/normal for 2022 entry date)

## T6 start
- Site candidate: Wylie, TX city center (33.0151, -96.5388) from Nominatim fallback — substation coords not found in OSM, GP&L map blocked (403), Overpass timed out
- cdse.py chip attempt: 401 Unauthorized — CDSE credentials not configured in this environment
- Imagery: not retrieved; construction visibility: unknown
- Site candidate confidence: LOW (city centroid, not confirmed substation location)

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~28. Deep scan recommended.
- Blockers this run: gmaps 429, PUCT interchange 402, CDSE 401, GP&L map 403

## Deep scan start — 2026-07-19

Picking up from triage. All 6.9 gates met, IA signed 2025-05-06. Five focus threads:
1. PUCT docket 54974 IA PDF
2. Peregrine Energy Solutions press release + funding
3. Wylie Switch 138kV substation precise coords + CDSE imagery
4. TX SOS LLC registration (Mallard Energy Storage / Drake BESS)
5. Collin County building permits for BESS construction

## Deep scan S1 — developer/LLC chain (2026-07-19)

- Peregrine Energy Solutions press release Dec 22 2025 confirms: project name "Mallard Energy Storage", 250 MW / 500 MWh, "~30 miles NE of Dallas, TX", EPC = WHC Energy Services LLC (a Surerus Murphy company), technology = Wärtsilä Quantum2, tolling with unnamed Fortune 500, under construction as of 2025-12-17
- Nov 17 2025 release confirms $317M financing: Bildmore Clean Energy (pref equity), First Citizens Bank + Societe Generale (coord lead arrangers), Siemens Financial Services, East West Bank; McGuireWoods for Peregrine
- Ownership chain: Drake BESS LLC → Mallard Energy Storage LLC → Peregrine Energy Solutions (Boulder CO, est 2022) → AB CarVal (equity since 2022 founding ~$20B AUM)
- "30 miles NE of Dallas" is consistent with Wylie/Collin County (actual ~25-30 mi NE of Dallas CBD)
- Capacity in IA/queue is 257.3 MW vs 250 MW in PR — typical rounding/nameplate difference
- Source URLs: peregrineenergysolutions.com/press-release/... (two releases)

## Deep scan S2 — PUCT/FERC filing found (2026-07-19)

FERC PUCT docket 54974, doc 393 = FERC EWG self-certification filing Dec 9 2025:
- Confirms: 250 MW BESS in Collin County TX
- Transmission provider: City of Garland TX d/b/a Garland Power & Light (GP&L) — NOT Oncor
- Interconnection: GP&L's "first terminating structure outside the fence of the newly constructed substation owned by the Facility in Collin County, Texas"
- Expected commencement of operations: June 2026 (!!)
- Entity: Mallard Energy Storage LLC (Delaware LLC)
- Parent/contact: Peregrine Energy Solutions, 1495 Canyon Blvd Suite 235 Boulder CO 80302
- Contact: Alice Bray, Director of Asset Management, abray@peregrineenergysolutions.com
- Counsel: McGuireWoods LLP (Julia English, DC)
- Artifact: sources/2026-07-19_puct_54974_ia.pdf

KEY: June 2026 expected operations date conflicts sharply with reported ERCOT COD of 2027-01-29. 
This is FERC filing stating June 2026 as start of operations — highly credible.
Also implies the substation at the Facility is "newly constructed" = site already has major civil work done.

## Deep scan continued — 2026-07-19

### S3 — PUCT IA content
- PUCT docket 54974 doc 393 = FERC EWG self-certification (Mallard Energy Storage LLC, EG26-92-000)
- Key fact: "expected to commence operations in June 2026" — very early vs. ERCOT reported 2027-01-29
- Transmission provider confirmed: City of Garland TX d/b/a Garland Power & Light (GP&L), NOT Oncor
- Interconnection at GP&L's "first terminating structure outside the fence of the newly constructed substation owned by the Facility in Collin County" — project builds its own gen-tie substation
- Source: sources/2026-07-19_puct_54974_ia.pdf

### S4 — Press releases content
- Dec 17 2025 PR (sources/2026-07-19_peregrine_mallard-wartsila-pr-dec2025.html): "advancing construction of the Mallard Energy Storage (Mallard) project, 30 miles Northeast of Dallas. The 250 MW / 500 MWh installation"; EPC = WHC Energy Services LLC (a Surerus Murphy company); technology = Wärtsilä Quantum2; tolling agreement with unnamed Fortune 500
- Nov 13 2025 PR (sources/2026-07-19_peregrine_mallard-317m-financing-nov2025.html): $317M financing closed: Bildmore Clean Energy (pref equity), First Citizens Bank + Societe Generale (coord lead arrangers), Siemens Financial Services, East West Bank; McGuireWoods LLP for Peregrine
- Peregrine founded April 2022 by Hagen Lee; equity from AB CarVal (~$20B AUM) since founding

### S5 — Site identification attempts
- gmaps.py: 429 rate-limited both attempts
- Overpass API: 406 Not Acceptable (content-type issue) — could not get substations near Wylie
- Nominatim: no results for Wylie Switch
- Collin CAD esearch.collincad.org: Cloudflare-blocked
- GP&L website pages: JavaScript-rendered, no substation list accessible
- CDSE 1km chip attempt at 33.015, -96.539: RemoteDisconnected (CDSE transient outage)
- Site confidence remains LOW — city centroid only. "30 miles NE of Dallas" is consistent with Wylie TX area.
- Existing large chip (s2_2026-07-01.png) shows dense suburban Wylie — no obvious BESS gravel pad visible in urban center

### S6 — Negative evidence log
- No abatement/Ch.313/JETI found (expected — post-2022, JETI not yet approved for this project)
- No FAA OE/AAA filings (not applicable — battery, no tall structures)
- PUCT direct search for IA PDF 402-blocked (triage finding confirmed)
- Collin CAD blocked by Cloudflare
- TX Comptroller entity search returned empty (JS-driven)
