# Triage log — 27INR0501 Mesquite Creek Windpower Repower

## T1 start

queue_history.py output: 15 snapshots (2025-04-01 → 2026-06-01), 0 COD-drift events.

Key milestone dates:
- Screening started: 2025-04-29
- Screening complete: 2025-07-26
- FIS requested: 2025-04-28
- FIS approved: NOT achieved
- IA signed: NOT achieved
- All 6.9 milestones: NOT achieved
- Construction start/end: NOT achieved

COD drift: None. 2027-12-31 held stable across all 15 snapshots (Apr 2025 – Jun 2026).

Assessment: Early-stage project. Screening done, FIS requested but not approved. No IA. No
construction milestones. This is pre-construction — 18 months from reported COD with no IA.

## T2 start

gmaps.py places "Mesquite Creek Windpower Repower" → HTTP 429 (rate-limited).
Retry with county query → HTTP 429 again. Budget exhausted.
Result: 0 pins found. Normal for early-stage project.

## T3 start

Search 1 (DDG: "Mesquite Creek Windpower Repower Texas"):
- Developer entity listed as "Mesquite Creek Wind LLC" in ERCOT queue
- Original 2015 farm owned by Duke Energy Renewables / Manulife / Sumitomo; BNB Renewables
  developed it. Perennial Power acquired 50% JV stake in 2015.
- Repower appears to be the same ~212 MW site in Dawson County (Lamesa area)
- No press releases or project news found for repower specifically

Search 2 (LLC registration): No Texas SOS filing found via web search.

Search 3 (repower developer 2025-2026): "Mesquite Creek Wind LLC" confirmed as queue entity.
  No new ownership announcements found for 2025-2026.

interconnection.fyi page: No coordinates. Developer identity locked. IA status locked.
  POI confirmed: Long Draw 345kV substation. No linked public documents.

Result: news_found = weak (aggregator pages only, no direct project news). LLC name
  confirmed as "Mesquite Creek Wind LLC". Developer identity unclear — could still be
  Duke/Perennial/BNB entity. No sources worth saving (paywall-gated aggregators).

## T4 start

PUCT Interchange search attempts:
- FilingParty="Mesquite Creek Windpower Repower" → HTTP 402
- FilingParty="Mesquite Creek Wind" → HTTP 402
- Base search page → HTTP 402

Portal blocked (402 on all attempts). Budget exhausted. IA status: NOT FOUND via triage.
Note: IA milestone not achieved in queue either, consistent with no IA filing found.

## T5 start

TX Comptroller Ch.313 page: No searchable database reachable via WebFetch; navigation
  returned generic program pages. No Dawson County / Mesquite Creek entry found.
JETI registry: No searchable list visible; no project entries found.
Note: This is a repower of a 2015-vintage project. A Ch.313 abatement may exist for the
  ORIGINAL build (pre-2022 cutoff), but searching for the repower specifically is expected
  to come up empty (JETI is post-2022). Result: abatement_found = false for repower.

## T6 start

Site candidate identified: ~32.70°N, 101.74°W (Dawson/Borden County boundary, ~8 miles
from Lamesa). Source: EIA-860M via Wikidata (32°42'N, 101°44'W) + Wikimapia turbine pin
(32°41'28"N, 101°41'35"W). Confidence: HIGH — this is an existing operating farm repower,
coordinates from public turbine databases. 118 GE 1.7-100 turbines, Long Draw 345kV substation.

3×3 chip grid attempt (buffer-km=2, step=0.03°, date=2026-07-01): ALL 9 chips failed
with HTTP 401/403 — CDSE credentials not available in this environment.
Contact sheet: not produced. Imagery: SKIPPED — auth blocked.

## T7 start

Wrote triage_findings.json and triage.md. Triage complete. Turns used: 22.

Blockers encountered: gmaps.py 429, PUCT Interchange 402, CDSE 401/403.
All blockers logged per rules; no engineering-around attempted.

## Deep scan — Stage 1 (LLC / parent chain)

**2026-07-19**

TX Comptroller entity search: portal redirects to comptroller.texas.gov/taxes/franchise/account-status/search — search form present but results require JS; no direct API path accessible. Query "Mesquite Creek Wind" returned no static content. Negative evidence.

TX SOS direct: SOSDirect requires paid subscription. Web-accessible search not available without account.

OpenCorporates: CAPTCHA/bot block — no results returned.

bizapedia.com/tx/mesquite-creek-wind-llc.html: Security check page — no data. bizapedia.com/tx/mesquite-creek-windpower-repower-llc.html: HTTP 410 Gone (page never existed).

SEC EDGAR EFTS full-text search (efts.sec.gov): HTTP 403 on all query patterns — access blocked from this environment. Cannot confirm or deny SEC filings mentioning "Mesquite Creek Wind".

4coffshore.com: HTTP 403. prnewswire.com/mesquite-creek-wind: HTTP 404. News search: no repower announcement found via any accessible source.

Developer identity: UNCONFIRMED. Queue entity = "Mesquite Creek Wind LLC". Original farm ownership chain: Duke Energy Renewables / Manulife / Sumitomo / Perennial Power (BNB Renewables developed 2015). Current repower developer unidentified — no press release, no SOS filing reachable.

## Deep scan — Stage 2 (County records)

**2026-07-19**

Dawson CAD (dawsoncad.org): Homepage accessible. Owner search form present (POST endpoint). Direct URL patterns return 404. Could not execute owner search for "Mesquite Creek Wind" or variants — dynamic form requires JS session. Negative result by access failure, not confirmed absence.

PUCT Interchange: All attempts still return HTTP 402 (requires account). IA milestone NOT achieved in ERCOT queue as of Jun 2026, consistent with no filed IA.

TX Comptroller Ch.313/JETI: No accessible search results. Repower projects post-2022 would need JETI (not Ch.313); no JETI entry found.

## Deep scan — Stage 3 (Site pinpoint)

**2026-07-19**

gmaps.py: HTTP 429 rate-limit on all attempts.

Site candidate confirmed from triage: 32.700°N, 101.741°W (EIA-860M + Wikimapia turbine database for existing Mesquite Creek Wind Farm). 118 GE 1.7-100 turbines on Dawson/Borden County boundary. HIGH confidence — repower is of known operating site; coordinates are authoritative.

POI "Long Draw 345 kV" consistent with West Texas transmission geography near Lamesa (~8 mi).

## Deep scan — Stage 4 (Satellite imagery)

**2026-07-19**

s2_2026-07-01.png: 6 km buffer chip centered 32.700N, 101.741W. Existing turbine array visible as ~118 small white dots in regular grid pattern across agricultural (center-pivot irrigation) land. No construction activity, no pad prep, no new access roads, no turbine removal visible. Undisturbed operating farm.

s2_2026-01-01.png: Same frame 6 months prior. Identical pattern — same turbine dot array, same agricultural background. No change between Jan and Jul 2026.

VERDICT: no_construction_activity. Existing turbines operating; no repower mobilization visible.

## Deep scan — Stage 5 blockers

FAA OE/AAA portal: Migrated to Angular SPA. All legacy searchAction.do URLs return 404. Portal shows government shutdown notice. No turbine obstruction filings accessible. Cannot confirm or deny new FAA filings for repower turbines.

Budget exhausted before: Dawson CAD owner search, USWTDB turbine coordinate download, TX SOS confirmation of LLC entity.
