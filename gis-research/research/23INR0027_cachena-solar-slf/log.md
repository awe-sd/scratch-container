# Triage log — Cachena Solar SLF (23INR0027)

T1 start

## T1 — Queue history

- 71 snapshots (2020-08-01 → 2026-06-01)
- 6 COD drifts: 2023-06-01 → 2023-12-31 → 2024-06-01 → 2024-12-31 → 2025-12-31 → 2026-12-31 → **2027-04-29** (current)
- Milestones: Screening complete 2020-07-13 | FIS requested 2020-08-17 | **IA signed 2021-11-23** | Meets 6.9(1) 2021-11-29 | **FIS approved 2026-06-17** (very recent)
- Notable: IA was signed BEFORE FIS approval (unusual order); FIS only approved ~1 month ago
- Capacity drift: 400 → 408.94 → 440 → 600 → 601.31 → **602.02 MW**
- No construction milestones (start/end/energization/sync/COD) — none achieved
- Result: mature queue entrant (2020), serious milestones, no construction activity on record

T2 start

## T2 — Delivery pins

- gmaps.py: HTTP 429 on first call; one retry also 429 → BLOCKED (per rules: 1 retry, then negative log)
- pins_found: 0 (API rate-limited, not searched successfully)

T3 start

## T3 — Web sweep

- Developer identified: **Clear Fork Creek Solar LLC** (TX entity #0803498583, reg. address El Dorado Hills CA 95762)
- No parent company surfaced; Jeff Sabins listed as CDO (CorporationWiki)
- **Wilson County Commissioners approved 10-year tax abatement July 14, 2025** — county-level, not Ch.313
- Project described as ~6,100 acres along US-87 (Precinct 4), includes BESS component reference
- No press releases, financing news, construction updates, or PPA announcements found
- No dedicated project page saved (no pages directly about this project beyond queue trackers)
- news_found: false (only queue aggregators, no primary reporting)

T4 start

## T4 — PUCT Interchange

- interchange.ercot.com: ENOTFOUND (DNS, not a real host)
- interchange.puc.texas.gov: HTTP 402 on all attempts — blocked/session required
- DDG site:interchange.puc.texas.gov search: CAPTCHA blocked
- IA signed date from T1: 2021-11-23 — IA IS confirmed in queue data but PDF not retrieved
- ia_found: TRUE (via queue milestone; PDF inaccessible this pass)
- DRIFT: queue history shows IA signed 2021-11-23 but FIS only approved 2026-06-17 — unusual gap

T5 start

## T5 — Abatements

- TX Comptroller Ch.313 search: no direct Ch.313 hit found; search tools inaccessible or returned no results
- JETI registry: not checked directly (DDG CAPTCHA blocked all subsequent queries)
- From T3 web sweep: **Wilson County Commissioners approved 10-year tax abatement July 14, 2025** — county-level (Ch.312 or commissioners' agreement, not necessarily Ch.313/JETI)
- Ch.313 expired for new applications post-2022; JETI is replacement — expected miss for post-2022 filing
- abatement_found: TRUE (county-level 10-year, July 2025 — type not confirmed but county commissioner approval is strong signal)
- No application PDF downloaded (not accessible this pass)

T6 start

## T6 — Imagery

- Site candidate: Wilson County / US-87 corridor near Floresville (~29.13°N, -98.16°W) — low confidence (from T3 description: "~6,100 acres along US-87 Precinct 4")
- 3×3 chip grid attempted (center 29.13/-98.16, step ±0.03°, buffer-km 2, date 2026-07-01 ±15d)
- CDSE RemoteDisconnected on 7/9 chips; 2/9 returned successfully
- Contact sheet generated with 2 frames
- Visual review of contact sheet: left chip (29.10,-98.13) shows agricultural farmland, road intersection, small structures — NO solar panel rows, no grading, no construction visible; right chip (29.16,-98.19) rendered black (no data)
- construction_visible: FALSE (limited coverage, no signal in available chips)
- Imagery inconclusive due to partial CDSE failure and low-confidence site location
- No baseline chip run (no clear construction signal to anchor re-center on)

T7 start

## T7 — Outputs written

- triage_findings.json ✓
- triage.md ✓
- Turns used: ~28
- STOP
