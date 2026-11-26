# PINNED: teids without a resolved DAM PSSE identity/status — revisit later

As of 2026-07-09. Final-table DAM coverage: `ercotDampsseId` mapped for
10,834 / 10,927 branch_id'd teids; `dampsse_default_status` populated for
10,907 (fallback tiers + candidate-consensus). This file pins what's left
so it can be parked now and picked up later. Machine-readable details:
`dampsse_unmapped_diagnosis.csv` (identity buckets) and
`dampsse_fallback_mappings.csv` (every fallback-tier match, for audit).

## The 20 teids with NO dampsse_default_status (from branch_tracking_table.csv)

### A. Parallel units whose candidate statuses disagree (9) — identity ambiguous AND it matters
| teid | our name | candidates | note |
|---|---|---|---|
| 720535, 719724, 719725, 720526 | MULBERRY_{1,2}_{345,138}_1_H | MULBERRY_R-E1/ET/EL/WL/WT | East/West units, one side in service, one not. Auction says Closed (0.67-0.73). Need to know which E/W unit each teid is. |
| 417454 | RDOSC_AXFMRH | RDOSC_FMR1/FMR2 | our name has no unit digit; units differ in status |
| 395316 | HDRSC_AXFMRH | HDRSC_FMR1/FMR2 | same pattern |
| 97895 | SASASW_ATH | SASASW_AT1/AT_M | same pattern (AT_M = mobile/spare?) |
| 7650, 6021 | BWNSW_AXFMR{2,1}_H | BWNSW_S1_2/S001/S002 | same pattern |

Resolution path: identify the physical unit (E/W, 1/2) per teid — from the
CIM model bus numbers, or ask ops. Alternatively the RT dynamic rating
crosswalk (`ercotRtDynamicRatingView` has elementTEID + station IDs) may
pin these directly for lines; for these transformers a one-time manual
call is probably fastest.

### B. Mapped, but dormant in DAM — no hourly rows in the 2-year window (5)
teids 2061 (CRLTN1↔MONETY2), 278981 (PC__PANTHER1), 1743 (known reused
teid), 280071 (GRNBYU_A5STR), 280066 (CEDARP_A1STR). The star-points
(A5STR/A1STR) and 1743 are *correctly* absent. "Dropped from the DA
model" is itself a status signal — candidate treatment: not-in-current-model.

### C. Genuinely absent from the DA model (5)
- 3133, 1940, 1529 — GSU/plant-internal stubs (13.8kV-1kV). Possible
  future inference: inherit status from the associated generator via
  `ercotDampsseGnTimeseries.inService`.
- 836689 — row literally named `15060__E_OldTeid` (stale).
- 881081 — ABEAST series device; outage data says energized 2026-06-24,
  auction says Closed 1.0. DAM candidates were transformer-typed only.

### D. LOTEBUSH (1)
397830 `LOTEBUSH_T1S_HS` — candidates LOTEBUSH_T1 vs T1S with differing
status; auction already says Open (0.0). Likely series device/spare —
manual call.

## Identity-only ambiguity, status already inferred by consensus (73)
73 teids have `dampsse_default_status` (all Closed — every parallel
candidate in service) via the `candidates_consensus` tier but NO
`ercotDampsseId` (identity still ambiguous among parallels). Fine for
status purposes; resolve identity later via psseCktId history or
impedance matching if it ever matters. Listed in
`dampsse_default_status_fallback.csv` where tier=candidates_consensus.

## Deferred mechanisms (noted, unbuilt)
- Tier-4 impedance (r/x/b) matching — needs impedances on our side
  (PTOBRANCH-derived; CIM TeidMap export has none).
- RT dynamic rating crosswalk as an independent mapping check
  (elementTEID + RDFID + branchID + names, 15-min cadence).
- Outage cross-check: confirm default-Closed lines' Open hours coincide
  with logged outages (target: borderline pct_inservice 0.4-0.6).
- Auction-snapshot discounting before in_service_date (fixes the
  recently-energized lag; 229 of 267 remaining DAM-vs-auction
  disagreements).
