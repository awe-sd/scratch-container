T1 start

## T1 — queue history
- 83 snapshots, 9 COD changes: 2021-06-11 → ... → 2027-05-01 (current)
- Capacity: 300 MW (2019) → 165 → 135 → ~133 MW (current 132.98 MW)
- FIS approved: 2026-03-13; IA signed: 2021-02-21 (appeared in queue 2026-04-01 snapshot)
- Meets 6.9(1): 2026-04-24; Meets all 6.9: 2026-05-19
- No construction start/end dates; no energization/sync/COD approvals
- COD drift pattern: aggressive slippage from 2021 original → 6 years later

T2 start

## T2 — delivery pins
- gmaps.py blocked: HTTP 429 on both attempts (exact name + county variant). One retry used.
- No pins recorded. NORMAL.

T3 start

## T3 — web sweep
- Developer confirmed: **Repsol Renewables** (acquired from **ConnectGen Operating LLC** ~2024)
- Groundbreaking: **October 2025** — construction actively underway as of KBTX April 2026
- Location: Leon County near **Marquez, TX** (~1,300 acres)
- 595 MW total "Pecan Prairie Solar Facility"; this INR is the South portion (~133 MW)
- Sources saved: kbtx.com article (April 2026)
- gem.wiki 403; interconnection.fyi snippet (owner: Repsol); infrasure.ai snippet (ConnectGen)
- "Pecan Prairie South LLC" DDG search: no results

T4 start

## T4 — PUCT Interchange
- interchange.puc.texas.gov: HTTP 402 on all attempts (FilingParty + Description queries)
- No PUCT script available; portal requires session auth
- No IA document retrieved. Per rules: blocked portal → negative log, move on.

T5 start

## T5 — abatements
- TX Comptroller Ch.313 portal: no direct URL access; site is a navigation hub, no filterable table reachable via WebFetch
- JETI registry: no searchable list available via the pages fetched
- Ch.313 expired for new apps after Dec 2022; project in queue since 2019 (COD was ~2022 originally) — potential historical abatement possible but not confirmed
- No abatement found. NORMAL for a project without clear school-district documentation surfaced.

T6 start

## T6 — imagery
- Site candidate: near Marquez, Leon County, TX (~31.24°N, 96.25°W); confidence LOW (no pin, no IA map)
  - Basis: KBTX article confirms "near Marquez" and 1,300-acre site in Leon County
- CDSE 3×3 grid attempt: HTTP 401/403 on all 9 chips — credentials not configured (~/.config/gis-research.env is example file)
- One retry also 401. BLOCKED — cannot acquire imagery this session.
- Skipping sheet/frame reads. No imagery acquired.

T7 start

## T7 — write and stop
- triage_findings.json written
- triage.md written (10 lines)
- Turns used: ~22
- STOP

## D1 — SPV / IA resolution (session 2, 2026-07-20)
- puct.py match on "Pecan Prairie South", "Repsol", "ConnectGen", "CG Leon County LLC" (no suffix): all 0 hits — queue codename search alone insufficient
- puct.py search "CG Leon County" (broad, no docket filter) surfaced NEW dockets 59753/59754/59906/59907: PGC + REC-generator registrations for **CG Leon County LLC** (no "II") — filed 2026-05-12 / 2026-06-18
- Fetched docket 59753 item 1: PGC registration form. CONFIRMED SPV = CG Leon County LLC. Exact match: 132.98 MW, Solar, ERCOT North, Leon County, TSP "Cross Transmission Texas". Physical unit address: 9396 FM 3, South Normangee, TX 77871. Corporate parent: Repsol Renewables North America, Inc. (sources/2026-07-20_puct_59753-1_filing.pdf)
- CG Leon County II LLC = SIBLING project "Nabatoto Solar North (Pecan Prairie North)" = 21INR0428 (confirmed by text in First Amendment fixing an INR typo). NOT our INR — do not conflate. 400-450MW, separate co-located facility.
- Docket 35077 item 1242 (2021-02-26 original SGIA) is between CTT and CG Leon County II LLC ONLY (North) — our project (South) was not yet a signatory at execution.
- Docket 35077 item 2483 = "Seventh Amendment to SGIA" (signed 2026-04-09, filed 2026-05-12 — SAME DAY as the PGC registration) ADDS CG Leon County LLC (South, our INR) as co-Generator to the shared-facilities agreement. This is the FIRST time South is a party. CONFIRMED via exhibit text: "Name: Pecan Prairie South (or CG Leon County I Project)", 130 MW at POI, Leon County.
- South-specific Exhibit B (7th Amendment): all pre-construction milestones "N/A (In-Service Date Achieved)"; In-Service Date 04/15/2025 (past); Trial Operation 10/21/2026; Scheduled COD **09/30/2027** — LATER than queue's reported 2027-05-01 by 5 months. Live COD divergence between binding IA and self-reported queue date.
- Exhibit E (7th Amendment): total combined security $27,900,000, already fully provided (Letter of Credit / cash) as of 03/28/2025, joint & several liability between CG Leon County LLC (South) and CG Leon County II LLC (North) — not split per-project. Strong reality signal: real money posted, in advance of formal contractual admission as a party.
- Exhibit C3 (POI diagram): shared CTT station taps "To Pecan Prairie North 320MW" and "To Pecan Prairie South 130MW" between "To Limestone" and "To Gibbons Creek" lines — consistent with queue POI text "CTT Yellow Wolf, bus # 79007" (station name not spelled out as Yellow Wolf in text reviewed; treating as consistent, not confirmed literal match).
- gmaps.py places: HTTP 429 (rate limited) on 3 attempts with backoff (5s/15s/30s) — logged negative, will retry later or proceed without Places pin; PGC physical address (9396 FM 3, South Normangee TX) is a strong independent site lead already.

## D2 — Site + imagery (session 2, 2026-07-20)
- gmaps.py places: HTTP 429 (rate-limited) on 5 attempts across ~2 minutes with backoff — logged negative, Google Places pin not obtained this session.
- CDSE chip/timelapse: cdse.py raised `http.client.RemoteDisconnected` on every attempt (multiple dates/buffers). Diagnosed root cause via manual curl+token replication: CDSE openEO sync endpoint returns **HTTP 402 PaymentRequired — "You do not have sufficient credits to perform this request"** (marketplace-portal.dataspace.copernicus.eu/pages/pricing). cdse.py's urllib request handling does not surface the 402 body cleanly and instead raises RemoteDisconnected, masking the real cause.
- CONCLUSION: CDSE account is out of processing credits fleet-wide as of 2026-07-20 ~16:50 UTC. No satellite imagery obtainable this session for ANY project, not specific to this one. This is a fleet-level blocker — should be reported to the user/ops, not retried further here.
- Site coordinates therefore rest on: (1) EIA-860M coords 31.05001, -96.221 (factsheet.json, plant 64981) and (2) PGC registration physical address "9396 FM 3, South Normangee, TX 77871" (sources/2026-07-20_puct_59753-1_filing.pdf) — both independent of the queue report, cross-checking each other's rough locale (South Normangee is in southern Leon County, consistent with EIA lat 31.05 being south of Leon County center).
- No IA exhibit map (C3/C1) gives lat/lon directly — Exhibit C3 is a schematic (POI topology only: To Limestone / To Gibbons Creek / To Pecan Prairie North 320MW / To Pecan Prairie South 130MW), not a georeferenced site map. No parcel-boundary map exists in any IA document reviewed. site.map_artifacts is empty — this is expected per playbook (no CAD/abatement doc obtained yet either).

## D3-D5 — Ch313, wrap-up (session 2, 2026-07-20, budget cutoff)
- ch313.py resolve --name "CG Leon" surfaced BOTH sibling Ch313 agreements: #1702 CG Leon County II LLC (Leon ISD = North/21INR0428) and #1703 CG Leon County LLC (Normangee ISD = South/21INR0371, our project). Downloaded app/agmt/amend1 PDFs for #1703.
- Ch313 #1703 app Tab 16 map (p26, rendered): 2019-12-04 dated "Proposed Reinvestment Zone" polygon along FM 3, straddling Robertson/Leon county line NW of Normangee near Marquez — a DIFFERENT locale than the EIA-860M/PGC-address South Normangee point (~15-20km apart). Judgment call in findings.json: weighted EIA-860M (2 independent sources, stable 2022-2026) over this single 2019 static map, since project capacity shrank 300MW->130MW since the map was drawn (likely pre-shrink combined footprint). NOT resolved with imagery — flagged for next pass.
- Tab 10 (p24): one incidental CAD parcel inside the Ch313 zone (GHCJ Ranches LLC, 69.535 ac, Property ID 613681) — a landowner parcel, not necessarily the SPV's own land.
- queue_history.py 21INR0371: 83 snapshots, 9 COD changes -> timeline.json/md written.
- eia_history.py 21INR0371 --write: plant 64981 'Pecan Prairie South Solar', entity Repsol Renewables NA, coords 31.05001/-96.221 STABLE across all 5 years of EIA-860M reports (2022-04 to 2026-05); planned COD drifted 2023-07->2025-05->2025-12->2026-03->2027-03; status held "(L) Regulatory approvals pending. Not under construction" the entire time -> eia_history.json written. This resolved the site-coordinate conflict in favor of South Normangee over the 2019 Ch313 map.
- build_brief.py 21INR0371: wrote brief.html (17KB, 62 sources, 0 images — no imagery this session).
- build_index.py: refreshed research/INDEX.md (164 projects).
- BUDGET CUTOFF at 80% warning — stopped after wrap-up tools; did NOT get to: CAD owner-name search for CG Leon County LLC itself, TX SOS entity lookup, land-tenure determination, gmaps retry, CDSE retry. dossier.md + findings.json written before cutoff per playbook rule.
