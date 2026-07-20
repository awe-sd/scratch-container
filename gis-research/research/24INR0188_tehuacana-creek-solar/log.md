# Triage log — Tehuacana Creek Solar (24INR0188)

## T1 start
- 55 snapshots (2021-12-01 → 2026-06-01)
- 7 COD-drift events: 2024-06-01 → 2024-12-31 → 2025-05-31 → 2025-07-17 → 2026-03-10 → 2026-12-31 → 2027-03-10 → **2027-05-18** (current)
- Capacity drift: 700 MW → 715 → 838.5 → **505.43 MW** (large downsizing mid-2024)
- Key milestones achieved: IA signed 2024-11-25, FIS approved 2026-06-16, Meets 6.9(1) 2025-02-12, Meets all 6.9 2026-04-23
- No construction-start, construction-end, energization, sync, or COA milestones
- COD 2027-05-18 with 7 prior slips = substantial schedule risk; all 6.9 only just cleared Apr 2026

## T2 start
- gmaps.py 429 on first call; one retry also 429 — API rate-limited, all 4 planned queries blocked
- No pins found (tool blocked, not a negative signal on the project itself)

## T3 start
- DDG: CAPTCHA block on both queries (one retry each) — no results
- Bing: 3 queries returned; zero results for "Tehuacana Creek Solar" — all unrelated content
- No developer name surfaced, no news/PR pages found
- No pages saved to sources/

## T4 start
- PUCT Interchange: 402 Payment Required on all paths including root — portal requires authenticated session
- One retry on alternate search paths — all 402
- IA DOES exist per queue history (iaSigned = 2024-11-25) but PDF not accessible via WebFetch
- ia_found signal = TRUE (queue data), PDF content = not retrieved

## T5 start
- TX Comptroller Ch.313: page returned general portal, no filterable application list accessible via WebFetch; county-filter URL also returned general page — no Tehuacana Creek Solar or Navarro County results
- JETI registry: no searchable database accessible via WebFetch; JETI info page only
- Note: Ch. 313 expired 2022; post-2022 projects (this one entered 2021 but still active) may use JETI — absence is expected/normal
- abatement_found = false (not accessible to verify either way)

## T6 start
- No pin (gmaps blocked), no IA map (PUCT blocked), no abatement map
- POI: "Tap 345kV 3381 Big Brown – 68091 Navarro circuit" — Big Brown plant in Freestone Co, Navarro substation likely near Corsicana; only narrows to county-level corridor
- Site candidate = "somewhere along Big Brown–Navarro 345kV line in Navarro County" — county-scale only
- Per checklist: SKIP imagery — log "no site candidate"
- construction_visible = false (not assessed)

## T7 start
- Wrote triage_findings.json and triage.md
- Turns used: ~23
- STOP

## D1 — Stage 1: LLC → parent chain (2026-07-19)
- Navarro County CC Oct 14 2025 special road use permit/bond: "Tehuacana Creek Solar LLC, c/o Parliament Energy Holdings LLC, 9651 Katy Fwy Suite 600, Houston TX 77024", contact Bradman Moore 832-808-4920 → confirms LLC name and developer identity [sources/2026-07-19_navarro-cc_2025-10-14-tehuacana-road-permit.pdf]
- Road bond $800,000 via McGriff/Marsh McLennan, surety Accelerant National Insurance; bond transmittal to "EnCap Investments, Parliament Energy Holdings LLC" [sources/2026-07-19_navarro-cc_2025-10-14-tehuacana-road-bond.pdf]
- Parliament Energy portfolio confirms: Tehuacana Creek Solar, backed by EnCap Investments and Mercuria Energy [https://www.parliamentenergy.com]
- Parliament Solar (Parliament Energy's flagship) completed early 2025 — 640 MWdc in Waller County TX → developer is not a paper entity

## D2 — Stage 2: Roads establish site location (2026-07-19)
- Road use permit routes: FM 246, SW CR 2386, SW CR 2340, SW CR 2370, SW CR 2380, SW CR 2360 — all in Precinct 3 (SW Navarro County)
- SW roads in Navarro County use a grid format; SW prefix = southwest quadrant, intersections define location corridor
- FM 246 runs east-west through the southern portion of Navarro County; SW CRs 2360-2386 are a cluster of parallel roads

## D3 — Parliament Energy portfolio page confirms COD (2026-07-19)
- Parliament Energy portfolio at parliamentenergy.com/portfolio: "Tehuacana Creek Solar — In development, Q4 2027"
- Developer-stated COD is Q4 2027 vs queue-reported 2027-05-18 (Q2); a ~6-month gap
- Parliament Solar completed "June 2025" per same page (vs earlier triage "early 2025") — developer is operational, not paper
- Portfolio total 2.7 GWdc / 2.1 GWac across 5 projects; Tehuacana is one of 3 @ Q4 2027

## D4 — Stage 3: Site pinpoint via road network (2026-07-19)
- Road permit roads in SW Navarro County: SW CR 2370 (31.872,-96.358), SW CR 2380 (31.861,-96.403), SW CR 2360 (31.879,-96.357), SW CR 2386 (31.860,-96.387), FM 246 (31.878,-96.345) — Overpass OSM data
- Road cluster centroid: approx 31.865, -96.385 as initial search center
- POI ("Tap 345kV 3381 Big Brown – 68091 Navarro circuit") is consistent: Big Brown substation is in Freestone County (~31.9,-96.0), Navarro substation is near Corsicana (~32.1,-96.5); a tap point along this 345kV line would be ~31.8-32.0,-96.3-96.4 range — consistent with site location

## D5 — Stage 2: Utility easement confirms construction timeline (2026-07-19)
- Navarro CC Jan 12 2026 approved Item 16: "Utility Easement for Tehuacana Creek Solar LLC in Pct 3"
- Easement form dated Dec 12, 2025: "Estimated start date of construction: 4/1/2026; Estimated completion date: 4/1/2027"
- Applicant contact: Harold E. Coulby Jr., phone 713-659-6100 (same Houston address as road permit)
- Construction window is Apr 2026 – Apr 2027; COD would follow post-commissioning (Oct-Nov 2027 if commissioning takes ~4-6 months)
- This is the clearest schedule signal: developer's own construction-start estimate = Apr 2026 [sources/2026-07-19_navarro-cc_2026-01-12-tehuacana-utility-easement.pdf]

## D6 — Negative findings log (2026-07-19)
- CDSE credentials (CDSE_PASSWORD in ~/.config/gis-research.env) return "invalid_grant" — satellite imagery not retrieved; this is a credential-expired condition, not a project signal
- Google Maps Places API: 429 rate-limited throughout session — no delivery pin found
- Google Maps Static API: 403 (API not enabled for key) — no site map image
- PUCT Interchange: 402 on all search paths — IA PDF not retrieved; IA confirmed to exist via queue data (iaSigned=2024-11-25)
- TX Comptroller entity search: UI-only, no API returns; entity not confirmed via comptroller.texas.gov
- TX SOS: $1/search fee wall — entity not confirmed via SOSDirect
- OpenCorporates: CAPTCHA blocked
- SEC EDGAR: 403 on full-text search API
- No news/press releases found for Tehuacana Creek Solar (Parliament Energy news page 504 timeout)
- CAD parcels: ACT.acttax.com form requires session cookie, POST returned form only; no parcel found under LLC name
- Navarro CC 2024-09-09 Construction Maestros abatement: unrelated (concrete batch plant at 915 SE CR 0010)
- Navarro CC 2024-08-12 Sunraycer/Gaia Solar (road Pct 2, NE CRs): different project/different quadrant — not Tehuacana
