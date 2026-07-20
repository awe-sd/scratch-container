# Dossier — Piedra Solar (25INR0168)

Researched 2026-07-19 · site ~31.80, -96.50 (low confidence) · verdict **real_early**

## 1. Verdict

- **real_early** — TotalEnergies SE lists "Piedra Solar, LLC" as 100%-owned subsidiary in four consecutive 20-F filings 2022–2025 ([2025 20-F](sources/2026-07-19_sec-edgar_totalenergies-2025-20f.html)), and IA is signed + all 6.9 milestones met ([queue timeline](timeline.md)); however no construction activity visible in 13 Sentinel-2 chips across Freestone County
- Construction: **no_activity**, first activity not yet seen
- Site: ~31.80, -96.50 — POI corridor inference only, low confidence ([map](https://www.google.com/maps/@31.80,-96.50,5000m/data=!3m1!1e3))
- COD: reported 2026-12-22 → independent **2028-Q1**, drift risk **high** (no groundbreaking ~5 months from reported COD; 3 prior slips)

## 2. Site identification

- Derivation: geographic inference from ERCOT bus IDs — Navarro (68091) near Corsicana TX (~32.08N, -96.47W), Limestone (46020) near Groesbeck TX (~31.52N, -96.53W); 345kV line runs N-S through Freestone County; tap likely ~31.75-31.85N, -96.45-96.55W
- **Stated project area: unknown** — IA not retrieved (PUCT portal JS-gated); CAD portal under maintenance; no abatement application with map
- Cross-checks: none available — no delivery pin (gmaps 429), no parcel match, no news photos
- Not obtainable: exact tap coordinates (CEII-equivalent in PUCT IA; portal inaccessible), CAD parcel owner-name search (maintenance outage), exact Navarro/Limestone substation coordinates

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Piedra Solar, LLC | SPV | [TotalEnergies 2025 20-F](sources/2026-07-19_sec-edgar_totalenergies-2025-20f.html) subsidiary list |
| TotalEnergies SE (TTE) | 100% owner/developer | [2025 20-F](sources/2026-07-19_sec-edgar_totalenergies-2025-20f.html), [2024 20-F](sources/2026-07-19_sec-edgar_totalenergies-2024-20f.html) (4 consecutive filings) |
| TotalEnergies Renewables USA | Operating entity (inferred) | 1201 Louisiana St Houston address; pattern from Myrtle/Danish Fields/Cottonwood |
| EPC / PPA | Unknown | No press release or announcement found |

- Financing: no press release or project financing announcement found; TotalEnergies has strong balance sheet (self-development likely)
- Texas operating portfolio context: Myrtle Solar ~380MW (2023 COD), Danish Fields ~720MW + Cottonwood ~455MW (2024 COD) — Piedra is next in pipeline ([PV-Tech 2024-09-30](https://www.pv-tech.org/totalenergies-commissions-1-2gw-texas-solar-plus-storage-portfolio/))

## 4. Land & county records

- Tenure: **unknown** — CAD portal under maintenance; no parcel search possible; no abatement application with tract description
- Abatements/agreements: none found (Ch.313 expired 2022; JETI post-2023; no Ch.312 entry); absence expected for 2022-filed project
- CAD: 0 results (portal unavailable)

## 5. Interconnection & contractual schedule

- POI per queue: "Tap 345-kV line Navarro (68091) – Limestone (46020))" — Oncor TSP territory, Freestone County
- IA retrieved: **NO** — PUCT Interchange requires JavaScript; all curl/API attempts blocked (402/404)
- IA signed per queue data: 2024-07-02 (milestone confirmed)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (not retrieved) | 2024-07-02 (per queue) | unknown |

| Milestone | From queue data |
|---|---|
| IA signed | 2024-07-02 |
| Meets 6.9(1) | 2025-09-17 |
| Meets all 6.9 | 2025-10-30 |
| Construction start | — (not in queue) |
| Reported COD | 2026-12-22 |

- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** — 2025-06-01 → 2026-04-20 → 2026-09-30 → 2026-12-22; in reports since 2023-03 (40 snapshots)
- Capacity trimmed: 305.5 → 281.7 MW over history

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07 | 13 chips across Freestone County POI corridor — undisturbed rural/ag land throughout | [contact sheet](imagery/contact_sheet_v2.png) |

- Verdict: **no_activity** — 13 × 2 km buffer chips covering 31.73-31.83N, -96.16 to -96.55W show no solar construction signatures. Note: precise tap location is unknown; search covers the most probable corridor but cannot rule out a site at the far eastern or far western fringe of Freestone County

## 7. COD assessment

- Reported 2026-12-22 is ~5 months away with zero visible ground activity. A 281.7 MW utility solar project requires ~12-18 months of earthwork + racking + electrical. Even if construction began today (July 2026), 2026-12-22 COD is structurally impossible
- The 3 prior COD slips (averaging ~6 months each: Jun 2025 → Apr 2026 → Sep 2026 → Dec 2026) show a pattern of incremental pushes
- All key milestones are complete (IA signed, FIS approved, meets all 6.9) — project IS fundable; TotalEnergies is a credible, well-capitalized developer
- No NTP evidence, no EPC contract, no PPA announced — pre-construction procurement phase likely still underway
- Next realistic slip: Q2-Q3 2026 report will likely push COD to 2027-Q3 or 2028-Q1
- **Independent estimate: 2028-Q1, drift risk high** (no construction by July 2026 with Dec 2026 target; pattern of slips; large project ~500-900 acres requiring full civil campaign)

## 8. Could not determine

- Exact site lat/lon (no parcel, no pin, no abatement map; PUCT IA inaccessible)
- IA document contents (financial security amounts, specific milestone schedule, equipment list)
- EPC contractor, PPA offtaker
- Land tenure (leased vs. purchased)
- CAD parcel IDs (portal under maintenance)
- Project area in acres (IA not obtained)
- Construction start date (none in queue; none visible in imagery)
