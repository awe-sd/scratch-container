"""Task 08-X AMENDMENT 2 harness (tag task08x2): corrected dual truths, three
trend variants x sheet on/off = 6 P-configs, B0/B1 rescored, conformal LOFO
diagnostic, variance-share diagnostics. See docs/training_log.md -- the
task08x AMENDMENT 2 pre-registration entry (written BEFORE this run) is the
binding spec; §7 criteria are verbatim unchanged from the original task08x
pre-registration.

TRUTH: every fold scored under BOTH truth_sym (symmetric matched-hour,
validate.py convention) and truth_norm (annual fit through the target year,
numerically the old rule-sweep basis) -- src/truth_bases.py. The defective
run-1 pre-registered truth (calendar-asymmetric backtest.run_fold
reproduction) is retired and never quoted here. Criteria are evaluated under
EACH truth separately; never blended.

CONFIGS: trend in {llt_free, llt_damped, llt_t5} x sheet in {on, off} -> 6
"P-<trend>[+sheet]" models (P-free+sheet, P-free, P-damped+sheet, P-damped,
P-t5+sheet, P-t5). Same N=10,000 paths, 24 months, seed=42 FLAT across all
six configs (no per-config salting); the jump layer keeps its own existing
zone/wall salt (prob_size.simulate_jump_paths, unchanged) and is simulated
ONCE per (zone, wall), shared identically across every sheet-on config so
only the trend differs between them.

COMPONENT A: data/derived/size_index_monthly_w{2021..2024}.parquet (run-1
artifacts) are REUSED, not refit -- loaded from disk and fed directly to the
trend fits. The one unavoidable in-memory recomputation is base_month_gwh
(the jump layer's unit-conversion constant), which isn't persisted anywhere;
it is recovered via sim_m.build_monthly_index() (no file write) and checked
bit-close to the loaded parquet before being trusted (see
component_a_context()).

ITERATE is CONSUMED by this run (the damped-slope + heavy-tail iteration IS
this run) -- no further tuning follows a per-config ITERATE-pattern read.

Run: uv run python load-forecast/scripts/experiment_prob_size2.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import config as cfg  # noqa: E402
import prob_size as ps  # noqa: E402
import size_index as si  # noqa: E402
import size_index_monthly as sim_m  # noqa: E402
from truth_bases import normalized_growth, symmetric_growth, zone_frame  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiment_prob_size import (  # noqa: E402
    annual_at_wall,
    b0_growth_points,
    b1_growth_params,
    pooled_b0_sigma,
)

OUTPUT_DIR = cfg.PROJECT_ROOT / "output"
FOLDS_CSV = OUTPUT_DIR / "task08x2_folds.csv"
SAMPLES_PARQUET = OUTPUT_DIR / "task08x2_samples.parquet"
CONFORMAL_CSV = OUTPUT_DIR / "task08x2_conformal.csv"
DIAGNOSTICS_CSV = OUTPUT_DIR / "task08x2_diagnostics.csv"
EXPERIMENTS_CSV = OUTPUT_DIR / "experiments.csv"
RUN1_FOLDS_CSV = OUTPUT_DIR / "task08x_folds.csv"
RUN1_DIAG_CSV = OUTPUT_DIR / "task08x_truth_diagnostic.csv"

WALLS = sim_m.WALLS
QLEVELS = (0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)
QNAMES = ("p5", "p10", "p25", "p50", "p75", "p90", "p95")
SEED = ps.SEED  # 42, FLAT across all 6 configs -- no per-config salting
CONFORMAL_LEVEL = 0.80

TRENDS = ("free", "damped", "t5")
SHEETS = ("sheet", "nosheet")

FOLDS_COLUMNS = [
    "zone", "wall", "horizon", "model", "truth_sym", "truth_norm",
    "p5", "p10", "p25", "p50", "p75", "p90", "p95",
    "crps_sym", "crps_norm", "covered_10_90_sym", "covered_10_90_norm",
    "band_width_10_90", "jump_units_target_year", "jump_mw_target_year",
    "seed", "notes",
]


def config_name(trend: str, sheet: str) -> str:
    base = {"free": "P-free", "damped": "P-damped", "t5": "P-t5"}[trend]
    return f"{base}+sheet" if sheet == "sheet" else base


P_CONFIGS = [config_name(t, s) for t in TRENDS for s in SHEETS]


# ---------------------------------------------------------------------------
# Component A reuse (no refit of the persisted artifact; base_month_gwh is the
# one unavoidable in-memory recomputation, verified bit-close to the parquet)
# ---------------------------------------------------------------------------


def component_a_context(daily_by_zone: dict[str, pd.DataFrame]):
    monthly_by_wall = {
        w: pd.read_parquet(cfg.DERIVED_DIR / f"size_index_monthly_w{w}.parquet") for w in WALLS
    }
    base_month_gwh: dict[tuple[str, int], dict[int, float]] = {}
    max_drift = 0.0
    for zone in cfg.ZONES:
        for wall in WALLS:
            mi = sim_m.build_monthly_index(daily_by_zone[zone], zone, wall)
            base_month_gwh[(zone, wall)] = mi.base_month_gwh
            persisted = monthly_by_wall[wall]
            pz = persisted.loc[persisted["zone"] == zone].sort_values("ym")["size_idx_m"].to_numpy(dtype=float)
            fz = mi.monthly.sort_values("ym")["size_idx_m"].to_numpy(dtype=float)
            if len(pz) != len(fz):
                raise AssertionError(f"{zone} w{wall}: component-A row-count mismatch vs run-1 parquet")
            d = float(np.abs(pz - fz).max())
            max_drift = max(max_drift, d)
            if d > 1e-9:
                raise AssertionError(
                    f"{zone} w{wall}: component-A drift vs run-1 parquet (max |diff|={d:.3e} > 1e-9) "
                    "-- Component A must not be refit for task08x2, only reused"
                )
    return monthly_by_wall, base_month_gwh, max_drift


def jump_target_year_stats(units: pd.DataFrame, zone: str, target_year: int) -> tuple[int, float]:
    z = units.loc[(units["weather_zone"] == zone) & (pd.to_datetime(units["online"]).dt.year == target_year)]
    return int(len(z)), float(z["mw"].sum())


# ---------------------------------------------------------------------------
# Fold-row assembly (dual truth schema)
# ---------------------------------------------------------------------------


def sample_dual_row(zone, wall, horizon, model, truth_sym, truth_norm, samples,
                    jump_units_ty, jump_mw_ty, notes="") -> dict:
    q = {n: float(np.quantile(samples, p)) for n, p in zip(QNAMES, QLEVELS)}
    row = {
        "zone": zone, "wall": wall, "horizon": horizon, "model": model,
        "truth_sym": truth_sym, "truth_norm": truth_norm, **q,
        "band_width_10_90": q["p90"] - q["p10"],
        "jump_units_target_year": jump_units_ty, "jump_mw_target_year": jump_mw_ty,
        "seed": SEED, "notes": notes,
    }
    for tag, tv in (("sym", truth_sym), ("norm", truth_norm)):
        if np.isfinite(tv):
            row[f"crps_{tag}"] = ps.crps_empirical(tv, samples)
            row[f"covered_10_90_{tag}"] = bool(q["p10"] <= tv <= q["p90"])
        else:
            row[f"crps_{tag}"] = np.nan
            row[f"covered_10_90_{tag}"] = None
    return row


def gaussian_dual_row(zone, wall, horizon, model, truth_sym, truth_norm, mu, sigma,
                      jump_units_ty, jump_mw_ty, notes="") -> dict:
    q = {n: mu + norm.ppf(p) * sigma for n, p in zip(QNAMES, QLEVELS)}
    row = {
        "zone": zone, "wall": wall, "horizon": horizon, "model": model,
        "truth_sym": truth_sym, "truth_norm": truth_norm, **q,
        "band_width_10_90": q["p90"] - q["p10"],
        "jump_units_target_year": jump_units_ty, "jump_mw_target_year": jump_mw_ty,
        "seed": SEED, "notes": notes,
    }
    for tag, tv in (("sym", truth_sym), ("norm", truth_norm)):
        if np.isfinite(tv):
            row[f"crps_{tag}"] = ps.crps_gaussian(tv, mu, sigma)
            row[f"covered_10_90_{tag}"] = bool(q["p10"] <= tv <= q["p90"])
        else:
            row[f"crps_{tag}"] = np.nan
            row[f"covered_10_90_{tag}"] = None
    return row


# ---------------------------------------------------------------------------
# Conformal LOFO diagnostic (module-level, pure function -- unit-testable)
# ---------------------------------------------------------------------------


def conformal_lofo(truth: np.ndarray, p10: np.ndarray, p50: np.ndarray, p90: np.ndarray,
                   level: float = CONFORMAL_LEVEL) -> pd.DataFrame:
    """Leave-one-fold-out conformal calibration diagnostic (POST-HOC, judged
    on nothing). score s_j = |truth_j - p50_j| / ((p90_j-p10_j)/2) over all
    folds; for fold i, k_i = `level`-th percentile of {s_j : j != i} (numpy
    quantile, default linear interpolation); calibrated coverage_i =
    |truth_i - p50_i| <= k_i * (p90_i-p10_i)/2; calibrated width_i =
    k_i * (p90_i - p10_i) (full width, not half). Returns one row per fold:
    s, k, calibrated_cover, calibrated_width."""
    truth = np.asarray(truth, dtype=float)
    p10 = np.asarray(p10, dtype=float)
    p50 = np.asarray(p50, dtype=float)
    p90 = np.asarray(p90, dtype=float)
    n = len(truth)
    half_width = (p90 - p10) / 2.0
    width = p90 - p10
    s = np.abs(truth - p50) / half_width
    k = np.empty(n)
    cover = np.empty(n, dtype=bool)
    cal_width = np.empty(n)
    for i in range(n):
        others = np.delete(s, i)
        k[i] = np.quantile(others, level)
        cover[i] = np.abs(truth[i] - p50[i]) <= k[i] * half_width[i]
        cal_width[i] = k[i] * width[i]
    return pd.DataFrame({"s": s, "k": k, "calibrated_cover": cover, "calibrated_width": cal_width})


# ---------------------------------------------------------------------------
# Regression anchors vs run-1 (P-free+sheet must reproduce run 1 exactly)
# ---------------------------------------------------------------------------


def run_regression_checks(folds: pd.DataFrame) -> None:
    run1_folds = pd.read_csv(RUN1_FOLDS_CSV)
    run1_diag = pd.read_csv(RUN1_DIAG_CSV)

    pfs = folds.loc[folds["model"] == "P-free+sheet"].copy()
    r1p = run1_folds.loc[run1_folds["model"] == "P"].copy()
    m = pfs.merge(r1p, on=["zone", "wall", "horizon"], suffixes=("_new", "_run1"))
    if len(m) != len(pfs):
        raise AssertionError("regression merge dropped rows -- zone/wall/horizon mismatch vs run-1 folds")
    worst = 0.0
    for qn in QNAMES:
        diff = (m[f"{qn}_new"] - m[f"{qn}_run1"]).abs()
        worst = max(worst, float(diff.max()))
        if diff.max() >= 1e-6:
            raise AssertionError(f"REGRESSION: {qn} diverges from run-1 P by up to {diff.max():.2e} (tol 1e-6)")
    wdiff = (m["band_width_10_90_new"] - m["band_width_10_90_run1"]).abs()
    worst = max(worst, float(wdiff.max()))
    if wdiff.max() >= 1e-6:
        raise AssertionError(f"REGRESSION: band_width_10_90 diverges from run-1 P by up to {wdiff.max():.2e}")
    print(f"regression check 1 PASSED: P-free+sheet quantiles/width match run-1 {RUN1_FOLDS_CSV.name} "
          f"model-P rows (worst |diff|={worst:.2e}, tol 1e-6)")

    r1d = run1_diag.loc[run1_diag["model"] == "P"].copy()
    m2 = pfs.merge(r1d, on=["zone", "wall", "horizon"], suffixes=("_new", "_diag"))
    if len(m2) != len(pfs):
        raise AssertionError("regression merge dropped rows -- zone/wall/horizon mismatch vs run-1 diagnostic")
    worst_crps = 0.0
    for tag in ("sym", "norm"):
        cdiff = (m2[f"crps_{tag}_new"] - m2[f"crps_{tag}_diag"]).abs()
        worst_crps = max(worst_crps, float(cdiff.max()))
        if cdiff.max() >= 1e-3:
            raise AssertionError(f"REGRESSION: crps_{tag} diverges from {RUN1_DIAG_CSV.name} by up to {cdiff.max():.2e}")
        cov_new = m2[f"covered_10_90_{tag}_new"]
        cov_old = m2[f"covered_10_90_{tag}_diag"]
        both_known = cov_new.notna() & cov_old.notna()
        mismatch = both_known & (cov_new.astype("boolean") != cov_old.astype("boolean"))
        if mismatch.any():
            raise AssertionError(f"REGRESSION: covered_10_90_{tag} disagrees with {RUN1_DIAG_CSV.name} "
                                  f"on {int(mismatch.sum())} folds")
    print(f"regression check 2 PASSED: P-free+sheet crps_sym/crps_norm/coverage match {RUN1_DIAG_CSV.name} "
          f"model-P rows (worst |crps diff|={worst_crps:.2e}, tol 1e-3; coverage exact)")

    pfo = folds.loc[(folds["model"] == "P-free") & (folds["zone"] == "NCENT") & (folds["wall"] == 2024)
                    & (folds["horizon"] == 1)]
    if len(pfo) != 1:
        raise AssertionError(f"expected exactly 1 P-free NCENT w2024 h1 row, found {len(pfo)}")
    pfo = pfo.iloc[0]
    expect = {"p10": 1.68, "p50": 3.61, "p90": 5.55, "p95": 6.06}
    for k, v in expect.items():
        if abs(pfo[k] - v) >= 0.02:
            raise AssertionError(
                f"REGRESSION: P-free (sheet-off) NCENT w2024 {k}={pfo[k]:.3f} vs published RESULTS "
                f"CORRECTION value {v} (tol 0.02)"
            )
    h1_pf = folds.loc[(folds["model"] == "P-free") & (folds["horizon"] == 1)]
    cov_sym = int(h1_pf["covered_10_90_sym"].sum())
    cov_norm = int(h1_pf["covered_10_90_norm"].sum())
    if cov_sym != 8 or cov_norm != 8:
        raise AssertionError(f"REGRESSION: P-free (sheet-off) coverage sym={cov_sym}/12 norm={cov_norm}/12, "
                              "published RESULTS CORRECTION says 8/12 both")
    crps_sym_mean = float(h1_pf["crps_sym"].mean())
    crps_norm_mean = float(h1_pf["crps_norm"].mean())
    if abs(crps_sym_mean - 3.328) >= 0.02 or abs(crps_norm_mean - 1.833) >= 0.02:
        raise AssertionError(
            f"REGRESSION: P-free (sheet-off) CRPS h1 mean sym={crps_sym_mean:.3f} norm={crps_norm_mean:.3f} "
            "vs published RESULTS CORRECTION 3.328/1.833 (tol 0.02)"
        )
    print("regression check 3 PASSED: P-free (sheet-off) reproduces the RESULTS CORRECTION headline "
          "(NCENT w2024 [p10,p50,p90,p95]=[1.68,3.61,5.55,6.06], coverage 8/12 sym+norm, "
          "CRPS h1 mean 3.328 sym / 1.833 norm)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    t0 = time.time()
    print("=== Task 08-X AMENDMENT 2 (tag task08x2): dual truth, 3 trends x sheet on/off ===")
    print(f"seed={SEED} (flat, no per-config salting) N={ps.N_PATHS} H={ps.H_MONTHS} "
          f"conformal_level={CONFORMAL_LEVEL}")

    load_hourly = pd.read_parquet(
        cfg.DERIVED_DIR / "load_hourly.parquet",
        columns=["weather_zone", "ts_local", "load_mw", "event_flag"],
    )
    zone_weather = pd.read_parquet(cfg.DERIVED_DIR / "zone_weather_hourly.parquet")
    frames = {z: zone_frame(load_hourly, zone_weather, z) for z in cfg.ZONES}
    daily = {z: si.build_daily(load_hourly, zone_weather, z) for z in cfg.ZONES}

    print("\n--- component A: loading run-1 monthly indices (REUSE, no refit of the artifact) ---")
    monthly_by_wall, base_month_gwh, max_drift = component_a_context(daily)
    n_rows = sum(len(v) for v in monthly_by_wall.values())
    print(f"loaded {n_rows} monthly rows across {len(WALLS)} walls; base_month_gwh recomputed in-memory "
          f"(not persisted, needed only for the jump layer), max drift vs persisted parquet = {max_drift:.2e} (tol 1e-9)")

    units, udiag = ps.load_jump_units()
    print(f"\njump units: {udiag['n_units']} rows usable | mw_source {udiag['mw_source_tally']} | "
          f"dropped: {udiag['n_unmapped_rows']} unmapped, {udiag['n_zone_out_of_scope']} zone-out-of-scope, "
          f"{udiag['n_no_online_date']} no-online-date, {udiag['n_no_mw']} no-usable-MW")

    sigma_b0 = pooled_b0_sigma()
    print(f"B0 pooled sigma (18 backtest_rolling growth errors, ddof=1): {sigma_b0:.3f} pp")

    fold_rows: list[dict] = []
    diag_rows: list[dict] = []
    fit_cache: dict[tuple[str, int], dict] = {}

    for zone in cfg.ZONES:
        for wall in WALLS:
            monthly_w = monthly_by_wall[wall]
            llt = ps.fit_llt(monthly_w, zone, wall)
            ets = ps.fit_ets_damped(monthly_w, zone, wall)
            wall_vals = monthly_w.loc[
                (monthly_w["zone"] == zone) & (pd.to_datetime(monthly_w["ym"]).dt.year == wall), "size_idx_m"
            ]
            if len(wall_vals) != 12:
                raise ValueError(f"{zone} w{wall}: wall year has {len(wall_vals)} monthly values")
            level_wall = float(wall_vals.mean())
            fit_cache[(zone, wall)] = {"llt": llt, "ets": ets, "level_wall": level_wall}

            jump_paths, jdiag = ps.simulate_jump_paths(units, zone, wall, base_month_gwh[(zone, wall)])
            zero_paths = np.zeros_like(jump_paths)

            truth_sym = {}
            truth_norm = {}
            for h in (1, 2):
                base_y, tgt_y = wall + h - 1, wall + h
                truth_sym[h] = symmetric_growth(frames[zone], base_y, tgt_y)
                truth_norm[h] = normalized_growth(daily[zone], zone, tgt_y)

            p = llt.params
            tot = p["sigma2.irregular"] + p["sigma2.level"] + p["sigma2.trend"]
            diag_rows.append({
                "zone": zone, "wall": wall,
                "llt_sigma2_irregular": p["sigma2.irregular"], "llt_sigma2_level": p["sigma2.level"],
                "llt_sigma2_trend": p["sigma2.trend"],
                "share_irregular": p["sigma2.irregular"] / tot, "share_level": p["sigma2.level"] / tot,
                "share_trend": p["sigma2.trend"] / tot, "llt_slope_var_boundary": llt.slope_var_boundary,
                "ets_alpha": ets.alpha, "ets_beta": ets.beta, "ets_phi": ets.phi, "ets_sigma2": ets.sigma2,
                "ets_phi_boundary": ets.phi_boundary,
            })

            trend_paths = {
                "free": ps.simulate_llt_paths(llt, seed=SEED),
                "damped": ps.simulate_ets_paths(ets, seed=SEED),
                "t5": ps.simulate_llt_t5_paths(llt, seed=SEED),
            }
            for arr in trend_paths.values():
                assert arr.shape == (ps.N_PATHS, ps.H_MONTHS), f"unexpected trend path shape {arr.shape}"

            for trend in TRENDS:
                for sheet in SHEETS:
                    model = config_name(trend, sheet)
                    jp = jump_paths if sheet == "sheet" else zero_paths
                    size_paths = trend_paths[trend] + jp
                    g1, g2 = ps.paths_to_growth(size_paths, level_wall)
                    for h, g in ((1, g1), (2, g2)):
                        ju, jm = jump_target_year_stats(units, zone, wall + h)
                        note_parts = []
                        if trend == "damped" and ets.phi_boundary:
                            note_parts.append("ETS phi at bound")
                        if trend == "free" and llt.slope_var_boundary:
                            note_parts.append("LLT slope-var boundary")
                        if not np.isfinite(truth_sym[h]) or not np.isfinite(truth_norm[h]):
                            note_parts.append("partial/no truth (incomplete target year)")
                        fold_rows.append(sample_dual_row(
                            zone, wall, h, model, truth_sym[h], truth_norm[h], g, ju, jm,
                            "; ".join(note_parts)))

            annual = annual_at_wall(daily[zone], zone, wall)
            b0g1, b0g2 = b0_growth_points(annual, zone, wall)
            mu1, sd1, mu2, sd2 = b1_growth_params(annual)
            for h, (mu, sd) in ((1, (b0g1, sigma_b0)), (2, (b0g2, sigma_b0))):
                ju, jm = jump_target_year_stats(units, zone, wall + h)
                note = "sigma=h1 pooled" if h == 2 else ""
                if not np.isfinite(truth_sym[h]) or not np.isfinite(truth_norm[h]):
                    note = (note + "; partial/no truth (incomplete target year)").strip("; ")
                fold_rows.append(gaussian_dual_row(zone, wall, h, "B0", truth_sym[h], truth_norm[h], mu, sd, ju, jm, note))
            for h, (mu, sd) in ((1, (mu1, sd1)), (2, (mu2, sd2))):
                ju, jm = jump_target_year_stats(units, zone, wall + h)
                note = "partial/no truth (incomplete target year)" if (
                    not np.isfinite(truth_sym[h]) or not np.isfinite(truth_norm[h])) else ""
                fold_rows.append(gaussian_dual_row(zone, wall, h, "B1", truth_sym[h], truth_norm[h], mu, sd, ju, jm, note))

            ju1, jm1 = jump_target_year_stats(units, zone, wall + 1)
            print(f"{zone} w{wall}: truth_sym h1 {truth_sym[1]:+.2f}% truth_norm h1 {truth_norm[1]:+.2f}% | "
                  f"llt boundary={llt.slope_var_boundary} ets phi={ets.phi:.3f}(boundary={ets.phi_boundary}) | "
                  f"jump target-yr {wall + 1}: {ju1} units / {jm1:.0f} MW")

    folds = pd.DataFrame(fold_rows)[FOLDS_COLUMNS]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    folds.to_csv(FOLDS_CSV, index=False)
    diagnostics = pd.DataFrame(diag_rows)
    diagnostics.to_csv(DIAGNOSTICS_CSV, index=False)
    print(f"\nwrote {FOLDS_CSV} ({len(folds)} rows), {DIAGNOSTICS_CSV} ({len(diagnostics)} rows)")

    print("\n--- regression anchors vs run-1 (P-free+sheet must reproduce run 1 exactly) ---")
    run_regression_checks(folds)

    print("\n=== variance-share diagnostics (LLT sigma2 shares + ETS params, per zone-wall) ===")
    print(diagnostics.round(4).to_string(index=False))

    h1 = folds.loc[folds["horizon"] == 1]

    print("\n=== §7 criteria, EACH P-config UNDER EACH truth (sym, norm separately; no blending) ===")
    verdict_rows = []
    for truth_tag in ("sym", "norm"):
        for cfgname in P_CONFIGS:
            p1 = h1.loc[h1["model"] == cfgname].set_index(["zone", "wall"])
            c1_row = p1.loc[("NCENT", 2024)]
            tv = c1_row[f"truth_{truth_tag}"]
            c1 = bool(tv <= c1_row["p95"])
            cov = int(p1[f"covered_10_90_{truth_tag}"].sum())
            c2 = cov >= 8
            crps_mean = {m: float(h1.loc[h1["model"] == m, f"crps_{truth_tag}"].mean())
                        for m in (cfgname, "B0", "B1")}
            c3 = crps_mean[cfgname] < crps_mean["B0"] and crps_mean[cfgname] < crps_mean["B1"]
            w_coast = float(p1.loc[("COAST", 2024), "band_width_10_90"])
            w_scent = float(p1.loc[("SCENT", 2024), "band_width_10_90"])
            c4 = (w_coast <= 5.0) and (w_scent <= 5.0)
            kill1 = not c1
            kill2 = c2 and (w_coast > 8.0 or w_scent > 8.0)
            print(f"\n--- {cfgname} | truth_{truth_tag} ---")
            print(f"C1 NCENT w2024 truth {tv:+.2f} <= P95 {c1_row['p95']:+.2f}: {c1}")
            print(f"C2 coverage {cov}/12 (need >=8): {c2}")
            print(f"C3 CRPS h1 mean — {cfgname} {crps_mean[cfgname]:.3f} vs B0 {crps_mean['B0']:.3f} "
                  f"vs B1 {crps_mean['B1']:.3f}: beats both = {c3}")
            print(f"C4 wall-2024 P10-P90 width — COAST {w_coast:.2f} SCENT {w_scent:.2f} pp (<=5.0 each): {c4}")
            print(f"KILL-2 proximity (width > 8.0): COAST {w_coast > 8.0} SCENT {w_scent > 8.0}")
            if c1 and c2 and c3 and c4:
                pattern = "PROMOTE-pattern"
            elif kill1:
                pattern = "KILL-pattern (C1 fails)"
            elif kill2:
                pattern = "KILL-pattern (coverage only via >4pp bands)"
            elif c2 and not c3:
                pattern = "ITERATE-pattern (CONSUMED this run -- no further tuning follows)"
            else:
                pattern = "STOP-AND-REPORT-pattern"
            print(f"mechanical pattern: {pattern}")
            verdict_rows.append({"config": cfgname, "truth": truth_tag, "c1": c1, "c2": c2, "c3": c3, "c4": c4,
                                 "coverage": cov, "w_coast": w_coast, "w_scent": w_scent, "pattern": pattern})

    print("\n=== median-accuracy table: mean |p50 - truth| per model per truth, 12 h1 folds ===")
    acc_rows = []
    for truth_tag in ("sym", "norm"):
        for m in P_CONFIGS + ["B0", "B1"]:
            sub = h1.loc[h1["model"] == m]
            mae = float((sub["p50"] - sub[f"truth_{truth_tag}"]).abs().mean())
            acc_rows.append({"model": m, "truth": truth_tag, "mean_abs_p50_err": mae})
    acc_df = pd.DataFrame(acc_rows)
    print(acc_df.pivot(index="model", columns="truth", values="mean_abs_p50_err").round(3)
          .reindex(P_CONFIGS + ["B0", "B1"]).to_string())

    print(f"\n=== conformal LOFO diagnostic (POST-HOC, judged on nothing) — level={CONFORMAL_LEVEL} ===")
    conformal_frames = []
    for truth_tag in ("sym", "norm"):
        for cfgname in P_CONFIGS:
            sub = h1.loc[h1["model"] == cfgname].reset_index(drop=True)
            truth = sub[f"truth_{truth_tag}"].to_numpy(dtype=float)
            if not np.all(np.isfinite(truth)):
                print(f"{cfgname} | truth_{truth_tag}: SKIPPED (non-finite truth among the 12 h1 folds)")
                continue
            cal = conformal_lofo(truth, sub["p10"].to_numpy(dtype=float), sub["p50"].to_numpy(dtype=float),
                                 sub["p90"].to_numpy(dtype=float), level=CONFORMAL_LEVEL)
            cal["model"] = cfgname
            cal["truth_basis"] = truth_tag
            cal["zone"] = sub["zone"].to_numpy()
            cal["wall"] = sub["wall"].to_numpy()
            conformal_frames.append(cal)
            print(f"{cfgname} | truth_{truth_tag}: calibrated coverage {int(cal['calibrated_cover'].sum())}/12, "
                  f"median calibrated width {cal['calibrated_width'].median():.2f} pp "
                  f"(uncalibrated width median {sub['band_width_10_90'].median():.2f} pp)")
    conformal_df = pd.concat(conformal_frames, ignore_index=True)
    conformal_df = conformal_df[["model", "truth_basis", "zone", "wall", "s", "k", "calibrated_cover", "calibrated_width"]]
    conformal_df.to_csv(CONFORMAL_CSV, index=False)
    print(f"wrote {CONFORMAL_CSV} ({len(conformal_df)} rows)")

    print("\n=== winner selection: lowest mean of (crps_sym+crps_norm)/2 over the 12 h1 folds, 6 P-configs ===")
    winner_scores = {}
    for cfgname in P_CONFIGS:
        sub = h1.loc[h1["model"] == cfgname]
        score = float(((sub["crps_sym"] + sub["crps_norm"]) / 2.0).mean())
        winner_scores[cfgname] = score
        print(f"{cfgname}: {score:.4f}")
    winner = min(winner_scores, key=winner_scores.get)
    print(f"\nWINNER: {winner} (mean (crps_sym+crps_norm)/2 = {winner_scores[winner]:.4f})")

    print(f"\n--- persisting samples for winner ({winner}) ONLY ---")
    w_trend, w_sheet = next((t, s) for t in TRENDS for s in SHEETS if config_name(t, s) == winner)
    sample_frames = []
    for zone in cfg.ZONES:
        for wall in WALLS:
            ctx = fit_cache[(zone, wall)]
            if w_trend == "free":
                trend_p = ps.simulate_llt_paths(ctx["llt"], seed=SEED)
            elif w_trend == "damped":
                trend_p = ps.simulate_ets_paths(ctx["ets"], seed=SEED)
            else:
                trend_p = ps.simulate_llt_t5_paths(ctx["llt"], seed=SEED)
            if w_sheet == "sheet":
                jump_p, _ = ps.simulate_jump_paths(units, zone, wall, base_month_gwh[(zone, wall)])
            else:
                jump_p = np.zeros_like(trend_p)
            size_p = trend_p + jump_p
            n = ps.N_PATHS
            sample_frames.append(pd.DataFrame({
                "zone": np.repeat(zone, n * ps.H_MONTHS),
                "wall": np.full(n * ps.H_MONTHS, wall, dtype=np.int32),
                "sample_id": np.repeat(np.arange(n, dtype=np.int32), ps.H_MONTHS),
                "horizon_month": np.tile(np.arange(1, ps.H_MONTHS + 1, dtype=np.int32), n),
                "size_idx": size_p.astype(np.float32).ravel(),
                "llt_component": trend_p.astype(np.float32).ravel(),
                "jump_component": jump_p.astype(np.float32).ravel(),
            }))
    samples = pd.concat(sample_frames, ignore_index=True)
    samples.to_parquet(SAMPLES_PARQUET, index=False)
    print(f"wrote {SAMPLES_PARQUET} ({len(samples):,} rows, winner={winner})")

    print("\n--- leaderboard ---")
    knobs = {"trend_configs": P_CONFIGS, "n_paths": ps.N_PATHS, "seed": SEED,
            "sigma_b0": round(sigma_b0, 3), "conformal_level": CONFORMAL_LEVEL, "winner": winner}
    ts = str(pd.Timestamp.now())
    lb = []
    for cfgname in P_CONFIGS:
        sub = h1.loc[h1["model"] == cfgname]
        lb.append({
            "zone": "ALL3", "wall_year": "2021-2024", "target_year": "h1", "status": "ok",
            "tag": f"task08x2-{cfgname}", "params": json.dumps(knobs), "ts": ts,
            "crps_sym_h1_mean": round(float(sub["crps_sym"].mean()), 4),
            "crps_norm_h1_mean": round(float(sub["crps_norm"].mean()), 4),
            "coverage_10_90_sym_h1": f"{int(sub['covered_10_90_sym'].sum())}/12",
            "coverage_10_90_norm_h1": f"{int(sub['covered_10_90_norm'].sum())}/12",
            "basis_note": "sym+norm corrected truths, see training_log task08x2",
        })
    add = pd.DataFrame(lb)
    if EXPERIMENTS_CSV.exists():
        prior = pd.read_csv(EXPERIMENTS_CSV)
        add = pd.concat([prior, add], ignore_index=True)
    add.to_csv(EXPERIMENTS_CSV, index=False)
    print(f"appended {len(lb)} leaderboard rows to {EXPERIMENTS_CSV}")

    print(f"\ntotal runtime {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
