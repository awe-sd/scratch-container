# Triage log — Buffalo Gap 2 Wind Repower (26INR0625)

## T1 start
**queue_history.py** — 19 snapshots (2024-12-01 → 2026-06-01)

Key milestones:
- Screening complete: 2025-02-20
- FIS approved: 2026-03-17
- **IA signed: 2005-02-28** (date looks like data artifact — likely 2025-02-28, appeared in queue Oct 2025)
- Meets 6.9(1): 2026-03-25
- Meets all 6.9: 2026-05-05
- Construction start/end: NOT reported
- Commercial operation approved: NOT reported

COD drift: 2026-12-01 → **2027-02-01** (1 slip, ~2 months)
Capacity drift: 231.81 → 231.49 MW (minor rounding adjustments)

**T1 result:** Project is past all pre-construction gates (IA signed, all 6.9 met). COD 2027-02-01 is 7 months out from today (2026-07-18). Construction not yet reported in queue. IA signed date anomalous (2005 vs ~2025).

## T2 start — gmaps.py places
All queries returned HTTP 429 (rate-limited). One retry attempted after 15s, still 429.
**T2 result: 0 pins found. No delivery pins. (API rate-limited, not a project signal.)**

## T3 start
Searched: "Buffalo Gap 2 Wind Repower" news/general; "Buffalo Gap 2 Wind Repower LLC" registration; developer + AES. Third query hit CAPTCHA — stopped.

Found:
- **Developer entity name**: "Buffalo Gap Wind Farm 2, LLC" (from ercotqueue.com via DDG)
- ercotqueue.com rates build probability 93%, expected online Jan 31 2027
- infrasure.ai, cleanview.co, interconnection.fyi all list it as proposed/planned wind project
- **No news, no construction announcements, no turbine procurement hits**
- Original Buffalo Gap wind farms (1/2/3) were AES assets; "Buffalo Gap Wind Farm 2" naming may indicate same owner repowering their own asset

No developer press release or news article saved to sources/ — no direct-project pages found beyond queue-aggregator sites.

**T3 result: LLC name confirmed (Buffalo Gap Wind Farm 2, LLC). Developer likely AES (legacy asset repower) but not confirmed. No news signal.**

## T4 start
Attempted PUCT Interchange search at interchange.puc.texas.gov — all endpoints return HTTP 402 (Payment Required / session cookie required). Tried: /search, /Documents/search, /search/filings/ — all blocked. Per rules: one retry done, negative logged.
Note: IA signed date in queue = 2005-02-28 (likely data artifact for 2025-02-28); IA exists per queue milestone.

**T4 result: PUCT portal blocked (402). IA signed flag IS SET in queue data (2025-02-28 likely). IA document not retrieved.**

## T5 start
Searched TX Comptroller Ch.313 and JETI for Nolan County + "Buffalo Gap" wind. Ch.313 portal at mycpa.cpa.state.tx.us/ch313 returned 404. DDG search for Ch.313 + JETI + "Buffalo Gap" + Nolan County returned zero results.
Note: Ch.313 program expired end of 2022; this project entered queue 2024 (26INR prefix suggests 2024 filing). JETI miss is normal for a project this new that may not have filed yet.

**T5 result: No abatement found (expected — post-2022 project, JETI application may not yet be public or not filed).**

## T6 start
Site candidate: thewindpower.net records Buffalo Gap Wind Farm 2 at 32°18'38"N, 100°8'57"W = 32.310556N, -100.149167W (155× GE 1.5sle, 232.5 MW, Nolan County). This is the existing operating plant being repowered. Source: https://www.thewindpower.net/windfarm_en_3211_buffalo-gap-2.php

DDG confirmed AES connection: "part of a broader AES redevelopment across Taylor and Nolan counties."

CDSE imagery: 9 chips attempted, 2 retrieved (401 auth expiry blocked remaining 7). Contact sheet not generated (naming mismatch).

Images read (2 full-size reads used):
- chip_32.280556_-100.149167.png: Clearly shows existing operational wind turbine array — ~15-20 bright turbine pads with white access road strings. Classic operational wind farm signature. NO new construction/disturbed soil visible.
- chip_32.310556_-100.179167.png: Rougher cedar-breaks terrain west of center; turbines visible at frame edges only; no construction activity.

**T6 result:** Site confirmed at ~32.31N, 100.15W (existing AES Buffalo Gap WF2 footprint). Existing turbines visible. NO repower construction activity visible in June 2026 imagery. COD of 2027-02-01 is 7 months away — 231 MW wind repower typically requires 12-18 months of construction; absence of visible activity raises schedule concern.

## T7 start

## Deep scan start — 2026-07-19

### D1: AES SEC filings — Buffalo Gap Repowering confirmation
Searched EDGAR full-text for "Buffalo Gap Wind Farm 2" and found 3 hits — all AES Corp (CIK 0000874761) Exhibit 21.1 filings (FY2022, FY2023, FY2024). 
Fetched AES FY2025 10-K (0000874761-26-000063, filed 2026-03-02).

**KEY FINDING: Buffalo Gap Repowering is real and financed.**
From main body aes-20251231.htm:
1. Construction pipeline table: "Buffalo Gap Repowering US-TX Wind 527 MW 100% 1H 2027"
2. Note on redeemable stock: "In December 2025, AES entered into agreements with HASI, including an investment agreement under which HASI invested $200 million in the Buffalo Gap wind repowering project in exchange for a preferred membership interest."
3. SPV holdco = AES DevCo Holdco, LLC (Renewables SBU)

AES expects 1H 2027 COD for the 527 MW combined (BG1+BG2+BG3) Buffalo Gap repower.
Artifact: sources/2026-07-19_sec_aes_fy2025_10k_buffalo-gap-repower-excerpt.txt

### D2: Sister INR capacities confirmed
- 26INR0622 Buffalo Gap 1: 120.23 MW, same COD 2027-02-01, same IA date
- 26INR0625 Buffalo Gap 2: 231.49 MW (this project)
- 26INR0626 Buffalo Gap 3: 168.45 MW, same COD 2027-02-01, same IA date
- Total: ~520 MW (AES states 527 MW — minor rounding diff; matches the 3-WF repower picture)

All 3 have identical milestone timestamps: FIS approved 2026-03-17, IA signed 2025-10 (date in queue "2005-02-28" = data artifact for 2025-02-28), all 6.9 met 2026-05-05.

### D3: PUCT portal blocked (402), PUCT search requires JS
PUCT interchange.puc.texas.gov returns 402 for direct API requests. JS-rendered search UI. IA not retrieved from PUCT. (Negative evidence logged.)

### D4: FAA OE/AAA portal — 404/not accessible
FAA OE/AAA portal returns 404 for state/county/type search. DOF file redirect blocked. No FAA obstruction coordinates retrieved. (Negative evidence logged.)

### D5: Nolan County CAD — 0 hits for all Buffalo Gap / AES variants
nolan-cad.org owner search returns 0 hits for: "Buffalo Gap Wind Farm 2", "Buffalo Gap Wind", "AES", "AES CORP", "BUFFALO GAP WIND FARM 2", etc. 
Likely explanation: wind turbine mineral accounts in Texas are often assessed by PAI (Pritchard & Abbott Inc.) as industrial personal property, not in the standard real property CAD owner search. Mineral/utility assessments handled separately.

### D6: AES 2023 investor day deck — context
Buffalo Gap I, II, III impairments of $193M noted (expired PPA, ERCOT volatility circa 2022-2023). This explains the repower motivation — old GE 1.5sle turbines being replaced with higher-capacity modern turbines.

## Deep scan continued — 2026-07-19

### D7: AES Q3 2025 10-Q (filed 2025-11-04) — tax equity buyout
"During the third quarter of 2025, AES Renewable Holdings completed buyouts of tax equity partners at Buffalo Gap I, Buffalo Gap II, and Buffalo Gap III, resulting in a decrease to NCI of $28 million and a decrease to additional paid-in capital of $42 million."
Artifact: sources/2026-07-19_sec_aes_q3_2025_10q_buffalo-gap-excerpt.txt
WHY: Tax equity buyout is a standard pre-repower step; confirms AES was actively preparing for repower by mid-2025.

### D8: AES FY2025 10-K — construction pipeline table
"Buffalo Gap Repowering US-TX Wind 527 MW 100% 1H 2027" — appears in pipeline table alongside funded projects under construction.
Artifact: sources/2026-07-19_sec_aes_fy2025_10k_construction_pipeline.txt
WHY: Corroborates the HASI excerpt; 1H 2027 is AES's own stated guidance as of Dec 31, 2025.

### D9: AES Q1 2026 10-Q (filed 2026-05-05) — no Buffalo Gap mention
Searched aes-20260331.htm for "buffalo gap" — 0 hits. Project not discussed individually in Q1 2026 disclosure.
WHY: No new construction start announcement or status update in the most recent quarterly.

### D10: EDGAR broad search — Buffalo Gap + construction
Only AES filings mention "Buffalo Gap Repowering"; no third-party turbine supplier (GE Vernova, Vestas, Siemens Gamesa) or EPC contract announcement found.
WHY: Absence of turbine procurement press release suggests order not yet public or not yet placed.

### D11: Imagery key frames — 4-date series Oct 2025 → Jul 2026
Sentinel-2 chips retrieved for 2025-10-01, 2026-01-01, 2026-04-01, 2026-07-01 at 6km buffer.
Contact sheet shows: stable operational turbine array throughout all 4 dates. No staging areas, no foundation excavation, no turbine removal, no new roads.
Artifact: imagery/contact_sheet.png
WHY: Decisive negative — construction has not started as of Jul 2026; 7 months before reported COD (Feb 1, 2027), making that date unreachable.

### D12: thewindpower.net site record
Confirmed: 155x GE 1.5sle, 232.5 MW, lat 32.310556, lon -100.149167, Nolan County TX.
Artifact: sources/2026-07-19_thewindpower_buffalo-gap-2-site-record.txt

### D13: FAA OE/AAA portal — 404 (govt shutdown)
FAA OE/AAA portal returns 404 — government shutdown mode, cannot accept new obstruction filings or process search requests.
WHY: No turbine coordinates available; this is a contingent gap that does not change the verdict given AES public disclosures.

### D14: PUCT Interchange portal — JS-only (blocked)
PUCT interchange.puc.texas.gov requires JavaScript rendering. All curl/HTTP requests return 402 or redirect to noscript page. IA document not retrieved.
WHY: Cannot obtain IA schedule exhibit; contractual COD unknown. ERCOT queue milestone confirms IA signed ~2025-02-28.

### D15: Nolan County CAD — 0 hits
nolan-cad.org owner search: 0 hits for Buffalo Gap Wind Farm 2 LLC, AES, Buffalo Gap Wind. Expected — wind turbines are assessed as industrial personal property in Texas, not in standard real-property owner search.

### D16: EDGAR — Buffalo Gap Joint Venture (CIK 0002111004)
Form D filed 2026-02-13 by "Buffalo Gap Joint Venture" — Oil and Gas joint venture based in Plano TX, managed by Eagle Natural Resources, LLC. $1.5M offering. UNRELATED to wind repower.

### D17: EAC Vintage 2025 A Series of EAC Master LLC (CIK 0002082924)
Form D filed 2025-10 and 2025-11 — address is "4400 Buffalo Gap Rd, Abilene TX" (street named Buffalo Gap Road). UNRELATED — this is a different entity on a street of the same name.

## Synthesis / Stage 5 complete
- Verdict: real_early (high confidence)
- Site: 32.310556N, 100.14917W — existing BG WF2 centroid (thewindpower.net + imagery)
- Construction stage: pre-construction (nothing visible through Jul 2026)
- Independent COD: 2027-Q3, drift risk HIGH
- Key artifacts: AES FY2025 10-K pipeline table, HASI $200M financing, Q3 2025 tax equity buyout, imagery contact sheet

