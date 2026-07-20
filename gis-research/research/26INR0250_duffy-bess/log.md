# Triage log — 26INR0250 Duffy BESS

T1 start
T1 result: 35 snapshots 2023-08-01→2026-06-01. COD drift ×2: 2026-03-31→2026-09-15→2026-12-31.
Key milestones: FIS approved 2026-03-03, IA signed 2025-07-28, Meets 6.9(1) 2025-08-04, Meets all 6.9 2026-04-27.
No construction start/end or energization dates. Capacity: 235.7→241.05 MW.

T2 start
T2 result: gmaps.py returned HTTP 429 (rate-limited) on all 3 queries (exact name, name+county, LLC name). No pins found. Budget exhausted.

T3 start
T3 result: DDG blocked (CAPTCHA). Bing: 4 queries for "Duffy BESS", "Duffy BESS LLC", "26INR0250", "Duffy battery Matagorda ERCOT" — all returned singer Duffy / unrelated results. No web presence, no developer name, no news. Normal for early-stage project.

T4 start
T4 result: PUCT Interchange returns HTTP 402 on all search endpoints (requires auth/session). No puct_search.py script available. Bing site search blocked by CAPTCHA. IA known to exist (signed 2025-07-28 per queue data) but PDF not retrieved. Budget exhausted.

T5 start
T5 result: No Ch.313 or JETI abatement found. TX Comptroller Ch.313 page is informational only (no search). Bing returned no JETI/abatement hits for Duffy BESS or Matagorda battery storage. Normal for post-2022 BESS project.

T6 start
T6 result: CDSE creds unavailable (HTTP 401 on all chip requests). Site candidate anchored to WAP→STP 345kV corridor: STP nuclear plant at ~28.796°N, 96.049°W; Wadsworth TX at ~28.836°N, 96.078°W. No imagery retrieved. Construction status unknown.

T7 start
T7 result: triage_findings.json + triage.md written. Turns used: ~28. STOP.

## Deep Scan

DS1 start: Stage 1 — LLC/developer + Stage 2 county/PUCT parallel
- Triage blockers: PUCT 402, gmaps 429, CDSE 401, DDG/Bing CAPTCHA
- Note: sibling project 23INR0057 Duffy Solar uses identical POI (WAP→STP CKT39 PTI# 5915-44000) — likely same developer
- OSM from Duffy Solar DS: AEP Wadsworth substation at 28.7851°N, 95.9380°W; STP switchyard ~28.799°N, 96.051°W
- CenterPoint 345kV line (id=1060258405): runs 28.8279,-95.8591 to 28.8018,-96.0498 (~18 km W-E in Matagorda Co)

DS2 result: STAGE 1 — Developer identity NOT established.
- TX Comptroller entity search: JS-rendered (no curl API available at tested endpoints)
- TX SOS SOSDirect: requires paid account ($1/search)
- SEC EDGAR: HTTP 403 on all search endpoints
- Bing/DDG web search: "Duffy BESS" consistently drowns in singer-Duffy noise; zero energy project results
- Sibling project 23INR0057 Duffy Solar also has zero web presence (confirmed in that project's deep scan)
- NEGATIVE: Developer chain fully unknown via available tools

DS3 result: STAGE 2 — County records
- PUCT Interchange: HTTP 402 on all queries (session auth required); IA PDF not retrieved
- Matagorda CAD: SSL certificate error (unable to get local issuer cert); inaccessible
- JETI (TX Comptroller): Only one Matagorda County agreement found: Formosa Plastics / Palacios ISD (petrochemical). No battery storage or "Duffy" entry. EXPECTED for post-2022 BESS — JETI rarely applies.
- Ch.313: Expired 2022; no post-2022 applications possible; expected miss.
- NEGATIVE: No county paper trail. IA known to exist but unread.

DS4 result: STAGE 3 — Site pinpoint
- Wadsworth village: 28.8327°N, 95.9358°W (Nominatim)
- AEP Wadsworth Substation: 28.7851°N, 95.9380°W (from sibling-project OSM DS)
- CenterPoint 345kV WAP-STP CKT39 eastern terminus: ~28.828°N, 95.859°W; western terminus (near STP): ~28.802°N, 96.050°W
- Tap location: "Tap 345kV WAP to STP CKT39" = could be AT the WAP (eastern CenterPoint) substation or at a mid-line switch
- No delivery pin (gmaps 429/quota); no parcel data (CAD inaccessible); no PUCT POI coordinates (402)
- Site candidates: (A) 28.7851°N, 95.9380°W [AEP Wadsworth sub], (B) 28.8279°N, 95.8591°W [CenterPoint eastern terminal], (C) somewhere along the 18-km WAP-STP 345kV corridor
- Confidence: LOW

DS5 result: STAGE 4 — Satellite imagery (WAP area, tight BESS search)
All 6 full-size reads used:
1. s2_2026-06-01_wap_tight.png (1km @ AEP Wadsworth 28.785,-95.938): Existing substation complex, no BESS pad, no new grading visible. Partly cloudy.
2. s2_2026-06-01_wap_3km.png (3km same): Wider view confirms substation plus surrounding farmland. No new industrial pads. Partly cloudy.
3. s2_2025-10-01_wap_tight.png (1km @ AEP Wadsworth, Oct 2025): Clear image — existing substation only, same footprint as Jun 2026. NO change.
4. s2_2026-06-01_stp_end.png (2km @ STP 28.799,-96.051): STP nuclear plant/cooling pond clearly visible. No BESS construction near switchyard. Partly cloudy.
5. s2_2026-06-01_wap_east_tight.png (1km @ CenterPoint E terminus 28.828,-95.859): SMALL PALE RECTANGULAR FEATURE visible near center — could be graded pad or light-colored structure. Inconclusive due to cloud shadows.
6. s2_2025-10-01_wap_east_tight.png (1km same, Oct 2025): Very cloudy — cannot confirm presence/absence of same feature. No comparison possible.
- Corridor midpoint (2km @ 28.810,-95.960): Cloudy farmland, no construction.
- Contact sheet: imagery/contact_sheet.png (8 frames)

IMAGERY VERDICT: No confirmed construction activity. AEP Wadsworth substation area shows no BESS development Oct 2025 through Jun 2026. Possible pale feature at CenterPoint eastern terminal (28.828,-95.859) in Jun 2026 is inconclusive — could be a small structure, tarp, or artifact; cannot distinguish from BESS pad at 10m resolution with cloud interference. No battery container rows or gravel pad definitively visible anywhere along the WAP-STP corridor.

DS6: STAGE 5 — Synthesis
- findings.json written (real_early verdict, 2027-Q4 independent COD, high drift risk)
- dossier.md written
- queue_history.py run: 35 snapshots, 2 COD changes confirmed
- build_brief.py run: brief.html written (6 KB, 3 images)
- build_index.py run: 101 projects indexed
RESEARCH COMPLETE.
