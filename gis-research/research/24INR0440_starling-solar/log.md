# Triage log — 24INR0440 Starling Solar

T1 start
## T1 — queue history
- 36 snapshots (2023-07-01 → 2026-06-01)
- COD drift: 3 changes (2025-05-09 → 2025-06-14 → 2027-05-15 → 2028-01-28)
- IA signed: 2026-02-17 (appeared first in 2026-06-01 snapshot) — RECENTLY SIGNED
- FIS requested: 2023-06-16; FIS approved: NOT YET
- Construction milestones: all blank
- Capacity history: 43.56 MW (original) → jumped to ~144 MW in Oct 2025 → settled 140.6 MW (2026-06-01)
  - POI note: Phase II addition of 42.24 MW to 23INR0035; storage companion 23INR0181
- No meets-6.9 milestones yet

T2 start
## T2 — delivery pins
- gmaps.py returning HTTP 429 on both attempts — rate limited. No pins obtained.
- Result: 0 pins found (tool blocked, not project-absent)

T3 start
## T3 — web sweep
- DDG search "Starling Solar 24INR0440 ERCOT": aggregator hits (ercotqueue.com, interconnection.fyi, cleanview.co, gridstatus.io) — no original news/press
- starlingsolar.com/about_starling → 302 redirect to apexcleanenergyproject.com → developer is **Apex Clean Energy**
- apexcleanenergy.com project page 404 (removed/migrated) — no active developer page
- No press releases, permitting news, or community announcements found
- Key finding: developer = Apex Clean Energy (saved to sources/apex_redirect.md)
- news_found: false (aggregator listings only, no original coverage)

T4 start
## T4 — PUCT Interchange
- interchange.puc.texas.gov/* → HTTP 402 on all URL variants (search/filings/, application.aspx, root)
- One retry (different URL) also 402 — portal blocked entirely in this environment
- DDG fallback for IA filing also returned CAPTCHA (no results)
- NOTE: queue data shows iaSigned=2026-02-17 — IA IS signed, likely filed at PUCT ~Feb 2026. Could not download.
- ia_found: cannot confirm (IA exists per queue data, but PDF not obtainable here)

T5 start
## T5 — abatements
- Ch.313 Comptroller site: no searchable database by county accessible via WebFetch
- JETI registry (jobsenergyincentives.gov): DNS not found
- DDG search for abatement hit CAPTCHA, no results
- Post-2022 projects rarely have Ch.313 (program expired); JETI is replacement but registry not accessible
- abatement_found: false (expected for 2024 filing date)

T6 start
## T6 — imagery
- No pin from T2 (gmaps rate-limited). No IA map from T4 (portal blocked). No CAD parcel hit obtained.
- POI: Birdhouse 138-kV sub (7255), Gonzales County — substation location not resolved via web search (DDG CAPTCHAs).
- No reliable site candidate better than "somewhere in Gonzales County" → SKIP imagery per checklist rule.
- construction_visible: false (imagery not run)

T7 start
## T7 — output
- triage_findings.json written
- triage.md written
- Turns used: ~22. Budget warning hit at 80% during T6 — imagery skipped (no site candidate anyway).
- DONE
