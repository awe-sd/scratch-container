# Triage log — OCI SunRoper (24INR0167)

## T1 start
queue_history.py: 56 snapshots, 5 COD drifts.
COD drift history: 2024-08-30 → 2025-06-01 → 2025-07-01 → 2026-07-01 → 2027-07-12 → 2027-10-01 (current).
Key milestones: FIS approved 2026-04-17; IA signed 2025-07-10; Meets 6.9(1) 2026-04-17.
No construction milestones achieved. Capacity increased 203.53→265.1 MW in Jan 2023.
COD slipped ~3 years from original 2024-08-30. IA signed = meaningful commitment signal.

## T2 start
T2: gmaps.py returned HTTP 429 on both calls (rate-limited). No pins found. Budget exhausted.

## T3 start
T3: DDG 403. Bing searches on "OCI SunRoper", "SunRoper solar Texas LLC", "OCI Solar Power Wharton" — all returned no relevant results. "OCI" likely = OCI Solar Power (San Antonio developer), but no web footprint for this specific project. No sources saved.

## T4 start
T4: PUCT Interchange returns HTTP 402 on all endpoints (requires session/auth). Cannot search FilingParty=OCI SunRoper or Description. No IA documents retrieved. Budget exhausted on blocked portal.

## T5 start
T5: TX Comptroller Ch.313 page has no county-filterable URL; no direct data returned. Bing CAPTCHA blocked final fallback. No abatement found. Normal for post-2022 project (Ch.313 expired; JETI not yet searchable via web). Budget exhausted.

## T6 start
No delivery pins from T2 (gmaps 429). No abatement map from T5. POI description: "tap138kV #43190 South Lane City to #42985 Dyann CKT#60" — names a 138 kV tap between Lane City (#43190) and Dyann (#42985) substations. Lane City is in Wharton County (~29.16N, 96.06W). Using Lane City area as best site candidate, confidence LOW-MEDIUM (infrastructure anchor).
Running 3x3 chip grid around 29.16N, 96.06W.
T6: CDSE API returned RemoteDisconnected on all chip calls (OAuth token endpoint unreachable). No imagery retrieved. Site candidate: ~29.16N, 96.06W (Lane City, Wharton County) based on POI substation names — LOW-MEDIUM confidence infrastructure anchor. No construction verdict possible.

## T7 start
Writing triage_findings.json and triage.md.
T7 complete. triage_findings.json + triage.md written. Turns used: ~28. STOP.

## Deep scan start — 2026-07-19

### Stage 1: Developer / parent chain

**CONFIRMED:** OCI Energy LLC (San Antonio, TX) = developer/owner. Rebranded from OCI Solar Power in July 2024.
- OCI Energy projects page: SunRoper listed as "Under Construction", Wharton County, 260 MW, 2027 target. Source: sources/2026-07-19_ocienergy_projects-portfolio.html

**CONFIRMED:** OCI Energy + Arava Power = joint venture (JV)
- Feb 20, 2025 JV PR: "forming a joint venture to develop Project SunRoper, a 260 MWac solar farm in Wharton County, Texas... ~60 miles SW of downtown Houston... construction slated to begin in 2025." Source: sources/2025-02-20_ocienergy_arava-jv-sunroper.pdf

**CONFIRMED:** Construction financing closed Feb 23, 2026
- ING Capital = lender (construction-to-term loan + tax equity bridge + LCs)
- Total investment ~$394 million; 20-year PPA with Fortune 100 (unnamed)
- EPC = WHC, LLC; Technical advisor = Black & Veatch
- Commercial operation: **"slated to begin commercial operation in Q3 2027"**
- Source: sources/2026-02-23_ocienergy_sunroper-financing.pdf

**CONFIRMED** (OCI news page): Tax equity financing $130M with Greenprint Capital closed June 22, 2026
- Source: sources/2026-07-19_ocienergy_news.html

**CONFIRMED** (OCI news page): Separate La Salle 670 MW project MIPA with Arava announced May 2026 — distinct from SunRoper
- SunRoper MW discrepancy: 265.1 MWac (ERCOT) = 260 MWac (OCI/JV PR) ≈ 347 MWdc (financing PR). DC:AC ~1.31. Consistent.

### Stage 1 negative evidence
- TX SOS SOSDirect = paywalled, no free entity lookup available
- TX Comptroller franchise tax search = form-based POST, no URL query API retrieved
- Arava Power website (aravapower.com, aravasolarpower.com, arava.com) = DNS not found from this container
- PUCT Interchange = 402 on all API endpoints; requires session auth

### Stage 2: County records
- Wharton CAD: multiple URL attempts (wcad.org, wcad.net, wharton-cad.org, whartoncad.com, whartoncad.org, whartoncentral.appraisal.district.texas.gov, search.wcad.org→Williamson CAD) — none resolved to Wharton County CAD
- Solar Power World article: no land/parcel/address info; says construction began 2025
- No Ch.313/JETI abatement found (expected — Ch.313 expired 2022, JETI not web-searchable)

### Stage 3: Site pinpoint
- gmaps.py: HTTP 429 (rate-limited) on all calls — no delivery pins retrieved
- Staticmap: Maps Static API not enabled for this key
- Site candidate remains 29.16N, 96.06W (Lane City, Wharton Co.) from POI substation names only — LOW confidence
- Wharton CAD portal: multiple URL attempts failed (none resolved); no parcel data retrieved

### Stage 4: Satellite imagery (4 of 6 frame budget used)
- 2026-06-01 chip at 29.16N, 96.06W: heavy cloud cover (>60%), uninterpretable
- 2026-03-15 chip at 29.16N, 96.06W: clear — agricultural/Colorado River corridor, NO solar construction
- 2025-11-01 chip: CDSE RemoteDisconnected, no image saved
- 2026-03-15 chip at 29.25N, 96.00W: clear — agricultural + small industrial (El Campo area), NO solar construction
- VERDICT: no_activity at 29.16N, 96.06W and 29.25N, 96.00W. Site candidate not verified.
- Site not found via imagery because parcel/exact location unknown; cannot confirm or refute construction stage

### Stage 5: Budget warning — synthesizing now
