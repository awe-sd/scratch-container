# Triage log — Austin Bayou Solar (25INR0102)

## T1 start
- 47 snapshots (2022-08-01 → 2026-06-01)
- COD drift: 2025-02-04 → 2025-03-01 → **2027-06-01** (2 changes; ~2.3-year total slip)
- IA signed: 2023-11-15 (appeared in 2024-05 report) ✓
- Meets 6.9(1): 2025-02-12 ✓  |  Meets all 6.9: NOT YET
- FIS requested: 2022-07-26  |  FIS approved: NOT achieved
- Construction start/end: NOT reported
- Capacity: 753.4 MW → **502.48 MW** (downsized 2025-05, ~33% reduction)
- No energization/sync/COD milestones

## T2 start
- gmaps.py 429 on first call; retry also 429 — tool blocked, 0 pins found
- No delivery pins obtained (normal — portal rate-limited)

## T3 start
- Project trackers (ercotqueue, cleanview, infrasure) confirm 502 MW solar COASTAL; build-chance 26%
- LLC: Austin Bayou Solar, LLC — incorporated 2022-05-20, TX foreign entity (Delaware), Active
- Registered address: 988 Howard Ave Suite 200, Burlingame CA 94010
- Same address hosts multiple solar project LLCs incl. Cottonwood Bayou Solar II (19INR0134) → likely **Intersect Power**
- PUCT docket 35077 / item 2079: IA with CenterPoint Energy Houston Electric ← KEY LEAD for T4
- Related queue entries: Austin Bayou Storage II (25INR0236), Storage III (25INR0237); Solar II (26INR0367) WITHDRAWN
- No developer press release or announcement found; parent company not explicitly confirmed
- Saved: sources/web_sweep.md

## T4 start
- PUCT Interchange portal returns HTTP 402 on all endpoints (controlNumber=35077, filingParty search)
- Docket 35077 identified from T3 as the IA docket — known to exist but PDF not retrievable this session
- ia_found = TRUE (confirmed via T3 web sweep; IA signed 2023-11-15 per queue history)
- PDF contents (parties page, milestone schedule) NOT obtained — blocked portal
- Note for deep scan: docket 35077 item 2079 contains IA with CenterPoint Energy Houston Electric

## T5 start
- TX Comptroller Ch.313 page non-searchable via WebFetch (links to tools only, no embedded data)
- DDG search for Ch.313/JETI/abatement + Austin Bayou Solar + Brazoria → no results
- No abatement found — normal for post-2022 projects (Ch.313 expired 2022; JETI replacement)
- abatement_found = FALSE

## T6 start
- T2 gmaps blocked (429), no pin
- T4 PUCT blocked (402), no IA map
- Attempted substation location lookup (Savana 43180 / Seabreeze 43020) via DDG + Bing — DDG returning bot-challenge pages; Bing found no specific coords
- Best candidate = "somewhere in Brazoria County" — below threshold
- SKIP imagery per checklist ("no site candidate")
- construction_visible = FALSE (not assessed)

## T7 start
- Wrote triage_findings.json and triage.md
- Turns used: 22
- STOP

## Deep scan — Stage 1+2 (2026-07-19)

### PUCT IA documents retrieved
- PUCT Docket 35077, Item 2079: 3 documents downloaded
  - Main IA PDF: sources/2026-07-19_puct_35077-2079_austin-bayou-solar-IA_main.pdf (149 pages, 10.8 MB)
  - Filed 2025-03-06 by Mickey Moon (CenterPoint Energy)
  - SGIA signed 2025-02-14 between CenterPoint Energy Houston Electric and Austin Bayou Solar, LLC
  - **IMPORTANT: This IA covers Austin Bayou Storage I, II, & III (25INR0235, 25INR0236, 25INR0237) NOT the solar project (25INR0102)**
  - Solar IA (signed 2023-11-15) must be a SEPARATE PUCT filing — not yet found

### Critical POI coordinates (from storage IA Exhibit C)
- Point of Interconnection: **29.3222714N, -95.3891644W** (Brazoria County, TX)
- Delivery Voltage: 345 kV
- NOTE: This POI likely shared with solar project (solar+storage share the same tap point)
- Cite: sources/2026-07-19_puct_35077-2079_austin-bayou-solar-IA_main.pdf p.43

### Developer identity — CORRECTED
- Contact in IA: **Mark Soutter** at PO Box 303427, Austin TX 78703
- Email: mark@sunchasepower.com → **Sunchase Power** (Austin TX), NOT Intersect Power
- EFT beneficiary: **Lagniappe Renewable Energy, LLC** (BancFirst, Oklahoma City, ABA 103003632, Acct 4005249075)
- Triage's 988 Howard Ave Burlingame CA = likely a different TX Comptroller match; needs re-verification
- Cite: sources/2026-07-19_puct_35077-2079_austin-bayou-solar-IA_main.pdf p.51 (Exhibit D)

### Contractual schedule (storage IA, Exhibit B, p.42)
- Prerequisite items due: 2025-02-14 (Scheduled Start Date)
- TIF In-Service Date: **2029-10-11** (or 56 months after prerequisite delivery)
- Scheduled COD: **2030-01-11** (or 3 months after In-Service Date)
- NOTE: This is the STORAGE schedule, not the SOLAR schedule. Solar project likely different.

### Financial security (storage IA, Exhibit E, p.52)
- TIF cost estimate: **$21,830,000**
- Form: irrevocable LC from qualifying financial institution

### Next: 
- Find solar IA (25INR0102 signed 2023-11-15) at PUCT — different docket/item
- Research Sunchase Power + Lagniappe Renewable Energy
- Run imagery at 29.3222714N, -95.3891644W

### Imagery — BLOCKED (2026-07-19)
- CDSE tool: HTTP 401 (credentials rejected — likely expired)
- gmaps staticmap: HTTP 403 (API not enabled for this key)
- gmaps places: HTTP 429 (rate limited)
- All satellite tools unavailable this session
- construction_visible = NOT ASSESSED (tool failure, not project signal)
- Will cite POI coords (29.3222714N, -95.3891644W) but cannot confirm satellite stage
