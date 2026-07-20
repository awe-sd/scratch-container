# Research Log — Great Rock BESS (25INR0230)

**Identity:** Great Rock BESS, LLC · Leon County TX · 300.9 MW BESS · POI "Tap 345kV 46020 Limestone - 967 Gibbon Creek Ckt 18" · NORTH zone · Reported COD 2027-12-20

---

## 2026-07-19 — Session start

- Stage 1 beginning: LLC search, parent chain, PUCT filings
- Stage 2 beginning: Leon County CAD, county records, tax abatements


## 2026-07-19 — Stage 1 & 2 findings

### Developer identity
- **Black Mountain Energy Storage (BMES)** is the developer — confirmed by La Marque city doc listing "Great Rock BESS · Black Mountain Energy Storage II · Tap 345kV 46020 Limestone - 967 Gibbon Creek Ckt 18 · Leon · NORTH · 307.14"
  Source: Brave search snippet from La Marque city agenda PDF (cert expired, couldn't read full doc)
- BMES = Texas developer founded 2021, known for developing and SELLING ERCOT BESS. Confirmed by energy-storage.news
- As of March 2025 (Bufflehead BESS article), Great Rock is still in BMES pipeline (not sold yet)
- BMES newsroom: no Great Rock sale announcement through July 2026
- Note: "25INR0231 Apache Hill BESS" is a sibling project at nearby POI (Hood county)

### LLC search
- TX Comptroller COA search: redirects, couldn't retrieve entity record
- PUCT Interchange: requires JavaScript, no IA found yet for Great Rock BESS

### POI geography
- "Tap 345kV 46020 Limestone - 967 Gibbon Creek Ckt 18" = tap on the 345kV line between NRG Limestone power plant and Gibbons Creek power station
- **NRG Limestone** (Google Maps pin): 31.423326, -96.251477 — Jewett, TX (Leon County) — 3964 FM 39
- **Gibbons Creek**: 30.620243, -96.081775 — Grimes County
- Project site must be in Leon County, along or near this 345kV corridor
- The site is likely NORTH of Jewett toward the Limestone plant, or along the line southward

### Negative evidence
- No Google Maps pin for "Great Rock BESS" (no delivery pin registered)
- BMES newsroom does not name individual project locations
- La Marque doc cert expired — couldn't read full project list


## 2026-07-19 — Stage 3/4 findings

### Geographic anchor — POI analysis
- Limestone plant (NRG, bus 46020): 31.423326, -96.251477 — Jewett TX (Leon County)
- Gibbons Creek plant (bus 967): 30.620243, -96.081775 (Grimes County)
- 345kV line runs S-SE between these two plants through Leon County
- At southern Leon County (lat~31.05-31.14), the line passes through approx lon -96.17 to -96.19

### Great Rock Energy Hub — MAJOR FIND
- Queue parquet reveals a **3-project energy hub** at the "Great Rock" site in Leon County:
  1. **25INR0230 Great Rock BESS** (300.9 MW BESS) — POI: Limestone-Gibbon Creek 345kV Ckt18
  2. **25INR0513 Kahla Storage** (200.9 MW BESS) — POI: Limestone-Gibbon Creek 345kV Ckt50 (same corridor)  
  3. **30INR0091 BM Great Rock Energy Center** (1,981 MW gas CC) — POI: LIMEST_POI_5 (same new tap)
  4. **29INR0366 BM Great Rock Energy Center II** (990.6 MW gas) — same county, no POI yet
- "BM" prefix = Black Mountain Energy Storage is the developer (confirmed)
- "LIMEST_POI_5" = a new planned 345kV substation tap along the Limestone-Gibbon Creek corridor

### Spatial proxy
- Pecan Prairie South Solar at 31.049, -96.217 (same 345kV corridor, Yellow Wolf bus)
- Pecan Prairie North Solar at 31.135, -96.263
- Great Rock tap is likely 1-5 km from Pecan Prairie sites, in the same FM 3/Normangee area

### Satellite imagery — Stage 4
- Full Limestone plant area (31.42, -96.25, 6km buffer): NRG Limestone plant complex visible, mine SE, no BESS construction — expected (construction start Oct 2026)
- Corridor chips (tight 2km buffer) at 3 points along 345kV line: all show undisturbed farmland/forest
- Normangee area chip (31.08, -96.235, 3km buffer): rural farmland, no BESS pads
- 345kV tap estimate area (31.10, -96.183, 3km): CDSE auth expired before pulling

### CDSE status: 401 Unauthorized — imagery production halted
- 3 corridor chips + 2 wider chips already pulled and inspected — all show no_activity
- Consistent with reported construction start 2026-10-20

### PUCT IA — NOT FOUND via automated tools
- PUCT requires JavaScript for search — direct document URL not recoverable without item number
- IA signed 2024-08-23 confirmed from queue parquet milestone
- Negative: could not access PUCT IA PDF to get financial security, milestones, schedule

### Leon County CAD — NOT FOUND
- leoncad.org returns 500 errors and 404s on search endpoints
- No parcel records found for Great Rock BESS LLC or BMES in Leon County

