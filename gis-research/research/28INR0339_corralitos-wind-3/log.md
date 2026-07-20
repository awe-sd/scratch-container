# Triage log — Corralitos Wind 3 (28INR0339)

## T1 start
- queue_history.py ran OK; 12 snapshots 2025-07-01 → 2026-06-01
- Screening started: 2025-06-13; Screening complete: 2025-09-11; FIS requested: 2025-06-24
- FIS approved: — ; IA signed: — ; all subsequent milestones: —
- COD drift: 0 changes — held 2028-05-31 throughout all 12 snapshots
- Assessment: very early stage — screening done, FIS requested but not approved, no IA; COD 2028-05-31 stable but likely aspirational

## T2 start
- gmaps.py returned HTTP 429 on both attempts (rate-limited); 1 retry per rules, budget exhausted
- No pins found — blocked portal, not a miss signal
- Result: pins_found = 0 (tool failure, not absence of project)

## T3 start
- Developer identified from DDG aggregators: Las Crestas Wind Energy, LLC / Bordas Energy
- Parent project: "Las Crestas Wind Project" ~400-500 MW, ~75,000 acres, Zapata County near San Ygnacio
- Companion project: Corralitos Wind 4 (28INR0340, 195.4 MW) same filing date
- DoD permit pause (May 2026) noted as potential risk for TX wind projects
- bordasenergy.com: unreachable; FAA OE portal: government shutdown notice; gridstatus.io: 403; interconnection.fyi: 404
- news_found = true (aggregator references only; no primary press release or news article saved)
- Saved: sources/t3_web_sweep.md

## T4 start
- PUCT Interchange (interchange.puc.texas.gov) returning HTTP 402 on all attempts — portal blocked
- Tried: filingParty=Corralitos Wind 3; filingParty=Las Crestas Wind Energy; base URL
- No IA found — blocked portal, not confirmed absence
- ia_found = false (portal inaccessible, not verified negative)

## T5 start
- TX Comptroller Ch.313 page: no searchable database; tools listed don't cover Ch.313 directly
- JETI page: no searchable registry online
- No Ch.313 or JETI record found for Zapata County / Corralitos Wind / Las Crestas Wind
- Expected: project filed June 2025; Ch.313 expired 2022, JETI is successor but no online registry yet — normal miss for this vintage
- abatement_found = false (expected for post-2022 project)

## T6 start
- POI: ETT 345kV Tiempo #80224 Substation, Zapata County — new substation, LRGV improvements project
- openinframap.org: no map data served (JavaScript-rendered; not parseable)
- DDG: confirmed Tiempo is in Zapata County, on CENIZO7C–DELSOL7C 345kV line; no GPS coordinates returned
- ettexas.com/projects: no Tiempo listed with coordinates
- Las Crestas Wind project described as ~75,000 acres near San Ygnacio, Zapata County — that is a general area, not a pin
- Best site estimate: "somewhere in Zapata County near San Ygnacio" — county centroid only, no parcel, no pin, no POI coordinates
- Per rules: no site candidate better than county-level → SKIP imagery, log "no site candidate"
- construction_visible = false (imagery not run)

## T7 start
- Wrote triage_findings.json and triage.md
- Turns used: ~28
- Blockers this run: gmaps.py 429, PUCT Interchange 402, FAA OE portal down, DDG CAPTCHAs
- All steps T1–T7 completed; imagery skipped per rules (no site candidate better than county)
- DONE
