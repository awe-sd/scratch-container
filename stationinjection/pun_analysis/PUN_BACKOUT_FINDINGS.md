# PUN net-injection back-out: findings (spike, 2026-09-25, revised)

## 1. Question and answer

ERCOT redacts SE branch flows across every tie into a private-use network (PUN), so
`AW.DBO.ERCOTSTATIONINJECTION` has no rows for the 56 PUN stations behind those ties. The
question: can we recover each PUN's net injection from the network model, DAM bus loads, SCED
generator telemetry, and the GENUNIT mapping, by balancing the visible ERCOT-side neighbour of
each redacted tie.

Yes, with caveats. The tie's MW is not missing from the data, it is lumped into the ERCOT-side
neighbour bus one hop away, and Kirchhoff's law lets it be pulled back out as a residual
(`R_S = N_S - Gen_S + Load_S`). This is exact for 8 of 56 PUNs (clean switching neighbours; only
3 of the 8 -- BTE, CCEC, AMOCOOIL -- are verified against independent SCED telemetry, to within a
few MW), load/DAM-adjusted for 24 more, combined-only (not individually attributable) for 12 that
share a neighbour with another PUN in 6 pairs, and not estimable at all for 12 that have no
SE-visible neighbour of their own.

For the fast scan specifically (Section 6, redone with the scan's own SSWG/CIM station-bus map
after an earlier bus-numbering artefact was found and withdrawn): lumping a redacted tie's MW at
the ERCOT-side neighbour is exact for radial ties (dead-end median and p90 |Delta|x100 = 0.00 MW,
max 0.40 MW per 100 MW of tie flow, across 360 tie x set rows) and small for meshed ties (worst
case 5.98 MW, 1.8% of rating, at CELANEBI/N_SHARPE; worst as a share of rating is 2.66% at
NCARBIDE/CANGREJO and NCARBIDE/PV_TAP). The formal meshed-lumping bound tops out at 28.7 MW at
PSA, driven mostly by the size of PSA's own estimated injection rather than by shift-factor
spread among neighbours. `ERCOTSTATIONINJECTION`'s current practice of lumping PUN MW at the
neighbour bus therefore already gives the fast scan, to within these small bounds, the right
answer for PUN MW; the back-out below changes station-level reporting and attribution, not scan
flows, except PSA and LYD (28.7 / 7.6 MW bounds, driven by their own injection size), CELANEBI
(5.5 MW, the largest shift-factor-driven bound), and, separately and smaller, CHE for kV placement
(2.1 MW, 0.16% of rating).

N_S is an SE measurement, so the lumped MW carries none of the DAM-load-forecast error quantified
in Section 4c; that error affects only the back-out's split of N_S into neighbour load and tie
flow. The fast scan's PUN MW is therefore magnitude-exact by construction and
placement-approximate within the Section 6 bounds.

## 2. Physics of the lump

At the ERCOT-side neighbour station S of a redacted tie, the SE state estimator's net injection
at S is

```
N_S = Gen_S - Load_S - F_tie
```

where `F_tie` is the flow from S into the PUN across the redacted tie (positive = flowing toward
the PUN). ERCOT does not report `F_tie` on its own; it is absorbed into `N_S` because the branch
itself is dropped from the published model, not because the flow disappears. Rearranging,
`F_tie = Gen_S - Load_S - N_S`, and defining the PUN's export through this tie as
`I_PUN = -F_tie`:

```
I_PUN = N_S - Gen_S + Load_S =: R_S
```

`N_S` comes from `ERCOTSTATIONINJECTION`; `Gen_S` and `Load_S` are visible, non-PUN quantities at
S (SCED telemetry and DAM load respectively). If S itself has no generation and no load of its
own, `Gen_S = Load_S = 0` and `I_PUN = N_S` exactly, no adjustment needed. Positive `I_PUN` means
the PUN exports net MW to the visible grid through that tie; negative means it imports.

## 3. Data used

| Source | Grain | What it gave | What it did not give |
|---|---|---|---|
| `AW.DBO.ERCOTSTATIONINJECTION` | (TIMESTAMP, NMMSSTATIONCODE, KVLEVEL) | `N_S` at every ERCOT-side neighbour | Nothing at PUN stations (that is the gap) |
| `AW.DBO.ERCOTDAMPSSELDVIEW` | (DATE, HE, STATIONNAME) | `RAWMWLDF` = `Load_S` in MW | PUN stations' own load, except DOWGEN (~131 MW, own-bus record, provenance unclear) and CSUNGATE (~10 MW) |
| `AW.DBO.ISOERCOTSCEDGENRESOURCE` / `ISOERCOTSCEDGEN` | 5-min, all ticks (`:00`-`:55`, not just `:55`) | `TELEMETEREDOUTPUT` = `Gen_S`, and PUN-side gross via `GENUNIT.UNITNAME='PUN'` (118 rows / 23 stations) | Station code directly; needs the DAM chain below |
| `GENUNIT` -> `ERCOTDAMPSSEGNDEF` -> `ERCOTDAMPSSESTATION` | unit -> station | 96% MW-weighted coverage of SCED units to a station name (second stage only, see below) | 51 of 1,614 tracked units unmapped at this stage (~4% MW-weighted); no authoritative unit-to-NMMS table exists |
| `AWDEV.ERCOTRT.ERCOTRTPSSE*` | hourly RT PSSE snapshot | Confirms PUN stations exist in the topology/rating model (not redacted there) | No solved MW; capacity/limit fields only, not usable for `N_S` |
| `SHIFT_FACTORS.DBO.BUS_SHIFTS` | (PSENSHIFTID, BUSNUM) | PSENS at ERCOT-side buses for the fast-scan check, joined via the scan's own SSWG/CIM station-bus map | PSENS at 74 of 81 real ties (126 of 128 PUN-union-neighbour stations map to a bus at all; MPPOI and LKVPD are absent from the map itself, not a `BUS_SHIFTS` gap; see Section 6) |

Nowhere does an SE gen/load/bus-MW table for PUN stations exist. `LOADDISTRIBUTIONFACTOR` in the
RT PSSE tables ranges -10..250 and is a scaling factor, not MW.

**DAM PSSE bus numbers must never be joined to `BUS_SHIFTS`.** `ERCOTDAMPSSELNVIEW`'s
`PSSEFROMBUSNUMBER`/`PSSETOBUSNUMBER` are DAM-model PSSE bus numbers, a different numbering
scheme from the SSWG numbers `BUS_SHIFTS.BUSNUM` uses. The two ranges overlap but name different
physical buses (e.g. SSWG 559 is HERITAGE 138 kV, not MIN), so joining the two directly produces
silently wrong tie-end comparisons rather than an error; this is exactly what the withdrawn
Section 6 analysis did (see Section 6).

**Compound unit-mapping miss rate.** The 96% figure above is MW-weighted and covers only the
second of two mapping stages. End to end: of 1,798 distinct SCED resource names, 184 have no
`GENUNIT` row at all (first stage, ~10% by count); of the surviving 1,614, a further 51 fail to
resolve a station name through the DAM chain (`ERCOTDAMPSSEGNDEF` -> `ERCOTDAMPSSESTATION`,
second stage). That leaves 1,563 of 1,798 mapped end to end, 86.9% by count. The second stage
alone is 96% MW-weighted (i.e. only 4% of MW-weighted capacity is lost there), but stating the
two stages together, count-weighted coverage (86.9%) is meaningfully lower than the second-stage
MW-weighted number alone suggests, because the first-stage loss (184 resources, mostly small or
retired) doesn't register the same way once weighted by MW.

**Mapping fork.** Two independent unit-to-station chains exist for the same SCED units, and they
disagree for some PUN plants. The DAM chain (`GENUNIT` -> `ISOERCOTSCEDGEN` ->
`ERCOTDAMPSSEGNDEF` -> `ERCOTDAMPSSESTATION`) places `BTE_CC1_1`..`6` at station BTE. The BUSNAME
chain used in `calibration_by_station.csv` places the same six units at station CHB, which is
BTE's own SE-visible neighbour. `Gen_S` in the back-out (Section 2) always uses the DAM chain, so
the truth test in Section 4a is, precisely, comparing CHB's SE-visible injection (which has no
DAM-chain generation of its own, so `Gen_S(CHB)=0` is correct) against BTE's DAM-chain-mapped
units' own telemetry. The two chains are consistent for the back-out method's purposes here, but
would give the wrong comparison if the BUSNAME-chain station label were substituted for `Gen_S`
instead of the DAM-chain one.

## 4. Validation

### 4a. Independent truth test (lead, June 2026, 720 hours each)

Three PUNs have both live SCED telemetry and a clean (no gen, no load) switching neighbour, so
`R_S` can be checked directly against the PUN's own metered output. Sorted by |SE mean R_S|
descending:

| PUN | Neighbour (S) | SE mean R_S (MW) | PUN's own SCED telemetered mean (MW) | Correlation |
|---|---|---|---|---|
| BTE | CHB | 406.2 | 411.1 | 0.994 |
| CCEC | CITGO_NO | 260.9 | 258.8 | 0.998 |
| AMOCOOIL | GRNBELT | 191.2 | 191.7 | 1.000 |

Implied on-site load at all three is small: ~5 MW at BTE, ~0 MW (-2 MW) at CCEC, ~1 MW at
AMOCOOIL. This confirms the sign convention, that the SE `:57` solve matches the nearest SCED run,
and that for pure switching neighbours the residual is the tie flow to within a few MW. This
spike's own recompute (`backout_truth_test.csv`) now matches: 411.1 MW / corr 0.994 at BTE, 258.8
MW / corr 0.998 at CCEC, 191.7 MW / corr 1.000 at AMOCOOIL, using the per-timestamp station sum
described in Section 8 (the earlier 415.3 / 261.3 / 193.4 MW figures came from a conditional-mean
bug, now fixed).

**Validation coverage is narrower than three clean rows suggests.** All three PUNs above are
EXACT_SWITCHING (Section 5): the method degenerates to `I_PUN = N_S` with no `Gen_S`/`Load_S`
correction at all, so this truth test validates the sign convention and the SE/SCED timing
match, not the `Load_S` correction term. Of the 24 DAM_LOAD_ADJUSTED PUNs, 19 have no
gen-bearing neighbour at all (`ANY_NEIGHBOR_HAS_GEN=False` in `pun_topology.csv`), so the leg
actually exercised there is `Load_S` from the DAM forecast, not `Gen_S`. The remaining rows of
`backout_truth_test.csv` extend the check into that DAM_LOAD_ADJUSTED regime, sorted by |implied
load| descending:

| PUN | Neighbour(s) | Implied on-site load (MW) | Correlation | Note |
|---|---|---|---|---|
| DOWGEN | DOW | 262.8 | 0.71 | This row does not exercise the `Load_S` leg either (DOW has zero DAM load and zero SCED gen); it is a fourth EXACT_SWITCHING case included for its implied-load magnitude. Only FORMOSA, DIB, BYU and the PSA+LHM group below extend the check into the DAM_LOAD_ADJUSTED regime. See Section 8 for the unresolved ~131 MW external reference figure. |
| BYU | MCB, ORION, SBK | 146.6 | 0.644 | Weakest correlation of any row; discussed below. |
| DIB | MNT, SRB | 42.9 | 0.71 | |
| PSA+LHM_COMBINED | BCV, HL, LY, MTS | 31.6 | 0.78 | 5% of hours implied negative load; combined check resolving the PSA/LHM entanglement (neighbour set is the union, LY counted once). Unchanged by the gross-column fix (Section 8). |
| FORMOSA | JOSLIN, LOLITA | 0.6 | 0.86 | |

LGE is entangled with I_DUPP1 (both PUNs' only real neighbour is I_DUPSW): `I_PUN(LGE) = R(I_DUPSW)`
is not independent of I_DUPP1's own figure, and LGE's persistently negative implied load in the
raw CSV is likely an artifact of attributing all of I_DUPSW's export to LGE alone, not a method
failure.

BYU is worth a paragraph because it is the weakest correlation in the table by a wide margin
(0.644, versus 0.71-1.00 everywhere else). BYU is MESHED with three real neighbours (MCB, ORION,
SBK), unlike the single clean neighbour behind each EXACT_SWITCHING row, so its `R_S` is exposed
to DAM load-forecast error at three neighbours simultaneously instead of zero, and it is also one
of the 21 MESHED PUNs in the corrected Section 6 meshed-lumping-bound table, where its worst
bound is 1.90 MW (shift set 85180943), not the withdrawn analysis's earlier number.
BYU's own gross telemetry (110.2 MW, effectively one active unit of two) is small relative to the
flows being netted at its neighbours, so a modest absolute mismatch there is a large fraction of
BYU's own signal. Read BYU's DAM_LOAD_ADJUSTED estimate as the least trustworthy of the 24, not
as evidence the method is broken generally.

**Snapshot screening.** June 2026 contains none of the five known SE partial-solve hours
(`se_partial_solve_hours.sql`, `<50%`-of-median-branch-row-count rule, re-run scoped to June 2026:
zero hours flagged). Rollout-night stub snapshots are excluded by that same rule. All estimable
PUNs have `N_HOURS = 720`, i.e. a full, unbroken hourly series for the month.

### 4b. Calibration at well-mapped generation stations (`calibration_summary.md`)

| Size band (mean SE MW) | N stations | Median \|SE - SCED\| | As % of output |
|---|---|---|---|
| 250-1000 MW (closest to PUN scale) | 42 | 3.19 MW | **0.67%** |
| >1000 MW | 7 | 10.59 MW | 0.65% |

No systematic bias (median mean-delta approximately 0, sign split ~50/50). The dominant failure
modes are unit-to-station mapping error (no authoritative table; 51 of 1,614 SCED units unmapped
at the DAM-chain stage) and wind/solar ramp timing, neither of which is the primary risk for
PUN-scale industrial co-gen.

### 4c. Noise floor and Load_S error bar (`backout_noise_floor.md`, `backout_residual_by_station.csv`)

| Neighbour class | Median \|R\| | 80th pct | 90th pct |
|---|---|---|---|
| No gen, no load | 0.0021 MW | 0.0052 MW | 0.0081 MW |
| Load only (most PUN neighbours) | 2.19 MW | 7.34 MW | 11.67 MW |
| Gen + load | 1.69 MW | 4.40 MW | 9.36 MW |

At load-only stations, `|R|/Load` runs 0.38 median, meaning the DAM load forecast (not the SE
solve) is the dominant error source wherever the neighbour serves load.

**`LOAD_ERR_MW` per PUN.** To turn that noise floor into a per-PUN error bar, take every
non-neighbour, load-only station (`HAS_LOAD`, not `HAS_GEN`, not a PUN neighbour) from
`backout_residual_by_station.csv`, bin by mean DAM load, and take the median and 90th percentile
of each bin's stations' own `MEDIAN_ABS_R`:

| Load bin (MW) | N stations | Bin median \|R\| (MW) | Bin p90 \|R\| (MW) |
|---|---|---|---|
| 0-5 | 1,395 | 0.73 | 2.17 |
| 5-15 | 909 | 3.10 | 6.14 |
| 15-40 | 812 | 7.62 | 12.98 |
| 40-100 | 190 | 14.90 | 33.12 |
| 100+ | 26 | 19.89 | 56.80 |

For each PUN, `LOAD_ERR_MW` is the sum, over its real neighbours, of that neighbour's bin median
(0 for a neighbour with no DAM load); a p90 version sums the bin p90 instead. Both are reported in
`backout_pun_estimates.csv` and in the Section 5 tables below. EXN's three neighbours carry DAM
loads of BT 20.2 MW, DKR 60.5 MW, and LH 9.6 MW, placing them in the 15-40, 40-100, and 5-15 MW
bins respectively, for `LOAD_ERR_MW(EXN) = 7.6 + 14.9 + 3.1 = 25.6 MW` (p90 52.2 MW).

**`LOAD_ERR_MW` scope.** `LOAD_ERR_MW` covers the `Load_S` leg only; it says nothing about a
neighbour's `Gen_S` leg. Five DAM_LOAD_ADJUSTED PUNs have at least one gen-bearing neighbour per
`pun_topology.csv` (`ANY_NEIGHBOR_HAS_GEN=True`): TAM, SL, PNPI, DIB, and BFM. At TAM, DIB, and BFM
(and, outside the DAM_LOAD_ADJUSTED set, at MSN) the mapped units at those gen-bearing neighbours
read zero output for the entire month, so the `Gen_S` term is a correct zero there in practice, not
an unquantified gap. That leaves only PNPI (via WAP), and SL (via AZ), actually carrying a material
gen leg the noise floor above doesn't price in. Sized against the calibration rate in Section 4b
(~0.65% of neighbour gross MW), that leg is on the order of 11 MW at PNPI (WAP's gross, excluding
the fanout-affected hours discussed below, is ~1,771 MW) and under 1 MW at SL (AZ's gross is ~2 MW).

**PNPI recomputed: gen-join fanout at WAP, not a real heavy tail.** The station WAP (PNPI's sole
neighbour) has 5 of 720 hours where the mapped-unit gen sum reads 4,424-5,500 MW against a true
station maximum of 3,130 MW (at the :55 SCED ticks); this is a gen-to-station join fanout, not a
real generation reading, and it inflated both `MEAN_I_P` and `STDEV_I_P` for PNPI in the original
table. Recomputing `R(WAP)` with those 5 hours excluded (`gen_s > 3,500` MW) gives `MEAN_I_P =
-30.0`, `STDEV_I_P = 20.9`, `P10/P90 = -54.3/-6.9` -- the P10/P90 band is essentially unchanged from
the original (-55.6/-7.0), confirming the fanout hours sat in the tail, not the bulk of the
distribution. Of the 72 neighbour stations behind all 56 PUNs, only WAP, AZ, and GBY carry any
mapped generation at all; AZ (SL's neighbour) and GBY (LYD's neighbour) show no comparable fanout,
so exactly one row in `backout_pun_estimates.csv` -- PNPI -- needed correction.
`backout_residual_by_station.csv`'s WAP row still carries the pre-fanout-correction `MEAN_R =
-47.79`; that CSV now has a `NOTE` column flagging it as such and pointing at
`backout_pun_estimates.csv`'s `PLAUSIBILITY_NOTE` for the corrected `MEAN_I_P = -30.0` PNPI
figure -- the two files were not both recomputed, so read the residual-by-station figure for WAP
as stale.

## 5. Results: per-PUN / per-group net exchange, June 2026

Method tags: **EXACT_SWITCHING** (neighbour has zero DAM load and zero SCED gen, not entangled)
gives `I_PUN = N_S` directly; **DAM_LOAD_ADJUSTED** applies the full `R_S` correction at one or
more clean-ish neighbours; **ENTANGLED_GROUP** means two PUNs share a real neighbour and only the
combined figure is meaningful; **NOT_ESTIMABLE** means no SE-visible neighbour exists at all.
Positive = PUN exports to the grid. All three tables below are sorted by |mean| descending.

`PUN_GROSS_SCED_MW` ("Own SCED gross") is the station mean of the per-timestamp sum of its
mapped units' `TELEMETEREDOUTPUT` (a unit with no row at a given tick contributes 0 to that
tick's sum). An earlier version of this table instead averaged each unit's own conditional mean
(over only the ticks where that unit had a row) and summed those averages; see Section 8 for the
size of the correction.

### Exact switching (8)

| PUN | Neighbour | Mean I_PUN | P10 | P90 | Own SCED gross | LOAD_ERR_MW (median, p90) |
|---|---|---|---|---|---|---|
| BTE | CHB | 406.2 | 29.8 | 530.6 | 411.3 | 0.0, 0.0 |
| CCEC | CITGO_NO | 260.9 | 113.2 | 382.3 | 258.2 | 0.0, 0.0 |
| DOWGEN | DOW | -248.7 | -322.7 | -140.4 | 14.2 | 0.0, 0.0 |
| AMOCOOIL | GRNBELT | 191.2 | 75.8 | 264.7 | 191.6 | 0.0, 0.0 |
| LEVEE | OYS | -89.7 | -101.7 | -61.6 | - | 0.0, 0.0 |
| DUP2_V | INV_TAP | -29.9 | -35.0 | -19.2 | - | 0.0, 0.0 |
| UCC_COGN | APACHE | -7.5 | -8.7 | -6.2 | 0.0 (units all read 0) | 0.0, 0.0 |
| PR | PRS | -7.0 | -17.7 | 5.0 | - | 0.0, 0.0 |

All eight of these neighbours are DAM-load-free by construction (that is what EXACT_SWITCHING
means), so `LOAD_ERR_MW` is zero for all of them; the correction term simply does not apply.

### DAM-load-adjusted (24)

| PUN | Class | Mean I_PUN | P10 | P90 | Own SCED gross | LOAD_ERR_MW (median, p90) |
|---|---|---|---|---|---|---|
| BBP | RADIAL | 132.2 | 113.7 | 150.2 | - | 0.7, 2.2 |
| EXN | MESHED | -83.2 | -182.7 | -29.3 | 0.0 (units all ONOS/OUT) | 25.6, 52.2 |
| TAM | MESHED | -80.6 | -98.2 | -64.9 | - | 10.7, 19.1 |
| PL | MESHED | 80.4 | -56.0 | 174.5 | - | 10.7, 19.1 |
| SL | MESHED | -61.8 | -79.4 | -48.8 | - | 14.9, 33.1 |
| MATKM | RADIAL | -56.2 | -92.1 | -42.1 | - | 7.6, 13.0 |
| TC | MESHED | -52.5 | -86.5 | -20.8 | 0.4 | 27.5, 69.8 |
| CELANEBI | MESHED | 52.0 | 39.3 | 66.2 | - | 7.6, 13.0 |
| OXY_INGL | RADIAL | 50.7 | 22.4 | 62.8 | - | 14.9, 33.1 |
| SDSES | RADIAL | -43.8 | -131.2 | 127.7 | - | 19.9, 56.8 |
| DIB | MESHED | -36.7 | -91.4 | 16.4 | 6.2 | 14.9, 33.1 |
| BYU | MESHED | -35.4 | -58.9 | -10.1 | 110.2 | 4.6, 10.5 |
| BSF | MESHED | -33.4 | -45.2 | -23.7 | - | 8.4, 15.1 |
| PNPI | RADIAL | -30.0 | -54.3 | -6.9 | - | 0.0, 0.0 |
| VISTRON | RADIAL | -26.2 | -41.6 | -11.4 | - | 0.7, 2.2 |
| BFM | MESHED | -20.1 | -25.7 | -15.2 | - | 7.6, 13.0 |
| FORMOSA | MESHED | 16.7 | -7.6 | 46.1 | 17.5 | 1.5, 4.3 |
| LKVPD | MESHED | -7.0 | -11.3 | -3.2 | - | 8.4, 15.1 |
| MIN | RADIAL | 4.7 | -2.1 | 6.9 | - | 0.7, 2.2 |
| CARBN | MESHED | -3.2 | -6.3 | 0.4 | 1.2 | 3.1, 6.1 |
| EQUISTAR | MESHED | 3.2 | -22.2 | 10.1 | - | 3.1, 6.1 |
| MPPOI | MESHED | 1.0 | -0.4 | 2.1 | - | 0.7, 2.2 |
| NCARBIDE | MESHED | 0.3 | -15.7 | 15.0 | 0.01 | 5.3, 12.6 |
| P66_3 | RADIAL | 0.2 | -0.7 | 0.9 | - | 0.0, 0.0 |

PNPI's mean/P10/P90 above are the gen-join-fanout-corrected values (see the PNPI paragraph in
Section 4c); re-ranked by \|mean\|, PNPI now sits between BSF and VISTRON rather than between
OXY_INGL and SDSES.

Own-SCED-gross figures corrected from the earlier conditional-mean sum: FORMOSA 87.4 -> 17.5 MW,
BYU 266.7 -> 110.2 MW, DIB 23.8 -> 6.2 MW, TC and NCARBIDE and CARBN and EXN were unaffected
(single or continuously-running dominant unit; unchanged).

### Entangled groups (6 pairs, 12 stations, combined figure only)

| Group | Members | Combined mean | P10 | P90 | Combined own SCED gross | LOAD_ERR_MW (median, p90) | Note |
|---|---|---|---|---|---|---|---|
| DPW (LYD's own set already = union) | LYD, CHE | 453.3 | -11.2 | 721.3 | - | 0.0, 0.0 | LYD's neighbour set (DPW, GBY) is a superset of CHE's (DPW); LYD's own row already is the group figure |
| LY (PSA's own set already = union) | PSA, LHM | 417.7 | 349.1 | 503.6 | 446.8 (357.9+88.9) | 30.1, 59.1 | Same superset relationship; matches the precomputed `PSA+LHM_COMBINED` row (mean 417.7) |
| PHILLPS2 (genuine partial overlap) | SCLPCOGN, PHILLPS5 | -80.7 (derived, see below) | n/a | n/a | 0.0 | 0.7, 2.2 | Union of 5 neighbours (FM524, LINVILLE, PHILLPS2, WCOLMAIN, OLDOCEAN), PHILLPS2 counted once; individual rows (-68.7 and -12.2) sum to -80.9, off by the double-counted PHILLPS2 contribution (-0.19 MW, negligible) |
| I_DUPSW (identical single-neighbour sets) | I_DUPP1, LGE | 71.7 | -16.5 | 191.4 | 9.3 | 0.0, 0.0 | Both PUNs' only real neighbour is I_DUPSW; the two rows are the same number, not independent |
| STONERSY (identical single-neighbour sets) | DUPV1, DUP1_V | -25.0 | -48.8 | 26.0 | - | 0.0, 0.0 | Same as above |
| HUD (MSN's own set already = union) | AK, MSN | 2.7 | -38.2 | 21.9 | - | 3.1, 6.1 | AK's standalone figure (144.3) is misleading in isolation: it is dominated by HUD's flow before netting against PET, which MSN's own (superset) neighbour set already includes |

Combined mean for the PHILLPS2 group was derived from `backout_residual_by_station.csv` (mean R
per station, summed over the union, each station once); P10/P90 of the combined series are not
computed as a joint series (no hourly join across stations was performed here), not left blank for
lack of a defensible number.

"LY" group's combined own SCED gross corrected from the earlier conditional-mean sum: 1,027.5 MW
(938.6+88.9) -> 446.8 MW (357.9+88.9), PSA's own gross being the part that changed. This 446.8 MW
figure differs from `backout_truth_test.csv`'s PSA+LHM_COMBINED `MEAN_G_P` of 449.4 MW because of
different tick sampling: the §5 figure is the hourly nearest-:55-tick station sum used throughout
this table, while `backout_truth_test.csv` averages over all 5-minute SCED ticks in the hour; both
are internally consistent, just not the same sampling basis. "I_DUPSW"
group's combined own SCED gross corrected from 205.3 MW to 9.3 MW (LGE's own gross; I_DUPP1 has no
mapped units of its own).

### Not estimable (12, isolated from SE)

COPSUB8, CPCSUB9, COPSUB10, P66SUB6, ARC, CSUNGATE, LBM3, P66SUB12, SPPKM, INGLCOSW, CAL, OXY_CC.
All 12 have zero real (SE-visible) neighbours; their only ties are to other PUN stations. Per the
topology, their export reaches the grid only through a neighbouring PUN's own real ties, so their
MW is not separately unknown, it is already folded into that boundary PUN's combined figure where
one exists (e.g. CAL's and OXY_CC's own SCED gross, 99.9 MW and 6.4 MW respectively, transit
through PL and EQUISTAR's ties and are already inside those PUNs' `I_PUN` above).

Two of the 12 are not folded into a single boundary PUN this cleanly. INGLCOSW exits via two
boundary PUNs at once (I_DUPP1 and OXY_INGL), so its MW is split across two different group
figures rather than living entirely inside one. And the COPSUB8 -> CPCSUB9 -> COPSUB10 ->
P66SUB12 chain (all four themselves NOT_ESTIMABLE) exits the SE-visible grid only through
SCLPCOGN's own ties, so its MW, if any, is folded into the PHILLPS2 combined figure above, not
into any of the four intermediate stations' own numbers (which don't have one).

## 6. Fast-scan impact

**This section replaces the earlier fast-scan analysis in full; the earlier version is
withdrawn.** That analysis resolved tie endpoints through
`ERCOTDAMPSSELNVIEW.PSSEFROMBUSNUMBER`/`PSSETOBUSNUMBER`, which are DAM-model PSSE bus numbers,
not the SSWG numbers `SHIFT_FACTORS.DBO.BUS_SHIFTS.BUSNUM` uses, and not the numbers in the fast
scan's own CIM-205-union-`ERCOTDATADICTIONARY` station-bus map. The two numbering schemes overlap
on the same integer ranges but name different physical buses: SSWG 559 is HERITAGE 138 kV, not
MIN; 1276 is APPLE 69 kV, not BNT; 1765 is ECTOR, not UCC_COGN; 652 is ABR, not APACHE. Every
tie-end comparison in the withdrawn analysis (`pun_tie_buses.csv`, `pun_shift_equivalence.csv`/
`.md`, `farfield_*`, `fastscan_meshed_bound.csv`) therefore paired unrelated buses, and its
findings -- including the 29/30-of-73-buses and 31-of-81-ties coverage gaps, the 13-23 MW/100MW
dead-end mismatches, `DIBMNT21A` at 11.0%, `APA_UCC11` at 9.9%, the EXN 66.2 MW bound, the "9
RADIAL PUNs with measurable PSENS" count, and the far-field/genuinely-open-tie hypothesis -- are
withdrawn along with it. The redo below (`shiftequiv2_*`) uses the scan's own map instead. The
lead independently verified that map against the live shift-factor tables: 5,713 of 5,714 SE
stations (100% of MW) have buses present in each live set (5,714 is the count of stations with
rows at the 2026-06-15 12:57 snapshot used for this map-coverage check; the 5,649-station Section
4c/9 noise-floor population plus the 72 PUN neighbours implies 5,721 stations with any June row at
all -- snapshot vs. any-June-row are different station universes, not a discrepancy), and for the
PUN topology specifically,
54 of 56 PUN stations and 72 of 72 neighbours are present (311 of 327 PUN buses). With the
corrected map, a PUN station's PSENS equals its neighbour's to 4 decimal places in sets 84813542
(6965), 85181110 (12020_B), and 105406151 (890_H): MIN = BNT at 0.0145, UCC_COGN = APACHE at
0.0146, DOWGEN = DOW at 0.0147, BTE = CHB at 0.0145, and EXN = BT = DKR = LH at 0.0145.

**Coverage.** Of the 56 PUN-union-72-neighbour stations (128 names), 126 have at least one bus in
the corrected map; the two misses, `MPPOI` and `LKVPD`, have no entry under those station codes in
either `CIMSTATIONVOLTAGELEVEL`/`CIMCONNODE` or `ERCOTDATADICTIONARY` (confirmed by a targeted
`ILIKE` search, not just an absence in the filtered pull). Of the 81 real ties, 74 (91%) have both
PUN-side and ERCOT-side PSENS populated in at least one of the 24 non-degenerate shift sets; the 7
unvalued ties are exactly the ties touching `MPPOI` (`6217_A`, `6217_B`) and `LKVPD` (`1250_J`,
`1250_F`, `1250_P`, `LKVEW_RC1`, `LKVTP_ONCOR_RC1`) -- the coverage gap is fully explained by these
2 unmapped stations, nothing else fell through.

The 12 NOT_ESTIMABLE isolated PUNs (Section 5) have no SE-visible neighbour of their own, so the
fast-scan lumping for them goes two hops out, through their boundary PUN's real neighbours (e.g.
ARC and LBM3 lump through PSA's neighbour HL; OXY_CC lumps through EQUISTAR's neighbour LON_HILL).
This spike's recompute of PSENS(ARC or LBM3, 138 kV) vs PSENS(HL, 138 kV) across the 24 sets
gives a worst two-hop |Delta|x100 of 4.535 MW (set 85771508/MDOPHR99A; median about 0.0003 MW),
and PSENS(OXY_CC, 138 kV) vs PSENS(LON_HILL, 138 kV) a worst of 0.72 MW (set 105244358; median
0.0 MW), the same order as the one-hop meshed deltas above. A reviewer check reported 3.34 MW for
the OXY_CC/LON_HILL pair; that figure was not reproduced here at any kV pairing tried (largest
across all pairings 5.28 MW, OXY_CC 13.8 kV vs LON_HILL 1 kV).

**Dead-end/radial check.** The cleanest test of the corrected map is the 15 dead-end PUN stations
(AK, AMOCOOIL, CCEC, BTE, DUP1_V, DUP2_V, DUPV1, DOWGEN, LGE, LEVEE, MIN, PNPI, PR, SDSES,
UCC_COGN -- `N_TIES=1`, no PUN-side neighbour), where the PUN bus is electrically just an
extension of its one neighbour and PUN-side and ERCOT-side PSENS must match. Across 15 ties x 24
sets = 360 tie x set rows, median and p90 |Delta|x100 are both 0.00 MW per 100 MW of tie flow, and
the max is 0.40 MW (`shiftequiv2_ties.csv`, `DEAD_END=True`); zero rows exceed 1 MW. This is the
opposite of what the withdrawn DAM-PSSE-bus mapping produced and confirms the corrected map is
measuring the right physical buses: radial lumping is exact in the scan's own terms.

**MESHED.** The broader RADIAL class (552 tie x set rows, not just dead ends) also sits at median
0.00 MW, p90 0.0004 MW. MESHED ties (1,224 tie x set rows) run modestly wider: median 0.00 MW, p90
0.09 MW, max 5.98 MW. Worst 10 by |Delta|x100:

| Tie | PUN | ERCOT nbr | Set (label) | PSENS_PUN | PSENS_ERCOT | \|Delta\|x100 (MW) | % of rating |
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

By raw MW, CELANEBI/N_SHARPE is worst (5.98 MW, 1.8% of a 330 MW branch). By % of the monitored
branch's rating, the ranking changes: NCARBIDE/CANGREJO and NCARBIDE/PV_TAP are worst, both at
2.66%, each on both the 172 MW `RAY_L_461` branch (set 85094114, delta 4.58 MW) and the 84 MW `RAYBURN69_2` branch (set 114432086, delta 2.24 MW), ahead of CELANEBI/N_SHARPE's 1.81%. Either
way every meshed
delta in the top 10 is under 6 MW and under 3% of rating -- a small, believable correction, not an
explosive one, unlike what the mismatched DAM PSSE bus numbers produced in the withdrawn version.

**Corrected meshed-lumping bound.** `shiftequiv2_meshed_bound.csv` gives a formal upper bound: for
every MESHED PUN x shift-set with 2 or more real neighbours present, `spread = max(PSENS_ERCOT) -
min(PSENS_ERCOT)` across those neighbours, `bound_MW = spread x max(|P10_I_P|, |P90_I_P|)`. This
bound is an upper limit, not a point estimate: it assumes the tie's entire export lands on the
single worst-case neighbour, while the state estimator actually splits flow across a MESHED PUN's
neighbours the way the real network does, so realised error is smaller in practice; it is driven
by the size of the PUN's own estimated injection at least as much as by shift-factor spread among
neighbours, not primarily by the spread. Of 504 PUN x set rows (21 distinct MESHED PUN stations,
all of them, including `MPPOI` and `LKVPD` since the bound only needs the ERCOT side), the median
bound is 0 MW (most sets don't touch a given PUN's flowgate at all); the median across the 187
rows with a materially nonzero bound (above 0.001 MW) is 0.010 MW. Top 10:

| PUN | Shift set | N neighbours | Spread (PSENS) | max\|I_PUN\| (MW) | Bound (MW) |
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

PSA and LYD dominate this table, and in both cases the bound is driven by the size of the PUN's
own estimated injection (PSA's P90 of 503.6 MW; LYD's P90 of 721.3 MW, itself entangled with CHE
per Section 5) rather than by an unusually large shift-factor spread among neighbours; the largest
bound that is genuinely shift-factor-driven rather than injection-size-driven is CELANEBI at 5.5
MW.

**kV placement.** Within-station kV placement is a non-issue almost everywhere: FORMOSA (54 buses
in the map, spanning 1/12/12.5/13.8/14/69/138 kV labels) and DOWGEN (48 buses, spanning
1/14/14.4/14.5/18/138 kV labels) show PSENS identical to machine precision at every kV level, for
every one of the 24 sets -- these stations behave as a single electrical node regardless of
voltage class. Scanning all 42 valued PUN stations, only 4 show a spread above 0.01 MW across kV
levels: CHE (max 2.11 MW), NCARBIDE (max 1.08 MW), PSA (max 0.11 MW), and SL (max 0.03 MW); three
more are nonzero but smaller: CELANEBI (0.0075 MW), VISTRON (0.005 MW), and BYU (0.004 MW). Of the
four largest, only CHE matters operationally -- its 138/345 kV split is a real transformer, not a
zero-impedance merge, and carries a materially different sensitivity, up to 2.1 MW, on the 1,314 MW `MDOPHR99A` branch (set 85771508, 0.16% of rating),
the largest kV-placement effect of any PUN station in absolute
MW though small as a share of rating. Any future placement decision for CHE specifically should
confirm which kV level the MW is actually injected at.

**Conclusion.** Lumping the tie MW at the neighbour station at the tie kV is equivalent to placing
it at the PUN station for radial ties, and within the stated bound for meshed ties. The current
`ERCOTSTATIONINJECTION` therefore already gives the fast scan the right answer for PUN MW to
within these bounds, and a back-out changes station-level reporting, not scan flows, except PSA
and LYD (28.7 / 7.6 MW bounds, driven by their own injection size), CELANEBI (5.5 MW, the largest
shift-factor-driven bound), and, separately and smaller, CHE for kV placement (2.1 MW, 0.16% of
rating).

## 7. Proposed method (design only, not deployed)

**Implemented 2026-09-25**: built as `ercot_pun_tie_map.sql` and `sp_load_ercot_pun_injection.sql`.
See `SESSION_HANDOFF.md`, "PUN injection loader", for the design fixes and dry-run results.

This is pseudocode for a design, not tested or executable SQL as written. A derived view,
`ERCOTPUNINJECTION`, at grain (TIMESTAMP, PUN station, tie kV), computed from
`ERCOTSTATIONINJECTION` plus the neighbour's DAM load and nearest-tick SCED gen (via the DAM gen
chain), grouped for entangled neighbours, tagged with the method flags from Section 5. This leaves
`ERCOTSTATIONINJECTION` itself unchanged; it is a new object, not a rewrite. Prerequisite not yet
fully verified: the crosswalk between `ERCOTSTATIONINJECTION.NMMSSTATIONCODE` and the DAM model's
`STATIONNAME` is confirmed equal for CHB, DOW, BCV, HL, LY, MTS, BT, DKR, LH, PWL, GRNBELT, and
CITGO_NO, but has not been verified globally across all ERCOT-side neighbours.

`PUN_TIE_MAP` must be materialised at (PUN station, real neighbour) grain, `DISTINCT` over ties --
several PUNs have multiple parallel physical ties to the same neighbour, and joining at raw tie
grain would double- (or triple-) count that neighbour's `N_S` in the `SUM(si.NETINJECTIONMW)`
below. NCARBIDE has 8 ties across only 6 distinct real neighbours; BBP has 3 ties to its single
real neighbour, PWL (`pun_topology.csv`, `N_TIES` vs `N_REAL_NEIGHBORS`). Separately,
`ERCOTSTATIONINJECTION` is at grain (TIMESTAMP, NMMSSTATIONCODE, KVLEVEL) per Section 3, and the
join below is on `NMMSSTATIONCODE` alone, so `si` is summed over every `KVLEVEL` row of each
neighbour station as well as over the group's neighbours -- a station with N kV-level rows at a
timestamp contributes all N to `n_s_total`, not one.

```sql
-- Pseudocode / design sketch, not tested. ISOMARKETID filters and the station-code crosswalk
-- (see prerequisite above) still need to be added before this is runnable.
CREATE OR REPLACE VIEW AWDEV.ERCOTRT.ERCOTPUNINJECTION AS
WITH neighbor_gen AS (
    SELECT sg."TIMESTAMP" AS gen_ts, ds.STATIONNAME AS station_name,
           SUM(sg.TELEMETEREDOUTPUT) AS gen_mw
    FROM AW.DBO.ISOERCOTSCEDGENRESOURCE sg
    JOIN AW.DBO.ISOERCOTSCEDGEN g ON g.GENID = sg.GENID
    JOIN AW.DBO.ERCOTDAMPSSEGNDEF dg ON dg.CPNODEID = g.CPNODEID
    JOIN AW.DBO.ERCOTDAMPSSESTATION ds ON ds.ERCOTDAMPSSESTATIONID = dg.STATIONID
    -- WHERE g.ISOMARKETID = 6  -- prerequisite: add ISO-6 filter once confirmed available here
    GROUP BY sg."TIMESTAMP", ds.STATIONNAME
),
neighbor_load AS (
    SELECT "DATE", HE, STATIONNAME, SUM(RAWMWLDF) AS load_mw
    FROM AW.DBO.ERCOTDAMPSSELDVIEW
    -- WHERE ISOMARKETID = 6  -- prerequisite: add ISO-6 filter once confirmed available here
    GROUP BY "DATE", HE, STATIONNAME
)
SELECT
    m.PUN_STATION,
    m.NEIGHBOR_GROUP_ID,                 -- shared across entangled PUNs
    si."TIMESTAMP",
    SUM(si.NETINJECTIONMW) AS n_s_total, -- summed over the group's real neighbours (each once) and
                                          -- all KVLEVEL rows of each neighbour station
    IFF(COUNT_IF(ng.gen_mw IS NULL) > 0, NULL, SUM(ng.gen_mw)) AS gen_s_total,
                                          -- SUM() alone ignores NULLs and would silently read a
                                          -- missing SCED tick as 0; force NULL if any row is missing
    IFF(COUNT_IF(nl.load_mw IS NULL) > 0, NULL, SUM(nl.load_mw)) AS load_s_total,
                                          -- same fix: SUM() alone would silently read a missing DAM
                                          -- load row as 0 instead of propagating NULL
    SUM(si.NETINJECTIONMW)
        - IFF(COUNT_IF(ng.gen_mw IS NULL) > 0, NULL, SUM(ng.gen_mw))
        + IFF(COUNT_IF(nl.load_mw IS NULL) > 0, NULL, SUM(nl.load_mw))
        AS i_pun_estimate,               -- NULL propagates; a coverage gap must not silently read as 0
    m.METHOD_TAG
FROM AWDEV.ERCOTRT.PUN_TIE_MAP m               -- materialized from pun_topology.csv / pun_tie_buses.csv
JOIN AW.DBO.ERCOTSTATIONINJECTION si ON si.NMMSSTATIONCODE = m.ERCOT_NEIGHBOR_STATION
    -- AND si.ISOMARKETID = 6  -- prerequisite: add ISO-6 filter once confirmed available here
LEFT JOIN neighbor_gen  ng ON ng.station_name = m.ERCOT_NEIGHBOR_STATION
                           AND ng.gen_ts = NEAREST_SCED_TICK(si."TIMESTAMP")
LEFT JOIN neighbor_load nl ON nl.STATIONNAME = m.ERCOT_NEIGHBOR_STATION
                           AND nl."DATE" = CAST(si."TIMESTAMP" AS DATE)
                           AND nl.HE = HOUR_ENDING(si."TIMESTAMP")
GROUP BY m.PUN_STATION, m.NEIGHBOR_GROUP_ID, si."TIMESTAMP", m.METHOD_TAG;
```

## 8. Caveats / NEEDS_CONTEXT

- **Gross-recompute correction, 2026-09-25**: `PUN_GROSS_SCED_MW` and `PUN_HSL_SUM_MW` in
  `backout_pun_estimates.csv`, and `MEAN_G_P`/implied load in `backout_truth_test.csv`, were
  originally computed by averaging each mapped unit's telemetry only over the ticks where that
  unit had a row, then summing those per-unit averages across a station's units. That
  overweights units that are frequently out of service or newly registered (each contributes its
  full running-average output rather than something closer to zero for the ticks it wasn't
  reporting). The fix sums `TELEMETEREDOUTPUT` across a station's units per SCED timestamp first
  (a unit with no row at a tick contributes 0 to that tick), then averages across timestamps.
  BTE's own gross moved from 868.5 to 411.3 MW; CCEC from 698.4 to 258.2 MW; PSA from 938.6 to
  357.9 MW; BYU from 266.7 to 110.2 MW. DOWGEN, AMOCOOIL, LHM, CARBN, TC, NCARBIDE, OXY_CC, and
  EXN were essentially unaffected (a single dominant unit, or continuously-running units, so the
  two averaging orders coincide). The lead's truth-test numbers (411.1 MW / corr 0.994 at BTE,
  258.8 MW / corr 0.998 at CCEC) are the per-timestamp station means; this spike's earlier
  recompute (415.3 / 261.3 MW) came from the same conditional-mean bug, now fixed (Section 4a).
- **DAM-forecast load error dominates at load-serving neighbours**: noise floor rises from
  sub-0.01 MW (no gen/load) to 2-12 MW (load-only) from DAM load-forecast error, not the SE solve.
  Treat the 24 DAM_LOAD_ADJUSTED rows as a few MW noisier than the 8 exact-switching rows; see
  Section 4c for the per-PUN `LOAD_ERR_MW` figure derived from this.
- **51 of 1,614 tracked SCED units are unmapped to a station** at the DAM-chain stage (1,614 is
  the second-stage population -- 1,798 distinct SCED resource names minus the 184 that fail the
  first stage entirely, Section 3; the 51 is ~4% MW-weighted of that 1,614, and 86.9% by count
  end to end across both mapping stages); no authoritative unit-to-NMMS-station table exists, so
  the busname+prefix+ratio-test chain used here is a best-effort reconstruction, especially for
  the 143 stations still on `PREFIX_FALLBACK`.
- **DOWGEN implied on-site load discrepancy**: back-out measures ~263 MW of implied on-site load
  (own SCED gross 14.2 MW minus -248.7 MW export); a separate DAM-model figure of ~131 MW exists
  for the DOWGEN bus itself (not the zero-load DOW neighbour), provenance unestablished. NEEDS_CONTEXT.
- **Gross-vs-net telemetry for PUN resources is open**: the truth test is consistent with either
  negligible on-site load at BTE/AMOCOOIL/CCEC, or SCED telemetry there already being net of
  on-site load. Either way SCED tracks the tie flow closely for those three, but the distinction
  matters wherever a PUN has real load (DOW is the counter-example; also see the DOW DAM-load note
  below).
- **DOW's DAM load is recorded but reads zero**: `pun_topology.csv` lists DOW as a load-bearing
  neighbour (`NEIGHBORS_WITH_DAM_LOAD=DOW`), but its DAM load is 0.0 MW in all 2,880 June rows of
  `ERCOTDAMPSSELDVIEW` (confirmed by direct query), which is why DOWGEN's `R_DOW = N_DOW` is
  treated as an unconfounded measurement above rather than a `Load_S`-adjusted one.
- **DAM-vs-SSWG bus-number trap**: the original fast-scan analysis (Section 6, now withdrawn)
  joined tie endpoints through `ERCOTDAMPSSELNVIEW`'s DAM-model PSSE bus numbers against
  `SHIFT_FACTORS.DBO.BUS_SHIFTS.BUSNUM`, which is keyed on SSWG bus numbers -- a different
  numbering scheme that happens to overlap in range, so the join silently paired unrelated
  physical buses instead of erroring. Found by the grading gate, not caught in the original
  build; treat any future PUN-side bus join as suspect unless it goes through the scan's own
  CIM-205/`ERCOTDATADICTIONARY` map. `MPPOI` and `LKVPD` still need a name crosswalk: neither
  appears in that map under those station codes, so their 7 ties (`6217_A`, `6217_B`, `1250_J`,
  `1250_F`, `1250_P`, `LKVEW_RC1`, `LKVTP_ONCOR_RC1`) remain unvalued.
- **56 vs 57 station count, resolved**: `pun_topology.csv` and `backout_pun_estimates.csv` both
  list 56 stations with zero diff between them. A naive split of `se_redacted_lines_2026-06.csv`'s
  `STATION_ABSENT_FROM_SE` column yields 57 tokens, but the 57th is the literal string "NA" from 4
  non-PUN redacted lines (`1580_E`, `1580_F`, `FT_NA_06A`, `NA_WEB06A`). There are 56 PUN stations.

## 9. Files index

| File | Contents |
|---|---|
| `inventory.md` | Schema inventory; confirms no SE gen/load-per-station MW table exists anywhere |
| `pun_topology.csv` | 56 PUN stations, tie counts, class, neighbour gen/load flags |
| `pun_tie_buses.csv` | 104 redacted lines resolved to bus numbers, PUN vs ERCOT side, class |
| `pun_sced_units.csv` | 23 PUN stations' own SCED-mapped units, telemetered output |
| `calibration_summary.md` / `calibration_by_station.csv` | SE-vs-SCED agreement, 443 well-mapped non-PUN stations |
| `backout_noise_floor.md` | Noise floor by neighbour class, 5,649 non-PUN-neighbour stations |
| `backout_pun_estimates.csv` | Per-PUN mean/P10/P90 `I_PUN`, corrected own SCED gross, `LOAD_ERR_MW` (median, p90), entanglement notes (the columns previously named `NEIGHBOR_NOISE_FLOOR_MW`/`SNR` have been removed; see `backout_residual_by_station.csv` and Section 4c instead) |
| `backout_truth_test.csv` | This spike's own truth-test recompute (corrected gross for BTE/CCEC/AMOCOOIL/DOWGEN), includes PSA+LHM_COMBINED |
| `backout_residual_by_station.csv` | Per-station mean/median/P90 residual; used to derive the PHILLPS2 group figure and the Section 4c `LOAD_ERR_MW` bins; `NOTE` column flags WAP's stale pre-fanout-correction `MEAN_R` (Section 4c) |
| `shiftequiv2_summary.md` | Current Section 6 source: coverage, |Delta|x100 distribution, worst-10 tables, corrected bound, kV-placement check |
| `shiftequiv2_ties.csv` | Current: PSENS(PUN) vs PSENS(ERCOT) per tie x shift-set, corrected SSWG/CIM map, `DEAD_END` flag, `PCT_OF_RATING` |
| `shiftequiv2_meshed_bound.csv` | Current: corrected meshed-lumping bound per MESHED PUN x shift-set |
| `shiftequiv2_station_kv.csv` | Current: PSENS by (station, kV-level) bucket, for the Section 6 kV-placement check |
| `pun_tie_buses.csv` | SUPERSEDED (bus-numbering artefact, Section 6) -- kept for audit. 104 redacted lines resolved to *DAM PSSE* bus numbers, PUN vs ERCOT side, class; do not join these numbers to `BUS_SHIFTS.BUSNUM` |
| `pun_shift_equivalence.md` / `.csv` | SUPERSEDED (bus-numbering artefact, Section 6) -- kept for audit. PSENS(PUN) vs PSENS(ERCOT), 25 shift sets, 81 real ties, computed against the wrong (DAM PSSE) bus numbering; superseded by `shiftequiv2_ties.csv` |
| `farfield_summary.md` / `farfield_by_set.csv` | SUPERSEDED (bus-numbering artefact, Section 6) -- kept for audit. Far-field mechanism test (rejected), run against the wrong bus numbering |
| `fastscan_meshed_bound.csv` | SUPERSEDED (bus-numbering artefact, Section 6) -- kept for audit. Meshed-lumping error bound per PUN x shift-set, computed against the wrong bus numbering; superseded by `shiftequiv2_meshed_bound.csv` |
| `.../output/se_redacted_lines_2026-06.csv` | 104 redacted DAM-model lines; source for the 56-vs-57 reconciliation |
| `.../se_redacted_lines_vs_dam_model.sql` | Query used to identify redacted lines from the DAM model |
| `.../sp_load_ercot_station_injection.sql` | Production proc populating `ERCOTSTATIONINJECTION`; source for Sections 2, 7, 9 |
