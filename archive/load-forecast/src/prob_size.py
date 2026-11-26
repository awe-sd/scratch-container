"""Task 08-X component B: Model P = local linear trend + large-load jump layer.

Trend: statsmodels UnobservedComponents(level='local linear trend') MLE on the
monthly canonical size index (size_index_monthly.py), simulated forward 24
months x N paths from the filtered state at the wall (statsmodels `simulate`
with anchor='end' -- draws state + observation innovations; initial-state
uncertainty at the anchor is NOT resampled, an accepted MVE simplification,
recorded in the training log). If MLE puts the slope variance on the zero
boundary, that is recorded and accepted, never hand-tuned.

Jump layer: sdalvi tracking-sheet rows (data/derived/large_loads.csv -- the
per-bus/phase rows, richer than the sites rollup: they carry expected_mw,
per-phase online_date, and the sheet's own confidence tier 1/2/3). Zone via
the SAME bus->station->county->zone chain as Task 07 (ncl_stations.map_sheet_rows
+ zone_map, cache-first -- no DB hit when the dictionary cache exists).
Per unit, per path: Bernoulli(p_mat) materialization, linear ramp from the
online month over ramp_len ~ U(6,18) months, monthly GWh = MW x hours-in-month
/ 1000 x ramp fraction, converted to index units by dividing by THAT CALENDAR
MONTH's base-year normals-predicted energy (MonthlyIndex.base_month_gwh).
[Dimensional note recorded in the pre-registration entry: the spec's "divide
by annual energy" phrasing is off by ~12x for a monthly ratio index; the
per-month divisor is the dimensionally correct reading and reduces to the
annual divisor when annualizing.]

p_mat mapping (sheet confidence tier -> spec bucket knobs):
  1 -> 0.85 (energized/under_construction), 2 -> 0.5 (signed/committed),
  3 -> 0.25 (announced/other), missing/unknown -> 0.5.

MW per unit: expected_mw if > 0, else dam_mw if > 0, else the row is dropped
and logged (max_mw is nameplate, never used to size a jump).

Only units with online date STRICTLY AFTER the wall enter (double-count
guard); units online before the wall are inside the fitted trend. Residual
overlap from partially-ramped sites = accepted, logged, upward band bias.

Amendment-2 additions (2026-08-16, task08x2, appended -- fit_llt and
simulate_llt_paths above are unchanged, run-1 tests still pass): two more
trend variants alongside the free LLT, per training_log's variant grid --
`fit_ets_damped` + `simulate_ets_paths` (statsmodels ETSModel damped-trend
class, MLE) and `simulate_llt_t5_paths` (hand-rolled Student-t(5) shocks on
llt_free's own MLE variances, with MVN-resampled initial state).
CORRECTION (Opus gate 2, 2026-08-16): statsmodels 0.14.6 MLEResults.simulate
ALREADY resamples the initial state from the predicted-state moments at the
anchor, so run-1's "initial-state uncertainty not resampled" caveat (docstring
above, pre-registration) was factually wrong, and t5's init-state draw is NOT
a differentiator -- the only real t5 delta vs llt_free is the t(5) shocks.
The hand-roll (filtered draw + one transition) is distributionally equivalent
to statsmodels' predicted-state draw (verified, no off-by-one).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg  # noqa: E402
import ncl_stations as ns  # noqa: E402

N_PATHS = 10_000
H_MONTHS = 24
SEED = 42
P_MAT_BY_CONFIDENCE = {1: 0.85, 2: 0.50, 3: 0.25}
P_MAT_DEFAULT = 0.50
RAMP_MONTHS_RANGE = (6.0, 18.0)
SLOPE_VAR_BOUNDARY = 1e-12  # sigma2.trend below this = boundary fit, recorded

# amendment-2 (task08x2)
ETS_PHI_BOUNDS = (0.8, 0.98)     # statsmodels ETSModel default damping_trend bounds
ETS_PHI_BOUNDARY_TOL = 1e-3      # phi within this of either bound = pinned, recorded
T5_DF = 5                        # Student-t degrees of freedom for the t5 trend variant
T5_VAR_SCALE = (T5_DF - 2) / T5_DF  # 3/5: unit-scale t5 draw has variance df/(df-2); this
                                    # factor brings it back to variance 1 so sqrt(sigma2 *
                                    # T5_VAR_SCALE) is the scale whose t5 draw has variance sigma2


# ---------------------------------------------------------------------------
# LLT trend
# ---------------------------------------------------------------------------


@dataclass
class LLTFit:
    zone: str
    wall_year: int
    params: dict[str, float]
    slope_var_boundary: bool
    n_obs: int
    results: object = field(repr=False)


def fit_llt(monthly: pd.DataFrame, zone: str, wall_year: int) -> LLTFit:
    """MLE local-linear-trend fit on one wall's monthly index for one zone."""
    from statsmodels.tsa.statespace.structural import UnobservedComponents

    m = monthly.loc[monthly["zone"] == zone].sort_values("ym")
    series = pd.Series(
        m["size_idx_m"].to_numpy(dtype=float),
        index=pd.PeriodIndex(pd.to_datetime(m["ym"]), freq="M"),
    )
    mod = UnobservedComponents(series, level="local linear trend")
    res = mod.fit(disp=0, maxiter=500)
    params = dict(zip(res.param_names, np.asarray(res.params, dtype=float)))
    slope_var = params.get("sigma2.trend", np.nan)
    return LLTFit(
        zone=zone, wall_year=wall_year, params=params,
        slope_var_boundary=bool(slope_var < SLOPE_VAR_BOUNDARY),
        n_obs=len(series), results=res,
    )


def simulate_llt_paths(fit: LLTFit, n_paths: int = N_PATHS, n_months: int = H_MONTHS,
                       seed: int = SEED) -> np.ndarray:
    """(n_paths, n_months) simulated monthly index levels past the wall."""
    rng = np.random.default_rng(seed)
    try:
        sim = fit.results.simulate(
            nsimulations=n_months, repetitions=n_paths, anchor="end", random_state=rng
        )
    except TypeError:  # older statsmodels without random_state on simulate
        np.random.seed(seed)
        sim = fit.results.simulate(nsimulations=n_months, repetitions=n_paths, anchor="end")
    arr = np.asarray(sim, dtype=float)
    if arr.shape == (n_months, n_paths):
        arr = arr.T
    if arr.shape != (n_paths, n_months):
        raise ValueError(f"unexpected simulate() shape {arr.shape}")
    return arr


# ---------------------------------------------------------------------------
# Amendment-2 trend variants: ETS damped-trend, hand-rolled Student-t(5) LLT
# ---------------------------------------------------------------------------


@dataclass
class ETSFit:
    zone: str
    wall_year: int
    alpha: float           # smoothing_level
    beta: float             # smoothing_trend
    phi: float              # damping_trend
    sigma2: float           # concentrated MLE scale (mean squared residual) -- see ETSResults.scale
    phi_boundary: bool
    n_obs: int
    results: object = field(repr=False)


def fit_ets_damped(monthly: pd.DataFrame, zone: str, wall_year: int) -> ETSFit:
    """MLE damped-trend ETS(A,Ad,N) fit -- statsmodels ETSModel(error='add',
    trend='add', damped_trend=True, seasonal=None) -- on the same monthly
    series prep as fit_llt. phi (damping_trend) is bounded to [0.8, 0.98] by
    statsmodels; pinning at either bound is recorded here and accepted, never
    hand-tuned (same convention as fit_llt's slope-variance boundary flag).
    sigma2 = res.scale, the concentrated-out mean-squared-residual estimate of
    the model's single innovation variance (verified against statsmodels
    source: ETSResults.__init__ sets `scale = np.mean(self._residuals ** 2)`)."""
    from statsmodels.tsa.exponential_smoothing.ets import ETSModel

    m = monthly.loc[monthly["zone"] == zone].sort_values("ym")
    series = pd.Series(
        m["size_idx_m"].to_numpy(dtype=float),
        index=pd.PeriodIndex(pd.to_datetime(m["ym"]), freq="M"),
    )
    mod = ETSModel(series, error="add", trend="add", damped_trend=True, seasonal=None)
    res = mod.fit(disp=False, maxiter=1000)
    phi = float(res.damping_trend)
    lb, ub = ETS_PHI_BOUNDS
    boundary = bool(phi <= lb + ETS_PHI_BOUNDARY_TOL or phi >= ub - ETS_PHI_BOUNDARY_TOL)
    return ETSFit(
        zone=zone, wall_year=wall_year,
        alpha=float(res.smoothing_level), beta=float(res.smoothing_trend), phi=phi,
        sigma2=float(res.scale), phi_boundary=boundary,
        n_obs=len(series), results=res,
    )


def simulate_ets_paths(fit: ETSFit, n_paths: int = N_PATHS, n_months: int = H_MONTHS,
                       seed: int = SEED) -> np.ndarray:
    """(n_paths, n_months) simulated monthly index levels past the wall,
    ETS(A,Ad,N). Shape contract identical to simulate_llt_paths.

    API note (checked against the installed statsmodels 0.14.6):
    ETSResults.simulate's `random_state` must be None, an int, or an
    np.random.RandomState -- passing a np.random.Generator (as
    simulate_llt_paths does for the UnobservedComponents/LLT results object)
    raises ValueError there. simulate() itself is neither missing nor broken,
    so the sanctioned hand-rolled fallback is NOT used; an int seed is passed
    instead, which gives the same determinism guarantee (verified: identical
    seed -> identical paths bit-for-bit, different seed -> different paths)."""
    sim = fit.results.simulate(nsimulations=n_months, repetitions=n_paths, anchor="end", random_state=seed)
    arr = np.asarray(sim, dtype=float)
    if arr.shape == (n_months, n_paths):
        arr = arr.T
    if arr.shape != (n_paths, n_months):
        raise ValueError(f"unexpected ETS simulate() shape {arr.shape}")
    return arr


def simulate_llt_t5_paths(llt_fit: LLTFit, n_paths: int = N_PATHS, n_months: int = H_MONTHS,
                          seed: int = SEED) -> np.ndarray:
    """(n_paths, n_months) hand-rolled local-linear-trend simulator on
    llt_free's own MLE variances (sigma2.level, sigma2.trend, sigma2.irregular
    from fit_llt), with Student-t(df=5) state shocks in place of the model's
    Gaussian ones and an MVN-resampled initial state (closes run-1's
    no-initial-state-uncertainty caveat for this variant only -- statsmodels'
    simulate() starts from the filtered end-state POINT, no resampling).

    State layout: llt_fit.results.filtered_state has shape (2, n_obs), rows
    [level, trend] (verified against res.states.filtered columns); the [:, -1]
    slice is the wall's [level, trend] filtered mean, filtered_state_cov[:, :, -1]
    its 2x2 covariance.

    Transition: level_{t+1} = level_t + slope_t + eta_t, slope_{t+1} = slope_t + zeta_t.
    eta_t, zeta_t ~ Student-t(5), scaled by sqrt(sigma2 * T5_VAR_SCALE) so their
    variance equals the Gaussian MLE variance (a unit-scale t5 draw has variance
    df/(df-2) = 5/3; T5_VAR_SCALE = 3/5 undoes that before applying sigma2).
    Observation: y_t = level_t + N(0, sigma2.irregular). Vectorized over paths;
    the 24-step time loop is sequential (state dependency) but trivially cheap."""
    rng = np.random.default_rng(seed)
    p = llt_fit.params
    sigma2_level = float(p["sigma2.level"])
    sigma2_trend = float(p["sigma2.trend"])
    sigma2_irregular = float(p["sigma2.irregular"])
    scale_level = np.sqrt(sigma2_level * T5_VAR_SCALE)
    scale_trend = np.sqrt(sigma2_trend * T5_VAR_SCALE)
    sigma_irr = np.sqrt(sigma2_irregular)

    res = llt_fit.results
    mean = np.asarray(res.filtered_state[:, -1], dtype=float)          # [level, trend] at the wall
    cov = np.asarray(res.filtered_state_cov[:, :, -1], dtype=float)    # 2x2 at the wall
    cov = (cov + cov.T) / 2.0  # numerical symmetry guard (boundary fits can leave tiny asymmetry)
    init = rng.multivariate_normal(mean, cov, size=n_paths, check_valid="ignore")
    level = init[:, 0].copy()
    slope = init[:, 1].copy()

    out = np.empty((n_paths, n_months), dtype=np.float64)
    for t in range(n_months):
        eta = rng.standard_t(T5_DF, size=n_paths) * scale_level
        zeta = rng.standard_t(T5_DF, size=n_paths) * scale_trend
        level = level + slope + eta
        slope = slope + zeta
        eps = rng.normal(0.0, sigma_irr, size=n_paths)
        out[:, t] = level + eps
    return out


# ---------------------------------------------------------------------------
# Jump layer
# ---------------------------------------------------------------------------


def load_jump_units() -> tuple[pd.DataFrame, dict]:
    """Sheet rows -> jump units (weather_zone, site_name, online, mw, p_mat,
    mw_source) + a diagnostics dict of everything dropped (no silent caps)."""
    sheet = pd.read_csv(ns.LARGE_LOADS_CSV)
    dictionary, snap = ns.pull_dictionary_snapshot()
    mapped, unmapped = ns.map_sheet_rows(sheet, dictionary)
    zmap, _ = ns.zone_map()
    mapped = mapped.copy()
    mapped["weather_zone"] = mapped["county"].map(lambda c: zmap.get(c) if c else None)

    diag: dict = {"dictionary_snapshot": snap, "n_sheet_rows": len(sheet)}
    diag["n_unmapped_rows"] = len(unmapped)
    diag["unmapped_mw_expected"] = float(pd.to_numeric(unmapped["expected_mw"], errors="coerce").clip(lower=0).sum())

    in_scope = mapped.loc[mapped["weather_zone"].isin(cfg.ZONES)].copy()
    diag["n_zone_out_of_scope"] = int(len(mapped) - len(in_scope))

    online = pd.to_datetime(in_scope["online_date"], errors="coerce")
    diag["n_no_online_date"] = int(online.isna().sum())
    in_scope = in_scope.loc[online.notna()].copy()
    in_scope["online"] = online.loc[in_scope.index]

    exp = pd.to_numeric(in_scope["expected_mw"], errors="coerce")
    dam = pd.to_numeric(in_scope["dam_mw"], errors="coerce")
    mw = exp.where(exp > 0, dam.where(dam > 0))
    src = pd.Series(np.where(exp > 0, "expected_mw", np.where(dam > 0, "dam_mw", "none")),
                    index=in_scope.index)
    diag["n_no_mw"] = int((src == "none").sum())
    keep = src != "none"
    in_scope, mw, src = in_scope.loc[keep], mw.loc[keep], src.loc[keep]

    conf = pd.to_numeric(in_scope["confidence"], errors="coerce")
    p_mat = conf.map(lambda c: P_MAT_BY_CONFIDENCE.get(int(c)) if pd.notna(c) and int(c) in P_MAT_BY_CONFIDENCE else P_MAT_DEFAULT)
    diag["n_default_p_mat"] = int((~conf.isin(list(P_MAT_BY_CONFIDENCE))).sum())

    units = pd.DataFrame({
        "weather_zone": in_scope["weather_zone"].to_numpy(),
        "site_name": in_scope["site_name"].to_numpy(),
        "online": in_scope["online"].to_numpy(),
        "mw": mw.to_numpy(dtype=float),
        "p_mat": p_mat.to_numpy(dtype=float),
        "mw_source": src.to_numpy(),
    })
    diag["mw_source_tally"] = units["mw_source"].value_counts().to_dict()
    diag["n_units"] = len(units)
    return units, diag


def simulate_jump_paths(
    units: pd.DataFrame, zone: str, wall_year: int, base_month_gwh: dict[int, float],
    n_paths: int = N_PATHS, n_months: int = H_MONTHS, seed: int = SEED,
) -> tuple[np.ndarray, dict]:
    """(n_paths, n_months) jump contribution in index units for one (zone, wall).

    Months simulated = wall+1 Jan .. wall+2 Dec. Units online <= wall-12-31 are
    excluded (in-trend); units online after the window contribute zero.
    """
    months = pd.period_range(f"{wall_year + 1}-01", periods=n_months, freq="M")
    hours = np.array([p.days_in_month * 24.0 for p in months])
    base = np.array([base_month_gwh[p.month] for p in months])

    z = units.loc[
        (units["weather_zone"] == zone)
        & (pd.to_datetime(units["online"]) > pd.Timestamp(f"{wall_year}-12-31"))
    ]
    n_in_window = int((pd.to_datetime(z["online"]).dt.to_period("M") <= months[-1]).sum())
    diag = {"zone": zone, "wall": wall_year, "n_units_after_wall": len(z),
            "n_units_in_window": n_in_window,
            "mw_after_wall": float(z["mw"].sum()),
            "mw_in_window": float(z.loc[pd.to_datetime(z["online"]).dt.to_period("M") <= months[-1], "mw"].sum())}

    rng = np.random.default_rng(seed + wall_year * 10 + {"NCENT": 1, "COAST": 2, "SCENT": 3}.get(zone, 0))
    out = np.zeros((n_paths, n_months), dtype=np.float64)
    for _, u in z.iterrows():
        online_p = pd.Timestamp(u["online"]).to_period("M")
        k = np.array([(p - online_p).n + 1 for p in months], dtype=float)  # online month -> k=1
        if k[-1] <= 0:  # entirely after the window
            continue
        mat = rng.random(n_paths) < float(u["p_mat"])
        ramp_len = rng.uniform(*RAMP_MONTHS_RANGE, size=n_paths)
        frac = np.clip((k[None, :] - 0.5) / ramp_len[:, None], 0.0, 1.0)
        idx_unit = float(u["mw"]) * hours / 1000.0 / base  # index units per month at full ramp
        out += mat[:, None] * frac * idx_unit[None, :]
    return out, diag


# ---------------------------------------------------------------------------
# Annualization + scores
# ---------------------------------------------------------------------------


def paths_to_growth(paths: np.ndarray, level_wall: float) -> tuple[np.ndarray, np.ndarray]:
    """Per path: annual level wall+1 = mean(months 1-12), wall+2 = mean(13-24).
    Returns y/y growth in PERCENT: g1 = wall+1 over wall, g2 = wall+2 over wall+1."""
    lvl1 = paths[:, :12].mean(axis=1)
    lvl2 = paths[:, 12:24].mean(axis=1)
    g1 = 100.0 * (lvl1 / level_wall - 1.0)
    g2 = 100.0 * (lvl2 / lvl1 - 1.0)
    return g1, g2


def crps_empirical(y: float, samples: np.ndarray) -> float:
    """Sample-based CRPS: mean|x-y| - (1/(2N^2)) sum_ij |x_i-x_j|, the pairwise
    term computed O(N log N) from the sorted sample."""
    x = np.sort(np.asarray(samples, dtype=float))
    n = len(x)
    term1 = float(np.abs(x - y).mean())
    k = np.arange(1, n + 1, dtype=float)
    term2 = float(((2.0 * k - n - 1.0) * x).sum()) / (n * n)
    return term1 - term2


def crps_gaussian(y: float, mu: float, sigma: float) -> float:
    """Closed-form CRPS of N(mu, sigma^2) at y."""
    z = (y - mu) / sigma
    return float(sigma * (z * (2.0 * norm.cdf(z) - 1.0) + 2.0 * norm.pdf(z) - 1.0 / np.sqrt(np.pi)))
