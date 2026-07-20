# Dossier — NavBoot BESS (25INR0375)

Researched 2026-07-19 · site 27.806, -97.571 · verdict **real_early**

## 1. Verdict

- **real_early** — signed IA (AEP Texas, Oct 2025) + $258.1M EPC contract (SolarMax, Jan 2026) confirm real commitment; no imagery construction signal yet
- Construction: **clearing** (early), first activity not confirmed in imagery
- Site: 27.806, -97.571 — IA Exhibit C "~6 miles east of Robstown, TX"; McKenzie Rd Station OSM node 174705983 (27.8057,-97.5715), medium confidence ([map](https://www.google.com/maps/@27.806,-97.571,5000m/data=!3m1!1e3))
- COD: reported 2027-11-11 → independent **2028-Q1**, drift risk **med** (FIS pending; SolarMax execution risk)

## 2. Site identification

- Derivation: IA Exhibit C states "approximately six (6) miles east of Robstown, Texas"; new "Navboot Substation" connected by 0.25-mile 138kV tap from AEP's McKenzie Rd Station; McKenzie Rd Station located via OSM (way 174705983) at 27.8057,-97.5715 — site within ~0.5 km of that pin
- **Stated project area: not determined** — no CAD parcels, no abatement agreement; compact BESS (~20-80 acres expected)
- Cross-checks: OSM McKenzie Rd Station coords consistent with IA "6 mi E of Robstown"; Google Places "Mc Kenzie Road Sub Station" at 3601 Callicoatte Rd (27.8457,-97.6115) is ~5 km north — different structure, same name; IA is the authoritative reference
- Not obtainable: exact Navboot Substation pad coordinates (Exhibit C coordinates redacted/CEII)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| NavBoot BESS LLC | SPV | TX SOS File 0805452629; party on [AEP Texas IA](https://interchange.puc.texas.gov/Documents/35077_2292_1554642.PDF) (PUCT 35077-2292) |
| Navboot Holdco LLC | HoldCo (Delaware) | Named in [SolarMax 8-K EPC](sources/2026-07-19_sec_solarmax-8k-epc-navboot.html) as EPC counterparty |
| Navitas Energy LLC | Developer | NavBoot LLC (TX) manager = Navitas Energy; IA Exhibit D contact gmanalac@navitasenergy.org |
| GP Manalac | Founder/CEO Navitas | [Leyline PR 2022](sources/2026-07-19_prnewswire_leyline-navitas-energy.html); navitasenergy.org |
| Leyline Renewable Capital | Growth capital investor | [PR Newswire 2022-10-06](sources/2026-07-19_prnewswire_leyline-navitas-energy.html) — non-dilutive, 500-1000 MW ERCOT target |
| SolarMax Renewable Energy Provider | EPC contractor | [GlobeNewswire 2026-01-06](sources/2026-07-19_globenewswire_solarmax-epc-navboot-600mwh.html); [8-K](sources/2026-07-19_sec_solarmax-8k-epc-navboot.html) |

- Financing: status unknown; no project-finance close announced; Leyline growth capital is early-stage only
- PPA offtaker: not identified

## 4. Land & county records

- Tenure: **unknown** — no CAD parcel found under NavBoot/Navitas; no abatement agreement (Ch.312/313/JETI) found; BESS thin county trail expected per playbook
- Abatements: none found (post-2022 project; Ch.313 expired; JETI search not completed)
- CAD: 0 hits for NavBoot, Navitas Energy in Nueces County (expected for compact leased site)

## 5. Interconnection & contractual schedule

- POI per IA: "First dead-end structure outside Navboot Substation fence, on a new 0.25-mile 138kV line with OPGW from AEP's McKenzie Rd Station" — matches queue POI "8858 MCKENZIE4A 138kV" ([IA](https://interchange.puc.texas.gov/Documents/35077_2292_1554642.PDF), PUCT 35077-2292)
- Equipment (Exhibit C): 99× SMA SCS 3800 inverters × 3.06 MW = 302.9 MW; delivery voltage 138kV; storage ~600 MWh (2h duration)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (PUCT 35077-2292) | 2025-10-20 | $7,500,000 (LC / corporate guaranty / cash) |

| Milestone | Original IA (from execution date 2025-10-20) |
|---|---|
| In-Service | +32 months → ~2028-06 |
| Trial Operation | +33 months → ~2028-07 |
| Scheduled COD | +34 months → ~2028-08 |

- Note: Reported COD 2027-11-11 is ~13 months post-IA — more aggressive than the IA's 34-month contractual maximum; likely reflects an optimistic parallel-track assumption
- Queue-history COD drift ([timeline.md](timeline.md)): **2 changes** — 2025-06 → 2026-12 → 2027-11-11; in reports since 2023-03 (40 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-03 | Candidate site (Callicoatte/McKenzie Rd area): suburban fringe, possible graded pad visible; no container rows | [png](imagery/s2_2026-03-01_candidate1.png) |
| 2026-06 | Heavily clouded at candidate 1; candidate 2 (rural) shows no activity | [c1](imagery/s2_2026-06-01_candidate1.png) [c2](imagery/s2_2026-06-01_candidate2.png) |

- Verdict: **clearing/early** — prepared rectangular pad visible at McKenzie Rd substation area March 2026; 10m/px Sentinel-2 cannot confirm BESS container rows; note EPC signed Jan 2026 so mobilization expected late Q1/Q2 2026

## 7. COD assessment

- Reported 2027-11-11 is ~13 months post-IA execution — aggressive vs the IA's own 34-month contractual schedule (implying ~2028-08 maximum)
- 0.25-mile transmission tap is minimal — grid work should not be the bottleneck; but FIS not yet approved as of 2026-06 snapshot is a gate risk
- EPC contract signed Jan 2026 ($258.1M, SolarMax / Nasdaq:SMXT); BESS construction is fast (~12-18 months from mobilization); 2027-11 plausible but tight
- SolarMax is a small-cap company (Nasdaq:SMXT); this is a large contract relative to their scale — execution risk real
- No financing close or offtaker announced — merchant/bilateral risk; project could slip pending financing
- Prior COD drift: twice already (from 2025-06); pattern of optimistic early CODs
- **Independent estimate: 2028-Q1, drift risk medium** — contractual anchor supports late 2027/early 2028; FIS gap and financing risk add ~1 quarter buffer

## 8. Could not determine

- Exact Navboot Substation pad coordinates (Exhibit C CEII-redacted or not publicly available)
- Underlying land parcel ownership / lease counterparty
- Project financing close date or lender
- PPA offtaker
- FERC/PUCT IA PDF directly (HTTP 402 on PUCT interchange; 403 on FERC eLibrary)
- Confirmed container-row imagery (Sentinel-2 10m ceiling; cloud cover in June 2026 chips)
