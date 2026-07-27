# Triage log — Coyanosa Gas (25INR0711)

T1 start
- queue_history.py ran: 5 snapshots (2026-02-01 → 2026-06-01)
- IA signed: 2025-03-13 (present in ALL snapshots — pre-dates the queue window)
- COD drift: 2026-04-28 → 2026-09-29 → 2026-12-17 (2 slips in 5 months)
- No construction milestones: screening, FIS, 6.9 gates, construction start/end all null
- Notable: IA signed without any FIS/screening dates showing — unusual milestone order
T1 end

T2 start
- gmaps.py: 429 Too Many Requests on both attempts (exact name; name+county) — budget exhausted
- pins_found: 0 (tool blocked, not a clean miss)
T2 end

T3 start
- DDG: CAPTCHA-blocked on both attempts
- Bing: returned unrelated results for "Coyanosa Gas" + Texas power plant; CAPTCHA on targeted site: query
- No developer name, LLC registration, or news surfaced
- news_found: false
T3 end

T4 start
- interchange.ercot.com: DNS not resolving from container
- interchange.puc.texas.gov: HTTP 402 on all attempts (FilingParty=Coyanosa Gas, base URL)
- ia_found: false (portal blocked — not a clean miss)
T4 end

T5 start
- TX Comptroller Ch.313 page: no direct data, redirects to sub-tools
- JETI current-agreements: 11 agreements listed, no Winkler County, no Coyanosa Gas
- JETI applications page: not fetched (budget conservation — JETI normal-absent for post-2022 gas projects)
- TX Comptroller taxable entity search: redirected to new URL, not re-fetched (budget)
- abatement_found: false (normal for post-2022, small gas peaker)
T5 end

T6 start
- Site candidate: Coyanosa substation, ~31.375°N, -103.093°W (Pecos County, community of Coyanosa)
  - Derived from POI: "Station Name: COYANOSA, Load Name: COYAN_2, TNMP Transformer T-2 (25kV), 138kV"
  - Coyanosa is a named community in Pecos County (not Winkler — county mismatch worth noting)
  - Confidence: low (POI-infrastructure only, no parcel or pin confirmation)
- cdse.py: 401/403 on all 9 grid chips — CDSE_PASSWORD absent from ~/.config/gis-research.env (example file)
- Imagery: BLOCKED — cannot produce contact sheet or frame reads
- construction_visible: unknown
T6 end

T7 start
- wrote triage_findings.json
- wrote triage.md
- turns used: ~28
- T2 blocked (gmaps 429), T3 blocked (DDG/Bing CAPTCHA), T4 blocked (PUCT 402 / ERCOT DNS),
  T6 blocked (CDSE_PASSWORD absent)
- Key actionable gap: TCEQ air permit unresolved — check this before approving deep scan
T7 end
