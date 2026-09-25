# PUN tie shift-factor equivalence

Question: for the fast scan (monitored-branch flow = Σ bus shift factor × injection), is it
harmless that a redacted tie's MW gets lumped at the ERCOT-side neighbour bus instead of the
true (PUN-side) bus? Harmless iff PSENS(PUN bus) ≈ PSENS(ERCOT-side bus) for the branches the
desk actually monitors.

Scope: 104 redacted DAM-model lines (`se_redacted_lines_2026-06.csv`), bus numbers resolved
from `AW.DBO.ERCOTDAMPSSELNVIEW` at DATE=2026-06-15 HE=12, shift factors from
`SHIFT_FACTORS.DBO.BUS_SHIFTS` (ISOMARKETID=6) for the 25 PSENSHIFTIDs backing the 25
FAST_SCAN_CONFIG rows with the most `FAST_SCAN_RESULTS` rows in 2026 (all tied at 4,559 rows
each — a healthy, actively-scored set of monitored branches).

Of the 104 redacted lines: **81** are genuine PUN↔ERCOT ties (58 MESHED, 23 RADIAL) with both
endpoints resolved; **19** are PUN↔PUN ties (both endpoints are PUN stations per
`pun_topology.csv` — no ERCOT-side comparison is possible, excluded from the stats below); **4**
(`1580_E`, `1580_F`, `FT_NA_06A`, `NA_WEB06A`) have neither endpoint matching a PUN station in
the topology file — these look like ordinary redacted-but-not-PUN lines and are excluded/flagged
in `pun_tie_buses.csv`.

## (a) Is the PUN-side bus even in BUS_SHIFTS?

Across the 81 real ties there are 73 distinct PUN-side buses. Checked against *every* shift set
ISO 6 has ever computed (not just the desk's top 25):

- **44 of 73 (60%) PUN-side buses appear in BUS_SHIFTS at all; 29 (40%) never appear in any
  shift set.**
- At the tie level: **50 of 81 ties (62%) have a PUN-side bus that shows up somewhere in
  BUS_SHIFTS; 31 of 81 (38%) never do** (list in `pun_tie_buses.csv` / reproducible from the
  `missing_ties` check above — includes AK, BTE, BYU×2, CARBN, CCEC, CELANEBI, DIB, EQUISTAR×2,
  FORMOSA, I_DUPP1, LGE, LHM, LKVPD, LYD, MPPOI×2, NCARBIDE×2, PHILLPS5×2, PL, PR, SCLPCOGN,
  SDSES, SL, TAM×2, TC×2).
- Restricting to just the desk's 25 monitored-branch shift sets, the number is almost identical
  (43/73 buses, 49/81 ties) — the PUN-side bus's absence is structural, not an artifact of which
  25 branches happened to be sampled.

**For these 31 ties the fast scan literally cannot place an injection at the PUN bus under any
shift set — lumping the tie's MW at the ERCOT-side neighbour isn't an approximation choice, it's
the only representable option.** But "only option" is not the same as "safe," and it is the
least-verified bucket precisely because there's no PUN-side PSENS to compare against. If the fast
scan effectively treats the missing PUN bus as contributing nothing, the resulting error is not
zero — it is `|PSENS_ERCOT| × tie_MW`, i.e. whatever the ERCOT-side bus's own sensitivity happens
to be. Over the 375 (tie × shift-set) pairs in our 25-config sample where the ERCOT-side bus has
a PSENS but the PUN-side bus is simply absent, `|PSENS_ERCOT|×100` has median 0.14 MW, p90 4.0
MW, max 22.9 MW (`BERPL_96A`/PL↔BER, `1250_P`/`1250_F` LKVPD↔TIMBR/LLTSW, `BYUMCB96A`,
`NCARBI_SEADRF11`/`NCARBI_SANDCR11`, all under the wide-area `6965` shift set) — the same shape
and magnitude as the tail in (b). **For these 31 ties the error from lumping is unquantifiable in
the direction of "how wrong is the PUN side," but is bounded by, and empirically similar to, the
Δ tail measured elsewhere in this analysis — it should be treated as an unverified continuation
of the tail in (b), not as a separately "safe" bucket.**

## (b) Distribution of |Δ| = |PSENS(PUN) − PSENS(ERCOT)| × 100

Computed over all (tie × PSENSHIFTID) pairs where both buses have a PSENS value (875 of 2,025
pairs = 81 ties × 25 shift sets; the other 1,150 pairs are NULL on one or both sides per (a)).

| Class  | n (valid pairs) | median | p75  | p90  | p95   | p99   | max |
|--------|-----------------|--------|------|------|-------|-------|-----|
| RADIAL | 225             | 0.05   | 0.33 | 1.58 | 5.99  | 20.9  | 100.0 |
| MESHED | 650             | 0.07   | 0.48 | 1.52 | 2.82  | 21.0  | 36.2 |

**RADIAL is ~0 in the typical case — confirmed at the median/p75 (≤0.3 MW error per 100 MW of
tie flow) — but the blanket "RADIAL ⇒ safe" claim is refuted by the tail.** Note the median isn't
*exactly* 0 even for RADIAL, where clean radial theory says it should be (same electrical path
beyond the ERCOT-side bus ⇒ identical shift factor): a small nonzero floor everywhere is the
signature of distributed slack in how these shift sets are referenced, not a topology surprise.

A handful of RADIAL ties blow past MESHED-tier errors: `BNTMIN16A` (23.2), `APA_UCC11` (21.1),
`DUP91` (20.2), `DOW_A_21`/`BLCBAY_VISTRO11`/`G138_221` (13-15), all driven by the same handful
of wide-area shift sets (see below). One additional RADIAL pair, `BLCBAY_VISTRO11` under the
shift set for branch `6830_B`, initially looked like the single worst case in this dataset
(Δ×100 = 100.0, PSENS(BLCBAYU4)=1.0000 exactly, PSENS(VISTRON)=0.0000 exactly) — but checking
`FAST_SCAN_CONFIG` and the raw `BUS_SHIFTS` distribution for that shift set (PSENSHIFTID
105366920) shows only **11 of 10,723 buses** in the whole system have any nonzero PSENS at all
under it (vs. 10,700+/10,722 nonzero for the other wide-area sets below). `6830_B`
(OLNEY↔CRDSW, 40 MW) sits on a near-empty/local shift-set footprint, not a genuine
system-spanning sensitivity — BLCBAYU4 being one of the rare nonzero buses looks like an
artifact of that narrow footprint rather than evidence the PUN lumping is uniquely dangerous
there. **This pair is excluded from the ranked tables and conclusion below**, and is reported
separately as a shift-set-construction caveat rather than a PUN-lumping finding.

**Worst 10 MESHED ties** (|Δ|×100 MW of monitored-branch flow error per 100 MW of tie flow, vs.
the branch's own `DEFAULT_RATE_B`; the degenerate `6830_B` shift set is excluded throughout, see
caveat above):

| Tie | PUN station | ERCOT neighbour | \|Δ\|×100 (MW) | Monitored branch (label) | Rating (MW) |
|---|---|---|---|---|---|
| BT_EXN66A | EXN | BT | 36.18 | 6965 | 1031.4 |
| CO_PL_84A | PL | CO | 24.18 | 6965 | 1031.4 |
| BSFHN_02A | BSF | HN | 23.91 | 6965 | 1031.4 |
| BSFBZ_02A | BSF | BZ | 23.81 | 6965 | 1031.4 |
| LKVTP_ONCOR_RC1 | LKVPD | LKVTP_RC | 22.83 | 6965 | 1031.4 |
| BOG_T6S1 | SL | BOG | 21.69 | 505_B | 1031.0 |
| GREENL_NCARBI11 | NCARBIDE | GREENLK | 21.24 | 6965 | 1031.4 |
| CANGRE_NCARBI11 | NCARBIDE | CANGREJO | 20.70 | 6965 | 1031.4 |
| CANGRE_NCARBI21 | NCARBIDE | CANGREJO | 20.51 | 6965 | 1031.4 |
| DKREXN83A | EXN | DKR | 18.58 | 890_H | 213.0 |

These are all against a ~1,031 MW-rated branch (`6965`/`505_B`), so in absolute MW terms they
look scary but are only 1.8-3.5% of the branch's rating. **Normalizing |Δ|×100 by the branch's
own `DEFAULT_RATE_B` reorders the ranking** and surfaces the pairs that could actually matter for
a headroom call:

| Tie | Class | \|Δ\|×100 (MW) | Monitored branch | Rating (MW) | \|Δ\|×100 as % of rating |
|---|---|---|---|---|---|
| DIBMNT21A (DIB↔MNT) | MESHED | 3.31 | HARI_VRBS11 | 30.0 | **11.0%** |
| APA_UCC11 (UCC_COGN↔APACHE) | RADIAL | 21.07 | 890_H | 213.0 | **9.9%** |
| EXNLH_03A (EXN↔LH) | MESHED | 15.89 | 12020_B | 179.3 | **8.9%** |
| DKREXN83A (EXN↔DKR) | MESHED | 18.58 | 890_H | 213.0 | **8.7%** |
| DOW_A_21 (DOWGEN↔DOW) | RADIAL | 14.79 | 12020_B | 179.3 | 8.3% |
| BLCBAY_VISTRO11 (VISTRON↔BLCBAYU4) | RADIAL | 14.12 | 12020_B | 179.3 | 7.9% |
| G138_221 (AMOCOOIL↔GRNBELT) | RADIAL | 13.45 | 12020_B | 179.3 | 7.5% |
| BFMMIR961 (BFM↔MIRAGE) | MESHED | 10.58 | 6215_A | 185.0 | 5.7% |
| ALIQUI_OXY_IN11 (OXY_INGL↔ALIQUING) | RADIAL | 11.80 | COTULL_REVEIL11 | 246.0 | 4.8% |

All four driving configs (`890_H`, `12020_B`, `HARI_VRBS11`, `6215_A`, `COTULL_REVEIL11`) were
spot-checked against `BUS_SHIFTS` and confirmed non-degenerate (thousands of nonzero buses each),
so these are genuine, not artifacts.

**The tail is concentrated in 4 of the 25 shift sets** (`6965`, `505_B`, `12020_B`, `890_H` —
mean |Δ|×100 of 8.1, 3.1, 3.1, 1.6 MW respectively, vs. ≤1.1 for every other config), not spread
evenly across the 25. `6965` alone accounts for 14 of the top-5%-worst pairs. Checked directly
against `SHIFT_FACTORS.DBO.BUS_SHIFTS` (count of nonzero PSENS out of 10,722-10,723 total buses
in the system): `6965` (PSENSHIFTID 84813542) is nonzero at 10,700 buses, `505_B` (84967546) at
10,721, `12020_B` (85181110) at 10,323, `890_H` (105406151) at 4,944 — these four configs
genuinely do have shift-factor footprints spanning most or all of the system (confirmed, not
inferred), unlike a typical config where PSENS decays to ~0 a few buses from the branch. This is
why they dominate the tail: any PUN-vs-ERCOT bus pair, anywhere, has a good chance of showing a
real, non-negligible PSENS difference under one of these four.

## (c) Are the large-Δ MESHED PUNs genuine through-paths?

Yes, for the stations driving the worst cases. Looking at how much PSENS varies **among a
MESHED PUN's own real neighbours** (same shift set, different neighbour stations):

| PUN station | Shift set | PSENS range across its real neighbours | spread |
|---|---|---|---|
| EXN | 84813542 (`6965`) | 0.0124 to 0.3749 | 0.363 |
| NCARBIDE | 84813542 (`6965`) | −0.1975 to 0.0134 | 0.211 |
| SL | 84967546 (`505_B`) | −0.0947 to 0.0823 | 0.177 |
| EXN | 85181110 (`12020_B`) | −0.0052 to 0.1537 | 0.159 |
| SCLPCOGN | 84813542 (`6965`) | −0.0820 to 0.0128 | 0.095 |

EXN's three real neighbours (BT, DKR, LH) span PSENS 0.012–0.375 under the same shift set —
a 30x spread between neighbours of the *same* PUN station. That is the signature of a genuine
electrical crossroads: EXN sits on a real through-path where flow really does split unevenly
depending on which side of the station you inject at, so no single "neighbour" choice is a good
proxy for the others, let alone for the PUN bus itself. The same holds for NCARBIDE, SL, and
SCLPCOGN (all appear repeatedly in the worst-10 lists above). This means the large PUN-vs-ERCOT
Δ at these stations isn't a fluke of picking the "wrong" neighbour in the topology build — even
the *right* neighbour would disagree with its siblings by a similar margin, because the
underlying network genuinely fans out there.

## (d) Conclusion

For most of the 81 real PUN ties, lumping the redacted tie's MW at the ERCOT-side neighbour is
harmless for the fast scan: median/typical |Δ|×100 is ≤0.1-0.2 MW of monitored-branch-flow error
per 100 MW of tie flow, for both RADIAL and (somewhat surprisingly) MESHED ties alike — the shift
factors really are close at the two ends most of the time, and a small nonzero RADIAL floor is
just reference-slack noise, not a real electrical difference. It also can't be avoided for 31 of
the 81 ties (38%), since the PUN-side bus never appears in BUS_SHIFTS under any shift set ISO 6
has computed — there the neighbour lumping is the only representable choice. That bucket is not
verified safe, though: where a PSENS-at-the-ERCOT-bus number does exist for the same tie under
another shift set, it shows the same tail shape as below (median 0.14, p90 4.0, max 22.9
MW/100MW) — so treat "unavoidable" as "unavoidable and unquantified," not "unavoidable and fine."

The assumption breaks materially, and non-randomly, for a specific subset: about 10% of (tie ×
shift-set) pairs, concentrated in 4 of the 25 monitored branches (`6965`, `505_B`, `12020_B`,
`890_H`) whose shift-factor footprint genuinely spans nearly the whole system (confirmed via
`BUS_SHIFTS` nonzero-bus counts, not inferred) — so PUN-adjacent bus pairs anywhere are likely to
show a real difference under one of these four. In absolute MW the worst raw numbers (20-36
MW/100MW at EXN, NCARBIDE, SL, BSF, PL, LKVPD) are all against the ~1,031 MW-rated `6965`/`505_B`
branches, so proportionally small (≤3.5% of rating). **Normalized by rating, the single worst
case is `DIBMNT21A` (DIB↔MNT): 3.3 MW/100MW of tie flow against a 30 MW-rated branch
(`HARI_VRBS11`) — 11% of that branch's rating per 100 MW of tie flow lost to the lumping
approximation** — with `APA_UCC11` (9.9% of a 213 MW branch), `EXNLH_03A` (8.9% of 179 MW), and
`DKREXN83A` (8.7% of 213 MW) close behind. If actual flow on the DIB/APA_UCC/EXN ties is a
meaningful fraction of tie capacity, these are the cases that could plausibly flip a "no headroom
concern" read for a small-rated monitored branch. (One additional pair, `BLCBAY_VISTRO11` against
branch `6830_B`, showed the largest raw number in the dataset, Δ×100=100 MW/40MW rating — but
that shift set is a near-empty, 11-of-10,723-bus footprint, confirmed degenerate, and is excluded
from this ranking rather than treated as a finding; it's flagged separately as a data-quality
caveat for whoever owns `FAST_SCAN_CONFIG`/shift-set generation.)

**Bottom line: the PUN-lumping simplification is safe on average and structurally unavoidable
for ~38% of ties, but it is not uniformly safe. It should specifically be flagged for ties into
EXN, NCARBIDE, SL, DIB, PL/LKVPD/BSF-adjacent stations and for UCC_COGN/APACHE — particularly
against the smaller-rated monitored branches (`HARI_VRBS11` 30 MW, `890_H`/`12020_B` ~180-213
MW) where the error is a double-digit percentage of rating, not just a large-looking raw MW
number against a 1,000+ MW branch.**

## Files

- `pun_tie_buses.csv` — 104 rows, one per redacted line: PUN station/bus, ERCOT-side
  station/bus, kV, class, and a note flagging PUN-PUN ties, unidentified ties, or missing bus
  lookups.
- `pun_shift_equivalence.csv` — 2,025 rows (81 real ties × 25 shift sets): PSENS at both ends,
  Δ, |Δ|×100, and the config's branch label / DEFAULT_RATE_B.
