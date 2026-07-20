# Triage log — 20INR0083 Baird North Wind

T1 start

## T1 — Queue history
- 95 snapshots (2018-08-01 → 2026-06-01); 11 reported-COD changes
- IA signed: 2019-05-31 | FIS approved: 2020-10-30
- Approved for energization: 2021-08-09 | Approved for synchronization: 2021-08-20
- Commercial operation approved: NOT YET (still in queue)
- Construction start/end: not reported in queue data
- COD drift: 2020-12-15 → 2021-06-15 → 2021-07-15 → 2021-09-30 → 2021-10-23 → 2021-12-10 → 2022-02-10 → 2022-12-01 → 2023-04-01 → 2023-10-31 → 2025-12-31 → 2026-12-31 (current)
- Capacity: 278 → 300.3 → 293.55 → 331.2 → 350.0 → 340.0 (current)
- NOTE: Approved for sync but NOT commercial operation — unusual; project is deep in queue with all milestones except COD

T2 start

## T2 — Delivery pins
- gmaps.py places: HTTP 429 on all 2 attempts (rate-limited). Budget exhausted.
- Result: 0 pins found (blocked portal, not a negative signal about the project)

T3 start

## T3 — Web sweep
- DDG: CAPTCHA blocked (one retry — still blocked)
- Bing "Baird North Wind" + wind farm Texas: no results, all hits were R.W. Baird financial firm
- Bing "Baird North Wind" LLC ERCOT: no results
- Bing Callahan County 340 MW wind 2026: no results
- Result: 0 news/PR hits, no developer name surfaced, no LLC registration found
- Project has very low web footprint — consistent with a stalled or private-stage project

T4 start

## T4 — PUCT Interchange
- interchange.puc.texas.gov: HTTP 402 on all URL patterns (portal blocked — not authenticated)
- Bing searches for "Baird North Wind" + PUCT/docket/IA: no results surfaced
- Queue data confirms IA signed 2019-05-31 — IA EXISTS but PDF not retrieved
- No milestone schedule exhibit obtained
- Result: IA existence confirmed via queue data; content/schedule blocked

T5 start

## T5 — Abatements
- TX Comptroller Ch.313 pages: navigation pages only, no searchable list accessible via WebFetch
- Bing search for Callahan County Ch.313 wind abatement: no results
- Project entered queue 2018 (pre-2022), so Ch.313 was available and could have been filed
- JETI: N/A (pre-2022 project, Ch.313 was the relevant vehicle)
- Result: No abatement found — inconclusive (portal not accessible, not a confirmed negative)

T6 start

## T6 — Imagery
- Site candidate: thewindpower.net gave lat 32°27'13.5"N / lon 99°26'50.5"W (= 32.4538, -99.4474) for Mesquite Sky wind farm (same project)
  — confidence: HIGH (named source, matches Callahan County)
- Also discovered: project name "Mesquite Sky", developer/owner Clearway Energy, BMP Wind LLC
  — web source claims "began commercial operation 11/30/2021"
- Sentinel-2 chip downloaded: 2026-07-01 ±15d, 4km buffer
- Imagery verdict: EXISTING OPERATIONAL WIND FARM VISIBLE
  — extensive systematic access road network covering ~tens of km²
  — numerous small white features (turbine pads) distributed across road network
  — no fresh grading or active construction visible; infrastructure appears mature
  — consistent with a completed/operational facility, NOT active construction of new phase
- Construction signal for NEW capacity: NEGATIVE (no visible ground disturbance)
- Key question raised: is 20INR0083 the original project (now operational) or an expansion?
  Queue shows approved-for-sync 2021-08-20 but no commercial-operation-approved date — discrepancy with web claim of COD 11/30/2021

T7 start

## T7 — Output
- triage_findings.json written
- triage.md written (9 lines)
- Turns used: ~22
- Run complete.

## Deep Scan — T1 — Corporate Chain (Stage 1)
- Sources: SEC EDGAR full-text search "Mesquite Sky", "BMP Wind"
- CONFIRMED: 20INR0083 (Baird North Wind / BMP Wind LLC) = Mesquite Sky wind project
  - BMP Wind LLC = Project Company (holds ERCOT queue slot)
  - BMP Wind LLC ← Mesquite Sky TE Holdco LLC (tax equity fund) ← Mesquite Sky Holding LLC ← Clearway Energy / Lighthouse Renewable Class A LLC
  - Seller: Clearway Renew LLC (subsidiary of Clearway Energy Group LLC)
  - Source: SEC 8-K (2022-01-18) — First Amendment to Mesquite Sky MIPA
    sources/2022-01-18_sec_clearway_8k_mesquite-sky-mipa-amend1.htm
  - Source: MIPA original (2020-12-22): "BMP Wind LLC is the Project Company"
    sources/2020-12-22_sec_clearway_ex10-3_mesquite-sky-mipa-original.htm
- Chain: BMP Wind LLC → Mesquite Sky Holding LLC → Clearway Energy Inc. / Lighthouse Renewable (50% Class B interests)
- Cost: $62M (Class B) + $2.4M (Class A) for 50.01% interests; Class A owned by third-party investor

## Deep Scan — T2 — COD confirmation (Stage 2)
- Clearway 10-K FY2021 (filed 2022-02-28): "340 MW utility scale wind project located in Callahan County, Texas, which achieved commercial operations in December 2021"
  - Footnote: "14 of 23 turbines operational by Dec 31, 2021; remaining 45 MW (9 turbines) operational January 2022"
  - Full COD: January 2022
  - Source: sources/2022-02-28_sec_clearway_10k_2021_cwen.htm
- Clearway 10-K FY2025 (filed 2026-02-24): Mesquite Sky still in operating portfolio
  - 340 MW, 50% ownership, December 2021 COD, PPAs through 2033-2036
  - Source: sources/2026-02-24_sec_clearway_10k_2025_cwen.htm
- Turbine count: 23 turbines × ~14.8 MW avg = 340 MW total

## Deep Scan — T3 — PUCT/FAA/CAD
- PUCT Interchange: paywalled (HTTP 402) — IA content not retrieved
- FAA OE/AAA: search form returned 404; portal appears down/changed endpoint
- Callahan CAD: renders via JS — static fetch returns no property data
- SEC filings ZERO hits for "Baird North Wind" — confirms ERCOT used BMP Wind LLC as queue entity name

## Deep Scan — T4 — ERCOT Queue Stale Entry Analysis
- Timeline: IA signed 2019-05-31; approved-for-energization 2021-08-09; approved-for-sync 2021-08-20
- Commercial-operation-approved: NOT YET per ERCOT queue (still showing 2026-12-31 COD)
- COD drift: 12 changes, 2020-12-15 → 2026-12-31 — extreme drift pattern; last change 2025-12-01
- Assessment: The ERCOT queue entry is an orphaned/stale record. The project (Mesquite Sky) 
  was physically operational in January 2022 but ERCOT never issued the commercial-operation-approved 
  milestone. This is consistent with a prolonged administrative/settlement dispute or data error.
  The queue COD of 2026-12-31 is administratively maintained, not reflecting physical reality.

## Deep Scan — T5 — Satellite Stage 4
- Site candidate: 32.4538, -99.4474 (from thewindpower.net Mesquite Sky listing, HIGH confidence)
- Sentinel-2 imagery:
  - 2020-06: Pre-construction — undisturbed farmland/pasture, NO roads or pads (baseline)
    imagery/key/s2_2020-06_preconstruction.png
  - 2021-06: ACTIVE CONSTRUCTION — extensive new access road network + ~20 turbine pads visible
    as bright orange/tan circles connected by roads; construction activity confirmed
    imagery/key/s2_2021-06_construction-active.png
  - 2026-07: OPERATIONAL — mature road network, turbines visible (bases/shadows), no fresh disturbance
    imagery/key/s2_2026-07_operational.png
- Construction timeline from imagery: first activity BEFORE June 2021; fully operational by 2022
- Matches SEC-confirmed COD: December 2021 (14/23 turbines) / January 2022 (all 23 turbines)
- Site center approx: 32.45, -99.45 (triage candidate confirmed consistent with imagery)
- gmaps.py staticmap: HTTP 403 (Maps Static API not enabled) — map not generated

## Deep Scan — T6 — Stage 5 Synthesis
- findings.json written
- dossier.md written
- queue_history.py run: 95 snapshots, 11 COD changes
- build_brief.py run: brief.html written (7 KB, 3 images, 12 sources)
- build_index.py run: 46 projects indexed
- VERDICT: real_active — project operational since January 2022; queue entry stale/orphaned
