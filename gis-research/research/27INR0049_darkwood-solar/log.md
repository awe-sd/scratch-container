# Triage log — 27INR0049 Darkwood Solar

**Date:** 2026-07-19
**Triage started**

---

T1 start
**T1 result:** 32 snapshots (2023-11-01 → 2026-06-01). Milestones: Screening complete 2023-09-01, FIS approved 2025-07-29, IA signed 2025-11-05. No construction start/end or energization milestones. COD drift: 1 change — 2027-01-30 → 2027-09-20 (slipped ~8 months, noted at 2025-07-01 snapshot). Capacity stable at 150.76 MW since 2024-01-01. **Strong queue progression: IA signed is a material milestone.**

T2 start
**T2 result:** gmaps.py returned HTTP 429 on both attempts (rate-limited). No pins found. Pins: 0.

T3 start
**T3 result:** Developer confirmed as **Mustang Creek Solar, LLC** (Austin TX); operating entity Mustang Creek Solar I, LLC (EIA Form 860). "Darkwood Solar LLC" not found as registered entity. Companion BESS (150.5 MW) at same site. **Construction signal:** Facebook group post states construction started on Evan Ranch (Comanche Co.). PUCT IA filing found (Oncor, Nov 2025, case ~35077). Location: near CR 328/343 between Proctor and HWY 36. Notes saved to sources/web_sweep_notes.md.

T4 start
**T4 result:** PUCT Interchange portal returned HTTP 402 on all attempts (auth/payment wall). Could not download IA PDF. **IA existence confirmed via T3 web sweep** (Oncor filed Standard Generation IA, Nov 2025, case ~35077) — IA is real, just not downloadable here. Milestone schedule exhibit not retrieved.

T5 start
**T5 result:** TX Comptroller Ch.313 page did not surface searchable data (portal redirects/generic page). DDG search for JETI/abatement hit CAPTCHA. No Ch.313 or JETI abatement found for Darkwood Solar / Mustang Creek Solar in Comanche County. **Normal for post-2022 project** (Ch.313 expired; JETI is newer and not yet widely filed). Not a negative signal.

T6 start
**T6 result:** Site candidate: ~31.97°N, 98.47°W (near Proctor TX, CR 328/343 area, Evan Ranch — low confidence, inferred from community posts). Contact sheet (2 frames): 2024-06-15 baseline shows Proctor Lake vicinity, green farmland/pasture, no solar infrastructure visible. 2026-06-15 chip is all-black (no valid Sentinel-2 composite available — likely data gap or heavy cloud cover at this date/location). **No construction visible in imagery.** Coordinate estimate may be offset (centered near Proctor Lake, not confirmed Evan Ranch parcel). Construction signal from Facebook text only, not confirmed by imagery.

T7 start
**T7 result:** triage_findings.json + triage.md written. Turns used: ~22. STOP.

---

## Deep scan — 2026-07-20

D0: findings.json skeleton written (checkpoint-triggered). Read PLAYBOOK.md, DOSSIER_TEMPLATE.md, Hanson example, spec §5.

D1: Ran `exhibit.py scan` on existing IA PDF (sources/2026-07-19_puct_35077-2307...pdf, 52pp, filed 2025-11-14).
KEY FIND: This is the signed Standard Generation IA for BOTH Darkwood Solar (27INR0049) and co-located
Darkwood BESS (27INR0050), Oncor + Mustang Creek Solar LLC. Full text extracted via pymupdf (no pdftotext binary
in container).
- Exhibit B (Time Schedule, p.29): In-Service Date May 13 2027; Trial Operation May 23 2027;
  **Scheduled Commercial Operation Date September 20, 2027** — EXACT MATCH to queue-reported COD (2027-09-20).
- Exhibit C (p.32): POI = "proposed Baggett Switching Station within the Company Comanche Peak Switch to
  Company Comanche Switch 345 kV transmission line" — matches queue POI text exactly. Solar: 40x Sungrow
  SG4400UD inverters, 176 MVA gross / 150.76 MW net. BESS: 43x Sungrow SC4000UD-MV-US, 150.5 MW.
- Attachment 1 to Exhibit C (p.45, one-line diagram): confirms both Darkwood Solar (150.76 MW) and Darkwood
  BESS (150.5 MW) tie into Baggett Switch; generator-side 0.2-mile transmission line to POI.
- Exhibit E (Security, p.51-52): LC/cash deposit schedule — $8,224,875 effective on/before 2025-08-04,
  rising to $18,111,175 effective on/before 2025-10-31.
- NO parcel/plat/boundary map in this IA — Exhibit C attachments are electrical one-lines only, not geographic.
  site.map_artifacts remains empty pending another document.
- Rendered pages: sources/2026-07-19..._p32.png (Exhibit C text), _p45.png (one-line diagram, read — confirms
  above, no coordinates).

Checkpoint write: findings.json updated with IA contractual_schedule, cod_assessment partial, llc_chain (Mustang
Creek Solar LLC as signatory).

---

D1 cont'd / D2 start — 2026-07-20 (checkpoint 2)

- puct.py match 27INR0049: CONFIRMED (INR-in-PDF) for filing 35077-2307 — re-downloaded identical file, deduped
  (md5 match), kept original 2026-07-19-dated copy.
- ch313.py resolve 27INR0049: NEGATIVE — no Ch.313/JETI hit for "Darkwood Solar" (740+38 rows searched).
- eia_history.py 27INR0049 --write: EIA plant 68478 "Darkwood Solar", entity Mustang Creek Solar I LLC, coords
  31.92853,-98.4241. Planned COD moved 2027-01 (through 2026-02 snapshot) -> 2027-10 (2026-03 onward). Status
  "(L) Regulatory approvals pending. Not under construction" every month 2025-01 -> 2026-05 (14 straight months).
  This CONTRADICTS the triage Facebook "construction started" claim as of the most recent EIA snapshot.
- queue_history.py 27INR0049: re-confirmed 32 snapshots, 1 COD change 2027-01-30 -> 2027-09-20 at 2025-07-01.
  Note: this queue COD slip landed EXACTLY on the IA's own Sept 20 2027 Scheduled COD (IA not signed until
  Nov 2025, but queue updated its number in Jul 2025 — likely pre-agreed schedule ahead of signature).
- search.py sweeps (all logged as negative/inconclusive):
  - "Baggett Switch Comanche County Texas" -> only Baggett Creek Cemetery historical hits, no substation page.
    "Baggett Switch" is likely a new/unbuilt switching station name, not yet on OpenInfraMap or public gazetteers.
  - "Mustang Creek Solar Darkwood Comanche County" -> only the same 2 Facebook group posts + unrelated
    "Cedar Creek Energy" project (different company, Minnesota-based, irrelevant hit on "Mustang Creek" name).
  - "TotalEnergies Comanche County Texas solar" -> TotalEnergies has no TX project matching (checked their
    project page directly via WebFetch — no Comanche/Darkwood/Mustang Creek mention). Not the developer.
  - "Darkwood Solar Texas 150 MW" -> no relevant results (home depot solar lights, unrelated plant DB).
  - WebFetch on Facebook post URL (facebook.com/groups/erathcountystopsolarfarmshere/posts/1636489723727376/):
    JS-rendered, only title/header returned — could not corroborate or refute the construction claim from FB text.
- Comanche CAD (esearch.comanchecad.org): JS/Kendo SPA, curl-based owner search returns app shell/302, not
  results. Could not complete parcel search this session — logged as a tooling limitation, not a true negative.
- gmaps.py places: HTTP 429 (rate limited) on both attempts this session (same failure as triage) — retry later.

Checkpoint write: findings.json updated — real_project_verdict set to "real_early" (signed IA + financial
security posted + FIS approved = real filing activity; but EIA says not under construction, no imagery
confirmation, no CAD/abatement corroboration — "early" pending site/construction verification).

---

D2 site pinpoint — 2026-07-20

- gmaps.py places: HTTP 429 on "Mustang Creek Solar" and "Darkwood Solar Comanche County Texas" — same
  rate-limit as triage, still blocked (likely fleet-wide quota exhaustion, not per-project). Logged negative.
- cdse.py chip: RemoteDisconnected / connection error on EIA coords (31.92853,-98.4241) AND on a known-good
  reprobe at Hanson Solar's confirmed coords (31.6950,-99.5315) — confirms this is a transient CDSE
  service-side issue right now, not a bad coordinate or bad request. Will retry later before wrap-up.
- Site candidate status: EIA-860M coords (31.92853,-98.4241, plant 68478 Darkwood Solar) are a SECOND,
  independently-sourced site candidate (vs. the triage's low-confidence Facebook/community-post guess at
  31.97,-98.47, ~10km away). EIA coords are derived from the generator's own regulatory filing (860M),
  materially more authoritative than a Facebook post, but still not a parcel/pin/imagery fix.

---

D3 gap-fill — MAJOR FIND — 2026-07-20

- search.py "jobs.totalenergies.com Mustang Creek Solar" surfaced 4 active job postings: Construction Manager,
  Mechanical QA/QC, Civil QA/QC, Electrical QA/QC — all "Mustang Creek Solar (Contract)", employer
  "TotalEnergies Renewables USA, LLC" (TERUSA), location Cleburne-Marti Drive TX, division Gas Renewables &
  Power / Project Execution. (jobs.totalenergies.com postings 80213/80214/80215/80315)
- Followed to TotalEnergies press release dated 2026-02-09: "TotalEnergies to Provide 1 GW of Solar Capacity
  to Power Google's Data Centers in Texas for 15 Years" — names Wichita (805 MWp) and **Mustang Creek
  (195 MWp)** as "TotalEnergies-owned sites currently under development in Texas... construction scheduled
  to begin in Q2 2026." 15-year PPA with Google, part of a 1 GW / 28 TWh deal.
  Saved: sources/2026-07-20_totalenergies_1gw-google-ppa-mustang-creek-pressrelease.pdf (+ .html mirror).
- THIS IDENTIFIES THE TRUE DEVELOPER/PARENT: TotalEnergies Renewables USA, LLC — not a random shell. Mustang
  Creek Solar LLC (the IA signatory) is TotalEnergies' project-level SPV. Google is confirmed offtaker.
- Reconciling capacity: PR says "Mustang Creek (195 MWp)" vs. ERCOT queue capacityMw=150.76 MW (net, at 34.5kV
  per IA Exhibit C) — 195 MWp is plausible as DC/gross nameplate vs. 150.76 MW AC net; NOT a discrepancy, just
  different capacity conventions (common solar DC:AC ratio ~1.3). Also matches earlier queue note "MWp" is
  typically DC panel rating.
  NOTE: "Mustang Creek Solar" almost certainly = Darkwood Solar (27INR0049) + Darkwood BESS (27INR0050)
  combined, or just the solar increment — PR doesn't separately break out BESS. Treating PR capacity as
  gross/DC nameplate for the solar block; queue's 150.76 MW is net AC, consistent with IA Exhibit C.
- Construction timing: Q2 2026 (Apr-Jun 2026) announced start is NOW PAST as of research date (2026-07-20) —
  i.e. construction should already be underway or about to be, consistent with active hiring for
  construction-phase QA/QC roles.
- EIA-860M "Not under construction" through May 2026 is NOT a contradiction — that snapshot predates the
  announced Q2 2026 start (May 2026 is still technically within Q2, and EIA reporting typically lags).
- This corroborates (does not fully confirm) the triage Facebook claim of construction starting on Evan Ranch —
  timing lines up with a real, named, financially-backed (Google PPA) developer's own announced schedule.
- cdse.py: retried at EIA coords AND known-good Hanson reprobe coords — both failed with the same
  RemoteDisconnected error. Confirmed CDSE service outage this session; imagery ground-truth unobtainable
  despite 3 attempts across 2 different endpoints/coords.
- gmaps.py: 3rd attempt ("Baggett Switch...") still 429. All Places lookups blocked this session.

Checkpoint write: findings.json updated — llc_chain now includes TotalEnergies Renewables USA LLC (developer/
owner) and Google LLC (offtaker), construction verdict changed to "unconfirmed_but_imminent" with the Q2 2026
PR-announced start date as primary evidence.

---

D4/D5 synthesis + wrap-up — 2026-07-20

- Additional negative searches: "Evan Ranch Comanche County Texas solar" (no hits beyond generic county
  pages), "Proctor Texas Comanche County solar farm 2026" (no new hits), Comanche Peak-Comanche 345kV route
  searches (no public map found; unrelated Oncor projects), "Baggett" + interconnection searches (no hits —
  confirms Baggett Switch is not yet a documented/named place anywhere outside this IA).
- ch313.py resolve retried with --name and --county flags: same negative result (no Ch.313/JETI match).
- Distance check (haversine, done locally, no tool): EIA coord (31.92853,-98.4241) vs. triage Facebook-derived
  coord (31.97,-98.47) = 6.3 km apart; both ~5 km from Proctor, TX — a soft/partial cross-check, not a fix.
- Final cdse.py and gmaps.py retries before wrap-up: both still failing (CDSE RemoteDisconnected, gmaps 429).
  Confirmed as session-wide tool outages, not fixable by this agent — recorded in
  findings.json.tool_outages_this_session for the batch operator to notice and possibly rerun imagery later.
- Wrote dossier.md per DOSSIER_TEMPLATE.md structure (Hanson Solar as reference).
- Final findings.json pass: site (EIA coord, confidence=low), project_area (not obtainable, explained),
  cod_assessment (independent 2027-Q4, drift_risk medium), real_project_verdict=real_early.
- D5 wrap-up commands run: queue_history.py (already current, 32 snapshots), eia_history.py --write (already
  current, wrote eia_history.json), build_brief.py 27INR0049 -> brief.html (9 KB, 2 images, 6 sources),
  build_index.py -> research/index.json + INDEX.md refreshed (160 projects).

RUN COMPLETE.
