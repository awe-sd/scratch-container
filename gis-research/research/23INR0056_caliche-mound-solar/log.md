# Research Log — Caliche Mound Solar (23INR0056)

Researched: 2026-07-19  
Researcher: agent  
County: Deaf Smith, TX  
Capacity: 406.6 MW solar PV  
POI: tap 345kV 23906 AJSwope – 23910 Windmill  
CDR Zone: PANHANDLE  
Reported COD: 2027-10-26

---

## Stage 1 — LLC / Parent chain

**Triage carry-forward:** SPV = Caliche Mound Solar, LLC (confirmed via PUCT #35077 IA filing). Developer "Tierra Blanco Solar LLC" appeared on aggregators during triage but was not independently confirmed.

**Deep scan attempts — all blocked:**
- TX Comptroller COA (mycpa.cpa.state.tx.us) → redirects to login-gated comptroller.texas.gov; no programmatic entity lookup possible
- TX SOS SOSDirect (direct.sos.state.tx.us) → requires paid $1/search subscriber account
- SEC EDGAR EFTS full-text search (efts.sec.gov) → HTTP 403 on ~40 separate queries; this IP/environment is uniformly blocked
- SEC EDGAR company browse (sec.gov/cgi-bin/browse-edgar) → HTTP 403
- FERC eLibrary → returns empty page with just "eLibrary" text; no results extractable via WebFetch
- PUCT Interchange (interchange.puc.texas.gov) → HTTP 402 Payment Required on all queries
- OpenCorporates → CAPTCHA wall
- Bizapedia → CAPTCHA wall
- Corporate Wiki → HTTP 403

**Result:** Developer chain NOT verified this session. Prior triage finding (Tierra Blanco Solar LLC) stands as best available but unconfirmed.

---

## Stage 2 — PUCT Interconnection Agreement

PUCT Control #35077 is an Oncor IA filing dated 2023-10-26, confirming IA signed 2023-10-12. PDF contents unread — PUCT Interchange portal returned HTTP 402 on all programmatic queries. PDF would contain exact POI coordinates, milestone schedule, and potentially counterparty/developer identity.

**Action:** Pull PUCT #35077 PDF directly via authenticated browser or PUCT bulk download tool.

---

## Stage 3 — Site candidate / imagery

Not completed. POI substations (AJSwope 23906, Windmill 23910) not geolocated this session. Without site coordinates, Sentinel-2 imagery sweep was skipped.

---

## Stage 4 — Abatement

- Chapter 313: Portal not accessible.
- JETI: Not searched — session budget exhausted before this stage.

**Action:** Search JETI registry at Texas Comptroller for post-2022 Deaf Smith County application by Caliche Mound Solar or Tierra Blanco Solar.

---

## Stage 5 — News / Press

No press releases, PPA announcements, or developer announcements found on any accessible public source:
- Law360: zero results
- CleanTechnica: zero results  
- PV-Tech: zero results
- GlobeNewswire: zero results
- Local TX papers (thecastrocountynews.com): no relevant articles
- TCEQ search: no results for "caliche mound solar"

This is consistent with a pre-announcement project — likely still in development/financing phase with no public press.

---

## COD Assessment

Reported COD: 2027-10-26. IA signed 2023-10-12. Meets 6.9(1): 2025-02-12. Meets all 6.9: NOT YET. The project has slipped 5 times, accumulating ~4.5 years of delay since its original 2020 COD claim. The 2027 date is plausible given the IA milestone, but slip history indicates meaningful probability of further delay.

---

## Summary

Deep scan was largely unsuccessful due to infrastructure access barriers:
1. SEC EDGAR EFTS blocked (HTTP 403) — probably IP/bot filter
2. PUCT Interchange blocked (HTTP 402) — subscription required
3. TX SOS/Comptroller entity databases — require paid accounts or interactive sessions

**Best next steps:**
1. Pull PUCT #35077 IA PDF (needs authenticated access or curl with correct auth)
2. TX SOS entity lookup for Caliche Mound Solar LLC (requires SOSDirect account or TX SOS staff contact)
3. Geolocate AJSwope/Windmill 345kV substations → run Sentinel-2 sweep
4. Search JETI registry for Deaf Smith County / Caliche Mound Solar

---

## RE-RUN 2026-07-20 (user-ordered, 1M token budget, per sources/REFRESH_DIRECTIVE.md)

### D0/D1 — IA PDF read (rung-0 CONFIRMED, INR verified in text)

IA already on disk: `sources/2026-07-19_puct_35077-1688_interconnection-agreement-between-oncor-electric.pdf`
(47pp, PUCT docket 35077 item 1688, filed 2023-10-26). `exhibit.py scan` flagged p14/p38 as
map candidates but they're DocuSign section headers, not maps — this IA has **no** boundary/
parcel exhibit page (Exhibit C is text-only interconnection details + one-line diagram, no
site plan). Extracted full text via pypdf (`/tmp/ia_full.txt`, not saved to sources — derived,
not a primary artifact) and grepped for schedule/POI/security terms.

**CRITICAL FINDING — signed IA counterparty is NOT "Caliche Mound Solar, LLC":**
p6 (page 90 of raw text): *"...between Oncor Electric Delivery Company LLC...and **CIG DS1,
LLC** ('Generator')..."* Signature page, notice/billing addresses, and EFT wire instructions
(pp37-43) all name **CIG DS1, LLC**, Attn: Joshua Leu, 2600 S. Waverly Rd, Lansing, MI 48911,
contacts @cigcap.com. Only the PUCT filing *cover letter* (p2, written by Oncor's regulatory
staff) uses "Caliche Mound Solar, LLC" — likely the queue/project alias Oncor used for the
filing, or an intermediate name later formalized as CIG DS1, LLC. Exhibit "C" ITEM 1 confirms
the project's operating name: "1. Name: **Caliche Mound Solar**" (p31/raw line 888) — so this
IS the same project; the LEGAL entity is CIG DS1, LLC, not a separate "Caliche Mound Solar,
LLC" SPV. **This overturns the triage/factsheet SPV field** (`spv.candidates[0].entity =
"Caliche Mound Solar, LLC"` — that was reading only the cover-letter alias, not the executed
signature page).

**Parent/developer identified via search.py:** cigcap.com = "CIG Companies" / "CIG Capital" /
"CIG Renewables" / "CIG Solar." Their own solar-portfolio page
(https://www.cigcap.com/cig-solar-portfolio/, fetched via WebFetch 2026-07-20) lists **"CIG
DS1 — 516 MW — Northern Texas — 2025 COD — BBB-rated green bond"** among six DS-numbered
Texas solar projects (DS1 516MW, DS2 502MW, MDS3 900MW, MDS4 1.2GW, DS5 210MW, DS6 214MW) —
"exact location...not displayed based on mutual non-disclosures." 516 MW vs the queue's 406.6
MW / IA Exhibit C's "408.21 MW at generator terminals" (433.35 MVA gross, 107× Power
Electronics HEM FS4200M inverters) is a plausible DC:AC nameplate variance, not a mismatch —
CIG's own marketing rounds to nameplate/DC-ish figures.

Third-party corroboration: power-technology.com "CIG DS1 Solar PV Park" profile (WebFetch
2026-07-20) — 506 MW, Texas, "permitting stage" (as of Oct 2024 update), owner CIG Capital
100%, **PPA with Danfoss, 75 MW / 12-year term**, expected 1,073,732 MWh/yr. No coordinates/
county given. renewablesnow.com headline ("CIG to pour $870m into utility-scale solar in
Texas") returned HTTP 403 — logged negative, could not read body.

**Not found:** no page on cigcap.com or any press source ties "CIG DS1" explicitly to Deaf
Smith County or "Caliche Mound" by name — the DS1↔Caliche-Mound link rests entirely on the
IA document (same INR, same project name in Exhibit C, same MW class) plus the fact that this
is the ONLY IA on file for 23INR0056. Treat as CONFIRMED via IA primary-source logic (exact
INR match + exact project-name match in Exhibit C), not via CIG's own disclosures (which
deliberately omit location "per mutual NDA").

### D1 — Milestone schedule (Exhibit B) + Financial security (Exhibit E)

Exhibit "B" Time Schedule (original IA, raw lines 822-882):
- Notice to proceed w/ design/procurement + security: **2023-10-10**
- Notice to commence construction + security: **2024-04-17**
- **In-Service Date: 2025-04-17**
- **Scheduled Trial Operation Date: 2025-04-28**
- **Scheduled Commercial Operation Date: 2025-08-28**
- Generator to provide lat/lon of all solar panel units to TSP: 2024-10-17
- No amendments found on disk or in PUCT docket join table (only 1 join item, `factsheet.ia.join_items=1`) — this appears to be the ONLY IA filing, unamended.

**This is decisive negative evidence for drift**: the *signed, unamended* IA schedule commits
to COD 2025-08-28 — over 2 years before the queue's *current* reported claim of 2027-10-26.
The queue COD has clearly drifted far past the contractual schedule with NO corresponding IA
amendment on file (compare Hanson Solar, where every queue slip was mirrored by a filed
Amendment). Either (a) an amendment exists but was never filed with PUCT / not yet indexed by
inr_harvest.py, or (b) the project slipped without updating the binding schedule, which per
Article 4/10.6 would ordinarily trigger default provisions — TSP likely granted informal
extensions or the Generator is technically in schedule breach. Could not determine which;
logging both as open items.

Exhibit "E" Security Arrangement (raw lines 1470-1539):
- Irrevocable Standby Letter of Credit, effective on/before 2023-10-10
- **Amount: $12,995,303**
- Bank must hold A-/A3 rating; held through 5 business days after Commercial Operation confirmed to ERCOT, or 90 days after termination

### D1 — POI confirmed precisely

Exhibit "C" (raw lines 886-1090): POI = **Mule Deer Switch**, in Deaf Smith County, TX, on
TSP's AJ Swope – Windmill 345kV line (matches queue POI text exactly). *"The Mule Deer Switch
will be located on CO Road 8, 2.6 miles east of US Highway 60."* This is a NEW substation
being built for this interconnection (not an existing switch) — Exhibit C describes new
switchyard construction (air-break switches, relay panels, dead-end structures) at Mule Deer
Switch, plus modifications to the existing AJ Swope and Windmill switches. This is a
precise, low-ambiguity site anchor: CO Rd 8 + 2.6 mi east of US-60, Deaf Smith County.

No boundary/parcel/array-layout map exhibit exists in this IA (only a schematic one-line
diagram for switchyard wiring, not geospatial) — `site.map_artifacts` will be empty for this
project; site fix rests on the POI text description + imagery search around Mule Deer Switch.

### D2 — Site geolocation (pending): search CO Road 8 × US-60 intersection, Deaf Smith Co, +2.6mi east, then imagery.

### County-records web sweep (search.py + WebFetch, 2026-07-20)

- abc7amarillo.com "Deaf Smith County commissioners approve $500 million tax abatement for
  solar farms" (2024-01-23 commissioners court vote): approved **Mule Deer Solar** and **Tiera
  Blanco Solar** (sic — county's own article misspells "Tierra Blanco"), both developed by
  **Chermac Energy**, located near County Road BB, combined $500M abatement value. NEITHER
  "Caliche Mound" NOR "CIG" NOR "DS1" appears in this article. **"Mule Deer Solar" as a
  project name is a striking coincidence with "Mule Deer Switch" as this project's POI** —
  investigate whether "Mule Deer Solar" (Chermac Energy) is THIS project under a different
  developer/name, or a distinct neighboring project sharing the same switch name by
  coincidence (Deaf Smith has multiple large solar queue entries). Logged as an open thread,
  not yet resolved — do not conflate without a corroborating INR/LLC-name match.
- abc7amarillo.com companion article "Deaf Smith County Commission clears way for hydrogen
  plant, wind farm, solar farm — Intersect Power" (separate article, Intersect Power project,
  not reviewed in detail — different developer, logged for completeness only).
- txses.org Deaf Smith county resource page — not yet reviewed.
- search.py "\"CIG DS1\" Deaf Smith OR \"Caliche Mound\"" — zero relevant hits (Dark Souls
  wiki results, one Facebook video about caliche ROAD BASE unrelated to solar). Negative.
- Original triage's "Tierra Blanco Solar LLC" developer attribution (from an aggregator, per
  triage_findings.json) may actually be **Chermac Energy's "Tiera Blanco Solar"** per this
  abc7amarillo article — i.e., the triage aggregator's developer guess may have been reading
  the SAME public reporting this session found, but for the WRONG one of two adjacent Deaf
  Smith projects (Mule Deer Solar / Tiera Blanco Solar, both Chermac). Given this project's
  own signed IA names CIG DS1, LLC as Generator and its POI is Mule Deer Switch, "Tierra
  Blanco Solar LLC" as this project's developer is very likely a triage-stage misattribution
  — DO NOT carry forward "Tierra Blanco" as this project's developer in the final dossier.

### CIG Companies developer corroboration (search.py + WebFetch + curl)

- cigcap.com blocks direct curl (HTTP 406) but a follow-up `curl -sL -A "Mozilla/5.0"` with a
  full browser UA succeeded — saved `sources/2026-07-20_cigcap_solar-portfolio.html`. Verbatim
  quote: *"CIG DS1 — DS1 P1 is a 2025 COD 516 MW solar project located in Northern Texas. It
  has a projected stable valuation of $1.345 billion (50% ITC)...blend of merchant and A rated
  VPPAs. The green bond has an investment grade rating of BBB."* Same page lists a related
  "CIG DS2 / DS1 P2" (502 MW, 2025 NTP, Northern Texas) as a DIFFERENT, second project — logged
  to avoid conflating the two.
- power-technology.com "CIG DS1 Solar PV Park" profile (WebFetch only — direct curl 403'd, not
  independently re-fetchable/saved to sources/ as a raw artifact, cite via URL only): 506 MW,
  Texas, "permitting stage" as of Oct 2024, owner CIG Capital 100%, PPA with **Danfoss, 75 MW /
  12-year term**, ~1,073,732 MWh/yr expected. No county/coordinates disclosed.
- renewablesnow.com "CIG to pour $870m into utility-scale solar in Texas" — HTTP 403 via
  WebFetch, could not read body; logged negative, headline only.
- None of CIG's own public materials name Deaf Smith County or "Caliche Mound" explicitly
  (deliberate, per their own NDA disclaimer) — the CIG DS1 <-> Caliche Mound <-> 23INR0056 link
  rests on: (a) capacity band match (516/506 MW marketing vs 433.35 MVA gross / 408.21 MW
  dispatched IA nameplate / 406.6 MW queue — all same project, rounded differently across
  sources), (2025 COD marketing claim is CLOSE to the IA's own original 2025-08-28 scheduled
  COD — corroborating, not coincidental) and (b) CIG DS1, LLC being the literal signed IA party
  for INR 23INR0056. No single source states "CIG DS1 = Caliche Mound Solar = 23INR0056" in one
  sentence — this is a multi-source triangulation, treat as CONFIRMED via the primary IA
  document, well-corroborated (not merely leading) by CIG's own marketing.

### D1 amendment re-check (puct.py match, two keys)

Re-ran `puct.py match 23INR0056 --dir sources/` and `--key "CIG DS1"` — BOTH return only the
same single filing 35077-1688 (rung-0, INR-verified CONFIRMED). **No amendment exists under
either the project alias or the legal SPV name.** This makes the ~2-year gap between the IA's
own Scheduled COD (2025-08-28) and the queue's current claim (2027-10-26) unexplained by any
paper trail — the queue COD has drifted with no visible contractual mechanism. Treat as a
red flag: either informal (unfiled) schedule renegotiation, or the queue COD field is stale/
disconnected from the binding IA schedule (queue COD fields are self-reported, unlike the IA).

### D2 — Site geolocation via POI text (no boundary map exists in this IA)

No parcel/boundary/site-plan exhibit exists anywhere in the 47pp IA (`exhibit.py scan` found
only DocuSign section-header false positives at p14/p38; the only "map" is a schematic
one-line electrical diagram, Attachment 1 to Exhibit C, not geospatial). Per playbook rule 4
(no county centroids — must have a derivation method), used the POI TEXT description
literally: *"The Mule Deer Switch will be located on CO Road 8, 2.6 miles east of US Highway
60."* (Exhibit C.2). Derivation:
1. OSM Overpass query for `way["ref"="US 60"]` and `way["name"="County Road 8"]` within Deaf
   Smith County — found the two ways share a common node at **34.8509863, -102.3239961** (the
   literal US-60 x CR8 intersection).
2. Walked 2.6 mi EAST along CR8's own road geometry (haversine cumulative distance along real
   road vertices, not a straight-line bearing) → **34.84993, -102.27918**.
3. Cross-check: Overpass `power=substation` sweep of the wider area found REAL, named 345kV
   substations "**Windmill Substation**" (34.77338,-102.30455) and "**Hereford Wind
   Substation**" (34.77308,-102.29813) ~5.4-5.5 mi south of the candidate — confirms the
   AJ Swope-Windmill 345kV corridor named in the IA actually exists near Hereford; no OSM node
   literally named "AJ Swope" or "Mule Deer" was found (expected — Mule Deer is a NEW switch
   per the IA, not yet mapped).
- Recorded as `site.method = POI text geolocation` with medium confidence — this is a road-
  intersection + distance derivation cross-checked against real substation infrastructure, NOT
  a county centroid.

### D2 — Imagery (first pull, inconclusive — cloud cover)

`cdse.py chip --lat 34.84993 --lon -102.27918 --date 2026-07-15 --buffer-km 2` — first attempt
hit CDSE capacity/RemoteDisconnected errors (shared token/capacity contention; ~6+ other deep-
scan agents running concurrently in this container per `ps aux`, e.g. El Patrimonio, Lucky 7
Solar, Cradle Solar INR dirs). Per playbook "do NOT loop" rule, logged as negative and did not
retry in a loop; one later foreground retry succeeded. Saved
`imagery/s2_2026-07-15_center.png` (scene 2026-07-18, 30.5% cloud) — heavily cloud-obscured;
visible clear patches show undisturbed farmland/pasture + small ranch structures, no
grading/racking signature visible. INCONCLUSIVE, not a verdict — need a grid sweep / different
date to get past the cloud cover before committing to a construction-stage call.

### D2 — Grid sweep (clear scenes) + verdict

Pulled a 3x3 grid (`imagery/grid/s2_c*.png`, 2km buffer each, ±0.04° steps, scene 2026-05-19,
4.1% cloud, CLEAR) plus a wide single chip (`imagery/s2_2026-05-01.png`, 3km buffer, scene
2026-05-09, 0% cloud, CLEAR) around the candidate. Read c01, c02, c20, c22 + both wide/center
chips (6 full-size frames total, at the playbook cap). Findings: candidate site itself is
active center-pivot-irrigated farmland crossed by a highway and a winding creek; surrounding
grid shows dairy/feedyard operations, a private airstrip, ranch structures — NO grading, NO
racking, NO substation-pad clearing anywhere in the ~9x9 km search area. **Verdict:
no_activity.** Caveat: site-fix confidence is only medium (no boundary map in the IA), so the
true array footprint could sit outside this searched area if the switch-to-array offset is
larger than assumed — flagged in findings.json as a stated limitation, not resolved further
given the ≤6 full-size-frame cap.

### D5 — queue_history.py: CRITICAL CORRECTION to earlier cod_assessment

Ran `queue_history.py 23INR0056` → `timeline.md` (72 monthly snapshots, 2020-07→2026-06).
This REVISES my earlier real-time read of the divergence: the queue's own reported COD
**held at 2025-08-28 for 25 consecutive months (2023-02 through 2025-03)** — i.e., it was
NOT stale/disconnected from the IA; it matched the IA's Scheduled Commercial Operation Date
exactly, confirming the two were genuinely tracking the same target. The queue COD then
slipped POST-HOC, after 2025-08-28 had already passed with no construction: first to
2026-10-10 (as of the 2025-04 snapshot), then to 2027-10-15/2027-10-26 (from 2026-02 onward).
Both slips are undocumented by any IA amendment (re-verified via `puct.py match`, twice).
This is a more precise and more damning read than my initial "unexplained 2-year gap" framing
— the project hit, then missed, its real contractual date, and has been informally
re-forecast twice since with zero visible construction progress. Updated findings.json
cod_assessment and dossier.md §5/§7 accordingly.

### D5 — eia_history.py

`eia_history.py 23INR0056 --write` → NOT in EIA-860M (TX slice). Negative evidence, consistent
with factsheet.eia.status. No eia_history.json written (tool's own no-match behavior).
