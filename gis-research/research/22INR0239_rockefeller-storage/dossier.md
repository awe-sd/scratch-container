# Dossier — Rockefeller Storage (22INR0239)

Researched 2026-07-19 · site 31.0440, -100.5480 · verdict **real_early**

## 1. Verdict

- **real_early** — signed IA (Sep 2024) + $9M security + compact gravel pad confirmed in S2 imagery at site described in IA ([pad frame](imagery/key/s2_2026-07-01.png))
- Construction: **pad/grading**, site prepared; no container rows visible yet (10 m/px ceiling)
- Site: 31.0440, -100.5480 — IA text "Schleicher County ~10 mi north of Eldorado" + S2 imagery pad match, medium-high confidence ([satellite view](https://www.google.com/maps/@31.0440,-100.5480,5000m/data=!3m1!1e3))
- COD: reported 2027-06-01 → independent **2027-Q3/Q4**, drift risk **medium-high** (relative-date schedule; 4 prior slips; no amendment; pad but no containers yet)

## 2. Site identification

- Derivation: IA Exhibit C "Schleicher County approx. 10 miles north of Eldorado, TX" + new Rockefeller Substation → 345 kV line to ETT's Big Hill Station; S2 chip confirms white gravel pad at ~31.044°N, -100.548°W adjacent to Big Hill Station area ([IA](sources/2026-07-19_puct_35077_IA.pdf))
- **Stated project area: not in IA** (no acreage exhibit); footprint ~15 ac estimated from pad dimensions in S2 chip, consistent with 207 MW BESS
- Cross-checks: IA POI "second transmission structure outside fence of Big Hill Station" ([IA](sources/2026-07-19_puct_35077_IA.pdf)) + S2 pad location adjacent to Big Hill Station area
- Not obtainable: exact Rockefeller Substation coordinates (not in IA); Google Maps delivery pin (API rate-limited); Schleicher CAD parcel number (JS-gated portal)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Mittel Rockefeller Storage LLC | SPV / Generator | party on [IA](sources/2026-07-19_puct_35077_IA.pdf) |
| ENGIE IR Holdings LLC | financial entity / parent | bank account in IA [Exhibit D](sources/2026-07-19_puct_35077_IA.pdf) — BofA ABA 111000012, Acct 004451303776 |
| ENGIE North America | developer/owner | contacts tarek.morgan@engie.com + Eric.tarantino@engie.com at 1360 Post Oak Blvd Houston TX ([IA Exhibit D](sources/2026-07-19_puct_35077_IA.pdf)) |
| Electric Transmission Texas (AEP) | TSP / counterparty | [IA](sources/2026-07-19_puct_35077_IA.pdf) |

- Financing: no public financing announcement found; ENGIE parent-guarantee structure permitted by IA Exhibit E

## 4. Land & county records

- Tenure: **unknown** — no CAD parcel found (Schleicher CAD portal is JS-gated; search for Mittel/Rockefeller/ENGIE returned no accessible results)
- Abatements: none found; Ch.313 expired 2022; JETI (HB 1535) search blocked by CAPTCHA — normal for BESS with limited county footprint
- CAD: 0 hits (search blocked by JS/CAPTCHA)

## 5. Interconnection & contractual schedule

- POI per signed IA: "TSP's second transmission structure outside the fence of TSP's Big Hill Station … terminates Generator's 345 kV transmission line from the Substation" ([IA Exhibit C](sources/2026-07-19_puct_35077_IA.pdf)) — matches queue POI "76003 Big Hill 345kV" exactly
- Equipment (Exhibit C): 78 × SMA SCS 2630 UP-XT-US inverters (2.651 MW each) = 206.778 MW; 34.5 kV WSL metering for charging (confirmed BESS, not solar)
- No IA amendments found in PUCT project 35077 records as of 2026-07-19

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077_IA.pdf)) | 2024-09-23 | $9,000,000 LC or corporate guaranty to ETT |

| Milestone | Original IA 2024 (relative from Sections 4.2+4.3 satisfaction) | Approximate calendar date |
|---|---|---|
| In-Service | 31 months | ~2027-04-23 |
| Trial Operation | 32 months | ~2027-05-23 |
| Scheduled COD | 34 months | ~2027-07-23 |

- Schedule anchor: Sections 4.2+4.3 conditions were satisfied at execution (2024-09-23) per IA; 31/32/34-month clock started then
- Queue-history COD drift ([timeline.md](timeline.md)): **4 changes** — 2022-12 → 2023-02 → 2024-12 → 2025-12 → 2027-06; 3-yr capacity gap (0 MW Oct 2021–Jul 2024) indicates prior suspension/re-entry

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| ≤2025-12 | Compact gravel pad (~15 ac) visible adjacent to Big Hill Station; no container rows | [2025-12](imagery/key/s2_2025-12-01.png) |
| 2026-07 | Same pad, same footprint; no visible container installation at 10 m/px | [2026-07](imagery/key/s2_2026-07-01.png) |

- Verdict: **pad/grading** — site prepared and graded; no container deployment confirmed at S2 resolution; CDSE auth failure prevented pre-Dec 2025 history (cannot confirm 2024 start date)
- Prior imagery unavailable: CDSE credentials expired; cannot bracket first activity date

## 7. COD assessment

- Contractual COD anchor: IA signed 2024-09-23 + relative schedule = ~2027-07-23 In-Service, which slightly lags the reported 2027-06-01
- The IA schedule gives 34 months to COD (≈2027-07); reported COD of 2027-06 is slightly ahead of contractual — either reflects parallel grid work or queue reporting rounding
- Imagery shows pad present as of Dec 2025 but no container rows — BESS containers typically deploy in 6–12 months from pad; a Dec 2026–Mar 2027 commissioning window is plausible if containers arrive in H2 2026
- Risk factors: 4 prior COD slips spanning 5 years; 3-yr 0 MW capacity gap (Oct 2021–Jul 2024) suggests prior withdrawal; no financing announcement; no amendment filed; "Meets all 6.9" milestone NOT achieved (still pending)
- For: IA executed + $9M security posted; ENGIE tier-1 developer; pad constructed; BESS builds fast (12–18 months from pad to COD)
- **Independent estimate: 2027-Q3/Q4, drift risk medium-high** (contractual anchor ~2027-07; 4 prior slips; construction active but pre-container)

## 8. Could not determine

- Exact Rockefeller Substation / site coordinates (no pin, no parcel, CEII-like precision not in IA)
- Construction start date (CDSE credentials expired; pre-Dec 2025 imagery unavailable)
- Container deployment status (S2 10 m/px cannot confirm BESS containers on gravel pad)
- Financing/PPA arrangements (no public announcement found)
- Land tenure (CAD portal JS-gated; no abatement application found)
- SMA SCS 2630 delivery/procurement status
