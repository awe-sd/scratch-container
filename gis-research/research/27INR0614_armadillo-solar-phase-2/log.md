# Triage log — Armadillo Solar Phase 2 (27INR0614)

## T1 start
- queue_history.py run: 1 snapshot (2026-06-01 only)
- COD drift: 0 changes; 2027-03-04 held in single snapshot
- Milestones: FIS requested 2026-06-26; all others (screening, FIS approved, IA signed, construction) = null
- Early-stage project: no IA, no construction milestones
- T1 complete

## T2 start
- gmaps.py places: HTTP 429 on initial attempt; 429 on retry — tool rate-limited, no pins retrieved
- 0 delivery pins found
- T2 complete (negative, tool blocked)

## T3 start
- DDG search "Armadillo Solar Phase 2 Navarro Texas solar project": found CleanView.co (201 MW, 2027), AES.com page (204 MW, 8mi SE Corsicana, near Navarro/Mildred/Eureka), Navarro County Chronicle article (construction Spring 2025 — appears to be Phase 1 / original project)
- Developer: AES Corporation; prior developer/owner: Ørsted Onshore North America LLC (2020 origin, transitioned to AES ~2024)
- AES page: 2,000 acres, 204 MW, COD target 2027, no Phase 1 vs Phase 2 distinction explicitly stated
- Chronicle article: "Armadillo Solar" (no Phase 2) — Spring 2025 construction start, Winter 2026 COD — likely Phase 1
- 27INR0614 appears to be Phase 2, separate queue entry from Phase 1
- Source saved: sources/t3_aes_project_page.md
- T3 complete

## T4 start
- interchange.puc.texas.gov: HTTP 402 on all attempts (FilingSearch, Default.aspx, alternate URL) — portal blocked in this environment
- No IA document retrieved; IA status per queue = not yet signed (iaSigned = null in T1)
- T4 complete (negative, portal blocked)

## T5 start
- TX Comptroller Ch.313 page: no searchable database on the page itself; no downloadable list accessible via WebFetch
- DDG search "Navarro County Armadillo Solar Chapter 313 OR tax abatement OR JETI": no results
- No abatement found for Phase 2 (27INR0614); Ch.313 program ended 2022, so a 2027-COD project filing post-2022 would go through JETI instead
- Note: Phase 1 (original Armadillo Solar, Ørsted origin ~2020) may have a Ch.313 agreement — not verified in this triage
- T5 complete (negative for Phase 2)

## T6 start
- Site candidate from T3: ~32.035°N, -96.377°W (Mildred, TX area) — 8 mi SE of Corsicana per AES description; confidence: medium
- cdse.py chips attempt: HTTP 401 Unauthorized — ~/.config/gis-research.env contains only example placeholder, real CDSE credentials not configured
- Imagery SKIPPED — credentials unavailable; 401 = hard blocker, not retriable within triage rules
- T6 complete (negative, credentials not configured)

## T7 start
- triage_findings.json written
- triage.md written (10 lines)
- Turns used: 22
- T7 complete — STOP
# Deep scan log — Armadillo Solar Phase 2 (27INR0614) — 2026-07-23

## D0: read triage_findings.json, triage.md, factsheet.json, log.md, inventoried sources/ (1 file: t3_aes_project_page.md)
- No prior deep-scan artifacts existed. findings.json skeleton written.

## D1: systematic SPV ladder
- puct.py match 27INR0614 --dir sources/ → 0 candidates by exact name key (no rung-0 INR-join hit, no name-key hit)
- spv.py resolve 27INR0614 → no systematic candidate (not in EIA-860M, no docket-index party match)
- ch313.py resolve 27INR0614 [+ --county Navarro, --name armadillo] → NEGATIVE — no Ch.313/JETI match
- ch312.py resolve 27INR0614 [+ --county Navarro, --name armadillo, --name AES] → 42 county-only candidates, 0 by name (all unrelated Corsicana city abatements — Pactiv, Russell Stover, etc.) — WEAK negative evidence
- minutes.py resolve 27INR0614 / --name "Armadillo Solar" --county Navarro → Navarro county NOT YET HARVESTED (0 indexed files); ran `minutes.py harvest --county Navarro` → 0 candidate links, 0 new PDFs found (county's minutes portal returned nothing crawlable)
- **tceq.py resolve --county Navarro --keyword Armadillo --storm → HIT.** Facility "ARMADILLO SOLAR PROJECT" [ACTIVE], 3 storm permits (TXR1511RP, TXR1538TO, TXR1543QE). Owners: **Armadillo Solar Center, LLC**, **Hanwha Q Cells EPC USA LLC** (EPC), **The AES Corporation**.
  - Direct API query (data.texas.gov t34q-qzi3, Dallas/Fort Worth region table) resolved TWO regulated entities under near-identical names/location:
    - RN111934428: owner "The AES Corporation", permit TXR1543QE, CANCELLED, affil begin 2024-03-08, site desc "NEAR THE INTERSECTION OF STATE HIGHWAY 287 AND SE COUNTY ROAD 2040 BETWEEN THE CITIES OF MILDRED AND NAVARRO, TX"
    - RN112015482: owners "Armadillo Solar Center, LLC" + "Hanwha Q Cells EPC USA LLC", permits TXR1511RP (CANCELLED, begin 2024-07-25) and **TXR1538TO (ACTIVE, Hanwha affil begin 2025-02-07)**, site desc "SOUTH OF THE INTERSECTION OF STATE HIGHWAY 287 AND SE COUNTY ROAD 2040 BETWEEN THE CITIES OF MILDRED AND NAVARRO TX"
  - Interpretation: AES's own construction-stormwater NOI (2024-03, cancelled) was superseded by the project-entity SPV "Armadillo Solar Center, LLC" NOI (2024-07, cancelled — likely re-registration) then the CURRENT ACTIVE coverage TXR1538TO with EPC Hanwha Q Cells on board since 2025-02-07. This is an ACTIVE construction-stormwater registration = dirt-moving evidence per playbook.
  - SPV confirmed (via TCEQ Central Registry, primary doc, not a banned aggregator): **Armadillo Solar Center, LLC**

## D1 continued: IA documents fetched via puct.py match --key "Armadillo Solar Center"
- 4 filings found: original IA (35077-1230, 2021-02-02) + Amendments 5,6,7 (2024-2025) — ALL are for **21INR0421 "Armadillo Solar"** (= Phase 1), NOT 27INR0614 (Phase 2). This is the KEY disambiguation: Phase 1 and Phase 2 are genuinely separate ERCOT queue entries at the same site/POI.
- Phase 1 IA facts (sources/2026-07-23_puct_35077-1230_*.pdf + amendments):
  - Parties: Oncor Electric Delivery Company LLC (TSP) + Armadillo Solar Center, LLC (Generator)
  - POI (Exhibit C, original IA p31): "Revolution Switch at 138kV... located adjacent to TSP's existing 69kV Navarro Sub on Main St in the town of Navarro in Navarro County, Texas" — MATCHES target 27INR0614's POI text "3387 Revolution 138kV" almost exactly (same substation, "Revolution")
  - Original capacity: 270 inverters, 226.8 MVA gross, 204 MW net plant / 200 MW at POI (TMEIC PCS-840 inverters)
  - Amendment 7 (2025-10-31) capacity update: 57 inverters, 231.85 MVA gross, 202.6 MW at generator terminals / 200.03 MW at 34.5kV bus (SMA SC4400-UP-US inverters) — inverter technology/count changed (270 TMEIC → 57 SMA), same net MW
  - Schedule drift across amendments (all for 21INR0421):
    - Original (2021): In-Service 2022-11-17, Trial Op 2022-11-27, **COD 2022-12-31**
    - Amendment 5 (2024-08-14): In-Service 2025-12-04, Trial Op 2026-07-01, **COD 2026-12-31** (4-year slip)
    - Amendment 6 (2025-08-01): In-Service 2026-04-16, Trial Op 2026-07-01, **COD 2026-12-31** (unchanged COD, In-Service pushed later)
    - Amendment 7 (2025-10-31): In-Service 2026-04-16, Trial Op 2026-06-01 (pulled earlier), **COD 2026-12-31** (unchanged)
  - Financial security (Amendment 5, Exhibit E): LC schedule $4,086,825 (2021-02-08) → $9,081,832 (2022-02-14) → $10,833,691 (2024-12-04)
  - Generator notice address: Armadillo Solar Center, LLC, Attn Asset Mgmt/Interconnection, 282 Century Place Ste 2000, Louisville CO 80027 — AES's Colorado address (acedlegalnotices@aes.com etc.) — confirms AES = current owner/operator of Phase 1 SPV
- **Interpretation for 27INR0614 (Phase 2):** Phase 1 (21INR0421) is a REAL, actively-progressing 200MW project at the same POI/substation, now in final construction stage (In-Service Apr 2026, Trial Op Jun 2026, COD Dec 2026 per its own Amendment 7), operated by AES via the same "Armadillo Solar Center, LLC" SPV shell. Phase 2 (our target, 200.71 MW) has NOT yet signed its own IA (confirmed — 0 IA candidates found under "Armadillo Solar Phase 2" queue name; all 4 IA filings found are captioned 21INR0421). Phase 2 is credibly a real expansion phase riding the same interconnection point/substation as an already-under-construction Phase 1, but it individually has NOT reached IA execution — this is the single most decisive risk factor for the 2027-03-04 claim.

## D2/D3: news search + Navarro County ROW agreement (primary document, map artifact)
- search.py "Armadillo Solar Phase 2 Navarro County AES" → hits: thenavcochronicle.com article, gem.wiki/Armadillo_Solar_Center, Facebook page, Orsted PPA press release, **Navarro County ROW agreement PDF** (navarro.easydocs.us — county's own document server, primary source)
- Downloaded sources/2026-07-23_navarrocounty_row-agreement-armadillo-solar.pdf (6 pages) — Road and Right-of-Way Agreement, Navarro County Commissioners' Court + Armadillo Solar Center, LLC, effective 2021-10-08
  - Company at signing: "Armadillo Solar Center, LLC, a Delaware LLC" — sole member chain: Orsted Onshore DevCo, LLC -> Orsted Onshore North America, LLC (pre-AES acquisition ownership, confirms triage's Orsted->AES transition note)
  - Signed by Philip Moore, SVP, Orsted Onshore North America
  - Exhibit (p6): "Armadillo Solar / Navarro County, TX / August 2021" project-area map — shows the "Armadillo Project Area" boundary as **TWO distinct adjoining polygons** (a western parcel cluster along SE CR 1090/2050/2060 and an eastern parcel cluster along SE CR 2070/2080/2090/2100), both within one overall boundary bordered by SE CR 2040 to the north. 8.91 total miles of adjacent county roads (2040,2050,2060,2070,2080,2090,2100,1090).
  - Extracted map: sources/armadillo_row_p6_map.png (added to site.map_artifacts)
  - **This two-polygon shape directly matches the TWO graded/racked clusters visible in Sentinel-2 imagery (imagery/s2_2026-07-20_xwide.png) — strong evidence the WEST cluster = Phase 1 (21INR0421, IA-confirmed, under construction per Amendment 7 schedule) and the EAST cluster = Phase 2 (27INR0614, our target) is the OTHER polygon within the same original 2021 project-area boundary, now also showing grading/racking-stage construction activity.**
- gem.wiki/Armadillo_Solar_Center noted as a candidate secondary source — NOT fetched (not a banned queue-tracker but adds no primary evidence beyond what's already confirmed; skipped to conserve budget)

## D3 continued: Corsicana Daily Sun 2020 article + Ch.313 cross-check
- Downloaded sources/2026-07-23_corsicanadailysun_solar-center-planned.html (2020-11-02, "Solar Center planned for Navarro County")
  - Combined project (pre-split): 200 MW, **2,300 acres**, ~1 mile N of Mildred High School on Hwy 287
  - Reinvestment zone (Ch.313-track) approved by Commissioners Court June 2020; includes leased land from **6 property owners** in Mildred ISD
  - Mildred ISD board unanimously approved letting Mildred ISD apply for a Ch.313 "appraised value limitation agreement" Sept 2020 (per article's decoded ROT13-style garbled text — county+district process, not yet an executed agreement per the article's own wording: "second step in a three-step process")
  - Orsted Onshore quote (Matthew Crosby, Dir. Policy & Regulatory Affairs): "construction of the solar farm is on track to begin in 2022, with energy production expected to go online the following year [2023]" — this is the ORIGINAL COD target, badly missed (Phase 1's actual current schedule per Amendment 7 is COD 2026-12-31, a 3+ year slip from the 2020 public statement)
  - >600,000 solar panels planned, 440,000 MWh/yr, ~24,500 homes powered
- Checked data/reference/ch313_agreements.json (740 rows) directly for 'Mildred' district or 'Armadillo'/'Orsted' applicant — **0 matches**. Mildred ISD does not appear in the Ch.313 registry at all. Combined with ch313.py resolve negative and JETI absence: the Sept-2020 Mildred ISD board vote to "apply" for a Ch.313 value-limitation agreement APPARENTLY NEVER RESULTED IN AN EXECUTED AGREEMENT (or the agreement predates/postdates the registry's coverage under an unrecognized name) — recorded as negative evidence, moderately strong since Ch.313 registry is meant to be comprehensive for executed agreements pre-2023.

## D2/D3: Navarro County Ch.312 Tax Abatement Agreement (2020-11-09) — PRIMARY DOC, ch312.py registry MISS confirmed as weak-negative-evidence case
- Downloaded sources/2026-07-23_navarrocounty_tax-abatement-armadillo-solar.pdf (43 pages) — executed Chapter 312 Tax Abatement Agreement, Navarro County + Armadillo Solar Center, LLC, approved by Commissioners Court 2020-10-12/signed ~2020-11-09
  - This is the SAME LLC (Armadillo Solar Center, LLC) that is IA party for Phase 1 (21INR0421) — confirms one shell entity has covered the combined original project since 2020
  - Terms: ≥175 MW nameplate, ≥$140,000,000 min investment, 100% abatement for 10-yr Abatement Period on county + road/bridge ad valorem taxes; anticipated construction start "no later than 2024-01-01", anticipated COD "no later than 2024-12-31" (ORIGINAL target — now superseded; actual Phase 1 COD per its IA Amendment 7 is 2026-12-31, a 2-year slip from this abatement agreement's own target)
  - Exhibit A (sources/armadillo_ch312_p19_map.png): reinvestment-zone boundary map — same dogleg/zigzag shape as the 2021 ROW-agreement project-area map, near Mildred/Navarro/Cheneyboro, Navarro Co.
  - Exhibit B (parcel table): 27 parcels, landowners Mike/Vic/Andra/Scott Miller family, Peggy Herod, W&J Solar Properties LLC, Chad Kindle, Richard & Stephanie McVay — total acreage summed = **2,335.6 acres**, matching the Corsicana Daily Sun's reported 2,300 acres almost exactly (independent cross-check of project_area)
  - **This Ch.312 agreement was NOT found by `ch312.py resolve`** — it's absent from the live/purged/report open-data tables the tool queries (predates or was purged beyond the tool's Wayback recovery window). Confirms the playbook's own caveat: "a MISS is weak negative evidence... some counties never report" — here the county's OWN commissioners-court document server had the executed agreement all along; the Comptroller registry simply never carried/retained it. Locating it required county-minutes-adjacent web search, not the registry tool.
- Also fetched sources/2026-07-23_navcochronicle_armadillo-solar-signals-bright-future.html (Navarro County Chronicle) — large file (503KB), not yet parsed for text (time-boxed); filename retained as an artifact for provenance if needed later.

## NavCo Chronicle article (2025-06-02) parsed
- "Armadillo Solar Project" (AES, 204 MW) — county commissioners toured site; "Set to begin construction in Spring 2025"; "$300M+ capital investment"; "Commercial operation is anticipated to begin in Winter 2026" — MATCHES Phase 1 IA Amendment 7 schedule (Trial Op 2026-06-01, COD 2026-12-31) almost exactly. No "Phase 2" language anywhere in this article — publicly, AES/media only ever reference the single "Armadillo Solar Project" at 204 MW (=Phase 1 net capacity per original IA Exhibit C). This is consistent with Phase 2 (27INR0614) not yet being publicly branded/announced separately — an early-stage-project signal, not a paper-project signal (Phase 1 sibling is real and under construction at the identical POI/substation).

## D5: deterministic wrap-up
- queue_history.py 27INR0614 -> timeline.md/json (1 snapshot, 0 COD changes)
- eia_history.py 27INR0614 --write -> NOT in EIA-860M (negative evidence, logged)
- build_brief.py 27INR0614 -> brief.html (12 KB, 6 images, 11 sources)
- build_index.py -> research/index.json + INDEX.md refreshed (178 projects)
- findings.json, dossier.md, log.md all finalized. Turns/budget: well within limits (~207k/1M tokens spent, well under 25% of budget).
- FINAL VERDICT: real_early. Site 32.008418,-96.374303 high confidence. Construction: racking (attributable to co-located sibling 21INR0421, not confirmed Phase-2-specific). Independent COD 2027-Q4 (low confidence), drift risk HIGH — no signed IA for 27INR0614 itself found; queue's 2027-03-04 claim reads as an early placeholder given the co-located sibling's 4-year historical slip pattern.
