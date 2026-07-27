# Dossier — Tokio Solar (23INR0349)

Researched 2026-07-20 · site 31.42742, -97.31086 · verdict **real_early**

## 1. Verdict

- **real_early** — signed IA with $7.88M financial security posted, SPV confirmed in PUCT and EIA-860M; but EIA status "(P) Planned, regulatory approvals not initiated" held all 38 months of reporting with no construction visible ([IA](sources/2026-07-19_puct_35077-1720_generation-interconnection-agreement-between-onc.pdf))
- Construction: **no_activity**, first activity not yet seen
- Site: 31.42742, -97.31086 — EIA-860M plant-name match (plant 66397), confirmed by GEM wiki; consistent with IA Exhibit C "Sunflower Switch ~16 miles SW of Waco TX off Hwy US-84 W" ([Exhibit C](sources/2026-07-19_puct_35077-1720_generation-interconnection-agreem_p32.png)) ([map](https://google.com/maps/@31.42742,-97.31086,5000m/data=!3m1!1e3))
- COD: reported 2027-08-25 → independent **2028-Q3 or later**, drift risk **high** (no FIS, no construction, 2 prior EIA slips since IA signing)

## 2. Site identification

- Derivation: EIA-860M plant 66397 coords (31.42742, -97.31086), cross-confirmed by GEM wiki (same pin, cites EIA-860M); IA names POI as "Sunflower Switch in TSP's Waco West Sub–Temple Elm Creek Switch 138 kV Line, McLennan County" approx 16 miles SW of Waco off US-84 W — measured 12.8 miles SW of Waco center, directionally consistent ([Exhibit C](sources/2026-07-19_puct_35077-1720_generation-interconnection-agreem_p32.png))
- **Stated project area: not obtained** — no Ch.313/JETI abatement doc, McLennan CAD is JS-gated; acreage unknown
- Cross-checks: EIA-860M pin ↔ GEM wiki ↔ IA POI text — agree within 5 km; no CAD parcel or Places pin obtained
- Not obtainable: exact parcel boundaries, CAD acreage; CDSE imagery at confirmed coords (openEO endpoint down this session)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Gransolar Texas Eight, LLC | SPV | [IA](sources/2026-07-19_puct_35077-1720_generation-interconnection-agreement-between-onc.pdf) CONFIRMED (INR in PDF); EIA-860M |
| Gransolar Group (Spain) | Developer/parent (100%) | [GEM wiki](https://www.gem.wiki/Tokio_Solar) |
| Oncor Electric Delivery | TSP | [IA](sources/2026-07-19_puct_35077-1720_generation-interconnection-agreement-between-onc.pdf) |
| EPC / offtaker | Unknown | Not found |

- Financing: $7,882,720 irrevocable standby LC posted by 2023-11-08 per Exhibit E; no PPA or construction financing announcement found
- Note: Triage flagged possible Adapture Renewables attribution (from banned aggregator); no primary-source transfer evidence found; Gransolar Group remains current owner per GEM wiki (2026-07-20 update)

## 4. Land & county records

- Tenure: **unknown** — no CAD parcel record obtained (portal JS-gated); no deed or lease in public sources
- Abatements/agreements: no Ch.313 (expired Dec 2022) or JETI application found — expected for 2023 project, does not indicate paper
- CAD: McLennan CAD (esearch.mclennancad.org) returns empty to curl queries — negative evidence logged

## 5. Interconnection & contractual schedule

- POI per signed IA: "Sunflower Switch in TSP's Waco West Sub – Temple Elm Creek Switch 138 kV Line, McLennan County, Texas… approximately 16 miles SW of Waco, Texas off of Hwy US-84 W" ([Exhibit C](sources/2026-07-19_puct_35077-1720_generation-interconnection-agreem_p32.png))
- Equipment: 59 Sungrow SG3425UD_MV inverters; 202.08 MVA / 177.64 MW dispatched; 138 kV delivery

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077-1720_generation-interconnection-agreement-between-onc.pdf)) | 2023-11-06 | $7,882,720 irrevocable standby LC |

| Milestone | Original IA (2023) |
|---|---|
| In-Service Date | 2025-05-08 |
| Trial Operation | 2025-04-27 |
| Scheduled COD | **2025-08-25** |

- Queue-history COD drift ([timeline.md](timeline.md)): 3 changes, 2024-10-31 → 2025-03-24 → 2025-08-25 → **2027-08-25** (net +34 months from original)
- IA COD was 2025-08-25; current queue COD is 2027-08-25 = exactly 2-year slip post-IA

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | Agricultural farmland at POI substation vicinity (31.41, -97.15 — confirmed-coords chip failed) | [png](../s2_center_2026-07-01.png) |

- Verdict: **no_activity** — CDSE openEO endpoint down this session; no chip obtained at confirmed coords (31.4274, -97.3109); triage chip at substation vicinity shows undisturbed agriculture; EIA status "(P) Planned, regulatory approvals not initiated" corroborates
- Frame reads used: 1/6 budget (triage image only)

## 7. COD assessment

- **IA COD already missed**: original contract COD was 2025-08-25, which has passed; queue now shows 2027-08-25 (+24 months), already a known slip
- **EIA confirms same drift pattern**: 2025-08 → 2026-08 → 2027-08 over 38 months of reporting; never upgraded from "(P) Planned"
- **FIS not approved**: FIS requested 2022-04-14 but not approved as of latest queue snapshot — this is the most anomalous signal; IA was executed without FIS, unusual (IA typically follows FIS)
- **No construction evidence**: EIA status, absence of news, absent CAD trace, no Places pin — all consistent with pre-construction
- **Independent COD estimate**: assuming construction start in 2H 2026 (optimistic) + 12–15 months build time → earliest **2028-Q1**; more conservatively **2028-Q3** given ongoing FIS gap and current pace. Reported 2027-08-25 appears unreachable without an immediate construction start and no further delays.
- **Drift risk: high** — FIS gap unresolved; COD has slipped 3× in queue, 3× in EIA; no construction commenced; developer has only 1 ERCOT project and no visible construction momentum

## 8. Could not determine

- Exact project parcel(s) and acreage (CAD JS-gated; no abatement doc)
- Land tenure (leased vs. purchased)
- EPC contractor / PPA offtaker
- Whether Adapture Renewables acquired project rights (triage flag; no primary source)
- Satellite ground truth at confirmed coords (CDSE openEO down during session)
- FIS status explanation (why approved-without-FIS pattern occurred)
