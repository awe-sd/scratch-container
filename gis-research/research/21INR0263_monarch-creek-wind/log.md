# Triage log — Monarch Creek Wind (21INR0263)

## T1 start
**queue_history.py output:** 83 snapshots, 9 reported-COD changes.

**Key milestones:**
- Screening started: 2019-04-25 | complete: 2019-07-19
- IA signed: 2020-08-24 (early, pre-FIS — unusual)
- FIS requested: 2019-08-05 | FIS approved: 2025-11-05 (6+ year gap)
- Meets 6.9(1): 2025-12-22 | Meets all 6.9: 2026-01-26
- Construction start/end: NOT reported
- COD drift: 9 changes, from 2021-10-01 → 2027-09-17 (6-year total slip)

**Capacity history:** wildly variable — 350→209→351→344→279→287→284→283.4 MW (current)

**Assessment:** Active in queue, all pre-COD gates cleared as of Jan 2026, but no construction milestone yet. Significant COD drift; current COD 2027-09-17 is the 10th reported value.

## T2 start
**T2 result:** gmaps.py returning HTTP 429 (rate-limited) on all calls. No pins found. 0 delivery pins.

## T3 start
**T3 result:**
- DDG CAPTCHA blocked first query; no retry attempted per rules.
- LLC search returned: Monarch Creek Wind LLC filed as FOREIGN LLC in TX on 2022-05-12 (formerly "King Creek Wind Farm 3 LLC"). Registry 0804576895, tax ID 32084663247. Status: Active.
- Ch.313 agreement with Throckmorton ISD exists (Comptroller ID 1807) — filed Dec 2022.
- EWG self-cert Feb 2025 (FERC). 288 MW, ERCOT WEST, expected 2027.
- Developer/parent company: not identified in web sweep; LLC is a foreign entity (formed out of state). Parent unknown — no press releases or developer attribution found.
- AKA "King Creek Wind Farm 3 LLC" is a strong alternate name for T4 searches.
- No news/press releases about construction or financing found.
- Sources: DuckDuckGo search results (no pages saved — no direct project pages found to fetch).

## T4 start
**T4 result:**
- PUCT Control Number: 35077
- Item 1138 (2020-08-28): Interconnection Agreement between Oncor Electric Delivery Co LLC and Monarch Creek Wind — 2 documents
- Item 2355: Amendment No. 2 to Standard Generation Interconnection Agreement (Oncor / Monarch Creek Wind)
- Additional item 1877: Amended and Restated SGIA between Oncor and Monarch Creek Wind
- PUCT Interchange portal returns HTTP 402 (auth required) on all document URL attempts — PDFs not downloadable during triage.
- POI: Oncor network (consistent with "Coody Crossing Switch 345kV" POI description).
- IA is confirmed to EXIST. Party pages and milestone schedule NOT retrieved due to portal block.

## T5 start
**T5 result:**
- Ch.313 agreement found: Comptroller ID 1807, applicant King Creek Wind Farm 3 LLC (→ Monarch Creek Wind LLC), Throckmorton CISD.
- Application filed Apr 2022; original agreement signed Dec 2022; amended twice (Mar 2025, Aug 2025).
- Project: 58 × 6.0 MW turbines = 350 MW (application figure; queue now 283.4 MW). Throckmorton County, entirely within Throckmorton CISD.
- Developer confirmed: EDF Renewables (Matthew McCluskey VP; Todd Eagleston Project Dev Mgr).
- Value limitation start: Jan 1, 2028 (qualifying period start Jan 1, 2026).
- Preliminary turbine layout map (TAB 11 in app) shows project area near Haskell/Throckmorton county border — no extractable coordinates from embedded image.
- JETI: not checked (Ch.313 found; post-2022 JETI check not needed per checklist rule).
- NOTE: Ch.313 data found during T3/T4 PDF retrieval, formally logged here.

## T6 start
Site candidate derivation: Ch.313 app map shows project near Haskell-Throckmorton county border (northern Throckmorton County). Using estimated centroid ~33.38°N, 99.2°W (near Haskell/Throckmorton border) as starting point — confidence LOW. POI "Coody Crossing Switch" location unknown; no pin from T2.
**T6 result:** SKIPPED imagery — budget warning at 88% (88,748/100,000 tokens). Site candidate is county-level only (northern Throckmorton Co near Haskell border, ~33.2°N 99.2°W, LOW confidence). No pin from T2, no extractable coordinates from Ch.313 map image. Per checklist: skip imagery when confidence is low + budget pressure.

## T7 start
**T7 result:** triage_findings.json + triage.md written. Turns used: ~28. Run complete.

## Deep scan — 2026-07-19

### D1 — FAA OE/AAA turbine filings (DECISIVE)
**Result:** 86 turbine obstruction evaluation filings found: ASNs 2024-WTW-8086-OE through 2024-WTW-8171-OE. Filed 2024-08-05. All "No Hazard" determination. 66 primary + 20 alternate positions. AGL height 599 ft. Counties: Throckmorton (49) / Haskell (37). Site centroid: 33.20938, -99.46218. Bounding box 12 km E-W × 6 km N-S.
**Why it matters:** FAA turbine filings give exact turbine coordinates — highest-confidence site pinpoint for wind; confirms both county extent and turbine count order of magnitude.
**Artifact:** sources/2026-07-19_faa_oe_aaa_turbine-filings.json

### D2 — PUCT Interchange IA documents
**Result:** All puc.texas.gov subdomains blocked — HTTP 402 Payment Required at network level. No document content, milestone schedule, or financial security amounts retrieved.
**Why it matters:** Negative — contractual COD commitment date unverified from this environment.

### D3 — Imagery (3 chips at FAA centroid)
**2024-07-01:** Undisturbed rangeland baseline. No pads, no roads.
**2026-01-01:** Still undisturbed — construction had not started as of January 2026.
**2026-06-15:** Active construction visible — extensive graded turbine pad network + branching access roads across full project footprint (~12 km E-W). Classic wind farm civil works pattern.
**Construction stage: clearing/civil works.** First activity: between 2026-01 and 2026-06.
**Why it matters:** Confirms active construction underway; brackets construction start to 2026-Q1/Q2.
**Artifacts:** imagery/key/s2_2024-07-01_baseline.png, imagery/key/s2_2026-01-01.png, imagery/key/s2_2026-06-15_latest.png

### D4 — EDF press releases / financing
**Result:** No press release found during triage or deep scan. FERC EWG self-cert Feb 2025 (288 MW, ERCOT WEST) found during triage. Financing status unknown.
**Why it matters:** Negative — no offtake/financing announcement; construction underway suggests deal may have closed without public announcement.

### D5 — Synthesis
Verdict: real_active. Site confirmed via FAA filings + imagery. Construction stage: civil works. COD estimate: 2027-Q4, drift risk high (9 prior slips + no tower erection visible yet).
