# Dossier — Darkwood Solar (27INR0049)

Researched 2026-07-20 · site 31.92853, -98.4241 · verdict **real_early**

## 1. Verdict

- **real_early** — signed IA names TotalEnergies-affiliated "Mustang Creek Solar" (195 MWp) as under development with a Google 15-yr PPA ([PR](sources/2026-07-20_totalenergies_1gw-google-ppa-mustang-creek-pressrelease.pdf)); no independent construction confirmation obtained this session
- Construction: **unconfirmed but imminent** — PR states start "Q2 2026" (already past at research date); 4 active TotalEnergies construction-phase job postings; EIA-860M still shows "Not under construction" through its 2026-05 snapshot ([eia_history.json](eia_history.json))
- Site: 31.92853, -98.4241 — EIA-860M filing coordinate, low confidence ([satellite view](https://www.google.com/maps/@31.92853,-98.4241,5000m/data=!3m1!1e3)); cross-checks with a lower-confidence community-post estimate within 6.3 km
- COD: reported 2027-09-20 → independent **2027-Q4**, drift risk **medium** (contractually grounded, but zero verified construction evidence)

## 2. Site identification

- Derivation: no parcel, Places pin, or imagery fix obtained. Best available coordinate is the entity's own EIA-860M filing for plant 68478 "Darkwood Solar" ([eia_history.json](eia_history.json)), operator Mustang Creek Solar I, LLC
- **Stated project area: not obtainable** — no Ch.313/JETI/CAD/IA-exhibit document with acreage was found; imagery footprint could not be checked (CDSE outage this session)
- Cross-checks: EIA coord (31.92853,-98.4241) and triage's Facebook/community-post estimate (31.97,-98.47, near Proctor TX, Evan Ranch/CR328-CR343) are **6.3 km apart** — both cluster near Proctor, consistent with the IA's stated POI (the Comanche Peak Switch–Comanche Switch 345 kV line passes through this stretch of Comanche County), but do not converge tightly enough to call this a fix
- Not obtainable: exact Baggett Switching Station coordinates — the station name returns no hits on OpenInfraMap/web search beyond unrelated "Baggett Creek Cemetery" records, consistent with it being a new, not-yet-built switch specific to this interconnection ([IA Exhibit C](sources/2026-07-19_puct_35077-2307_standard-generation-interconnection-agreement-be.pdf), p.32)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Mustang Creek Solar LLC | SPV / IA signatory | "Generator" party on signed IA, CONFIRMED via INR-in-text match ([IA](sources/2026-07-19_puct_35077-2307_standard-generation-interconnection-agreement-be.pdf), p.6) |
| Mustang Creek Solar I, LLC | EIA reporting entity | EIA-860M plant 68478 "Darkwood Solar" operator of record ([eia_history.json](eia_history.json)) |
| TotalEnergies Renewables USA, LLC | developer/owner | PR: "TotalEnergies-owned sites currently under development... Mustang Creek (195 MWp)" ([PR](sources/2026-07-20_totalenergies_1gw-google-ppa-mustang-creek-pressrelease.pdf)); 4 active construction-phase job postings at Cleburne TX under this legal entity |
| Google LLC | offtaker / PPA | Same PR: 15-yr PPA, part of 1 GW/28 TWh deal with Wichita (805 MWp) + Mustang Creek (195 MWp); quote from Google's Will Conkling ([PR](sources/2026-07-20_totalenergies_1gw-google-ppa-mustang-creek-pressrelease.pdf)) |

- Financing: not disclosed in the PR; no separate financing-close announcement found. The Google PPA (signed, 15-yr, 1 GW combined) is itself strong revenue-certainty evidence for a top-tier public developer (TotalEnergies, 10 GW US portfolio, 5 GW in ERCOT)

## 4. Land & county records

- Tenure: **unknown** — not determined this session
- Abatements/agreements: **negative** — no Ch.313 agreement or JETI application found for "Darkwood Solar" across 740 Ch.313 + 38 JETI rows ([ch313.py resolve](sources/)); normal for a project this size/timing, not itself a red flag
- CAD: not completed — Comanche CAD's search portal (esearch.comanchecad.org) is a JS/Kendo single-page app; curl-based owner-name queries returned only the app shell/redirect, not results. Logged as a tooling gap, not a true negative

## 5. Interconnection & contractual schedule

- POI per signed IA: "The Point of Interconnection is located in Comanche County, Texas, at the proposed Baggett Switching Station within the Company Comanche Peak Switch to Company Comanche Switch 345 kV transmission line" ([IA](sources/2026-07-19_puct_35077-2307_standard-generation-interconnection-agreement-be.pdf), p.32) — matches queue POI text exactly
- Equipment (Exhibit C): Solar — 40× Sungrow SG4400UD inverters, 176 MVA gross / 150.76 MW net at 34.5 kV. Co-located BESS (27INR0050, Darkwood BESS) — 43× Sungrow SC4000UD-MV-US, 172 MVA gross / 150.5 MW net

| IA document | Signed | Financial security posted |
|---|---|---|
| Standard Generation IA ([pdf](sources/2026-07-19_puct_35077-2307_standard-generation-interconnection-agreement-be.pdf)) | 2025 (filed with PUCT 2025-11-14) | $8,224,875 effective on/before 2025-08-04 → $18,111,175 effective on/before 2025-10-31 |

(Single IA document on file; no amendment yet — both security effective dates have already passed as of the 2026-07-20 research date, implying the security has been posted on schedule if the project remains in good standing.)

| Milestone | Original IA (2025) |
|---|---|
| In-Service | May 13, 2027 |
| Trial Operation | May 23, 2027 |
| Scheduled COD | **September 20, 2027** |

- Queue-history COD drift (from [timeline.md](timeline.md)): **1 change** — 2027-01-30 → 2027-09-20 (at the 2025-07-01 snapshot, ~8 months). The queue's revised number lands exactly on the IA's own contractual Scheduled COD.

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2024-06 | Undisturbed farmland at low-confidence triage coordinate (31.97,-98.47) | [2024-06-15](imagery/s2_2024-06-15.png) |
| 2026-06 | All-black frame — no valid Sentinel-2 composite (cloud/data gap) | [2026-06-15](imagery/s2_2026-06-15.png) |

- Verdict: **cannot confirm construction from imagery** — the only chips on file are centered on a low-confidence community-post coordinate, not the EIA-filing coordinate used as this run's best site estimate; CDSE imagery API failed with connection errors on every retry this session (transient service outage, confirmed by a failed reprobe at Hanson Solar's already-verified coordinates)

## 7. COD assessment

- Reported 2027-09-20 is the exact contractual Scheduled COD in the signed, INR-confirmed [IA](sources/2026-07-19_puct_35077-2307_standard-generation-interconnection-agreement-be.pdf) — strongly grounded
- TotalEnergies' own press release states Mustang Creek construction was scheduled to begin Q2 2026 ([PR](sources/2026-07-20_totalenergies_1gw-google-ppa-mustang-creek-pressrelease.pdf)) — roughly 11 months before the IA's May 2027 In-Service Date, a plausible but not generous build window for 150 MW solar + 150 MW BESS
- EIA-860M's own planned-COD figure slipped from 2027-01 to 2027-10 between its 2026-02 and 2026-03 snapshots — an independent second source drifting later, converging within a month of the IA date
- Risk: zero independently-verified construction evidence (imagery down, Places API down, CAD portal unreachable this session); EIA-860M still shows "not under construction" as of its most recent (2026-05) snapshot, the same month the announced Q2 2026 window closes
- For: named, financially credible developer (TotalEnergies, 5 GW ERCOT portfolio) with a signed 15-yr Google PPA; signed IA with financial security scheduled and (per already-passed effective dates) presumably posted; active construction-phase hiring
- **Independent estimate: 2027-Q4, drift risk medium** — nudged one quarter later than the reported COD purely because no independent construction evidence could be obtained this session to corroborate the announced on-schedule start; the contractual and financial fundamentals otherwise support the reported date

## 8. Could not determine

- Exact site parcel/boundary — no map exhibit in the IA, no CAD parcel search completed (portal is a JS SPA unreachable via curl), no acreage figure
- Physical construction status — CDSE Sentinel-2 imagery API failed on every attempt this session (confirmed as a service-side outage via a failed reprobe at an already-verified coordinate); Google Places delivery-pin search was rate-limited (HTTP 429) on every attempt
- Land tenure (leased vs. purchased)
- Exact relationship between "Mustang Creek Solar" (195 MWp, per TotalEnergies PR) and the queue's 150.76 MW net AC figure — plausible DC/AC nameplate difference, not independently reconciled
- Whether "Mustang Creek Solar I, LLC" (EIA) and "Mustang Creek Solar LLC" (IA signatory) are the same entity or a parent/subsidiary pair — not resolved via TX SOS (SOSDirect is a paid service, out of scope)
