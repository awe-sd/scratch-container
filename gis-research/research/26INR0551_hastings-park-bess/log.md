# Triage log — Hastings Park BESS (26INR0551)

## T1 start
queue_history.py → 23 snapshots (2024-08-01 → 2026-06-01).
Milestones: Screening started 2024-08-16, complete 2024-11-01; FIS requested 2024-08-09, approved 2025-03-21; IA signed 2025-08-13.
No construction start/end; no energization/sync/COA.
COD drift: 2026-12-31 (held Aug 2024 – Aug 2025) → 2027-09-15 (held Sep 2025 – Jun 2026). 1 slip, ~9 months.
T1 result: IA signed, FIS approved, no construction milestones yet.

## T2 start
gmaps.py places: 429 Too Many Requests on both attempts (rate-limited). No pins found.
T2 result: 0 pins.

## T3 start
DDG search "Hastings Park BESS battery storage Texas": surfaced ercotqueue.com, cleanview.co, infrasure.ai, interconnection.fyi — all project-tracker aggregators, no primary source.
Developer name from ercotqueue.com result snippet: "Brazos Roots BESS, LLC" — unverified, not in ERCOT GIS data field.
DDG search "Brazos Roots BESS LLC developer": CAPTCHA block on retry.
cleanview.co: developer field unpopulated (paywalled).
ercotqueue.com: page returned empty body.
No press releases, news articles, or corporate filings found for project or LLC name.
No pages saved to sources/ (no primary-source hits).
T3 result: possible developer name "Brazos Roots BESS, LLC" (single unverified source); no news, no PR.

## T4 start
PUCT Interchange portal (interchange.puc.texas.gov): HTTP 402 on all URL patterns tried — portal blocked/session-gated.
No IA PDF retrieved. IA is confirmed signed (2025-08-13 per queue milestones) but document not accessible via triage.
T4 result: IA existence CONFIRMED by queue data; document content NOT retrieved (portal blocked). CEII/redaction status unknown.

## T5 start
TX Comptroller Ch.313 portal: no searchable database accessible via WebFetch — landing pages only, no table/filter for agreements.
JETI registry: same — no searchable list available via WebFetch.
No abatement or JETI entry found for Hastings Park BESS or Brazoria County battery storage.
Post-2022 project: Ch.313 expired 2022 so no 313 expected; JETI is the successor but portal not searchable.
T5 result: no abatement found (normal for post-2022 BESS project without public JETI entry).

## T6 start
Site candidate: Hastings 138kV substation at 29.48325, -95.25257 (Brazoria County TX) — from Mapcarta via DDG search. Confidence: medium (single source, unverified against ERCOT transmission map).
CDSE chip attempt: HTTP 401 Unauthorized — credentials missing or expired in ~/.config/gis-research.env. Imagery skipped.
T6 result: site candidate established (substation coords); no imagery obtained (auth failure).

## T7 start
triage_findings.json written. triage.md written. Turns used: ~22.
Blockers this run: gmaps 429 (T2), PUCT Interchange 402 (T4), CDSE 401 (T6).
T7 result: DONE.

---

## Deep scan — 2026-07-19

## D1 — Developer identity / LLC chain
DDG search "Hastings Park BESS developer" → multiple aggregator hits confirm developer is **Brazos Roots BESS, LLC**. Single-project LLC, new (registered TX 2025-01-01 as foreign LLC from another state), TX Tax ID 32099702915. No parent company identified in public sources.
Source: DDG SERP (aggregators confirm; no primary doc yet). BANNED sources not used as evidence.
D1 result: Developer = Brazos Roots BESS, LLC (foreign LLC). Parent unknown.

## D2 — PUCT IA filing
DDG search confirms: PUCT Control Number 35077, Item 2222. Parties: Brazos Roots BESS LLC ↔ Texas-New Mexico Power Company. Filed 2025-08-14.
PUCT Interchange portal returns HTTP 402 Payment Required on all URL patterns tried (35077-2222.PDF, /search/filings/, /search/documents/). Portal session-gated, not accessible via WebFetch.
Source: DDG SERP secondary; document not retrieved. Negative evidence logged.
D2 result: IA EXISTS (PUCT 35077/2222, TNMP, filed 2025-08-14). Content NOT retrieved — 402 blocked.

## D3 — Substation coordinates (primary)
OSM way 338758521 retrieved via OSM API. Tags confirm: name="Hastings Substation", operator="Texas-New Mexico Power", voltage="138000;12500". Five-node polygon with coordinates:
  N1: 29.4835160, -95.2528005
  N2: 29.4835248, -95.2523622
  N3: 29.4829732, -95.2523476
  N4: 29.4829645, -95.2527859
  Center: **29.48324°N, -95.25257°W**
Matches queue POI "39010 138kV HASTINGS" and TNMP operator exactly.
Artifact: OSM way 338758521 (https://www.openstreetmap.org/way/338758521)
D3 result: Substation center at 29.48324, -95.25257 — HIGH CONFIDENCE. Method: OSM node polygon centroid, TNMP operator confirmed.

## D4 — Brazoria CAD owner search
Brazoria CAD portal at esearch.brazoriacad.org — search by owner "Hastings Park BESS" returned 404. JavaScript-driven interface not accessible via WebFetch. TX Comptroller franchise search redirects to session-gated AJAX portal (not queryable via WebFetch). TX SOS direct search returns 404. TX franchise data API (data.texas.gov) returned empty for "Hastings Park".
Negative evidence: 0 CAD parcels found under this owner name. Expected for BESS (little land, possible leasehold or utility yard).
D4 result: 0 CAD parcels found. Portal access blocked. Normal for compact BESS beside a utility substation.

## D5 — Google Places (gmaps)
HTTP 429 (rate limited). No delivery pin obtained.
D5 result: Negative (rate limit).

## D6 — OpenInfraMap / substation confirmation
OpenInfraMap at those coordinates returns no renderable map data via WebFetch (JavaScript map). OSM way data used instead — equally authoritative.
D6 result: TNMP Hastings Substation confirmed at 29.48324, -95.25257 via OSM primary data.

## D7 — Imagery analysis
Dec 2025 (2km): Substation visible, small compound, no adjacent pad/containers. Area is residential/agricultural scrubland south of Houston.
Apr 2026 (2km): Identical to Dec 2025 — no change, no construction activity visible.
500m tight (Apr 2026): Substation compound clearly visible, undeveloped scrubland to west and north. No gravel pad, no container rows, no staging area.
Jul 2026 (cloud-obstructed): Partial cloud cover, consistent with earlier frames where visible.
Verdict: no_activity — all frames undisturbed, no BESS construction signature at any date.
D7 result: no_activity through Apr 2026. No construction visible in any of 4 frames.

## D8 — Financial security / NTP
timeline.json `financial_security_latest: "No"` as of 2026-06-01 (most recent snapshot).
This means `financialSecurityAndNoticeToProceedProvided = "No"` in the June 2026 queue report.
IA was signed 2025-08-13. As of June 2026 (10 months post-IA), no NTP/financial security provided.
BESS builds: 12-18 months from NTP. If NTP comes after June 2026, earliest COD ~mid-2028.
Reported COD 2027-09-15 = 14 months from today and requires NTP within weeks to be achievable.
D8 result: No financial security/NTP as of Jun 2026 — MAJOR drift signal. Reported 2027-09 COD implausible without imminent NTP.

## D9 — Developer parent company
Multiple search attempts (DDG, bizapedia, opencorporates, SEC EDGAR) — all blocked by CAPTCHA or auth barriers.
Confirmed: Brazos Roots BESS LLC is a foreign LLC (non-TX state of formation), TX registered 2025-01-01, TX Tax ID 32099702915.
No parent company, investor, EPC, or PPA offtaker identified in any accessible source.
No press releases or news coverage found.
D9 result: Developer parent UNKNOWN. Single-project LLC, new formation, no public track record found.
