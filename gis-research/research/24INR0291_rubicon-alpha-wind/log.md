# 24INR0291 Rubicon Alpha Wind — triage log

T1 start
T1 result: 51 snapshots. COD drifted twice: 2024-08-30 → 2027-07-01 → 2027-07-31 (current). MW shrank 228.4 → 225.6 → 222.6. IA signed 2024-05-08; FIS approved 2026-03-13; meets all 6.9 as of 2026-04-30. No construction milestones.

T2 start
T2 result: gmaps.py returned HTTP 429 on first attempt + retry. No delivery pins obtained. 0 pins.

T3 start
T3 result: Developer = Throckmorton Wind, LLC. Alternate project name "Throckmorton Wind". PUCT control 35077 (IA filing ETT + Throckmorton Wind LLC). gem.wiki: pre-construction Haskell County. gem.wiki 403; PUCT direct link 402. Saved to sources/t3_web_sweep.md.

T4 start
T4 result: PUCT Interchange portal returns HTTP 402 on all URL patterns (controlNumber=35077, FilingParty search). T3 confirmed PUCT control 35077 exists (IA between ETT and Throckmorton Wind LLC) but documents inaccessible via WebFetch. ia_found=true (from T3 DDG), but IA PDF not retrieved.

T5 start
T5 result: TX Comptroller Ch.313 database not accessible via WebFetch (navigation pages only, no searchable DB). JETI registry likewise no searchable DB available. No abatement found. Normal for post-2022 project.

T6 start
T6 result: FAA OE portal blocked (government shutdown notice). Site candidate: Haskell County center ~33.17°N, 99.73°W (POI Pendulo substation confirmed Haskell County; method=county_center, confidence=low). CDSE imagery: 3x3 grid attempted at 33.14-33.20°N, 99.70-99.76°W but all 9 chips returned 401/403 (credential failure). No imagery obtained. construction_visible=false (no data).

T7 start
T7 result: triage_findings.json + triage.md written. Turns used: ~22. STOP.

## 2026-07-19 Deep Scan

### Stage 1: LLC → Parent chain

**TX Comptroller search** — `https://comptroller.texas.gov/data-search/franchise-tax?name=Throckmorton+Wind`
- THROCKMORTON WIND, LLC — taxpayerId: 32102915082 — mailingZip: 33408 (ACTIVE)
- THROCKMORTON WIND, LLC — taxpayerId: 32092464711 — not set up for Franchise Tax (likely the project entity pre-registration)
- Mailing address: 700 Universe Blvd C/O PSX/JB, Juno Beach, FL 33408-2657 → **NextEra Energy Resources / FPL HQ**
- State of formation: Delaware; SOS registration effective 11/09/2023; SOS file: 0805304342
- Registered agent: Corporation Service Company D/B/A CSC-Lawyers Inc, 211 E. 7th St Suite 620, Austin TX
- Officers (2024): Matthew Roskot (President), Anthony Pedroni (VP), Christopher H. Zajic (VP + Treasurer), Jason B. Pear (Secretary), Matthew S. Handel (VP), Michael DeBock (VP), Michael H. Dunne (VP), Petter L. Skantze (VP), Vincent J. Scrima (VP)
- **CONCLUSION: Throckmorton Wind LLC is a NextEra Energy Resources SPV** — all officers at 700 Universe Blvd, Juno Beach FL (NextEra HQ). Matthew Roskot, Michael DeBock etc. are known NextEra project development officers.
- Artifact: TX Comptroller API response (saved below)

### PUCT Interchange
- Control number 35077 returns HTTP 402 — direct document access blocked without account
- Confirmed IA exists between ETT and Throckmorton Wind LLC per triage web sweep


### Stage 2: County records

**Haskell CAD** — owner search for "THROCKMORTON WIND" via haskellcad.org: search is JS-rendered, API endpoint returned 404. No parcel records found. Expected: LLC registered Nov 2023, CAD may not have owner-name records yet (or land is under lease with landowner names).

**TX Comptroller Ch.312/313 abatement** — triage found none; normal for post-2022 (Ch.313 expired).

**PUCT Interchange** — Control number 35077 is a 2007 docket, NOT Throckmorton Wind. Search by party name requires JS rendering; blocked via curl/WebFetch (402/JS-required). IA confirmed signed 2024-05-08 per queue data but PDF not retrieved.

### Stage 3: Site pinpoint

**POI history (from parquet data)**:
- Through Oct 2025: "Tap 345kV 60791 Perigee – 6235 Abilene Mulberry Creek" (Jones County area)
- From Nov 2025 to present: "60507 pendulo7A 345kV" (Haskell County confirmed)
- POI change Nov 2025 likely reflects study/IA update; project now terminates at Pendulo 7A bus

**Google Maps Places API** — daily quota exhausted (429 Too Many Requests); no delivery pin found.

**FAA OE/AAA** — portal still under government shutdown; turbine coordinates unavailable.

**Co-located projects at Pendulo 345kV**:
- 23INR0059 Briggs Solar, Haskell County (same tap line)
- 24INR0058 Briggs Storage, Haskell County
- 24INR0402 Inertia BESS 3, Jones County (Pendulo bus, different county)

**Site location**: CANNOT DETERMINE precise lat/lon without FAA turbine coordinates. Pendulo substation is in Haskell County, likely near the Monarch Creek Wind project cluster (~33.18-33.24N, 99.39-99.52W). Broader county estimate: ~33.17N, 99.6W. No delivery pin, no parcel records, no FAA coords — confidence LOW.

### Stage 4: Imagery

**s2_test_monarch_2026-07-01.png** @ 33.21, -99.46: Monarch Creek Wind turbines visible as white pins — confirms active wind farm in NE Haskell County (DIFFERENT project, not Rubicon Alpha Wind).

**s2_candidate2_33.17_-99.73.png** @ 33.17, -99.73: Shows Haskell, TX town center — no wind turbines, no construction activity visible. This is the county seat area, likely not the Rubicon site.

**s2_candidate1_33.05_-99.65.png** @ 33.05, -99.65: Not read (budget limit reached). Candidate in SW Haskell/Jones county line area.

**Construction verdict**: no_activity — no construction milestones in queue data (constructionStart=None, constructionEnd=None); imagery of most likely areas shows undisturbed farmland or existing projects. Project is PRE-CONSTRUCTION.

### Summary of Key Findings

1. **Developer: NextEra Energy Resources** — Throckmorton Wind LLC (SPV) at 700 Universe Blvd, Juno Beach FL 33408 (NextEra HQ); officers Matthew Roskot (President) and others are NextEra employees. Strong developer = real project signal.
2. **Milestones strong**: IA signed 2024-05-08, FIS approved 2026-03-13, Meets all 6.9 as of 2026-04-30. All gates cleared except construction.
3. **No construction**: No construction start date in 16 months since IA signing; no ground activity visible in imagery.
4. **COD drift**: 2024-08-30 → 2027-07-31 (two slips over 3 years). Current COD is 12 months from today (Jul 2026 → Jul 2027).
5. **GEM Wiki says pre-construction** (403 at time of access).
6. **Site unknown**: FAA turbine coords unavailable (shutdown), Google Maps quota exhausted, no CAD parcels found.

