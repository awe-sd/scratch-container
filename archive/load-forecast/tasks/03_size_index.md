# tasks/03_size_index.md
Objective: size_index table incl. 2027–2028 extrapolation.
Method: per zone, daily energy OLS on piecewise-linear daily-mean temp
(knots ~55/65/75°F), weekday/holiday dummies, YEAR FIXED EFFECTS (one level
dummy per year — replaces the original linear date trend per sdalvi ruling
2026-08-14: a global slope can't show recent acceleration); apply event
weights. Climate-normal daily temp = 10-yr calendar-day average ending at
the train wall. Predict a canonical FULL calendar (every day of every fitted
year, so data holes/leap days can't bias the level) at normals → annual
normalized_gwh (scaled to a 365.25-day year) → size_idx. Extrapolate
linearly on last 6 fitted years; mark source='extrapolated'.
Accept: fitted R² ≥ 0.85 per zone on daily energy; size_idx
monotone-plausible (flag any y/y move > 6% for review).
