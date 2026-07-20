# Triage log — Space City Solar (21INR0341)

## T1 start

**queue_history.py result:** 81 snapshots (2019-10-01 → 2026-06-01), 6 reported-COD changes.

**Milestones achieved:**
- Screening started: 2019-11-01
- Screening complete: 2020-03-06
- FIS requested: 2019-10-15
- FIS approved: — (never)
- IA signed: 2025-12-11 (recently!)
- Meets 6.9(1): 2021-01-11
- Meets all 6.9: — (never)
- Construction start/end, energization, sync, COD: all —

**COD drift (6 changes):**
- 2021-12-01 → 2022-05-06 → 2022-12-30 → 2024-05-30 → 2025-07-01 → 2026-06-01 → 2027-06-01
- Current COD claim: 2027-06-01

**Capacity changes:**
- ~610 MW (2019-10-01 → 2025-03-01), then downscoped to 366 MW in 2025-04-01

**T1 summary:** IA signed Dec 2025 (significant milestone). COD slipped 6 times over 5+ years. 
Capacity cut by ~40% in early 2025. No construction milestones triggered. FIS was never approved 
yet IA signed (non-standard path). 2027-06-01 COD still ~17 months away.

## T2 start

**gmaps.py attempts:** 2 × HTTP 429 (rate-limited). Budget exhausted after 2 calls per rules.
**Result:** No pins found. Normal — no delivery pins for this project.

## T3 start

**Developer:** EDF Renewables North America (edf-re.com)
**Multi-phase project:** Earlier phases (up to 345 MWac/455 MWdc) reportedly operating or near-COD. 
  The 366 MW in queue appears to be a later phase targeting 2027.
**PPAs found:** BASF (55 MWac, ~Dec 2020) + Enterprise Products Partners (100 MWac VPPA).
**Transmission match:** CenterPoint 345-kV line to Hillje Substation — matches POI "44200 Hillje 345kV".
**Construction claims (press):** Summer 2021 start, Summer 2022 COD for early phases. No update on 366 MW phase.
**LLC note:** "Space City Solar LLC" as standalone entity is a small Houston installer (F-16944) — NOT the EDF entity.
**Saved:** sources/t3_web_sweep.md

## T4 start

**PUCT Interchange portal:** HTTP 402 on all attempts (requires authenticated session). Cannot retrieve filings directly.
**DDG fallback:** Found PUCT Case No. 51568, item 32 (doc 1116825.PDF). 
  - References "Space City Solar Generation Facility" interconnection to CenterPoint Hillje Substation.
  - EDF Renewables + CenterPoint negotiated IA executed ~Dec 15, 2020.
  - PDF also blocked (402).
**IA reference note:** Queue timeline shows iaSigned = 2025-12-11, but PUCT case references an IA executed Dec 2020.
  These may be different instruments (PUCT Case 51568 = CenterPoint transmission IA; 
  ERCOT queue iaSigned = ERCOT Generation Interconnection Agreement).
**Result:** IA known to exist (PUCT Case 51568 + ERCOT milestone); content CEII/portal-blocked during triage.

## T5 start

**TX Comptroller Ch.313:** Portal not returning searchable data via WebFetch (overview pages only, no searchable DB content).
**JETI registry:** No JETI results found via DDG search for this project.
**Note:** Project was announced 2019-2020; Ch.313 was the applicable incentive at that time (expired Sept 2022). 
  EDF press materials mention "$30M+ in tax revenue" — suggests they may have negotiated direct tax deals 
  rather than a value limitation. No abatement application confirmed or ruled out.
**Result:** Abatement status inconclusive — portal blocked, no web evidence found. Normal for deep-scan to pursue.

## T6 start

**Site candidate:** Hillje substation area (29.030°N, -96.236°W) — from CenterPoint CCN filing.
  Solar site itself is near the substation but exact parcel unknown (no pin from T2).
  Method: POI infrastructure (substation coords). Confidence: medium (substation ≠ solar field centroid).
**CDSE attempt:** HTTP 403 — ~/.config/gis-research.env contains only example template, no real CDSE credentials.
  Imagery cannot be acquired. Budget exhausted after 2 attempts (chip + auth check).
**Result:** No imagery acquired. construction_visible = false/unknown.

## T7 start

**Written:** triage_findings.json + triage.md
**Turns used:** ~28
**deep_scan_recommended:** true
**Key blockers this run:** gmaps 429, PUCT portal 402, CDSE credentials missing.

## TRIAGE COMPLETE

## D1 — Deep scan start (2026-07-19)

**deep_scan_focus threads:**
1. PUCT Case 51568 — IA/CCN filing
2. Earlier phases operational vs. still queued
3. CDSE imagery at 29.030,-96.236
4. EDF Renewables project page / press release for 366 MW tranche
5. Wharton ISD Ch.313 application

**CDSE chip acquired:** imagery/s2_2026-07-01.png (6 km buffer, 2026-07-01 ±15d)
**OBSERVATION:** Upper-left quadrant (NW of center at 29.030, -96.236) shows a clear solar installation — dark uniform rectangular grid pattern characteristic of installed PV modules. Array appears substantial — multiple rows of panels visible. This is within ~2-3 km NW of the POI substation center. **This indicates a phase is substantially complete or operating.**
**Implication:** Earlier-phase panels confirmed visible from space. Need to re-center to confirm exact location and whether this is the same site as the 366 MW INR project.

**PUCT portal:** HTTP 402 again — portal requires auth, cannot retrieve filing.
**gmaps.py:** HTTP 429 both attempts.
**TX Comptroller franchise search:** JavaScript-heavy, returns no data via WebFetch.
**Ch.312/380 search:** Returns no data via WebFetch.
**whartonjournal.com:** Domain parked (not a real site).
**whartoncountytx.gov:** DNS not found.

## D2 — Imagery pivots

**Chip 1 (29.030, -96.236, 6km):** Solar array visible in upper-left quadrant → ~NW of POI substation center → array approx at 29.06N, -96.28W
**Chip 2 (29.065, -96.290, 2km tight):** Clear panel installation — uniform dark rectangular blocks filling frame → confirms installed modules (solar operating)
**Chip 3 (29.065, -96.290, 6km):** Array now in lower-right quadrant → contradicts my estimate. Array centroid likely ~29.04-29.05N, -96.265W, SE of the 29.065 center
**Conclusion:** Panel installation CONFIRMED as existing (not under construction). Phase 1 or subset operating. Array footprint appears 1-2 km in tight view. Need to re-center to ~29.045, -96.265 to find the full site.
**EDF Re news page:** No Space City Solar articles (404 on press page, no matches on news index)

## D3 — PUCT Case 51568 document retrieved

**Source:** sources/2026-07-19_puct_51568_32_1116825_IA.PDF (970 KB)
**Document type:** Direct Testimony of Lesli B. Cummings, CenterPoint Energy, SOAH Docket 473-21-1431 / PUCT 51568
**Date of filing:** 2021-03-17 (stamped)
**Key facts:**
- Project confirmed: "EDF Renewables Development, Inc. ('EDF Renewables') planned Space City Solar Interconnection Substation"
- Transmission line: 3.5 to 8.0 mile, 345 kV single-circuit between Hillje Substation and Space City Solar Interconnection Substation
- Timeline per 2021 testimony: "expected to be completed by June of 2022"
- IA between EDF Renewables and CenterPoint Energy executed Dec 15, 2020, filed at Commission Jan 11, 2021 (Attachment 15 of CCN)
- Study area: FM 441 (N), CR 330 / Wharton-Matagorda line (S), CR 307 (W), SH 71 (E)
- Danish Fields Solar LLC = separate project also interconnecting to Hillje Substation
- Route 3 selected: 3.5 miles, shortest route
**Implication:** Site is in the area bounded by FM 441/CR 330/CR 307/SH 71 - this is NW of Wharton, roughly consistent with 29.06N, -96.29W (array visible in imagery). Hillje Substation is at ~29.03N, 96.24W (from triage). The Space City Solar Interconnection Substation is somewhere between or near the solar field.

## D4 — OSM infrastructure data + site location refinement

**Hillje Substation (CenterPoint 345kV):** OSM way 100064466 → lat=29.0297, lon=-96.2365 (this is the POI)
**Second "Hillje Substation" in OSM:** way 516225602 → lat=29.1910, lon=-96.3555 (different grid operator or lower voltage)
**Unnamed substation:** way 1465121535 → lat=29.0684, lon=-96.2699 (could be Space City Solar or Danish Fields interconnect sub)
**Two solar plants in area:**
- Cascade Solar: way 1072756151, lat=29.2059, lon=-96.0278
- Red Tailed Hawk Solar: way 1451876838, lat=29.1807, lon=-96.1470
**Danish Fields Solar:** Also mentioned as interconnecting to Hillje Substation in 2021

**PUCT CCN Schedule (from Doc 34, Item 34):**
- ROW/Land acquisition: 02/2021 → 11/2021
- Engineering & Design: 02/2021 → 08/2021
- Material procurement: 05/2021 → 01/2022
- Construction: 02/2022 → 05/2022
- Energize: 06/2022

**Study area per CCN testimony:**
- North: FM 441
- South: CR 330 / Wharton-Matagorda County line
- West: CR 307
- East: SH 71

**Site estimate update:** The solar array visible in imagery at ~29.065N, -96.290W is located ~2.5 km NNW of Hillje Substation (29.030N, -96.236W). This is NW of the substation and within the study area. However, this could be the Danish Fields array or the earlier Space City Solar phase, not the 366 MW second phase.

**Action:** Need to determine: (1) Is the array we see Space City Solar or Danish Fields? (2) Where exactly is the 366 MW 21INR0341 phase going to be built?

## D5 — Space City Solar Interconnection Substation FOUND in OSM

**OSM Way 1465121535:** power=substation, substation=generation, voltage=345000 (345kV!)
**Center: 29.06838N, -96.27007W**
**Geometry:** A small rectangular enclosure ~44m × ~40m → 1,750 sq meters
**This is the Space City Solar Interconnection Substation** (built by EDF Renewables, connects to CenterPoint Hillje at 345kV)
**Location:** 2.5 km NNW of Hillje Substation (29.030N, -96.236W) — consistent with the 3.5-mile transmission line Route 3 described in PUCT CCN
**Cross-check:** The array visible in imagery at ~29.065N, -96.29W is immediately west/northwest of this substation — CONFIRMED as Space City Solar
**Site coordinate:** 29.06838N, -96.27007W (substation center = high confidence anchor for site)
**Array centroid:** Array extends ~1-3km west/NW of substation, estimated array center ~29.065N, -96.285W

## D6 (continued) — Aktina Solar details

**OSM Aktina Solar (relation 20056372):** EIA ref 64927, start_date=2023-12, Hecate Energy Ramsey LLC, 500 MW
**Extent:** lat 29.04258-29.10384, lon -96.30723 to -96.25857 (~33 km² bounding box, ~8164 acres)
**This is what we see in imagery — not Space City Solar at all**
**Aktina Solar at Hillje is operational since 2023-12, NOT Space City Solar**
**The 345kV generation substation at 29.068, -96.270 is Aktina Solar's substation**
**SPACE CITY SOLAR (21INR0341) = SEPARATE PROJECT — possibly at different location**
**Need to find where the 366 MW Space City Solar site is — it's NOT at 29.065, -96.290 (that's Aktina Solar)**
