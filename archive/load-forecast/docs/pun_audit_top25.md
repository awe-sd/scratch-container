# PUN over-flagging audit — top 25 flagged stations (recovered 2026-08-15)

Source: Task 07 recon agent. Query: `AWDev.dbo.ercotLoadEstimation_term_bal`
joined to `_station_bal` (`run_id='1'`), stations with `pun_score > 0`,
window **2026-02-19 → 2026-02-26** (168 hours), `pun_total_est_load_mw`
**summed over kv per (station, timestamp) first** (term_bal grain includes kv;
the naive join fans out and understates MW), then averaged over flagged hours.

Classification legend: matched against the confirmed-NCL set
(datacenter sheet ∪ `ercotManuallyUpdatedLoad` roster). UNKNOWN = flagged by
`pun_score>0` but in neither confirmed source.

| Rank | Station | Avg MW (flagged hrs) | Avg pun_score | Hrs flagged /168 | unresolved_xfmr | Classification |
|---|---|---|---|---|---|---|
| 1 | JCK | 799.6 | 0.182 | 168 | 0 | UNKNOWN → **sdalvi 2026-08-15: generator station** (county gloss uncertain: dictionary puts JCK in BRAZORIA/COAST, mapper guesses "Jones Creek"; ruling stands) |
| 2 | RNKSW | 711.8 | 0.083 | 168 | 0 | UNKNOWN → **sdalvi 2026-08-15: has NO PUN load — flag is wrong (over-flagging confirmed at rank 2)**. DENTON/NCENT; real load 20→42 MW avg 2023→2025 |
| 3 | SNDSW | 678.8 | 0.077 | 168 | 0 | **datacenter-sheet-match** (Riot: Rockdale, TX; sheet `dam_mw`=600; ercotStationLoad sees it: 143→612 MW 2021→2023) |
| 4 | DOW | 536.1 | 0.200 | 168 | 0 | **known-NCL** (roster: DOW CHEMICAL) → **sdalvi 2026-08-15: IS a PUN** (correctly flagged; ercotStationLoad still sees 140–290 MW) |
| 5 | LON_HILL | 441.3 | 0.050 | 168 | 0 | UNKNOWN → **sdalvi 2026-08-15: generator** (NUECES/SOUTH) |
| 6 | GBY | 428.4 | 0.083 | 168 | 0 | **datacenter-sheet-match** (ECL: TerraSite-TX1, HARRIS → COAST, bus 40710, sheet `max_mw` 1000, online 2025-07-01) — caught by the Opus gate 2026-08-15. → **sdalvi 2026-08-15: generator** — verified: GBY is the only control station with a populated `GenMW` column and its `WithdrawMW` is net-negative, deepening (−36 → −90 MW 2023→2025). The sheet's TerraSite-TX1 → bus 40710 → GBY mapping is co-located-at-best; do NOT treat GBY WithdrawMW as datacenter load |
| 7 | STEWART | 428.1 | 0.125 | 168 | 0 | UNKNOWN |
| 8 | HCKSW | 389.3 | 0.083 | 168 | 0 | **datacenter-sheet-match** (CyrusOne: DFW7) |
| 9 | BOG | 257.2 | 0.429 | 168 | 0 | UNKNOWN |
| 10 | GILLCR | 167.0 | 0.143 | 168 | 0 | UNKNOWN |
| 11 | AZ | 161.9 | 0.333 | 168 | 0 | UNKNOWN (loose grep hit "Amazon" — false positive, discarded) |
| 12 | FIRON | 155.2 | 0.250 | **25** | 0 | UNKNOWN, partial-week flag |
| 13 | WTRML | 149.7 | 0.091 | 168 | 0 | **datacenter-sheet-match** (Databank: Red Oak DFW9–16 + Skybox: PowerCampus Dallas + Stack: DFW02 Bldgs 2–6, same bus 2429) |
| 14 | SDMSW | 136.1 | 0.333 | 168 | 0 | UNKNOWN |
| 15 | STILES | 118.3 | 0.500 | 168 | 0 | UNKNOWN |
| 16 | OYS | 96.4 | 0.333 | 168 | 0 | UNKNOWN |
| 17 | DPW | 95.4 | 0.250 | 168 | 0 | UNKNOWN |
| 18 | ATKINS | 82.4 | 0.167 | 168 | 0 | UNKNOWN |
| 19 | HUD | 61.9 | 0.667 | 168 | 0 | UNKNOWN |
| 20 | CANAL_RD | 57.3 | 0.500 | **25** | 0 | UNKNOWN, partial-week flag |
| 21 | CL | 41.3 | 0.143 | 168 | 0 | UNKNOWN |
| 22 | BST | 41.0 | 0.333 | 168 | 0 | UNKNOWN |
| 23 | LCSES | 38.9 | 0.077 | 168 | 0 | UNKNOWN → **sdalvi 2026-08-15: generator** (MCLENNAN/NCENT — was a 9%-of-gap candidate, now dead) |
| 24 | MAINLAND | 38.5 | 0.333 | 168 | 0 | UNKNOWN |
| 25 | RYSSW | 37.4 | 0.056 | 168 | 0 | UNKNOWN |

Tally (post Opus-gate correction + sdalvi rulings 2026-08-15): 1 known-NCL
(DOW — sdalvi: real PUN), 4 datacenter-sheet-match (GBY of these ruled
generator), 20 originally-UNKNOWN — sdalvi ruled JCK/LON_HILL/LCSES
generators and RNKSW no-PUN-load → **16 unruled, "rest unclear" per sdalvi**.
Mapper adds: DPW and HUD run always-negative (generator/cogen pattern).
The corrections do NOT overturn the over-flagging finding: the load-bearing
evidence is RNKSW (711.8 MW zeroed by a 0.083 score,
`unresolved_xfmr_count=0`, sdalvi-confirmed no PUN load), untouched.

## VERIFIED 2026-08-15: ercotStationLoad is BLIND to some real large loads

Direct cache reads (`data/raw/station_load/`), yearly avg `WithdrawMW`:

| Station (confirmed NCL, zone) | ercotStationLoad | State estimator (Feb-2026 wk) |
|---|---|---|
| HCKSW (CyrusOne DFW7, TARRANT/NCENT) | **~0.1 MW every year 2021–2026** | **389.3 MW** |
| WTRML (Databank+Skybox+Stack, DALLAS/NCENT) | **~0 MW every year** | **149.7 MW** |
| SNDSW (Riot Rockdale, SCENT) | 143→612 MW 2021→2023 (SEEN fine) | 678.8 MW ✓ |
| DOW (PUN per sdalvi) | 140–290 MW (seen) | 536.1 MW |

Consequences: (1) a ~0 reading in ercotStationLoad CANNOT rule a PUN-flagged
station out (SDMSW/STEWART/GILLCR "~0" readings are INCONCLUSIVE); (2) Task
07's NCENT subtraction under-subtracted the two biggest confirmed NCENT
datacenters (~539 MW combined per SE, Feb-2026) — compounded by their sheet
online dates (2026-07-01) gating them to zero anyway despite the SE showing
them already drawing. The Task 07 "confirmed NCL doesn't explain NCENT"
conclusion is therefore PREMATURE — see project_brief.md §7.

## Recon agent's read (verbatim substance)

- Do NOT read the 84% UNKNOWN share as proof of over-flagging — the roster is
  a different asset class (renewable/gen station-service, mostly negative
  WithdrawMW), so its 1/25 hit rate measures scope mismatch, not flag quality.
  The datacenter sheet is the on-class comparison: 4/25 hits after the GBY
  correction (the recon originally reported 3/25, i.e. 84% unknown at recon
  time; 80% corrected).
- What actually supports the over-flagging suspicion: `pun_score` is a
  small-magnitude continuous score and the exclusion threshold is `>0`.
  RNKSW was flagged 168/168 hours at avg score 0.083 while averaging 712 MW —
  a marginal score zeroes a large load entirely under `clean_plus_internal_mw`,
  with `unresolved_xfmr_count=0` (fully-resolved topology). sdalvi's rank-2
  ruling (no PUN load at RNKSW) confirms this failure mode on the largest
  ambiguous row.
- SNDSW cross-validation: 678.8 MW (SE path) vs 600 MW sheet `dam_mw` for
  Riot Rockdale — two independent paths, consistent magnitude.
- The `isConforming` flag lives on `AW.dbo.ercotManuallyUpdatedLoad`
  (SQL Server), not on the LDF table.
- Namespaces: SE `station` == `NmmsStationCode` (roster, ercotStationLoad);
  the LDF `SUBSTATION` and sheet `dam_bus_name` are DIFFERENT conventions;
  `MRIDLOAD` (GUID) is the only durable cross-source key candidate.

## Next

County/zone + 2019–2026 load history for all 21 originally-flagged rows
(18 still unruled after JCK/RNKSW/GBY) →
`docs/pun_unknowns_map.md` + `data/derived/pun_unknowns_map.csv`
(Sonnet mapper agent, dispatched 2026-08-15). Question to answer: which
UNKNOWNs sit in NCENT and grew materially 2023→2026? Materiality yardstick:
closing NCENT's 3 pp gap needs ≈432 MW average continuous load; the entire
confirmed NCENT NCL set is ≈114 MW. NOTE: `ercotStationLoad` ends 2026-06-15
— 2026 stats are partial (no summer), compare seasonally matched windows.
