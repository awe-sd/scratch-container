# Dossier — OCI Cobb Creek Solar (25INR0229)

Researched 2026-07-20 · site ~32.1152, -97.0678 · verdict **real_active**

## 1. Verdict

- **real_active** — [IA confirmed](sources/2026-07-20_puct_35077-1898_standard-generation-interconnection-agreement-be.pdf) (Oncor/OCI Hillsboro Solar LLC, $16.7M security posted); EIA-860M reports construction complete as of April 2026 ([eia_history.json](eia_history.json))
- Construction: **substantially_complete** per EIA, awaiting Oncor's Bynum Switch TIF; first activity visible mid-2025 per EIA progression
- Site: ~32.1152, -97.0678 — EIA-860M coords + Google Places "Hill II North yard" (32.136058, -97.061804) both converge on NW Hill County near Milford TX ([satellite view](https://www.google.com/maps/@32.1152,-97.0678,5000m/data=!3m1!1e3))
- COD: reported 2027-12-31 → independent **2026-Q4** (low-end) to **2027-Q1** (TSP delay risk), drift risk **med** (generator ready, Bynum Switch bottleneck)

## 2. Site identification

- Derivation: EIA-860M plant 68481 "Hill Solar II" at 32.1152, -97.06783, Hill Co (county+prime-mover+MW match to 25INR0229) ([eia_history.json](eia_history.json))
- **Stated project area: not obtained** — no Ch.313 application; Hill CAD portal JS-blocked
- Cross-checks: Google Places "Hill II North yard" at 32.136058, -97.061804 near Milford TX (~2.4 km N of EIA coords — within footprint of ~900-ac site); sibling "Hill Solar I" at 32.1673,-97.0699 indicates an OCI solar cluster in this corridor
- Satellite imagery: **unavailable this run** (CDSE out of credits; Google Static Maps disabled) — site fix is EIA candidate + Places pin, not imagery-verified
- Not obtainable: Bynum Switch exact coordinates (CEII-redacted in [IA Exhibit C](sources/2026-07-20_puct_35077-1898_standard-generation-interconnection-agreement-be.pdf))

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| OCI Hillsboro Solar LLC | SPV (legal name) | Party on [IA](sources/2026-07-20_puct_35077-1898_standard-generation-interconnection-agreement-be.pdf) signed 2024-07-24 |
| Hill Solar II, LLC | Probable EIA filing entity | [EIA-860M](eia_history.json) plant 68481, Hill Co, 200 MW, same project by county+fuel+MW |
| OCI (brand) | Developer/parent (suspected) | Prior PUCT item [35077-1251](https://interchange.puc.texas.gov) "OCI SOL LLC (Golinda)" 2021; "OCI Hillsboro" naming pattern |
| HEC Renewable Energy America LLC | Possible developer alias | EIA-860M "OCI Hillsboro" 200 MW entry @ 31.941,-97.021; different coords/COD — may be a separate filings record |

- Financing: $16,707,463 surety posted per [IA Exhibit E](sources/2026-07-20_puct_35077-1898_standard-generation-interconnection-agreement-be.pdf); no press announcement, PPA, or external financing record found (all searches failed)

## 4. Land & county records

- Tenure: **unknown** — Hill CAD JS-blocked; no deed records; no Ch.313/JETI agreement (expected for post-2022 project)
- Abatements: **none found** — ch313.py: NEGATIVE; JETI not publicly indexed; normal for project entering queue 2022
- CAD: 0 parcels retrieved — Hill CAD requires browser session; owner names unidentified

## 5. Interconnection & contractual schedule

- POI per signed IA: "proposed Bynum Switch within TSP's Venus–Sam SW 345 kV transmission line, Hill County, Texas" ([IA](sources/2026-07-20_puct_35077-1898_standard-generation-interconnection-agreement-be.pdf)) — switch is NEW Oncor infrastructure to be constructed
- Equipment (Exhibit C): 54× Power Electronics HEM GENIII FS4010M inverters (4.01 MVA each, 216.54 MVA nameplate, **203.1 MW net**); co-located BESS 25INR0233: 51× FP4200M2 inverters, 201.6 MW net

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-20_puct_35077-1898_standard-generation-interconnection-agreement-be.pdf)) | 2024-07-24 | $16,707,463 surety due 2024-07-31 |

| Milestone | Original IA (2024) |
|---|---|
| In-Service | 2026-05-07 |
| Trial Operation | 2026-09-01 |
| Scheduled COD | **2026-12-01** |

- Queue-history COD drift ([timeline.md](timeline.md)): **5 changes** — 2025-06 → 2026-06 → 2026-07 → 2026-09 → 2026-12 → 2027-12-31; current queue COD is **12 months beyond** IA contractual date

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-01 to 2025-08 | EIA: under construction ≤50% ([EIA record](eia_history.json)) | no imagery |
| 2025-09 to 2026-03 | EIA: under construction >50% ([EIA record](eia_history.json)) | no imagery |
| 2026-04 to 2026-05 | **EIA: construction complete, not yet commercial** ([EIA record](eia_history.json)) | no imagery |

- Verdict: **substantially_complete** per EIA-860M — construction finished ~2026-04; CDSE satellite imagery unavailable this run (out of credits)

## 7. COD assessment

- **Contractual COD = 2026-12-01** (original IA, no amendments filed). Queue COD 2027-12-31 is 12 months beyond this without a filed amendment — highly unusual.
- **EIA says construction complete (TS status) since April 2026** with planned COD 2026-06 (already past). Generator may be physically ready and awaiting interconnection.
- **Probable bottleneck: Bynum Switch** — the IA's POI is a "proposed" new 345 kV switch that Oncor must construct as TIF. TSP infrastructure delays routinely push CODs 6–18 months beyond contractual dates without formal IA amendments. Queue COD 2027-12-31 likely reflects Oncor's revised switch timeline.
- Queue's 5 prior slips pre-date the IA execution — the slips during 2023–2024 are explained by the FIS study process; post-IA slips (2025-12 → 2027-12-31) are likely tied to the Bynum Switch schedule.
- **Independent estimate: 2026-Q4** most likely if Bynum Switch is on track; **2027-Q1** is the delay scenario. Queue's 2027-12-31 appears extreme relative to EIA evidence of construction completion.

## 8. Could not determine

- Exact Bynum Switch location / coordinates (CEII-redacted in IA Exhibit C)
- Land tenure / parcel owner names (Hill CAD JS-blocked; no deed records)
- Developer parent-company chain beyond OCI brand inference
- PPA status, financing details (no news; all web searches failed this session)
- Satellite imagery ground truth (CDSE out of credits; Google Static Maps disabled)
- Project acreage (no Ch.313; no CAD)
- Whether "Hill Solar II, LLC" (EIA) and "OCI Hillsboro Solar LLC" (IA) are legally the same entity
