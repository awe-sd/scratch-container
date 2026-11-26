# PUN shift-equivalence redo — corrected bus map (shiftequiv2)

Redo of `pun_shift_equivalence.csv` using the SSWG/CIM station→bus map instead of the
void `ERCOTDAMPSSELNVIEW` PSSE tie-bus numbers. One combined query joined the map
(restricted to the 56 PUN ∪ 72 neighbour stations = 128 names) to
`SHIFT_FACTORS.DBO.BUS_SHIFTS` for the 24 non-degenerate PSENSHIFTIDs (16,896 rows),
plus one standalone map-only pull for the "N buses in map" denominator (733 rows) and
one name-check query confirming `MPPOI`/`LKVPD` genuinely have no entry in either
source table under those station codes (3 queries total, well inside budget).

## (a) Coverage

- **126 of 128** stations (56 PUN ∪ 72 neighbours) have ≥1 bus in the map. The 2 misses
  are `MPPOI` and `LKVPD` (both PUN, MESHED) — neither name exists in
  `CIMSTATIONVOLTAGELEVEL`/`CIMCONNODE` nor `ERCOTDATADICTIONARY`; confirmed by a
  targeted `ILIKE` search, not just an absence in the filtered pull.
- **74 of 81** included ties (91%) have both PUN-side and ERCOT-side PSENS populated in
  at least one of the 24 sets. The 7 never-valued ties are exactly the ties touching
  `MPPOI` (`6217_A`, `6217_B`) and `LKVPD` (`1250_J`, `1250_F`, `1250_P`,
  `LKVEW_RC1`, `LKVTP_ONCOR_RC1`) — i.e. coverage failure is fully explained by the
  2 unmapped PUN stations, nothing else fell through.
- **42 of 44** PUN stations that appear in the 81-tie list get a valued comparison
  (only `MPPOI`/`LKVPD` don't). At the tie×set grain, 1,776 of 1,944 rows (91.4%) are
  fully valued.
- Note: the MESHED bound (part d) does **not** need the PUN side, so `MPPOI` and
  `LKVPD` still get a bound number since their neighbours (`KEYSB`/`WLVSW`,
  `LKVEW_RC`/`LKVTP_RC`/`LLTSW`/`PLSTH`/`TIMBR`) are all present in the map.

## (b) |Δ|×100 distribution

| Group | n (tie×set) | median | p90 | max |
|---|---|---|---|---|
| RADIAL (all) | 552 | 0.0000 | 0.0004 | 1.745 |
| RADIAL, non-dead-end | 192 | 0.0000 | 0.0100 | 1.745 |
| MESHED | 1,224 | 0.0000 | 0.0868 | 5.984 |
| **DEAD_END** (15 ties × 24 sets = 360) | 360 | **0.0000** | **0.0000** | **0.397** |

**Physics check passes.** Dead-end ties (`N_TIES=1` and no `PUN_NEIGHBORS` — 15 PUN
stations: AK, AMOCOOIL, CCEC, BTE, DUP1_V, DUP2_V, DUPV1, DOWGEN, LGE, LEVEE, MIN, PNPI,
PR, SDSES, UCC_COGN) must show PUN-side ≈ ERCOT-side since the PUN station is
electrically just an extension of the neighbour with nothing else attached. **Zero**
dead-end tie×set rows exceed 1 MW; the worst is 0.40 MW. This is the opposite of what
the void PSSE-bus mapping would have produced, and is the key sanity signal that the
corrected map is measuring the right physical buses.

## (c) MESHED worst 10

By |Δ|×100 MW:

| Tie | PUN | ERCOT nbr | Set (label) | PSENS_PUN | PSENS_ERCOT | \|Δ\|×100 | % of rating |
|---|---|---|---|---|---|---|---|
| CELANE_N_SHAR11 | CELANEBI | N_SHARPE | 105244358 (AIRLIN_B_DAVI21) | 0.1298 | 0.1897 | 5.98 | 1.81% |
| CANGRE_NCARBI11 | NCARBIDE | CANGREJO | 85094114 (RAY_L_461) | -0.0536 | -0.0078 | 4.58 | 2.66% |
| NCARBI_PV_TAP11 | NCARBIDE | PV_TAP | 85094114 (RAY_L_461) | -0.0536 | -0.0078 | 4.58 | 2.66% |
| HL_PSA08A | PSA | HL | 85771508 (MDOPHR99A) | -0.1701 | -0.2112 | 4.11 | 0.31% |
| FORMOS_LOLITA11 | FORMOSA | LOLITA | 86158670 (RAY_L_461) | 0.0702 | 0.0341 | 3.61 | 2.10% |
| BYUSBK96A | BYU | SBK | 85180943 (MDOPHR99A) | -0.3007 | -0.3296 | 2.89 | 0.22% |
| BYUSBK96A | BYU | SBK | 85771508 (MDOPHR99A) | -0.3404 | -0.3677 | 2.73 | 0.21% |
| CELANE_KLEBER11 | CELANEBI | KLEBERG | 105244358 (AIRLIN_B_DAVI21) | 0.1298 | 0.1059 | 2.39 | 0.72% |
| CANGRE_NCARBI11 | NCARBIDE | CANGREJO | 114432086 (RAYBURN69_2) | -0.0245 | -0.0469 | 2.24 | 2.66% |
| NCARBI_PV_TAP11 | NCARBIDE | PV_TAP | 114432086 (RAYBURN69_2) | -0.0245 | -0.0469 | 2.24 | 2.66% |

By % of rating the ranking is nearly identical (NCARBIDE/CANGREJO-PV_TAP pair tops out
at 2.66%, CELANEBI-N_SHARPE at 1.81%). All meshed deltas are small in absolute terms
(<6 MW) and small relative to branch rating (<3%) — a believable, non-explosive
correction, unlike what mismatched PSSE bus numbers would have produced.

## (d) Corrected MESHED bound

`shiftequiv2_meshed_bound.csv`: for each MESHED PUN×set with ≥2 real neighbours,
`spread = max(PSENS_ERCOT) - min(PSENS_ERCOT)` over its neighbours at the tie kV,
`bound_MW = spread × max(|P10_I_P|, |P90_I_P|)`. 504 PUN×set rows, 21 distinct MESHED
PUN stations covered (all 21 MESHED stations in topology, including `MPPOI`/`LKVPD`
since the bound only needs the ERCOT side). Median bound is 0 MW across all rows
(most sets don't touch a given PUN's flowgate at all); median over the 187 rows with a
nonzero bound is **0.010 MW**.

Top 10:

| PUN | Set | N nbrs | spread(PSENS) | max\|I_P\| | bound (MW) |
|---|---|---|---|---|---|
| PSA | 85771508 | 4 | 0.0570 | 503.6 | 28.68 |
| PSA | 85180943 | 4 | 0.0249 | 503.6 | 12.54 |
| LYD | 85771508 | 2 | 0.0105 | 721.3 | 7.59 |
| LYD | 88414476 | 2 | 0.0104 | 721.3 | 7.49 |
| CELANEBI | 105244358 | 2 | 0.0837 | 66.2 | 5.54 |
| PSA | 88414476 | 4 | 0.0075 | 503.6 | 3.75 |
| EXN | 85771508 | 3 | 0.0173 | 182.7 | 3.16 |
| LYD | 85180943 | 2 | 0.0033 | 721.3 | 2.38 |
| FORMOSA | 86158670 | 2 | 0.0437 | 46.1 | 2.01 |
| BYU | 85180943 | 3 | 0.0323 | 58.9 | 1.90 |

PSA and LYD dominate the bound — both driven by a large `MAX_ABS_I_P` (LYD's P90 of
721 MW, itself flagged in `backout_pun_estimates.csv` as directional-only/entangled
with CHE) rather than an unusually large shift-factor spread. The largest genuinely
shift-factor-driven bound is CELANEBI at 5.5 MW.

## (e) Within-station kV spread (placement sensitivity)

`AVG_PSENS` is computed per (station, kV-level) bucket in `shiftequiv2_station_kv.csv`,
where kV-level snaps each map row to the station's own nominal candidate kV (from
`KV_LEVELS`/tie kV) within 1.0 kV, falling back to the raw rounded kV as its own bucket
when nothing is within tolerance (this is also how the CIM-vs-ERCOTDATADICTIONARY
decimal drift — e.g. 12.0 vs 12.5, 13.8 vs 14.0 — gets reconciled without inventing a
dedup rule; duplicate-source labels for the same bus carry the identical PSENS value,
so bucket counts use `nunique(BUSNUM)` and are unaffected by the double label).

- **FORMOSA** (54 buses in map, spanning 1/12/12.5/13.8/14/69/138 kV labels) and
  **DOWGEN** (48 buses, spanning 1/14/14.4/14.5/18/138 kV labels): PSENS is **identical
  to machine precision at every kV level, for every one of the 24 sets** — the 138 kV
  tie-level average equals the ~14 kV and ~69 kV internal-level averages exactly
  (min=avg=max within every bucket). These stations behave as a single electrical node
  in the shift-factor model regardless of voltage class.
- This is not universal, though: scanning all 42 valued PUN stations for any
  within-station spread across kV levels, only **4** show a spread above 0.01 MW —
  `CHE` (max 2.11 MW, its 138/345 kV split is a real transformer, not a zero-Z merge),
  `NCARBIDE` (max 1.08 MW), `PSA` (max 0.108 MW), `SL` (max 0.030 MW). Three more are
  nonzero but smaller: `CELANEBI` (0.0075 MW), `VISTRON` (0.005 MW), `BYU` (0.004 MW) —
  seven of 42 stations show any nonzero spread at all. "Combo" here means one (PUN
  station × shift-set) pair with ≥2 populated `KV_LEVEL` buckets in
  `shiftequiv2_station_kv.csv`; restricted to the 42 valued PUN stations that is **744**
  combos (not 130 as originally stated — that figure could not be reproduced under this
  or any other grouping tried), median spread 0.00 MW, p90 ≈0.00 MW (<0.001 MW) — driven
  to ~0 because most multi-kV-level stations (FORMOSA, DOWGEN, etc.) are exact-node cases
  across all 24 sets, and only the 7 stations above contribute any nonzero mass.
- **Practical read:** for the overwhelming majority of PUN stations, it would not have
  mattered which internal voltage level the injection was nominally attached to — the
  shift factor is the same. `CHE` is the one PUN station where a genuinely different
  voltage class (345 kV vs 138 kV) inside the station carries a materially different
  sensitivity — up to 2.1 MW, on a 1,314 MW-rated branch (0.16% of rating), the largest
  kV-placement effect of any PUN station in absolute MW though small as a share of
  rating — so any future placement decision for CHE specifically should confirm which
  kV level the
  MW is actually injected at.

## (f) Conclusion

For **radial** ties, lumping the tie MW at the neighbour station is unambiguously
equivalent to placing it at the PUN station: dead-end deltas (the cleanest radial
subset, where the PUN station has no other connection) sit at essentially zero
(median 0.00, p90 0.00, max 0.40 MW) across all 24 contingency sets — exactly what a
single-tie radial spur should produce in a DC shift-factor model, since the PUN bus
and its one neighbour are, up to a lossless line, the same point in the network for
sensitivity purposes.

For **meshed** stations the equivalence is *approximate but small*: PUN-side and a
given neighbour's ERCOT-side sensitivities differ by at most ~6 MW (CELANEBI/N_SHARPE)
and typically under 3% of the monitored branch's rating, because a meshed PUN station
sits at a real electrical branch point between several neighbours whose individual
sensitivities genuinely differ from each other (that's what "meshed" means) — the PUN
bus's own sensitivity is a real, if modest, blend of its neighbours', not identical to
any single one of them. The corrected bound (part d) sizes the resulting worst-case MW
mismatch from choosing "lump at one neighbour" over "value the PUN bus directly":
median ~0.01 MW, essentially negligible; a handful of PUN stations (PSA, LYD, CELANEBI,
EXN, FORMOSA, BYU) can see bounds in the 2–29 MW range in specific sets, driven mostly
by those PUNs' own large estimated injection (I_P) rather than by an unusually large
shift-factor spread among their neighbours. Net: within-station kV placement is a
non-issue almost everywhere (part e) and even the "lump at nearest neighbour vs. value
the PUN node itself" approximation is small in absolute terms for both radial and
meshed classes in the scan's own units — the exception worth flagging by name is
`PSA` and `LYD` in the largest-few sets, and `CHE` for kV-placement specifically.
