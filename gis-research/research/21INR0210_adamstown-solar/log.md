# Triage log — Adamstown Solar (21INR0210)

## T1 start
- 86 snapshots (2019-05-01 → 2026-06-01)
- COD drift count: 7 (2021-12-31 → 2022-12-31 → 2023-09-30 → 2024-09-30 → 2025-05-31 → 2026-06-01 → 2026-09-30 → 2027-08-31)
- Current reported COD: 2027-08-31
- Key milestones: IA signed 2024-12-04; FIS approved 2026-02-25; Meets 6.9(1) 2025-12-19
- NOT achieved: Meets all 6.9, construction start, construction end, energization, sync, commercial operation
- Capacity stable ~250 MW (minor revisions over time; current 250.88 MW)
- T1 complete

## T2 start
- gmaps.py: HTTP 429 on first call; 429 on retry (budget exhausted)
- No pins found (API rate-limited, not a project signal)
- T2 complete — 0 pins

## T3 start
- Developer LLC: Adams Creek Solar Project, LLC; parent: Savion LLC
- Official project site found: adamscreeksolarproject.com; ~2,618 acres, ~796k modules
- PUCT IA link surfaced from DDG results (35077_2025_1453242.PDF)
- First Amendment to IA filed 2026-04-10
- TX Comptroller Ch.313 with Harrold ISD (#1872) found
- Saved: sources/t3_web_sweep.md
- T3 complete — news_found=true, developer=Savion LLC

## T4 start
- PUCT interchange.puc.texas.gov returns HTTP 402 on all requests (portal blocked)
- IA existence confirmed via T3 web sweep: case 35077, document 35077_2025_1453242.PDF
- First Amendment to IA also filed (2026-04-10) — surfaced by DDG snippet
- IA signed date in queue: 2024-12-04 (consistent with 2025 filing)
- PDF content not accessible — schedule exhibit not retrieved
- T4 complete — ia_found=true (indirect, via web), schedule not retrieved

## T5 start
- TX Comptroller Ch.313 #1872 CONFIRMED: Adams Creek Solar Project LLC + Harrold ISD, posted 2022-06-13
- Agreement and Findings PDF posted 2022-12-20
- JETI registry URL 404 — cannot check; normal for project that filed Ch.313 in 2022 (before JETI)
- T5 complete — abatement_found=true (Ch.313 #1872, Harrold ISD)

## T6 start
- Site candidate: Harrold, TX area (~34.074°N, 99.379°W) — inferred from Ch.313 with Harrold ISD + project name "Harrold ISD Solar PV Park"
- Ran 3×3 chip grid at center; all 9 chips returned HTTP 401 Unauthorized (CDSE creds not configured)
- No retry attempted (blocked = one retry rule = no satellite imagery retrieved)
- construction_visible: unknown (no imagery)
- T6 complete — imagery blocked

## T7 start
- Wrote triage_findings.json and triage.md
- Turns used: 18
- deep_scan_recommended: true
- T7 complete

## Deep scan start — 2026-07-19

Picking up from triage. Gaps to close:
1. PUCT IA PDF + First Amendment schedule
2. CDSE imagery (creds should be configured now)
3. Ch.313 #1872 agreement PDF — investment + schedule
4. adamscreeksolarproject.com — parcel map, acreage
5. gmaps delivery pin


## PUCT IA retrieved — 2026-07-19
- File: sources/2026-07-19_puct_35077-1453242_adamstown-solar-IA.pdf
- Signed: December 4, 2024 (Docusign; countersigned)
- Parties: Oncor Electric Delivery Company LLC + Adams Creek Solar Project, LLC (Adamstown Solar, 21INR0210)
- POI: Wichita County, TX — TSP's Western Wind Switching Station within Krum West Switch to Riley Switch (AEP) 345 kV line (location CEII-redacted)
- Equipment: 64x Sungrow SG4400UD-MV-US inverters, 281.6 MVA / 254.48 MW dispatched
- IA Schedule (Exhibit B):
  - Notice to proceed / security: December 6, 2024
  - In-Service Date: December 3, 2026
  - Trial Operation: January 2, 2027
  - Scheduled COD: August 31, 2027
- Financial security: LC $17,554,077 effective on or before December 6, 2024
- Prior SGIA dated August 8, 2022 superseded by this December 2024 IA

## Ch.313 application key data — 2026-07-19
- File: sources/2026-07-19_comptroller_ch313_1872-adams-creek-agmt.pdf
- Applicant: Adams Creek Solar Project, LLC with Harrold ISD
- County: Wilbarger
- Estimated construction commencement: October 1, 2026
- Commencement of commercial operations: December 31, 2027
- Total proposed investment: $225,000,000
- Limitation amount: $20,000,000
- QTP: 2026-2027
- Limitation period begins: Jan 1, 2028 (Jan 1 following commercial operations)

## Project website confirmation — 2026-07-19
- URL: https://www.adamscreeksolarproject.com/
- Location: "approximately six miles northeast of Harrold in Wilbarger County, Texas"
- Acreage: "approximately 1,800 acres"
- Capacity: "up to 250 megawatts"
- "Construction began in 2026" + "commercial operation in 2027"
- County contribution: $200,000 community engagement payment


## Shell 20-F confirms ownership — 2026-07-19
- Shell plc EX-8.1 (FY2025, filed 2026-03-12): Adams Creek Solar Project, LLC is 100% subsidiary
- Savion LLC = wholly-owned Shell subsidiary
- Chain: Adams Creek Solar Project, LLC → Savion LLC → Shell plc
- Source: SEC 20-F adsh=0001628280-26-017024, EX-8.1 exhibit
- "Adams Creek Solar Project, LLC [c] CORPORATION SERVICE COMPANY, 251 LITTLE FALLS DRIVE, WILMINGTON, 19808"
- Registered agent: Corporation Service Company, Wilmington DE (common for Shell subsidiaries)
- Contact in IA: Chad Craven, Matt Adams — savionenergy.com email addresses

## SEC EDGAR negative: no Form D filings for Adams Creek Solar
- No private placement Form D found — consistent with direct corporate subsidiary model (no third-party equity raise needed)

## CDSE imagery status — 2026-07-19
- Auth intermittently failing (403/401); 4 chips retrieved
- Chips show: Harrold area undisturbed farmland (~34.12-34.17°N, 99.32-99.38°W range)
- Correct site estimate: ~34.15°N, 99.27°W (6 mi NE of Harrold); not yet confirmed by imagery
- Imagery search blocked by CDSE rate limit


## 2026-07-20 — D1/D2 research

### D0 - Skeleton written
findings.json skeleton created before research began.

### D1 - IA Schedule (original IA, Dec 4 2024)
- Source: 2026-07-20_puct_35077-2025_standard-generation-interconnection-agreement-be.pdf (CONFIRMED)
- Exhibit B:
  - In-Service Date: December 3, 2026
  - Scheduled Trial Operation Date: January 2, 2027 (original) → March 8, 2027 (Amendment 1)
  - Scheduled COD: August 31, 2027
- Financial security: $17,554,077 LC (Irrevocable Standby Letter of Credit, Exhibit E)
- POI: "Western Wind Switching Station within the Krum West Switch to Riley Switch (AEP) 345 kV line" — Wichita County, TX
- Equipment: 64 Sungrow SG4400UD-MV-US inverters, 281.6 MVA (original) → amended to 350 TMEIC PVU-L0840URN inverters, 253.6 MW
- Generator contact: Chad Craven, VP Transmission, @savionenergy.com — SAVION LLC confirmed as parent

### D1 - Amendment No. 1 (April 10, 2026)
- Source: 2026-07-20_puct_35077-2479_amendment-no-1-to-the-standard-generation-interc.pdf (CONFIRMED)
- Only change to schedule: Trial Operation moved from Jan 2, 2027 → March 8, 2027
- COD remains August 31, 2027 (unchanged)
- Inverter type changed: Sungrow SG4400UD (64 × 4.4 MVA) → TMEIC PVU-L0840URN (350 × 0.78 MVA)
- Filed: May 5, 2026 (signing: April 10, 2026)

### D1 - Ch.313 key facts
- Source: 2026-07-19_comptroller_ch313_1872-adams-creek-agmt.pdf + 2026-07-19_comptroller_ch313_1872-adams-creek-app.pdf
- SPV: Adams Creek Solar Project, LLC (TX franchise 32067584329)
- Project: 250 MW AC, 796,000 PV panels, 67 central inverters (app)
- Total investment: $225,000,000 in Wilbarger County, Harrold ISD
- Limitation period: 2026-2027 start (10 year limitation through ~2037)
- Land: NOT owned by applicant (land = not applicable per Tab 9)
- Agreement executed: December 8, 2022 (Harrold ISD board)

### D2 - Site pinpoint
- Google Places: "Adams Creek Solar Field" at 16476 FM 370, Electra, TX 76360 → 34.151030, -98.952161
  DECISIVE ARTIFACT: matches FM 370 E shown on Ch.313 map p38; Electra address matches Wichita Co. near Wilbarger line
- Ch.313 map p38: project boundary straddles FM 370 E, county roads 127-131 N; "Adams Creek" label visible
- Ch.313 map p39: project NNE of Harrold, near Wilbarger/Wichita county line

### D2 - Map pages saved
- sources/ch313_map_p37.png through ch313_map_p41.png extracted from Ch.313 agreement PDF

### D2 - CDSE imagery — BLOCKED (402 insufficient credits)
- Attempted cdse.py chip for 2026-07-01, 2026-06-01, 2026-05-01
- All return HTTP 402 PaymentRequired from openEO /result endpoint
- Satellite imagery cannot be retrieved this run
- Negative evidence logged: construction stage unverifiable from imagery

### D3 - Search results — ALL FAILED
- search.py backend unavailable (SEARCH FAILED on all backends) for:
  - "Adamstown Solar Savion 21INR0210 Wilbarger Texas construction"
  - "Adams Creek Solar Project Savion Wilbarger Texas"
  - "Savion Energy Adams Creek Solar Wilbarger"
- Negative evidence: no web search results retrievable

### D3 - Site location confidence
- Google Places "Adams Creek Solar Field" at 16476 FM 370, Electra TX → 34.151030, -98.952161
  HIGH confidence: consistent with Ch.313 map p38 (FM 370 E road visible on project boundary map),
  consistent with IA stating POI in Wichita County (Electra is Wichita County), consistent with
  triage lat ~34.07 being slightly south (triage used Harrold ISD centroid; actual site is NNE of Harrold)

### D3 - Savion LLC parent confirmed
- Address in IA Exhibit D: 422 Admiral Blvd, Kansas City, MO 64106 → Savion Energy HQ
- email domains: @savionenergy.com (Chad Craven VP Transmission, Matt Adams)

### D3 - Amendment 1 key finding
- Inverter change: Sungrow SG4400UD → TMEIC PVU-L0840URN (350 units × 0.78 MVA)
- This is a significant equipment substitution, signed April 10, 2026 — indicates active procurement as of Q2 2026
- Trial Op date slipped 2 months (Jan 2 → Mar 8, 2027)
- COD unchanged at Aug 31, 2027

### D3 - Prior IA note
- PUCT 35077-1475 (Sep 2022): earlier SGIA between Oncor and "Adamstown Solar & Storage / Adams Creek"
  This is superseded by the Dec 2024 IA. The "& Storage" component may have been dropped.
