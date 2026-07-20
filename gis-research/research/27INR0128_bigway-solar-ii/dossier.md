# Dossier — Bigway Solar II (27INR0128)

Researched 2026-07-19 · site 33.77561, -100.31339 · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed Feb 2025 + active Ch.312 abatement + Road Use Agreement Jan 2026 confirm real project; but [satellite imagery](imagery/key/s2_2026-07-15_present.png) shows zero ground disturbance as of July 2026 (18 months before reported COD)
- Construction: **no_activity**, first activity: not yet visible
- Site: 33.77561, -100.31339 — 10 OTLS survey-abstract polygons from [King County abatement agenda](sources/2026-07-19_king-county_jan2026_agenda.pdf), high confidence ([satellite view](https://www.google.com/maps/@33.77561,-100.31339,5000m/data=!3m1!1e3))
- COD: reported 2027-12-31 → independent **2028-Q4**, drift risk **high** (no construction visible 18 mo before reported COD; FIS unapproved)

## 2. Site identification

- Derivation: Texas GLO OTLS ArcGIS FeatureServer queried by 10 survey-abstract numbers from [King County Jan 2026 agenda](sources/2026-07-19_king-county_jan2026_agenda.pdf); all 10 polygons cluster in northern King County at 33.74–33.81°N, -100.34 to -100.29°W
- **Stated project area: 7,681 acres** (sum of OTLS polygon areas for all 10 abatement tracts) — abatement mentions 175 MW AC of improvements; imagery footprint consistent with undisturbed ranchland of that scale
- Cross-checks: POI description "Tap 345KV #59904 Cottonwood – #60500 Edith Clarke Ckt #2" is consistent with ETT's West Texas 345kV network in King/Knox county area; OTLS tracts all match King County (not adjacent county)
- Not obtainable: Cottonwood substation exact coords (not in OSM/Overpass; PUCT IA not retrieved); Google Places pin (429-blocked throughout); CAD parcel situs addresses (JS-only portal)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Bigway Solar, LLC | SPV | party on IA (PUCT 35077-2069, IA signed 2025-02-15) + [abatement agenda](sources/2026-07-19_king-county_jan2026_agenda.pdf) |
| Stetson Renewables Holdings, LLC | developer/abatement applicant | [King County Jan 2026 agenda](sources/2026-07-19_king-county_jan2026_agenda.pdf): "Name of Applicant for Abatement" |
| NextEra Energy Interconnection Holdings | parent developer | PUCT 35077 filing party per triage T3 web research (source URL blocked at retrieval) |
| EPC | — | not announced |
| Offtaker | — | no PPA announced |

- Financing: not announced; no press releases found for this project

## 4. Land & county records

- Tenure: **leased** (presumed) — ranchland in King County; Stetson/Bigway Solar as "assignee" language in abatement implies underlying landowner leases rather than purchase
- Abatements/agreements: **Ch.312 Second Amendment**, King County Jan 12, 2026 ([agenda](sources/2026-07-19_king-county_jan2026_agenda.pdf)) — Stetson Renewables Holdings LLC and/or Bigway Solar LLC; Reinvestment Zone #2021-01 (original zone predates this queue entry); improvements = solar panels, invertors, substation, roads, collection system, SCADA; **175 MW AC, $210,000,000 estimated cost**; Road Use Agreement also approved (item 2)
- Tracts (from agenda): D&W RR CO (A-1030), MASON A ×2 (A-1160, A-1212), MASSEY JV (A-255), TT RR CO ×2 (A-320, A-1077), I&GN RR CO ×2 (A-309, A-312), BURLESON J (A-13), GROGAN HRS (A-990)
- CAD: search portal JS-only; no parcel owner-name query possible; 0 results from Socrata / API attempts

## 5. Interconnection & contractual schedule

- IA signed 2025-02-15 (queue milestone confirmed); PUCT control 35077, item 2069; TSP = Electric Transmission Texas (ETT/AEP); IA text not retrieved (402-blocked)
- POI: "Tap 345KV #59904 Cottonwood - #60500 Edith Clarke Ckt #2"
- FIS approved: NOT achieved (as of 2026-06-01 queue snapshot)
- Meets all 6.9: NOT achieved

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (PUCT 35077-2069) | 2025-02-15 | not retrieved (402-blocked) |

| Milestone | Original IA |
|---|---|
| In-Service | not retrieved |
| Trial Operation | not retrieved |
| Scheduled COD | not retrieved |

- Queue-history COD drift ([timeline.md](timeline.md)): **2 changes** — 2029-07-01 → 2028-12-31 → 2027-12-31 (both pull-forwards)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-01-15 | Undisturbed ranchland + irrigated pivots; no clearing, no construction | [png](imagery/key/s2_2026-01-15_6mo_back.png) |
| 2026-07-15 | Same character; no ground disturbance in full 6 km view | [png](imagery/key/s2_2026-07-15_present.png) |

- Verdict: **no_activity** — PLAYBOOK early-exit applied (two no-activity reads at present + 6 months back); no solar construction signatures anywhere in 6km frame centered on abatement tract cluster

## 7. COD assessment

- Reported COD 2027-12-31 is contractually unconfirmed (IA schedule not retrieved); it was pulled forward twice from 2029-07 over ~2 years — likely driven by paper milestones (IA signed, abatement amendment) rather than construction progress
- As of 2026-07-19, **zero ground activity** visible at the site; FIS not approved; "Meets all 6.9" not achieved — these are pre-NTP conditions
- A 206 MW solar project requires 12–18 months of civil + electrical construction minimum; without NTP before ~mid-2026, COD 2027-12-31 is physically impossible
- Road Use Agreement approved Jan 2026 = pre-construction permitting; consistent with construction start possibly mid-2026, but not confirmed
- NextEra-scale developer with live abatement and signed IA has real commitment; but COD pull-forward pattern with no visible progress warrants skepticism
- **Independent estimate: 2028-Q4, drift risk high** — if construction starts mid-2026, 18-month build → ~end-2027 optimistically; more likely completion late 2028 given FIS outstanding and no activity visible yet; 2029 slip possible if FIS delayed

## 8. Could not determine

- IA contractual schedule (In-Service, Trial Op, Scheduled COD milestones) — PUCT Interchange 402-blocked
- Financial security amount posted with ETT — IA not retrieved
- EPC contractor — no announcement found
- PPA offtaker — no announcement found
- Exact Cottonwood substation coordinates — not in OSM; CEII if in IA
- Exact NTP date or construction start — no press release, no visible construction
- Stetson Renewables Holdings → NextEra parent chain at primary source (TX SOS paywall; OpenCorporates 0 results)
- Companion project 27INR0127 Bigway Solar I (195 MW, same county/IA) — joint or independent build schedule unclear
