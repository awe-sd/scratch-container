"""Task 08-X AMENDMENT 2 synthetic tests: ETS damped-trend fit+simulate shape
and determinism, hand-rolled Student-t(5) LLT simulator (shape, determinism,
variance sanity, mean-trajectory anchor alignment), and the conformal LOFO
diagnostic on a hand-built toy with a known answer."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import prob_size as ps  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import experiment_prob_size2 as eps2  # noqa: E402


def synthetic_monthly(zone="TESTZ", n=48, seed=1) -> pd.DataFrame:
    """A clean trending-with-noise monthly index -- same recipe verified
    (manually, before writing this test) to give a non-boundary LLT fit
    (slope_var_boundary=False) and an ETS phi fit that pins at the 0.98 upper
    bound (recorded as phi_boundary=True, not an error -- statsmodels' default
    damping_trend bounds are [0.8, 0.98])."""
    rng = np.random.default_rng(seed)
    yms = pd.period_range("2019-01", periods=n, freq="M")
    y = 1.0 + 0.008 * np.arange(n) + rng.normal(0, 0.008, n)
    return pd.DataFrame({
        "zone": zone, "ym": [p.start_time for p in yms],
        "size_idx_m": y, "n_days_used": 30,
    })


# ---------------------------------------------------------------------------
# (1) ETS damped-trend: fit + simulate shape/determinism
# ---------------------------------------------------------------------------


def test_ets_damped_fit_and_simulate_shape_determinism():
    monthly = synthetic_monthly()
    fit = ps.fit_ets_damped(monthly, "TESTZ", 2022)
    assert fit.zone == "TESTZ" and fit.wall_year == 2022
    for v in (fit.alpha, fit.beta, fit.phi, fit.sigma2):
        assert np.isfinite(v)
    assert ps.ETS_PHI_BOUNDS[0] - 1e-6 <= fit.phi <= ps.ETS_PHI_BOUNDS[1] + 1e-6
    # this particular synthetic series pins phi at the upper bound (recorded,
    # accepted, same convention as fit_llt's slope-variance boundary flag)
    assert fit.phi_boundary is True
    assert fit.sigma2 > 0

    paths = ps.simulate_ets_paths(fit, n_paths=200, n_months=24, seed=42)
    assert paths.shape == (200, 24)
    assert np.all(np.isfinite(paths))

    paths_again = ps.simulate_ets_paths(fit, n_paths=200, n_months=24, seed=42)
    np.testing.assert_array_equal(paths, paths_again)  # determinism, same seed

    paths_other_seed = ps.simulate_ets_paths(fit, n_paths=200, n_months=24, seed=43)
    assert not np.array_equal(paths, paths_other_seed)  # different seed -> different draw


# ---------------------------------------------------------------------------
# (2) Hand-rolled Student-t(5) LLT simulator: shape, determinism, variance
#     sanity, mean-trajectory anchor alignment
# ---------------------------------------------------------------------------


def test_llt_t5_paths_shape_and_determinism():
    monthly = synthetic_monthly()
    llt = ps.fit_llt(monthly, "TESTZ", 2022)

    paths = ps.simulate_llt_t5_paths(llt, n_paths=300, n_months=24, seed=42)
    assert paths.shape == (300, 24)
    assert np.all(np.isfinite(paths))

    paths_again = ps.simulate_llt_t5_paths(llt, n_paths=300, n_months=24, seed=42)
    np.testing.assert_array_equal(paths, paths_again)

    paths_other_seed = ps.simulate_llt_t5_paths(llt, n_paths=300, n_months=24, seed=43)
    assert not np.array_equal(paths, paths_other_seed)


def test_llt_t5_shock_variance_matches_gaussian_target():
    """The Student-t(5) shocks are scaled by sqrt(sigma2 * 3/5) specifically
    so their variance equals the fitted Gaussian MLE variance (a unit-scale
    t5 draw has variance df/(df-2) = 5/3; T5_VAR_SCALE=3/5 undoes that).
    Draw the shock distribution directly (bypassing the recursive state) and
    check sample variance against the target within 15%."""
    monthly = synthetic_monthly()
    llt = ps.fit_llt(monthly, "TESTZ", 2022)
    rng = np.random.default_rng(999)
    n_draw = 300_000

    for key in ("sigma2.level", "sigma2.trend"):
        sigma2 = float(llt.params[key])
        if sigma2 <= 0:
            continue  # boundary fit -- shock is deterministically 0, nothing to check
        scale = np.sqrt(sigma2 * ps.T5_VAR_SCALE)
        draw = rng.standard_t(ps.T5_DF, size=n_draw) * scale
        target_std = np.sqrt(sigma2)
        rel_err = abs(draw.std() - target_std) / target_std
        assert rel_err < 0.15, f"{key}: t5 shock std {draw.std():.3e} vs Gaussian target {target_std:.3e} ({rel_err:.1%} off)"


def test_llt_t5_mean_trajectory_matches_analytical_anchor():
    """Anchor-alignment check: with t5 shocks (mean 0, same as Gaussian) and
    an MVN-resampled initial state (unbiased -- mean of the draw equals the
    filtered_state mean exactly), E[level_t] = level0 + t*slope0 for both
    simulate_llt_t5_paths and (independently) simulate_llt_paths on the SAME
    fit. This catches an off-by-one against `simulate(anchor='end')` that
    would silently shift the whole growth distribution while still "looking"
    plausible. Compares MEANS only, at a generous Monte-Carlo tolerance --
    t5's bands are legitimately WIDER at short horizons than simulate_llt_paths
    (initial-state resampling adds variance simulate_llt_paths doesn't have);
    that's an accepted, deliberate difference, not a bug, so variance is not
    compared here."""
    monthly = synthetic_monthly()
    llt = ps.fit_llt(monthly, "TESTZ", 2022)
    level0, slope0 = np.asarray(llt.results.filtered_state[:, -1], dtype=float)
    analytical = level0 + np.arange(1, 25) * slope0

    n_mc = 30_000
    t5_paths = ps.simulate_llt_t5_paths(llt, n_paths=n_mc, n_months=24, seed=42)
    mean_traj = t5_paths.mean(axis=0)
    se_traj = t5_paths.std(axis=0) / np.sqrt(n_mc)
    tol = 6 * se_traj + 1e-9  # 6-sigma MC band: loose enough not to flake, tight
                              # enough that a real anchor/off-by-one bug (a
                              # systematic multi-sigma bias) would fail it
    assert np.all(np.abs(mean_traj - analytical) < tol), (
        f"t5 mean trajectory diverges from the analytical level0+t*slope0 anchor "
        f"by more than a 6-sigma MC band at month(s) "
        f"{np.where(np.abs(mean_traj - analytical) >= tol)[0] + 1}"
    )

    # simulate_llt_paths (statsmodels, point-anchor, Gaussian) must agree with
    # the SAME analytical target -- confirms the reference simulator's anchor
    # is what we think it is, independent of the t5 implementation
    llt_paths = ps.simulate_llt_paths(llt, n_paths=n_mc, n_months=24, seed=42)
    mean_traj_llt = llt_paths.mean(axis=0)
    se_traj_llt = llt_paths.std(axis=0) / np.sqrt(n_mc)
    tol_llt = 6 * se_traj_llt + 1e-9
    assert np.all(np.abs(mean_traj_llt - analytical) < tol_llt)


# ---------------------------------------------------------------------------
# (3) Conformal LOFO diagnostic: hand-built 12-fold toy, known answer
# ---------------------------------------------------------------------------


def test_conformal_lofo_known_answer():
    """11 folds sit exactly at p50 (score 0); 1 fold is a wild miss (score 2.0).
    Leaving out any of the 11 well-behaved folds, the other 10 zeros + the one
    2.0 outlier still put the 80th percentile at 0 (n=11: position 0.8*10=8.0,
    the sorted array's index 8 is still one of the ten zeros). Leaving out the
    outlier fold itself, the remaining 11 are all zeros -> k=0 too. So k_i=0
    for all 12 folds: the 11 good folds calibrate-cover (0<=0), the outlier
    does not (20 > 0); every calibrated width is 0."""
    truth = np.array([10.0] * 11 + [30.0])
    p10 = np.zeros(12)
    p50 = np.full(12, 10.0)
    p90 = np.full(12, 20.0)

    cal = eps2.conformal_lofo(truth, p10, p50, p90, level=0.80)
    assert len(cal) == 12
    np.testing.assert_allclose(cal["s"].to_numpy(), [0.0] * 11 + [2.0])
    np.testing.assert_allclose(cal["k"].to_numpy(), 0.0, atol=1e-12)
    assert list(cal["calibrated_cover"]) == [True] * 11 + [False]
    assert int(cal["calibrated_cover"].sum()) == 11
    np.testing.assert_allclose(cal["calibrated_width"].to_numpy(), 0.0, atol=1e-12)
