# Triage log — Ferdinand Grid BESS II (27INR0393)

## T1 start
**queue_history.py**: 19 snapshots (2024-12-01 → 2026-06-01)

### Milestone status
- Screening started: 2024-12-19
- Screening complete: 2025-03-04
- FIS requested: 2024-12-03
- FIS approved: **NOT achieved**
- IA signed: **NOT achieved**
- Meets 6.9(1): NOT achieved
- Meets all 6.9: NOT achieved
- Construction start/end: NOT achieved

### COD drift
- 2027-06-08 (held 2024-12-01 → 2026-05-01)
- 2027-12-01 (shifted 2026-06-01, 1 change)

**T1 result**: Early-stage project. Screening done, FIS in progress (requested not approved). No IA. One COD slip of ~6 months. No construction milestones.

---

## T2 start
**gmaps.py places**: HTTP 429 on first call, 429 on retry → blocked. No pins found.

**T2 result**: 0 pins. gmaps API rate-limited, tool unavailable this session.

---

## T3 start
**Web sweep findings:**
- infrasure.ai: developer listed as **Ambar Power Holdco LLC**, 208.12 MW, Bexar County, COD ~2027
- interconnection.fyi: owner listed as **Coval Infrastructure DevCo LLC** (may be parent/predecessor or name change)
- gridstatus.io: confirms queue entry
- Ferdinand Grid BESS **I** (22INR0422) also exists — separate earlier project in same county, IA already executed on BESS I
- Third DDG query hit CAPTCHA — no retry per rules
- No news/PR articles found specifically for BESS II

**T3 result**: Two developer name candidates (Ambar Power Holdco LLC / Coval Infrastructure DevCo LLC). BESS I predecessor confirms developer is active and has executed an IA for a related project. No press coverage for BESS II.

---

## T4 start
- PUCT Interchange direct URL: HTTP 402 both attempts → blocked
- DDG site: search repeatedly returning CAPTCHA — no results
- No IA PDF found for 27INR0393
- Note: BESS I (22INR0422) reportedly has IA executed per T3 sources — that is a different INR

**T4 result**: No IA found for 27INR0393 (BESS II). PUCT portal inaccessible via WebFetch. Normal finding given project has not yet reached FIS approval.

---

## T5 start
- TX Comptroller Ch.313 page: no searchable database for Ch.313 specifically (program expired 2023); no project-level data
- JETI registry URL (gov.texas.gov/grid/jeti): 404
- Post-2022 battery projects are NOT expected to have Ch.313 (expired); JETI is the replacement but URL not functional

**T5 result**: No abatement found. Normal — Ch.313 expired before this project entered the queue (2024). JETI registry inaccessible.

---

## T6 start
**Site candidate**: Leon Creek Switchyard (CPS Energy, 138kV transmission) found via OSM Overpass query.
- Coordinates: **29.3503°N, 98.5752°W** (Bexar County, SW San Antonio)
- Method: POI name "5260 Leon Creek 138kV" → OSM substation lookup
- Confidence: HIGH — named match, confirmed transmission-class switchyard

**Imagery**: cdse.py chip attempted at Leon Creek Switchyard (2026-07-01, buffer 1km).
- Result: HTTP 401 Unauthorized — CDSE credentials not available in this session.
- Contact sheet: not generated.

**T6 result**: Site candidate located with high confidence. No imagery available due to CDSE auth failure. No construction verdict possible from satellite.

---

## T7 start
Wrote triage_findings.json and triage.md. **Turns used: 27.** Run complete.

---

## DEEP SCAN — 2026-07-19

### Stage 1 — LLC → parent chain

**2026-07-19 — Bizapedia TX entity search**
- Query: bizapedia.com/tx/coval-infrastructure-devco-llc.html
- **FOUND**: Coval Infrastructure DevCo LLC, TX ID 0805845202, founded 2024-12-30
- Address: 11801 Domain Blvd Suite 450, Austin TX 78758
- Parent/member: AMBAR POWER DEVCO HOLDCO LLC
- Registered agent: CT Corporation System, 1999 Bryan St Suite 900, Dallas TX 75201
- Artifact: `sources/2026-07-19_bizapedia_coval-infrastructure-devco.html`

**2026-07-19 — Blackstone 10-K EX-21.1 (SEC EDGAR)**
- EDGAR full-text search "Ambar Power" → Blackstone Inc (BX) 10-K filed 2025-02-28
- **FOUND**: "BX Ambar Power 2 Aggregator GP L.L.C." Delaware in subsidiary list (EX-21.1)
- GP structure = Blackstone fund aggregator for energy investment
- Artifact: `sources/2026-07-19_sec_blackstone-ex211-subsidiaries.htm`

**2026-07-19 — AYPA Power confirmed as Blackstone platform**
- Yahoo search "Ambar Power Texas" → multiple AYPA Power links
- aypa.com confirms: "a Blackstone Portfolio Company", 33 projects N America
- TX projects include Wolf Tank BESS, Borden County BESS
- Artifact: `sources/2026-07-19_aypa-power_homepage.html`
- **Chain**: Ferdinand Grid BESS II LLC (SPV) → Coval Infrastructure DevCo LLC → Ambar Power DevCo Holdco LLC → AYPA Power → Blackstone (BX)

**Negative searches (Stage 1):**
- TX Comptroller: POST-gated, no results. TX SOS: JS-gated. OpenCorporates: 0 hits all entities. LinkedIn: no page. ambarpower.com: no response.

---

### Stage 2 — County records

**PUCT Interchange**: React/JS-gated — no IA filing found for 27INR0393 (expected: IA not signed per queue).
**BESS I companion (22INR0422)**: IA signed 2022-11-28; **Commercial Operation Approved 2026-06-09** — ONLINE. Same POI. Developer has executed. COD slipped 3x (~3 years total). Artifact: `sources/bess1_timeline.md/timeline.md`.
**Abatements/CAD**: None found — Ch.313 expired 2022; likely on CPS Energy land.

---

### Stage 3 — Site pinpoint

**OSM Overpass confirmed**: Leon Creek Switchyard, OSM way 317830185, CPS Energy 138kV transmission, bounds 29.3494–29.3512°N / 98.5761–98.5742°W, centroid **29.3503, -98.5752**. Adjacent to Leon Creek Power Plant (EIA-860 ref 3609, 7718 Quintana Rd). Artifact: `sources/2026-07-19_osm_leon-creek-switchyard.json`.
**Confidence: HIGH** — exact POI name match; BESS I at same POI is now online.

---

### Stage 4 — Satellite imagery

- 1km chip 2026-07-01: existing CPS Energy complex; BESS I now operational (online Jun 2026), pads not distinguishable from utility infrastructure at this resolution.
- 1km chip 2025-07-01: some brown/graded areas visible near power plant (BESS I under construction at that time, IA signed 2022).
- 3km / 0.5km chips also retrieved (see imagery/).
- CDSE 401 on later requests; no timelapse obtained.
- **Verdict: no_new_activity** — BESS II has no IA signed, no construction milestones; existing BESS I pad may be visible but indistinct at 10m/px.

---

### Stage 5 — Synthesis

- Verdict: **real_early** — institutional developer (AYPA/Blackstone), confirmed POI, companion BESS I online
- FIS pending 18+ months (requested Dec 2024, still not approved Jun 2026) = critical bottleneck
- Reported COD 2027-12-01 not achievable without FIS approval imminent
- BESS I 3-year slip precedent; independent estimate: **2028-Q4**, drift risk **HIGH**

