# Dossier — Camino Santiago Solar (22INR0605)

Researched 2026-07-20 · site ~31.01, -96.90 (Herndon locality, Milam Co — low confidence, CEII-redacted) · verdict **real_early**

## 1. Verdict

- **real_early** — signed IA (PUCT docket 35077-2028) confirmed with $28.5M irrevocable standby LC; Cobra Grupo (ACS Group) institutional developer; Sungrow inverter model specified ([IA p32](sources/2026-07-20_puct_35077-2028_standard-generation-interconnection-agreement-be.pdf))
- Construction: **no confirmed activity** — no queue construction milestones; CDSE imagery unavailable (infrastructure outage 2026-07-20); no Google Places construction pin
- Site: ~31.01, -96.90 — Herndon locality triangulation (Herndon Cemetery 31.041,-96.864; Little Pond Creek 30.986,-96.937); exact coordinates CEII-redacted in IA Exhibit C ([one-line diagram](sources/2026-07-20_puct_35077-2028_standard-generation-interconnecti_p43.png))
- COD: reported 2027-09-01 → independent **2027-Q3 to 2028-Q1**, drift risk **high** (IA COD already 6+ months behind queue; 5 slips total; no construction visible)

## 2. Site identification

- Derivation: IA Exhibit C (p32) states POI is "the proposed Herndon Switch in TSP's Little Pond SW to Hog Creek SW 345 kV line … located approximately [CEII-redacted]" — locality triangulated from Herndon Cemetery (31.041296,-96.863594) and Little Pond Creek (30.986007,-96.937255), both in Milam County ([Exhibit C](sources/2026-07-20_puct_35077-2028_standard-generation-interconnecti_p32.png))
- **Stated project area: not obtained** — no abatement application, CAD parcel, or IA acreage statement found; portal JS-blocked; 196 MW solar ≈ 900–1,400 acres typical
- Cross-checks: Herndon Cemetery (Google Places hit, Rosebud TX 76570), Little Pond Creek (natural feature, Milam Co), Cattlemen 2 Solar Park nearby at 31.083,-96.854 confirms active solar corridor in area
- Not obtainable: exact POI coordinates (CEII-redacted in IA); CAD parcel owner records (JS portal); CDSE imagery (infrastructure outage)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Camino Solar Project, LLC | SPV/Generator | [IA p6-7](sources/2026-07-20_puct_35077-2028_standard-generation-interconnection-agreement-be.pdf) — Oscar Manuel Yunta Toledo, Officer |
| Cobra Grupo (ACS Group subsidiary, Spain) | Developer/owner | [IA Exhibit D](sources/2026-07-20_puct_35077-2028_standard-generation-interconnecti_p48.png) — grupocobra.com emails throughout notices; 580 Westlake Park Blvd #515 Houston TX 77079 |
| Oncor Electric Delivery Company LLC | TSP | [IA p6](sources/2026-07-20_puct_35077-2028_standard-generation-interconnection-agreement-be.pdf) — Jim Greer, EVP/COO |
| Sungrow | Equipment supplier | [IA Exhibit C p32](sources/2026-07-20_puct_35077-2028_standard-generation-interconnecti_p32.png) — 51× SG4400UD-MV-US inverters |

- Financing: LC posted Dec 2024 (Bank of America); no PPA, financing announcement, or EPC contractor found

## 4. Land & county records

- Tenure: **unknown** — IA states Generator will "acquire, or have an option to acquire, or have a perpetual easement" for Herndon Switch Property; no deed or lease in public record
- Abatements/agreements: No Ch.313 (expired 2022) or JETI application found via ch313.py or DDG searches — normal for 2022 entry; Milam County commissioners court minutes searched (no solar project items visible in index)
- CAD: Milam CAD portal JS-blocked — no owner-name search results returned

## 5. Interconnection & contractual schedule

- POI per signed IA: "Herndon Switch in TSP's Little Pond SW to Hog Creek SW 345 kV line, Milam County" — new switchyard, 2× 345kV sources, ring bus, TSP-owned TIF ([Exhibit C p32](sources/2026-07-20_puct_35077-2028_standard-generation-interconnecti_p32.png), [one-line p43](sources/2026-07-20_puct_35077-2028_standard-generation-interconnecti_p43.png))
- Equipment: 51× Sungrow SG4400UD-MV-US at 4.4 MVA each; 224.4 MVA nameplate; 196.3 MW at 34.5kV bus

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA — docket 35077-2028 ([pdf](sources/2026-07-20_puct_35077-2028_standard-generation-interconnection-agreement-be.pdf)) | 2024-12-06 | $28,511,804 Irrevocable Standby LC (Bank of America, effective by 2024-12-06) |

| Milestone | IA Exhibit B |
|---|---|
| In-Service Date | 2026-12-03 |
| Trial Operation | 2027-01-03 |
| Scheduled COD (IA) | **2027-02-18** |

- Queue-history COD drift ([timeline.md](timeline.md)): 5 changes, 2025-07-31 → 2027-09-01 (26-month total slip); most recent change added 7 months vs the IA COD of 2027-02-18

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-20 | CDSE imagery unavailable — infrastructure outage (RemoteDisconnected on all attempts) | — |

- Verdict: **no satellite confirmation** — imagery not obtainable this run; no alternative imagery source available without GMAPS Static API

## 7. COD assessment

- IA COD of 2027-02-18 has already been exceeded by the queue reporting 2027-09-01 — the developer is 6+ months behind their own contractual schedule with no visible construction progress
- Five queue slips spanning 26 months (original 2025-07-31 to current 2027-09-01) indicate persistent execution difficulty ([timeline.md](timeline.md))
- Financial security of $28.5M and IA execution (Cobra Grupo/ACS) signal genuine intent — this is not a paper project; but no amendment has been filed since ([puct.py filings 35077](log.md))
- FIS never approved despite being requested 2023-01-05 (3.5 years) — this is the key gating risk; without FIS, the switchyard and gen tie cannot be finalized
- Cobra's own PR pipeline (Barrett Solar, Rains Co., "first US project", COD Mar 2026; Bynum Solar next, COD Apr 2026) does not mention Camino Santiago at all as of Feb 2026 — corroborates that this project is behind its more-advanced sister project, not ahead of it ([spainuscc.org](log.md))
- Key IA milestones that were due before today: notice-to-proceed design (Dec 2024), metering design to ERCOT (Jun 2025), one-line drawings to TSP (Sep 2025), ROW coordination (Oct 2025), TSP ROW exhibits (Jan 2026), equipment names (Apr 2026) — unclear if any were met; none reflected in queue
- Independent estimate: **2027-Q3 to 2028-Q1**, with slip risk toward 2028-H1 if FIS/ROW issues continue; queue COD of 2027-09-01 is the floor if everything goes smoothly

## 8. Could not determine

- Exact site lat/lon (CEII-redacted in IA; CDSE openEO endpoint down both scans — infra outage, not a negative finding; gmaps.py Places 429-rate-limited this pass)
- Project acreage (no abatement, no CAD hit; IA re-scanned page-by-page, confirmed no acreage exhibit exists beyond the one-line diagram)
- No docket amendment exists (`puct.py filings 35077 --party "Camino"` → 0 beyond base SGIA) — base IA schedule is the only contractual document
- Whether IA notice-to-proceed deadlines (Dec 2024–Apr 2026) were actually met
- EPC contractor identity, PPA offtaker, or financing structure
- Whether FIS is pending or blocked — queue shows no approval after 3.5 years
- Note: two web hits for "Camino Solar" are **namesake false positives**, ruled out via WebFetch — Avangrid's unrelated "Camino Solar PV Park" (California, 57MW) and Grupo Cobra's own PR names **Barrett Solar (Rains Co.)** as zero.e's first US project, with Camino Santiago unmentioned in Cobra's public pipeline as of Feb 2026
