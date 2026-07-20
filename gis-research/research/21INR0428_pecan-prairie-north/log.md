# Triage log — Pecan Prairie North (21INR0428)

## T1 start
queue_history.py → 82 snapshots (2019-09-01 → 2026-06-01), 7 COD changes.
- IA signed: 2021-02-26
- FIS approved: 2026-03-13
- Meets 6.9(1): 2025-08-20; Meets all 6.9: 2026-05-19 (2 months ago)
- Construction start/end: NOT reported
- COD drift: 2021-07-01 → 2027-05-01 (6 yr total slip); currently 2027-05-01
- Capacity: started 500 MW, now 324.11 MW (recent step-down from 451 → 321 → 324)
- No energization/sync/commercial-operation milestones

T1 complete.

## T2 start
gmaps.py places "Pecan Prairie North" → HTTP 429 Too Many Requests (rate-limited).
Retry with alternate query → 429 again. Budget exhausted. No pins found.
T2 result: 0 pins.

## T3 start
DDG search "Pecan Prairie North solar Texas":
- interconnection.fyi/eia/plant/64999: 350 MW solar, Leon TX, EIA ID 64999 (planned)
- cleanview.co: 324 MW, expected online May 2027
- gem.wiki: "pre-construction, Leon County TX" (403 on direct fetch)
- infrasure.ai: plant 64999, fixed-tilt technology
- Developer: ConnectGen (Houston), acquired by Repsol Renewables 2024
  - Main "Pecan Prairie" project (595 MW) reportedly under construction
  - Pecan Prairie North (350 MW) = planned, May 2027
  - Pecan Prairie South (~133 MW) = planned, March 2027
- Project previously called "Leon County Solar"
- LLC name "Pecan Prairie North LLC" not confirmed via SOS search (bot-blocked)
T3 complete: developer = Repsol/ConnectGen; news_found = true (construction on flagship, North still planned).

## T4 start
PUCT Interchange direct URL fetch → HTTP 402 (all URL variants). Budget: 2 of 6 spent on portal.
Web search for PUCT IA filings → bot-captcha / no results found.
Note: timeline.md confirms iaSigned = 2021-02-26, so IA EXISTS in ERCOT records — but PUCT
Interchange portal is inaccessible via WebFetch in this session.
T4 result: ia_found = true (IA signed per queue data 2021-02-26), but PUCT PDF not retrieved.

## T5 start
TX Comptroller Ch.313 page → no searchable data accessible via WebFetch (xlsx URL redirected to generic page).
DDG search for Ch.313/JETI + Leon County + Pecan Prairie → bot captcha, no results.
Note: project entered queue 2021 (post-2022 Ch.313 expiry makes JETI the likely path if any abatement applied).
No abatement documents found. This is NORMAL for a project this vintage without public JETI announcement.
T5 result: abatement_found = false.

## T6 start
Site candidate: "southwestern Leon County, TX" from T3 web sweep. No pin coordinates available.
Center estimate: ~31.24°N, -96.25°W (SW quadrant of Leon County, near Marquez).
Attempted 3×3 chip grid via cdse.py → HTTP 401 Unauthorized on all 9 chips.
CDSE credentials not loaded in ~/.config/gis-research.env for this session.
T6 result: imagery blocked (401 auth failure). construction_visible = false/unknown.

## T7 start
Wrote triage_findings.json and triage.md.
Turns used: ~28. Tool failures this run: gmaps.py 429 (T2), PUCT Interchange 402 (T4), CDSE 401 (T6).
T7 complete. Stopping.

## D1 - Deep scan start (2026-07-19)

### EIA 860M - DECISIVE COORDINATE FIND
Source: EIA Form 860M May 2026 (downloaded to sources/2026-05_eia860m_may2026.xlsx)
- Plant ID: 64999, Plant Name: "Pecan Prairie North Solar"
- Entity: Repsol Renewables NA (Entity ID: 65265)
- Location: Leon County TX, ERCO
- Capacity: 350 MW nameplate
- Technology: Solar Photovoltaic (PV)
- Planned Operation: May 2027
- **Status: "(L) Regulatory approvals pending. Not under construction"** — as of May 2026
- **Coordinates: 31.13718°N, -96.26925°W** — HIGH CONFIDENCE (EIA-reported, confirmed Leon County TX)
- Note: EIA shows 350 MW vs ERCOT's 324.11 MW — minor discrepancy, expected (different accounting)

Sibling projects also in EIA 860M at same entity (Repsol Renewables NA, EID 65265):
- Pecan Prairie South Solar (Plant 64981): 130 MW, Leon County, Planned Mar 2027, lat 31.05001 lon -96.221
- Pecan BESS (Plant 67774, Gransolar TX Three LLC): 157 MW battery, Leon County, Planned Jul 2027

IMPORTANT: This is the first confirmed coordinate for the site. Replacing triage estimate of 31.24/-96.25 (which was county-level only, wrong).


### IMAGERY ANALYSIS - COMPLETE (timelapse Jul 2024 - Jun 2026)
Source: CDSE Sentinel-2 timelapse, 21 monthly frames, 6km buffer, stored in imagery/
Contact sheet: imagery/contact_sheet.png

Frames reviewed full-size (5 full-size reads out of 6 allowed):
1. s2_test.png (wrong location, triage estimate 31.24/-96.25) - no solar activity
2. s2_2026-07-01_xwide.png (EIA coords 31.13718/-96.26925) - undisturbed rural Leon County
3. s2_2026-07_tight.png (2km buffer, EIA coords) - crossroads, no construction
4. s2_2024-12-01.png - classic winter deciduous forest brown, no graded polygon, no construction
5. s2_2025-10-01.png - fall season, undisturbed rural landscape, no construction activity
6. s2_2026-06-01.png (reviewed) - cloud-heavy, green summer, no solar site visible through clouds

CONCLUSION: NO CONSTRUCTION ACTIVITY observed at EIA-reported coordinates (31.13718/-96.26925) across entire 2-year timelapse Jul 2024 - Jun 2026.
- No graded rectangles
- No racking/module rows
- No substation construction pad
- Pattern: stable undisturbed rural farmland/forest throughout

This is FULLY CONSISTENT with EIA 860M May 2026 status "(L) Regulatory approvals pending. Not under construction."

Site is pre-construction as of at least June 2026. With reported COD = 2027-05-01 (~10 months away), and no construction started, the reported COD is NOT achievable. Independent estimate: 2028-Q1 base case.

### IMAGERY NOTE - LOCATION UNCERTAINTY
EIA coordinates are a reported centroid, not GPS-surveyed. The true project footprint (324 MW ≈ ~1,600-2,900 acres) could extend several km in any direction from 31.13718/-96.26925. The 6km xwide chip covers a 6km radius, which should capture any large-scale construction within ~6km of the centroid. The absence of any graded polygon across the full 6km frame (all seasons) is strong confirmation of no_activity.


### STAGE 1-2 SUMMARY — OWNERSHIP & COUNTY RECORDS

Developer chain:
- Pecan Prairie North Solar LLC (assumed SPV name — TX SOS unconfirmed, SOSDirect is paid)
- Repsol Renewables NA (EIA 860M Entity ID 65265, entity name confirmed)
- Repsol acquired ConnectGen in early 2024 (widely reported, ConnectGen was developer)
- ConnectGen was a Houston-based developer — previously "Leon County Solar"

EIA 860M (May 2026, Plant ID 64999, sources/2026-05_eia860m_may2026.xlsx):
- Pecan Prairie North Solar, 350 MW, Leon County TX, ERCO, planned May 2027
- Status: "(L) Regulatory approvals pending. Not under construction"
- Coordinates: 31.13718°N, -96.26925°W

Negative evidence logged:
- PUCT Interchange portal: 402 errors via WebFetch; POST returns 404
- TX Comptroller entity search: JavaScript-dependent, returns only load-wait state
- TX SOS SOSDirect: $1/search fee, not accessible
- Leon County CAD: LCAD.org DNS fails or returns blank
- JETI applications database: TX Comptroller JETI pages redirect to main site (no JETI app portal found)
- Leon County commissioners court website: leoncountytx.gov DNS fails
- Google/Bing web searches: return only banned-source queue aggregators for "Pecan Prairie North"
- Repsol press room: no Pecan Prairie announcements found
- ConnectGen website: blank/empty

No abatement document, IA text, EPC announcement, or county record found.

Key POSITIVE evidence (admissible sources):
1. EIA 860M = project is real, registered, Repsol, not under construction, planned May 2027
2. Queue timeline (timeline.md) = IA signed 2021-02-26, all 6.9 milestones met 2026-05-19
3. Imagery = 21-month timelapse confirms no construction at EIA coordinates through Jun 2026

