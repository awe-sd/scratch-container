# Research log — Skull Creek Solar (23INR0289)

T1 start

**T1 — Queue history**
- 55 monthly snapshots (2021-12-01 → 2026-06-01)
- Milestones achieved: Screening started 2021-05-28, Screening complete 2021-08-19, FIS requested 2021-12-16, IA signed 2024-05-20
- Milestones NOT achieved: FIS approved, Meets 6.9(1), Meets all 6.9, Construction start/end, energization/sync/COD approvals
- COD drift: 5 changes — 2024-06-01 → 2025-07-01 → 2025-09-16 → 2026-09-16 → 2027-05-16 → 2027-07-30 (current)
- ~36-month total slip from original 2024-06-01 target
- Capacity stable ~136-137 MW throughout; slight tweaks (124.74 → 136.08 → 136.76 → 137.26 → 136.98)
- IA signed May 2024 is a meaningful milestone — project has cleared interconnection agreement stage
- No 6.9 milestones → not yet in notice-to-proceed / full engineering phase
- T1 complete

T2 start

**T2 — Delivery pins**
- gmaps.py returning HTTP 429 (rate limited) on all queries — blocked after 1 retry per rules
- No pins found
- T2 complete (blocked)

T3 start

**T3 — Web sweep**
- Developer identified: Zelestra (Spanish renewables company)
- SPV confirmed: Skull Creek Solar, LLC
- PPA: Meta (long-term, full output, for data centers) — announced but Zelestra site 403
- Capacity: 176 MWdc / ~137 MW AC (confirms queue figure)
- Location: Anderson County TX confirmed
- Expected COD from PPA coverage: ~May 2027 (aligns with current queue 2027-07-30)
- PUCT IA PDF found: interchange.puc.texas.gov/Documents/35077_1848_1400681.PDF
- PUCT IA Amendment No. 3 found (executed 2025-10-13): interchange.puc.texas.gov/Documents/35077_2290_1554235.PDF
- Saved to sources/web_sweep_t3.md
- T3 complete (news_found = true, developer = Zelestra, offtaker = Meta)

T4 start

**T4 — PUCT Interchange**
- IA PDF URLs identified in T3: 35077_1848_1400681.PDF (original IA) and 35077_2290_1554235.PDF (Amendment No. 3, 2025-10-13)
- Both direct PDF URLs return HTTP 402 (payment/auth required)
- PUCT interchange portal also 402
- DRIFT NOTE: IA exists (confirmed via T3 search snippets), docket appears to be 35077
- ia_found = TRUE (confirmed via search engine snippet — "ERCOT Standard Generation Interconnection Agreement for SKULL CREEK SOLAR GINR 23INR0289")
- Amendment No. 3 executed 2025-10-13 (Oncor + Skull Creek Solar LLC) — schedule likely revised
- Cannot download PDFs; milestone schedule content unknown
- T4 complete (IA confirmed, PDFs inaccessible)

T5 start

**T5 — Abatements**
- TX Comptroller Ch.313 pages all return overview/navigation content, no data tables accessible via WebFetch
- JETI page similarly inaccessible
- No Ch.313 or JETI record found for Anderson County / Skull Creek Solar / Zelestra
- Normal for post-2022 projects (Ch.313 expired Dec 2022); JETI is new and registry sparsely populated
- abatement_found = false
- T5 complete (portal data not accessible, no record found)

T6 start

**T6 — Imagery**
- Site candidate: Tennessee Colony area (POI: "Tap 138kV Tennessee Colony - Blackfoot Massey Lake Switch"), center estimate 31.84°N, 95.90°W
- infrasure.ai: groundbreaking March 2026, McCarthy EPC — construction active as of T3
- cdse.py 3×3 grid chips at current date (2026-06-01): ALL returned HTTP 401/403 — CDSE credentials not valid/loaded
- construction_visible = unknown (imagery blocked)
- T6 complete (credentials absent, no contact sheet produced)

T7 start

**T7 — Write and stop**
- triage_findings.json written
- triage.md written (10 lines)
- Turns used: ~22
- T7 complete — STOP
