# Triage log — 27INR0557 STP Unit2 High Pressure Turbine Upgrade

## T1 start
- queue_history.py ran; 3 snapshots (2026-04-01 → 2026-06-01)
- Screening started 2026-04-30; FIS requested 2026-04-29
- No further milestones achieved (no screening complete, no IA, no construction)
- COD drift: 2027-07-31 → 2027-04-23 (pulled in ~3 months between Apr and May snapshots)
- COD drift count: 1

## T2 start
- gmaps.py places "STP Unit2 High Pressure Turbine Upgrade" → HTTP 429 (rate limited)
- Retry "STP Unit2 High Pressure Turbine Upgrade Matagorda Texas" → HTTP 429 again
- T2 budget exhausted (2 calls = max for 429 scenario)
- INFERENCE (not a pin): STP = South Texas Project nuclear plant, Matagorda County. Known site at ~28.794°N, -96.045°W near Bay City, TX. Turbine upgrade to existing Unit 2, not greenfield.
- pins_found: 0 (formal); site candidate: STP nuclear station (high confidence by domain knowledge)

## T3 start
- DDG search "STP Unit 2 high pressure turbine upgrade ERCOT" → no results
- DDG search "South Texas Project Unit 2 turbine upgrade 2027" → no results
- DDG search "27INR0557" OR "STP Unit2 High Pressure Turbine" → CAPTCHA blocked
- DDG search NRC license amendment → CAPTCHA blocked (one retry = budget used)
- NRC ADAMS web portal → HTTP 403
- No web pages saved to sources/ (nothing found directly about this project)
- CONTEXT: STP is South Texas Project (existing nuclear plant, Bay City TX). Unit 2 HP turbine upgrade = uprate to existing licensed capacity (likely power uprate filing with NRC). No LLC/developer news surfaced.
- news_found: false

## T4 start
- PUCT Interchange search (FilingParty=STP Unit2...) → HTTP 402 Payment Required
- PUCT Interchange documents endpoint → HTTP 402
- PUCT Interchange root → HTTP 402
- PUCT main site root → HTTP 402
- Entire puc.texas.gov domain returning 402; portal blocked in this environment
- ia_found: false (portal inaccessible, not confirmed absence)

## T5 start
- TX Comptroller Ch.313 agreements page → general overview page only, no filterable data
- Ch.313 value limitation page → no direct Matagorda County filter
- Ch.313 is expired (sunset 2022); turbine upgrades at existing nuclear plants unlikely to qualify for Ch.313 (industrial property, not new investment)
- JETI registry not directly accessible via WebFetch (no URL tried; T5 budget at 3 calls)
- abatement_found: false (Ch.313 portal inaccessible to direct data; JETI not checked — note for deep scan)
- NOTE: Nuclear uprate at existing plant is unlikely to seek Ch.313/JETI — existing industrial property, not a new standalone project

## T6 start
- Site candidate: STP nuclear plant, ~28.794°N, -96.048°W (domain knowledge, high confidence)
- Attempted 9-chip 3×3 grid; CDSE RemoteDisconnected errors on 7/9; 2 chips written (SE, W)
- Center chip (28.794°N, -96.048°W) → CDSE error
- Built contact sheet from 2 available chips
- SE chip (28.824°N, -96.018°W): rural/agricultural land, Colorado River arc, grid-patterned structures partially visible, heavy cloud cover
- W chip (28.794°N, -96.078°W): heavy cloud cover, road curve
- Plant site not clearly visible in either chip; cooling towers / containment domes not distinguishable
- construction_visible: false (indeterminate — cloud obscured + possible coordinate offset from plant center)
- No full-size frame reads justified (contact sheet insufficient to locate construction activity)

## T7 start
- triage_findings.json written
- triage.md written (10 lines)
- Total turns used: ~28
- STOP

## Deep scan T1
- Wikipedia (accessed 2026-07-18) confirms STP ownership: Constellation Energy 44% / CPS Energy 40% / Austin Energy 16%; operator STPNOC. Per-unit gross ~1,354 MW, net 1,280 MW; thermal 3,853 MWth. Unit 2 license expires 2048-12-15.
- ERCOT INR claim 1,336.52 MW is within ~2% of Wikipedia's gross (1,354 MW); ~4% above net (1,280 MW). Plausible as post-HPT-upgrade net output (marginal MUR-type recovery).
- NRC ADAMS DNS failed (adams.nrc.gov unresolvable in this env); NRC info-finder 403; nrc.gov MUP page 403; stpnuclearoperating.com DNS fail; stpegs.com 404.
- Bing search returning near-total false-positive "STP oil / Stone Temple Pilots" noise — usable content nil.
- Constellation acquired NRG's ~44% stake — search inconclusive but recent per general knowledge (Constellation deal in 2023).

## Deep scan T2 — infra tools all blocked
- CDSE token endpoint returns `invalid_grant` (401) — CDSE_USERNAME/PASSWORD invalid on THIS session, not a rate limit. No new Sentinel-2 imagery obtainable.
- Google Maps: Places API HTTP 429, Static Maps API HTTP 403 ("not activated"). No static map / delivery pin.
- DDG (all endpoints incl. /lite) → CAPTCHA blocked.
- Bing → returns generic false-positive noise ("STP oil", "Stone Temple Pilots").
- Google Search → error page.
- NRC ADAMS: adams.nrc.gov DNS unresolved; nrc.gov/info-finder returns 403.
- PUCT Interchange: puc.texas.gov HTTP 402 across all paths.
- TX Comptroller taxable-entity search is a JavaScript SPA; guest curl returns the shell only; no discoverable JSON endpoint.
- Constellation Energy newsroom → 404 for the news page.
- Wikipedia + Wikipedia only usable open source. Saved to sources/2026-07-18_wikipedia_south-texas-project.html

## Deep scan T3 — capacity sanity check via Wikipedia
- STP infobox: 2× 3,853 MWth thermal; 1,354 MW gross / 1,280 MW net per unit; nameplate total 2,560 MW ([Wikipedia](sources/2026-07-18_wikipedia_south-texas-nuclear.html))
- "List of largest power stations" table lists STP at **2,760 MW total** → **~1,380 MW/unit gross** (higher of two Wikipedia figures)
- ERCOT INR claim **1,336.52 MW** falls within this gross-per-unit band. Interpretation: the INR represents Unit 2's FULL re-rated gross MW post-HPT — not a marginal uprate delta. Standard ERCOT practice for material modifications is to re-register the entire modified unit's capacity.
- Cancelled STP 3&4 ABWR proposal was 2× 1,356 MWe — same size class ([WNA USA nuclear power page](http://world-nuclear.org/information-library/country-profiles/countries-t-z/usa-nuclear-power)); confirms 1,336–1,356 MW per unit is the standard STP number.
- Wikipedia mentions of STP + turbine + uprate: NONE. NRG divestiture ("NRG exits nuclear…" WNN, ref cited 2023-06-28) IS cited by the Constellation Energy Wikipedia article; the WNN article URL 404s here.

## Deep scan T4 — coordinate + no fresh imagery
- Plant infobox coords: **28.79556°N, 96.04889°W** — 5-decimal, satisfies "no county centroids" rule. Method: Wikipedia authoritative infobox for existing licensed nuclear plant.
- Triage chips off-center (SE = 28.824N-96.018W = NE of plant; W = 28.794N-96.078W = W of plant); neither shows the plant island itself; both partly cloudy. Cannot re-fetch (CDSE 401 invalid_grant this session).
- **Construction verdict**: cannot independently assess — but note this is an INSIDE-turbine-hall replacement (HPT rotor swap during refueling outage), not a visible exterior earthworks project. Sentinel-2 would show at most a modest laydown yard even at peak.

## Deep scan T5 — verdict rationale
- Underlying asset (Unit 2) = operating licensed nuclear reactor. Not paper.
- ERCOT queue registration = 3 snapshots old, screening started, no FIS approval, no IA signed, no financial security. Queue paperwork is at its earliest possible stage.
- HPT swaps happen ONLY during scheduled refueling outages (~18-month cycle, ~30-45 day window). The 2027-04-23 COD sits inside a plausible spring-2027 outage window.
- COD drift so far: pulled IN 3 months (2027-07-31 → 2027-04-23) between month 1 and month 2 — unusual direction; either the applicant firmed up the outage schedule or the initial date was a placeholder.
- No air permit needed (no combustion). No TEF. No new water rights (existing reservoir).
- **VERDICT: real_early** — asset is real, but ERCOT contractual pipeline is at zero.
- **Independent COD: 2027-Q2** (matches a spring refueling window). **Drift risk: medium** — no signed IA, no financial security, but a physical constraint (outage window) anchors ±6 months.
