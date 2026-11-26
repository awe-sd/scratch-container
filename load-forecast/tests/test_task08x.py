"""Task 08-X synthetic tests: monthly-index consistency (spec §3), jump layer,
empirical CRPS vs the Gaussian closed form."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import config as cfg  # noqa: E402
import prob_size as ps  # noqa: E402
import size_index_monthly as sim_m  # noqa: E402


def synthetic_daily(start="2017-01-01", end="2020-12-31", seed=7) -> pd.DataFrame:
    """Additive world in the fitted model family: level-per-year + PWL temp +
    weekday effect. No events."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start, end, freq="D")
    doy = dates.dayofyear.to_numpy()
    temp = 70 + 25 * np.sin(2 * np.pi * (doy - 105) / 365.25) + rng.normal(0, 3, len(dates))
    year_level = (dates.year - dates.year.min()).to_numpy() * 15_000.0
    weekday_dip = np.where(dates.dayofweek >= 5, -8_000.0, 0.0)
    energy = (
        500_000.0 + year_level + weekday_dip
        + 4_000.0 * np.maximum(temp - 75, 0) + 1_500.0 * np.maximum(65 - temp, 0)
        + rng.normal(0, 1_000, len(dates))
    )
    return pd.DataFrame({
        "date": dates, "energy_mwh": energy, "temp_mean_f": temp,
        "event_flag": pd.Series([None] * len(dates), dtype="object"),
    })


# ---------------------------------------------------------------------------
# (a) monthly-index consistency vs annual (spec §3)
# ---------------------------------------------------------------------------


def test_monthly_index_consistency_and_base_anchor():
    daily = synthetic_daily()
    mi = sim_m.build_monthly_index(daily, "TESTZ", wall_year=2020, base_year=2019)
    m = mi.monthly
    assert len(m) == 48  # 4 years x 12 months

    base_vals = m.loc[pd.to_datetime(m["ym"]).dt.year == 2019, "size_idx_m"]
    assert len(base_vals) == 12
    np.testing.assert_allclose(base_vals, 1.0, atol=1e-9)  # base months exactly 1.0

    # 12-month mean vs the same-wall annual size_idx within 0.5% (raises if not)
    rep = sim_m.consistency_report(daily, "TESTZ", 2020, m, base_year=2019)
    assert (rep["rel_diff"].abs() <= sim_m.CONSISTENCY_TOL).all()
    # growth direction sane: 2020 level above 2018
    y_means = m.assign(y=pd.to_datetime(m["ym"]).dt.year).groupby("y")["size_idx_m"].mean()
    assert y_means[2020] > y_means[2018]


# ---------------------------------------------------------------------------
# (b) jump layer on a synthetic 2-site sheet, fixed seed
# ---------------------------------------------------------------------------


def test_jump_layer_synthetic_sites():
    units = pd.DataFrame({
        "weather_zone": ["NCENT", "NCENT", "NCENT"],
        "site_name": ["A", "B", "C_pre_wall"],
        "online": pd.to_datetime(["2025-03-15", "2025-06-01", "2024-06-01"]),
        "mw": [100.0, 50.0, 999.0],
        "p_mat": [1.0, 0.0, 1.0],
        "mw_source": ["expected_mw"] * 3,
    })
    base = {mth: 1000.0 for mth in range(1, 13)}
    paths, diag = ps.simulate_jump_paths(units, "NCENT", 2024, base, n_paths=500, seed=123)

    assert paths.shape == (500, 24)
    assert diag["n_units_after_wall"] == 2          # C excluded (online <= wall)
    assert np.all(paths[:, 0] == 0) and np.all(paths[:, 1] == 0)  # Jan/Feb 2025: pre-online
    # ramp FRACTION is nondecreasing (index units wiggle with days-in-month,
    # so divide the hours profile back out before checking monotonicity)
    months = pd.period_range("2025-01", periods=24, freq="M")
    hours = np.array([p.days_in_month * 24.0 for p in months])
    frac_like = paths / hours[None, :]
    assert np.all(np.diff(frac_like, axis=1) >= -1e-15)

    # B has p_mat=0 -> only A contributes; by month 24 (k=22) every ramp (<=18mo)
    # is complete: 100 MW * 744 h / 1000 / 1000 GWh = 0.0744 index units
    dec26 = 100.0 * (31 * 24) / 1000.0 / 1000.0
    np.testing.assert_allclose(paths[:, 23], dec26, rtol=1e-12)

    # March 2025 (k=1): frac = 0.5/ramp_len in [0.5/18, 0.5/6] of the March value
    mar = 100.0 * (31 * 24) / 1000.0 / 1000.0
    assert np.all(paths[:, 2] >= mar * 0.5 / 18.0 - 1e-12)
    assert np.all(paths[:, 2] <= mar * 0.5 / 6.0 + 1e-12)

    # determinism
    paths2, _ = ps.simulate_jump_paths(units, "NCENT", 2024, base, n_paths=500, seed=123)
    np.testing.assert_array_equal(paths, paths2)


# ---------------------------------------------------------------------------
# (c) empirical CRPS vs Gaussian closed form
# ---------------------------------------------------------------------------


def test_crps_empirical_matches_gaussian_closed_form():
    rng = np.random.default_rng(0)
    mu, sigma = 1.0, 2.0
    x = rng.normal(mu, sigma, 400_000)
    for y in (-2.0, 1.0, 4.0):
        emp = ps.crps_empirical(y, x)
        ana = ps.crps_gaussian(y, mu, sigma)
        assert abs(emp - ana) < 0.01, (y, emp, ana)


def test_crps_degenerate_ensemble_is_absolute_error():
    x = np.full(1000, 3.0)
    assert ps.crps_empirical(5.0, x) == pytest.approx(2.0)
    assert ps.crps_empirical(3.0, x) == pytest.approx(0.0)


def test_paths_to_growth_flat_paths_zero_growth():
    paths = np.full((10, 24), 1.23)
    g1, g2 = ps.paths_to_growth(paths, 1.23)
    np.testing.assert_allclose(g1, 0.0, atol=1e-12)
    np.testing.assert_allclose(g2, 0.0, atol=1e-12)
