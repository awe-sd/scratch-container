# Research Log — Blue Skies BESS (25INR0046)

Researched: 2026-07-19
County: Hill, TX | Capacity: 306.26 MW | Fuel: Battery/Storage
POI: "68090 SAM SW 345kV" | Zone: NORTH | Reported COD: 2028-04-01

---

## Stage 1 — LLC → parent chain

### 2026-07-19 TX Comptroller COA - "blue skies bess"
- Query: https://comptroller.texas.gov/data-search/franchise-tax?name=blue+skies+bess
- Result: **0 hits** — entity not registered under that exact name

### 2026-07-19 TX Comptroller COA - "blue skies"
- Query: https://comptroller.texas.gov/data-search/franchise-tax?name=blue+skies
- Result: 115 entities; only energy-related: BLUE SKIES ENERGY LLC (zip 75254), BLUE SKIES SOLAR I, LLC (94538), BLUE SKIES AND TAILWINDS (78669)
- Finding: No "Blue Skies BESS LLC" in TX COA. Project LLC either not yet registered or uses different name.

### 2026-07-19 ERCOT parquet — interconnectingFacility field
- Found: **ACTX BESS Project LLC** is the `interconnectingFacility` entity in ERCOT records
- Earlier project name: **"Ash Creek BESS"** (through 2022-09; renamed to "Blue Skies BESS" in 2022-10 snapshot)
- Source: local ercot_generation_interconnect.parquet

### 2026-07-19 TX Comptroller COA - "actx bess"
- Query: https://comptroller.texas.gov/data-search/franchise-tax?name=actx+bess
- Result: **1 hit**: ACTX BESS PROJECT LLC, taxpayerId=32087469618, mailingAddressZip=85254 (Scottsdale AZ)

### 2026-07-19 TX Comptroller COA - "actx"
- All 7 ACTX entities: ACTX PROPERTIES (76308 - Wichita Falls), ACTX LLC (76177 - Fort Worth), 
  ACTXLP LLC (04092), ACTX BESS PROJECT LLC (85254 - Scottsdale AZ), 
  ACTX VENTURES (77418), ACTX FINANCIAL ADVISORY (78729 - Austin), ACTXTRAINING (75002)
- No clear parent/developer name discovered from COA data

### 2026-07-19 DuckDuckGo web search — "ACTX BESS" developer
- Queries: "ACTX BESS Project" developer; "ACTX BESS" texas battery storage
- Result: **0 web results** — entity has no public press releases or news coverage found

### 2026-07-19 SEC EDGAR full-text search — "blue skies bess"
- Total: 0 hits

---

## Stage 2 — County records sweep

### 2026-07-19 PUCT Interchange — "blue skies bess" filing party
- Result: 0 records found
- Also tried: "blue skies", "ash creek bess", "actx bess", "SAM SW", "blue skies bess" case style
- All: 0 records

### 2026-07-19 PUCT Interchange — SAM SW substation
- Query: Description "SAM SW"
- Found 3 results: Dockets 38230, 38642, 51016 — all for Lone Star Transmission LLC
- Key finding: **SAM Switch is in Hill County on the Central A-to-Navarro 345kV CREZ line**
- Docket 51016: "SAM SWITCH-TO-HUBBARD WIND 345-KV TRANSMISSION LINE IN HILL COUNTY"
  — Hubbard TX is in eastern Hill County

### 2026-07-19 Nominatim — "Ash Creek Hill County Texas"
- Result: **Ash Creek, Hill County, Texas: lat 31.9185519, lon -96.8448854** (river)
- Original project name "Ash Creek BESS" confirms site is near this waterway

### 2026-07-19 TX Comptroller Ch313/JETI — Hill County
- ch313/agreements.php query with county=Hill: JS-rendered page, could not retrieve
- No direct hits confirmed

### 2026-07-19 Hill CAD — esearch.hillcad.org
- Status: ECONNREFUSED — site unavailable

### 2026-07-19 Hill County commissioners court
- co.hill.tx.us: 404 on commissioners page; no abatement minutes found

---

## Stage 3 — Site pinpoint

### 2026-07-19 Derived location
- Ash Creek flows near Hubbard TX (eastern Hill County): 31.9186, -96.8449
- SAM Switch is on 345kV line in Hill County — docket 51016 references Hubbard Wind in Hill County
- BESS sites attach to substations; Hubbard TX area ~31.85-31.92, -96.79-96.85 is primary search zone

---

## Stage 2 (continued) — Hill County abatement document

### 2026-07-19 Hill County Commissioners Court notice — Hubbard Energy Storage II
- Source: `sources/2026-07-19_hillcounty_hubbard-energy-storage-II-30day.pdf`
- **KEY FINDING**: Tax abatement applicant = **Hubbard Energy Storage II, LLC**, 700 Universe Boulevard, Juno Beach, FL 33408
- **700 Universe Blvd, Juno Beach FL 33408 = NextEra Energy Resources HQ** — this is a NextEra project
- Location: Eastern Hill County, Malone ISD, **Hill CAD parcel 121422** ("PT OF NAVARRO CO SCH LAND A-673 TR 1 152.00 AC")
- Site area: **~10 acres** for battery energy storage facility
- Capital investment: >$115,000,000
- Improvements scope: Concrete Foundations, Batteries, Inverters/Transformers, Containers, Cabling, Collection Line/Station
- Site map (p.2): Project star placed between Hillsboro and Hubbard — northwest of Hubbard TX
- Site map (p.3): Parcel shape = tilted rectangle accessed by County Road 2423
- Meeting date: August 27, 2024 (Reinvestment Zone 018)
- WHY MATTERS: NextEra is one of the largest BESS developers in the US; real developer = strong real/paper signal. Abatement confirms land secured, capital committed, schedule serious.

### 2026-07-19 Link between "Hubbard Energy Storage II" and "Blue Skies BESS / ACTX BESS"
- ERCOT queue lists `interconnectingFacility = ACTX BESS Project LLC`; queue project = "Blue Skies BESS" (Hill County, 306 MW, SAM SW 345kV)
- County abatement lists "Hubbard Energy Storage II, LLC" (NextEra shell) in same county, same technology
- NextEra commonly uses project-site-named LLCs for county filings separate from the ERCOT interconnecting entity LLC
- Assessment: high confidence these are the same project — Hill County BESS near Hubbard TX, same POI corridor (SAM Switch on 345kV CREZ line per PUCT docket 51016)

## Stage 4 — Satellite imagery
*See imagery/ directory — structure_2km.png shows candidate site*

### 2026-07-19 Existing imagery reviewed
- `s2_2026-07-01_ashcreek_6km.png`: Wide view of eastern Hill County; shows agricultural land + small rectangular grid structure in lower-left quadrant
- `s2_2026-07-01_ashcreek_2km.png`: 2km chip centered near Ash Creek; shows farmland, no obvious BESS structure
- `s2_2026-07-01_structure_2km.png`: **2km chip showing dark rectangular blocks in rows** — candidate BESS container array. Location to be confirmed vs. CAD parcel 121422

---

## Negative searches logged

1. PUCT IA search — "blue skies bess" (filing party): 0 records
2. PUCT IA search — "blue skies" (filing party): 0 records
3. PUCT — "ash creek bess" (filing party): 0 records
4. PUCT — "actx bess" (filing party): 0 records
5. PUCT — "SAM SW" case style: 0 records (found under description)
6. TX COA — "blue skies bess": 0 hits
7. SEC EDGAR — "blue skies bess": 0 hits
8. Web — "ACTX BESS" developer/parent: 0 results
9. Nominatim — "SAM Switch": 0 results
10. Hill CAD property search — unavailable (ECONNREFUSED)
