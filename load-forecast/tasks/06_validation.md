# tasks/06_validation.md
Objective: honest 2025–2026 scorecard.
Method: models trained ≤2024 only. Replay actual 2025–2026 weather at
extrapolated size_idx. Score per zone: monthly energy MAPE, annual growth
error (pp/yr), peak-day error (diagnostic). Second pass at climate-normal
weather to decompose residual into weather-miss vs trend-miss.
Accept: targets in CLAUDE.md; write results to validation_report.md with
per-zone tables and the decomposition.
