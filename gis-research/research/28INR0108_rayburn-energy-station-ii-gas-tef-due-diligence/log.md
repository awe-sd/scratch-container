# Research Log — Rayburn Energy Station II Gas (28INR0108)

Research started 2026-07-19

## Identity packet
- INR: 28INR0108
- Project: RAYBURN ENERGY STATION II Gas (TEF-Due Diligence)
- County: Grayson, Texas
- Capacity: 570.0 MW
- Fuel/Technology: Gas turbine
- POI: Double Tap 138 kV Haggerty (12677) - Progress Park (#12678) & Haggerty - Winding Oaks Switch
- CDR zone: NORTH
- Reported COD (claim): 2028-02-26

## Stage 1 — LLC / Parent chain


### 2026-07-19 Stage 1 findings

**TX Comptroller (franchise tax API):** Found "RAYBURN ENERGY STATION II LLC" taxpayer 32097231602, zip 75201 (Dallas); "RAYBURN ENERGY STATION LLC" (predecessor/RES I) taxpayer 32089607363, zip 75087 (Rockwall — Rayburn Electric HQ).
Artifact: sources/2026-07-19_comptroller_api_rayburn.json

**Rayburn Electric Cooperative news releases (primary):**
- Groundbreaking June 9, 2026: 570 MW, $685M, adjacent to RES I in Sherman TX, Siemens Energy 10x SGT-800 turbines, EPC = Primoris Services Corp, commercial operations target Summer 2028
  Artifact: sources/2026-07-19_rayburnelectric_groundbreaking-pr.html
- TEF loan executed June 4, 2026: PUCT Texas Energy Fund, only cooperative selected from 125+ applicants, RES I = 758 MW combined cycle acquired after Winter Storm Uri, legal advisors: Dentons + Eversheds Sutherland, financial advisor: Jefferies
  Artifact: sources/2026-07-19_rayburnelectric_tef-loan-pr.html
- Sherman City Council approved expansion May 19, 2026, 570 MW expansion, $685M
  Artifact: sources/2026-07-19_rayburnelectric_sherman-expansion-pr.html

**Developer:** Rayburn Country Electric Cooperative, Inc. (headquartered 950 Rayburn Way, Rockwall TX 75087; ERCOT zip 75201 = Dallas registered address for the LLC)

**Turbine:** Siemens SGT-800 (10 units) - DECISIVE reality signal: Siemens industrial turbines have long lead times (1-2+ years), orders confirm committed capital

**EPC:** Primoris Services Corporation

**Location:** Adjacent to RES I (Rayburn Energy Station I, existing 758 MW combined cycle), which OSM places at 33.57772, -96.61547, Sherman TX (Hilton neighborhood)

**TEF loan:** PUCT Texas Energy Fund - Rayburn only cooperative among 17 gas projects, $5.38B total program

**Stage 1 conclusion:** Rayburn Country Electric Cooperative → Rayburn Energy Station II LLC (SPV). This is a regulated cooperative, not a speculative merchant developer. Strong institutional backing.


## Stage 2 — County records

**Grayson CAD owner search:** Portal at esearch.graysonappraisal.org is JS-based SPA; direct API calls returned "Page Not Found". No CAD parcel confirmed under "Rayburn Energy Station II" or "Rayburn Country Electric" — expected for a cooperative-owned expansion adjacent to existing RES I footprint.
  Source: 2026-07-19 — esearch.graysonappraisal.org — negative

**TCEQ NSR air permit search (Grayson County, customer=RAYBURN ENERGY, ALL statuses):**
  Result: "There are no projects for the criteria selected." — NSR permit not yet in TCEQ airperm system under this name. Also searched "RAYBURN COUNTRY" — no results. NOTE: Permit may be pending under different applicant name (e.g., cooperative entity rather than LLC), or application may not yet be in the public database. A gas turbine facility of 570 MW MUST have a TCEQ NSR permit before construction can complete — this is a gap to flag.
  Artifact: sources/2026-07-19_tceq_nsr_all_status.html

**Queue timeline (Stage 5 tool run early):**
  - IA signed 2025-12-22 (first in Jan 2026 report)
  - Meets 6.9(1) achieved 2026-06-02 (just before June 9 groundbreaking)
  - FIS not yet approved (major milestone gap)
  - COD 2028-02-26 — ZERO drift across 18 monthly snapshots (Jan 2025 → Jun 2026)
  Artifact: timeline.md

## Stage 3 — Site pinpoint

**OSM Nominatim:** "Rayburn Energy Station" at 33.57772, -96.61547, Sherman TX (Hilton neighborhood)
  Method: OSM industrial node
  
**Groundbreaking photo analysis (sources/2026-07-19_rayburnelectric_groundbreaking-photo.jpg):**
  Camera faces NW toward RES I (heat recovery stacks and turbine hall clearly visible as backdrop). Foreground = crushed gravel pad = early RES II construction site. Equipment visible at right edge. Site immediately south of RES I at approximately 33.573–33.575, -96.615.
  Method: Photographic analysis
  
**Site estimate:** 33.5750, -96.6155 (±0.003 degrees ~300m) — RES I OSM coord + photo orientation → immediately south. Confidence: medium (no parcel/address confirmation).

## Stage 4 — Satellite imagery

**s2_RESI_2026-07-01.png (6km xwide):** Large industrial complex visible at center (~33.577); characteristic CCGT structures (heat recovery, cooling towers). Adjacent cleared areas south.

**s2_tight_2km_2026-07-01.png (2km, centered 33.5777):** RES I visible lower-center with industrial footprint.

**s2_RESII_pre-gb_2026-05-01.png (2km, centered 33.5750):** Pre-groundbreaking — industrial area visible, surrounding land undisturbed.

**s2_RESII_south_2026-07-01.png (2km, centered 33.5730):** Post-groundbreaking — same area, consistent with very early construction (at 10m resolution changes from a single June 9 groundbreaking are not yet detectable in Sentinel-2).

**Imagery verdict: clearing/early_construction** — groundbreaking confirmed by primary source (June 9, 2026 press release + photo); Sentinel-2 at 10m cannot resolve individual turbine pads or concrete work started ~6 weeks ago.

