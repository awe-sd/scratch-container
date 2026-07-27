# Triage log — Myers Solar (26INR0134)

## T1 start


**Queue history results:**
- First appeared: 2023-06-01; 37 monthly snapshots through 2026-06-01
- COD drift: 3 values — 2026-09-01 (held 18 months) → 2028-07-01 (1 month) → 2028-05-22 (current, held since 2025-01)
- COD slipped ~2 years from original target
- No FIS approved, no IA signed, no construction dates, no energization/sync/COD approvals
- Capacity: 100.94 MW → 101.59 MW (minor bump May 2025)
- Milestone status: stuck at Screening complete (2023-09-20); FIS still not approved
- **Assessment: early-stage project, no completed development milestones beyond screening**

## T2 start

**Delivery pins (gmaps.py):**
- Query 1 "Myers Solar": HTTP 429 Too Many Requests — rate limited
- Query 2 "Myers Solar Bee County Texas": HTTP 429 — rate limited
- Budget exhausted (2/4 calls used, API blocked)
- **Result: 0 pins found; gmaps.py 429 rate-limit**

## T3 start

**Web sweep results:**
- Developer confirmed: **BT Myers Solar, LLC** (not "Myers Solar, LLC" per identity packet)
- TX LLC filed 2023-04-17; registered agent Wayne L. Pope, Farmers Branch TX
- No parent company identified; 0 commissioned projects
- Companion project: Myers Storage 26INR0135 (75.7 MW BESS), same developer/county
- ercotqueue.com rates build-chance at 5% (No IA)
- gem.wiki entry exists but returned 403
- No news articles, permits, or press releases found
- **Result: developer identity clarified; no news; no site coordinates from web**

## T4 start

**PUCT Interchange filings search:**
- interchange.puc.texas.gov returns HTTP 402 on all URL patterns (root, search, documents)
- Portal requires session/auth not available in this environment
- Budget: 4 calls used; all blocked
- **Result: PUCT portal inaccessible; IA status unknown from PUCT; queue shows no IA signed**

## T5 start

**Abatements (Ch.313 / JETI):**
- TX Comptroller Ch.313 applications page: no searchable list rendered; tools require direct portal access
- DDG search for "Myers Solar" OR "BT Myers Solar" + "chapter 313" OR "JETI" OR "tax abatement": zero results
- No abatement application found
- **Result: no abatement found — normal for 2023 entry post-Ch.313 expiry; JETI not registered**

## T6 start

**Site candidate search:**
- No pin from T2 (gmaps blocked)
- No IA found in T4 (portal blocked) → no IA map
- No abatement parcel from T5
- POI "8629 Baez 69 kV": searched OSM Nominatim + DDG (CAPTCHA) — no substation coordinates found; "Baez" not resolvable to a lat/lon
- Best available: county-level only (Bee County, TX) — per checklist rules, SKIP imagery when no better candidate than county
- **Result: no site candidate; imagery SKIPPED per rules**

## T7 start

**Outputs written:**
- `triage_findings.json` — all-negative signals; deep_scan_recommended=false
- `triage.md` — 10-line human summary
- `sources/t3_web_sweep.md` — developer identity and web sources
- `log.md` — this file

**Turns used: 22. Triage complete.**

