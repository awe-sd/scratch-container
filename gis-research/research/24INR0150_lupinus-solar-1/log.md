# Triage log — Lupinus Solar 1 (24INR0150)

T1 start

## T1 — Queue history
- 50 snapshots: 2022-05-01 → 2026-06-01
- COD drift (3 changes): 2024-12-30 → 2025-12-31 → 2026-09-21 → 2027-09-13 (current)
- IA signed: 2025-06-26 (first in 2025-07-01 report)
- Meets 6.9(1): 2025-08-05
- FIS requested 2022-05-11; FIS approval: NOT achieved
- Construction start/end: NOT reported
- Capacity: 164.86 MW (2022-05 → 2025-11) → 162.31 MW (2025-12 → present)
- Status: IA signed, 6.9(1) met, but no FIS approval, no construction milestones

T2 start

## T2 — Delivery pins
- gmaps.py: HTTP 429 (rate-limited) on all 2 attempts; tool blocked for triage
- No pins obtained. Normal result.

T3 start

## T3 — Web sweep
- Developer: Sunraycer Renewables (Crayhill Capital portfolio company)
- SPV: Lupinus Solar, LLC; early-stage developer: Diode Ventures
- $901M project financing closed 2026-05-14 (MUFG, Ally Bank, Nomura, Nord/LB, SocGen)
- Portfolio: Eagle Springs + Lupinus 1 + Lupinus 2 (479.5 MWac solar + 236.5 MWac BESS)
- Google PPAs backing Lupinus projects
- Groundbreaking: 2026-03-17 (construction confirmed underway)
- Eagle Springs targets late 2026 COD; Lupinus sites targeting 2027
- Sources saved to sources/web_sweep_summary.md
- gem.wiki: 403 blocked; DuckDuckGo CAPTCHA on two queries; 3 aggregator sites returned rich data

T4 start

## T4 — PUCT Interchange
- interchange.puc.texas.gov: HTTP 402 on all direct fetch attempts (portal requires session/auth)
- DDG search for PUCT docket "Lupinus Solar": no docket number surfaced
- IA existence CONFIRMED via T1 (iaSigned = 2025-06-26) + T3 (press coverage); PDF not retrieved
- No milestone schedule exhibit obtained; deep scan should attempt authenticated PUCT access

T5 start

## T5 — Abatements
- TX Comptroller Ch.313: portal returned overview pages only; no searchable table accessible via WebFetch; no Franklin County solar entry found
- JETI: DDG search returned no JETI applications for Lupinus/Sunraycer/Franklin County
- Normal for post-2022 project (Ch.313 expired 2022); JETI miss expected at triage without direct portal access
- Deep scan: try authenticated Comptroller ch313 data export + JETI portal directly

T6 start

## T6 — Imagery
- Site candidate assessment: no pin from T2 (gmaps blocked), no coords from aggregators (cleanview/interconnection.fyi), OpenInfraMap rendered no data, no groundbreaking press release with location
- Best available: "Franklin County, TX" — county-level only; no specific parcel or intersection
- Per checklist: no site candidate better than county → SKIP imagery
- Note: construction IS confirmed (groundbreaking 2026-03-17, financing closed). Deep scan should resolve site location first (county permit records, Texas Railroad Commission, or ERCOT GIS node map) then run imagery.

T7 start

## T7 — Final outputs
- triage_findings.json written
- triage.md written
- Turns used: ~28
- STOP

---
# Deep scan log — 2026-07-20

## D0 — Skeleton
- findings.json skeleton written; triage handoff read

## D1 — IA documents
- puct.py match: 35077-2199 (original IA) CONFIRMED via INR-in-text; 35077-2426 (Amend 1) CONFIRMED
- Unverified: 35077-2427 (dupe of Amend 1?), 35077-2468 (Lupinus 2 Amend 2), 35077-2469 (Lupinus 2 Amend 3)
- IA p29 Exhibit B Time Schedule: In-Service 2027-05-13, Trial Op 2027-05-17, COD **2027-09-17** — matches reported 2027-09-13 (queue rounds 4 days)
- IA p31: key intermediate milestones — All-Weather Road grading design by 2026-04-01, road complete by 2026-08-14, 4-hole pads at POI by 2027-03-12, equipment by 2027-04-13
- IA p51 One-Line Diagram: Paradise Lake Switch taps Woodard 345kV – Monticello 345kV; co-located Lupinus 1 Storage 82.97 MW (24INR0153) on same switchyard
- Amendment 1 (2026-02-12): only replaced Exhibit E security language (added Fitch rating); NO schedule change
- Amendments 2+3 both cover Lupinus Solar 2 (24INR0154) — not this project; unverified flag correct
- NEGATIVE: ch313/JETI no match for Franklin County solar (expected — project filed 2024, post-Ch.313 expiry; JETI miss = no tax abatement filed yet or under a name variant)

## D2 — Site + imagery
- Google Places pin: "Lupinus 1 & 2 Solar | 2651 W Farm Rd 71, Talco, TX 75487 | 33.330457, -95.290265" — decisive delivery pin in Franklin County
- Sentinel-2 chip requested at 33.330457, -95.290265: CDSE openEO synchronous endpoint returns HTTP 402, batch jobs endpoint returns 403; token auth works fine; catalog confirms S2B scene exists 2026-07-14 (T15STS/T15STT). Imagery not obtained — logged as negative evidence.
- Static Maps API 403 (not activated for key) — no site map image

## D3 — Gap fill / county records
- Groundbreaking PR (prnewswire 302715699): EPC = McCarthy Building Companies; "Northeast TX ~90 miles outside Dallas"; communities include Mt. Vernon, TX (Franklin County seat); Lupinus I+II completion "early 2028"
- Construction review article: location = Hagansport TX (Franklin County area); "Franklin and Delta Counties" for I+II; BESS = e-STORAGE (Canadian Solar) SolBank 3.0
- Google PPA article (solarpowerworldonline): "approximately 400-MWac Lupinus PV facility in Franklin County"; expected COD "late Q4 2027"
- Franklin County CAD portal (esearch.franklin-cad.org): TLS connect error — SSL routines unexpected EOF; 0 parcels obtained
- ch313/JETI: no match (expected — post-2022 project, JETI not yet filed or under unrecognized name)
- EIA history: plant 66895, entity Sunraycer Assets I LLC; status = "Planned - regulatory approvals not initiated" through 2026-05; planned COD 2027-09 stable since 2025-06 — CONFIRMS queue COD
- EIA coords (30.30338, -95.25692) appear erroneous (lat ~3° south of Franklin County); not used for site

## D4 — Synthesis
- Verdict: real_active — financing closed, EPC on site, IA confirmed, Google PPA executed
- Independent COD: 2027-Q4; drift risk: medium (3 prior slips; PR says "early 2028"; IA says Sept 2027)
- dossier.md written

## D5 — Wrap-up tools
- queue_history.py run: timeline.json + timeline.md updated (50 snapshots, 3 COD changes)
- eia_history.py --write run: eia_history.json written

## Shared-campus imagery (user-directed, 2026-07-21)
5-date series covering the full Lupinus 1+2 campus at Hagansport Switch (frames identical in both project dirs). Groundbreaking 2026-03-17 (PR) corroborated: clearing visible 2026-04, ~4km contiguous earthworks by 2026-07-15. Verdict: clearing_grading_active for both INRs.
