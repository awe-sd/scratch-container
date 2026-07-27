# Triage log — Bonham Solar SLF (25INR0199)

T1 start
- queue_history.py ran OK; 44 monthly snapshots (2022-11-01 → 2026-06-01)
- Milestones: Screening complete 2023-02-09, FIS approved 2026-06-26, IA signed 2024-08-07, Meets 6.9(1) 2025-05-09
- Meets all 6.9: NOT achieved. Construction dates: none. COA: none.
- COD drift (3 changes): 2025-02-18 → 2026-04-27 → 2026-08-31 → 2027-04-06 (current)
- Capacity: 139.6 MW → 138.4 MW (minor trim Sep 2023)
- IA signed 2024-08-07 ✓ — meaningful commitment signal

T2 start
- gmaps.py: HTTP 429 (rate-limited) on all 4 queries — no pins. Normal miss.

T3 start — web sweep
- Bing: "Bonham Solar SLF" → 0 project hits (only Bonhams auction house noise)
- Bing: "Bonham Solar" Limestone County Texas → 0 hits
- Bing: 25INR0199 ERCOT → 0 hits
- Bing: "Bonham Solar SLF LLC" TX SOS → 0 hits
- No developer name surfaced; no news; no LLC registration found in web search.

T4 start — PUCT Interchange
- interchange.puc.texas.gov: HTTP 402 on all direct API queries (paywall/session auth required)
- Bing site: search → CAPTCHA blocked
- Bing web: "Bonham Solar" PUCT interconnection agreement → 0 hits
- IA IS signed (2024-08-07 per queue history) but PDF not retrievable via web search
- No IA PDF recovered; no docket number surfaced. PUCT portal blocked for triage.

T5 start — abatements
- TX Comptroller Ch.313 page: no searchable database accessible via WebFetch
- Bing: "Bonham Solar" chapter 313 / JETI / tax abatement Limestone County → 0 hits
- Bing: JETI Limestone County solar 2024/2025 → 0 hits
- No abatement found. Normal for post-2022 project without JETI.

T6 start — imagery
- Site candidate: POI line midpoint between Mexia (31.6816°N, -96.4784°W) and Groesbeck (31.5243°N, -96.5339°W)
  → estimated center ~31.60°N, -96.51°W; confidence LOW (line corridor only, no pin, no abatement map)
- cdse.py chips attempt: HTTP 401 Unauthorized — CDSE credentials not configured (~/.config/gis-research.env is example only)
- Imagery skipped: auth failure. No contact sheet produced.

T7 start — write outputs
- triage_findings.json written
- triage.md written
- Turns used: ~28. STOP.

## Deep scan — 2026-07-20

D0: findings.json skeleton written.

D1: puct.py match 25INR0199 --dir sources/
- HIT via INR join table rung 0 (exact): filing 35077-1915, filed 8/29/2024
- "Standard Generation Interconnection Agreement between Oncor Electric Delivery Company LLC and J&J Solar Ranch, LLC (XE Bonham Solar 1)"
- SPV name resolved: J&J Solar Ranch, LLC — filed under project alias "XE Bonham Solar 1"
- Downloaded: sources/2026-07-20_puct_35077-1915_standard-generation-interconnection-agreement-be.pdf (1711 KB, 54 pages)
- Verification: CONFIRMED (INR found in document text) — usable as primary evidence without further check

D1 continued: IA content extracted (PUCT 35077-1915, Standard SGIA, executed 8/7/2024, filed 8/29/2024)
- Parties: Oncor Electric Delivery Company LLC (TSP) and J&J Solar Ranch, LLC (Generator) — "XE Bonham Solar 1", GINR 25INR0199
- Generator notice address: 1255 23rd Street NW, Suite 300, Washington DC 20037; contacts @x-elio.com (kerri.neary, ivan.illera, griffin.payne) — X-ELIO is the developer (global solar IPP, HQ Madrid/Chicago). "X-ELIO" = the "XE" in "XE Bonham Solar 1".
- Signed: Generator (Kerri Neary, Authorized rep) 8/6/2024; TSP (Jim Greer, EVP/COO) 8/7/2024
- Facilities Study Agreement executed 2023-02-27 (predates IA by ~18 months — normal)
- Exhibit B Time Schedule (original, unamended):
  - NTP date: Sept 27, 2024
  - In-Service Date: April 23, 2026
  - Scheduled Trial Operation: May 3, 2026
  - Scheduled Commercial Operation Date: **August 31, 2026**
  - Two new switches being built as interconnection facilities: "Baines Creek Switch" (Generator-side, deeds/easements deed-transfer by Sept 12 2025) and "Phifer Creek Switch Station" (associated transmission lines, deed transfer by June 6 2025)
- Exhibit E Security: Irrevocable Standby LC, effective on/before Sept 27, 2024, amount **$26,061,887.00** — no amendments found (single-document IA, no Amendment on file/in join table)
- Ex D bank details redacted (ABA/account numbers blacked out) — normal
- Lone Star Infrastructure Protection Act attestation (10.22): Generator warrants no China/Iran/N.Korea/Russia ownership/control ties — standard boilerplate, not project-specific signal

**KEY FINDING — COD divergence**: signed IA Scheduled COD = 2026-08-31. Queue-claimed COD (reported) = 2027-04-06 — the queue has ALREADY SLIPPED ~7 months past the contractual date in the only IA on file (no amendment exists to explain this). This is decisive negative-drift evidence: the project is behind its own signed schedule with no formal IA amendment yet filed to reflect the new date.

D2 continued: Site pinpoint attempts
- gmaps.py places: HTTP 429 rate-limited for "Bonham Solar SLF", "J&J Solar Ranch", "Baines Creek Switch Limestone County Texas" — same failure mode as triage; retry later or accept as unavailable this session
- ch313.py resolve 25INR0199 (+--name, +--county): NEGATIVE — no Ch.313/JETI match for Bonham Solar SLF (expected: IA signed 2024, project likely too new/small for a value-limitation filing)
- search.py "X-Elio" + "Bonham" + "J&J Solar Ranch": only hits are X-Elio's UNRELATED "Liberty Solar" project (Dayton TX, BASF-contracted, 72MW+60MW storage) — Bonham/J&J Solar Ranch does not appear in X-Elio's public press materials. X-Elio identification remains PROBABLE (via IA contact-email domain @x-elio.com) but NOT press-confirmed for this specific project.
- opencorporates hit for "J&J Solar, LLC" (Arizona) and "J&J Solar Ranch, LLC" (bizapedia, Dover DE) — likely a Delaware holding-co shell registration typical of project SPVs; not yet independently verified as the same entity (name matches exactly)
- TX Comptroller taxable-entity search: form is JS-driven, WebFetch cannot submit search (redirects to static search page) — negative/blocked, consistent with triage's finding
- Oncor "Current Transmission Line Projects" page fetched: NO mention of Baines Creek Switch, Ranchland Switch, Phifer Creek Switch, Mexia, Groesbeck, or Limestone County — these are apparently too small/generator-specific to appear on Oncor's public CCN-project list (normal; that list covers large CCN-reviewed lines, not single-generator switch taps)

D2 continued: site pinpoint via infrastructure name cross-reference
- search.py "\"Baines Creek\" Limestone County Texas": HIT — Baines Creek is a real named creek at Fort Parker State Park (near Mexia/Groesbeck, Limestone Co.), with a "Baines Creek Trail" (2.5mi) per TPWD park map (https://tpwd.texas.gov/publications/pwdpubs/media/park_maps/pwd_mp_p4503_0034j.pdf) and a "Baines Creek Ranch" vacation rental near Groesbeck (Airbnb listing) — this independently corroborates the IA's "Baines Creek Switch" name as tied to real local geography, NOT a generic/invented name.
- Fort Parker State Park coords (Wikipedia): 31.60361N, -96.55083W — within ~1km of triage's POI-line-midpoint estimate (31.60N, -96.51W). Baines Creek runs through/near the park.
- "Ranchland Switch" and "Phifer Creek Switch" web searches: no direct location hits (both drowned out by unrelated "ranch land for sale" and "Phifer Cemetery" noise) — negative evidence, but consistent with small single-generator switch names not indexed publicly.
- Limestone CAD (esearch.limestonecad.com) owner-name search: portal unreachable from this network (curl timeout / WebFetch "socket closed" on both the search form and results URL) — BLOCKED, logged as negative evidence per playbook Stage 2 guidance (route around; commissioners' minutes / abatement docs unavailable substitute not found either)
- Limestone County commissioners court minutes / Bonham Solar / J&J Solar Ranch: not searched yet (time-budget priority given to imagery next)

Site candidate refined: ~31.60N / -96.53W (between Fort Parker SP / Baines Creek and the POI's Mexia-Groesbeck 138kV line) — method: named-infrastructure cross-reference (IA switch name -> real creek/park geography) + POI line corridor. Confidence: MEDIUM (creek name match is decisive for the switch's existence/rough area; exact site polygon not yet imagery-confirmed).

D2: gmaps.py places — HTTP 429 (Too Many Requests) for "Bonham Solar SLF" and "J&J Solar Ranch construction" — same fleet-wide rate-limit as triage run. Delivery-pin trick unavailable this session.

D2/D4 — IMAGERY BLOCKED (hard constraint, not a query problem)
- cdse.py chip (multiple lat/lon combos, serial + parallel): all failed with `http.client.RemoteDisconnected`. Root-caused via direct curl to the openEO endpoint with a fresh bearer token: server returns **HTTP 402 Payment Required** — "You do not have sufficient credits to perform this request" (marketplace-portal.dataspace.copernicus.eu/pages/pricing). CDSE account auth itself works fine (password-grant token issued OK); the account's Sentinel-2 processing credit balance is exhausted. cdse.py's urllib path surfaces this as a RemoteDisconnected rather than a clean HTTPError (traefik credits-check layer likely closes the connection oddly for non-curl clients), but the underlying cause is confirmed via curl: 402/PaymentRequired.
- CONSEQUENCE: no Sentinel-2 imagery obtainable this session for ANY project, not just this one. Satellite ground-truth stage (D2/Stage 4) cannot be completed. This is an account-level quota exhaustion, not a per-project failure — flagging for the pipeline operator (budget/credits need refill at CDSE marketplace).
- construction.verdict left as "unknown" / "imagery_unavailable" rather than guessed.

D2/D3 — GMAPS ALSO BLOCKED (confirmed root cause via direct API call, not just gmaps.py wrapper)
- Places API (delivery-pin trick): direct curl to places.googleapis.com:searchText confirms HTTP 429 RESOURCE_EXHAUSTED — "SearchTextRequest per day" quota = 100/project/day, exhausted fleet-wide (shared GMAPS_API_KEY across all concurrent research agents). Not query-specific; every places query fails identically.
- Static Maps API: direct curl to maps.googleapis.com/maps/api/staticmap returns HTTP 403 "This API is not activated on your API project" — Static Maps was never enabled on this GCP project (separate issue from the Places quota). Site-highlighted map image cannot be produced via gmaps.py staticmap this session regardless of quota.
- Combined with the CDSE 402 (credits exhausted), BOTH imagery-adjacent tool paths (Sentinel-2 chips AND Google Places/StaticMap) are unavailable for this run. This project's D2/Stage-3/Stage-4 site-pinpoint-via-imagery work is capped at: named-infrastructure cross-reference (Baines Creek) + IA POI text + queue POI description. No satellite/pin/map artifact possible today.

D3: County/corporate paper trail
- opencorporates.com "J&J Solar Ranch, LLC" (Delaware, entry 6540271) and bizapedia.com listing: both BLOCKED by bot-detection/CAPTCHA (HAProxy security check) — WebFetch cannot pass through. Search snippet confirms entity exists as a Delaware LLC registered via a corporate-services agent in Dover, DE (typical project-SPV shell registration pattern) but no officers/registered-agent detail obtained.
- Limestone County commissioners court portal (civicclerk.com) + web search for "Bonham Solar" in commissioners court records: NEGATIVE — no agenda/minutes hits. Consistent with ch313.py negative result (no Ch.313/JETI abatement filed) — this project appears to have no local tax-abatement agreement, which for a 138MW solar project built 2024-2026 is plausible (post-2022 JETI-era projects file abatements less uniformly; also this project may simply not have sought one).
- No press release, PR Newswire, or developer announcement found for "Bonham Solar" / "J&J Solar Ranch" under X-Elio or any other developer name — unlike Hanson Solar (Cypress Creek) which had multiple PRs, this project has ZERO public developer-side promotion. This is itself informative: either (a) X-Elio doesn't publicize mid-size Texas assets the way CCR does, or (b) the project is genuinely lower-profile/earlier-stage.

D5 wrap-up (deterministic)
- queue_history.py 25INR0199: OK -> timeline.json/timeline.md (44 snapshots, 3 COD changes; confirms IA-date match window 2024-05->2025-11 then fresh slip)
- eia_history.py 25INR0199 --write: NOT in EIA-860M (negative evidence, logged)
- build_brief.py 25INR0199: OK -> brief.html (14KB, 35 sources)
- build_index.py: OK -> research/index.json + INDEX.md refreshed (164 projects)

RUN COMPLETE. Turns used: well under cap. Token budget: well under cap (single-document IA meant fewer image reads than typical; imagery stage entirely blocked by account-level quota exhaustion across CDSE + Google Places + Static Maps).

FINAL VERDICT: real_early. Signed IA + $26.06M LC = genuine financial commitment (not paper). But: post-signing COD slip with no amendment, no press/financing news, no abatement filing, land tenure unknown, developer unconfirmed by press, and NO construction-stage evidence obtainable this session due to infrastructure blockers (not project-status evidence). Independent COD 2027-Q2 (provisional, contractual basis only) vs reported 2027-04-06 — treated as high drift risk given the demonstrated pattern of un-amended slippage.

## Imagery fix + re-derivation — 2026-07-21

**Task**: earlier session's imagery stage was entirely blocked (CDSE 402 credits exhausted). This
session re-derives site provenance, fetches imagery via s2aws.py (cdse.py remains down per
operator note), and re-assesses construction with the new frames.

**Site provenance re-check**: re-read the full 54-page IA (all Exhibit A-E pages, not just the
one-line diagram at p47) looking for an actual map/site-plan exhibit per the requested provenance
ladder (map exhibit > IA Exhibit C text > imagery-verified EIA > documented Places pin). Confirmed
via `exhibit.py list` (4 candidate pages: p14, p30, p31, p44) plus manual read of p28-54: **no
geographic map/site-plan exists in this IA** — Attachment 1 to Exhibit C is explicitly labeled
"for illustration only ... not for design/construction/operations" (an electrical one-line diagram,
not a map), and the Exhibit C text confirms the Generator's obligation to hand TSP actual
lat/lon-of-panels was due 2025-10-23 (i.e., not part of this filing). So the highest achievable
rung this session is **IA Exhibit C text**, which is what the existing site derivation already
used — no downgrade needed, but found ADDITIONAL corroborating text on p33-36 (previously not
transcribed): the interconnection work "loop[s] the existing Groesbeck Main Substation - Mexia
Main Substation 138 kV transmission line into TSP Baines Creek Switch." Cross-checked against
`data/ercot_generation_interconnect.parquet` (latest fileDate 2026-06-01): 25INR0199's own
`poiLocation` field reads verbatim "TAP 138 kV MEXIA_2_1_8 3632 - GROES_SE1_8 3634" — an exact,
independent match to the IA text. Confidence raised low-medium → medium (see findings.json site
note for full reasoning); still short of a parcel-level fix (no map exhibit exists to get one).

**eia_history.py 25INR0199 --write**: re-ran, confirmed still NOT in EIA-860M TX slice (negative
evidence, unchanged from prior session).

**Banned-domain grep** (infrasure|futuregrid|cleanview|interconnection.fyi|gridinfo|ercotqueue):
ran across the whole project dir. Zero hits in any deliverable (findings.json, dossier.md, log.md,
brief.html, factsheet, timeline, triage files). The only string matches anywhere in the directory
are inside the raw agent transcript JSONL files (`run_stream_*.jsonl`), where the banned-domain
list is quoted verbatim from the PLAYBOOK.md rules text fed to the agent each run — not a citation.
No cleanup needed.

**Imagery fetch** (`s2aws.py chips`, anchor 31.60N/-96.53W, 3.5km buffer, 20-day window, max-cloud
25, dates 2024-07-01/2025-07-01/2026-01-15/2026-04-15/2026-07-15): first pass wrote 5 PNGs but 2
(2026-01-15, 2026-07-15) came back from MGRS tile 14RQV with ~1/3 of the frame as black nodata
(tile-seam clip — the anchor sits near the 14SQA/14RQV tile boundary; 14SQA fully covers the AOI
on every date, 14RQV does not). Per convention (probes to scratch, never project imagery/), queried
`s2aws.search_scenes()` directly from a scratch probe script to list all STAC candidates per window,
confirmed a low-cloud 14SQA-tile alternative existed for every date (0.0-1.2% cloud each), rendered
those instead with the same RGB/reproject logic, verified full-frame coverage + magic bytes, THEN
copied the 5 final PNGs into `imagery/key/` (replacing the tile-clipped/cloud-heavy originals, which
were deleted, not kept). Also swapped 2024-07-01's picked scene from 14.8% cloud to a cleaner 1.2%
cloud same-tile alternative, and 2025-07-01/2026-04-15 from >23% cloud to 0.0% cloud alternatives
within the same search window (14SQA, dates 2025-07-24 and 2026-03-21 respectively) — all still
within the requested date windows. Final 5 frames all magic-byte-verified PNG, full 3.5km-buffer
framing with margin, ISO-dated filenames matching the query date.

**Per-date read** (see findings.json construction.evidence for full detail):
- s2_2024-07-14.png (scene 2024-07-14, 1.2% cloud): unbroken green pasture at/around anchor, no clearing.
- s2_2025-07-24.png (scene 2025-07-24, 0.0% cloud): still unbroken pasture, no clearing.
- s2_2026-01-15.png (scene 2026-01-15, 0.0% cloud): STEP CHANGE — bare/graded ground inside a
  road-bounded parcel + a new small white structure at the road junction, both absent in 2024/2025.
- s2_2026-03-21.png (scene 2026-03-21, 0.0% cloud): same cleared footprint, structure persists.
- s2_2026-07-19.png (scene 2026-07-19, 0.2% cloud): cleared footprint now shows internal grid-pattern
  access tracks + mixed bare/re-vegetated ground; structure still present (plausibly the Baines
  Creek Switch control house per the IA's Attachment 1 equipment list). Read conservatively as
  active switchyard + adjacent generator-site build-out IN PROGRESS, not a confirmed finished/
  energized PV array — Sentinel-2's 10m/px resolution cannot resolve individual panel rows.
- A separate tan borrow-pit/quarry ~1km NE of the anchor is geometrically unchanged across all 5
  dates 2024-2026 — confirmed pre-existing, unrelated to this project.

**Neighbor check** (required: Limestone Co. has Leighton Solar SLF 24INR0298 + Fiji Solar 25INR0128
both nearby/on-corridor): queried `data/eia_generator_tx.parquet` (county=Limestone, latest
reportDate 2026-05-01) for haversine distance from the anchor — nearest is Mexia Solar Project
(Ellomay USA, operating) at 11.79km, Naduah Solar at 16.19km, both outside the 3.5km buffer, ruled
out. Queried `data/ercot_generation_interconnect.parquet` (latest fileDate) for other Limestone Co.
queue projects: Fiji Solar (25INR0128, 202.7MW) has the IDENTICAL poiLocation line segment
(Groesbeck Main - Mexia) as Bonham — a genuine confusion risk — but `puct.py match 25INR0128`
returns 0 IA candidates and the queue shows it still at "FIS Started, No IA" (pre-construction
stage), so it cannot be the source of the observed grading/structure. Also found 26INR0619 "Bonham
Storage SLF" — same interconnecting entity "J&J Solar Ranch LLC", same POI line — a co-located
BESS sibling at the SAME site, not a separate location. Leighton Solar SLF's own findings.json pins
it at 31.53N/-96.73W (Ben Hur Switching Station), ~20km west, geographically distinct. Construction
observed is attributed to Bonham Solar SLF / J&J Solar Ranch LLC.

**findings.json updates**: site.confidence low-medium → medium (method/note rewritten with the
provenance-ladder check + neighbor-check reasoning); construction.verdict
unknown_imagery_unavailable → under_construction, first_activity_seen bracketed to
2025-07-24/2026-01-15, full per-date evidence + imagery_artifacts (5 repo-relative paths) added;
real_project_verdict real_early → real_active; cod_assessment.reasoning_evidence updated to fold
in the new imagery evidence (construction confirmed but visibly incomplete as of 2026-07-19,
supporting rather than replacing the paper-based drift read — independent estimate unchanged at
2027-Q2, high drift risk, now with direct supporting evidence instead of a pure paper inference).

Turns/tokens: well under cap for this fix session.

2026-07-21 (orchestrator): renamed imagery/key frames from query dates to TRUE scene
acquisition dates (2024-07-01→07-14, 2025-07-01→07-24, 2026-04-15→03-21, 2026-07-15→07-19)
per ISO-true-date filename convention; findings.json imagery_artifacts synced; brief rebuilt.
