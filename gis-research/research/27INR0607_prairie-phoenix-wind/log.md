# 27INR0607 Prairie Phoenix Wind — research log

Project: Prairie Phoenix Wind | INR: 27INR0607 | 297.25 MW Wind | McLennan County, TX | CDR: NORTH
POI: 3403 Lake Hall 345kV | Reported COD: 2027-09-01
Researched: 2026-07-19

---

## Triage pass (prior session)

T1: queue_history.py — 5 snapshots (2026-02-01 → 2026-06-01). Screening complete 2026-05-01. FIS requested. No FIS approval, no IA, no construction dates. COD stable at 2027-09-01.
T2: gmaps.py places — HTTP 429 rate-limited. No pins obtained.
T3: Web search — Developer = ENGIE. Prairie Phoenix Wind LLC registered TX 2025-06-25, 1360 Post Oak Blvd Houston. Repower of Prairie Hill Wind Farm near Mart TX (McLennan+Limestone counties). Old: 100 turbines decommissioning early 2026. New: 63 turbines ~297 MW. Deep scan recommended.
T4: PUCT Interchange — HTTP 402. No IA filing retrieved.
T5: Ch.313 / JETI — No search accessible (post-2022 repeal). JETI 404. No abatement found.
T6: CDSE imagery — CDSE 401 Unauthorized. No chips obtained. Candidate site: ~31.54°N, -96.83°W (Prairie Hill Farm near Mart TX).
T7: Triage closed. Blockers: gmaps 429, PUCT 402, CDSE 401, FAA offline.

---

## Deep scan — 2026-07-19

### Stage 1 — LLC → parent chain

**S1-A: GLEIF LEI record**
- URL: https://api.gleif.org/api/v1/lei-records/254900B3TFPPM1COE679
- Date: 2026-07-19
- Result: PRAIRIE PHOENIX WIND PROJECT, LLC — ACTIVE Delaware LLC. HQ 1360 Post Oak Blvd Suite 400 Houston TX 77056. Prior names: "Roosevelt II Wind Project, LLC" → "Red Lake Wind Project, LLC". TX foreign registration June 25 2025 (tax ID 32100901506). Entity created 2013-10-01.
- Artifact: sources/2026-07-19_gleif_prairie-phoenix-wind-lei.json
- Why: Confirms ENGIE NA developer via shared HQ; LLC pipeline repurposing pattern consistent with ENGIE's existing TX assets.

**S1-B: KWTX news — Prairie Hill repower (Feb 2026)**
- URL: https://www.kwtx.com/2026/02/06/100-wind-turbines-be-taken-down-replaced-mart-texas/
- Result: ENGIE decommissioning 100 turbines at Prairie Hill Wind Farm (Mart TX, McLennan+Limestone counties). Replacing with 63 more efficient turbines, maintaining ~300 MW. ENGIE VP of Public Affairs: Julie Vitek.
- Artifact: sources/2026-07-19_kwtx_prairie-hill-repower-feb2026.html

**S1-C: KWTX news — Prairie Hill repower (Mar 2026)**
- URL: https://www.kwtx.com/2026/03/31/prairie-hill-wind-farm-replacement-project-continues-near-mart/
- Result: ~20% of turbines felled by late March 2026. Foundation removal starts late April 2026. Decommissioning completion: late Aug/early Sep 2026. New turbine installation: ~1 year after decommissioning = ~fall 2027. No mention of "Prairie Phoenix Wind" name.
- Artifact: sources/2026-07-19_kwtx_prairie-hill-repower-mar2026.html

**S1-D: TX Comptroller entity search**
- URL: https://mycpa.cpa.state.tx.us/coa/ — redirects to search page, automated fetch blocked.
- Query: "Prairie Phoenix Wind" — no result obtained.
- Negative evidence logged.

**S1-E: PPA / press release search**
- Queries: prnewswire.com, businesswire.com, sec.gov for "Prairie Phoenix Wind"
- Result: No dedicated press release found for Prairie Phoenix Wind. No PPA or EPC announced.
- Negative evidence logged.

**S1-F: FAA OE/AAA filings**
- URL: oeaaa.faa.gov
- Result: System offline (government shutdown). No turbine coordinates accessible.
- Negative evidence logged. DECISIVE GAP — turbine coord search must be reattempted when FAA system restored.

---

### Stage 2 — County records

**S2-A: PUCT Interchange filings**
- URL: https://interchange.puc.texas.gov/search/filings/ — text="Prairie Phoenix Wind"
- Result: HTTP 402 Payment Required. No IA retrieved.
- Negative evidence logged.

**S2-B: McLennan CAD parcel search**
- Not executed (portal blocked in this session; queue only 5 months old).
- Negative evidence logged.

**S2-C: Ch.313/JETI / abatement**
- Ch.313 program repealed post-2022; this is a 2026 entry — no Ch.313 expected.
- JETI: no search executed.
- Negative evidence logged (expected absence, not strong paper signal).

---

### Stage 3 — Site pinpoint

**S3-A: Google Places delivery-pin**
- HTTP 429 rate-limited. No pin obtained.
- Negative evidence logged.

**S3-B: POI inference**
- POI "3403 Lake Hall 345kV" — "Lake Hall" is an ERCOT 345 kV switching station.
- Prairie Hill Wind Farm (ENGIE, existing ~300 MW, near Mart TX) interconnects via similar McLennan County substations.
- Approximate area: 31.5–31.6°N, 96.8–96.9°W (Mart TX vicinity, McLennan County).
- Confidence: LOW. No independent coordinate from parcel, pin, or FAA filing.

---

### Stage 4 — Satellite imagery
- CDSE creds returned 401 in triage; not reattempted (budget constraint).
- No imagery chips acquired.
- Verdict: UNASSESSABLE from satellite in this session.

---

### Stage 5 — Queue history
- queue_history.py 27INR0607: 5 snapshots, 0 COD changes, no IA signed.
- Artifact: timeline.md, timeline.json

---

## Negative evidence count: 7
## Banned source violations: 0
