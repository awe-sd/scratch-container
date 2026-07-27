# Dossier — STP Unit2 High Pressure Turbine Upgrade (27INR0557)

Researched 2026-07-18 · site 28.79556, -96.04889 · verdict **real_early**

## 1. Verdict

- **real_early** — underlying asset is an operating licensed nuclear reactor (Unit 2 of the South Texas Project, in commercial operation since 1989-06-19, NRC docket 05000499, license to 2048-12-15) ([Wikipedia infobox](sources/2026-07-18_wikipedia_south-texas-nuclear.html)); the ERCOT queue paperwork is at its earliest possible stage ([timeline.md](timeline.md))
- Construction: **operating (interior modification)** — HP rotor swap during a scheduled refueling outage; not visible from Sentinel-2 as new earthworks
- Site: 28.79556, -96.04889 — Wikipedia authoritative infobox for existing licensed plant, high confidence ([satellite view](https://www.google.com/maps/@28.79556,-96.04889,5000m/data=!3m1!1e3))
- COD: reported 2027-04-23 → independent **2027-Q2**, drift risk **medium** (physical outage-window anchor; no IA yet)

## 2. Site identification

- Derivation: STP infobox coordinates ([Wikipedia](sources/2026-07-18_wikipedia_south-texas-nuclear.html)) — an operating licensed plant, not a speculative site to pinpoint
- **Stated project area: 12,200 acres** (site total) per [Wikipedia](sources/2026-07-18_wikipedia_south-texas-nuclear.html) — imagery footprint check unverified this session (CDSE credentials rejected; existing triage chips off-center)
- Cross-checks: capacity 2×1,354 MW gross matches "list of largest power stations" figure of 2,760 MW ([Wikipedia list](https://en.wikipedia.org/wiki/List_of_largest_power_stations_in_the_United_States)); cancelled STP 3&4 were spec'd at 1,356 MWe/unit — same size class ([WNA USA](http://world-nuclear.org/information-library/country-profiles/countries-t-z/usa-nuclear-power))
- Not obtainable: independent laydown/staging imagery this session (CDSE HTTP 401 `invalid_grant`)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| STP Nuclear Operating Company (STPNOC) | Operator | [Wikipedia infobox](sources/2026-07-18_wikipedia_south-texas-nuclear.html) — NRC-licensed operator, dockets 05000498/499 |
| Constellation Energy | Owner 44% | [Wikipedia](sources/2026-07-18_wikipedia_south-texas-nuclear.html); acquired from NRG per Wikipedia footnote to World Nuclear News "NRG exits nuclear with sale of South Texas Project stake" (retrieved 2023-06-28; WNN URL 404 in this environment) |
| CPS Energy (San Antonio) | Owner 40% | [Wikipedia](sources/2026-07-18_wikipedia_south-texas-nuclear.html) |
| Austin Energy | Owner 16% | [Wikipedia](sources/2026-07-18_wikipedia_south-texas-nuclear.html) |

- Financing: not separately documented — an internal-modification capex funded through owner-consortium operating cash flow / capital plan; no project-financing announcement found. Search access severely limited this session ([log.md](log.md)).
- INR applicant entity name (LLC search): **not confirmed** — TX Comptroller taxable-entity search is a JavaScript SPA and returned no data via WebFetch; SOSDirect is paid-only. Most likely applicant is STPNOC (as licensed operator) or Constellation, but this is not evidenced.

## 4. Land & county records

- Tenure: **purchased** — original 12,200-ac plant site + 7,000-ac cooling reservoir, developed 1970s-80s ([Wikipedia](sources/2026-07-18_wikipedia_south-texas-nuclear.html)); no new land required for HPT swap
- Abatements/agreements: none expected for an internal turbine replacement at an existing industrial property (Ch.313 sunset 2022; JETI targets new investment). Not searched in depth — low-value thread for this project type.
- CAD: not searched — no new parcel involvement expected; the plant occupies known Matagorda County parcels under STPNOC/owners

## 5. Interconnection & contractual schedule

- POI per queue identity: "5915 SO_TEX__345A 345 kV" — the existing STP 345 kV switchyard (SO_TEX prefix consistent with the South Texas nuclear switching station). No signed IA obtained this session ([log.md](log.md)); PUCT Interchange returned HTTP 402 across all endpoints.
- Equipment: HP-turbine rotor replacement in the Unit 2 turbine building; specific OEM (Siemens/GE/Mitsubishi/Toshiba/Doosan) not found in accessible sources this session
- **Contractual schedule: no documents obtained.** ERCOT queue history is the only reachable evidence — see [timeline.md](timeline.md):

| Milestone | Status |
|---|---|
| Screening started | 2026-04-30 |
| FIS requested | 2026-04-29 |
| FIS approved | — |
| IA signed | — |
| Financial security posted | **No** |

- Queue-history COD drift ([timeline.md](timeline.md)): **1 change, direction unusual (pulled IN)** — 2027-07-31 → 2027-04-23 between 2026-04 and 2026-05 snapshots; capacity unchanged at 1,336.52 MW across all 3 snapshots

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-06-01 SE quadrant | rural/agricultural land NE of plant, plant island NOT in frame, partly cloudy | [png](imagery/s2_2026-06-01_SE.png) |
| 2026-06-01 W quadrant | heavy cloud, road curve, plant island NOT in frame | [png](imagery/s2_2026-06-01_W.png) |

- Verdict: **operating (existing licensed reactor)** — HPT work is interior to the turbine building and would show at most a modest laydown yard at 10 m Sentinel-2 resolution. No fresh imagery obtained this session (CDSE HTTP 401 `invalid_grant`); triage chips were off-center and cloud-obscured.

## 7. COD assessment

- Reported 2027-04-23 has a physical anchor absent from most queue CODs: **HP-turbine rotor swaps occur only inside scheduled refueling outages** (US PWR cycle 18-24 months, outage window 30-45 days). A spring-2027 outage window structurally frames the date.
- COD moved IN 3 months (2027-07-31 → 2027-04-23) between snapshots 1 and 2 — atypical direction; consistent with the operator locking to a firm outage schedule
- Against: no FIS approval, no signed IA, no financial security — the ERCOT contractual pipeline is at zero; the schedule risk is procedural rather than physical
- 1,336.52 MW = the full re-registered gross output of Unit 2 (matches Wikipedia's 1,354 MW gross-per-unit within ~1%), not a marginal uprate increment — standard ERCOT re-registration for a material generator modification
- **Independent estimate: 2027-Q2, drift risk medium** — the outage-window physical constraint bounds slip to ~±6 months; IA execution in H2-2026 is the critical path

## 8. Could not determine

- INR applicant LLC (Comptroller SPA blocked; SOSDirect paid); the "STP Unit2 High Pressure Turbine Upgrade, LLC" name in the identity packet is unverified — a project-specific LLC may not exist and the applicant may be STPNOC or Constellation directly
- Signed IA / financial security amount (PUCT Interchange HTTP 402 across all endpoints)
- NRC ADAMS docket for a license amendment or 10 CFR 50.59 evaluation on the turbine change (adams.nrc.gov DNS unresolved, nrc.gov info-finder 403)
- Turbine OEM (Siemens / GE / Mitsubishi / Toshiba / Doosan) — no accessible PR / trade press this session (DDG CAPTCHA, Bing false-positive noise, Google search error, world-nuclear-news.org URLs 404)
- Fresh, on-target Sentinel-2 imagery of the plant island (CDSE credentials rejected as `invalid_grant`)
