# Triage log — 24INR0058 Briggs Storage

T1 start
- 52 snapshots (2022-03-01 → 2026-06-01)
- COD drift count: 2 (2024-12-31 → 2027-09-15 → 2028-04-15)
- IA signed: 2025-03-15; Meets 6.9(1): 2025-03-24
- FIS approved: MISSING (no date)
- Construction start/end: MISSING
- Capacity: jumped from ~70 MW (2022-2025) to 336 MW on 2025-07-01 — major upsize
T1 done

T2 start
- gmaps.py: HTTP 429 on both attempts (rate limited) — 0 pins found
T2 done (budget exhausted, tool blocked)

T3 start
- "Briggs Storage" + ERCOT: project listed at infrasure.ai, interconnection.fyi (both data aggregators, not primary news)
- Developer name on IA: Briggs Solar, LLC (original); amended IA shows IP Quantum III, LLC as successor/transferee
- IP Quantum III, LLC: ERCOT developer, IA with ETT dated 2025-08-21, 2 active projects (Briggs Solar + Briggs Storage)
- No news articles, press releases, or parent-company disclosure found
- Key thread: ownership transfer Briggs Solar LLC → IP Quantum III LLC; parent unknown
- PUCT control number surfaced: 35077 — to be chased in T4
T3 done

T4 start
- PUCT Interchange: all search endpoints returning HTTP 402 (all 3 attempts: filingParty=Briggs Storage, filingParty=IP Quantum, description=Briggs Storage)
- Control number 35077 surfaced in T3 web sweep — confirmed IA exists (ETT + IP Quantum III, dated ~2025-08-21)
- Could not download IA PDF or milestone schedule exhibit — portal blocked
- ia_found: true (confirmed by T3 web data) but content not retrieved
T4 done (portal blocked after budget)

T5 start
- TX Comptroller Ch.313 page: no searchable/filterable database available
- JETI + Ch.313 web search: no results for Briggs Storage, Briggs Solar, IP Quantum III in Haskell County
- Ch.313 expired 2022 — normal for post-2022 projects to lack it; JETI is successor but appears unapplied here
- abatement_found: false (normal for battery project at this stage)
T5 done

T6 start
- Site candidate: Haskell TX town center (33.158, -99.733) — Clear Crossing sub confirmed in Haskell; no precise coords
- cdse.py chip: 7/9 grid points failed (401/403 auth); 2 chips retrieved (eastern column, LON=-99.703)
- Contact sheet: 2 chips, agricultural patchwork + Haskell town; NO BESS pad, gravel, or container rows visible
- construction_visible: false (eastern chips only; western chips near substation not retrieved)
T6 done

T7 start
- triage_findings.json written
- triage.md written
- turns used: ~28
T7 done

## Deep scan — 2026-07-19

D1 start — reading triage, timeline, and running parallel research agent
- Triage had wrong coords: searched Haskell town center (33.158, -99.733); Clear Crossing sub is at (33.0014, -99.6055) — ~17 km south; all prior imagery missed the site entirely
D1 done

D2 start — subagent research on PUCT IA, IP Quantum III identity, and substation location
- Clear Crossing 345kV substation confirmed at 33.0013738°N, 99.6054944°W (OSM Way 453376936); Haskell County, TX; operator = AEP/ETT
- IP Quantum III, LLC = Intersect Power LLC (parent); CEO Sheldon Kimber; Durham NC address (5310 S Alston Ave)
- Google/Alphabet announced acquisition of Intersect Power Dec 2025
- PUCT CN 35077, Item 2235: "First Amended and Restated ERCOT SGIA between ETT and IP Quantum III LLC" executed 2025-08-21, filed 2025-08-25; covers both 23INR0059 (Briggs Solar) and 24INR0058 (Briggs Storage)
- IA PDF URL identified (35077_2235_1533641.PDF) but returns HTTP 402 — content not retrieved
- IP Quantum family in ERCOT: Quantum Solar (21INR0207) + Quantum Storage (26INR0310) at Kilby Station already approved-for-sync 2026; Solace Solar (23INR0031) + Solace Storage (26INR0309) at Graham-Tonkawas approved-for-sync 2026; Briggs cluster furthest behind
- FIS anomaly: requested 2022-03-04, never approved — likely tied to 4x capacity upsize (70→336 MW Jul 2025), may require new restudy
D2 done

D3 start — satellite imagery at corrected location (Clear Crossing sub at 33.0014, -99.6055)
D3 done
- chip_2km_2026-07: MASSIVE substantially-complete solar arrays visible at Clear Crossing sub — hundreds of acres; tight chip shows pale compound adjacent to substation (possible BESS pad or sub yard)
- chip_wide_4km_2026-07: full extent visible — solar array north and south of substation; large installation
- 2024-01 and 2023-06 chips downloaded but not read (budget exhausted)
- CRITICAL AMBIGUITY: solar at this location may be Quantum Solar (21INR0207, Kilby Station, approved-for-sync Apr 2026) which appears to be a different substation, OR early Briggs Solar (23INR0059) construction; BESS pad (Briggs Storage) not definitively identified in imagery
- BUDGET EXHAUSTED: synthesizing now
