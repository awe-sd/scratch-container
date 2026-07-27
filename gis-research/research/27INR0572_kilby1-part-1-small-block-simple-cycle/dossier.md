# Dossier — Kilby1 Part 1 Small Block Simple Cycle (27INR0572)

Researched 2026-07-19 · site ~31.40, -103.50 (low confidence) · verdict **real_early**

## 1. Verdict

- **real_early** — TCEQ air permits 181895/PSDTX1684/GHGPSDTX260 filed Oct 2025 for 2,869 MW Kilby Power Plant + GE Vernova confirmed as primary turbine supplier + 20-yr Microsoft PPA signed Jun 22, 2026 ([sources/T1_web_sweep_notes.md](sources/T1_web_sweep_notes.md)); yet FID not taken as of Jun 23, 2026 and no IA signed
- Construction: **pre_construction** — no site activity in imagery; kilby.com says 2026 = "site prep, engineering, equipment fabrication" ([kilby.com/project](sources/2026-07-19_kilby.com_project.html))
- Site: ~31.40, -103.50 — "near Pecos TX" per news coverage, **low confidence** — no parcel, pin, or IA to tighten ([Pecos TX area](https://www.google.com/maps/@31.40,-103.50,5000m/data=!3m1!1e3))
- COD: reported 2027-11-04 → independent **2028-Q4 to 2029-Q1**, drift risk **high** (FID not taken Jun 2026; no signed IA; thermal build = 3-4 yr)

## 2. Site identification

- Derivation: kilby.com and news confirm "Reeves County near Pecos TX"; Solstice Sub (POI) OSM Way W500535889 = AEP 345/138 kV at **30.9485, -103.3617** in Pecos County ([OSM](https://www.openstreetmap.org/way/500535889)) — gas plant is in Reeves County per queue, presumably NW of sub along a 345 kV tie
- **Stated project area: unknown** — no IA, no abatement application, no CAD parcel found; gas plant area not determinable
- DriveTexas link on kilby.com/contact at zoom 9 (broad area ~-102.66, 31.21) is Pecos County, not useful for pin
- Not obtainable: exact site address or coordinates (no PUCT IA, no abatement, no confirmed Google pin; CDSE auth expired before full grid search)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Energy Forge One LLC | SPV/developer | [kilby.com/about](sources/2026-07-19_kilby.com_about.html); TCEQ permit applicant |
| Chevron Corporation | Parent (100% owner of EFO) | [kilby.com copyright ©2026](sources/2026-07-19_kilby.com_project.html); [EnergyCapitalHTX](sources/2026-07-19_energycapitalhtx_chevron-microsoft-deal.html) |
| Engine No. 1 / Joulent | JV partner / power delivery | [kilby.com/about](sources/2026-07-19_kilby.com_about.html); [EnergyCapitalHTX](sources/2026-07-19_energycapitalhtx_chevron-microsoft-deal.html) |
| Microsoft Corporation | Offtaker (20-yr PPA) | [EnergyCapitalHTX Jun 23 2026](sources/2026-07-19_energycapitalhtx_chevron-microsoft-deal.html) |
| GE Vernova | Primary turbine supplier | [EnergyCapitalHTX](sources/2026-07-19_energycapitalhtx_chevron-microsoft-deal.html): "GE Vernova will supply most of the plant's power capacity" |
| Solar Turbines (Caterpillar) | Secondary turbine supplier | [kilby.com/about](sources/2026-07-19_kilby.com_about.html) |

- Financing: **FID not taken** as of Jun 23, 2026 ([EnergyCapitalHTX](sources/2026-07-19_energycapitalhtx_chevron-microsoft-deal.html): "final investment decision expected later in 2026"); no project financing announcement found

## 4. Land & county records

- Tenure: **unknown** — no land purchase/lease documents found; no CAD parcels under Energy Forge One in Reeves County (0 search results; web-only approach)
- Abatements: none found — Ch.312/313/JETI registry not searched successfully; Reeves County commissioners court website inaccessible
- CAD: Reeves County CAD portal not accessible (propaccess.trueautomation.com timeout)
- TCEQ permit files **Reeves County** as facility location, confirms "near Pecos" ([sources/T1_web_sweep_notes.md](sources/T1_web_sweep_notes.md))

## 5. Interconnection & contractual schedule

- **No IA signed** — PUCT Interchange 402-blocked; queue as of 2026-06-01 shows `iaSigned` not achieved
- POI per queue: #60404 Solstice Substation 345 kV (AEP, confirmed via [OSM W500535889](https://www.openstreetmap.org/way/500535889)); actual location: Pecos County at 30.9485, -103.3617
- TCEQ air permits: 181895 / PSDTX1684 / GHGPSDTX260, filed Oct 16, 2025, public meeting Jun 10, 2026, **still PENDING** ([sources/T1_web_sweep_notes.md](sources/T1_web_sweep_notes.md))

| IA document | Signed | Financial security posted |
|---|---|---|
| No IA found | — | — |

| Milestone | Queue / ERCOT estimate |
|---|---|
| Screening complete | 2026-01-06 |
| FIS approved | not achieved |
| IA signed | not achieved |
| Scheduled COD (reported) | 2027-11-04 |

- Queue-history COD drift ([timeline.md](timeline.md)): **0 changes** — 2027-11-04 held across all 9 snapshots (2025-10 to 2026-06)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | Solstice Sub area (30.9485, -103.3617): undisturbed desert, no construction | [solstice_chip](imagery/s2_2026-07-01_solstice.png) |
| 2026-07-01 | North of sub (31.05, -103.40): undisturbed rangeland, no grading | [north_chip](imagery/s2_2026-07-01_north.png) |

- Verdict: **no_activity** — no construction signature in covered area; exact plant site (Reeves County, near Pecos) not captured due to CDSE credential failure after two chips

## 7. COD assessment

- Reported 2027-11-04 is an ERCOT queue estimate — no signed IA found, so no contractual backing
- **FID expected "later in 2026"** (Jun 23, 2026): assuming FID Oct-Nov 2026, thermal plant of this complexity (15+ turbines, co-located data center) requires 30-42 months to COD → earliest realistic COD for Part 1 = **2029-Q3 to 2030-Q1**; optimistic scenario with aggressive modular approach → **2028-Q4**
- TCEQ air permit still pending: permit issuance typically takes 6-12 months from application (filed Oct 2025); expected permit ~Q2-Q3 2026 — aligns with "2026 site prep"
- Supporting signals: GE Vernova turbine supply confirmed, Microsoft PPA signed, Chevron balance sheet, SCR emissions controls designed — not a paper project
- Risk factors: FID not confirmed, no IA, no construction visible, no turbine delivery news, data center co-location complexity, water supply (brackish groundwater, produced water reuse)
- **Independent estimate: 2028-Q4 to 2029-Q1 for Part 1 Small Block; drift risk HIGH vs. reported 2027-11-04**

## 8. Could not determine

- Exact site coordinates (no PUCT IA, no abatement, CDSE expired; only "near Pecos, Reeves County" confirmed)
- Project area in acres (no IA, no abatement application)
- TCEQ permit final issuance date (pending as of research date)
- FID date (expected "later in 2026" but not yet announced)
- Turbine model numbers or confirmed delivery schedule
- Reeves County CAD parcel records (portal unavailable)
- Specific phasing breakdown for Part 1 vs. Parts 2/3/4 within the 2.67 GW total project
