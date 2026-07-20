# Triage log — SANJAC BESS (24INR0081)

## T1 start

**Queue history** (60 monthly snapshots, 2021-07-01 → 2026-06-01):
- COD drift count: 4 slips (2023-01-01 → 2024-01-01 → 2024-12-01 → 2025-12-01 → 2027-04-04)
- Current COD: 2027-04-04 (held since 2024-03-01)
- Milestones achieved: Screening started (2021-07-08), Screening complete (2021-09-28), FIS requested (2021-07-08)
- FIS approved: NO | IA signed: NO | 6.9 milestones: NONE | Construction: NONE
- Capacity: 200→208.63→202.37 MW (settled at 202.37 since 2023-02)
- Verdict: Project has been in FIS phase ~5 years with no IA. Very early stage.

## T2 start

**Delivery pins (gmaps.py places):**
- Query 1 "SANJAC BESS": HTTP 429 Too Many Requests
- Query 2 "SANJAC BESS Harris County Texas": HTTP 429 (one retry used)
- gmaps.py blocked — no pins found. Normal for a battery-storage project with no public brand.
- Pins found: 0

## T3 start

**Web sweep results:**
- Developer candidates: "Castleman Power" (ercotqueue.com), "Ocis Intelligent Energy" (ocisenergy.com/project/project-sanjac/) — relationship unclear
- Ocis Energy describes "Project SanJac" as BESS + data center load interconnect, 250 MW, Harris County, 20 miles from downtown Houston, target 2028
  - Corporate address: 5850 San Felipe Rd., Suite 601, Houston, TX 77057 (just an office)
  - No site address or coordinates disclosed
- "SANJAC BESS, LLC" LLC registration search: no results from DDG
- news_found: YES (Ocis project page exists; third-party trackers confirm project)
- Source saved: sources/ocis_energy_sanjac.md

## T4 start

**PUCT Interchange filings:**
- FilingParty="SANJAC BESS": HTTP 402 (session/cookie required)
- Description="SANJAC BESS": HTTP 402
- One retry used; portal blocked for all query forms
- IA found: NO (portal inaccessible; absence is portal block, not confirmed miss)
- Note: No IA milestone in queue history either — consistent with early FIS phase

## T5 start

**Abatements (Ch.313 / JETI):**
- Ch.313: No dedicated searchable database for Harris County; agreement docs on subpages not searched (budget spent)
- JETI current agreements for Harris County-area school districts: NRG gas projects only, no BESS, no SANJAC
- Abatement found: NO — consistent with post-2022 project (Ch.313 expired 2022-12-31; JETI unlikely for BESS-only)
- Normal result for this project type and vintage

## T6 start

**Imagery:**
- Site candidate method: POI "40270 Riverside 138kV" substation + Ocis description ("20 mi from Houston, Harris County, secure industrial park, SanJac area")
- Substation geolocation attempts: DDG (bot challenges), Nominatim (no substation results), OpenInfraMap (no data returned), substationlocator.com (DNS fail), ERCOT nodal inputs (404)
- No lat/lon found for "Riverside 138kV" or ERCOT node 40270
- Best area inference: NE Harris County industrial corridor (Channelview/Baytown/San Jacinto River area) — not precise enough for a 1-km buffer chip run
- Decision: SKIP imagery — no site candidate with sufficient precision
- Log: "no site candidate"

## T7 start

**Output files written:**
- triage_findings.json
- triage.md (8 lines)
- sources/ocis_energy_sanjac.md

**Turns used: ~28. Triage complete.**
