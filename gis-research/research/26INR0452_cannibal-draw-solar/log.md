# Triage log — Cannibal Draw Solar (26INR0452)

## T1 start
queue_history.py: 25 snapshots (2024-06-01 → 2026-06-01). 1 COD change.
- IA signed: 2025-01-17 (first seen 2025-01-01 snapshot) — significant milestone
- Meets 6.9(1): 2025-02-12 — passed first financial security gate
- Meets all 6.9: NOT achieved
- Construction start/end: NOT reported
- COD drift: 2027-07-01 → 2028-04-10 (shifted ~9 months in Nov 2024)
- Current reported COD: 2028-04-10 (~22 months out from triage date)
- FIS requested 2024-06-10 but FIS approved: NOT recorded (unusual given IA signed)

## T2 start
gmaps.py: HTTP 429 on both attempts (rate-limited). No pins obtained.
pins_found: 0

## T3 start
DDG search "Cannibal Draw Solar": developer = Red River Clean Energy (Dallas TX/Seattle WA); 6-project ~1,346 MW TX portfolio; no parent company surfaced.
LLC: Foreign LLC TX registered 2023-12-26, Dallas TX address, Delaware likely formation state.
Key snippet: "IA between Wind Energy Transmission Texas LLC and Cannibal Draw Solar LLC filed with PUCT" — confirms IA at PUCT with WETT counterparty.
Also referenced as "Cannibal Draw Solar and Storage" — BESS component (~98.6 MW) may have separate INR.
No news articles or press releases found.

## T4 start
PUCT Interchange portal: HTTP 402 on all direct URL attempts (blocked). One retry via DDG found the filing.
IA FOUND: PUCT Docket 35077, Item 2050, filed 2025-01-22
- Filing party: Wind Energy Transmission Texas, LLC (WETT)
- Counterparty: Cannibal Draw Solar, LLC
- IA effective date: 2025-01-17 (matches queue milestone)
- Capacity confirmed: 149.5 MW solar + 99 MW BESS
- COD per IA: 2028-04-09 (queue shows 2028-04-10 — 1-day discrepancy, likely rounding)
- Filing note: "slight deviations from Commission-approved Standard form"
- PDF at interchange.puc.texas.gov/Documents/35077_2050_1460868.PDF — HTTP 402, could not retrieve
- Milestone schedule exhibit NOT extracted (portal blocked)

## T5 start
Ch.313: Portal pages not machine-searchable; direct county URL returned generic page. Ch.313 sunset Dec 2022 — 26INR0452 filed June 2024, so Ch.313 ineligible regardless.
JETI: DDG returned CAPTCHA, no result.
No abatement found. Normal for a post-2022 project — JETI eligibility possible but not confirmed.

## T6 start
Site candidate: Sand Bluff substation (POI) at 32.0035, -101.2732 (Glasscock County) — from Overpass API on OSM way.
cdse.py chips attempt: HTTP 401 Unauthorized — CDSE_PASSWORD not set in ~/.config/gis-research.env (example file only).
Imagery blocked. construction_visible = false (not assessed).

## T7 start
triage_findings.json and triage.md written. Turns used: 22. Run complete.
