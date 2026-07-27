# Dossier — Erika Solar (24INR0303)

Researched 2026-07-20 · site 32.5367, -96.22112 · verdict **real_active**

## 1. Verdict

- **real_active** — EIA reports "Under construction, more than 50 percent complete" (March–May 2026); $19.9M LC posted; all 6.9 milestones complete; three signed IA amendments all [CONFIRMED](sources/2026-07-20_puct_35077-1691_interconnection-agreement-between-oncor-electric.pdf) with INR in PDF
- Construction: **racking/active** (EIA >50% as of 2026-05), first activity date not bracketed (CDSE unavailable)
- Site: 32.5367, -96.22112 — EIA-860M plant coords + IA Exhibit C "6.5 miles SE of Kaufman TX on FM 1836", med confidence ([satellite view](https://www.google.com/maps/@32.5367,-96.22112,5000m/data=!3m1!1e3))
- COD: reported 2027-06-30 → independent **2027-Q3**, drift risk **med** (EIA COD 2026-12 vs queue 2027-06; equipment swap Oct 2025; 4 prior slips)

## 2. Site identification

- Derivation: EIA-860M plant 69585 'Kaufman Solar' entity 'Kaufman Solar, LLC' reports coords 32.5367, -96.22112 (Kaufman Co, 200 MW, solar); consistent with IA Exhibit C: "Healy Switching Station approximately 6.5 miles south east of Kaufman, TX, on FM 1836" ([IA Exhibit C](sources/2026-07-19_puct_35077-1691_interconnection-agreement-between-oncor-electric.pdf), p.27)
- **Stated project area: not obtainable** — no Ch.313/JETI application filed; CAD portal requires interactive session; no acreage found
- Cross-checks: EIA coords ↔ IA POI description agree (FM 1836, SE of Kaufman city) — within expected range; Google Places "Kaufman Solar construction" returned no pin
- Not obtainable: exact Healy Switch coordinates (not in public domain); CDSE imagery blocked (RemoteDisconnected throughout run); no satellite confirmation

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Kaufman Solar, LLC | SPV | [Original IA](sources/2026-07-19_puct_35077-1691_interconnection-agreement-between-oncor-electric.pdf) parties page; [Amend 3](sources/2026-07-19_puct_35077-2293_amendment-no-3-to-the-standard-generation-interc.pdf) header "GIR 24INR0303 – Kaufman Solar, LLC (Erika Solar)" |
| Parent/developer | unknown | TX Comptroller search inaccessible; search backends failed; no press releases found |

- Financing: $19,899,031 Irrevocable Standby LC posted (per [Amend 2 Exhibit E](sources/2026-07-19_puct_35077-2197_amendment-no-2-to-the-standard-generation-interc.pdf)); security raised from $14.1M at signing — consistent with construction progress

## 4. Land & county records

- Tenure: **unknown** — Kaufman CAD portal requires interactive browser session; no parcels retrieved
- Abatements/agreements: no Ch.312/313 or JETI filing found (ch313.py: negative; post-2022 project, absence expected)
- CAD: 0 parcels retrieved (portal inaccessible via WebFetch)

## 5. Interconnection & contractual schedule

- POI per signed IA: "Healy Switching Station to be constructed within TSP's Elkton Switch to Tri Corner Switch 345 kV transmission line… 6.5 miles SE of Kaufman TX on FM 1836" ([IA Exhibit C](sources/2026-07-19_puct_35077-1691_interconnection-agreement-between-oncor-electric.pdf), [one-line diagram](sources/2026-07-19_puct_35077-1691_interconnection-agreement-between_p40.png))
- Equipment (Amend 3, Oct 2025): 52 × **GE LV5+ FLEX 1566** solar inverters × 4.58 MVA = 238.16 MVA gross, 200 MW at POI — changed from original 57 × Power Electronics HEM 4105M

| IA document | Signed | Financial security posted |
|---|---|---|
| Original SGIA ([pdf](sources/2026-07-19_puct_35077-1691_interconnection-agreement-between-oncor-electric.pdf)) | 2023-10-12 | $14,109,499 LC (by 2023-10-17) |
| Amendment No. 2 ([pdf](sources/2026-07-19_puct_35077-2197_amendment-no-2-to-the-standard-generation-interc.pdf)) | 2025-07-14 | $19,899,031 LC (by 2026-05-07; +$5.8M) |
| Amendment No. 3 ([pdf](sources/2026-07-19_puct_35077-2293_amendment-no-3-to-the-standard-generation-interc.pdf)) | 2025-10-17 | unchanged ($19,899,031) — equipment change only |

| Milestone | Original IA (2023) | Amendment No. 2 (2025) |
|---|---|---|
| In-Service | 2025-04-17 | **2026-05-07** |
| Trial Operation | 2025-04-30 | **2026-10-01** |
| Scheduled COD | 2026-02-24 | **2027-06-30** |

- Queue-history COD drift ([timeline.md](timeline.md)): **4 changes** — 2024-08-30 → 2025-08-31 → 2026-07-01 → 2027-07-24 → 2027-06-30; in reports since 2022-07 (48 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-03 | EIA status: (U) construction ≤50% → (V) >50% | [EIA history](eia_history.json) |
| 2026-05 | EIA status: (V) >50% complete (latest report) | [EIA history](eia_history.json) |

- Verdict: **racking/active** — CDSE imagery unavailable (RemoteDisconnected on all attempts); EIA-860M is the sole construction-stage proxy. EIA reports transition from ≤50% to >50% construction between Feb and March 2026, consistent with module installation phase

## 7. COD assessment

- Queue COD 2027-06-30 is contractually grounded in [Amendment No. 2](sources/2026-07-19_puct_35077-2197_amendment-no-2-to-the-standard-generation-interc.pdf) — not a raw estimate
- EIA reports planned COD **2026-12**, 6 months earlier than the queue claim — divergence suggests queue lags EIA update; EIA is based on developer-reported data to federal regulators
- Construction is >50% complete as of May 2026; 200 MW solar typically needs 6–12 months from 50% to COD
- In-Service date per Amend 2 is 2026-05-07 — already past; the queue has not reported construction start, suggesting In-Service milestone may have slipped again
- Equipment switch (Power Electronics → GE LV5+ FLEX) in Oct 2025 implies supply chain reset; may account for the remaining gap vs the 2026-12 EIA target
- Risk factors: 4 prior COD slips; In-Service likely overdue; no construction-start date in queue; parent developer identity unknown; no EPC or offtake press releases
- For: $19.9M LC posted; >50% construction confirmed; all 6.9 milestones complete; FIS approved; active IA amendments through 2025
- **Independent estimate: 2027-Q3, drift risk medium** (EIA says Q4-2026, queue says Q2-2027; splitting the difference and adding one quarter for the overdue In-Service)

## 8. Could not determine

- Parent developer / ultimate owner (TX Comptroller/SOS inaccessible; all search backends failed)
- Satellite imagery — CDSE RemoteDisconnected throughout; no visual construction confirmation
- Land tenure (CAD portal requires interactive session)
- Project acreage (no Ch.313/CAD/abatement docs obtained)
- EPC contractor identity (no press releases found)
- Amendment No. 1 content (PDF not retrieved; signed 2023-12-27 per Amend 3 recital)
- Whether In-Service date (2026-05-07) was met or further slipped
