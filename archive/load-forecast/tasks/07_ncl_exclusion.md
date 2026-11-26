# tasks/07_ncl_exclusion.md — CONCRETE PLAN (sdalvi rulings 2026-08-15)

Objective: CONFORMING (organic) load growth per zone. Identify confirmed
non-conforming/large-load stations, subtract their hourly MW from zonal load,
refit the size index on the organic series. Forward additions are OUT OF SCOPE
(sdalvi: "we focus only on conforming load growth").

Rulings: subtraction source = HYBRID (ercotStationLoad primary, LoadEstimation
cross-check, flag >20% monthly disagreements); NCL set = CONFIRMED ONLY
(datacenter sheet ∪ ercotManuallyUpdatedLoad roster; PUN-flagged unknowns
excluded pending audit); zones = NCENT/COAST/SCENT only.

Pipeline:
1. NCL station set (src/ncl_stations.py): roster NmmsStationCodes (already in
   namespace) ∪ sheet stations (SswgBusNumber → ercotDataDictionary →
   NmmsStationCode; fall back to dam_bus_name exact match, report unmapped).
   Zone-attribute via SswgBusNumber → PlanningBusCounty → county crosswalk;
   keep 3 in-scope zones. Output: data/derived/ncl_stations.csv with
   provenance column (sheet/roster/both) for sdalvi review.
2. Station load pull (src/pull_station_load.py): ercotStationLoad from
   SNOWFLAKE (AI_READ_ONLY; identical copy to SQL Server, better for scans) —
   WithdrawMW hourly 2015→present for the NCL set, cache parquet per station.
3. Organic series (src/organic_load.py): zone NCL MW sum per hour (hour-ending
   aligned) → organic_load_hourly.parquet = load_hourly − zone NCL. Negative
   guard: organic must stay > 50% of total in every hour (else flag, don't
   clip silently). Cross-check leg: monthly station sums vs LoadEstimation
   pun_total (2021→2026-02 overlap), report >20% disagreements.
4. Organic size index: refit year effects on organic daily energy → organic
   vs total growth table per zone (THE deliverable).
5. Prove it: rolling backtest on the organic series — hypothesis: NCENT
   organic growth error collapses toward COAST/SCENT levels.

Known traps: 4 station-name namespaces (SE station / NmmsStationCode /
dam_bus_name / LDF SUBSTATION) — only the documented joins above are trusted;
ercotStationLoad ends ~2026-06 (organic series ends there); roster is heavy on
generator station-service loads (negative WithdrawMW — keep sign-aware, do NOT
abs()); LDF is Snowflake-only, quarterly study-weeks, no conforming flag.
