# Triage log — Yellow Cat Wind (25INR0018)

## T1 start
- queue_history.py ran: 52 snapshots (2022-03-01 → 2026-06-01)
- **COD drift: 5 changes** — started 2024-06-01, now 2027-04-01 (+34 months total slip)
  - 2024-06-01 → 2024-10-01 → 2024-12-23 → 2026-03-31 → 2026-09-30 → 2027-04-01
- **Milestones achieved**: Screening started (2021-08-17), Screening complete (2021-11-05), FIS requested (2022-03-07), FIS approved (2025-12-09), **IA signed (2024-07-09)**, Meets 6.9(1) (2025-02-12), Meets all 6.9 (2026-01-27)
- Construction start/end, energization, sync, COD: all NULL
- Capacity: started 300 MW, now 262 MW (downsized ~38 MW from 2025-03)
- **Status: IA signed + meets all 6.9 — real project, pre-construction**

## T2 start
- gmaps.py places: 429 Too Many Requests on first call; retried once — still 429. BLOCKED.
- No delivery pins found. Normal finding.

## T3 start
- DDG: CAPTCHA blocked. One retry = same result. Blocked.
- Bing: "Yellow Cat Wind" + Texas/Navarro/ERCOT/25INR0018 — zero project-specific results (3 queries). Common words ("yellow", "cat") drown signal.
- No developer name surfaced. No news/PR found.
- **T3 result: no web signal. Normal for pre-construction project with generic name.**

## T4 start
- PUCT Interchange: all URLs (/, /apps/eFilingItem/search/) returning HTTP 402 Payment Required. BLOCKED entirely.
- IA status from queue data: iaSigned = 2024-07-09 — confirmed IA exists, but document not retrievable via PUCT portal this session.
- **T4 result: IA confirmed signed (queue data), PUCT portal blocked. Cannot retrieve PDF or schedule exhibit.**

## T5 start
- TX Comptroller Ch.313: portal navigation pages only; no searchable database accessible via WebFetch.
- JETI current-agreements.php: 11 agreements listed; none for Navarro County or "Yellow Cat Wind".
- JETI applications.php: page error, no data loaded.
- **T5 result: no abatement found. Normal — JETI is new (HB 5), only 11 agreements total. Ch.313 closed to new applicants 2022; this project (screening 2021) could have applied but no evidence found.**

## T6 start
- FAA OE/AAA: system returning shutdown/503 notices; no turbine filings accessible.
- Web search for Venus 345kV substation + Navarro wind farm: no coordinates found.
- JETI/abatement: no map artifact.
- PUCT IA: portal blocked, no map exhibit.
- Site candidate: only "somewhere in Navarro County" (32.05°N, 96.47°W county center) — below imagery threshold.
- **SKIP imagery per checklist rule: no site candidate better than county-level. Log: "no site candidate".**

## T7 start
- triage_findings.json written
- triage.md written
- **Turns used: ~28. T7 complete. STOP.**

## Deep scan — 2026-07-19

### D1 — Stage 1 (LLC / developer identity)
- TX Comptroller COA search: AJAX-based portal, form submission blocked; no entity result for "Yellow Cat Wind" returned (response = nav page, not results). Logged negative.
- SEC EDGAR full-text search "Yellow Cat Wind": 0 hits across all filings. Logged negative.
- SEC EDGAR "WTG Hubbard": 0 hits. Logged negative.
- PUCT Interchange: portal accessible but JS-rendered search (requires browser); API endpoints not public; could not retrieve IA PDF. Logged negative.
- FAA OE/AAA: still in government shutdown mode; no turbine filings accessible. Logged negative.

### D2 — Stage 2 (County records)
- JETI current agreements: 11 entries, none for Navarro County. Logged negative.
- Navarro County commissioners court minutes searched (2023–2026 regular meetings):
  - No "Yellow Cat Wind" or wind energy permit found in any meeting through 2025.
  - **2026-07-13 Regular minutes**: Item 17 "Approve Surety Bond for WTG Hubbard Transmission LLC in PCT 3"
  - Downloaded and read PDF: Bond No. 810024731, **WTG Hubbard Transmission, LLC** (principal), Atlantic Specialty Insurance Co. (surety), $265,000 penal sum, for **Special Road Use** permit, Navarro County PCT 3, effective **June 18, 2026**. Signed June 18, 2026.
  - **KEY FINDING**: "WTG Hubbard Transmission LLC" = transmission line entity for wind project. "Hubbard" = Hubbard TX (Hill County, just south of Navarro County line, ~31.85°N 96.80°W). PCT 3 = southern/SW Navarro County. Road use bond obtained June 2026 = active pre-construction / mobilization.
  - Saved: sources/2026-07-19_navarro-county_2026-07-13-wtg-hubbard-surety-bond.pdf

### D3 — Stage 3 Site pinpoint (working hypothesis)
- Hubbard TX: 31.847°N, 96.796°W (Hill County). PCT 3 of Navarro County borders Hill County to the south.
- POI: "Tap 345kV 1906 Venus - 68091 Navarro" — the Venus 345kV substation is near Venus TX (Johnson County, 32.43°N, 97.10°W); the 345kV line runs SE toward a Navarro substation. The tap point is somewhere along this ~60-mile corridor.
- Working site hypothesis: southern Navarro County or northern Hill County near Hubbard (~31.9-32.0°N, 96.7-96.9°W). Need TX SOS/Comptroller for "WTG Hubbard" parent entity to confirm Yellow Cat Wind link.

### D4 — KEY ARTIFACTS (2024-12-09 road use permit findings)
- **Yellow Cat Wind LLC** confirmed as applicant (not just an INR name)
- Contact: Jason Tillman, 2201 Civic Circle Suite 916, Amarillo TX 79109, ph 612-466-5254
- Load: Wind Turbine Generation Components (nacelles, tower sections, blades — Schnabel/RGN trailers)
- Routes: NW 4110, NW 4130, NW 4240, NW 4250, NW 4270, NW 4280, NW 4300, NW 4360, NW 4370, NW 4400, NW 4420, NW 4450, NW 4050 — PCT 4 Navarro County, 18 miles
- Permit term: 9.1.25 – 12.31.27, signed 12.4.24; road bond $100,000/mile
- **Implication**: Turbine deliveries planned to start September 2025; 18 miles of NW roads in PCT 4 = site is in NW Navarro County
- WTG Hubbard Transmission LLC (June 2026 surety bond, PCT 3) = separate transmission line entity confirming same project in adjacent precinct
- Imagery: SKIPPED (no site coordinates yet — NW road lookup pending); budget constraint forces synthesis now
- Developer address: Amarillo TX 79109 → likely a small/independent developer or project office; no web signal found (SEC EDGAR = 0, no news, no PR)

### D5 — Imagery attempt
- CDSE chip: HTTP 401 Unauthorized — ~/.config/gis-research.env contains example/placeholder credentials only. No satellite imagery obtained.
- Site coordinates established from county road names (NW 4110–4450, PCT 4, Navarro County): 32.075°N, 96.780°W ± ~8 km (road network spans 31.98–32.09°N, 96.78–96.81°W).
- No imagery = cannot confirm construction stage visually.
- NOTE: Road use permit signed Dec 2024, term starts Sep 2025 → turbine delivery expected to have begun ~Sep 2025. Transmission LLC bond June 2026 = transmission line construction active now (Jul 2026).
