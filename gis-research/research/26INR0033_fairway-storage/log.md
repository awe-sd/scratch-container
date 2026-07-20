# Triage log — 26INR0033 Fairway Storage

**Project:** Fairway Storage  
**INR:** 26INR0033  
**County:** Freestone, TX  
**Capacity:** 120.3 MW BESS  
**COD (claimed):** 2027-09-24  
**Date:** 2026-07-19  

---

T1 start
**Result:** 41 snapshots (2023-02 → 2026-06). IA signed 2025-08-11. Meets 6.9(1) 2026-03-09. No FIS approved, no construction dates, no energization/sync/COD approvals. COD drifted 5x: 2026-04-30 → 2026-06-29 → 2026-05-31 → 2026-06-29 → 2027-02-03 → 2027-09-24 (~17-month total slip). Capacity trimmed 121.03→120.3 MW at 2025-05.

T2 start
**Result:** gmaps.py returned HTTP 429 on first call; retry also 429. No pins found. Normal — BESS site may not be a named place. Budget exhausted.

T3 start
**Result:** Developer identified — Nofar USA Energy Texas LLC (sole member/manager of Fairway Storage LLC); parent OY Nofar Energy (Israeli). EPC partner Qcells USA (Hanwha Qcells). Part of 350 MW / 700 MWh two-project Texas BESS deal (Fairway + Bracero Pecan). Described as "final steps of interconnection approvals" at announcement. PUCT IA filing found: Oncor + Fairway Storage LLC (doc 35077_2254_1537453). Qcells press release URL returned 404. Saved to sources/t3_web_sweep.md.

T4 start
**Result:** PUCT interchange portal (interchange.puc.texas.gov) returned HTTP 402 on all attempts — filing search, application page, and direct PDF URL. IA existence confirmed from T3 DDG search (doc 35077_2254_1537453, Oncor + Fairway Storage LLC) but PDF content not retrievable during triage. ia_found = TRUE (from T3 evidence), schedule exhibit not extracted.

T5 start
**Result:** Ch.313 expired 2022 — project entered queue 2022-11, so Ch.313 ineligible. JETI (HB5) portal not web-searchable via public URL. No abatement found. Normal for this vintage. abatement_found = FALSE.

T6 start
**Site candidate:** Fairfield, TX (31.7241°N, 96.1552°W) — inferred from POI "196 FAIRFIELD" on Oncor 138kV system; Freestone County seat. No precise substation coords found (DDG returned nothing). CDSE cdse.py returned HTTP 403/401 on all 9 grid chip calls — CDSE credentials invalid/expired. No imagery obtained. construction_visible = FALSE (not assessed). 

T7 start — wrote triage_findings.json + triage.md. Turns used: ~28. STOP.
