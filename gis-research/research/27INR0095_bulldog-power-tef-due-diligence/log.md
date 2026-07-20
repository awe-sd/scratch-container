# Triage log — 27INR0095 Bulldog Power (TEF - Due Diligence)

## T1 start
- Script: queue_history.py 27INR0095
- 32 snapshots (2023-11-01 → 2026-06-01)
- Milestones: Screening complete 2024-02-08, FIS approved 2026-03-20
- No IA signed, no 6.9 milestones, no construction dates
- COD drift (2 changes): 2027-07-24 → 2026-04-30 → 2027-12-18
- Capacity change: 300.75 MW → 311.0 MW (2025-06)
- T1 complete

## T2 start
- gmaps.py 429 rate-limited on all queries; retried once, still blocked
- No delivery pins found
- T2 complete (blocked)

## T3 start
- Developer identified: Nightpeak Energy LLC (Oakland, CA); Bulldog Power is the SPV/subsidiary
- TEF application: PUCT APP-00000159 / docket 56896; advanced to due-diligence stage
- TEF WITHDRAWAL confirmed February 2026 (Nightpeak withdrew Bulldog Power + Homestead Power 260 MW)
- Brazoria County denied tax breaks connected to broader ~$3B AI-related development
- Near Sweeny, TX (Brazoria County)
- PUCT interchange PDF (56896_101_1583127.PDF) returned 402; docket search also 402
- Key sources: EnergyChoiceMatters.com (Paul Ring), DDG results referencing PUC filing
- Saved: no pages downloadable (402/blocked); findings logged here
- T3 complete (budget 5: used ~4)

## T4 start
- PUCT interchange portal returns 402 on all search URLs (filing search, case search, TEF list page)
- Known docket: PUCT case 56896 / APP-00000159 (Bulldog Power TEF application)
- TEF withdrawal filing known from T3 (doc 56896_101_1583127.PDF) but PDF also 402
- No IA in queue data (T1); TEF withdrawal makes IA unlikely
- T4 complete (portal blocked, budget used)

## T5 start
- Comptroller Ch.313 page: no searchable database content returned; county filter not functional via WebFetch
- DDG search for Ch.313/JETI returned CAPTCHA block on retry
- T3 already noted: Brazoria County DENIED tax breaks for Nightpeak/Bulldog (AI-related development context)
- Project filed in 2023; Ch.313 expired Dec 2022; JETI post-2022 replacement — no JETI hit found
- No abatement found (consistent with denial + Ch.313 expiry)
- T5 complete (no abatement found, normal for post-2022)

## T6 start
- Site candidate: ~29.04N, -95.70W (Sweeny TX / FM 524 corridor, low confidence; no pin from T2, no IA map, T3 only said "near Sweeny")
- cdse.py returned 401/403 on all 9 grid chips — CDSE credentials invalid in this session
- No imagery obtained; no contact sheet generated
- construction_visible: false (no data)
- T6 complete (auth blocked)

## T7 start
- triage_findings.json written
- triage.md written (10 lines)
- Total turns used: 22
- T7 complete — STOP
