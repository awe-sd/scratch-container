# Triage log — Lupinus Storage 2 (24INR0155)

T1 start

## T1 — Queue history

Script output: 50 monthly snapshots (2022-05-01 → 2026-06-01), 3 reported-COD changes.

**Milestone summary:**
- Screening started: 2021-12-13
- Screening complete: 2022-03-10
- FIS requested: 2022-05-11
- FIS approved: 2026-03-17 (very recent)
- IA signed: 2025-03-04
- Meets 6.9(1): 2026-04-22
- Meets all 6.9: 2026-04-22
- Construction start/end: not reported
- Commercial operation approved: not reported

**COD drift (3 changes):**
1. 2024-12-30 (held 2022-05 → 2023-03)
2. 2025-12-31 (held 2023-04 → 2023-04, one month)
3. 2026-09-21 (held 2023-05 → 2025-02)
4. 2027-04-03 (current, held 2025-03 → 2026-06)

**Capacity:** 122.92 MW → 124.55 MW (bumped 2025-10)

**Assessment:** COD slipped 2+ years from original 2024-12-30. IA signed 2025-03 — real
development milestone. FIS approved 2026-03, both 6.9 gates met 2026-04. No construction
dates yet. Current COD 2027-04-03 is plausible given IA signed ~2 years prior with ~12-18
month battery build time.

T2 start

## T2 — Delivery pins

gmaps.py places returned HTTP 429 (rate-limited) on both attempts: "Lupinus Storage 2" and
"Lupinus Storage 2 Franklin County Texas". Per rules: one retry, then negative log.
No pins found. No further attempts.

T3 start

## T3 — Web sweep

**Developer identified: Sunraycer**
LLC names: Lupinus Solar 2, LLC; Lupinus BESS 2, LLC
Technology partner: Canadian Solar e-STORAGE
Capacity confirmed: ~124.55 MW / 301 MWh

Key findings:
- Sunraycer closed $901M project financing (May 2026) covering Eagle Springs + Lupinus 1 & 2
- Construction reportedly starting Q3 2026 (Solar Power World)
- Commercial operation targeted Q2 2027 — consistent with queue COD 2027-04-03
- "Build-chance 92%" per ercotqueue.com (IA + FIS complete)

Blocked: constructionfront.com (403), second DDG query (CAPTCHA). Saved to sources/T3_web_sweep.md.
No news found about delays, cancellation, or controversy.

T4 start

## T4 — PUCT Interchange filings

PUCT Interchange portal (interchange.puc.texas.gov) returned HTTP 402 on all attempts:
- /search?FilingParty=Lupinus+Storage+2 → 402
- /Documents/search?FilingParty=... → 402
- / (root) → 402

Per rules: portal blocked, one retry attempted (different URL patterns), negative log.
IA is confirmed signed 2025-03-04 per queue milestones. Could not retrieve PDF from PUCT.
No schedule exhibit obtained.

T5 start

## T5 — Abatements

TX Comptroller Ch.313 list: portal served overview/general page only — no application-level
data accessible via WebFetch (returned nav pages, not database records).
JETI registry: same — served overview page, no searchable application data.

Note: Ch.313 program closed to new applications after 2022; project entered queue 2021-12.
JETI is the successor — post-2022 projects would use JETI. No Franklin County BESS/Lupinus
hit found, but portal not machine-readable in this environment.

Result: abatement status unknown, likely no Ch.313 (deadline passed), JETI unknown.
Normal miss for early-stage BESS project without land-intensive footprint.

T6 start

## T6 — Imagery

Site candidate identified: Hagansport Switch substation at ~33.3415°N, -95.2494°W
(Hagansport community, Franklin County, at SH 37 / FM 71 junction, 11 mi NW of
Mount Vernon). Confidence: medium — community location matches POI name, substation
infrastructure likely nearby.

CDSE imagery attempt: cdse.py chips --lat 33.3415 --lon -95.2494 --dates 2026-06-01,2024-06-01 --buffer-km 2
Result: HTTP 401 Unauthorized on both dates.
Env file (~/.config/gis-research.env) is example template only — no real CDSE credentials
configured in this environment. Cannot retrieve Sentinel-2 imagery.

Imagery result: unavailable (auth not configured). No visual construction evidence.

T7 start

## T7 — Write and stop

triage_findings.json written.
triage.md written.
Turns used: ~22. Deep scan recommended.

END TRIAGE.
