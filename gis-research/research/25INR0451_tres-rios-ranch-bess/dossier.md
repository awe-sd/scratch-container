# Dossier — Tres Rios Ranch BESS (25INR0451)

Researched 2026-07-19 · site unknown · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed 2025-12-30 (confirmed queue milestone) + POI substation Twelvemile (bus 76008) confirmed in-service 2025-05-30 per [ERCOT TPIT 6719A](sources/ercot_tpit_twelvemile_6719.txt)
- Construction: **no_activity** (confidence: low — no satellite imagery possible without site pin)
- Site: not established — no delivery pin, no CAD parcel, PUCT IA blocked
- COD: reported 2027-12-31 → independent **2028-Q1**, drift risk **medium** (tight 24-month window, developer unknown, 1 prior 2-yr slip)

## 2. Site identification

- Derivation: not established — gmaps 429, Nominatim empty, Upton CAD portals inaccessible, PUCT IA text blocked (402)
- **Stated project area:** not found (no abatement, no IA exhibit, no CAD parcel)
- Cross-checks: none possible — no pin to cross-check
- POI substation Twelvemile (bus 76008) is in **Pecos + Crockett counties** per [TPIT 6719A](sources/ercot_tpit_twelvemile_6719.txt); BESS site is in Upton County per queue; BESS likely connects via gen-tie ~20–30 km north of the Twelvemile sub
- Not obtainable: exact Twelvemile substation lat/lon (not in OSM, HIFLD, or public GIS; ERCOT nodal coords are CEII); exact BESS site parcel

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Tres Rios Ranch BESS, LLC (unverified) | SPV | queue project name only; TX Comptroller API 403, TX SOS paid |
| Unknown | developer | zero public footprint; no news, no PR, no web presence |
| Unknown | EPC | not found |
| Unknown | offtaker / PPA | not found |

- Financing: unknown — no press release, no PUCT filing text

## 4. Land & county records

- Tenure: **unknown** — no parcel data retrieved
- Abatements: none found; expected for post-2022 BESS (Ch.313 expired 2022; JETI portal returned errors)
- CAD: Upton County CAD portals (upton.cad.state.tx.us, trueautomation cid=163) — DNS/session errors; 0 searches completed

## 5. Interconnection & contractual schedule

- POI: "76008 Twelvemile 345kV" — on the **STEC 345-kV Bakersfield–Schneeman Draw double-circuit line**; substation addition circuit 1 confirmed in-service 2025-05-30, circuit 2 planned, per [ERCOT TPIT 6719A/6719B](sources/ercot_tpit_twelvemile_6719.txt); TSP = LCRATSC
- Equipment: unknown (IA text not retrieved)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2025-12-30 | unknown — IA text blocked (PUCT 402) |

| Milestone | Queue data |
|---|---|
| IA signed | 2025-12-30 |
| FIS approved | never (anomaly — possibly waived) |
| Scheduled COD | 2027-12-31 (reported claim) |

- Queue-history COD drift (from [timeline.md](timeline.md)): **2 changes** — 2025-12-31 (2023-05 to 2024-07) → 2027-12-31 (2024-08 to present; ~2-yr slip)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| (none) | No imagery run — no site pin established | — |

- Verdict: **no imagery** — PLAYBOOK prohibits county-centroid search; no lat/lon to chip around

## 7. COD assessment

- Reported 2027-12-31 is 24 months from IA signing (2025-12-30); BESS builds typically 12–18 months — feasible only if procurement (equipment + EPC) started at or before IA
- POI substation infrastructure is confirmed in-service per TPIT 6719A (ISD 2025-05-30) — positive signal; interconnection capacity exists
- Risk factors: no developer ID, no financing announcement, FIS never achieved despite IA signed, zero web footprint, prior 2-year COD slip
- For: IA is the biggest commitment gate; having it signed without any web presence is unusual but not impossible for a family-office or smaller developer
- **Independent estimate: 2028-Q1, drift risk medium** — one quarter slip from reported COD; could slip further if developer is undercapitalized

## 8. Could not determine

- Developer identity and parent chain (TX SOS paid; Comptroller API blocked)
- Exact BESS site location in Upton County (no pin from any source)
- IA parties, security amount, and contractual schedule exhibits (PUCT 402)
- Whether FIS not achieved is a waiver, a data lag, or a red flag
- Any satellite evidence of site preparation or construction
- PPA counterparty, EPC contractor, or project financing status
