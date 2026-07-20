
T1 result: 52 snapshots. COD drifted 4 times: 2024-04-15 → 2025-02-14 → 2025-04-15 → 2027-09-30 → 2028-05-11. IA signed 2025-12-18 (first in 2026-01-01 report). FIS approved: not achieved. Construction milestones: none. Capacity stable at 221.78 MW since 2024-05-01.

T2 start

T2 result: gmaps.py returning HTTP 429 (rate-limited) on all 4 queries. Budget exhausted (2 attempts = 1 retry each). No pins found.

T3 start

T3 result: Developer identified as Palmera Solar Development, LLC (from queue-tracking aggregator hit). No press releases or direct news found. Second search for LLC registration blocked by CAPTCHA. Third search (Palmera Solar + Utley/Freestone) returned no results. No source pages saved — only aggregator hits, not primary sources about this project.

T4 start

T4 result: PUCT Interchange portal returns HTTP 402 on all URL attempts (requires authenticated session). DDG search for PUCT filings blocked by CAPTCHA. IA signed date confirmed from queue data (2025-12-18) but no PDF obtained. Budget exhausted. No IA document retrieved.

T5 start

T5 result: TX Comptroller Ch.313 page navigates to overview pages only — no direct searchable database accessible via WebFetch. JETI not checked (budget exhausted at 4 calls). No abatement found. Post-2022 project so Ch.313 is expired program; JETI miss is normal.

T6 start

T6 result: Site candidate = Big Brown Switch area (~31.87,-96.28), POI-infrastructure method, low confidence (no pin, no abatement map). 2 of 9 grid chips downloaded (7 failed: CDSE RemoteDisconnected). Contact sheet read: rural/agricultural land, wooded terrain, small settlement — no solar panel arrays, no cleared/graded land, no construction staging visible. No construction signal.

T7 start

T7 complete. triage_findings.json + triage.md written. Turns used: ~26. STOP.

## Deep scan — 2026-07-19

### Stage 1 — LLC / parent chain

- TX Comptroller taxable entity search (mycpa URL) → redirects to non-queryable page (JS-driven form). API endpoint forbidden (403). No result.
- Bing/DuckDuckGo searches for "Palmera Solar Development" Texas → no primary-source hits; only unrelated entities named Palmera. Developer identity from triage pass was aggregator-sourced; NOT verified from primary source.
- Bing "Utley Solar" Freestone Texas → no relevant results.
- SEC EDGAR search for "Utley Solar" and "Palmera Solar" → 403 blocked.
- SOSDirect (TX SOS) → requires authenticated session (SOSDirect paid portal).
- "Palmera Solar" ERCOT, PUCT searches → no primary results found.
- NEGATIVE: No primary evidence of developer identity obtained.

### Stage 2 — County records

- Freestone CAD (freestonecad.org) → "Server maintenance" all attempts; no property search accessible.
- PUCT Interchange search for "Utley Solar" → 402 Payment Required on all URL attempts; IA PDF not retrieved.
- PUCT PUCT interchange via Bing → no control number surfaced.
- TX Comptroller Ch.313 / JETI: post-2022 project, Ch.313 expired. JETI search not reachable (JS-driven). Not finding abatement.
- Freestone County commissioners court search → not yet attempted.
- NEGATIVE: No IA PDF, no CAD parcels, no abatement found.

### Stage 3 — Site pinpoint

- Nominatim "Utley Texas" → Utley hamlet in Bastrop County (30.1818, -97.4208); NOT in Freestone. Project name not derived from a Freestone community.
- Big Brown Power Plant coordinates confirmed: 31.8225, -96.0582 (Freestone County), per Nominatim.
- POI: "Tap 345kV 3381 Big Brown Switch - 3391 Jewett" → solar project taps the Oncor Big Brown–Jewett 345kV line.
- Jewett city (Leon County) ~31.36, -96.14. The 345kV line runs roughly N-S; tap point likely in Freestone County near Big Brown.
- Site candidate: vicinity of Big Brown at 31.82, -96.06 (Freestone Co.), method=POI-infrastructure, confidence=low-medium.
- gmaps.py → 429 rate limit on all queries. No delivery pin found.
- NEGATIVE: No Google Maps pin, no parcel situs, no news coords. POI-based location only.

### Stage 2 (continued) — County records

- Freestone County appraisal district: site in server maintenance throughout all attempts; no owner-name search possible.
- PUCT Interchange: consistently 402 on all URL patterns. IA PDF not retrieved.
- Ch.313/JETI: post-2022 project, Ch.313 expired 2022. JETI portal JS-driven, not accessible.
- Freestone County commissioners court website: co.freestone.tx.us DNS error; freestonecounty.org DNS error; no court minutes retrieved.
- NEGATIVE: No abatement, no CAD, no IA PDF, no court minutes found.

### Stage 2 — ERCOT parquet context find (KEY)

- Queried ercot_generation_interconnect.parquet for all Freestone County projects in latest snapshot.
- BM Freestone Energy Center (29INR0298) has exact coordinates **31.813367°, -96.147730°** embedded in its POI description for the Big Brown W switch area. This is the same 345kV line Utley Solar taps (3381 Big Brown Switch W - 3391 Jewett N).
- Utley Solar POI = "Tap 345kV 3381 Big Brown Switch - 3391 Jewett" → same circuit as BM Freestone (Big Brown W to Navarro corridor).
- Jewett city (Leon Co): ~31.362, -96.143. The 345kV line runs roughly N-S from Big Brown W (31.813, -96.148) to Jewett N, through southern Freestone County.
- Site candidate revised: somewhere along 345kV corridor ~31.5–31.8 lat, ~-96.14 to -96.18 lon (Freestone County, S of Big Brown W switch).
- Confidence still low — no parcel, no pin, no abatement map.

### Stage 3 — Site pinpoint update

- Original triage candidate (31.87, -96.28) now assessed as WRONG — that was the wrong portion of Freestone Co.
- Revised candidate: 31.813, -96.148 (Big Brown W switch area) or nearby along 345kV corridor S toward Jewett.
- No Google Maps pin obtained (429 rate limit).
- No parcel situs.
- No news/photo coords.

### Stage 4 — Satellite imagery

- Big Brown plant center (31.822, -96.058): former lignite plant and mine visible; no solar activity. Note: solar site would NOT be on the plant footprint but on agricultural land near the 345kV line tap.
- Triage imagery (31.84-31.87, -96.28-96.31): rural wooded/agricultural land, no solar activity.
- Grid chip (31.670, -96.110): rural wooded residential land, no solar activity.
- CDSE auth (token 401) failing after initial cached chip; unable to get new imagery for revised candidate area.
- NEGATIVE result: no construction visible in ANY chip acquired. Note: the site has NOT been pinpointed with confidence, so imagery may simply not cover the right location.

### Milestone/queue analysis (KEY FINDING)

From parquet history (52 snapshots):
- FIS requested 2022-03-09 → STILL NOT APPROVED as of 2026-06-01 (4+ years unresolved).
- IA signed 2025-12-18 (without FIS approval — unusual sequencing per ERCOT process).
- Financial security: NEVER posted (financialSecurityAndNoticeToProceedProvided = "No" in all 52 snapshots).
- Notice to proceed: never provided (same field).
- 5 COD changes in 4 years: 2024-04 → 2025-02 → 2025-04 → 2027-09 → 2028-05.
- COD slipped from original 2024-04-15 to 2028-05-11 — a 49-month total drift.
- This is a major red flag for a real/active project: no financial security despite IA signed; FIS unapproved after 4 years.


### Stage 5 — Synthesis

- findings.json written: verdict=unclear, cod=2029-Q2, drift=high
- dossier.md written
- queue_history.py run: timeline.json + timeline.md refreshed (same data as triage)
- build_brief.py run: brief.html generated
- build_index.py run: index refreshed (108 projects)

### Summary of key findings

1. FIS requested 2022-03-09, STILL unapproved 2026-06-01 (4+ years, 52 snapshots). Anomalous: IA signed Dec 2025 without FIS approved.
2. Financial security NEVER posted in all 52 snapshots. No notice to proceed.
3. Developer (Palmera Solar Development LLC) has zero public web presence — no press releases, no project pages, no regulatory filings findable via exhaustive web search.
4. 5 COD changes totaling 49-month drift (2024-04-15 → 2028-05-11).
5. No imagery of confirmed site: CDSE auth failed for revised candidate; imagery coverage was incomplete/wrong area.
6. PUCT Interchange blocked (HTTP 402 all patterns); IA PDF not retrieved.
7. Freestone CAD in maintenance; no parcels found.
8. Site best estimate: ~31.813, -96.148 (Big Brown W switch corridor, S through Freestone Co), confidence=low.
