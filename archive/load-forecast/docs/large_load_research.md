# Large-load research inputs (sdalvi, 2026-08-15) — Task 07 foundation

Goal: identify non-conforming/large loads (datacenters etc.), subtract from
zonal load → clean organic growth. Directly targets the NCENT structural
growth under-forecast.

## Chain sdalvi described

1. Bus name → `ercotDataDictionary` rows with **DAM MWs ≠ 0** → map to
   **station name**.
2. Station name → estimated station load:
   `SELECT esl.* FROM AW.dbo.ercotStationLoad AS esl`
   — "in snowflake" per sdalvi (check both engines); imperfect, built from
   **branch flow data**.
3. **DAM LDF** (load distribution factors), published by ERCOT only every few
   months, ~2–3 months lag → identifies large loads for removal.
4. **Latest rebuild** of load profiles: `AWDev.dbo.ercotLoadEstimation_term_bal`
   + `_station_bal` (state-estimator based; schema family
   `AW(Dev).DBO.ERCOTLOADEST*` — learn it). `run_id='1'`. `pun_score=0` = clean;
   `unresolved_xfmr_count` splits clean vs internal-missing. Bad/failed
   intervals: `ABS(SUM(pun_total_est_load_mw)) <= 50` system-wide → exclude
   (would be nice: a ref table of bad intervals going forward).
   **Use `clean_plus_internal_mw`.**

## sdalvi's reference queries (verbatim)

### System-level per timestamp

```sql
SELECT
    t.se_timestamp,
    SUM(CASE WHEN COALESCE(sb.pun_score, 0) = 0
             THEN t.pun_total_est_load_mw ELSE 0 END)  AS clean_plus_internal_mw,
    SUM(CASE WHEN COALESCE(sb.pun_score, 0) = 0 AND COALESCE(sb.unresolved_xfmr_count, 0) = 0
             THEN t.pun_total_est_load_mw ELSE 0 END)  AS clean_station_est_load_mw,
    SUM(CASE WHEN COALESCE(sb.pun_score, 0) = 0 AND COALESCE(sb.unresolved_xfmr_count, 0) > 0
             THEN t.pun_total_est_load_mw ELSE 0 END)  AS internal_missing_station_est_load_mw
FROM AWDev.dbo.ercotLoadEstimation_term_bal t
LEFT JOIN AWDev.dbo.ercotLoadEstimation_station_bal sb
    ON sb.station = t.station
   AND sb.se_timestamp = t.se_timestamp
   AND sb.run_id = '1'
WHERE t.run_id = '1'
  AND t.se_timestamp >= CAST('2026-01-01 00:00:00' AS DATETIME2(0))
  AND t.se_timestamp <= CAST('2026-03-23 00:00:00' AS DATETIME2(0))
GROUP BY t.se_timestamp
ORDER BY t.se_timestamp
```

### Station/kV level (with failed-interval exclusion)

```sql
SELECT
    t.se_timestamp, t.station, t.kv,
    CASE WHEN COALESCE(sb.pun_score, 0) = 0
         THEN t.pun_total_est_load_mw ELSE 0 END       AS clean_plus_internal_mw,
    CASE WHEN COALESCE(sb.pun_score, 0) = 0 AND COALESCE(sb.unresolved_xfmr_count, 0) = 0
         THEN t.pun_total_est_load_mw ELSE 0 END       AS clean_station_est_load_mw,
    CASE WHEN COALESCE(sb.pun_score, 0) = 0 AND COALESCE(sb.unresolved_xfmr_count, 0) > 0
         THEN t.pun_total_est_load_mw ELSE 0 END       AS internal_missing_station_est_load_mw,
    t.pun_total_est_load_mw
FROM AWDev.dbo.ercotLoadEstimation_term_bal t
LEFT JOIN AWDev.dbo.ercotLoadEstimation_station_bal sb
    ON sb.station = t.station AND sb.se_timestamp = t.se_timestamp AND sb.run_id = '1'
WHERE t.run_id = '1'
  AND t.se_timestamp >= CAST('2026-01-01 00:00:00' AS DATETIME2(0))
  AND t.se_timestamp <= CAST('2026-03-23 00:00:00' AS DATETIME2(0))
  AND t.se_timestamp NOT IN (
      SELECT t2.se_timestamp
      FROM AWDev.dbo.ercotLoadEstimation_term_bal t2
      WHERE t2.run_id = '1'
        AND t2.se_timestamp >= CAST('2026-01-01 00:00:00' AS DATETIME2(0))
        AND t2.se_timestamp <= CAST('2026-03-23 00:00:00' AS DATETIME2(0))
      GROUP BY t2.se_timestamp
      HAVING ABS(SUM(t2.pun_total_est_load_mw)) <= 50.0
  )
ORDER BY t.se_timestamp, t.station, t.kv
```

## Zone attribution path (from gis-research prior art)

Station/bus → county: `BusID(SSWG) → ercotDataDictionary.SswgBusNumber →
PlanningBusCounty` (latest snapshot); county → weather zone via the crosswalk
already in this repo. Gets station-level NCL MW into zonal subtraction.

## PUN redactions (sdalvi, 2026-08-15)

Some loads are REDACTED because they are PUNs (private use networks — load
behind a private network, mostly in the WEST). Manual fill-in table:
`ercotManuallyUpdatedLoad` in the SQL DB. This is why `pun_score` exists in
the estimation tables — PUN-contaminated stations are the ones the
clean_plus_internal_mw filter (pun_score=0) drops.

## sdalvi answers (2026-08-15, round 2)

- **DAM MWs**: live in sdalvi's manually-built datacenter tracking sheet —
  saved verbatim at `data/raw/large_loads/datacenter_tracking_raw.txt`
  (per-bus, per-phase Expected/DAM MW with online dates through 2030; also the
  FORWARD additions schedule for the size index).
- **DAM LDF internal table**: `AW.DBO.ERCOTLOADDISTRIBUTIONFACTORS` (recon's
  %LDF% pattern missed it — name spells out LOADDISTRIBUTIONFACTORS).
- **ercotManuallyUpdatedLoad purpose**: identify which stations are
  non-conforming → look up load AT those stations (ercotStationLoad) →
  subtract from zonal load for years where station MW exists.
- **PUN flagging**: sdalvi suspects the pun_score exclusion (9.5–12% of system
  load) is OVER-FLAGGING — do not trust clean_plus_internal_mw until the
  biggest excluded stations are named and gut-checked.

## Known caveats (sdalvi)

- ercotStationLoad: branch-flow derived, imperfect.
- LDF: 2–3 month lag vs actual load in report.
- LoadEstimation tables: some bad intervals beyond the <=50 filter.
- ERCOT DOES mark conforming vs non-conforming loads, but the classification
  is NOT clean — usable as a signal, not as truth. Find where the flag lives
  (data dict? LDF files?) and characterize its dirtiness before trusting it.
