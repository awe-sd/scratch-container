# Far-field PSENS check on PUN tie shift-equivalence, 25 shift sets

## Bottom line

The **operational conclusion is well-supported and unaffected by anything
below**: a RADIAL tie's two ends must physically match, they don't (34 of
225 RADIAL pairs differ by >1 MW/100MW, up to 23 MW), and genuinely radial
non-PUN buses do match exactly (per the CPSES 150111/150112 vs. 1900 control
in the brief). PUN-side PSENS values on RADIAL ties are unusable as
injection sensitivities, whatever the cause, and ERCOT-side lumping is the
right fast-scan treatment for RADIAL ties on that basis alone.

**The proposed *mechanism* -- "PUN buses are far-field because they're
disconnected under distributed slack" -- is NOT supported.** I ran three
checks against ground truth and all three came back negative:

1. **Lift vs. base rate ≈ 1.0.** The far-field flag rate for PUN buses is
   statistically indistinguishable from the far-field rate of a random bus
   in the same set (see below) -- the flag is measuring "how big is this
   set's far-field band," not "is this a PUN bus."
2. **`DEADBUS=0`** on both ends of the motivating example (bus 559/MIN and
   bus 1276/BNT under PSENSHIFTID 84813542) -- the model does not consider
   either bus disconnected.
3. **On buses the model *does* flag `DEADBUS=1`** (confirmed-dead, not PUN),
   the far-field test only catches them **35% of the time.** A detector that
   misses known-dead buses 65% of the time is not measuring disconnection.

So: act on the RADIAL-identity-violation finding (it's solid), but do not
carry forward "PUN buses are far-field" as an established mechanism --
report it as open, and see the branch-open alternative in the conclusion.

## Method

Per spec: for each PSENSHIFTID, queried `SHIFT_FACTORS.DBO.BUS_SHIFTS`
(ISOMARKETID=6), grouped buses by `ROUND(PSENS,4)`, took the far-field
constant = the modal rounded value, flagged `|PSENS - constant| <= 0.0008`
as far-field. Results are in `farfield_flagged.csv` (row-level) and
`farfield_by_set.csv` (per-set constant + `SHARE_FARFIELD` + a
`RELIABILITY` column). **Relabel `RELIABILITY` as a base-rate tier, not a
confidence measure** -- see the lift check below for why.

Three follow-up checks, all done locally from data already pulled (no extra
queries beyond the two noted):

- **Exact-value spike test** (one extra query, `farfield_exact_spike.csv`):
  only 2 of 25 sets (101827040, 105366920) have a true degenerate spike
  (99.9%+ of buses at *exactly* 0.0000). In those two sets PSENS_PUN and
  PSENS_ERCOT are both ~0 on every tie -- not PUN-specific, these are
  structurally different (near-null) shift sets and are excluded below as
  `DEGENERATE_ALL_ZERO`. The other 23 sets show `SHARE_FARFIELD` (share of
  all 10,722-10,723 buses within tolerance of the mode) ranging continuously
  from 6.3% to 89.1% -- no clean spike/no-spike split.
- **`DEADBUS` ground truth** (one extra query, `farfield_deadbus_check.csv`,
  all 73 PUN-side + all ERCOT-side buses x 25 sets = 2,025 rows returned of
  3,325 possible). Only 54 rows have `DEADBUS=1`, concentrated on two buses
  (474: 25 obs, 6693: 25 obs) that are **not PUN- or ERCOT-side ties** --
  generic buses that happen to be dead in some cases. Joining the far-field
  flag onto these 54 known-dead observations: **19 of 54 (35%) are flagged
  far-field** (bus 474: 13/25 = 52%; bus 6693: 6/25 = 24%). This is the
  cleanest falsification in the analysis: a bus the underlying case marks as
  literally disconnected fails the far-field test most of the time.
- **Base-rate / lift check** (no query, from `farfield_by_set.csv`): mean
  `SHARE_FARFIELD` across the 9 HIGH-tier sets = 0.714; PUN-bus far-field
  rate in those same 9 sets = 0.726 -- lift ≈ **1.02**. Pooled over all 25
  sets: expected far-field bus-observations under "PUN buses behave like a
  random bus" = 43 buses x mean(SHARE_FARFIELD)=12.23/25 per set-sum ≈ 526;
  observed = 554 -- lift ≈ **1.05**. Essentially no lift. Whatever tier a
  set falls in, PUN buses land in the far-field band about as often as any
  other bus does in that same set.
- **A cleaner, harder signal that doesn't depend on any tolerance band:**
  30 of the 73 distinct PUN-side buses in the CSV have **no PSENS value in
  `BUS_SHIFTS` at all, in any of the 25 sets** -- confirmed by re-querying
  those exact BUSNUMs; they are absent from the table entirely, not merely
  an extraction gap in the CSV build. That is unambiguous: those 30 buses
  are simply not modeled in these cases, full stop, and cannot be used for
  injection placement -- no tolerance judgment call needed. The 43 buses
  with data are the ones the rest of this report is about, and for them the
  far-field label carries little information (see lift, above).

## (a) PUN far-field while ERCOT-side is not, by CLASS (tie x set pairs, both PSENS present)

Overall (23 non-degenerate sets pooled):

| CLASS  | pairs | PUN-farfield-only | share |
|--------|-------|--------------------|-------|
| MESHED | 650   | 60                 | 9.2%  |
| RADIAL | 225   | 42                 | 18.7% |

RADIAL ties show the pattern ~2x as often as MESHED, which matches the
*identity* argument (a radial dead-end has no real path, so if anything is
going to fall in the far-field band, it should), but given the lift ≈ 1.0
finding above, treat this gap as circumstantial support at best, not proof
of the far-field mechanism specifically.

## (b) RADIAL pairs, |delta|x100 > 1 MW

- RADIAL pairs total: 225; with |delta|x100 > 1 MW: **34**
- Explained by PUN_FARFIELD (PUN side flagged far-field): **8 of 34 (24%)**
  -- **the "nearly all" expectation does not hold**, consistent with the
  detector's ~35% true-positive rate on known-dead buses above (same order
  of magnitude).

Full "not explained" list in `farfield_flagged.csv`
(`CLASS=="RADIAL" & ABS_DELTA_X100_MW>1 & PUN_FARFIELD!=True`). Notable
recurring ties in that list, appearing across multiple sets with PSENS_PUN
values that move around a lot (not sitting near any set's constant) rather
than looking like near-misses on a tolerance band: `ALIQUI_OXY_IN11`
(OXY_INGL/ALIQUING, 8 occurrences, PSENS_PUN 0.003-0.085), `APA_UCC11`
(UCC_COGN/APACHE, PSENS_PUN -0.220), `BLCBAY_VISTRO11` (VISTRON/BLCBAYU4,
PSENS_PUN 0.017 vs PSENS_ERCOT 0.158). These look like real, if noisy,
divergence between the two ends -- exactly what the RADIAL-identity
violation says should not happen, regardless of far-field status. This is
independent confirmation that the values are simply unusable on these ties,
not that a mechanism has been identified.

## (c) MESHED distribution of |delta|x100, excluding PUN_FARFIELD rows

MESHED pairs total: 650; after excluding PUN_FARFIELD rows: 334

- median: **0.36 MW**
- p90: **2.77 MW**
- max: **36.18 MW**

Worst 5 (all on branch 6965 / PSENSHIFTID 84813542, a MEDIUM-tier set with a
two-humped PSENS histogram, 0.0130 vs 0.0145):

| BRANCH | TIE | Rating (A) | PUN station | ERCOT station | PSENS_PUN | PSENS_ERCOT | constant | \|delta\|x100 |
|---|---|---|---|---|---|---|---|---|
| 6965 | BT_EXN66A | 1031.4 | EXN | BT | 0.0131 | 0.3749 | 0.0145 | 36.18 |
| 6965 | CO_PL_84A | 1031.4 | PL | CO | -0.2287 | 0.0131 | 0.0145 | 24.18 |
| 6965 | BSFHN_02A | 1031.4 | BSF | HN | -0.2249 | 0.0142 | 0.0145 | 23.91 |
| 6965 | BSFBZ_02A | 1031.4 | BSF | BZ | -0.2249 | 0.0132 | 0.0145 | 23.81 |
| 6965 | LKVTP_ONCOR_RC1 | 1031.4 | LKVPD | LKVTP_RC | 0.0163 | -0.2120 | 0.0145 | 22.83 |

In each row PSENS_PUN sits at or near this set's constant (0.0131-0.0163
against 0.0145) while PSENS_ERCOT is the outlier (-0.225 to +0.375). Given
the lift/DEADBUS findings above, don't over-read this as proof PSENS_PUN is
"the disconnected one" -- it's equally consistent with PSENS_ERCOT simply
being a genuinely large real sensitivity on a meshed path (which MESHED ties
are allowed to have) while PSENS_PUN happens to be small. Either way,
PSENS_PUN is the smaller/near-null value here, so if a substitution is
needed, use PSENS_ERCOT, not PSENS_PUN -- do **not** average or prefer the
PUN-side number for these rows.

## (d) 73 distinct PUN-side buses: consistency of far-field status

- 73 distinct PUN-side buses; **30 are absent from `BUS_SHIFTS` in all 25
  sets** (see method section -- a clean, tolerance-free "not modeled"
  signal). 43 have data in at least one set.
- Of the 43: pooled across all 23 non-degenerate sets, 0 are far-field in
  every set, 0 are never far-field; mean far-field fraction 51.5%.
  Restricted to the 9 HIGH base-rate-tier sets, mean rises to 72.6% -- but
  the base rate in those same 9 sets is 71.4% (lift ≈ 1.02, see above), so
  this rise tracks the tier's base rate, not a PUN-specific effect.

## (e) Conclusion

**Operational answer (well-supported):** No, don't place a real injection
directly at a PUN bus using these shift sets, and yes, lumping at the
ERCOT-side neighbour is the right fast-scan treatment for RADIAL ties --
but on the strength of the RADIAL-identity violation itself (34/225 pairs
differ by >1 MW, up to 23 MW, against a physical requirement that they be
identical, corroborated by non-PUN radial controls matching exactly), not
on the strength of a confirmed far-field mechanism. For 30 of the 73 PUN
buses this is moot -- they simply have no PSENS value in any of these 25
sets and cannot be used at all. For MESHED ties the identity argument
doesn't apply (the two ends are allowed to differ), so ERCOT-side lumping
there is only an approximation, with error up to 0.36 MW median / 2.77 MW
p90 / 36 MW max (worst case all on one branch, 6965).

**Mechanism (not supported -- report as open, not established):** three
independent checks (lift ≈ 1.0-1.05 vs. base rate, `DEADBUS=0` on both ends
of the motivating bus-559 example, and a 35% true-positive rate on
confirmed-dead control buses) all argue against "PUN buses take the
far-field constant because they're disconnected under distributed slack."
The `MODE(ROUND(PSENS,4))`-based flag mostly reflects how large each set's
own far-field band happens to be, not which buses are PUN. **The live
alternative hypothesis, not checked this session:** the tie *branch itself*
may be open/out of service in some cases, which would legitimately decouple
the two ends without either bus being "dead." This would need a branch/tie
in-service or topology status table (not identified in this session's
budget) joined by PSENSHIFTID x branch. It matters because it would **flip**
part of the operational recommendation: an injection at a PUN bus behind a
genuinely open tie does not reach the ERCOT-side neighbour through that
path at all, so lumping would be wrong for exactly those (PSENSHIFTID,
tie) combinations, even though it's right for the rest. Recommend that as
the next query before this method is used to build the injection-placement
table for real.
