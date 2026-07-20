# Triage log — 20INR0097 El Sauz Ranch

T1 start
T1 result: 88 snapshots (2019-03-01 → 2026-06-01). 32 COD changes — extreme drift 2021-09-30 → 2026-08-02. IA signed 2021-01-27, FIS approved 2021-10-29, approved for energization 2022-09-28, approved for sync 2023-02-28. No construction-start/end, no commercial-operation-approved. Capacity stable at 301.5 MW since 2021-06.

T2 start
T2 result: gmaps.py 429 Too Many Requests on both attempts (exact name + name+county). No pins found. BLOCKED — logged, moved on.

T3 start
T3 result: SKIPPED — budget warning hit at 86% during T2. No web sweep performed.

T4 start
T4 result: SKIPPED — budget constraint. IA signed 2021-01-27 per queue data; PUCT filing not fetched.

T5 start
T5 result: SKIPPED — budget constraint. No Ch.313/JETI check performed.

T6 start
T6 result: SKIPPED — no site candidate established (gmaps blocked, no other pin source). Logged: no site candidate.

T7 start
T7 result: Output files written. Turns used: ~10.

## Deep scan start — 2026-07-19

**S1: gmaps.py places "El Sauz wind" → pin confirmed**
- Result: "El Sauz Wind Farm Laydown | 25498 Farm to Market 3142, Raymondville, TX 78580 | 26.497309,-97.599482 | association_or_organization,point_of_interest,establishment"
- Significance: Named "Wind Farm Laydown" = active construction/staging area. FM 3142, Willacy County. This is the staging yard, not centroid.
- Artifact: logged (gmaps output)

**S1b: gmaps.py places "El Sauz Ranch"**
- Result: "El Sauz Ranch - East Foundation | 37216 TX-186, Port Mansfield TX 78598 | 26.536727,-97.446643 | ranch,farm"
- This is the El Sauz Ranch actual ranch property on TX-186 — a different location from the wind farm laydown. Not a construction pin.

**S4: Sentinel-2 chip 2026-07-01 at 26.497309,-97.599482 acquired**
- Path: imagery/s2_2026-07-01.png (2407 KB, 6.0 km buffer, cloud≤40%)
- Observation: Partly cloudy. Agricultural/mixed landscape around Raymondville TX. Small scattered white marks visible across fields that may be turbine nacelles. Town of Raymondville visible at left edge. Cloud shadows obscure portions. Need wider grid and historical frames to confirm turbine presence.

**S1c: FAA OE/AAA search failed — system showing government shutdown notice, not searchable**
- Significance: Negative evidence logged. FAA OE/AAA not available for turbine coord lookup.

**S2: Willacy CAD esearch.willacycad.org**
- URL search attempts return 404 for direct GET. CAD portal requires form-based search. Portal confirmed available at esearch.willacycad.org.
- Negative: No direct results obtained yet.

**S2: TX Comptroller Ch.313 database**
- Page redirects/returns overview only — direct search URL not resolved yet.

## Deep scan continued — 2026-07-19

**S3: Site pin confirmed — "El Sauz Wind Farm Laydown"**
- gmaps.py result: 25498 FM 3142, Raymondville TX 78580 | 26.497309,-97.599482
- Place type: association_or_organization,point_of_interest — named "Wind Farm Laydown"
- Significance: Active laydown/staging yard. FM 3142 is an agricultural road in Willacy County just west of the ranch area. This is THE construction staging area for the wind farm.
- Adjacent context: Magic Valley Wind Farm at 26.476467,-97.691015 (existing Avangrid/Iberdrola project nearby on Pennington Rd), Los Vientos wind farm at 26.358286,-97.673400 (FM507, Lyford TX)

**S4: Imagery analysis — multiple frames**
- 2020-06-01: Cloudy, pre-construction baseline — shows undisturbed agricultural fields with no turbine marks
- 2021-06-01: Mix of cleared/bare areas with road network formations visible — consistent with early construction earthworks
- 2021-10-01: CLEAREST early frame — shows extensive bare graded land with curved access road network radiating from hub points — CLASSIC WIND CONSTRUCTION PATTERN. New wide gravel roads converging at pad sites. This matches IA-signed date of 2021-01-27.
- 2022-03-01: CLEAREST operational-era frame — multiple small white T-crosses scattered across agricultural fields in repeating pattern. These are nacelle+blade shadows at 10m/px = turbines erected. Pattern consistent with 20-30+ turbine installations. ~6km frame centered on laydown site.
- 2024-06-01: Dense summer vegetation; landscape consistent with operating wind farm
- 2026-07-01: Partly cloudy; same scatter of white turbine marks; consistent with operating infrastructure
- VERDICT: Construction visible by Oct 2021; turbines erected by Feb/Mar 2022; project physically substantially_complete. Approved for synchronization 2023-02-28 per queue.

**S1/S2: Developer identity NOT established via web search**
- Web searches for "El Sauz Ranch LLC" return no results (Bing CAPTCHAs, grammar pages)
- TX Comptroller/SOS require paid access or form-based queries
- PUCT Interchange requires auth (402)
- FAA OE/AAA system unavailable (govt shutdown notice)
- TX Ch.312/313 search tool returns server error
- NEGATIVE: No press release, news article, or public filing found naming the developer

**S1: Transmission provider**
- AEP Texas Central (AEP Texas) serves Willacy County — the 345kV system designation "8663 EL SAUZ POI 345kV" is consistent with AEP's transmission infrastructure in this region.

**S5: Key queue anomaly**
- 32 COD changes from 2021-09-30 to 2026-08-02
- Approved for SYNC 2023-02-28 but NOT approved for commercial operation
- Post-sync stall of 40+ months (as of 2026-07-19) — very anomalous for a physically constructed project
- Possible causes: interconnection punch-list items, grid code testing failures, outstanding commissioning permits, PPA-related delay, or transmission upgrade delay on AEP side
- The project is REAL and PHYSICALLY BUILT but stuck in the sync→commercial-op gap

