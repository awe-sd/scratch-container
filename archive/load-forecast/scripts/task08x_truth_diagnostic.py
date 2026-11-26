"""Task 08-X POST-HOC TRUTH DIAGNOSTIC — does NOT alter the pre-registered run.

The first scored run (tag task08x, pre-registered truth = verbatim
backtest.run_fold actual_growth reproduction) printed truth values the repo's
own training log flags as not-quotable levels: run_fold's growth is
calendar-ASYMMETRIC when the BASE year contains uri/outage exclusions (the
base loses those hours, the target keeps the same calendar hours -> inflated
ratio; e.g. COAST wall-2024 'truth' +10.71%). run_fold is internally valid for
ERRORS (pred and actual share the asymmetry) but not as a truth LEVEL.

This script recomputes the fold scorecard under two corrected truth variants,
for sdalvi to rule on before any re-run:
  truth_sym  — SYMMETRIC matched hours: (month,day,hour) key intersection of
               both years' scoreable sets (the validate.py post-round-3 fix).
               Still raw load, so the year-pair weather delta remains.
  truth_norm — weather-normalized realized growth: annual size fit THROUGH the
               target year (train_end = target-12-31), y/y of normalized_gwh.
               No weather wedge; this is what a size-index forecast actually
               predicts. (Related to the banned rule-sweep basis — labeled
               explicitly, quoted only as a diagnostic.)

Output: output/task08x_truth_diagnostic.csv + printed criteria re-reads.
Run: uv run python load-forecast/scripts/task08x_truth_diagnostic.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import config as cfg  # noqa: E402
import prob_size as ps  # noqa: E402
import size_index as si  # noqa: E402
from truth_bases import normalized_growth, symmetric_growth, zone_frame  # noqa: E402

OUTPUT_DIR = cfg.PROJECT_ROOT / "output"
WALLS = (2021, 2022, 2023, 2024)


def main() -> None:
    folds = pd.read_csv(OUTPUT_DIR / "task08x_folds.csv")
    samples = pd.read_parquet(OUTPUT_DIR / "task08x_samples.parquet")

    load_hourly = pd.read_parquet(
        cfg.DERIVED_DIR / "load_hourly.parquet",
        columns=["weather_zone", "ts_local", "load_mw", "event_flag"],
    )
    zone_weather = pd.read_parquet(cfg.DERIVED_DIR / "zone_weather_hourly.parquet")
    frames = {z: zone_frame(load_hourly, zone_weather, z) for z in cfg.ZONES}
    daily = {z: si.build_daily(load_hourly, zone_weather, z) for z in cfg.ZONES}

    # P growth samples per fold, reconstructed from the persisted paths
    p_growth: dict[tuple[str, int, int], np.ndarray] = {}
    for (zone, wall), g in samples.groupby(["zone", "wall"]):
        mi = pd.read_parquet(cfg.DERIVED_DIR / f"size_index_monthly_w{wall}.parquet")
        mvals = mi.loc[(mi["zone"] == zone) & (pd.to_datetime(mi["ym"]).dt.year == wall), "size_idx_m"]
        level_wall = float(mvals.mean())
        wide = g.pivot(index="sample_id", columns="horizon_month", values="size_idx")
        paths = wide.sort_index()[list(range(1, 25))].to_numpy(dtype=float)
        g1, g2 = ps.paths_to_growth(paths, level_wall)
        p_growth[(zone, int(wall), 1)] = g1
        p_growth[(zone, int(wall), 2)] = g2

    rows = []
    for zone in cfg.ZONES:
        for wall in WALLS:
            for h in (1, 2):
                base_y, tgt_y = wall + h - 1, wall + h
                t_sym = symmetric_growth(frames[zone], base_y, tgt_y)
                t_norm = normalized_growth(daily[zone], zone, tgt_y)
                for model in ("P", "B0", "B1"):
                    fr = folds.loc[(folds["zone"] == zone) & (folds["wall"] == wall)
                                   & (folds["horizon"] == h) & (folds["model"] == model)].iloc[0]
                    rec = {"zone": zone, "wall": wall, "horizon": h, "model": model,
                           "truth_prereg": fr["truth"], "truth_sym": t_sym, "truth_norm": t_norm,
                           "p10": fr["p10"], "p50": fr["p50"], "p90": fr["p90"], "p95": fr["p95"],
                           "band_width_10_90": fr["band_width_10_90"]}
                    for tag, tv in (("sym", t_sym), ("norm", t_norm)):
                        if not np.isfinite(tv):
                            rec[f"covered_10_90_{tag}"] = None
                            rec[f"crps_{tag}"] = np.nan
                            continue
                        rec[f"covered_10_90_{tag}"] = bool(fr["p10"] <= tv <= fr["p90"])
                        if model == "P":
                            rec[f"crps_{tag}"] = ps.crps_empirical(tv, p_growth[(zone, wall, h)])
                        else:
                            mu = fr["p50"]
                            sigma = (fr["p90"] - fr["p10"]) / (2 * 1.2815515655446004)
                            rec[f"crps_{tag}"] = ps.crps_gaussian(tv, mu, sigma)
                    rows.append(rec)

    out = pd.DataFrame(rows)
    path = OUTPUT_DIR / "task08x_truth_diagnostic.csv"
    out.to_csv(path, index=False)
    print(f"wrote {path}\n")

    h1 = out.loc[out["horizon"] == 1]
    print("truth variants, horizon 1 (prereg = pre-registered run_fold reproduction):")
    tt = h1.loc[h1["model"] == "P", ["zone", "wall", "truth_prereg", "truth_sym", "truth_norm",
                                     "p10", "p50", "p90", "p95"]].round(2)
    print(tt.to_string(index=False))

    for tag in ("sym", "norm"):
        p1 = h1.loc[h1["model"] == "P"].set_index(["zone", "wall"])
        c1r = p1.loc[("NCENT", 2024)]
        tv = c1r[f"truth_{tag}"]
        c1 = bool(tv <= c1r["p95"])
        cov = int(p1[f"covered_10_90_{tag}"].sum())
        crps = {m: float(h1.loc[h1["model"] == m, f"crps_{tag}"].mean()) for m in ("P", "B0", "B1")}
        print(f"\n--- criteria re-read under truth_{tag} (POST-HOC DIAGNOSTIC, not the "
              f"pre-registered result) ---")
        print(f"1. NCENT w2024 truth ({tv:+.2f}) <= P95 ({c1r['p95']:+.2f}): {c1}")
        print(f"2. coverage [P10,P90]: {cov}/12 (need >=8)")
        print(f"3. mean CRPS h1 — P {crps['P']:.3f} | B0 {crps['B0']:.3f} | B1 {crps['B1']:.3f} "
              f"-> P beats both: {crps['P'] < crps['B0'] and crps['P'] < crps['B1']}")


if __name__ == "__main__":
    main()
