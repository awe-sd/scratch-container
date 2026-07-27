# Research Log — Mesa View Storage (25INR0417)

**Project:** Mesa View Storage | **INR:** 25INR0417 | **Date:** 2026-07-19
**Researcher:** Claude Sonnet 4.6

---

## Triage summary (prior session 2026-07-18)
- IA signed 2024-09-09 (document not yet retrieved)
- FIS approved 2026-06-11 (very recent, first appearing 2026-06-01 snapshot)
- 5 prior COD slips: 2025-05-31 → 2026-05-16 → 2026-10-31 → 2027-01-29 → 2027-06-15 → 2027-07-15
- Capacity halved: 501.9 MW → 251.3 MW (Aug-Oct 2024)
- No developer identified, no news, no construction milestones
- CDSE imagery blocked (HTTP 403) in triage — needs retry
- Site candidate: KINGMTSW #842 substation area, ~31.40, -102.00, Upton County — LOW confidence

## Deep scan threads
1. PUCT Interchange — retrieve IA document (signed 2024-09-09)
2. TX SOS / TX Comptroller — identify developer behind "Mesa View Storage, LLC"
3. KINGMTSW substation coords + imagery

---

## Stage 1 — LLC → parent chain

### 2026-07-19 — TX Comptroller entity search
- Query: "Mesa View Storage" — franchise tax portal returned redirect loop (JS-only)
- Result: 0 results returned via API call; TX SOS requires paid SOSDirect account — NOT ACCESSIBLE
- Result: SEC EDGAR full-text search: 0 hits for "Mesa View Storage" (confirmed via curl to efts.sec.gov)
- Negative evidence logged: no SEC filings, no news, no press releases found
- Developer identity: UNKNOWN — anonymous shell LLC

### 2026-07-19 — Web searches
- Google blocked automated fetch (HTTP 403 on all queries)
- No PR newswire, no LinkedIn, no project announcement found
- Project is anonymous — no developer attributed in any public source

## Stage 2 — County records

### 2026-07-19 — Upton CAD owner search
- Query: "MESA VIEW STORAGE" via uptoncad.org GetAutoSuggest → 0 results
- Expected for BESS: thin county trail, land typically leased not owned by LLC
- No abatement (Ch.313/JETI): post-2022 projects typically don't file Ch.313; JETI not found
- Upton County Commissioners Court: website DNS not resolving (upton.tx.us)

### 2026-07-19 — PUCT Interchange IA search
- PUCT Interchange requires JavaScript — direct curl/fetch returns static SPA shell with no data
- Could not retrieve IA document or control number — BLOCKED
- Queue data confirms IA signed 2024-09-09 and Financial Security + NTP provided starting Mar 2026 snapshot

### 2026-07-19 — Queue parquet deep read
- NTP milestone: first appeared Mar 2026 (previously "No" through Feb 2026) — NTP issued ~Feb/Mar 2026
- This is 17+ months AFTER IA signing (Sep 2024) — significant delay before NTP
- FIS approved 2026-06-11 (VERY recent — only 5 weeks before this research date)
- ginrStudyPhase latest: "SS Completed, FIS Completed, IA" — full queue milestones met
- No construction start, no construction end reported in any snapshot

## Stage 3 — Site pinpoint

### 2026-07-19 — EIA-860 Plant database (2025 Early Release)
- King Mountain Wind Ranch 1 (FPL Energy Upton Wind LP): 31.2092, -102.2417 — confirms wind farm location
- Upton County BESS (VESI Upton County BESS, LLC): 31.23924, -102.32169
- Castle Gap Solar Hybrid: 31.255, -102.272
- King Mountain Solar: 31.235934, -102.12285
- Cluster of BESS/solar around 31.21-31.26, -102.12 to -102.32 in Upton County
- POI is "Tap 345 kV KINGMTSW (#842) to NORTMC (#76000)"
  - NORTMC = likely "North McCamey" based on bus naming convention
  - Only one other project taps NORTMC (#76000): 28INR0086 West Royal Natural Gas (bus L_NORTMC5_1Y 345kV)
  - King Mountain Wind Farm coordinates per Wikipedia: 31.2378°N, 102.2378°W
  - KINGMTSW (#842) is the King Mountain Switch West 345 kV substation, ~31.21, -102.24
- Google Maps pin search: rate limited (HTTP 429 — gmaps.py failed)
- Site estimate: 31.21, -102.24 (KINGMTSW area) — MEDIUM confidence based on POI text and EIA cluster
  - NORTMC bus connects northward toward McCamey (~31.33, -102.22)
  - BESS would be sited near KINGMTSW or between KINGMTSW and NORTMC
  - Best estimate: 31.22-31.24, -102.20 to -102.24

## Stage 4 — Satellite imagery

### 2026-07-19 — CDSE imagery attempts
- Attempt 1 (triage session 2026-07-18): HTTP 403 on all chip requests
- Attempt 2 (this session): HTTP 403 again — account locked for "maximum concurrent sessions"
- Root cause: multiple triage sessions consumed session slots; account temporarily locked
- NO IMAGERY OBTAINED — all imagery evidence is missing
- Negative evidence: construction stage UNKNOWN

## Budget warning received — synthesizing with available evidence

