# Research log — AP Greenport (23INR0474)

## T1 start
- Script: `queue_history.py 23INR0474` — 50 snapshots 2022-05-01 → 2026-06-01
- Milestones: Screening complete 2022-09-06; FIS approved 2023-09-29; **IA NOT signed**; no 6.9 gates; no construction dates
- COD drift (4 changes): 2023-12-22 → (blank 1 month) → 2024-05-23 → 2024-07-01 → 2026-02-18 → **2027-11-19** (current)
- COD has slipped ~4 years from initial claim; currently 16+ months out
- Capacity: stabilised at 100.45 MW since 2023-03

## T2 start
- gmaps.py: HTTP 429 on both attempts — rate limited; no pins returned
- pins_found: 0

## T3 start
- Developer identified: Available Power (President: Ben Gregory)
- EPC partner: Linxon (exclusivity agreement signed May 2023)
- Part of broader 1 GW Available Power / Linxon ERCOT BESS pipeline
- COD per Linxon page: Q1 2025 (stale — queue now shows 2027-11-19)
- No SPV/LLC name found in press materials; "AP Greenport, LLC" is unverified
- No street address or GPS coords in web sources
- Sources saved: linxon_greenport_pr.md
- news_found: true

## T4 start
- PUCT Interchange: HTTP 402 on all endpoints — portal blocked for unauthenticated access
- Tried: FilingParty=AP+Greenport, FilingParty=Available+Power, base search URL — all 402
- ia_found: false (portal inaccessible, not confirmed absent)

## T5 start
- TX Comptroller Ch.313: portal returns navigation pages only; no agreement table accessible via WebFetch
- Ch.313 expired 2022-12-31 — project entered queue 2022-06-10, so Ch.313 filing is plausible but unlikely given timing; Travis County is also urban, less typical for large renewables
- JETI registry: gov.texas.gov/business/page/jeti returns 404 — URL not valid
- abatement_found: false (portals inaccessible or expired program)

## T6 start
- Site candidate: Austrop substation, Travis County eastern area near Hornsby Bend
- Estimated coords: lat=30.2513 lon=-97.470 (from Mapcarta snippet: lat 30.2513°N; lon estimated from Hornsby Bend offset ~6 mi east)
- cdse.py: 9 chips attempted in 3×3 grid; CDSE auth errors (401/403) on 7 chips; 2 chips returned
  - chip_30.2213_-97.500: rural/agricultural, river corridor visible, heavily cloud-masked — no construction signal
  - chip_30.2513_-97.440: rural/forested, heavily cloud-masked — no construction signal
- Contact sheet skipped (sheet cmd expects s2_*.png naming, only 2 chips with different names available)
- construction_visible: false (inconclusive — cloud cover and uncertain site coords; substation not positively identified in either chip)
- Imagery budget used: 2 full-size reads (within 3-read cap)

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~28
- Run complete
