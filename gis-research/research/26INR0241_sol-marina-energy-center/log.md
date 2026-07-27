# Triage log — Sol Marina Energy Center (26INR0241)

## T1 start

Queue history: 33 snapshots (2023-10-01 → 2026-06-01). COD drifted twice:
- 2026-06-30 (held 1 month, Oct–Nov 2023)
- 2027-04-17 (held ~20 months, Dec 2023–Jul 2025)
- 2027-10-29 (current, Aug 2025–Jun 2026)

COD-drift count: 2 changes (3 distinct values).

Milestone dates achieved:
- Screening started: 2023-10-25
- Screening complete: 2024-01-22
- FIS requested: 2023-09-07
- FIS approved: 2025-03-03
- IA signed: 2025-04-25
- Meets 6.9(1): 2025-07-29

NOT achieved: Meets all 6.9, construction start/end, energization, sync, COA.

Capacity: stable at 175.3 MW since Dec 2023 (bumped from 142.88 MW).

T1 complete — IA SIGNED (2025-04-25), good milestone stack, no construction dates yet.

## T2 start

gmaps.py places: "Sol Marina Energy Center" → HTTP 429 (rate limit). Retry with "Sol Marina Energy Center Ellis County solar" → HTTP 429 again. T2 budget exhausted.

Pins found: 0 (tool blocked, not negative evidence).

## T3 start

DDG sweep results:
- Developer confirmed: Adapture Solar Development, LLC
- SPV confirmed: Sol Marina Energy Center, LLC (TX foreign LLC, Delaware domestic, filed 2025-04-14, Active)
- Related project: 26INR0242 Sol Marina Energy Center BESS (57.15 MW, same INR block)
- IA PDF surfaced at PUCT docket 35077 → direct fetch returned HTTP 402 (portal requires session)
- No press releases or construction news found
- Third-party sites (ercotqueue.com, interconnection.fyi) confirm developer + 85% build-chance rating

Sources saved to sources/web_sweep_t3.md

T3 complete — developer known, IA exists at PUCT, no news.

## T4 start

PUCT Interchange portal: all requests return HTTP 402 (session cookie required). Cannot search or download via WebFetch.

IA is CONFIRMED to exist from T3 DDG results:
- Docket: 35077, document 2141
- URL: interchange.puc.texas.gov/Documents/35077_2141_1500541.PDF
- Description: Standard Generation Interconnection Agreement, Oncor ↔ Adapture Solar Development
- Covers both 26INR0241 (solar) and 26INR0242 (BESS), signed 2025-04-25
- Milestone schedule exhibit: NOT retrieved (portal blocked)

ia_found: TRUE (confirmed from DDG). Schedule exhibit: blocked, needs portal access.

T4 complete — IA confirmed, schedule exhibit unread (PUCT portal 402).

## T5 start

TX Comptroller Ch.313: program expired post-2022; no searchable registry found for this project. No applications expected for post-2022 projects.

JETI (HB 5): JETI subpage navigational only; no searchable registry accessible via WebFetch. No "Sol Marina" or "Adapture" entries surfaced.

abatement_found: FALSE — normal for 2026 application, Ch.313 expired; JETI possible but no evidence found.

T5 complete — no abatement found (expected).

## T6 start

Site candidate search:
- gmaps.py blocked (T2: 429)
- IA PDF blocked (T4: 402)
- POI: "Tap 345kV 2427 Watermill - 2466 Big Onion"
  - Watermill Switch: Dallas County per DDG results (not Ellis County substation)
  - Big Onion: no results found
- No pin, no abatement map, no IA map with coordinates

Best site candidate: "somewhere in Ellis County" — no specific location.
Per checklist rule: SKIP imagery when no candidate better than county-level.

construction_visible: N/A (imagery skipped)
site_candidate: null

T6 complete — no site candidate, imagery skipped per rules.

## T7 start

triage_findings.json written.
triage.md written.

Turns used: ~22. Deep scan recommended: YES.

T7 complete.

---

## D1 — IA Schedule extraction (2026-07-20)

exhibit.py scan: IA PDF 51pp, 2 candidate pages (p14, p40).
exhibit.py sheet: 13 tiles generated.
Rendered key pages: p14, p30, p36, p39, p40, p44.

### Exhibit B (Time Schedule) — confirmed from sheet08, p29-30:
- May 1, 2025: Generator provides notice to proceed (past)
- **In-Service Date: April 15, 2027**
- **Trial Operation: September 20, 2027**
- **Scheduled COD: October 29, 2027** (matches queue reported)
- May 15, 2026: Grading/drainage for Nimbus Switch + All-weather road completed (past deadline)
- Aug 14, 2026: All-weather road operational for Oncor access (upcoming)
- Sep 15, 2026: TSP takes possession of TIF deed/easement
- June 15, 2026: Generator provides site drawings w/ generating unit locations (past deadline)
- Oct 15, 2026: Generator provides lat/lon of all solar panel generating units to TSP

### Exhibit C (Interconnection Details) — confirmed from sheet10, p31:
- POI: Nimbus Switch (NEW 345kV switching station on Watermill–Big Onion 345kV line), Ellis County
- Address REDACTED (black box in PDF)
- Equipment: 47 SUNGROW SC4400UD-MV-US inverters, gross 196.46 MVA, net 175.26 MW at 34.5kV
- BESS companion: 16 SUNGROW SC4000UD-MV-US inverters, 57.15-58.6 MW (26INR0242)

### Exhibit C Attachment 1 (p44) — One-Line Diagram:
- Nimbus Switch taps between 345kV to Watermill Switch and 345kV to Big Onion Switch
- POI at fence between TSP (Nimbus Switch) and Generator Switchyard

### Exhibit C main body (p36):
- Shankle Switch – Pebble Creek Switch 138kV line: lowering required (project likely near/under this corridor)
- Watermill Switch Changes: carrier frequency modification for Nimbus Switch addition
- Big Onion Switch Changes: relay settings update for Nimbus Switch line

Financial security: confirmed "Yes" in factsheet (queue milestone). Amount not visible in pages read — may be in Exhibit A or separate section. Check sheet02 (p8 = Exhibit A) and sheet12.

Site location: Address redacted in Exhibit C — must find via POI infrastructure search.
Artifacts: sources/2026-07-19_puct_35077-2141_standard-generation-interconnecti_p44.png (one-line diagram showing Nimbus switch topology)

### Exhibit D (p46) — Notice/contact info:
- Developer: Adapture Solar Development, 1601 Harrison St Suite 1630, Oakland CA 94612
- Email: transmission-ix@adapturerenewables.com / AP@adapturerenewables.com
- Parent domain confirmed: adapturerenewables.com = Adapture Renewables
- Oncor contact: Robert Holt, 777 Main St Suite 707, Fort Worth TX 76102

### Exhibit E (p49-51) — Security Arrangement:
- **Financial security: $17,035,909 Irrevocable Standby Letter of Credit**
- Effective date: on or before May 1, 2025
- Instrument: ISBLC issued by Generator-selected TSP-approved major US commercial bank
- This is a real, substantial security posting — strong real-project signal
- Artifact: sources/2026-07-19_puct_35077-2141_standard-generation-inter_sheet13.png

## D2 — Site + Imagery (2026-07-20)

### Google Places pin:
- Query: "Sol Marina Energy Center" → 2210 Farrar Rd, Palmer, TX 75152, USA
- Coords: 32.467749, -96.707719
- Type: point_of_interest, establishment
- Palmer TX is in Ellis County — consistent with project county
- Confidence: med (pin exists, address in correct county; no imagery cross-check possible)

### CDSE imagery: UNAVAILABLE this session
- All chip/timelapse calls: RemoteDisconnected at openEO /result endpoint
- openEO endpoint itself pings OK (200) — likely load-balancer or backend overload
- Zero imagery frames obtained
- Construction stage: UNKNOWN (cannot determine from satellite)

### POI cross-check:
- POI per IA: Nimbus Switch (new 345kV) on Watermill–Big Onion line, Ellis County
- Watermill Switch is in Dallas County per triage search — Nimbus Switch will be a new tap on the line entering Ellis County
- 32.467749, -96.707719 is ~6 km NNW of Palmer TX, in rural Ellis County farmland
- Shankle–Pebble Creek 138kV line must be lowered for project → site likely near/under that corridor
- Cross-check pending: no imagery, no CAD parcel found (CAD web search failed — backend down)

## D3 — Gap-fill searches (2026-07-20)

### Web search backend: DOWN all session
- All DDG queries returning ConnectionError
- Negative evidence (cannot distinguish "no results" from "search failed"):
  1. "Adapture Solar Development Ellis County Texas Sol Marina" — FAILED (backend)
  2. "Sol Marina Energy Center Palmer Texas solar farm" — FAILED (backend)
  3. "Ellis County Appraisal District Sol Marina OR Adapture Solar" — FAILED (backend)
  4. "2210 Farrar Rd Palmer Texas solar OR Sol Marina" — FAILED (backend)
- ch313.py: NEGATIVE (no Ch.313/JETI match — expected for 2026 project)
- spv.py: Adapture Solar Development, LLC confirmed (PUCT index)
- eia_history.py: NOT IN EIA-860M (normal early-stage negative evidence)

### Adapture Renewables parent chain:
- SPV: Sol Marina Energy Center, LLC (DE/TX)
- Developer/operator: Adapture Solar Development, LLC
- Parent: Adapture Renewables (adapturerenewables.com, Oakland CA)
- No further parent chain found (web search down; Adapture Renewables appears to be independent)
