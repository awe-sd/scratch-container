"""Train everything: size index (Task 03) + shape models (Task 04), all zones.

Prereqs on disk: data/derived/load_hourly.parquet, zone_weather_hourly.parquet.
Outputs: size_index.parquet, models/shape_{zone}.txt, LOYO CV report printed.

Run:  uv run python load-forecast/scripts/train_all.py [--loyo]
"""
from __future__ import annotations

import argparse
import gc
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import config as cfg
import shape_model as sm
import size_index as si


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--loyo", action="store_true", help="run leave-one-year-out CV (slow)")
    args = ap.parse_args()

    load_hourly = pd.read_parquet(cfg.DERIVED_DIR / "load_hourly.parquet")
    zone_weather = pd.read_parquet(cfg.DERIVED_DIR / "zone_weather_hourly.parquet")

    # ---- Task 03: size index -------------------------------------------------
    daily_by_zone = {}
    for zone in cfg.ZONES:
        daily = si.build_daily(load_hourly, zone_weather, zone)
        daily_by_zone[zone] = daily

    size_index, diag = si.build_size_index(daily_by_zone, through_year=2028)
    for zone in cfg.ZONES:
        z = size_index[size_index["weather_zone"] == zone]
        r2 = diag[zone]["r2"]
        flag = "OK" if r2 >= 0.85 else "BELOW 0.85 TARGET"
        print(f"[{zone}] size-index daily R²={r2:.3f} ({flag}), {diag[zone]['n_days']} fit days")
        print(z[["year", "normalized_gwh", "size_idx", "source"]].round(3).to_string(index=False))

    # ---- Task 04: shape models -----------------------------------------------
    for zone in cfg.ZONES:
        frame = sm.build_frame(load_hourly, zone_weather, size_index, zone)
        n_train = int(sm._train_mask(frame).sum())
        print(f"\n[{zone}] shape frame: {len(frame):,} rows, {n_train:,} trainable")
        if args.loyo:
            cv = sm.loyo_mape(frame)
            cv["ok"] = cv["mape"] <= 0.05
            print(cv.assign(mape_pct=(100 * cv["mape"]).round(2))[
                ["year", "mape_pct", "n", "ok"]].to_string(index=False))
            worst = cv["mape"].max()
            print(f"[{zone}] LOYO worst-year MAPE {100 * worst:.2f}% (target ≤5%)")
            print("       note: LOYO validates SHAPE only — the year's level is divided "
                  "out of its own target; the level gate is validate.py's 2025-26 wall test")
        booster = sm.train_zone(frame)
        mono_ok, pd_curve = sm.check_monotone_above(booster, frame.loc[sm._train_mask(frame)])
        status = "OK" if mono_ok else "FAIL — REVIEW BEFORE USE"
        print(f"[{zone}] temp partial-dependence monotone above 78°F: {status}")
        if not mono_ok:
            print(pd_curve.round(1).to_string(index=False))
        span = f"{frame['ts_local'].min()}..{frame['ts_local'].max()}"
        path = sm.save_model(
            booster, zone,
            meta={"data_span": span, "trained_at": str(pd.Timestamp.now()), "monotone_ok": mono_ok},
        )
        print(f"[{zone}] saved {path}")
        del frame, booster
        gc.collect()  # 8 GiB cgroup cap — don't stack zone frames

    print("\ntraining complete — next: uv run python load-forecast/src/validate.py")


if __name__ == "__main__":
    main()
