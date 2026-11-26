# tasks/02_data_pull.md
Objective: load_hourly, weather_hourly, zone_weather_hourly.
Load: ERCOT Native Load archives 2015–present; parse to hour-ending CPT;
handle DST duplicate/missing hours explicitly; set event_flag per
CLAUDE.md rules.
Weather: ISD hourly for crosswalk stations; QC = drop physically
impossible values, cap interpolation at 3 consecutive hours (qc_flag);
convert to °F.
Zone series: population-weighted temp/dewpoint per hour; then avg24 and
ewm3d features computed on the weighted series.
Accept: no gaps > 3h post-QC; load row count matches hours in range per
zone; spot-check DFW-only vs weighted NCENT correlation (expect ~0.99).
