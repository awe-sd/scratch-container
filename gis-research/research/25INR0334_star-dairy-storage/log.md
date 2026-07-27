# Triage log — Star Dairy Storage (25INR0334)

## T1 start
- Script: `queue_history.py 25INR0334`
- 34 monthly snapshots (2023-04-01 → 2026-06-01)
- IA signed: 2024-12-09 (first appeared 2025-05-01 report)
- FIS: never approved
- COD drift (4 changes):
  - 2026-03-23 (original)
  - 2026-04-21
  - 2026-09-14
  - 2027-04-03
  - 2027-07-12 (current, ~16 months slip from original)
- Capacity: 209.1 → 204.93 → 205.24 MW (minor trims, stable)
- Milestones: Screening complete ✓, FIS requested ✓, IA signed ✓; no construction dates

## T2 start
- gmaps.py: HTTP 429 on both attempts ("Star Dairy Storage" and "Star Dairy Storage Lamar County")
- Budget exhausted after 1 retry per rules
- Result: 0 pins found — NORMAL, no Google Maps presence expected for a paper battery project

## T3 start
- Bing search: "Star Dairy Storage" battery ERCOT — 0 results
- Bing search: "Star Dairy Storage LLC" OR "25INR0334" — 0 results
- Bing search: "Star Dairy" battery storage Lamar County Texas — 0 results
- Bing search: "Star Dairy Storage" Paris Texas OR "Woodard" substation — 0 results
- DuckDuckGo: CAPTCHA blocked (1 retry used, counted as blocked)
- Result: no web presence, no developer name surfaced, no news/PR found

## T4 start
- PUCT Interchange direct URLs: HTTP 402 on all 3 attempts (auth-gated portal)
- Bing search "Star Dairy Storage" PUCT/IA: 0 results
- Bing search "Star Dairy Storage" interconnection agreement ERCOT: 0 results
- IA IS confirmed signed (2024-12-09) per queue data but no public PDF obtained
- Result: IA exists (queue-confirmed), document not retrieved — deep scan should attempt authenticated PUCT access

## T5 start
- TX Comptroller Ch.313 page: no searchable database found (Ch.313 program expired 2022)
- JETI Bing search for Lamar County battery: 0 results
- Result: no abatement found — NORMAL for post-2022 project; Ch.313 closed to new apps; JETI not publicly searchable

## T6 start
- Site candidate identified: Woodard area, Lamar County (Woodard Cemetery OSM anchor)
  - lat 33.461, lon -95.367 — based on WOODARD_5 bus name in POI description
  - Confidence: LOW (cemetery as geographic anchor, no substation coords confirmed)
- Attempted cdse.py chips at lat=33.461, lon=-95.367, buffer_km=2, date=2026-06-01
- RESULT: HTTP 401 Unauthorized — ~/.config/gis-research.env contains only example placeholder
- CDSE credentials not configured; imagery skipped
- No contact sheet produced; no construction verdict possible

## T7 start
- triage_findings.json: written
- triage.md: written
- Turns used: ~28
- STOP

## Deep scan — 2026-07-19

### D1: IA Retrieved
- PUCT Interchange docket 35077, item 2026 (filed 2025-01-02)
- Both 25INR0164 (Star Dairy Solar, 125.61 MW) and 25INR0334 (Star Dairy Storage, 204.93 MW) on same IA
- Party: Star Dairy Solar LLC (SPV for both); signed 2024-12-09
- Developer: X-Elio (Xavier.Tyler@X-Elio.com, 1255 23rd St NW Suite 300, Washington DC 20037)
- POI: Forgotten City Switch on Woodard Switch - Paris Switch 345kV line, Lamar County TX
- Contractual schedule per Exhibit B:
  - Security deadline: December 6, 2024
  - In-Service Date: December 3, 2026
  - Scheduled Trial Operation: December 13, 2026
  - Scheduled Commercial Operation: April 3, 2027
- Financial security: $14,850,285 LC posted on or before 2024-12-06 (Exhibit E)
- Equipment: 60x Power Electronics PCSM FP4200M storage inverters (204.93 MW)
- SOURCE: sources/2026-07-19_puct_35077-2026_oncor-star-dairy-solar-storage-IA.pdf

### D2: Developer identity — X-Elio
- X-Elio is a Spanish renewable energy developer (subsidiary of Tojeiro family holding)
- US headquarters: 1255 23rd St NW Suite 300, Washington DC 20037
- Contact: Xavier Tyler, Country Manager (also signed IA as Kerri Neary — Country Manager)
- No press releases found for Star Dairy project; zero web presence for this specific project
- NEGATIVE: No financing announcement, no PPA announcement found in web search

### D3: PUCT search results
- "Star Dairy Storage" in UtilityName, FilingParty: 0 results
- "Star Dairy" in FilingDescription: 1 record — docket 35077, item 2026 = the IA
- "Star Dairy Storage" in FilingDescription: 0 results (stored under Solar LLC entity)
- No amendment IA found — only original IA on file

### D4: Lamar CAD
- CAD portal found at esearch.lamarcad.org but requires JavaScript/SPA — not scrapable
- No abatement found (Ch.313 closed 2022, JETI not applicable)
- NEGATIVE: 0 parcels found under "Star Dairy" (expected for lease pre-construction)

### D5: Site candidate update
- OSM 345kV line data: Monticello-Paris 345kV line (Oncor) has junction at ~33.4675, -95.3724
- Both line segments share this node — consistent with a switching station location
- IA confirms: Forgotten City Switch will be ADJACENT to generator substation
- This junction is in NW Lamar County, ~25 miles SW of Paris TX
- NEW site candidate: lat=33.468, lon=-95.372 — medium confidence (line junction, not direct pin)
- Previous candidate (Woodard Cemetery, 33.461, -95.367) was 1.2 km SE — consistent range

### D6: CDSE imagery — BLOCKED
- cdse.py chip at lat=33.468, lon=-95.372, date=2026-06-01: HTTP 401 - Invalid user credentials
- CDSE credentials (sdalvi@appianwayenergy.com) appear expired or changed since triage was written
- No satellite imagery available for this project
- NEGATIVE: Cannot confirm construction stage via imagery

### D7: X-Elio developer profile
- X-Elio is a Spanish renewable energy developer (subsidiary of Grupo X-Elio)
- US headquarters: 1255 23rd St NW Suite 300, Washington DC 20037
- Key contact for Star Dairy: Xavier Tyler (listed in IA); IA signed by Kerri Neary (Country Manager)
- TRACK RECORD: X-Elio commissioned "Liberty Energy Project" (72MW solar + 60MW storage, Dayton TX, Harris County) Sept 2025 - their FIRST US solar+storage project
- SOURCE: Yahoo search results confirming Liberty Energy Project commissioned Sep 24-26, 2025
- Star Dairy Solar & Storage = X-Elio's SECOND US project, significantly larger (125.61 MW solar + 204.93 MW storage)
- No Star Dairy-specific PPA or financing announcement found in web search (as of 2026-07-19)
- NEGATIVE: No Google Maps delivery pin, no LinkedIn posts, no news articles about Star Dairy project
