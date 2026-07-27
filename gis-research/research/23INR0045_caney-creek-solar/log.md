# Triage log — Caney Creek Solar (23INR0045)

T1 start

## T1 — Queue history

queue_history.py: 65 snapshots (2021-02-01 → 2026-06-01), 3 COD changes.

COD drift:
- 2023-06-01 held 2021-02 → 2022-11 (original COD)
- 2024-06-01 held 2022-12 → 2023-04
- 2025-05-15 held 2023-05 → 2024-12
- 2027-06-21 held 2025-01 → 2026-06 (current)

Milestones achieved:
- Screening started: 2020-09-25
- Screening complete: 2020-12-16
- FIS requested: 2021-02-22
- IA signed: 2021-12-29
- Meets 6.9(1): 2021-12-13

Not achieved: FIS approved, Meets all 6.9, construction start/end, approved for energization/sync/COD.

Capacity: 102.6 MW → 121.97 MW (2021-03) → 121.04 MW (2025-10, current)

Key signals: IA signed Dec 2021 — project cleared first financing gate. COD has slipped 4 years total (2023→2027). No construction milestone in the queue data. FIS approval missing despite IA signed (unusual gap to note).

T2 start

## T2 — Delivery pins

gmaps.py: HTTP 429 (rate-limited) on all attempts — 1 initial + 1 retry. No pins found.
Result: 0 pins.

T3 start

## T3 — Web sweep

DDG search: "Caney Creek Solar Texas news" → multiple hits.

Developer confirmed: HEP Caney Creek Solar LLC / HEP Aquamarine Holdings LLC (Louisville, CO; TX foreign LLC registered 2020-09-11).
Financing: secured from Solareit (Virginia-based real estate company) per local opposition site.
Location detail: east of FM 47, south of I-20, Van Zandt County — 600+ acres.
Easements: six property owners leased easements to HEP Caney Creek Solar LLC for grid interconnection.
PUCT filing: Jan 2022 IA filing by Rayburn Country Electric Cooperative (control number 35077).
Local opposition group: savevzcounty.org tracks the project as "Active," build start Summer 2026.
Third-party aggregators (interconnection.fyi, ercotqueue.com, cleanview.co) confirm 121 MW, Jun 2027.

Saved: sources/savevzcounty_caney_creek.md

T4 start

## T4 — PUCT Interchange

Control number 35077 surfaced in T3 (Rayburn Country Electric Cooperative IA filing, Jan 2022).
All PUCT Interchange URL patterns returned HTTP 402 — portal requires session auth / subscription.
IA existence confirmed via T3 web sweep (queue milestone also shows iaSigned = 2021-12-29).
PDF content not retrievable; milestone schedule exhibit not obtained.

Result: IA found (confirmed via queue data + T3 reference), but PDF inaccessible during triage.
ia_found = true (queue milestone), PDF content = unavailable.

T5 start

## T5 — Abatements

TX Comptroller Ch.313 portal: dynamic site, not fetchable as static HTML — no table returned.
JETI registry: DDG search returned no results for Caney Creek Solar / HEP Caney Creek.
No Ch.313 application found; no JETI application found.
Normal for post-2022 project (Ch.313 expired Sep 2022; JETI launched 2023, filings sparse).

Result: abatement_found = false.

T6 start

## T6 — Imagery

Site candidate derived from T3: east of FM 47, south of I-20, Van Zandt County TX (~32.44N, -95.82W, medium confidence).
cdse.py: HTTP 401 Unauthorized on all chip requests — CDSE credentials not available in ~/.config/gis-research.env for this session.
No imagery obtained; contact sheet not produced.

Result: construction_visible = false (no imagery), construction verdict = unknown.

T7 start

## T7 — Write and stop

Wrote triage_findings.json and triage.md.
Turns used: ~28. STOP.

---

# DEEP SCAN — 2026-07-20

## D0 — checkpoint zero

Read triage_findings.json, log.md, factsheet.json, timeline.md. IA PDF already on disk:
sources/2026-07-19_puct_35077-1353_solar-generation-interconnection-agreement-betwe.pdf
(CONFIRMED — INR not literally in text but party name exact match; 47 pages, executed
2021-12-24/12-29). Wrote findings.json skeleton (all schema keys null).

## D1 — IA schedule extraction

exhibit.py scan: 2 map/exhibit candidate pages (p13, p35) — both are body-text false
positives (DocuSign boilerplate scan), NOT parcel/boundary maps. Confirmed by reading full
text of all Exhibit pages directly (pypdf extract_text, 47 pages) — **no parcel/boundary
map exists in this IA**; Exhibit C is text-only interconnection details, Attachment 1 is a
one-line electrical diagram (Ray Raymond Switching Station), not a site/parcel map.
site.map_artifacts stays empty — legitimately no map artifact in this document.

**Original IA (PUCT 35077-1353, executed 2021-12-24/12-29, between Rayburn Country
Electric Cooperative and HEP Caney Creek Solar LLC):**
- Exhibit B (Time Schedule, p28-29): Notice-to-proceed 2021-11-01; In-Service Date
  **2023-01-20**; Scheduled Trial Operation **2023-02-03**; Scheduled Commercial
  Operation Date **2023-06-01**. This matches the queue's FIRST reported COD
  (2023-06-01, held 2021-02→2022-11 per timeline.md) exactly — the original IA schedule
  IS the original queue COD claim, confirming the queue reflects contractual dates at
  that point.
- Exhibit C (Interconnection Details, p30): Name "HEP CANEY CREEK SOLAR, LLC". POI:
  "located approximately 8.3 miles west of Canton, TX on County Road 2120 in Van Zandt
  County, Texas. The proposed facility substation will be connected to a new substation
  tapping the Glen Pine-Explorer 138kV transmission line via a 0.1 mile transmission
  line." Delivery voltage 138kV. 33 inverters, SMA SC4200UP-US, 4.2 MVA each = 121.97 MW
  (rated capacity at signing, matches 2021-03→2025-09 queue MW).
- Exhibit E (Security): $50,000 posted 2021-12-13 (NTP) → $1,450,000 cash by 2022-01-14
  → $3,000,000 by 2022-04-01 → $4,277,047 by 2022-06-01 (final tier). Real money posted —
  strong reality signal.

**NO AMENDMENT ON FILE.** puct.py match (INR-join + name-key) returns only the single
original 2022-01-03 filing (35077-1353). Manually walked ALL 35 Rayburn-party filings in
docket 35077 (puct.py filings 35077 --party Rayburn) — many amendments exist for OTHER
Rayburn-interconnected projects (BT Signal Ranch has 6 amendments, Sowers/Tanzanite/Amador
etc.) but ZERO amendment filings mention Caney Creek or HEP. Also ran
`puct.py filings 35077 --match Caney` / `--match HEP` / `--from 2022-01-01 --to
2026-07-01` grepped for "caney" — only the single original hit each time. Misfetched
35077-1453 on a lead (turned out to be BT Sowers Storage's 1st Amendment, unrelated) —
deleted, logged here as negative evidence, not kept in sources/.

**This is decisive negative evidence**: the queue COD has slipped 3 times since 2023
(2023-06→2024-06→2025-05→2027-06, per timeline.md/triage) but the LEGALLY BINDING IA
schedule on file with the PUCT still says Commercial Operation **2023-06-01** — three
years in the past. Either (a) an amendment exists but was never filed with PUCT
(inconsistent with the Subst. R. 25.195(e) filing requirement — Rayburn filed 6+
amendments for its OTHER projects, so the absence for Caney Creek is a real signal, not
a tooling gap), or (b) the project's queue COD claims 2024/2025/2027 were never backed by
a renegotiated IA at all — i.e., the developer/TSP relationship on the ORIGINAL
schedule/security may be stale or lapsed. Recorded as the single most decisive finding.

## D2 — Site + imagery

POI text gives an independent, precise siting cross-check vs T3's vague "east of FM 47,
south of I-20" web description: **8.3 mi west of Canton, TX on CR 2120, tapping the Glen
Pine-Explorer 138kV line** (matches identity-packet POI "Tap 138kV 6829 Glen Pine - 6833
Explorer" exactly — CONFIRMED same project, same line).

Geocoded via OSM Nominatim (curl, free/no-key): CR 2120 way centroid = 32.5658, -95.9953;
Canton TX centroid = 32.5386, -95.8618. Distance/bearing (~8.0 mi, west) matches IA's
"8.3 miles west of Canton... on County Road 2120" closely. site.lat/lon set to
32.5658/-95.9953, method=IA POI text + geocode, confidence=medium (no imagery/parcel/pin
cross-check yet).

Google Places (gmaps.py places): HTTP 429 again this session (same failure as triage T2) —
tried "Caney Creek Solar", "HEP Caney Creek Solar", "Caney Creek Solar construction Van
Zandt" — 0 pins, all rate-limited. Logged as negative evidence (2nd consecutive session
with this failure).

CDSE imagery: persistent `RemoteDisconnected` on openEO `/result` sync endpoint across
6+ retries with backoff (10s/30s/45s x4) over ~5 min. Root cause: 5 OTHER deep-scan
agents running concurrently in this container (run_batch.py --concurrency 4 + solo
run_agent.py runs for 26INR0130/26INR0380/22INR0220/23INR0056), all hitting the same
shared CDSE openEO endpoint — matches the known "23% of deep scans imagery-less from
identity-endpoint contention" issue in CLAUDE.md, but manifesting as a result-endpoint
RemoteDisconnected rather than a 403 this time. Token cache at /tmp/.cdse_token_cache.json
exists (2437 bytes) so auth itself is not the blocker. No imagery obtained this session.
Proceeding to D3 gap-fill per playbook while imagery is unavailable; will retry CDSE once
more before D4 synthesis if turns/budget allow.

## D3 — Gap-fill

ch313.py resolve 23INR0045 (also tried --name/--county variants, same output — those
flags aren't implemented in this build): **0 Ch.313 agreements, 0 JETI applications**
matching Caney Creek/Van Zandt. Confirms triage T5 — no tax abatement filed. Consistent
with pipeline signing Dec 2021/schedule targeting 2023 COD: Ch.313 sunset Sep 2022,
project may simply not have pursued one (small-ish 121 MW project, or landowner-driven
deal without incentive).

spv.py resolve 23INR0045: only candidate = the same puct-index IA filing already on disk
(no EIA-860M hit — confirms factsheet.json `eia.status: not_in_eia`, will double check
with eia_history.py in D5).

Van Zandt CAD (esearch.vzcad.org): TLS handshake failure (`SSL routines: unexpected eof
while reading`) — portal unreachable from this container (likely blocks non-browser
clients/lacks matching cipher suite). Could not search parcels by owner name (HEP Caney
Creek Solar / HEP Aquamarine). Logged as negative evidence — same class of failure as
triage T5's Ch.313-portal-not-fetchable note.

TX Comptroller taxable-entity search (mycpa.cpa.state.tx.us/coa/): HTTP 302 redirect —
dynamic ASP.NET form, not fetchable as static HTML (same constraint noted in Hanson
dossier). No LLC officer/registered-agent detail obtained.

Developer confirmed independently: **hep North America** (us.hep.global) — "We develop,
build and operate solar farms across the United States and Canada", part of German-listed
hep global GmbH (renewables.digital profile: sources/... not saved, low-value directory
listing). IA IS signed by Ilan Caplan, "Authorized Signatory" @hep.global email domain —
this is a PRIMARY document match to the developer's own corporate identity, not just a
secondary-source claim. hep's own solar-farms/projects pages (us.hep.global/solar-farms/,
/projects/ 404) do NOT list "Caney Creek" or "Van Zandt" by name — the project isn't in
their public portfolio listing (could be omitted for pre-construction projects, or simply
an incomplete portfolio page; not strong evidence either way).

Refetched savevzcounty.org/current-projects directly (not cached DDG snippet) — saved as
sources/2026-07-20_savevzcounty_current-projects.html. Current text: "Caney Creek Solar
is planned for the area East of FM 47 and South of I20 and is a 600+ acre project. This
project is now planned for completion June 2027." Est. build start Summer 2026. This is
the SAME estimate as triage T3 (unchanged in 2 days) — the opposition group's own
completion estimate (June 2027) matches the queue's current reported COD (2027-06-21)
almost exactly, i.e. the community group is tracking the same claim, not independently
corroborating it.

NBC 5 DFW (nbcdfw.com) news article "Van Zandt County Community Group Fights Future
'Solar Farm'" confirmed to exist (title + local-news byline visible) but body text is
JS-rendered (React shell) and not extractable via curl — could not read article content.
Logged as a source that exists but wasn't fully retrievable this session.

Google Places (gmaps.py places) retried a 4th/5th time across ~15 min elapsed — still
HTTP 429. Confirmed persistent rate-limit issue this session, not a transient blip.

CDSE retry: after ~6 min, still RemoteDisconnected. Confirmed persistent for this
session's imagery access — see D2 note above. Deferred to end of session for one final
retry attempt.

## D4 — deterministic wrap-up (partial) + final CDSE attempt

queue_history.py 23INR0045: refreshed timeline.json/timeline.md, unchanged from triage
(65 snapshots, 3 COD changes).

eia_history.py 23INR0045 --write: confirms NOT in EIA-860M TX slice. Negative evidence
logged; consistent with factsheet.json and spv.py.

Final CDSE attempt (pgrep showed 18 concurrent run_agent/run_batch processes at this
point — MORE contended than earlier, not less): still RemoteDisconnected within 60s.
Tried gmaps.py staticmap as an alternative site-map image (doesn't share the Places
429): got a clean HTTP 403 — "Maps Static API" is not enabled for this project's API
key (permanent config gap, not contention). **Verdict: zero imagery evidence obtainable
this session by any available tool.** This is a tooling-availability failure, not a
finding about the project — recorded honestly in the dossier's "could not determine"
section rather than guessed at.
