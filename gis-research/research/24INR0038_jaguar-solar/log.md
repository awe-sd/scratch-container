# Research Log — Jaguar Solar (24INR0038)

Project: Jaguar Solar | INR: 24INR0038 | County: McLennan, TX | 300.87 MW Solar PV
POI: Tap 345kV 13405 Tradinghouse SES - 68090 Sam Switch | CDR zone: NORTH | Reported COD: 2027-12-11
Research started: 2026-07-19

---

## Stage 1 — LLC / parent chain


### Stage 1 findings (2026-07-19)

**LLC chain confirmed**: SP-Jaguar Solar LLC → renamed PP Jaguar Solar LLC (Sep 2024) → Perfect Power LLC (CEO Anthony Maselli, White Plains NY) → SER Capital Partners (PE, Rahul Advani). ~~"Enbridge" mentioned in one secondary source (infrasure.ai Nov 2024) — unverified from primary sources.~~ [2026-07-21: that Enbridge claim cited a banned queue-aggregator domain (infrasure.ai) and has been removed from findings.json — no primary-source corroboration found; see cleanup note below.]
- TX SOS file #0804302034 (Foreign LLC, Delaware, domestic jurisdiction)
- OpenCorporates: 251 Little Falls Drive, Wilmington DE 19808 (CSC statutory agent address)
- Source: web research, SER Capital Partners portfolio page [infrasure.ai citation removed 2026-07-21 — banned aggregator domain]

**PUCT IA**: IA with Oncor signed 2022-09-12. Fourth Amendment to IA dated June 3, 2025 exists. PUCT Interchange automated fetch returned HTTP 402 — manual access needed.

**Queue COD drift** (from timeline.md): 5 COD entries, 4 changes:
- 2024-04-30 (2021-07 → 2023-03)
- 2025-06-30 (2023-04 → 2024-04)
- 2026-06-01 (2024-05 → 2024-11)
- 2027-02-11 (2024-12 → 2025-10)
- 2027-12-11 (2025-11 → 2026-06, current)
IA signed 2022-09-12; Meets all 6.9 as of 2024-01-23; FIS not yet approved.

---

## Stage 2 — County Records

**Ch.313 Application #1688 (Axtell ISD, McLennan County)** — DIRECT MATCH:
- Applicant: SP-/PP Jaguar Solar LLC (TX taxpayer #32081793179)
- 157 MWac solar + 25 MWac BESS; $160.4M investment; limitation $15M/yr M&O
- First limitation year: Jan 1, 2025
- 4 parcels in **Tomas de la Vega survey**, McLennan County — total **1,938.54 acres**
  - TOMAS DE LA VEGA 625.0 ac
  - TOMAS DE LA VEGA 469.0 ac
  - TOMAS DE LA VEGA 485.14 ac
  - TOMAS DE LA VEGA 359.40 ac
- POI verbatim: "345 kV Tradinghouse Transmission Line to Sam Switch Substation"
- Source URLs identified; downloading now
- project_area = 1,938.54 acres (Ch.313 Exhibit 1)

**Google Places**: No "Jaguar Solar" or "PP Jaguar Solar" construction pins found. General solar installer results returned (unrelated). NEGATIVE for delivery pin.

**MCAD eSearch**: Site returned socket timeouts — blocked to automation. Parcel survey info obtained via Ch.313 agreement instead.

**McLennan County Commissioners Court**: Road Use Agreement with PP Jaguar Solar LLC on 2026-03-03 agenda. Document too large to fetch (>10MB PDF).

---

## Stage 3 — Imagery refresh, site re-derivation, banned-source cleanup (2026-07-21)

**Banned-source cleanup**: grepped findings.json, log.md, triage_findings.json, triage.md,
factsheet.{json,md}, brief.html, timeline.{json,md}, and sources/ for
`infrasure|futuregrid|cleanview|interconnection.fyi|gridinfo|ercotqueue|energyacuity`.
Hits only in findings.json (`developer.possible_partner`, `sources_found`) and log.md
(Stage 1, above — struck through). No `sources/` files originate from a banned domain
(sources/ only holds Comptroller Ch.313 PDFs and PUCT docket-35077 PDFs). Removed the
Enbridge/infrasure.ai citation from findings.json (`possible_partner` now marked
unconfirmed/removed; the `sources_found` line deleted) since it had no primary-source
corroboration independent of the banned aggregator.

**Site re-derivation** (previous coordinate was `medium` confidence and was only the
Tradinghouse SES transmission-line terminus, not the project site):
- Ran `exhibit.py scan` over every PDF in sources/ — found Ch.313 App #1688 Tab-11a
  "Project Boundary and Project Vicinity Map" (p29-33) and IA Exhibit C / Attachment 4
  (p31, p46 of the PUCT IA PDF).
- **New finding**: IA Exhibit C names the actual POI substation **"Tiger Creek Switch"**
  — a new Oncor switching station built specifically for this interconnection, tapped
  into the existing Sam Switch-Tradinghouse SES 345kV line (Exhibit C sections 8-9). This
  is a materially more precise identity than "Tradinghouse SES-Sam Switch tap." However
  both the precise location text in Exhibit C section 2 and the Attachment 4 vicinity map
  are **redacted (black boxes)** in the filed PUCT copy — confirmed by extracting the
  embedded CCITT-fax image directly (not a rendering bug: inverting the image shows the
  map/legend boxes are blank, not merely low-contrast). Logged as an explicit miss.
- Rendered the Ch.313 Tab-11a map exhibit (p31 county-wide, p32 zoomed) to sources/. The
  zoomed map shows a red "Proposed Reinvestment Zone & Project Boundary" polygon south of
  Axtell, near the Axtell ISD boundary and US-84/TX-31.
- Georeferenced p32 by OSM-geocoding 5 labeled places visible on the map (Ross, Tours,
  Leroy, Axtell, Mt Calm) and fitting a pixel->lat/lon affine transform (all residuals
  <70m). Predicted red-boundary centroid: **31.602, -96.975**.
- Cross-checked against `data/eia_generator_tx.parquet` (McLennan County, latest
  reportDate 2026-05-01): **"PP Jaguar BESS LLC"** (the companion battery project, same
  POI per Exhibit C) has an EIA-860M generator pin at **31.599920, -96.97054**,
  `(OP) Operating`. This is ~470m from the independently-georeferenced map centroid —
  strong triangulation from two unrelated methods. `eia_history.py 24INR0038 --write`
  found no 860M match under the solar entity name itself (logged as a negative — normal
  for a project whose PV field hasn't visibly started).
- **Adopted 31.59992, -96.97054 as the new site coordinate, confidence upgraded to
  high.** Old Tradinghouse-substation and Axtell-centroid estimates kept in findings.json
  as `superseded_estimate`/`superseded_alternate_estimate` for the record (the old Axtell
  alternate guess, 31.663/-97.135, was simply wrong — real Axtell village is
  31.6580/-96.9704 per OSM, not 31.66/-97.13).

**Imagery** (`s2aws.py chips`, 31.59992/-96.97054, buffer 3.5km, window 20d, cloud<=25%,
dates 2024-07-01/2025-07-01/2026-01-15/2026-04-15/2026-07-15 -> imagery/key/): all 5 chips
fetched, PNG-magic verified. All 5 share the same tile (S2 tile 14RPV) and all 5 carry an
identical ~18% black no-data band across the extreme north edge of the frame (tile-edge
gap, not a centering bug) — the site itself and the full Ch.313 project-boundary bbox
(computed from the same affine fit) sit well clear of that band, so no re-fetch was
needed. Read every frame at full-frame and tight-crop zoom:
- **2024-07-19**: bare, reddish-tan graded rectangular pad at the Tiger Creek Switch
  site — early civil/grading, no bright structures yet.
- **2025-07-17**: pad replaced by a bright white switchyard/BESS building complex
  (L-shaped main structure + separate elongated building south of the county road) —
  matches reported BESS Phase I mechanical completion (2025-04-02).
- **2026-01-28, 2026-05-03, 2026-07-19**: identical footprint to 2025-07, stable —
  confirms a completed, static facility, not an actively expanding construction site.
  (A striped/ribbed sun-glint pattern on the gantry structures in the 2026-04-15/05-03
  frame briefly looked like PV racking on first look; side-by-side comparison across all
  5 dates shows it's the same fixed substation footprint, just different shadow/sun
  angle — not a separate solar installation.)
- **No utility-scale solar PV array is visible anywhere in the full 7km x 7km frame at
  any date**, including the most recent (2026-07-19) pass. The 300 MW AC solar field
  itself has not visibly broken ground. This matches the repeated queue COD slips (now
  2027-12-11) and the county's Mar-2026 Road Use Agreement reading as a site-access
  negotiation rather than an active-construction signal.
- **Neighbor check**: queried `data/eia_generator_tx.parquet` for McLennan County
  (latest reportDate 2026-05-01) — Copperhead Solar, Sandy Creek Energy Station, Pepper
  Solar Farm, Griffin Solar, Albatross Solar, Braswell Solar, EDFR Bluebonnet, Eddy II,
  AbbVie Waco are all >8km from the imagery center and outside the 3.5km buffer, so no
  attribution risk in-frame. Tokio Solar (23INR0349, sibling project with its own
  research dir — not touched) is ~30km away, unrelated.

**findings.json updated**: site block (lat/lon/method/confidence/provenance_rung/
map_artifacts/superseded_estimate), infrastructure.tiger_creek_switch (new), construction
block (verdict/first_activity_seen/imagery_artifacts/assessment), developer
.possible_partner (banned citation removed), sources_found and pending lists refreshed.
`brief.html` rebuilt via `build_brief.py`.

