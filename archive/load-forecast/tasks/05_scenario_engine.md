# tasks/05_scenario_engine.md
Objective: scenario_hourly for arbitrary (weather_year, system_year).
Method: build feature frame from weather_year's zone_weather_hourly with
weather_year's own calendar; predict per-unit; multiply by
size_idx[system_year] × base-year GWh scale.
Deliver: CLI/function run_scenario(zone, wx_year, sys_year); pre-run
wx ∈ {2019, 2021(ex-Uri), 2022, 2023} × sys ∈ {2026, 2028}.
Accept: identity check — run_scenario(z, y, y) reproduces year-y actuals
within size-index normalization error.
