# Triage log — Myrtle Solar (19INR0041)

## T1 start
**Queue history**
- 110 snapshots (2017-05-01 → 2026-06-01), 31 COD slips — extreme drift record
- Original COD: 2019-03-17 → current reported: 2027-06-21 (8+ year slip)
- IA signed: 2019-11-13 ✓
- FIS approved: 2022-01-25 ✓
- Approved for energization: 2022-12-07 ✓
- Approved for synchronization: 2022-12-20 ✓
- **Commercial operation approved: NOT ACHIEVED** (blank)
- Construction start/end: NOT REPORTED
- Capacity grew: 200 MW → 240 MW → 321.2 MW (final bump 2021-09)
- Latest COD in queue (2026-06-01 snapshot): 2027-06-21

**Interpretation**: Project has energization/sync approvals from Dec 2022 but has never achieved commercial operation. 31 COD slips over 9 years is extremely high drift. Status is anomalous — approved for energization/sync but not commercial operation, and now re-queued with a 2027 COD. May be a partial/stalled commissioning or a project that received approvals for a prior smaller scope and now is attempting to complete at full 321.2 MW.

## T2 start
**Delivery pins — gmaps.py**
- Query 1 "Myrtle Solar": HTTP 429 Too Many Requests
- Query 2 "Myrtle Solar Brazoria County": HTTP 429 (one retry per rules)
- Result: BLOCKED — no pins found. Normal result; no coords to log.

## T3 start
**Web sweep**
- Developer confirmed: TotalEnergies (press release mentions Myrtle as "largest-to-date operated utility-scale solar farm with storage in US")
- Location confirmed: near Angleton, Brazoria County, ~2,400 acres
- Capacity: ~380 MW per TotalEnergies (vs 321.2 MW ERCOT queue — includes BESS and/or uprated solar)
- Status per multiple sources: operating / commissioned (ercotqueue.com: "Currently Commissioned; 100%"); GEM wiki: "operating"
- COD year: ~2023 per secondary sources (exact date not confirmed — TotalEnergies PR returned 404, GEM returned 403)
- LLC name "Myrtle Solar, LLC" — registration search blocked by CAPTCHA
- Saved: sources/web_sweep_t3.md
- **Key anomaly**: ERCOT queue still shows 2027-06-21 COD with no `approvedForCommercialOperation` date, yet web sources say it is operating. This is the central puzzle.

## T4 start
**PUCT Interchange filings**
- interchange.puc.texas.gov — HTTP 402 on root and all search paths (one retry attempted)
- Result: BLOCKED — cannot access portal. IA known to exist (queue timeline: iaSigned = 2019-11-13) but cannot retrieve documents.
- NOTE: IA existence is confirmed by queue data; PUCT filing details remain unknown.

## T5 start
**TX Comptroller Ch.313 abatements**
- comptroller.texas.gov ch313 portal: navigation pages only, no searchable agreement database accessible via WebFetch
- Ch.313 program closed to new applications after 2022; this 2019 project (TotalEnergies) is eligible era — could have a 313 agreement with Brazoria County ISD
- JETI: post-2022 replacement; not applicable for this project era
- Result: no abatement confirmed or ruled out — portal not machine-readable during triage

## T6 start
**Imagery — Sentinel-2 via cdse.py**
- Site candidate: near Angleton, Brazoria County (web sources: "north of Angleton", ~2,400 acres); confidence LOW (no pin, no coords; county + direction only)
- Grid center estimate: 29.22°N, 95.43°W (derived from Angleton centroid + "north" qualifier)
- 3×3 chip grid attempted (9 calls, --buffer-km 2, 2025-06-01): ALL failed HTTP 401 Unauthorized
- CDSE credentials not loaded — ~/.config/gis-research.env absent or empty in this environment
- Result: NO imagery acquired. Construction verdict: UNKNOWN from imagery.
- NOTE: Web sources (TotalEnergies PR, GEM, ercotqueue.com) independently report project as operating/commissioned ~2023. Imagery would confirm solar array presence but is not needed to establish operating status in this case.

## T7 start
Wrote triage_findings.json and triage.md. Turns used: ~28. STOP.

## Deep scan — Stage 2-4 findings (2026-07-19)

### EIA 860 data (artifact: sources/2026-07-19_eia860_plant_y2023.xlsx + generator files)
- **Site confirmed**: 24395 CR-48, Angleton TX 77515 — 29.228486°N, 95.427444°W (EIA Form 860 Plant file)
- CenterPoint Energy transmission owner, 138 kV grid voltage (matches POI "42110 Angleton 138kV")
- FERC EWG docket EG23-27-000 (solar) and EG23-275-000 (storage)
- **EIA Status: TS (Testing) in ALL years 2023, 2024, 2025** — never achieved OP
  - Myrtle Solar (66910): 313 MW solar, Status=TS, effective Aug 2023, updated Jul 2026
  - Myrtle Storage (66913): 150 MW BESS, Status=TS, effective Dec 2023, updated Mar 2026
- Companion BESS confirmed: Myrtle Storage, LLC (separate entity, same address)
- No EIA Operable entry for either — project has not achieved commercial operation per federal reporting

### Imagery (artifacts: imagery/key/s2_2022-06-01.png, s2_2024-01-01.png, s2_2025-11-01.png)
- 2022-06: Active construction (cleared/graded, road grid, NO modules visible)
- 2024-01: Modules substantially installed — dark module rows clearly visible
- 2025-11: Array substantially complete/operating appearance
- Site at 29.228, -95.428 — confirmed as the correct location (upper-center-right of frame)

### COD anomaly investigation
- ERCOT queue shows 2027-06-21 COD despite energization/sync approvals from Dec 2022
- EIA confirms TS status through Jul 2026 — formal commercial operation NOT achieved
- Possible explanations: (1) BESS still commissioning, (2) contractual/billing dispute, (3) capacity uprate scope pending
- The queue COD of 2027-06-21 suggests ~18-month delay still expected as of June 2026 snapshot

### TotalEnergies press release search (negative evidence)
- No dedicated Myrtle Solar press release found on corporate.totalenergies.us
- Dec 4, 2024 farm-down PR ($800M to Apollo for 50% of 2GW Texas portfolio) does NOT include Myrtle Solar
  in the named portfolio (Danish Fields, Cottonwood, Hill Solar I, two BESS) — Myrtle is NOT part of the Apollo deal
- Cottonwood Solar Farm image visible in TotalEnergies US homepage — NOT Myrtle

### PUCT IA
- Portal returned 402 in both triage and deep scan — IA docs not retrievable
- IA confirmed signed 2019-11-13 per queue history
