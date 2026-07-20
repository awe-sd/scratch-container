# Triage Log — 24INR0154 Lupinus Solar 2

T1 start
T1 result: 50 snapshots. 3 COD slips: 2024-12-30 → 2025-12-31 → 2026-09-21 → 2027-04-03 (current). IA signed 2025-03-04. FIS approved 2026-03-17 (after IA — unusual order). Meets all 6.9 as of 2026-04-22. No construction start/end. Capacity trimmed 244.24→242.31 MW in 2025-10.

T2 start
T2 result: gmaps.py 429 on first call, one retry also 429 — blocked. No delivery pins found. Budget spent.

T3 start
T3 result: Developer = Lupinus Solar 2, LLC; parent/owner per EIA Form 860 = Sunraycer Assets I LLC. LLC registered in Commerce TX. GEM wiki page exists (403). cleanview.co shows a paired 123 MW battery component (separate queue entry). No press releases or news articles found. ercotqueue.com lists 92% build-chance. Budget spent.

T4 start
T4 result: PUCT interchange portal returns 402 on all attempts (blocked). DDG search for PUCT filings found nothing. IA is confirmed signed per queue data (2025-03-04) but PDF not retrievable this pass. No docket number surfaced. Budget spent — IA exists in queue but document not obtained.

T5 start
T5 result: No Ch.313 or JETI abatement found for Lupinus Solar 2 / Sunraycer Assets in Franklin County. Comptroller portal did not return county-filtered data via WebFetch. DDG search returned zero results. Normal for post-2022 projects; Ch.313 program expired 2022. Budget spent.

T6 start
T6 result: Site candidate = Hagansport community, Franklin County TX (~33.20N, 95.20W), confidence LOW (POI community match, no pin). cdse.py returned 401/403 on all 9 chip attempts — CDSE credentials missing or expired. Imagery BLOCKED. Construction unknown. Budget spent.

T7 start
T7 result: triage_findings.json + triage.md written. 22 turns used. STOP.

## Deep scan — 2026-07-19

**S1: LLC / Parent chain**
- IA signed 2025-03-04: Generator = "Lupinus Solar 2, LLC"; signed by Nathan Krieger (SVP Commercial). [sources/2026-07-19_puct_35077-2101_oncor-lupinus-solar-2-IA.pdf]
- Parent: Sunraycer Renewables (Crayhill Capital Management, Annapolis MD) per pv-tech.org article 2026-03-24 area.
- PPA: Google signed dual PPAs with Sunraycer for Lupinus 1+2, ~400 MWac combined, March 2026; facilitated by LevelTen Energy LEAP. [web: pv-tech.org/sunraycer-google-ink-ppas-for-400mwac-lupinus-solar-project-in-texas/]
- Groundbreaking confirmed in March 2026 per pv-tech article. CRITICAL: construction has started.
- IA covers four INRs: 24INR0154 (Lupinus Solar 2), 24INR0155 (Lupinus Storage 2), 24INR0484 (Lupinus Solar 3), 24INR0490 (Lupinus Storage 3)

**S2: PUCT IA found**
- Control No. 35077, Item 2101 (original IA, filed 2025-03-31)
- Control No. 35077, Item 2427 (Amendment 1, filed 2026-03-12)
- Exhibit B schedule: In-Service Date = 2026-12-03; Scheduled Trial Operation = 2026-12-13; Scheduled COD = 2027-04-03
- Exhibit C POI: "Hagansport Switch in TSP's 138 kV, approximately 31 miles NE of Sulphur Springs, TX, Franklin County"
- Equipment: 80x Power Electronics HEM FS3430M inverters (274.4 MVA gross, 243.6 MW net)
- Exhibit E Security: LC $13,841,916 on/before 2025-03-03

**S3: Site location**
- Hagansport community: 33.3415°N, 95.2494°W (Nominatim geocode; confirmed as junction of TX-37 and FM-71, ~11 mi NW of Mt Vernon). This is the POI community, not the array centroid.
- IA says Hagansport Switch is ~31 mi NE of Sulphur Springs — matches Hagansport area.
- NEGATIVE: gmaps.py 429 (rate limited), cannot get delivery pins.

**S4: Imagery**
- CDSE credentials locked (too many concurrent sessions) — imagery BLOCKED for now.
- Will retry after cooldown.

**Amendment 1 (Item 2427)**
- Need to fetch from PUCT: https://interchange.puc.texas.gov/Documents/35077_2427_*.PDF
- Filed 2026-03-12 per DDG search result.


## Deep scan continued — 2026-07-19

**S1 completed: Owner chain**
- Lupinus Solar 2, LLC → Sunraycer Renewables → Crayhill Capital Management (Annapolis, MD)
- Google PPA (dual, ~400 MWac combined with Lupinus 1) signed March 2026 via LevelTen LEAP
- Groundbreaking March 2026 per PV-Tech 2026-03-24 article [sources/2026-07-19_pvtech_sunraycer-google-lupinus-ppas.html]
- Nathan Krieger (SVP Commercial) signed IA for Generator; Robert Holt (Oncor Director Transmission Services) signed Amendment 1
- No EPC contractor identified. No financing close announcement found.

**S2 completed: County records**
- Franklin CAD: 0 parcels under Lupinus Solar 2, Sunraycer, or variants — expected for leased farmland (4 searches)
- Ch.313/JETI: none found — expected, program expired 2022
- PUCT IA: Control 35077, Item 2101 (original IA 2025-03-31 filed) + Item 2427 (Amendment 1, 2026-03-12 filed)
- IA Exhibit B schedule: In-Service 2026-12-03, Trial Op 2026-12-13, COD 2027-04-03
- IA Exhibit C POI: Hagansport Switch, 138 kV, Franklin County, ~31 mi NE Sulphur Springs
- Exhibit E security: $13,841,916 LC (unchanged through Amendment 1 — Amend 1 only changed bank rating criteria)
- IA covers 4 INRs: 24INR0154 (Solar 2), 24INR0155 (Storage 2), 24INR0484 (Solar 3), 24INR0490 (Storage 3)

**S3 completed: Site pinpoint**
- Hagansport community nominatim: 33.3415, -95.2494
- Wide chip 2026-07 shows construction ~2.5 km SSW; re-centered to 33.305, -95.275
- Tight chip confirms large graded footprint with road grid and substation pad
- Confidence: medium-high (imagery shape-match + POI proximity; no delivery pins)

**S4 completed: Imagery**
- 2025-06: cloudy, inconclusive
- 2025-12: bare farmland, no activity [imagery/key/s2_2025-12_pre.png]
- 2026-07: large multi-polygon graded footprint with road grid, substation pad [imagery/key/s2_2026-07_active.png]
- CDSE credentials expired mid-session (max concurrent sessions); 2026-04 chip not obtained
- Timelapse job stopped (was consuming session slot without output)
- Stage: CLEARING confirmed; transition window 2025-12 → 2026-07, consistent with March 2026 groundbreaking

**NEGATIVE EVIDENCE logged:**
- No financing close press release (Sunraycer/Crayhill have not announced debt close)
- gmaps.py 429 throughout — no delivery pins
- TX Comptroller portal redirect loop — no entity data
- No local news coverage found (Mount Vernon Optic-Herald DNS unavailable)

## Wrap-up — 2026-07-19

- queue_history.py: timeline.json + timeline.md written (50 snapshots, 3 COD changes)
- build_brief.py: brief.html written (8 KB, 2 images, 3 sources)
- build_index.py: 101 projects indexed
- findings.json, dossier.md: complete
- Verdict: real_active | stage: clearing | independent COD: 2027-Q2 | drift: medium
