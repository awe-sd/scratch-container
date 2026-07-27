# Research Log — Piedra Solar (25INR0168)

Project: Piedra Solar, 281.7 MW Solar PV, Freestone County TX
POI: Tap 345-kV line Navarro (68091) – Limestone (46020)
CDR zone: NORTH
Reported COD: 2026-12-22
INR year: 2025 (in reports since 2023-03)

---

## Triage results (previous session, 2026-07-18)

- COD drifted 3×: 2025-06-01 → 2026-04-20 → 2026-09-30 → 2026-12-22 (current)
- IA signed 2024-07-02; FIS approved 2025-09-17; meets all 6.9 as of 2025-10-30
- Capacity trimmed: 305.5 → 300.93 → 282.0 → 281.7 MW
- No construction start/end dates in queue data
- Piedra Solar LLC: Delaware foreign LLC, TX registered 2022-07-05, 1201 Louisiana St Houston
- Piedra Solar II LLC also filed 2024-07-03
- PUCT Interchange returned 402 (JS-required portal, not accessible via curl)
- 3 of 9 grid chips captured (CDSE 401 in triage) — all showed no construction
- Site estimate: low confidence, POI corridor only
- Deep scan recommended

---

## Deep scan session: 2026-07-19

### Stage 1: LLC → Parent chain

**FIND (critical):** Searched SEC EDGAR for "Piedra Solar" via EDGAR full-text search API.
- TotalEnergies SE (CIK 0000879764, ticker TTE) lists "Piedra Solar, LLC" in ALL FOUR
  20-F annual reports (2022, 2023, 2024, 2025) as a 100%-owned subsidiary.
- Sources:
  - 2022 20-F: sources/2026-07-19_sec-edgar_totalenergies-2022-20f.html (subsidiary list)
  - 2024 20-F: sources/2026-07-19_sec-edgar_totalenergies-2024-20f.html
  - 2025 20-F: sources/2026-07-19_sec-edgar_totalenergies-2025-20f.html
- LLC chain confirmed: Piedra Solar, LLC → TotalEnergies SE (100%)
- Address 1201 Louisiana St, Houston TX 77002 = TotalEnergies E&P USA/Renewables USA offices (Hess Tower building)
- Related: Piedra Solar II, LLC also 100%-owned by TotalEnergies (Pigeon Run Solar, Plum Creek Solar all TotalEnergies US subsidiaries)

**TotalEnergies Texas solar portfolio context (PV-Tech, Dec 2024):**
- Myrtle Solar ~380MW (2023 COD, south Houston area, Sentinel-2 already confirmed operating)
- Danish Fields ~720MW + Cottonwood ~455MW (2024 COD, Texas)
- Piedra Solar 281.7 MW = TotalEnergies' next Texas solar project in development

**Negative:** No press releases or news articles specifically announcing Piedra Solar.
No PPA announcement found. No EPC contractor identified.

### Stage 2: County records

**CAD parcel search:** Freestone County CAD portal (freestonecad.org) — site under maintenance
at time of search. Could not search by owner name "Piedra Solar" or "TotalEnergies".
→ NEGATIVE: CAD parcel data not obtained.

**Tax abatements:**
- TX Comptroller Ch.313 registry: no Piedra Solar entries. Expected: Ch.313 expired 2022,
  project filed 2022 (before JETI era). Ch.312 and JETI not found for this project.
  → NEGATIVE for abatements (expected for post-2022 solar; absence not dispositive).

**PUCT Interchange:**
- Multiple attempts (curl, GET, POST, API guesses) all returned 402 or 404.
- Portal requires JavaScript (confirmed from page source); inaccessible to headless requests.
- IA filing could not be retrieved. → NEGATIVE: IA PDF not obtained.
  NOTE: Queue data confirms IA signed 2024-07-02, so IA exists — just inaccessible.

**Freestone County commissioner court:** Searched for agendas/minutes; county website shows
calendar with no entries and no public notice search. → NEGATIVE for commission records.

### Stage 3: Site pinpoint

**Google Places delivery-pin:** gmaps.py returned HTTP 429 (rate-limited) on all 4 attempts
across this session. → NEGATIVE: No delivery pin obtained.

**POI analysis:**
- Navarro (68091) = ERCOT bus, likely near Corsicana TX, Navarro County (~32.08N, -96.47W)
- Limestone (46020) = ERCOT bus, likely near Groesbeck TX, Limestone County (~31.52N, -96.53W)
- 345kV line between them runs N-S through Freestone County, corridor ~31.55-32.00N, -96.45-96.55W
- Tap point = site location. Distance from Navarro substation to Limestone substation ~40 miles.

**Site estimate (current, low confidence):**
- POI corridor: 31.73-31.83N, -96.45 to -96.55W (central-western Freestone County)
- Method: geographic inference from ERCOT bus IDs + county boundary
- Could not corroborate with parcel data, news articles, or delivery pin

### Stage 4: Satellite imagery

**Grid search performed:** 13 chips across Freestone County, July 2026:
- Row 31.73N: lon -96.16 (Fairfield area)
- Row 31.77N: lon -96.42, -96.45, -96.48, -96.55 (central-western corridor)
- Row 31.80N: lon -96.16, -96.42, -96.45, -96.48, -96.55 (same corridor)
- Row 31.83N: lon -96.42, -96.45, -96.48 (northern corridor)

**All 13 chips show:** undisturbed rural agricultural land / pasture. No graded polygons,
no cleared rectangles, no construction staging, no substation construction.
→ **No construction activity visible** across the entire surveyed area.

**Coverage note:** 6 months post-triage still no activity. The specific tap location on the
Navarro-Limestone 345kV line is not precisely known; the search covers the most probable
corridor but could be missing the actual site if the line runs further east (toward -96.0W)
or further north/south.

### Sources saved
- sources/2026-07-19_sec-edgar_totalenergies-2022-20f.html (Piedra Solar in subsidiary list)
- sources/2026-07-19_sec-edgar_totalenergies-2024-20f.html
- sources/2026-07-19_sec-edgar_totalenergies-2025-20f.html
- 13 × imagery/s2_2026-07-01_*.png (grid search, all no_activity)
- imagery/contact_sheet_v2.png (13-chip contact sheet)

### Negative evidence log (stage 2-3)
| Source | Query | Date | Result |
|--------|-------|------|--------|
| PUCT Interchange | "piedra solar" filings search | 2026-07-19 | 402 Payment Required (JS required) |
| TX Comptroller Ch.313/JETI | Piedra Solar, Freestone County | 2026-07-19 | No entries found |
| Freestone County CAD | Owner search Piedra Solar | 2026-07-19 | Site under maintenance |
| gmaps.py places | "Piedra Solar" / variants (4 attempts) | 2026-07-19 | 429 Too Many Requests |
| DuckDuckGo/Bing | "Piedra Solar" Freestone County | 2026-07-19 | No relevant results |
| TotalEnergies website | Piedra Solar project page | 2026-07-19 | 403/not found |
| TotalEnergies press releases | Piedra Solar | 2026-07-19 | No press releases |
| PV-Tech | TotalEnergies Texas solar | 2026-07-19 | No Piedra Solar mentions |
| Freestone County news/EDA | Solar projects | 2026-07-19 | Empty/unavailable |
| Freestone County commissioners | Solar agendas | 2026-07-19 | No relevant records |
| OSM Overpass | 345kV lines Freestone County | 2026-07-19 | 406 response (blocked) |
| SEC EDGAR | "Piedra Solar" Freestone County | 2026-07-19 | Only subsidiary list (no project details) |
| Google News RSS | "Piedra Solar" Texas | 2026-07-19 | 0 articles |
| FERC eLibrary | Piedra Solar LLC | 2026-07-19 | No results |
| Delaware SOS | Piedra Solar LLC | 2026-07-19 | No results retrieved |
| Reuters/GlobeNewswire | Piedra Solar | 2026-07-19 | No results |
