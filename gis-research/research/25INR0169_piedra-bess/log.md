T1 start

## T1 — queue history
- 40 snapshots (2023-03 → 2026-06), 5 reported-COD changes (6 distinct values)
- COD progression: 2025-06-01 → 2026-04-20 → 2026-09-30 → 2026-12-22 → 2026-12-31 → **2027-05-10** (latest)
- COD has drifted ~2 years since first appearance; current 2027-05-10 is latest and has held since 2026-03
- MW changes: 101.5 → 100.4 → 103.8 → 103.65 (minor capacity tweaks, not a red flag)
- IA signed 2024-07-02 ✓ — project has a signed interconnection agreement
- FIS approved 2025-09-18 ✓
- Meets 6.9(1) 2025-09-18 ✓
- No construction dates, no energization/COD approvals
- Screening complete 2022-11-30 (very early vintage for a 2025-era project)
T2 start

## T2 — delivery pins
- gmaps.py: HTTP 429 on both attempts (rate-limited); no pins retrieved
- Result: 0 pins found

T3 start

## T3 — web sweep
- Developer: Piedra Solar, LLC (Delaware LLC) — covers BOTH 25INR0168 (Piedra Solar) and 25INR0169 (Piedra BESS)
- TSP: Oncor Electric Delivery Company LLC
- IA signed 2024-07-02 (matches queue data); Amendment No. 1 executed 2024-10-31
- 25INR0168 is sibling solar project (co-sited); BESS is the storage component
- 86% build probability per ercotqueue.com (3rd-party estimate)
- No parent company, no press releases, no news articles found
- news_found: false (no primary-source news about THIS project)

T4 start

## T4 — PUCT Interchange
- PUCT Interchange returns HTTP 402 on all fetch attempts (auth required)
- Docket identified via DDG: **35077, item 2310** — "Amendment No. 1 to SGIA between Oncor and Piedra Solar, LLC"
- IA original date: 2024-07-02; Amendment No. 1: 2024-10-31
- PDF URL: interchange.puc.texas.gov/Documents/35077_2310_1558933.PDF — not accessible
- ia_found: true (confirmed via DDG snippet); document not downloaded

T5 start

## T5 — abatements
- Ch.313 Comptroller portal: no dedicated searchable list accessible via WebFetch
- DDG search for Ch.313/JETI + Piedra Solar/BESS + Freestone: no results
- abatement_found: false — normal for post-2022 BESS project (Ch.313 expired; JETI replacement is narrow)

T6 start

## T6 — imagery
- Site candidate: midpoint estimate along Navarro–Limestone 345-kV corridor ~31.75°N, 96.51°W (method: POI description interpolation; confidence: low)
- Chip: s2_center_2026-06-15.png (2 km buffer, 2026-06-15 ±15d)
- Observation: rural ag land + tree cover, heavy cloud cover over ~30% of frame, no visible gravel pad or container rows characteristic of BESS
- construction_visible: false (but inconclusive — cloud cover + rough site estimate)
- Budget: 1 full-size read used; no activity spotted → no re-center or baseline per rules

T7 start

## T7 — outputs written
- triage_findings.json ✓
- triage.md ✓
- Turns used: 22 of 35 budget
