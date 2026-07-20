# Dossier — Rubicon Alpha Wind (24INR0291)

Researched 2026-07-19 · site unknown (FAA/GMaps blocked) · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed, all interconnection gates cleared, developer is NextEra Energy Resources ([TX Comptroller](sources/2026-07-19_txcomptroller_throckmorton-wind-llc.json)); no construction started yet
- Construction: **no_activity** — zero construction milestones in queue; no ground disturbance in imagery of likely site areas
- Site: UNKNOWN — FAA OE shutdown, Google Places quota exhausted, Haskell CAD JS-blocked; Pendulo 345kV bus (60507) in Haskell County; Monarch Creek Wind at ~33.21°N,−99.46°W is nearby (different project); county-level estimate only ([satellite view](https://www.google.com/maps/@33.15,-99.6,70000m/data=!3m1!1e3))
- COD: reported 2027-07-31 → independent **2028-Q2**, drift risk **high** (no construction start 14 mo after IA; 2 prior slips)

## 2. Site identification

- Derivation: POI "60507 pendulo7A 345kV" → Pendulo 345kV substation, Haskell County TX; county confirmed per queue data ([timeline.md](timeline.md))
- POI history: changed Nov 2025 from "Tap 345kV 60791 Perigee – 6235 Abilene Mulberry Creek" (Jones County) to "60507 pendulo7A 345kV" — suggests scope/route revision
- **Stated project area: not obtainable** — no abatement (Ch.313 expired), no IA PDF retrieved, no CAD parcels
- Cross-checks: none achieved — FAA turbine coords unavailable (shutdown), no delivery pin, no parcel situs
- Not obtainable: exact site coordinates; Pendulo substation lat/lon (OSM blocked, ERCOT NOM not public)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Throckmorton Wind, LLC | SPV | [TX Comptroller](sources/2026-07-19_txcomptroller_throckmorton-wind-llc.json) — 700 Universe Blvd, Juno Beach FL 33408; DE LLC formed Nov 2023 |
| NextEra Energy Resources | developer/owner | Same address (NextEra HQ); officers Matthew Roskot (Pres), Anthony Pedroni, C. Zajic et al. are NextEra employees ([Comptroller](sources/2026-07-19_txcomptroller_throckmorton-wind-llc.json)) |
| EPC | unknown | Not found — pre-construction |
| Offtaker | unknown | Not found |

- Financing: unknown — no press releases, no PPA announcements found; pre-construction

## 4. Land & county records

- Tenure: **unknown** — no CAD parcels found under Throckmorton Wind or NextEra; land likely under lease (typical for wind); landowner names not identified
- Abatements: none found — Ch.313 expired Dec 2022; no JETI/Ch.312 found in county records
- CAD: 0 hits under LLC name (Haskell CAD JS-rendered, owner-name API blocked; negative result unverified)

## 5. Interconnection & contractual schedule

- POI per queue data: "60507 pendulo7A 345kV" — Pendulo 345kV substation, Haskell County ([timeline.md](timeline.md))
- TSP: Electric Transmission Texas (ETT/AEP) — confirmed via triage web sweep ([sources/t3_web_sweep.md](sources/t3_web_sweep.md))
- IA PDF not retrieved — PUCT interchange requires JavaScript; triage reference to control 35077 was a different 2007 docket

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2024-05-08 | Unknown — PDF not retrieved |

| Milestone | Queue data |
|---|---|
| Scheduled COD | 2027-07-31 |
| IA signed | 2024-05-08 |
| FIS approved | 2026-03-13 |
| Meets all 6.9 | 2026-04-30 |
| Construction start | — (none) |

- Queue-history COD drift ([timeline.md](timeline.md)): **2 changes** — 2024-08-30 → 2027-07-01 → 2027-07-31; in reports since 2022-04-01 (51 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | NE Haskell County (~33.21N,-99.46W): Monarch Creek Wind turbines visible; no Rubicon site identified | [png](imagery/s2_test_monarch_2026-07-01.png) |
| 2026-07-01 | Haskell town center (33.17N,-99.73W): undisturbed farmland, no turbine construction | [png](imagery/s2_candidate2_33.17_-99.73.png) |

- Verdict: **no_activity** — no construction milestones in queue (constructionStart=None); imagery of two candidate areas shows undisturbed farmland; site not precisely located

## 7. COD assessment

- Reported 2027-07-31 is contractual per IA (signed 2024-05-08); however, IA exhibits not retrieved — schedule unverified beyond queue date
- No construction started as of Jul 2026 — 14 months post-IA with zero ground activity
- Wind project construction typically requires 18-24 months from first turbine pad; to meet Jul 2027 COD, construction must start by ~Sep 2026 and run perfectly — extremely tight
- Two prior slips totaling 3 years (2024-08-30 original → 2027-07-31 current); pattern suggests timeline optimism
- For: NextEra is a Tier-1 developer with strong execution track record and financial depth; all interconnection gates cleared; project is serious
- Against: no physical activity 14 months post-IA; wind construction cannot be compressed below ~18 months; FAA turbine permits likely not yet filed (OE portal shutdown masks this)
- **Independent estimate: 2028-Q2, drift risk HIGH** — absent ground-break evidence within ~90 days, a 2028 COD is more credible than 2027

## 8. Could not determine

- Exact site coordinates (FAA OE shutdown; Google Places daily quota exhausted; CAD JS-blocked)
- Pendulo 345kV substation lat/lon (OSM errors; ERCOT nodal data not public)
- IA schedule exhibits and financial security amounts (PUCT interchange JS-rendered)
- Turbine model, hub height, rotor diameter (no FAA filings accessible)
- Offtaker / PPA status (no press releases found)
- Landowner names and parcel IDs (no CAD hits under LLC; Ch.313 expired)
- Project area in acres (no abatement, no IA exhibits)
