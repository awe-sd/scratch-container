# `RAW_STATION_NET_LOAD_MW` vs `STATION_NET_LOAD_MW` — what the difference actually is

Verified against live Snowflake 2026-08-28. Answers sdalvi's question: *"why are
we using RAW net load, I want an example where the expected net load was
different than expected."*

Companion to `load_estimation_schema.md` §3.2.

> **Correction notice.** An earlier revision of this doc (and of
> `load_estimation_schema.md` §3.2, and `pull_load_estimation.py`'s docstring)
> described the plain column as *"zeroed by the pipeline for PUN-scored
> station-hours"* and claimed ~6,133 MW of load was being *hidden*. **That
> reading was wrong.** The plain column does not hide load — it **relocates**
> each PUN component's net load onto one representative station. Nothing is
> lost; the component total is conserved exactly. §3 below is the proof. The
> practical conclusion (use `RAW_` for `InjectionFlow`) survives, but the reason
> is different and the "hidden MW" figures should not be quoted.

---

## 1. The short answer

Both columns are correct. They answer different questions.

| | what it gives you | right for |
|---|---|---|
| `RAW_STATION_NET_LOAD_MW` | each station's **own physical** net injection | anything **location-weighted** — shift factors, flows, congestion |
| `STATION_NET_LOAD_MW` | PUN component totals collapsed onto one **representative** station | **system/zone totals**, where you must not double-count a PUN |

`InjectionFlow` computes `SUM(StationPSENS × net)`. A shift factor is a property
of *where the load physically sits*, so the plain column — which teleports load
from SNDSW to CHRLY — applies the wrong station's sensitivity. That is why we
use `RAW_`. It is not because the plain column is broken.

## 2. The worked example: SNDSW, 2026-02-20

| SE_TIMESTAMP | `ercotStationLoad`<br>`WITHDRAWMW` | plain<br>`STATION_NET_LOAD_MW` | **`RAW_STATION_`<br>`NET_LOAD_MW`** | `term_bal`<br>`SUM(TOTAL_NET_LOAD_MW)` |
|---|---:|---:|---:|---:|
| 00:57 | 683.06 | **0.0** | 685.46 | 685.456671 |
| 03:57 | 680.03 | **0.0** | 713.74 | 713.743950 |
| 08:57 | 677.01 | **0.0** | 693.20 | 693.202338 |
| 15:57 | 681.47 | **0.0** | 728.06 | 728.056169 |
| 23:57 | 678.19 | **0.0** | 694.17 | 694.168448 |

Plain reads exactly 0.0 in all 72 hours checked (2026-02-19 → 02-21). `term_bal`
reproduces `RAW_` to six decimals, as expected — same underlying estimate.

**On the `ercotStationLoad` corroboration, stated honestly:** the agreement is
0.35% at 00:57 but **4.9–6.8% later in the day**, and the two sources disagree
on *shape*, not just level — `WITHDRAWMW` is nearly flat (676.99–683.06, a 6 MW
range) while `RAW_NET` swings 682–728 (46 MW). So `ercotStationLoad` confirms
the **order of magnitude and the existence** of ~680 MW at SNDSW; it does not
validate `RAW_` hour by hour. That is enough for the point being made here —
680 versus 0 is the whole argument — but do not cite this as tight agreement.

Metadata on those rows: `PUN_SCORE = 0.1538`, `COVERAGE_FLAG = HIGH`,
`HAS_LOAD = True`, `HAS_GENERATOR = False`, `RAW_STATION_EST_GENERATION_MW = 0`.
`GENMW` is NULL for SNDSW in `ercotStationLoad` all day — the same
NULL-generation gap in `genmw_coverage.md`.

## 3. What is really happening: PUN component allocation

SNDSW belongs to **PUN component 45 = {CHRLY, RKDLE, SDSES, SNDSW}** — the
Sandow/Rockdale complex — with **CHRLY as `PUN_COMPONENT_REPRESENTATIVE`**. At
2026-02-20 00:57:

| Station | role | `STATION_NET_LOAD_MW` | `RAW_STATION_NET_LOAD_MW` |
|---|---|---:|---:|
| **CHRLY** | representative | **699.249737** | NULL |
| RKDLE | member | 0.0 | 13.793066 |
| SDSES | member | 0.0 | NULL |
| SNDSW | member | 0.0 | 685.456671 |
| | | **Σ = 699.249737** | **Σ = 699.249737** |

`PUN_COMPONENT_NET_LOAD_MW` = **699.249737**. Both columns sum to it exactly.

Two independent confirmations that this is the general rule, not one lucky row:

**The predicate is exact.** Over Feb-2026, restricted to `pun_score > 0`:

| | rows | hard-zeroed (=0 while \|RAW\| > 1 MW) |
|---|---:|---:|
| is the representative | 61,275 | **0** |
| is *not* the representative | 75,817 | 62,720 |

Every one of the 62,720 zeroed rows is a non-representative. Zero exceptions.

**Conservation holds for every component.** At 2026-02-20 00:57, across all
**114** PUN components: `SUM(RAW)` matches `PUN_COMPONENT_NET_LOAD_MW` for
**114/114**, worst gap **0.000 MW**. `SUM(PLAIN)` likewise 114/114.

And where `pun_score = 0` — 3,475,723 rows, 94.1% of all station-hours — the two
columns are bit-identical, zero divergence. The columns only differ inside PUN
components.

## 4. NULLs — the one thing to handle

Neither column is complete row-by-row. Feb-2026, 3,691,992 rows:

| | RAW NULL | PLAIN NULL |
|---|---:|---:|
| no PUN component (3,475,723 rows) | 0 | 0 |
| non-representative (108,523) | 32,706 | 0 |
| representative (107,746) | 46,471 | 24,744 |

`RAW_` is NULL on 79,177 rows (2.1%), concentrated at representatives. Because
`SUM(RAW)` still reconciles to the component total exactly, a NULL means *this
station contributes nothing of its own* — so **`SUM()` skipping it is the
correct behaviour**, and `COALESCE(RAW_STATION_NET_LOAD_MW, 0)` is safe and
equivalent. Do not treat RAW NULL as missing data.

## 5. Why this decides the `InjectionFlow` column choice

`SUM(StationPSENS × net)` weights each station by its own shift factor.

- With **`RAW_`**, SNDSW's 685 MW is weighted by SNDSW's shift factor. Correct.
- With **plain**, SNDSW contributes 0 and CHRLY contributes 699 MW — the whole
  Sandow complex is weighted by CHRLY's shift factor. Wrong unless CHRLY and
  SNDSW happen to have identical sensitivities on the monitored element.
- **Worse, if the member set is partial.** If your `Members`/`StationShifts` set
  contains SNDSW but not CHRLY, the plain column contributes **nothing at all**
  for a 685 MW load. If it contains CHRLY but not SNDSW, you pick up the entire
  699 MW component at a station that physically draws none of it.

The join in the CTE is `ss.StationCode = sb.STATION`, and `ercotStationLoad`
carries SNDSW as its own 683 MW station — so the shift table is keyed to real
station codes, which is the convention `RAW_` matches.

**Conversely**: if you ever sum this family to a zone or system total, use the
**plain** column, or you are fine with `RAW_` too since both conserve — but
never mix them, and never sum `PUN_COMPONENT_NET_LOAD_MW` across member rows
(it repeats on every member, so it would multiply by component size).

**Recommendation for `InjectionFlow`: keep `RAW_STATION_NET_LOAD_MW`**, and
carry `PUN_COMPONENT_ID` / `PUN_COMPONENT_REPRESENTATIVE` through any diagnostic
output so PUN components stay visible.

## 6. Sharpened question for the SWE team

Supersedes the third bullet of item 6 in `swe_refresh_request.md`, which asked
"deliberate masking or a defect?" — the answer is **neither**: it is
representative-based PUN component allocation. Remaining questions:

1. **How is the representative chosen**, and is it stable over time? If it
   migrates between stations, the plain column's time series has jumps that are
   pure bookkeeping. (`PUN_COMPONENT_ID` 45 → CHRLY held across all our samples,
   but we have not tested stability across months.)
2. **Why is `RAW_` NULL at 43% of representative rows** rather than 0? A NULL
   and a 0 mean the same thing arithmetically here, but the choice is
   unexplained.
3. **Is the component decomposition in `RAW_` physically metered or modelled?**
   §2 shows `RAW_` and `ercotStationLoad` disagree on intra-day shape at SNDSW
   by up to 6.8%; knowing which is the better physical estimate matters for
   anyone using this location-weighted.

---

## Appendix: queries

Scripts (scratchpad, read-only): `raw_vs_plain.py`, `raw_vs_plain2.py`,
`pun_component.py`, `raw_nulls.py`.

```sql
-- §3 the decisive one: component membership and conservation
SELECT STATION, PUN_SCORE, PUN_COMPONENT_ID, PUN_COMPONENT_STATIONS,
       PUN_COMPONENT_REPRESENTATIVE, PUN_COMPONENT_NET_LOAD_MW,
       STATION_NET_LOAD_MW, RAW_STATION_NET_LOAD_MW
FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
WHERE SE_TIMESTAMP = '2026-02-20 00:57:00' AND PUN_COMPONENT_ID = 45
ORDER BY STATION;

-- §3 zeroing == non-representative, exactly
SELECT (STATION = PUN_COMPONENT_REPRESENTATIVE) AS IS_REP, COUNT(*) AS N,
       COUNT_IF(STATION_NET_LOAD_MW = 0 AND ABS(RAW_STATION_NET_LOAD_MW) > 1) AS N_ZEROED
FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
WHERE SE_TIMESTAMP >= '2026-02-01' AND SE_TIMESTAMP < '2026-03-01' AND PUN_SCORE > 0
GROUP BY 1;

-- §3 conservation across every component
WITH per_comp AS (
    SELECT PUN_COMPONENT_ID,
           MAX(PUN_COMPONENT_NET_LOAD_MW) AS COMP_TOTAL,
           SUM(RAW_STATION_NET_LOAD_MW)   AS SUM_RAW,
           SUM(STATION_NET_LOAD_MW)       AS SUM_PLAIN
    FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
    WHERE SE_TIMESTAMP = '2026-02-20 00:57:00' AND PUN_COMPONENT_ID IS NOT NULL
    GROUP BY PUN_COMPONENT_ID
)
SELECT COUNT(*) AS N_COMPONENTS,
       COUNT_IF(ABS(SUM_RAW - COMP_TOTAL) < 0.001)   AS RAW_MATCHES,
       COUNT_IF(ABS(SUM_PLAIN - COMP_TOTAL) < 0.001) AS PLAIN_MATCHES,
       ROUND(MAX(ABS(SUM_RAW - COMP_TOTAL)), 3)      AS WORST_RAW_GAP
FROM per_comp;
```
