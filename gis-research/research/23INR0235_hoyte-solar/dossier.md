# Dossier — Hoyte Solar (23INR0235)

Researched 2026-07-20 · site ~30.783, -96.865 · verdict **real_active**

## 1. Verdict

- **real_active** — Ferrovial SE acquired SPV for USD 19M (Jun 2025), committed EUR 174M PP&E; [20-F Dec 2025](sources/2026-07-19_sec_ferrovial_20F_annual2025_milano-solar.html) confirms "under construction in Texas, expected 2027"
- Construction: **active_construction**, visible in [2026-07-10 imagery](imagery/s2_2026-07-10_center.png) (road grid + graded area + parallel rows)
- Site: ~30.783, -96.865 — IA Exhibit C text "~5.0 miles north of Milano", Milam County ([map](https://www.google.com/maps/@30.783,-96.865,5000m/data=!3m1!1e3)); LOW-MEDIUM confidence (no parcel/CAD/pin obtained)
- COD: reported 2027-04-15 → independent **2027-Q2**, drift risk **medium** (In-Service date Dec 2025 already missed; 5 prior slips; Ferrovial institutional anchor)

## 2. Site identification

- Derivation: [IA Exhibit C](sources/2026-07-19_puct_35077-1514_interconnection-agreement-between-oncor-electric.pdf) states "Cannon Switch ~5.0 miles north of Milano, Milam County" → approx 30.783N, -96.865W
- **Stated project area: not found** — no Ch.313/JETI filing; no CAD owner-name hit; acreage unknown
- Cross-checks: [TPIT row 99344](sources/2026-07-19_ercot_tpit_cannon-switch.xlsx) confirms bus 3707 = Cannon Switch 138kV, Milam County, Oncor; [imagery chip](imagery/s2_2026-07-10_center.png) shows activity in the 30.75–30.81N, 96.80–96.87W area
- Not obtainable: exact Cannon Switch coordinates (CEII); parcel boundaries; Places pin (GMaps 429 throughout)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Milano Solar, LLC | SPV | [IA Exhibit D](sources/2026-07-19_puct_35077-1514_interconnection-agreement-between-oncor-electric.pdf); [PUCT docket 35077](sources/2026-07-19_puct_35077-2503_amendment-no-2-to-the-standard-generation-interc.pdf) |
| Electerra (Austin TX) | Original developer | [IA Exhibit D](sources/2026-07-19_puct_35077-1514_interconnection-agreement-between-oncor-electric.pdf) — dan@electerra.dev; sold to Ferrovial |
| Ferrovial Energy US, LLC | Current owner | [SEC 6-K Jun 2025](sources/2026-07-19_sec_ferrovial_6K_june2025_milano-solar-acquisition.html) — $19M acquisition |
| Ferrovial SE (NYSE: FER) | Ultimate parent | [20-F subsidiary list](sources/2026-07-19_sec_ferrovial_20F_subsidiary-list.html) |
| EPC | Unknown | Not named in any filing; Ferrovial 6-K noted "negotiating EPC contracts" at Jun 2025 acquisition |
| Offtaker | Unknown | Ferrovial 6-K: "negotiating PPAs" at acquisition; not confirmed in 20-F |

- Financing: EUR 174M PP&E additions in 2025 "fundamentally due to Milano Solar acquisition" ([20-F](sources/2026-07-19_sec_ferrovial_20F_annual2025_milano-solar.html)); EUR 32M bank guarantees issued for Milano Solar; no project-finance close confirmed in public filings

## 4. Land & county records

- Tenure: **unknown** — no CAD parcels found under Milano Solar or related names; Milam CAD portal JS-rendered
- Abatements/agreements: No Ch.313 or JETI agreement found — expected for 2023-vintage project; Comptroller portal not accessible for confirmation
- CAD: 0 hits (owner-name search blocked by JS rendering); county commissioners agendas showed no Milano Solar / Hoyte Solar references

## 5. Interconnection & contractual schedule

- POI per signed IA: "Cannon Switch 138kV, ~5.0 miles north of Milano, Milam County — Milano–Robertson 138 kV line section" ([IA](sources/2026-07-19_puct_35077-1514_interconnection-agreement-between-oncor-electric.pdf))
- Equipment per Amendment 2: 54× **Sungrow SG4400UD** inverters, 206.75 MW at 34.5 kV bus ([Amend 2](sources/2026-07-19_puct_35077-2503_amendment-no-2-to-the-standard-generation-interc.pdf))

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077-1514_interconnection-agreement-between-oncor-electric.pdf)) | 2022-10-14 | LC $3,662,558 → $8,142,020 |
| Amendment No. 1 ([pdf](sources/2026-07-19_puct_35077-2462_amendment-no-1-to-the-standard-generator-interco.pdf)) | 2023-11-16 | LC $9,793,633 (increased from Amend 1) |
| Amendment No. 2 ([pdf](sources/2026-07-19_puct_35077-2503_amendment-no-2-to-the-standard-generation-interc.pdf)) | 2026-05-27 | Exhibit E unchanged (Amend 1 amount stands) |

| Milestone | Original IA | Amendment 1 | Amendment 2 |
|---|---|---|---|
| In-Service | 2024-04-18 | 2025-05-08 | **2025-12-12** |
| Trial Operation | 2024-05-01 | 2025-05-18 | **2026-12-16** |
| Scheduled COD | 2024-06-01 | 2025-09-30 | **2027-04-15** |

- Queue-history COD drift ([timeline.md](timeline.md)): **5 changes**, 2023-12-31 → 2024-06-01 → 2025-09-30 → 2026-03-31 → 2026-12-15 → 2027-04-15

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-10 | Active construction: white road grid + graded polygon (lower-left); dark parallel rows = modules/racking (lower-center) | [png](imagery/s2_2026-07-10_center.png) |

- Verdict: **active_construction** — imagery consistent with active site; CDSE endpoint down, no timelapse or prior frames obtainable this session

## 7. COD assessment

- Contractual COD 2027-04-15 is the Amendment 2 schedule ([Amend 2 filed Jun 2026](sources/2026-07-19_puct_35077-2503_amendment-no-2-to-the-standard-generation-interc.pdf)), agreed by Ferrovial-owned Milano Solar LLC
- In-Service date was Dec 12, 2025 — already past as of this research; construction still active in Jul 2026 → TIF/GIF not yet energized or Oncor work ongoing
- Trial Operation due Dec 16, 2026 (5 months away); COD Apr 15, 2027 (9 months away)
- For: Ferrovial institutional backer (EUR 32M guarantees, EUR 174M committed PP&E, NYSE-listed), construction visually active, Amendment 2 signed just 7 weeks ago (May 2026 = fresh commitment), all ERCOT milestones met
- Against: In-Service date missed; 5 historical COD slips; PPA and EPC not confirmed in SEC filings as of Jun 2025 acquisition; EIA shows 214 MW candidate still at "Planned" status through May 2026
- **Independent estimate: 2027-Q2, drift risk medium** — COD could slip to 2027-Q3/Q4 if Trial Op encounters interconnection delays, but Ferrovial's institutional investment makes 2028+ or abandonment very unlikely

## 8. Could not determine

- Exact Cannon Switch / site coordinates (CEII; IA Exhibit C geographic text only)
- Project acreage (no Ch.313/JETI, no CAD access)
- EPC contractor name (not in any SEC filing)
- PPA offtaker (not disclosed; Ferrovial noted "negotiating" at Jun 2025 acquisition)
- Financial security amount under Amendment 2 (Exhibit E not replaced)
- First construction activity date (single imagery frame; timelapse not available)
- Whether In-Service date (Dec 2025) was achieved or missed (queue shows no energization milestone)
