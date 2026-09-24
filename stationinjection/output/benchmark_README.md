# Benchmark: ERCOTSTATIONINJECTION vs ERCOTSTATIONLOAD
Run 2026-09-24, `stationinjection/benchmark_vs_stationload.py`, range 2022-01-01..2026-07-25.

**What was compared.** NEW `AW.DBO.ERCOTSTATIONINJECTION` summed over `KVLEVEL` per (date, hour,
station) vs OLD `AW.DBO.ERCOTSTATIONLOAD` `-WITHDRAWMW` (station-level net; `GENMW` is a
different source, not compared). Join key: `TO_DATE(ts)=DATE`, `HOUR(ts)=HOUR`, station.

**Headline** (over rows present in both tables):

| Year | Rows (both) | within 0.01 MW | within 1 MW | > 10 MW | max \|diff\| |
|---|---|---|---|---|---|
| 2022 | 44,132,833 | 98.840% | 99.819% | 0.132% | 890.7 |
| 2023 | 44,691,254 | 98.596% | 99.619% | 0.271% | 2449.7 |
| 2024 | 46,108,606 | 98.679% | 99.761% | 0.166% | 2688.6 |
| 2025 | 47,797,093 | 98.772% | 99.815% | 0.140% | 1315.9 |
| 2026 | 27,423,499 | 98.901% | 99.841% | 0.129% | 924.5 |
2023/2024 lowest within-1MW, highest >10MW — classes 1 and 3 below.

**Disagreement classes** (diagnosed against raw SE branch table):

1. *NEW TABLE DEFECT, fixed in proc commit (fallback).* 2023-03-28 23:00→2023-04-04 23:00 (168h).
   In-force CIM model CIMFILEID 393 (2023Mar.L5) has no rows in `ERCOTTRANSFORMERWINDING`, so no
   transformer mirror fired: STP read −9 MW with no 25kV row, CPSES −43, and GSU-on-low-side
   stations doubled (HHGT 729@34.5 + 727@138 = 1457 vs old 729; CALAVERS ≈2.05× old). 376
   stations off >10 MW at 2023-03-30 12:57 — the March/April 2023 spike in `bad_by_month.csv`.
   Proc now mirrors from the latest earlier winding-bearing model; week must be re-run.
2. *OLD TABLE DROPS DEVICES (new is right).* BIGLAKE, N_SHARPE, YELWJCKT, THOMASTN, PUTN,
   HAMILTON, NLARSW, FIREROCK, SOLSTICE, LARDVFT disagree 48–99% of hours. Raw flows match NEW
   exactly (BIGLAKE 2026-07-01 12:57: new 69kV −0.51 / 138kV −20.72; old −0.52 = 69kV only, the
   three 138kV lines + SOURCE xfmr missing from old). N_SHARPE nets ~0 in raw flows (pure
   switching station); old −71.19 = the dropped 138_PS3_B phase-shifter.
3. *OLD TABLE COLLAPSED ON 2024-01-01.* All 24h, 1,896 stations near-zero in old (STP 1.6 MW vs
   new 2,688; old's own GENMW shows 2,676). SE snapshots complete (10,068 rows/hour). Old-table
   defect; explains the January 2024 bump.
4. *CONVENTION DIFFERENCE, not an error.* 214 hours (`duplicate_snapshot_hours.csv`) carry two SE
   snapshots (170 are model-load Tue 23:00 + 23:52/53 + 23:57/58). OLD averaged them (STP
   2022-01-01 13:00: 2671.25 & 2673.55 → old 2672.4); NEW keeps each snapshot as its own row.
   Consumers should take the latest snapshot per hour (`SP_RUN_FAST_SCAN_TEST_V2` does).
5. *ONE-SIDED STATIONS, not comparable.* OLD_ONLY (~200k/yr) = `WITHDRAWMW` NULL, `GENMW`-only
   cogens (OXY_CC, INGLCOSW, NCARBIDE, BTE, CAL …). NEW_ONLY (2024–2025) = hours/stations absent
   from old; e.g. ENTERPR has 96 hours in new with no old row for any station.

**Files.** `summary_by_year.csv` per-year diff buckets · `bad_by_month.csv` monthly bad-row rate ·
`worst_stations.csv` stations by bad-hour fraction · `worst_examples.csv` worst rows ·
`new_only_stations.csv`/`old_only_stations.csv` one-sided stations · `dup_hours.csv`/`duplicate_snapshot_hours.csv` multi-snapshot hours.
