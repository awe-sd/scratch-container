# 16INR0049 Nazareth Solar — Deep Scan Log

## Triage Findings (2026-07-18, inherited)

T1 result: 143 snapshots 2014-07-01→2026-06-01. 15 COD changes (2016-07-01 original → 2027-08-31 current). IA signed 2026-03-05 (very recent). FIS approved 2025-07-29. Meets 6.9(1) 2024-03-22. Meets all 6.9: NOT achieved. No construction start/end. Capacity 203 MW (stable since 2025-02). Strong milestone progression — just crossed IA gate.

T2 result: gmaps.py 429 Too Many Requests on both attempts ("Nazareth Solar"); all 4 query variants blocked. 0 pins found. Normal — no Google Places data available this session.

T3 result: Developer = Vesper Energy (formerly Lincoln Clean Energy); SPV = TX Nazareth Solar LLC. Financing ~$236M closed Jan 2025 (Generate Capital). Construction reportedly underway per infrasure.ai. COD discrepancy: infrasure says IA executed 2023-06-07 but queue shows 2026-03-05 (may be amendment/re-execution). Infrasure build probability 59%, estimated COD 2026. Sources: infrasure_project_page.md saved. DuckDuckGo CAPTCHAs blocked further searches after 2 attempts; budget exhausted at 5 calls.

T4 result: PUCT Interchange interchange.puc.texas.gov returned HTTP 402 on all attempts (FilingParty search, description search, direct page). Portal blocked — no IA PDF retrieved. Note: infrasure.ai reports IA was executed (either 2023-06-07 or re-executed 2026-03-05 per queue). IA likely exists but could not be retrieved during triage.

T5 result: Ch.313 ABATEMENT FOUND — Castro Solar One, LLC / Nazareth ISD, App No. 1784, filed 2022-04-19, first full tax year 2025. Entity name differs from queue (TX Nazareth Solar LLC) but Nazareth ISD is Castro County — almost certainly same project. No JETI check performed (budget exhausted at 4 calls). PDF not downloaded (triage rule: only triage-level hit; deep scan should retrieve application PDF).

T6 result: Site candidate = ~34.54,-102.11 (Nazareth TX, Castro County) from web context. 3x3 grid attempted; CDSE token 403 on 6/9 chips (rows 34.54+34.57). 3 south-row chips (34.51) written. Contact sheet: pure cropland, center-pivot agriculture, NO solar infrastructure visible. Partial coverage only — center and north rows not imaged. No construction signal from available chips.

T7 result: triage_findings.json + triage.md written. turns_used ~28. Deep scan recommended. STOP.

---

## Deep Scan (2026-07-20)

### D0 — Checkpoint zero
Findings.json skeleton written before research.

### D1 — IA Schedule

**puct.py match run 2026-07-20:**
- 3 filings confirmed via INR join table: 35077-1643, 35077-1929, 35077-2431
- 2 unconfirmed (earlier Sharyland IAs): 35077-551, 35077-829
- All IA PDFs downloaded to sources/

**IA 35077-1643 (Oncor, signed 2023-06-06, filed 2023-07-03):**
- SPV: TX Nazareth Solar Project, LLC (note: "Project" in full name, not in queue)
- POI: Ozark Trail Switch, Swisher County TX — tap on Ogallala Switch–Tule Canyon Switch 345 kV double-circuit line
- Original Exhibit B schedule: In-Service 2024-12-17, Trial Op 2024-12-27, SCOD 2025-04-26
- Security (Exhibit E): LC $4,174,433.00 due on/before 2023-06-12
- Equipment (Exhibit C): 65 × Sungrow SG3600UD inverters, 204.1 MW gross, 234 MVA at 34.5 kV bus
- Artifact: sources/2026-07-20_puct_35077-1643_interconnection-agreement-between-oncor-electric.pdf

**IA 35077-2431 (Oncor Amendment No. 1, signed 2026-03-05, filed 2026-03-16) — CURRENT:**
- Updated Exhibit B schedule: In-Service 2027-04-01, Trial Op 2027-04-11, SCOD 2027-08-31
- Equipment: 54 × Sungrow SG4400UD inverters (upgraded from SG3600UD), 203 MW at POI
- Notice-to-commence-construction security deadline: 2025-08-15
- Note: construction notice deadline August 2025 already passed — required notice presumably given
- Artifact: sources/2026-07-20_puct_35077-2431_amendment-no-1-to-the-standard-generation-interc.pdf

**IA 35077-1929 (Hornet Solar II LLC IA, signed 2024-08-19):**
- Co-tenancy IA for a second project at same Ozark Trail Switch POI
- Definitions confirm: TX Nazareth Solar LLC (16INR0049) is the co-tenant
- Separate project at same POI — important context
- Artifact: sources/2026-07-20_puct_35077-1929_interconnection-agreement-between-oncor-and-horn.pdf

### D2 — Site + Imagery

**Key finding: SITE IS IN SWISHER COUNTY, NOT CASTRO COUNTY**
- The queue says "Castro County" but IA Exhibit C clearly states "Ozark Trail Switch in Swisher County, Texas"
- Ch.313 application #1592 filed with Tulia ISD (Swisher County); "100% of project within Swisher County"
- Entity chain: TX Nazareth Solar LLC → renamed Hornet Solar II, LLC → renamed Hornet Solar LLC (Ch.313 #1592 history)
  Note: Ch.313 #1592 is under Tulia ISD; the triage-found Ch.313 "Castro Solar One / Nazareth ISD" (App #1784) is a DIFFERENT abatement for a DIFFERENT project, which the triage incorrectly linked to this INR

**Google Places pin (2026-07-20):**
- Query "Nazareth Solar" → 1291 Co Rd 2, Tulia TX 79088 → 34.4884, -101.9728
- Confirmed: manufacturer/point_of_interest/establishment category → construction site pin
- Artifact: gmaps.py result (no file saved; lat/lon noted in log)

**EIA-860M cross-check:**
- Plant 67575 "TX Nazareth Solar", entity "Vesper Energy Development LLC"
- EIA coordinates: 34.49, -101.97 (Swisher County) — matches Places pin within ~0.002°
- EIA status as of May 2026: "(T) Regulatory approvals received. Not under construction"
- EIA planned COD drifted: 2025-06 → 2025-12 → 2027-06 (last report May 2026)
- Artifact: eia_history.json

**CDSE imagery — BLOCKED (2026-07-20):**
- All chip attempts at 34.4884,-101.9728 failed with RemoteDisconnected (OpenEO 402 synchronous, 403 batch)
- Token authentication works; blocking is at job submission level (rate limiting)
- Negative evidence: no satellite imagery obtained for correct Swisher County location
- Prior triage chips (34.51,-102.08 to -102.14) were at wrong Castro County location; show undisturbed cropland at wrong site

**Ch.313 Application #1592 — Tulia ISD (2021-04-26):**
- Applicant: TX Nazareth Solar, LLC; parent: Vesper Energy Development LLC
- Project area: ~2,000 acres in Swisher County, all within Tulia ISD
- Planned inverters: 53 (original design), 506,000 solar modules
- Construction commencement: estimated Q4 2022 (per 2021 application, obviously slipped)
- Artifact: sources/2026-07-20_comptroller_ch313-1592_nazareth-app.pdf

### D3 — Gap-fill searches

**Search: "Vesper Energy Nazareth Solar construction 2025 2026"** → FAILED (all backends)
**Search: "Nazareth Solar Swisher County Texas solar farm"** → FAILED (all backends)
**Search: "Hornet Solar OR Nazareth Solar Tulia Generate Capital financing"** → FAILED (all backends)
Note: DDG backends appear rate-limited or unavailable in this session.

**spv.py result:**
- Confirmed PUCT docket index hits: TX Nazareth Solar LLC in filings 551, 829, 1643, 2431
- No EIA-860M mismatch

**ch313.py result:**
- Ch.313 #1592: Hornet Solar LLC f/k/a Hornet Solar II, LLC f/k/a TX Nazareth Solar, LLC / Tulia ISD
- Entity rename chain confirmed: TX Nazareth Solar → Hornet Solar II → Hornet Solar
- Note: triage-found "Castro Solar One / Nazareth ISD / App #1784" is NOT this project; that is a separate project near Nazareth TX in Castro County that the triage agent incorrectly linked

### D4 — Narrative
(See dossier.md)

## Second-pass user review (2026-07-21): accurate imagery + parcel boundary + cleanup

- STALE IMAGERY PURGED: the 3 triage tiles were centered on a wrong Castro County guess
  (34.51,-102.08..-102.14), ~10 km west of the verified pin — deleted.
- PARCEL BOUNDARY FOUND: Ch.313 App #1592 Tab 11 (Westwood 'Project Area' map, 2021-04-23)
  rendered to sources/..._p24.png (+ regional _p25.png) — red Project Boundary east of the
  Castro/Swisher line, PV blocks, substation, gen-tie west into Castro (resolves the
  queue-county vs Ch.313-county discrepancy).
- USER OBSERVATION CONFIRMED ("close to an existing solar plant"): the plant IS the
  built-out original Nazareth project — renamed through Hornet Solar II/Hornet Solar LLC
  and completed (out of the active queue). Chips time its build 2022 bare -> 2024 grid ->
  2026 paneled. 16INR0049 is a successor position (fresh IA 2026-03-05) at the same campus.
- Monthly 2026 series (7 frames, Jan-Jul) added per user request: no new-phase activity.
- BANNED-SOURCE CLEANUP: sources/infrasure_project_page.md deleted; the infrasure
  "construction reportedly underway" claim removed from findings evidence (it was also
  contradicted by EIA and now by imagery — the 'construction' it reported was the finished
  sibling plant).
