# Research log — Renegade Project (20INR0255)
Deep scan started 2026-07-19. Picking up from triage (2026-07-18).

## Triage summary (inherited)
- IA signed 2021-01-04; Ch.313 App 1422 with Hereford ISD, Deaf Smith County; 10 COD slips since 2019
- Construction-start reported 2026-03-01 in queue; no imagery captured (CDSE 401)
- Site candidate: Hereford, TX area (low confidence, county-seat proxy)
- Deep scan priority: PUCT IA doc, Ch.313 PDF parcel coords, CDSE imagery, developer identity

## 2026-07-19 — Ch.313 document fetch (Tasks 1–3)

### Sources fetched
- `sources/2026-07-19_comptroller_ch313_1422_renegade_app.pdf` — 20.8 MB, HTTP 200 (too large to read directly; agreement PDF read instead)
- `sources/2026-07-19_comptroller_ch313_1422_renegade_agreement.pdf` — 1.8 MB, HTTP 200, fully read (31 pp + exhibits)

### Key findings — Agreement (Comptroller App 1422, dated 2020-11-23)

**Entity names:**
- Applicant: Renegade Renewables, LLC d/b/a Dawn Solar (Texas Taxpayer ID #32061841139)
- School district: Hereford Independent School District
- Reinvestment zone: "Deaf Smith-Renegade Reinvestment Zone" (created by Deaf Smith County Commissioners Court, Resolution dated December 11, 2018)
- Applicant's authorized signatory: Allen B. Funk, Authorized Signatory
- CFO contact: David Mitchell, c/o Blue Planet Funding, 311 West 43rd Street, 12th Floor, New York, NY 10036; dmitchell@blueplanetfunding.com; (646) 515-0622
- Managing Member / copy-to: Sean Purdy, Everett Jones, LLC, 136 Market Street, Sunbury, PA 17801; everettjonesinv@gmail.com; (570) 259-9203
- District counsel: Underwood Law Firm, P.C. (Fred Stormer), 500 S. Taylor St Suite 1200, Amarillo TX 79101; (806) 379-0306

**Project description (Exhibit 3):**
- Dawn Solar — 650 MW DC solar PV farm, Deaf Smith County, TX, within Hereford ISD
- ~1,950,000 solar PV modules on single-axis trackers
- DC → inverter → 480V AC → transformers → 34.5 kV collection system → substations
- Includes generation transmission tie line within project boundary
- Mortenson (EPC, per map title block); Blue Planet Funding (investor/developer)
- Project map prepared December 6, 2018 (site selection map)

**Investment / schedule (from agreement):**
- Qualified Investment (Ch.313 minimum): $30,000,000
- Application filed: 2019-08-26
- Application Review Start Date: 2019-11-14
- Comptroller certificate issued: 2020-02-07
- Agreement approved/signed: 2020-11-23
- Qualifying Time Period: 2020-11-23 → 2022-12-31
- Tax Limitation Period: 2022-01-01 → 2031-12-31 ($30M appraised value cap for M&O)
- Final Termination Date: 2036-12-31
- Construction implied COD: tax limitation starts Jan 1, 2022 ("first complete tax year after commercial operation") → original expected COD ~2021

**Land description — EXHIBIT 1 (Reinvestment Zone, 11 tracts):**
Deaf Smith-Renegade Reinvestment Zone, Resolution dated December 11, 2018:
- Tract 1: All of Section 17, and West part of Section 18, Block 3, Deaf Smith County — ~811 acres (SAVE AND EXCEPT: Genevieve Miller residence/well life estate)
- Tract 2: All of Section 6, ~636 acres, Block K14, Tap RR Co. Survey, Deaf Smith County
- Tract 3: ~130 acres, Shaw Survey, Deaf Smith County
- Tract 4: ~315 acres, West ½ of Section 24 (except ~6 acres homestead), Block 3, AB&M Survey
- Tract 5: ~195 acres, East 195 acres out of West ½ of Section 5, Block K-1, Deaf Smith County (does not extend to North section line)
- Tract 6: East Half (E/2) of Section 5, Block K-14, Abstract 292 — 303.88 acres (excluding 3-acre Alice Celeste Thompson deed from W/2 NE corner)
- Tract 7: ~126 acres, East side of Section 25, Block 3, AB&M Survey and NW corner of Section 17, North and West of U.S. Hwy. 60, Block K-14, Tap RR Co. Survey (SAVE AND EXCEPT ~61 acres NW corner of Section 17, north of Hwy 60, permanently fenced)
- Tract 8: All of Section 7, Block K-14, Tap RR Co. Survey, Deaf Smith County
- Tract 9: All of Section 8, Block K-14, Tap RR Co. Survey — North and West of Highway 60
- Tract 10: All of W.A. Hunt Preemption Survey, Abstract No. 537, Deaf Smith County
- Tract 11: All of M.H. Cahill Preemption Survey, Abstract No. 535, Deaf Smith County

**Land description — EXHIBIT 2 (Qualified Investment Land, 16 tracts — more detailed metes and bounds):**
Tract One: West 128.58 acres out of West ½ of Section 5, Block K-14, Certificate No. 988, T.&N.O. R.R. Co. Original Grantee, Patent No. 570, Volume 26, Deaf Smith County (SAVE AND EXCEPT 14.93-acre tract; prior owner Robert Wilson Womble Instrument #97-0977)
Tract Two: South 124.18 acres, D.W. Dillon Tract, Patent No. 338, Volume 20, File No. SF 277 (patented 1901-05-28)
Tract Three: All of Section 17 and West part of Section 18, Block 3, ~795 acres (Genevieve Miller life estate exception)
Tract Four: All of Section 6, ~636 acres, Block K14, Tap RR Co. Survey
Tract Five: ~130 acres, Shaw Survey
Tract Six: ~315 acres, West ½ of Section 24 (except ~6 acres homestead), Block 3, AB&M Survey
Tract Seven: ~195 acres, East 195 acres out of West ½ of Section 5, Block K-14, Tap RR Co. Survey (does not extend to North section line)
Tract Eight: East Half (E/2) of Section 5, Block K-14, Abstract 292, 303.88 acres (excluding 3-acre Alice Celeste Thompson deed)
Tract Nine: ~126 acres, East side of Section 25, Block 3, AB&M Survey and NW corner of Section 17, North and West of U.S. Hwy. 60, Block K-14, Tap RR Co. Survey
Tract Ten: ~90 acres, SE corner of Section 25, Block 3, AB&M Survey — South and East of U.S. Hwy 60 and RR right-of-way
Tract Eleven: All of Section 17 and South ½ of Section 18, Block K-14, Tap RR Co. Survey (SAVE AND EXCEPT ~61 acres NW corner of Section 17, Block K-14, north of Hwy 60)
Tract Twelve: All of Section 7, Block 3, AB&M Survey
Tract Thirteen: All of Section 8, Block K-14, Tap RR Co. Survey — North and West of U.S. Hwy. 60
Tract Fourteen: All of W.A. Hunt Preemption Survey, Abstract No. 537
Tract Fifteen: All of M.H. Cahill Preemption Survey, Abstract No. 535
Tract Sixteen: ~309 acres, South ½ of Section 18, Block K14, Deaf Smith County (SAVE AND EXCEPT 10-acre NE corner tract)

**Roads and landmarks from map (Exhibit 1 aerial map, dated December 6, 2018):**
- County Road 12 (labeled on east side of project)
- County Road CC (labeled on north-south road within project interior)
- Highway 60 / U.S. Hwy. 60 (southern boundary — project spans both sides at Section 17/25 junction)
- RR right-of-way (near SE corner of project, parallels Hwy 60)

**Land descriptions include prior deed references (Exhibit 2):**
- Josef C. Grotegut, et ux — 8.92-acre tract, Volume 330, Page 869, Deed Records
- Wayne Betzen, et ux — 180.15-acre tract, Instrument Number 98-0573, Official Public Records
- Robert Wilson Womble, et al — 128.58-acre tract, Instrument Number 97-0977, Official Public Records
- Genevieve Miller — life estate in residence on Section 17/18, Block 3

**Qualified property (Exhibit 4):** ~1,950,000 PV modules on single-axis trackers, inverters, combiner boxes, 34.5 kV collection, electrical substations, gen transmission tie line, interconnection facilities. All within Hereford ISD and Deaf Smith County.

**Project design parameters (from Mortenson layout map, Exhibits 3 & 4):**
- Project name on map: "Trace 2 - Dawn Solar"
- Location: Amarillo, Texas (nearest weather station: Amarillo Rick Husband Intl Airport)
- Extreme Max Temp: 42.78°C
- Ground Snow Load: 1 psf
- Windspeed (3 sec peak gust): ~502.785 ft/s equivalent
- Module area MACC AC PO: 681,152
- TMY/C PO D/SARGE: 1.304
- Ground Cover Ratio: 0.35 (approximately)
- Single inverter output (MWAC): 5.93
- Number of inverters: 690
- Single inverter output with delay (MWAC): 5.1483
- Trackers: 36 module/tracker, 84-row; 56-module trackers: 275 modules per string → 278 strings
- Quantity of Trackers: 56-row: 11,766; 84-row: 22,376
- Total Quantity of Modules: 1,950,994
- Total AC Output (MWAC): ~3,790 MWAc (note: this is the layout MW, not the ERCOT queue MW)
- Block Configuration: 138
- Total number of inverter skids/Nameplates: 1,138 (56-row) + 138 = total; 3,790 MWAc total modules: 1,7607 MWAc

**PUCT Interchange (Task 2):** PUCT Interchange returns HTTP 402 from this environment (authentication required). Cannot search directly. Known context: IA signed 2021-01-04 per ERCOT queue data; POI = "Tap 345kV 23910 Windmill - 23906 AJ Swope"; TSP is likely Xcel Energy/SPS (Panhandle area). PUCT docket search must be done from a browser or authenticated session.

### No lat/lon coordinates found in agreement document
The Ch.313 agreement and exhibits contain only metes-and-bounds legal descriptions and survey references (Block K-14, Block 3, AB&M Survey, Tap RR Co. Survey). No GPS coordinates or parcel IDs (CAD account numbers) are present. The Deaf Smith County Appraisal District would have the CAD IDs for these parcels.


## 2026-07-19 — Deep scan Stage 1-3 (this session)

### Developer identity (Stage 1)

- **Blue Planet Funding confirmed as developer** — BPF project page at blueplanetfunding.com/projects lists "Dawn Solar - in progress, 683 MW, Deaf Smith County TX" with URL slug "renegade-renewable-llc"
  - `sources/2026-07-19_blueplanetfunding_dawn-solar-project-page.html` saved
  - Allen Funk (COO at BPF) = same Allen Funk who signed Ch.313 agreement as "Authorized Signatory" — confirms BPF = developer
  - CFO David Mitchell, c/o Blue Planet Funding, 311 West 43rd Street, 12th Floor, New York, NY 10036
  - Managing Member: Sean Purdy, Everett Jones, LLC, Sunbury PA
- Entity: Renegade Renewables, LLC d/b/a Dawn Solar (TX Tax ID #32061841139)
- No public PPA, financing, or EPC announcements found in web search (no PRs)
- EPC: Mortenson per Ch.313 docs (2018 design map title block); unconfirmed whether still EPC at construction start

### POI location research (Stage 2/3)

- AJ Swope and Windmill substations are on the 345kV AAWOTC line in the TX Panhandle (ERCOT 2015 study, source `2026-07-19_puct_45622_2_sps_transmission_study.pdf`)
  - AJ Swope = Oldham County (Spinning Spur Wind projects connect there — INR 131NR0048, 141NR0053)
  - Windmill = Castro County (Jumbo Road Wind INR 131NR0059b connects there)
  - Renegade Project POI = tap BETWEEN these on the 345kV line → Deaf Smith County
- TSP appears to be SPS/Xcel Energy (Panhandle area), not Oncor (PUCT Interchange returns 402)
- PUCT Interchange: returns 402 (payment required) from this environment; IA docket not accessible

### Site pinpoint attempts (Stage 3)

- Google Places API: 429 rate limited
- Hereford center chip (34.376°N, -102.397°W): undisturbed farmland, no construction activity
- CDSE: working for first chip (hereford center confirmed), then account blocked (403 on token)
  - One image captured: `imagery/s2_hereford_center_2026-06.png` — farmland, no solar

### Ch.313 land description → site area

From agreement exhibit, the project tracts include:
- Sections 5,6,7,8,17,18 Block K-14, Tap RR Co. Survey + Block 3 AB&M Survey, Deaf Smith County
- Highway 60 as southern boundary for some tracts
- Hereford ISD district (confirmed site is within Hereford ISD boundaries)
- Total reinvestment zone area ≈ 811+636+130+315+195+304+126+~800+~600+~600+~309 acres ≈ 4,800+ acres across 16 tracts
  → consistent with 683 MW DC solar at ~10 acres/MWdc = 6,830 acres total or ~4-5 acres/MWdc needed for 515 MWac

### Negative findings

- NEGATIVE: No web news/press releases about financing, EPC, PPA, or groundbreaking for Renegade Project/Dawn Solar
- NEGATIVE: Deaf Smith CAD search requires browser/CSRF token, can't query by API from this environment  
- NEGATIVE: PUCT Interchange returns 402 (auth required from this IP)
- NEGATIVE: TX Comptroller franchise tax search requires form submission (redirects to search page)
- NEGATIVE: CDSE account blocked (403 on OAuth token endpoint after first chip)

