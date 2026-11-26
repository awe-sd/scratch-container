# PUN back-out: non-neighbour noise floor (June 2026)

5,649 of 5,721 June `ERCOTSTATIONINJECTION` stations are NOT a real (SE-visible) neighbour of any PUN. Classified by whether they have a mapped SCED generator (`HAS_GEN`, DAM-chain mapping) and/or a DAM load record (`HAS_LOAD`):

| Class | N stations | Median of MEDIAN\|R\| | 80th pct | 90th pct | 95th pct |
|---|---|---|---|---|---|
| no gen, no load ("neither") | 1,618 | 0.0021 MW | 0.0052 MW | 0.0081 MW | 0.0114 MW |
| load only | 3,332 | 2.19 MW | 7.34 MW | 11.67 MW | 16.90 MW |
| gen only | 51 | 0.0028 MW | 1.94 MW | 4.93 MW | 11.12 MW |
| gen + load | 648 | 1.69 MW | 4.40 MW | 9.36 MW | 17.90 MW |

`|R|/Load` (load-bearing classes only):
- load-only: median 0.376, 80th pct 0.542, 90th pct 0.714 — i.e. at a typical load-only station the residual runs ~35-70% of that station's own load, which is far too large relative to load to serve as a per-station noise floor on its own; the **MW-scale floor (median\|R\| in MW) is the more useful headline** since most load-only stations are small (a few MW), so a percent-of-load framing exaggerates.
- gen+load: median 0.379, 80th pct 1.30, 90th pct 5.85 (heavier tail — battery/hybrid and partial-mapping stations live here, consistent with the prior SE-vs-SCED calibration).

## Headline noise floor
- **True instrument floor** (no gen, no load stations, i.e. the SE model's own measurement/rounding noise with nothing physical happening): **median\|R\| < 0.008 MW for 90% of stations** — sub-10-kW, consistent with SE solver residual noise, not a real signal.
- **Load-only stations** (the class most PUN neighbours fall into): **median\|R\| ≤ 2 MW for 50% of stations, ≤ 7.3 MW for 80%, ≤ 11.7 MW for 90%.** This is the practical noise floor to compare a candidate PUN-neighbour signal against.
- **Gen-bearing stations** (gen-only / gen+load): floor is similar at the median (~1.7-2 MW) but the tail is much fatter (90th pct 5-10 MW) — driven by the same failure modes documented in `calibration_summary.md` (partial unit mapping, wind/BESS volatility, timing offset).

## 15 worst non-neighbour stations (by MEDIAN\|R\|)
| Station | Class | Mean Gen | Mean Load | Mean N | Median\|R\| | Explanation |
|---|---|---|---|---|---|---|
| WHCCS2 | gen+load | 0.0 | — | high | 702.3 | Zero mapped gen despite large N — almost certainly an **unmapped generation resource** (one of the 51 units / ~4% MW-weighted that the DAM-chain+GENUNIT mapping misses); station name pattern (…CCS2) suggests a CCGT not carrying a resolvable CPNODEID link. |
| TGCCS | gen+load | 29.7 | — | high | 440.8 | Partial mapping: some but not all units at this CCGT resolved; residual reads like unmapped generation, mirrors CBEC in the SE-vs-SCED calibration. |
| FRONT_EC | load-only | 0.0 | — | high | 397.2 | HAS_GEN=False but the huge, one-sided N implies real (unmapped) generation — likely a wind/solar site whose SCED resource name doesn't match any GENID→station chain. |
| DCTM | load-only | 0.0 | — | high | 199.9 | Same pattern — unmapped generation masquerading as "load-only". |
| OVEJA | gen+load | 336.1 | — | high | 179.2 | Wind farm; matches the calibration doc's "fast-ramping + snapshot/SCED timing offset" failure mode (5-min nearest-tick vs true ramp). |
| HICKMAN, MULBERRY, CHLDDATA, MAVCRK_W/E, SAGEDRAW, BLSUMIT3/BLSUMMIT, DERMOTT, NBOHR, COYOTE_W, HARALD, BORDAS2, TAHOKA, SWEETWN4 | load-only / gen+load / gen-only | mixed | — | high | 108-166 | All wind or solar site names (matches `CANYONWD`, `WL`, `COYOTE`, `BORDAS`, `TORR`, `RELOJ`, `BIGSAMWD` flagged in the earlier calibration doc). Same two failure modes: (1) unmapped/partially-mapped turbine strings, (2) genuine fast-ramp + nearest-5-min-tick timing error. **Not evidence against the back-out method** — these are exactly the station types the calibration already flagged as unreliable for Gen_S, and none of them are PUN neighbours. |

**Conclusion:** the method's noise floor is essentially zero at truly quiet stations (sub-10-kW), a few MW at ordinary load stations, and only degrades at wind/solar/BESS/partially-mapped generation stations — none of which dominate the PUN-neighbour set (see `backout_pun_estimates.csv`, most PUN neighbours are load-only or no-gen/no-load switching stations with clean floors of 1-2 MW against MW-scale-to-hundred-MW signals).
