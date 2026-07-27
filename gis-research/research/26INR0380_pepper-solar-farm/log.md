# Triage log — Pepper Solar Farm (26INR0380)

## T1 start

**queue_history.py** — 29 snapshots (2024-02-01 → 2026-06-01), 2 reported-COD changes.

**Milestone summary:**
- Screening started: 2024-02-27
- Screening complete: 2024-05-20
- FIS requested: 2024-02-22
- FIS approved: — (not achieved)
- IA signed: 2025-06-23 (first appeared in 2025-08-01 report)
- Meets 6.9(1): 2025-08-11
- Meets all 6.9: — (not achieved)
- Construction start/end, energization, sync, commercial op: all blank

**COD drift:**
- 2026-07-01 → 2024-02 to 2024-03 (dropped ~1 month in)
- 2027-07-01 → 2024-04 to 2025-04
- 2027-09-20 → 2025-05 to present (current)
COD drifted out twice; now sitting at 2027-09-20. 2 COD changes = moderate drift.

**Capacity:** minor oscillation (120.69 → 120.72 → 120.9 → 120.72 MW), settled.

**Conclusion:** IA signed June 2025, meets 6.9(1) Aug 2025; 6.9(all) not yet met; no construction milestones. Active mid-queue project.

## T2 start

**gmaps.py places** — 429 Too Many Requests on all queries ("Pepper Solar Farm", "Pepper Solar Farm McLennan County Texas"). One retry attempted, still 429. No pins found. Normal for early-stage project; API rate-limited.

## T3 start

**Developer confirmed:** Sabanci Renewables (subsidiary of Sabanci Holding, Turkey). Originally developed by OCI Energy; acquired by Sabanci.
**LLC:** Pepper Solar Farm LLC (Texas foreign LLC, formed 2024-01-10); also "OCI San Antonio Pepper Solar Farm LLC" (prior entity).
**PPA:** 100% output sold to Meta (announced ~Jun 2026); combined with Lucky 7 (Hopkins County) for 220 MWAC total.
**Financing:** $533M financial close achieved (NORD/LB, MUFG, BBVA, Intesa Sanpaolo debt; Advantage Capital tax equity). Projects moving into construction phase.
**Capacity note:** Mercom reports 156 MWdc / 120 MWac — consistent with queue's 120.72 MW AC figure.
**COD:** H2 2027 per multiple sources — consistent with reported 2027-09-20.
**News found:** Yes — PPA announcement, acquisition, financing, Empact de-risking partnership.
Sources saved: t3_meta_ppa_spw.md, t3_financing_mercom.md

## T4 start

**PUCT Interchange** — HTTP 402 Payment Required on all attempted URLs (FilingSearch, main Interchange app, PUC interconnection page). Portal blocked; one retry attempted. No IA PDF retrieved during triage. IA signed date confirmed from queue data (2025-06-23) but schedule exhibit not accessible here.
Note: IA signed is confirmed by queue milestone — Sabanci likely filed under a docket; deep scan should retrieve this directly.

## T5 start

**TX Comptroller Ch.313** — no searchable index accessible via WebFetch (pages redirect to general overview). DDG sweep for "Pepper Solar" + "McLennan" + "313"/"abatement"/"JETI" returned zero hits.
**JETI** — same; JETI pages inaccessible via WebFetch.
**Conclusion:** No abatement found. Normal for post-2022 project (Ch.313 expired; JETI program relatively new, sparse public data). Not a negative signal.

## T6 start

**Site candidate:** 31.6784, -97.0460 (infrasure.ai + POI corroboration, confidence medium)
**Chips fetched:** 4 of 9 grid cells (CDSE 403 errors on 5 cells; parallel rate-limit issue)
**Contact sheet:** imagery/contact_sheet.png — 4 frames read
**Imagery verdict:** Center chip (grid_5, 31.6784/-97.0460) shows large reddish-orange cleared/disturbed area with geometric linear features distinct from surrounding agricultural land. Consistent with site preparation or early construction grading. Other frames show undisturbed agricultural land. Construction activity VISIBLE.

## T7 start

triage_findings.json and triage.md written. 28 turns used. STOP.

## D0/D1 — deep scan start (2026-07-20)

Read factsheet.json/md, triage_findings.json, triage.md. IA PDFs already on disk (2 verified,
from puct-index rung 0/1 per spv.candidates). Ran `exhibit.py scan` — 3 map-candidate pages
flagged in original IA (p14, p30, p40), 1 in Amendment (p5). Ran `exhibit.py sheet` on the
51-page original IA (13 tiles) + rendered all 8 pages of the 8-page Amendment full-size.

**IA Exhibit B (Time Schedule), original (signed 2025-06-23):**
- NTP/security date: July 01, 2025
- In-Service: May 13, 2027
- Scheduled Trial Operation: May 23, 2027
- **Scheduled Commercial Operation: September 20, 2027** — exact match to queue-reported COD.
Source: sources/2026-07-19_puct_35077-2195_standard-generation-interconnection-agreement-be.pdf
(sheet08.png, p29-32 region).

**Amendment No. 1 (signed 2025-07-02/07-03):** replaces Exhibit B and Exhibit E only. Same
In-Service/Trial-Op/COD dates verbatim — only change is NTP/security date pushed July 01 → July
11, 2025. Financial security unchanged: $16,987,109.00 irrevocable standby LC. Signed by Sabah
Bayatli, "President, OCI Solar Power LLC" for Pepper Solar Farm LLC — confirms OCI Solar Power
as the signing corporate parent/manager, consistent with triage's "OCI Energy" origin story
before Sabanci's acquisition.
Source: sources/2026-07-19_puct_35077-2196_amendment-no-1-to-the-standard-generation-interc.pdf

**IA Exhibit C (Interconnection Details):**
- Name: PEPPER SOLAR FARM
- POI: "proposed Axtell Switch to be located within TSP's Tradinghouse S.E.S. Switch – Elm Mott
  Switch 345 kV line," McLennan County — matches queue POI text exactly. Exact site-location
  sentence following this is REDACTED (black bar) — cannot extract site address/coords from IA.
- 33 turbines/inverters @ 4.01 MVA = 32.33 MVA gross (122.28 MW at gen terminals, 120.69 MW at
  34.5kV bus) — matches queue capacityMw (120.72, minor variance normal).
- Equipment: HEM_GENIII-FS4010M solar power electronics.
Source: same PDF, sheet12/13 region (Attachment 1 one-line diagram literally labeled "Pepper
Solar Farm — 120.69 MW").

No project_area/acres figure found in either IA document (Exhibit C makes no acreage statement;
land conveyance clauses are boilerplate, not site-specific).

## D2 — imagery

Reused triage's site candidate (31.6784, -97.0460 — EIA-860M coords, matches POI). Attempted to
pull a pre-2025 baseline chip (2024-07-01) to distinguish the reddish-tan polygons seen in the
2026-07-01 center chip from ordinary plowed/fallow cropland (this is cotton/ag country — tilled
fields commonly show this same tan/pink color at 10m/px, so a single chip is NOT decisive).
**CDSE API returned `RemoteDisconnected` on 3 consecutive attempts** (transient service issue,
not a credentials problem — confirmed same error signature each retry with backoff). Baseline
comparison NOT obtained this session. Construction verdict held at "unclear_pending_baseline"
rather than upgraded to the triage's "activity_visible" — the playbook's early-exit rule
requires the historical-comparison chip before concluding activity, and triage skipped that
step.

## D3 — gap fill (in progress)

Next: CAD parcel search (Pepper Solar Farm LLC / OCI Pepper Solar LLC), retry gmaps.py places
(triage got 429 not a real zero), retry CDSE for baseline + look-around grid.

**gmaps.py places retry:** 429 Too Many Requests again (same as triage). Not a zero-result;
API key fleet-throttled this session.

**gmaps.py staticmap:** HTTP 403 — "Maps Static API is not activated on this API project."
Infra gap (key missing a scope), not a research finding. Logged, moved on.

**McLennan CAD (esearch.mclennancad.org):** direct curl → TLS handshake failure ("unexpected
eof while reading" even with -k); WebFetch → hostname/cert-altname mismatch on the www.
subdomain, then "Socket is closed" on the bare hostname. Portal unreachable from this
tooling both ways. No parcel/owner-name search performed — logged as a blocked source, not
a zero-hit.

**CDSE cdse.py chip (baseline pull, 2024-07-01):** RemoteDisconnected on every attempt (6
retries across ~25 min, spaced with sleeps up to 30s). Token cache confirmed valid/populated
(not a credential issue). `pgrep` shows 8+ concurrent `run_agent.py --mode deep` + a
`run_batch.py --concurrency 4` fleet running simultaneously — almost certainly CDSE-side
contention/rate-limiting from the fleet, consistent with CLAUDE.md's documented CDSE 403
rate-limiting history. Baseline/look-around imagery NOT obtained this session. Re-examined
triage's other 3 grid chips (imagery/s2_31.6784_-97.0160, s2_31.6784_-97.0760,
s2_grid_8_31.6484_-97.0460, all 2026-07-01): reddish-tan polygons appear scattered broadly
across ALL FOUR chips, not concentrated at the site candidate — consistent with this being
the normal blackland-prairie tilled-cropland palette in this part of McLennan County, not a
site-specific disturbance signature. Downgrading triage's "activity_visible" verdict to
"unclear" pending a real baseline comparison.

**search.py sweep for site/parcel detail:**
- "Pepper Solar Farm McLennan County site address groundbreaking" → 5 hits: Global Energy
  Monitor (gem.wiki), PR Newswire acquisition release, Sabanci Climatetech project page, OCI
  Energy projects page, SolarQuarter (re-hash of PR Newswire). Downloaded GEM wiki, PR
  Newswire, Sabanci page.
- **GEM Wiki (sources/2026-07-20_gemwiki_pepper-solar-farm.html):** independently states
  coordinates 31.6784, -97.0460 "(exact)" — matches EIA-860M coords to 4 decimals, a second
  independent source. No acreage given.
- **PR Newswire (sources/2026-07-20_prnewswire_oci-sabanci-sale.html, 2025-07-15):** OCI
  Energy sold Project Pepper to Sabanci Renewables; OCI "developed Project Pepper from
  inception and led all phases of site acquisition, pre-construction site studies,
  permitting, and grid interconnection"; Sabanci "will now finance, construct, own and
  operate"; COD "expected... in Q3 of 2027"; Sabah Bayatli (OCI) and Tolga Kaan Doğancıoğlu
  (Sabanci Climate Technologies CEO) quoted; legal counsel Sidley Austin (OCI) / Troutman
  Pepper Locke (Sabanci — no relation to project name, coincidental).
- **Sabanci Climatetech project page (sources/2026-07-20_sabanciclimatetech_pepper-project-detail.html):**
  156 MWDC/120 MWAC, McLennan Co; **Final NTP: 12 Dec 2025** (LATER than the IA's Jul 2025
  NTP date — schedule has slipped ~5 months at the pre-construction stage even though queue
  COD hasn't moved); COD Q3 2027; Site Control Completed; IA "signed with Oncor"; **PPA
  under exclusivity (NOT yet fully executed)** — this contradicts triage T3's claim of a
  100%-signed Meta PPA, so that claim should be treated as UNCONFIRMED/likely premature
  press framing; EPC = Signal Energy; Modules = Waaree; Trackers = Game Change; QSE = TNSK;
  300+ construction jobs, 3 permanent, powers 25,000 homes.
- "Pepper Solar Farm acres site plan McLennan" → Waco Tribune local article found
  (wacotrib.com) — **paywalled, article body inaccessible** (subscriber-only JS-rendered
  content, only tracking/consent boilerplate retrievable via curl). Logged as blocked, not
  read. PowerMag article (powermag.com) downloaded — confirms same OCI→Sabanci acquisition
  story via the sister Lucky 7 (Hopkins Co, 745 acres) closing; no new Pepper-specific detail
  beyond what's already sourced.
- No acreage figure for Pepper found anywhere (IA Exhibit C has none; news covers Lucky 7's
  745 acres but never states Pepper's). `project_area` stays null — honest unknown.

**ch313.py / Ch.313/JETI:** confirmed 0 hits (factsheet.json registry.hits already empty;
not re-run, would be pure duplicate cost).

## D5 — deterministic wrap-up

- `queue_history.py 26INR0380` → timeline.json/timeline.md: 29 snapshots (2024-02 → 2026-06),
  2 COD changes, current COD 2027-09-20 held since 2025-05-01 (14 months stable in queue).
- `eia_history.py 26INR0380 --write` → eia_history.json: 18 EIA-860M monthly reports
  (2024-12 → 2026-05), planned COD steady at 2027-07 the entire time, capacity steady 120.0
  MW, status steady "(P) Planned for installation, but regulatory approvals not initiated"
  — EIA has NOT reflected any construction-stage status upgrade despite the signed IA
  (2025-06) and Sabanci's claimed financial close/construction-phase entry (mid-2026 news).
  This divergence (EIA still "Planned/pre-regulatory" vs. developer PR claiming construction
  underway) is itself a notable gap worth flagging in the dossier, though EIA lag is common.
- `build_brief.py 26INR0380` → brief.html (9 KB, 4 images, 31 sources). Required fixing
  findings.json's `contractual_schedule.milestones` shape (had been written as a flat dict;
  build_brief expects a list of `{name, ...}` rows matching the Hanson reference schema) —
  corrected, re-ran, succeeded.
- `build_index.py` → research/index.json + INDEX.md, 168 projects indexed.
- dossier.md written per DOSSIER_TEMPLATE.md, cross-checked against Hanson reference example.
- findings.json final pass: tightened land_tenure/construction wording to reflect genuinely
  unknown (not "not yet checked") status, downgraded construction verdict field from
  "unclear_pending_baseline" to "unclear" (baseline never obtained this session — CDSE outage
  persisted end to end).

## STOP — deep scan complete

Two verification gaps stayed open due to infra outages this session, not absence of leads:
McLennan CAD (TLS-unreachable) and CDSE imagery (RemoteDisconnected, fleet contention). Both
are flagged explicitly in findings.json/dossier.md §8 for a future re-run rather than papered
over. Everything else — IA schedule/security, ownership chain, POI, equipment, COD
cross-corroboration, queue/EIA drift history — is on solid sourced ground.
