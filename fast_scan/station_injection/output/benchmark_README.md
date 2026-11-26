# Benchmark: ERCOTSTATIONINJECTION vs ERCOTSTATIONLOAD
Run 2026-09-24, `fast_scan/station_injection/benchmark_vs_stationload.py`, range 2022-01-01..2026-07-25.

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

CONVENTION DIFFERENCE, not an error. SE snapshots are stamped :57/:58 and describe the top of the NEXT hour, so hours must be bucketed by nearest hour (DATE_TRUNC('HOUR', DATEADD('MINUTE', 30, ts))), not by floor. Bucketed that way there are 179 multi-snapshot hours (se_multiple_snapshot_hours.sql), all production-model rollout nights (153 Tuesdays): a small first snapshot of at most 33 branch rows, 98% of them devices whose active window ends that day (lines leaving the model), then the full snapshot on the new model. OLD averaged both into the hour; NEW keeps each snapshot as its own TIMESTAMP row. Consumers should take the latest snapshot per hour bucket.

5. *ONE-SIDED STATIONS, not comparable.* OLD_ONLY (~200k/yr) = `WITHDRAWMW` NULL, `GENMW`-only
   cogens (OXY_CC, INGLCOSW, NCARBIDE, BTE, CAL …). NEW_ONLY (2024–2025) = hours/stations absent
   from old; e.g. ENTERPR has 96 hours in new with no old row for any station.

**Files.** `summary_by_year.csv` per-year diff buckets · `bad_by_month.csv` monthly bad-row rate ·
`worst_stations.csv` stations by bad-hour fraction · `worst_examples.csv` worst rows ·
`new_only_stations.csv`/`old_only_stations.csv` one-sided stations · `dup_hours.csv`/`duplicate_snapshot_hours.csv` multi-snapshot hours.
