# Dossier — Sol Marina Energy Center (26INR0241)

Researched 2026-07-20 · site 32.467749, -96.707719 · verdict **real_early**

## 1. Verdict

- **real_early** — signed IA with $17M ISBLC posted, new 345kV switching station (Nimbus Switch) engineered, but no construction started as of Jul 2026 ([IA Exhibit E](sources/2026-07-19_puct_35077-2141_standard-generation-inter_sheet13.png))
- Construction: **no_activity**, first activity not yet seen (no imagery obtained — CDSE infrastructure failure this session)
- Site: 32.467749, -96.707719 — Google Places pin "Sol Marina Energy Center" at 2210 Farrar Rd, Palmer TX 75152, Ellis County ([map](https://google.com/maps/@32.467749,-96.707719,5000m/data=!3m1!1e3))
- COD: reported 2027-10-29 → independent **2028-Q2**, drift risk **med** (no construction started, one open 6.9 milestone, two prior COD slips)

## 2. Site identification

- Derivation: Google Places text search "Sol Marina Energy Center" → pin at 2210 Farrar Rd, Palmer TX 75152, Ellis County ([gmaps.py output](sources/web_sweep_t3.md))
- **Stated project area: unknown** — no Ch.313/JETI application found (program expired post-2022); IA does not state acreage; CAD search blocked (web backend down)
- Cross-checks: Palmer TX is in Ellis County ✓; POI Nimbus Switch on Watermill–Big Onion 345kV line is in Ellis County per IA Exhibit C ✓; Shankle–Pebble Creek 138kV line lowering required (site proximity indicator) ✓
- Site address in IA Exhibit C: **redacted** (black box); all-weather road address also redacted in Exhibit C grading section
- Not obtainable: exact POI switch coordinates (CEII); parcel IDs/acreage (CAD search failed); imagery confirmation (CDSE down)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Sol Marina Energy Center, LLC | SPV | [TX SOS / web sweep](sources/web_sweep_t3.md) — DE domestic, TX foreign, filed 2025-04-14, Active |
| Adapture Solar Development, LLC | Developer/operator | [IA party, Exhibit D](sources/2026-07-19_puct_35077-2141_standard-generation-inter_sheet13.png) — 1601 Harrison St #1630, Oakland CA |
| Adapture Renewables | Parent brand | [Exhibit D domain](sources/2026-07-19_puct_35077-2141_standard-generation-inter_sheet13.png) — adapturerenewables.com, AP@adapturerenewables.com |
| Oncor Electric Delivery | TSP | [IA cover](sources/2026-07-19_puct_35077-2141_standard-generation-interconnection-agreement-be.pdf) — Robert Holt, Fort Worth TX |

- Financing: **$17,035,909 ISBLC posted** by May 1, 2025 ([Exhibit E](sources/2026-07-19_puct_35077-2141_standard-generation-inter_sheet13.png)); irrevocable, transferable, major US commercial bank; no equity/debt financing details found

## 4. Land & county records

- Tenure: **unknown** — IA provides dual provisions (generator owns vs. does not own); no CAD parcel or deed found
- Abatements/agreements: **none found** — Ch.313 expired post-2022; JETI: no entry for Sol Marina or Adapture in 38-row dataset (negative evidence per ch313.py resolve)
- CAD: 0 hits — Ellis County CAD web search failed (DDG backend down all session); cannot confirm parcels by owner name

## 5. Interconnection & contractual schedule

- POI per signed IA: "Point of Interconnection is located in Ellis County, Texas, at Nimbus Switching Station ('Nimbus Switch') in TSP's 345 kV Watermill Switch to Big Onion Switch Transmission Line" ([IA Exhibit C, sheet10 p31](sources/2026-07-19_puct_35077-2141_standard-generation-inter_sheet10.png))
- Equipment: 47 SUNGROW SC4400UD-MV-US inverters; 196.46 MVA gross; **175.26 MW net** at 34.5kV bus; companion BESS 26INR0242 (16 SUNGROW SC4000UD, 57.15–58.6 MW) on same IA

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077-2141_standard-generation-interconnection-agreement-be.pdf)) | 2025-04-25 | **$17,035,909 ISBLC** effective ≤2025-05-01 |

| Milestone | Original IA |
|---|---|
| In-Service | 2027-04-15 |
| Trial Operation | 2027-09-20 |
| Scheduled COD | **2027-10-29** |

- Queue-history COD drift (from [timeline.md](timeline.md)): **2 changes** — 2026-06-30 (held 1 month) → 2027-04-17 (held ~20 months) → 2027-10-29 (current, held 11 months as of Jun 2026)
- Key near-term Exhibit B milestones (past or upcoming): site drawings due Jun 15, 2026 (past); all-weather road for Oncor access Aug 14, 2026; TSP takes TIF deed Sep 15, 2026; generator lat/lon to TSP Oct 15, 2026

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07 | CDSE infrastructure failure — no imagery obtained | — |

- Verdict: **unknown** — CDSE openEO /result and /jobs endpoints returned RemoteDisconnected on all calls this session; construction stage cannot be confirmed from satellite. Queue data and IA milestone structure imply pre-construction (no construction dates filed, panel lat/lon not yet due to TSP until Oct 2026).

## 7. COD assessment

- Contractual COD 2027-10-29 matches the reported queue date exactly — developer set it to the IA schedule
- No construction started as of Jul 2026 (~15 months to contracted COD). A 175 MW solar + new 345kV tap is a 15–18 month build; achievable but requires NTP in Q3 2026
- **Meets All 6.9 not yet achieved** as of Jun 2026 — this is a potential NTP blocker; if it slips to Q4 2026, contracted COD is at risk
- Two prior slips of ~10–12 months each; if pattern repeats, 2028-Q2 is the most defensible independent estimate
- $17M ISBLC and SUNGROW equipment spec confirm developer is committed — this is not a paper project
- EIA-860M absence is normal for a project that has not yet broken ground; not a negative signal at this stage
- Independent COD: **2028-Q2** (one ~6-month slip from contracted; contingent on Meets All 6.9 and NTP by Q3 2026)

## 8. Could not determine

- Project area (acres) — no abatement filing, IA address redacted, CAD search failed
- Exact site parcel IDs — CAD web search backend down all session
- Satellite construction stage — CDSE completely unavailable this session
- Adapture Renewables track record — web search down; no comparable completed project data
- Financial institution for ISBLC — bank account numbers redacted in Exhibit D
- Whether Meets All 6.9 milestone has since been achieved (queue snapshot Jun 2026 is last available)
