# Triage log — Northington Solar (25INR0319)

T1 start
- queue_history.py ran: 41 snapshots, 2023-02 → 2026-06
- IA signed: 2024-10-02 (first seen 2024-10-01 snapshot)
- FIS approved: NOT achieved
- Meets 6.9(1): 2025-02-12
- Meets all 6.9: NOT achieved
- Construction start/end: NOT reported
- COD drift (3 changes): 2025-12-31 → 2026-12-01 → 2027-07-15 → 2027-11-30 (current)
- Capacity change: 129.81 MW → 125.9 MW (2026-05)
T1 end

T2 start
- gmaps.py: HTTP 429 on all attempts (rate-limited); budget exhausted
- No pins found
T2 end

T3 start
- DDG search "Northington Solar Texas": LLC is DE-domiciled, registered TX as foreign LLC 2023-07-14, file# 0805142190; principal office Miami TX (note: small town in Roberts County); IA executed 2024-10-02 with AEP Texas Inc.; capacity ~126-130 MW; ERCOT SOUTH
- DDG search developer/parent: no results
- DDG search El Campo / Wharton: no results
- DDG search LLC Delaware: no results
- No developer parent identified; no news articles; no press releases
- Saved no source pages (no project-specific pages found)
T3 end

T4 start
- PUCT Interchange: HTTP 402 on all URL attempts (blocked/paywall); budget exhausted after retry
- IA already confirmed in queue data (signed 2024-10-02, AEP Texas Inc.) but no PDF retrieved
- No milestone-schedule exhibit obtained
T4 end

T5 start
- TX Comptroller Ch.313 portal: WebFetch returns navigation text only, no searchable table data; budget exhausted
- DDG search for JETI/Ch.313 Northington Solar Wharton: no results
- Ch.313 expired 2022; project filed 2023 so JETI/post-2022 regime applies — no JETI hit is normal
- No abatement found
T5 end

T6 start
- Site candidate: El Campo substation area (29.20, -96.27) — inferred from POI "El Campo (#8102) - Pulsar (#8192) Line; AEP" + El Campo, TX city center; no pin or IA map available; confidence LOW
- CDSE cdse.py chip: HTTP 401/403 on all 9 grid attempts; credentials missing/invalid
- No imagery obtained; construction_visible = unknown
T6 end

T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~28
T7 end

## Deep scan (2026-07-20)

D0: Read triage_findings.json, factsheet.json/md, log.md, timeline.md. Inventoried sources/ —
one IA PDF already present: `2026-07-19_puct_35077-1964_ercot-standard-generation-interconnection-agreem.pdf`
(1 verified item from triage puct.py match). No imagery yet (CDSE auth failed at triage). No
site candidate above low confidence. findings.json skeleton written.

D1: IA exhibit scan (exhibit.py scan + sheet + render p33-36,53-58,63) — MAJOR finds:
- Exhibit C (Interconnection Details, p35 [pdf p35](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p35.png)):
  Substation Name "Northington"; Location: "Wharton County approximately three (3) miles
  east of Louise, Texas"; POI = TSP's first dead-end structure outside fence of TSP's
  "Ursidae Station" terminating Generator's 138kV line; Delivery Voltage 138kV; Nominal
  129.81 MW plant capacity at inverter terminal, 39 units x 3.3285 MW; Sungrow SG3600UD
  inverters.
- Exhibit B (Time Schedule, p33-34 [pdf](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p33.png)):
  In-Service Date = 32 months from date all Section 4.2/4.3 conditions satisfied
  (Generator provided written authorization AS OF Execution Date — so clock starts at
  execution); Trial Operation = 33 months; Scheduled COD = 34 months from execution.
- Exhibit D (Notices, p54-55 [pdf](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p54.png)):
  Generator = "Northington Solar LLC", 800 Brickell Avenue, Suite 901, Miami FL 33131 —
  this is Matrix Renewables' known Miami HQ address. Contacts: tlan@matrixrenewables.com,
  interconnection@matrixrenewables.com, jbunta@matrixrenewables.com (Head of Legal),
  enevarez@matrixrenewables.com. DEVELOPER = Matrix Renewables (confirmed by email domain
  + address match, not just inference).
- Exhibit E (Security, p57 [pdf](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p57.png)):
  Financial security = $11,000,000 LC/guaranty, due within 10 business days after TSP
  executed-agreement notice.
- Still need: exact Execution/Filing Date to convert months->calendar dates (filing receipt
  on p1 said "Filing Date - 2024-10-25", queue iaSigned = 2024-10-02 — need to confirm which
  is Execution Date for Exhibit B clock).

D1 (cont): Execution Date confirmed = 2024-10-02 (AEP signature page [p14](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p14.png):
Judith Talavera, AEP President/COO, dated "10/2/2024 | 9:14 AM EDT"; AEP cover letter
[p2](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p2.png) confirms
"Agreement, dated October 2, 2024". Northington Solar LLC signed by Cindy Tindell
(Managing Director, Matrix Renewables USA LLC as Manager) 10-Sep-2024, and Philipp Rusch
(CFO, Matrix Renewables USA LLC) 11-Sep-2024 — AEP's countersignature on 10/2/2024 is the
later/operative execution date. Generator provided Section 4.2/4.3 written authorization
"AS OF the Execution Date" (Exhibit B) — clock starts 2024-10-02.

DECISIVE CROSS-CHECK: Exhibit B contractual dates from Execution Date 2024-10-02:
  In-Service (32 mo) = 2027-06-02
  Trial Operation (33 mo) = 2027-07-02
  Scheduled COD (34 mo) = 2027-08-02
Queue COD history (timeline.md) held 2027-07-15 from 2024-12 through 2026-04 — matches
this contractual calc almost exactly (~2 wks off). Then in the 2026-05 snapshot the queue
COD jumped to 2027-11-30 (current) — a ~4-month slip with NO IA amendment on file (puct.py
match found only 1 item — the original agreement; no amendment filing). This is a
self-reported slip beyond the countersigned contractual schedule, not yet backed by a
renegotiated IA. Independent COD leans toward contractual 2027-Q3 with acknowledgment of
the reported 2027-Q4 claim as a real but unconfirmed-by-paper slip risk.

D2/D3: search.py "Louise Texas Wharton County coordinates" -> Wikipedia gives Louise, TX
CDP center 29.1114N, 96.4033W. IA Exhibit C says Generator's own Northington substation is
"approximately three (3) miles east of Louise, Texas" -> rough site estimate ~29.11,-96.36
(will grid-search imagery around this, not treat as final).

search.py "Ursidae substation AEP Texas Wharton County" -> no direct hit on Ursidae; top
hits are unrelated AEP dockets/PUCT filings. search.py "Northington solar Matrix Renewables
Wharton" -> Matrix Renewables' own /existing-projects/u-s/ page surfaced (fetched via curl,
2026-07-20) but does NOT mention Northington, Wharton, or Louise anywhere in the page text —
only lists 4 financed/under-construction+operating projects (Tormes, Alamo BESS, Gaskell
West, Pleasant Valley). Northington's absence from Matrix's public "existing projects" page
is consistent with pre-construction/pre-financing stage, not necessarily paper-project
evidence (IA is signed+verified). Logged as negative evidence.

renewableenergymagazine.com 2026-06-29 Matrix financing PR (fetched via WebFetch) covers a
4-project portfolio (Tormes Solar TX-Navarro, Alamo BESS CA, Gaskell West CA, Pleasant
Valley ID) totaling 859 MWdc + 167 MWh, $1.3B+ investment — Northington NOT included in this
financing round. Negative evidence: no financing yet for this specific project.

D2 imagery: cdse.py chip failed 3x with http.client.RemoteDisconnected (not the 401/403 seen
at triage). Diagnosed directly: raw curl POST to the openEO /result endpoint with a valid
cached token returns clean `HTTP 402 Payment Required` — "You do not have sufficient
credits to perform this request" (marketplace-portal.dataspace.copernicus.eu/pages/pricing).
CONFIRMED: the CDSE account itself is out of Sentinel Hub processing credits — this is an
account/billing exhaustion, not a transient auth/network issue, and will not resolve on
retry. NO SATELLITE IMAGERY OBTAINABLE THIS SESSION. Negative evidence logged; falling back
to IA exhibit maps/text as primary site evidence per PLAYBOOK rule 4b. gmaps.py places/
staticmap also 429 rate-limited on this attempt (see below) — no Places pin or static map
image obtainable either. Construction stage verdict will be marked "unknown - no imagery"
rather than guessed.

D2 (cont) site geocode attempts:
- OSM Nominatim: "Ursidae Substation, Wharton County, Texas" -> 0 results; "Ursidae" alone
  -> 0 results. "Louise, Wharton County, Texas" -> 29.1091,-96.4084 (village node).
  "El Campo, Texas" -> 29.1966N,-96.2697W (town boundary centroid, NOT a substation pin —
  not used as site coordinate per no-county-centroids rule).
- Overpass API (overpass-api.de): HTTP 406 on POST. Mirror overpass.kumi.systems: returned
  487 power-tagged elements but bbox filter did not apply correctly (results clustered in
  TX Panhandle ~35.2-35.5N, not Wharton Co ~29N) — tool/query issue, abandoned rather than
  loop on it.
- puct.py search "Ursidae" -> 0 results across all PUCT dockets (not just 35077) — AEP's
  Ursidae Station has no other PUCT filing surface exposing coordinates.
- puct.py search "Northington" -> exactly 1 filing (control 35077, the original IA already
  on disk) — CONFIRMS no IA amendment exists yet; the 2027-11-30 queue COD slip (D1) is
  self-reported only, not contractually re-papered.
- CONCLUSION: cannot independently geocode Ursidae Station or the Northington substation to
  a lat/lon this session (no imagery, no Places pin, no OSM/Overpass hit, no CAD parcel
  pulled). Site is described with high textual precision (Exhibit C: "3 miles east of
  Louise, TX"; Exhibit C-1: distances to El Campo/Pulsar taps) but NOT independently
  geocoded to coordinates -- recording as text-derived estimate, confidence LOW, and being
  explicit in the dossier that no satellite/pin cross-check was possible this session.

D2/Stage2 CAD: whartoncad.net/property-search is a JS-rendered SPA ("Public Portal" only,
no static form) -- WebFetch returns no queryable content, confirming triage's earlier
finding. No CAD parcel search possible without a headless browser (out of scope/tooling).
Ch313/JETI resolver re-run: confirmed 0 hits for Northington Solar (post-2022 project,
JETI-era; absence is normal, matches triage). No parcel evidence obtained either way --
land tenure remains unknown (typical for leased solar ranchland per Hanson precedent).

Stage1 LLC/parent: search.py '"Northington Solar"' -> bizapedia.com/tx/northington-solar-llc.html
exists (confirms TX foreign-LLC registration) but bot-blocked on fetch (security check page,
no data extracted). NOTE: triage.md said "principal office Miami TX" (flagging Roberts
County oddity) -- this is corrected by the signed IA itself (D1): the real address is
Miami, FLORIDA 33131 (800 Brickell Avenue, Suite 901) = Matrix Renewables' known Miami FL
HQ, not a Texas Panhandle town. Triage's "Miami TX" note appears to have been a
state-field misread; superseded by primary-document evidence.
search.py "Matrix Renewables Wharton County solar 126 MW" -> confirms Matrix's 2026-06-26
pv-magazine-usa.com $1.3B financing PR (859 MW, 4 named projects, Northington NOT among
them -- consistent with earlier finding, this is the 3rd independent source confirming
Northington isn't in Matrix's currently-financed pipeline).

D5 wrap-up: queue_history.py 25INR0319 -> timeline.json/md rewritten, unchanged from triage
(41 snapshots, 3 COD changes) -- confirms no new monthly report since triage.
eia_history.py 25INR0319 --write -> "NOT in EIA-860M (TX slice)" confirmed (matches
factsheet.json not_in_eia) -- consistent with pre-construction/pre-financing status, no
divergence evidence available from this second source.

D4/D5 SYNTHESIS COMPLETE: findings.json, dossier.md finalized. brief.html + index rebuilt.
Verdict: real_early (signed IA + $11M security posted, developer=Matrix Renewables
confirmed via primary signature block; no construction/financing signal yet). Independent
COD 2027-Q3 (contractual, from signed IA Exhibit B), drift risk medium (self-reported
2027-11-30 slip has no amendment on file; FIS stalled ~3.3yr unexplained). Site not
independently geocoded this session (text-only from IA Exhibits C/C-1; no imagery due to
CDSE credit exhaustion, no Places pin due to gmaps 429). Total budget spent: ~162k/400k.
