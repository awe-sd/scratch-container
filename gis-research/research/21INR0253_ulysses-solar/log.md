# Triage log — Ulysses Solar (21INR0253)

## T1 start
- queue_history.py ran OK — 86 snapshots
- IA signed: 2022-10-03 ✓
- Meets 6.9(1): 2022-12-05 ✓
- Meets all 6.9: 2026-01-21 ✓ (recent — significant)
- FIS approved: 2025-12-15 ✓ (very recent)
- Construction start/end: NOT reported
- COD drift count: 7 changes, original 2021-11-01 → current 2027-03-02 (~16 months slip)
- MW: 150.0 → 151.2 (small bump 2025-05)
- **T1 result:** IA exists, all 6.9 milestones met, FIS very recently approved (Dec 2025). No construction dates yet. 7 COD slips over 4 years. Current COD 2027-03-02 plausible given all 6.9 met Jan 2026 and FIS Dec 2025.

## T2 start
- gmaps.py → HTTP 429 on first call; retry after 10s → 429 again. Budget exhausted.
- **T2 result:** No pins found (gmaps rate-limited, 0 results).

## T3 start
- DDG search "Ulysses Solar Texas news" → found on cleanview.co, infrasure.ai, interconnection.fyi, PUCT filing ref
- DDG search "Ulysses Solar LLC registration" → entity in NY (foreign LLC, filed 2014, address 111 Eighth Ave NY, C T Corporation agent) — likely shell/SPV, not the ERCOT-specific LLC
- Developer identified: **BNB Tennyson Solar LLC** (from infrasure.ai and PUCT cross-ref)
- PUCT filing: control 35077, item 1501 — IA between AEP Texas and BNB Tennyson Solar LLC — returned 402, could not retrieve directly (noted for T4)
- No construction or financing announcements found in any source
- infrasure.ai: financing close probability 25/100, permitting risk 25/100 — flagged as low
- Saved: sources/infrasure_project_page.md
- DDG "BNB Tennyson Solar Ulysses Solar" → CAPTCHA blocked
- **T3 result:** Developer = BNB Tennyson Solar LLC; no news/PR found; PUCT IA filing exists (control 35077); no public financing announcements.

## T4 start
- interchange.puc.texas.gov returns HTTP 402 on all direct URL attempts (filings search, document search, direct PDF URL for control 35077 item 1501)
- DDG site: search → CAPTCHA; Bing site: search → CAPTCHA
- Known IA reference from T3: PUCT control 35077, item 1501, filed 2022-10-18, "Standard Generation Interconnection Agreement" AEP Texas / BNB Tennyson Solar LLC — could not download
- **T4 result:** IA confirmed to exist (control 35077) from T3 cross-reference, but portal is blocked (402). Cannot extract milestone schedule exhibit during triage.

## T5 start
- TX Comptroller Ch.313 page → index/navigation only, no searchable data table returned
- JETI registry page → same, index only
- DDG search for "Ulysses Solar"/"BNB Tennyson" + "Coke County" + chapter 313 → CAPTCHA blocked
- Note: Ch.313 program expired end of 2022; post-2022 projects use JETI. This project entered queue 2019 but is a 2021 INR — could have a 313 agreement if applied pre-2022 expiry
- No abatement found in triage
- **T5 result:** No abatement confirmed. Portal/search not accessible during triage. Normal for post-2022; possible Ch.313 if applied 2021-2022 (deep scan should check directly).

## T6 start
- No pin from T2 (gmaps blocked)
- No abatement/IA map retrieved (T4/T5 portals blocked)
- Attempted to locate "Odysseus Substation 345kV" via DDG, Bing, ERCOT map, OSM Nominatim — no coordinates found
- Only location available: Coke County centroid ~31.87, -100.55 (county ~1,800 km², ~43 km × 42 km)
- County-level only = "somewhere in the county" → SKIP imagery per checklist rules
- **T6 result:** No site candidate. Imagery skipped.

## T7 start
- Wrote triage_findings.json
- Wrote triage.md
- **Turns used: 22** (budget: 35)
- STOP.
