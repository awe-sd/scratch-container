"""Task 08-X harness: probabilistic size-index MVE — folds, baselines, metrics.

Folds: 3 zones x walls {2021,2022,2023,2024} = 12 primary folds (horizon 1);
horizon 2 reported where truth exists (wall-2024 h2 target 2026 is a partial
year, noted). Score variable: y/y annual growth in PERCENT — h1 = wall+1 over
wall, h2 = wall+2 over wall+1 (pre-registered reading of "annualize wall+1 and
wall+2").

TRUTH BASIS: validate/backtest matched-hour basis — a verbatim reproduction of
backtest.run_fold's actual_growth (target-year scoreable hours vs the wall
year's hours matched on (month, day, hour); uri/outage excluded, covid in;
load hours require a weather match, as build_frame does). NEVER the rule-sweep
basis. The harness startup verifies the reproduction against the known
NCENT wall-2024 value (+4.81%) and aborts if it disagrees by > 0.05 pp.

Models:
  P  — LLT on the monthly canonical index + tracking-sheet jump layer (prob_size)
  B0 — production extrapolation (size_index.extrapolate, per-zone
       cfg.SIZE_EXTRAP_YEARS) + Gaussian band, sigma = pooled std of the
       production growth errors across all 18 backtest_rolling folds
  B1 — random walk with drift on the annual index (drift = mean of last 3
       annual diffs; per-step diff variance -> y/y growth band both horizons)
  B2 — ERCOT LTLF vintages (conditional; runs only if the recon found data)

Artifacts: output/task08x_folds.csv, output/task08x_samples.parquet,
one summary row per model appended to output/experiments.csv.

Run: uv run python load-forecast/scripts/experiment_prob_size.py
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
from truth_bases import zone_frame  # noqa: E402

OUTPUT_DIR = cfg.PROJECT_ROOT / "output"
FOLDS_CSV = OUTPUT_DIR / "task08x_folds.csv"
SAMPLES_PARQUET = OUTPUT_DIR / "task08x_samples.parquet"
EXPERIMENTS_CSV = OUTPUT_DIR / "experiments.csv"
BACKTEST_CSV = OUTPUT_DIR / "backtest_rolling.csv"

WALLS = sim_m.WALLS
BASIS = "validate/backtest matched-hour (backtest.run_fold actual_growth reproduction)"
QLEVELS = (0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)
QNAMES = ("p5", "p10", "p25", "p50", "p75", "p90", "p95")
TRUTH_CHECK = ("NCENT", 2024, 4.81, 0.05)  # zone, wall, expected h1 truth, tolerance pp


# ---------------------------------------------------------------------------
# Truth: matched-hour growth, verbatim run_fold reproduction
# ---------------------------------------------------------------------------


def matched_hour_growth(frame: pd.DataFrame, base_year: int, target_year: int) -> tuple[float, str]:
    """100 * (target scoreable load / base-year load on the target's
    (month,day,hour) key set - 1). Returns (growth_pct, note)."""
    test = frame.loc[(frame["day_year"] == target_year) & frame["scoreable"]]
    if len(test) < 1000:
        return float("nan"), f"no truth: only {len(test)} scoreable target hours"
    keys = set(zip(test["ts_local"].dt.month, test["ts_local"].dt.day, test["ts_local"].dt.hour))
    base_rows = frame.loc[(frame["day_year"] == base_year) & frame["scoreable"]]
    bk = list(zip(base_rows["ts_local"].dt.month, base_rows["ts_local"].dt.day, base_rows["ts_local"].dt.hour))
    mask = pd.Series([k in keys for k in bk], index=base_rows.index)
    base_sum = float(base_rows.loc[mask, "load_mw"].sum())
    growth = 100.0 * (float(test["load_mw"].sum()) / base_sum - 1.0)
    note = ""
    if len(test) < 8000:
        note = f"partial target year ({len(test)} hrs)"
    return growth, note


# ---------------------------------------------------------------------------
# Baselines
# ---------------------------------------------------------------------------


def pooled_b0_sigma() -> float:
    bt = pd.read_csv(BACKTEST_CSV)
    ok = bt.loc[bt["status"] == "ok", "growth_err_pp"].astype(float)
    return float(ok.std(ddof=1))


def annual_at_wall(daily: pd.DataFrame, zone: str, wall: int) -> pd.DataFrame:
    fit = si.fit_zone(daily, zone, train_end=f"{wall}-12-31")
    return si.normalized_annual_gwh(fit, daily, train_end=f"{wall}-12-31")


def b0_growth_points(annual: pd.DataFrame, zone: str, wall: int) -> tuple[float, float]:
    n_fit = cfg.SIZE_EXTRAP_YEARS.get(zone, 6)
    extra = si.extrapolate(annual, wall + 2, n_fit_years=n_fit)
    g_w = float(annual.loc[annual["year"] == wall, "normalized_gwh"].iloc[0])
    e1 = float(extra.loc[extra["year"] == wall + 1, "normalized_gwh"].iloc[0])
    e2 = float(extra.loc[extra["year"] == wall + 2, "normalized_gwh"].iloc[0])
    return 100.0 * (e1 / g_w - 1.0), 100.0 * (e2 / e1 - 1.0)


def b1_growth_params(annual: pd.DataFrame) -> tuple[float, float, float, float]:
    """(mu1, sd1, mu2, sd2) in growth %, random walk with drift on the annual
    index: drift = mean of last 3 annual diffs, per-step diff std (all fitted
    diffs, ddof=1) -> y/y band at each horizon."""
    g = annual.sort_values("year")["normalized_gwh"].to_numpy(dtype=float)
    diffs = np.diff(g)
    drift = float(diffs[-3:].mean())
    s_d = float(diffs.std(ddof=1))
    lvl_w = float(g[-1])
    mu1, sd1 = 100.0 * drift / lvl_w, 100.0 * s_d / lvl_w
    mu2, sd2 = 100.0 * drift / (lvl_w + drift), 100.0 * s_d / (lvl_w + drift)
    return mu1, sd1, mu2, sd2


# ---------------------------------------------------------------------------
# Fold-row assembly
# ---------------------------------------------------------------------------


def gaussian_row(zone, wall, horizon, model, truth, mu, sigma, note=""):
    q = {n: mu + norm.ppf(p) * sigma for n, p in zip(QNAMES, QLEVELS)}
    tq = float(norm.cdf((truth - mu) / sigma)) if np.isfinite(truth) else np.nan
    crps = ps.crps_gaussian(truth, mu, sigma) if np.isfinite(truth) else np.nan
    return {
        "zone": zone, "wall": wall, "horizon": horizon, "model": model,
        "truth": truth, "truth_quantile": tq, **q, "crps": crps,
        "covered_10_90": bool(q["p10"] <= truth <= q["p90"]) if np.isfinite(truth) else None,
        "covered_5_95": bool(q["p5"] <= truth <= q["p95"]) if np.isfinite(truth) else None,
        "band_width_10_90": q["p90"] - q["p10"],
        "seed": ps.SEED, "basis": BASIS, "notes": note,
    }


def sample_row(zone, wall, horizon, model, truth, samples, note=""):
    q = {n: float(np.quantile(samples, p)) for n, p in zip(QNAMES, QLEVELS)}
    tq = float((samples <= truth).mean()) if np.isfinite(truth) else np.nan
    crps = ps.crps_empirical(truth, samples) if np.isfinite(truth) else np.nan
    return {
        "zone": zone, "wall": wall, "horizon": horizon, "model": model,
        "truth": truth, "truth_quantile": tq, **q, "crps": crps,
        "covered_10_90": bool(q["p10"] <= truth <= q["p90"]) if np.isfinite(truth) else None,
        "covered_5_95": bool(q["p5"] <= truth <= q["p95"]) if np.isfinite(truth) else None,
        "band_width_10_90": q["p90"] - q["p10"],
        "seed": ps.SEED, "basis": BASIS, "notes": note,
    }


def append_experiments_row(rows: list[dict]) -> None:
    add = pd.DataFrame(rows)
    if EXPERIMENTS_CSV.exists():
        prior = pd.read_csv(EXPERIMENTS_CSV)
        add = pd.concat([prior, add], ignore_index=True)
    add.to_csv(EXPERIMENTS_CSV, index=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    t0 = time.time()
    print(f"=== Task 08-X probabilistic size-index MVE ===\nTRUTH BASIS: {BASIS}\nseed={ps.SEED} N={ps.N_PATHS}")

    load_hourly = pd.read_parquet(
        cfg.DERIVED_DIR / "load_hourly.parquet",
        columns=["weather_zone", "ts_local", "load_mw", "event_flag"],
    )
    zone_weather = pd.read_parquet(cfg.DERIVED_DIR / "zone_weather_hourly.parquet")

    # --- truth frames + reproduction check --------------------------------
    frames = {z: zone_frame(load_hourly, zone_weather, z) for z in cfg.ZONES}
    zc, wc, expect, tol = TRUTH_CHECK
    got, _ = matched_hour_growth(frames[zc], wc, wc + 1)
    print(f"truth reproduction check: {zc} wall-{wc} h1 = {got:+.2f}% (expected {expect:+.2f} ± {tol})")
    if not np.isfinite(got) or abs(got - expect) > tol:
        raise SystemExit("ABORT: matched-hour truth does not reproduce backtest.run_fold — fix before scoring")

    # --- component A: monthly canonical indices (writes parquets, asserts) -
    print("\n--- building monthly canonical size indices (4 walls x 3 zones) ---")
    monthly_indices = sim_m.build_all(WALLS)

    # --- jump units --------------------------------------------------------
    units, udiag = ps.load_jump_units()
    print(f"\njump units: {udiag['n_units']} rows usable | mw_source {udiag['mw_source_tally']} | "
          f"dropped: {udiag['n_unmapped_rows']} unmapped (expected_mw sum {udiag['unmapped_mw_expected']:.0f} MW), "
          f"{udiag['n_zone_out_of_scope']} zone-out-of-scope, {udiag['n_no_online_date']} no-online-date, "
          f"{udiag['n_no_mw']} no-usable-MW | default p_mat rows: {udiag['n_default_p_mat']}")

    sigma_b0 = pooled_b0_sigma()
    print(f"B0 pooled sigma (18 backtest_rolling growth errors, ddof=1): {sigma_b0:.3f} pp")

    daily = {z: si.build_daily(load_hourly, zone_weather, z) for z in cfg.ZONES}

    fold_rows: list[dict] = []
    sample_frames: list[pd.DataFrame] = []
    llt_flags: list[str] = []

    for zone in cfg.ZONES:
        for wall in WALLS:
            truth1, note1 = matched_hour_growth(frames[zone], wall, wall + 1)
            truth2, note2 = matched_hour_growth(frames[zone], wall + 1, wall + 2)

            # ---- Model P ----
            mi = monthly_indices[(zone, wall)]
            llt = ps.fit_llt(mi.monthly, zone, wall)
            if llt.slope_var_boundary:
                llt_flags.append(f"{zone} w{wall}: slope variance on zero boundary "
                                 f"(sigma2.trend={llt.params.get('sigma2.trend'):.3e})")
            llt_paths = ps.simulate_llt_paths(llt)
            jump_paths, jdiag = ps.simulate_jump_paths(units, zone, wall, mi.base_month_gwh)
            size_paths = llt_paths + jump_paths

            m = mi.monthly.copy()
            wall_vals = m.loc[pd.to_datetime(m["ym"]).dt.year == wall, "size_idx_m"]
            if len(wall_vals) != 12:
                raise ValueError(f"{zone} w{wall}: wall year has {len(wall_vals)} monthly values")
            level_wall = float(wall_vals.mean())

            g1, g2 = ps.paths_to_growth(size_paths, level_wall)
            p_note = (f"jump units in window: {jdiag['n_units_in_window']} "
                      f"({jdiag['mw_in_window']:.0f} MW)")
            if llt.slope_var_boundary:
                p_note += "; slope-var boundary"
            fold_rows.append(sample_row(zone, wall, 1, "P", truth1, g1, (note1 + "; " + p_note).strip("; ")))
            fold_rows.append(sample_row(zone, wall, 2, "P", truth2, g2, (note2 + "; " + p_note).strip("; ")))

            n = ps.N_PATHS
            sample_frames.append(pd.DataFrame({
                "zone": np.repeat(zone, n * ps.H_MONTHS),
                "wall": np.full(n * ps.H_MONTHS, wall, dtype=np.int32),
                "sample_id": np.repeat(np.arange(n, dtype=np.int32), ps.H_MONTHS),
                "horizon_month": np.tile(np.arange(1, ps.H_MONTHS + 1, dtype=np.int32), n),
                "size_idx": size_paths.astype(np.float32).ravel(),
                "llt_component": llt_paths.astype(np.float32).ravel(),
                "jump_component": jump_paths.astype(np.float32).ravel(),
            }))

            # ---- B0 ----
            annual = annual_at_wall(daily[zone], zone, wall)
            b0g1, b0g2 = b0_growth_points(annual, zone, wall)
            fold_rows.append(gaussian_row(zone, wall, 1, "B0", truth1, b0g1, sigma_b0, note1))
            fold_rows.append(gaussian_row(zone, wall, 2, "B0", truth2, b0g2, sigma_b0,
                                          (note2 + "; sigma=h1 pooled").strip("; ")))

            # ---- B1 ----
            mu1, sd1, mu2, sd2 = b1_growth_params(annual)
            fold_rows.append(gaussian_row(zone, wall, 1, "B1", truth1, mu1, sd1, note1))
            fold_rows.append(gaussian_row(zone, wall, 2, "B1", truth2, mu2, sd2, note2))

            print(f"{zone} w{wall}: truth h1 {truth1:+.2f}% | P p10/p50/p90 "
                  f"{np.quantile(g1, .1):+.2f}/{np.quantile(g1, .5):+.2f}/{np.quantile(g1, .9):+.2f} | "
                  f"B0 {b0g1:+.2f}±{sigma_b0:.2f} | B1 {mu1:+.2f}±{sd1:.2f} | {p_note}")

    folds = pd.DataFrame(fold_rows)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    folds.to_csv(FOLDS_CSV, index=False)
    samples = pd.concat(sample_frames, ignore_index=True)
    samples.to_parquet(SAMPLES_PARQUET, index=False)
    print(f"\nwrote {FOLDS_CSV} ({len(folds)} rows) and {SAMPLES_PARQUET} ({len(samples):,} rows)")
    if llt_flags:
        print("LLT boundary fits (admissible, recorded):\n  " + "\n  ".join(llt_flags))

    # --- pre-registered criteria, mechanical evaluation --------------------
    h1 = folds.loc[(folds["horizon"] == 1)]
    p1 = h1.loc[h1["model"] == "P"].set_index(["zone", "wall"])

    c1_row = p1.loc[("NCENT", 2024)]
    c1 = bool(c1_row["truth"] <= c1_row["p95"])
    cov = int(p1["covered_10_90"].sum())
    c2 = cov >= 8
    crps_mean = {m: float(h1.loc[h1["model"] == m, "crps"].mean()) for m in ("P", "B0", "B1")}
    c3 = crps_mean["P"] < crps_mean["B0"] and crps_mean["P"] < crps_mean["B1"]
    w_coast = float(p1.loc[("COAST", 2024), "band_width_10_90"])
    w_scent = float(p1.loc[("SCENT", 2024), "band_width_10_90"])
    c4 = (w_coast <= 5.0) and (w_scent <= 5.0)
    kill1 = not c1
    kill2 = c2 and (w_coast > 8.0 or w_scent > 8.0)

    print("\n=== pre-registered criteria (horizon 1, validate/backtest basis) ===")
    print(f"1. NCENT wall-2024 truth ({c1_row['truth']:+.2f}) <= P95 ({c1_row['p95']:+.2f}): {c1}")
    print(f"2. coverage truth in [P10,P90]: {cov}/12 (need >=8): {c2}")
    print(f"3. mean CRPS h1 — P {crps_mean['P']:.3f} vs B0 {crps_mean['B0']:.3f} vs B1 {crps_mean['B1']:.3f}: "
          f"P beats both = {c3}")
    print(f"4. wall-2024 P10-P90 width — COAST {w_coast:.2f} pp, SCENT {w_scent:.2f} pp (<=5.0 each): {c4}")
    if c1 and c2 and c3 and c4:
        verdict = "PROMOTE"
    elif kill1:
        verdict = "KILL (NCENT wall-2024 truth above P95 even with the jump layer)"
    elif kill2:
        verdict = "KILL (coverage bought only by >±4 pp bands)"
    elif c2 and not c3 and crps_mean["P"] >= crps_mean["B1"]:
        verdict = "ITERATE (coverage passes, CRPS loses to B1 — one damped-slope rerun allowed)"
    else:
        verdict = "STOP-AND-REPORT (failure pattern outside the pre-registered routes)"
    print(f"\nMECHANICAL VERDICT: {verdict}")

    # --- leaderboard rows ---------------------------------------------------
    knobs = {"p_mat": ps.P_MAT_BY_CONFIDENCE, "p_mat_default": ps.P_MAT_DEFAULT,
             "ramp_months": ps.RAMP_MONTHS_RANGE, "n_paths": ps.N_PATHS, "seed": ps.SEED,
             "sigma_b0": round(sigma_b0, 3)}
    ts = str(pd.Timestamp.now())
    lb = []
    for mdl in ("P", "B0", "B1"):
        hh = h1.loc[h1["model"] == mdl]
        lb.append({
            "zone": "ALL3", "wall_year": "2021-2024", "target_year": "h1",
            "status": "ok", "tag": f"task08x-{mdl}", "params": json.dumps(knobs) if mdl == "P" else "",
            "ts": ts,
            "crps_h1_mean": round(float(hh["crps"].mean()), 4),
            "coverage_10_90_h1": f"{int(hh['covered_10_90'].sum())}/12",
            "growth_err_pp": round(float((hh["p50"] - hh["truth"]).mean()), 2),
        })
    append_experiments_row(lb)
    print(f"appended 3 leaderboard rows to {EXPERIMENTS_CSV}")
    print(f"\ntotal {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
