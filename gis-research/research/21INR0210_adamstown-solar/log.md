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

