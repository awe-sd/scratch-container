# Triage log — Digital Ranch Gas (28INR0100)

## T1 start
- queue_history.py ran OK
- 1 snapshot only (2026-06-01) — project is brand-new in the queue
- Milestones: FIS requested 2026-06-26; everything else blank (no screening complete, no FIS approval, no IA, no construction dates)
- COD: 2027-12-01 — single data point, no drift
- Assessment: earliest possible stage; ~18-month COD claim with zero milestones is aggressive for a 378 MW gas recip plant

## T2 start
- gmaps.py: HTTP 429 on both attempts ("Digital Ranch Gas" and "Digital Ranch Gas Ellis County Texas") — rate-limited, one retry used per rules
- No pins found; negative result (normal for new project)

## T3 start
- DDG search "Digital Ranch Gas Texas power plant": CleanView.co + gridstatus.io both confirm 378 MW recip engine, Ellis TX, ~2027 — pure queue aggregators, no original content
- DDG search "Digital Ranch Gas LLC": same two aggregators only; no developer name, no company registration, no press release
- DDG search "Digital Ranch Texas gas energy developer": CAPTCHA block, one attempt used
- No sources saved (aggregator-only, no project-direct content)
- Developer identity: unknown; no LLC registration surface found

## T4 start
- PUCT Interchange search (FilingParty=Digital Ranch Gas): HTTP 402 on all three URL patterns — session authentication required, cannot access from this environment
- No IA found; negative result (also consistent with project being at FIS-requested stage only)

## T5 start
- TX Comptroller Ch.313: website structure does not expose a filterable data table via direct URL; no Ellis County gas/power entries found
- JETI registry (gov.texas.gov/organization/cje/jeti): no project list exposed
- No abatement found; normal — Ch.313 expired 2022, project filed 2026

## T6 start
- Site candidate: Venus, TX (32.4335, -97.1025) — POI is "Venus Switch 345 kV"; no pin or IA map available; county-town inference, confidence LOW
- cdse.py chips: CDSE auth expired mid-batch; only 2 of 9 chips retrieved (center + NW offset at 32.4635, -97.1325); 403/401 on remainder
- Contact sheet generated from 2 chips; read both full-size (both used as full-size reads under budget)
- Center chip: Venus TX town core + agricultural fields; small-town grid, suburban subdivision NE, scattered rural commercial — NO industrial footprint, no cleared site, no laydown yard, no construction structures
- NW chip (32.4635/-97.1325): similar character — farmland + small rural development
- Construction visible: NO
- Caveat: only 2/9 grid cells covered; true project parcel likely not at town center — Venus Switch substation could be offset; imagery sweep is incomplete

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~28
- STOP
