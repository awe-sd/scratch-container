# Dossier — Zeus Spade BESS (26INR0387)

Researched 2026-07-19 · site 32.33583, -100.91556 · verdict **paper**

## 1. Verdict

- **paper** — No IA filed (PUCT confirmed 0 records), FIS still pending 18 months after request, zero real-project signals (no developer identity, no financing, no abatement, no construction)
- Construction: **no_activity** — existing Morgan Creek power plant visible in imagery; no BESS pad, grading, or containers ([center chip](imagery/s2_center_2026-06-15.png))
- Site: 32.33583, -100.91556 — [Wikipedia Morgan Creek Steam Electric Station coordinates](https://en.wikipedia.org/wiki/List_of_power_stations_in_Texas) + POI bus match, high confidence for substation location ([map](https://www.google.com/maps/@32.33583,-100.91556,5000m/data=!3m1!1e3))
- COD: reported 2028-03-20 → independent **2029-Q2 at earliest / likely abandonment**, drift risk **high** (no IA, FIS overdue, 1 slip already)

## 2. Site identification

- Derivation: Wikipedia "List of power stations in Texas" gives Morgan Creek Steam Electric Station at 32°20'09"N 100°54'56"W = 32.33583, -100.91556; POI "Tap 345 kV 1030 Morgan Creek" matches ERCOT bus #1030 at that station
- **Stated project area: not found** — Mitchell CAD requires OAuth login; no IA or abatement filed; project area unverifiable
- Cross-checks: triage estimate (32.33, -100.91) within 450m of Wikipedia coords; satellite chips show existing industrial plant consistent with power station location; no BESS construction visible
- Not obtainable: exact BESS pad location within Morgan Creek substation footprint; Gasconades Creek bus #76030 coordinates (CEII/not published)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Zeus Spade BESS, LLC | SPV | Queue record |
| "Spade BESS" | Claimed developer | Tracker aggregators only (banned sources — no primary) |
| Unknown | Parent / developer | 0 primary sources found |

- Financing: **none found** — no press releases, no PUCT filings, no SEC Form D; TX Comptroller returns no entity for "Zeus Spade"; TX SOS requires paid access

## 4. Land & county records

- Tenure: **unknown** — Mitchell CAD requires OAuth login; no parcels accessible
- Abatements/agreements: none found (Ch.313 expired 2022; JETI portal inaccessible; 0 commissioner court records found for Spade/Zeus)
- CAD: 0 parcels retrievable (portal auth-gated); expected thin trail for BESS site (compact footprint, likely leased industrial parcel at existing substation)

## 5. Interconnection & contractual schedule

- **No IA filed** — PUCT Interchange search confirmed 0 records for "Zeus Spade" (both FilingParty and UtilityName), "Spade BESS", and all variants as of 2026-07-19
- FIS requested 2025-01-24; **not yet approved** as of latest queue snapshot (2026-06-01) — 17 months and counting; typical FIS turnaround is 6-12 months
- POI per queue: "Tap 345 kV 1030 Morgan Creek to 76030 Gasconades Creek" — no signed IA to confirm details

| IA document | Signed | Financial security posted |
|---|---|---|
| No IA found | — | — |

| Milestone | Status |
|---|---|
| FIS requested | 2025-01-24 |
| FIS approved | not achieved |
| IA signed | not achieved |
| Financial security | not posted |

- Queue-history COD drift (from [timeline.md](timeline.md)): **1 change** — 2027-03-20 → 2028-03-20 (slipped 1 year in Jun 2026 snapshot); project in queue 17 months with no milestone advances beyond FIS request

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-06-01 | Eastern edge farmland/creek drainage — undisturbed | [triage chips](imagery/contact_sheet.png) |
| 2026-06-15 | Morgan Creek Steam Electric Station — existing plant, no BESS pad/containers | [center 1km](imagery/s2_center_2026-06-15.png) |
| 2026-06-15 | 3km xwide — Lake Colorado City, power plant, agricultural land; no new construction | [xwide](imagery/s2_xwide_2026-06-15.png) |

- Verdict: **no_activity** — site occupied by existing gas power plant; no BESS construction at any stage visible; CDSE auth expired before confirmed fresh chips at refined coords (32.33583, -100.91556); visual coverage adequate for no_activity call

## 7. COD assessment

- Reported 2028-03-20 is unsupported — no signed IA exists; the date is a queue placeholder
- FIS approval is overdue: 18 months elapsed since FIS request with no approval recorded; until FIS clears, IA cannot be signed; until IA is signed, construction cannot start
- BESS construction is fast (~12-18 months), so the build schedule is not itself the bottleneck — the entire pre-construction process (FIS → IA → NTP → groundbreaking) is the constraint
- 0/5 real-project signals: no developer identity, no financing, no PPA, no land rights, no abatement
- Optimistic path: FIS Q3-2026, IA Q1-2027, NTP Q2-2027, build 15 months → COD ~2028-Q3; but optimistic assumes FIS imminent, which no evidence supports
- **Independent estimate: 2029-Q2 at earliest; more likely 2029-H2 or project cancellation; drift risk high**

## 8. Could not determine

- Developer parent company (TX SOS requires paid account; no primary source surfaced)
- Exact BESS pad location within Morgan Creek substation
- Mitchell CAD parcels (OAuth-gated portal)
- FIS approval timeline (no ERCOT milestone data accessible)
- Whether companion project Zeus Spade Wind (26INR0386, 987 MW) shares developer — no primary source
