# Dossier — Zeus Spade Wind (26INR0386)

Researched 2026-07-18 · site 32.3546, -100.9505 · verdict **paper**

## 1. Verdict

- **paper** — no signed IA ([PUCT 0 records for Spade Wind / Zeus Renewable / Zeus Spade / Spade BESS](sources/2026-07-18_puct-interchange_spade-wind-0-records.html)); no built or planned turbines in [USGS uswtdb Mitchell County](sources/2026-07-18_uswtdb_mitchell-county.json); no land in [Mitchell CAD 2025 roll](sources/2026-07-18_mitchell-cad_2025-appraisal-roll.xlsx); no developer web presence
- Construction: **no_activity** — undisturbed ranchland ([2026-07 contact sheet](imagery/2026-07_contact-sheet_18x18km.png))
- Site: 32.3546, -100.9505 — POI-infrastructure only (Morgan Creek tap area), low confidence ([satellite view](https://www.google.com/maps/@32.3546,-100.9505,5000m/data=!3m1!1e3))
- COD: reported 2027-03-20 → independent **2029-Q4 at the earliest, more likely cancelled**, drift risk **high** (pre-FIS, no IA, no land, no dev presence)

## 2. Site identification

- Derivation: POI text "Tap 345 kV 1030 Morgan Creek to 76030 Gasconades Creek" places the tap on the existing Morgan Creek–Gasconades Creek 345 kV line, near the Morgan Creek substation ~5 mi SW of Colorado City, TX ([satellite view](https://www.google.com/maps/@32.3546,-100.9505,5000m/data=!3m1!1e3))
- **Stated project area: unavailable** — no abatement, no signed IA, no CAD parcel; imagery footprint check: N/A (no footprint)
- Cross-checks: no delivery pin found ([gmaps places rate-limited in triage](log.md)); FAA OE portal was in Maintenance mode ([oeaaa.faa.gov/oeaaa/oe3a/main](https://oeaaa.faa.gov/oeaaa/oe3a/main/#/home)) so no turbine coords retrievable; USGS wind DB has zero Spade/Zeus entries in the county
- Not obtainable: exact turbine coordinates (FAA OE portal in maintenance); anchor site — because none of the four independent site anchors converged, the lat/lon is the POI vicinity, not the site

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Spade Wind, LLC | SPV | [TX Comptroller franchise data, SOS 0804549070, chartered 2022-05-02](sources/2026-07-18_tx-comptroller_spade-entities.json) |
| Zeus Renewable Energy Development, LLC | developer parent | Same-suite tenancy at 500 W 2nd St Ste 1900 Austin TX, chartered 2022-04-27, 5 days before Spade Wind LLCs ([suite-1900 tenants](sources/2026-07-18_tx-comptroller_suite-1900-tenants.json)) |
| — | EPC | Not identified — no press release, no delivery pin, no filed document |
| — | Offtake / PPA | Not identified — 0 SEC/EDGAR full-text hits; no offtake announcement |

- Financing: **no announcement** — SEC EDGAR full-text "Spade Wind" = 0 records; no domain, no LinkedIn public page, no news release found for Zeus Renewable Energy Development LLC (portfolio SPVs — Mitchell Solar I/II/III, Armstrong Solar, Houston County Solar, Rusk Solar — pattern of numbered county-labelled shells consistent with queue-position speculation) ([suite-1900 tenants](sources/2026-07-18_tx-comptroller_suite-1900-tenants.json))

## 4. Land & county records

- Tenure: **unknown** — no path to a lease record; no purchased parcels
- Abatements/agreements: **none** — JETI (HB 5) doesn't cover wind ([current JETI agreements list, 11 agreements, none renewable](https://comptroller.texas.gov/economy/development/prop-tax/jeti/current-agreements.php)); Ch.313 expired 2022-12-31 and doesn't apply to this 2024-queued project; no county-level Ch.312 minutes retrievable (Mitchell County Commissioners page has no online agenda archive)
- CAD: **0 parcels** under Spade Wind / Spade BESS / Zeus Renewable Energy / any Suite-1900 owner in Mitchell County's [2025 certified appraisal roll](sources/2026-07-18_mitchell-cad_2025-appraisal-roll.xlsx) (33,459 parcels searched). Only wind-farm owners in the county are RWE (Champion, Inadale, Roscoe) and Loraine Windpark — unrelated

## 5. Interconnection & contractual schedule

- POI per signed IA: **no IA signed** — [PUCT filing search](sources/2026-07-18_puct-interchange_spade-wind-0-records.html) returns 0 records for Spade Wind, Zeus Renewable, Zeus Spade, Spade BESS. Queue milestone `iaSigned=null` in the 2026-06-01 ERCOT report — consistent
- Equipment: not specified — no exhibit available

| IA document | Signed | Financial security posted |
|---|---|---|
| — | none on file | — |

- Queue-history COD drift ([timeline.md](timeline.md)): **0 changes** — COD 2027-03-20 held flat across all 15 monthly snapshots (2025-04-01 through 2026-06-01). This is not a positive: a project that never updates its schedule despite zero progress is not being actively managed.

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07 | Undisturbed West Texas ranchland + Colorado City Lake, no turbine pads, no access-road networks, no substation construction across an ~18 km x 18 km grid centered on the POI | [contact sheet](imagery/2026-07_contact-sheet_18x18km.png), [center chip](imagery/2026-07_morgan-creek-center.png) |

- Verdict: **no_activity** — reported construction start date 2025-08-01 has passed without any visible activity ~11 months later. Wind at 987 MW would require ~150-200 turbines strung across 20-40 km, far too large to miss at the 18-km grid resolution used. CDSE credential auth failed today (HTTP 401) so a newer full-scale xwide frame was not obtainable; the July 2026 grid from triage is the most recent obtainable evidence.

## 7. COD assessment

- **Not contractually grounded** — reported COD 2027-03-20 has no supporting IA. The IA-to-COD industry gap for a ~1 GW wind project is 24-36 months; a 9-month window from today is impossible without a signed IA
- Observed pace vs schedule: reported construction start 2025-08-01 shows no imagery activity 11 months later → schedule is aspirational, not being executed
- Risk factors: no developer web presence, no PPA, no financing, no EPC, no CAD parcels or leases discoverable, JETI ineligible; federal wind permitting pause (Trump DoD review, 54 TX projects) — additive tail risk
- **Independent estimate: 2029-Q4 at the earliest** if FIS approval lands 2026-H2 → IA countersign 2026-Q4 → financing/PPA/EPC 2027 → construction 2028 → commissioning 2029. More likely: withdrawn before IA — the SPV pattern (numbered county-name shells at a shared Austin office with no public identity) is a hallmark of queue-position speculation

## 8. Could not determine

- Exact turbine coordinates (FAA OE portal in "Maintenance Notification" on the day of research)
- Ultimate parent/investor above Zeus Renewable Energy Development LLC (no web presence, no SEC filings, no press releases)
- Land control status (no CAD ownership, no lease document, no abatement application)
- Whether this project is on the federal Trump-administration wind permitting pause list
- Whether the "construction start 2025-08-01" reported in the queue is a placeholder or a genuine developer claim — either way, no evidence supports it
