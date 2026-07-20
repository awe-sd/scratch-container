# Dossier — Aldrin 138 BESS (25INR0421)

Researched 2026-07-19 · site 29.45902, -95.25754 · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed, FIS approved, dedicated developer website active; but NO construction visible in Jul 2026 imagery with 12 months to reported COD ([500m chip](imagery/s2_29.459_95.258_2026-07-01_500m.png))
- Construction: **no_activity**, first activity not yet seen
- Site: 29.45902, -95.25754 — North Alvin TNMP 138kV substation per OSM Overpass API (way 174401064); developer confirms "directly next to an electrical substation" in [Brazoria County](sources/2026-07-19_aldrinenergystorage-com_home.html) ([map](https://www.google.com/maps/@29.45902,-95.25754,5000m/data=!3m1!1e3))
- COD: reported 2027-07-01 → independent **2028-Q2**, drift risk **high** (no construction, NTP gate uncleared, 24 mo prior drift)

## 2. Site identification

- Derivation: POI = "Bus 39015 North Alvin TNMP 138kV"; Overpass API confirmed substation at 29.45902, -95.25754 ([OSM source](sources/2026-07-19_osm-overpass_north-alvin-substation.json)); developer site confirms "less than 12 acres directly next to an electrical substation" ([home](sources/2026-07-19_aldrinenergystorage-com_home.html))
- **Stated project area: <12 acres** per [developer website](sources/2026-07-19_aldrinenergystorage-com_home.html) — imagery footprint consistent (small pad area adjacent to substation visible at 500m chip)
- Cross-checks: OSM substation coords agree with POI description; no contradicting parcel or pin found
- Not obtainable: CAD parcel (portal requires JS); PUCT IA PDF (portal requires JS); exact site address

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Aldrin Energy Storage LLC | SPV | [TX Comptroller](sources/2026-07-19_tx-comptroller_aldrin-energy-storage.html): ACTIVE, DE, eff. 2022-12-19, file 0804862187 |
| Vesper Energy | developer/parent | [Aldrin footer](sources/2026-07-19_aldrinenergystorage-com_home.html): "© 2025 Vesper Energy"; Co-CEO Juan Suarez shared |
| Magnetar Capital | majority equity (since 2020) | [Vesper about](sources/2026-07-19_vesperenergy-com_about-full.html): acquired Lendlease Energy Development 2020 |
| GCM Grosvenor | equity investor (since 2023) | [Vesper about](sources/2026-07-19_vesperenergy-com_about-full.html) |

- Financing: no project-level financing announcement found; Vesper is institutional (Magnetar + GCM Grosvenor equity)

## 4. Land & county records

- Tenure: **unknown** — developer states "privately owned land"; no CAD parcel found under Aldrin (portal JS-blocked); no deed or abatement document retrieved
- Abatements/agreements: none found — expected post-2022 (no Ch.313/JETI for battery projects)
- CAD: 0 hits — portal requires JS rendering; negative logged

## 5. Interconnection & contractual schedule

- POI per queue: "(Bus: 39015) North Alvin TNMP 138kV" — substation confirmed at 29.45902, -95.25754 ([OSM](sources/2026-07-19_osm-overpass_north-alvin-substation.json))
- Equipment: unknown — PUCT Interchange portal requires JS; IA PDF not retrieved

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2024-04-18 (per ERCOT queue) | unknown — PUCT portal inaccessible |

| Milestone | Queue record |
|---|---|
| IA Signed | 2024-04-18 |
| FIS Approved | 2025-08-22 |
| Meets 6.9(1) | 2024-05-06 |
| Meets all 6.9 (NTP gate) | **NOT achieved** as of 2026-06 |
| Reported COD | 2027-07-01 |

- Queue-history COD drift (from [timeline.md](timeline.md)): **2 changes** — 2025-07-15 → 2026-03-01 → 2027-07-01 (~24 months total slip)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-11 | substation visible, no adjacent BESS activity | [2km chip](imagery/s2_29.459_95.258_2025-11-01_2km.png) |
| 2026-07 | substation clear; adjacent land cleared/disturbed; NO container rows or gravel pad | [500m chip](imagery/s2_29.459_95.258_2026-07-01_500m.png) |

- Verdict: **no_activity** — substation confirmed at POI coordinates; <12-acre footprint scale resolved at 10 m/px; no BESS construction signal as of 2026-07-01

## 7. COD assessment

- Reported 2027-07-01 is ungrounded — IA PDF not retrieved, so no contractual milestone dates confirmed beyond the queue record
- No construction visible as of 2026-07-01 with only 12 months to reported COD; a 207 MW BESS requires 12-18 months to build from NTP
- "Meets all 6.9" (NTP gate) not achieved in Jun 2026 queue — project may not yet have NTP authority; this alone pushes COD beyond Jul 2027
- Developer website (last published Jul 2025) still says "could be operational as soon as end of 2025" — frozen messaging ~2 years behind schedule
- 2 prior COD slips totaling ~24 months; repeat slip pattern is high-risk signal
- Vesper's parallel BESS in California (Juniper Creek, 200 MW) also missed its end-2025 COD target — pattern of late-stage slippage
- **Independent estimate: 2028-Q2**, drift risk **high** — NTP uncleared + zero construction + repeat drift history

## 8. Could not determine

- IA PDF and contractual milestone schedule (PUCT Interchange requires JS)
- Financial security amount and NTP status
- Land tenure (CAD portal JS-blocked; no deed found)
- CAD parcel IDs and acreage confirmation
- Whether the 550 MW on developer website vs 207 MW in queue reflects a single-phase filing or project rescope
