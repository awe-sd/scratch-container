"""Fast experiment harness: one rolling-origin fold, <5 min, leaderboard CSV.

The iteration loop for model settings: run with overridden LightGBM params (or
--rounds), get scored on a genuinely out-of-sample year, and append to
output/experiments.csv. Improvements found here get promoted to the full model
via --promote (writes params/shape_lgb.json, which train_all.py --params reads).

Default fold: wall 2022 → target 2023 (the record summer — the hardest honest
test we have). Deterministic (fixed seed), memory-capped (num_threads=4).

Examples:
  uv run python load-forecast/scripts/experiment.py --tag baseline
  uv run python load-forecast/scripts/experiment.py --num-leaves 127 --learning-rate 0.03 --rounds 900 --tag deeper
  uv run python load-forecast/scripts/experiment.py --best          # show leaderboard
  uv run python load-forecast/scripts/experiment.py --promote <tag> # write params file
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import backtest as bt
import config as cfg
import shape_model as sm
import size_index as si

EXPERIMENTS_CSV = cfg.PROJECT_ROOT / "output" / "experiments.csv"
PARAMS_FILE = cfg.PROJECT_ROOT / "params" / "shape_lgb.json"


def run_experiment(
    zones: list[str], wall: int, params: dict, rounds: int, tag: str,
    n_fit_years: int | None = None,
) -> pd.DataFrame:
    load_hourly = pd.read_parquet(
        cfg.DERIVED_DIR / "load_hourly.parquet",
        columns=["weather_zone", "ts_local", "load_mw", "event_flag"],
    )
    zone_weather = pd.read_parquet(cfg.DERIVED_DIR / "zone_weather_hourly.parquet")
    rows = []
    for zone in zones:
        daily = si.build_daily(load_hourly, zone_weather, zone)
        r = bt.run_fold(zone, wall, load_hourly, zone_weather, daily,
                        params=params, num_rounds=rounds, n_fit_years=n_fit_years)
        r.update({"tag": tag, "params": json.dumps(params), "rounds": rounds,
                  "n_fit_years": n_fit_years if n_fit_years is not None else "per-zone",
                  "ts": str(pd.Timestamp.now())})
        rows.append(r)
        print(r)
    return pd.DataFrame(rows)


def append_leaderboard(result: pd.DataFrame) -> None:
    EXPERIMENTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    if EXPERIMENTS_CSV.exists():
        prior = pd.read_csv(EXPERIMENTS_CSV)
        result = pd.concat([prior, result], ignore_index=True)
    result.to_csv(EXPERIMENTS_CSV, index=False)


def show_best(zone_filter: str | None = None) -> None:
    if not EXPERIMENTS_CSV.exists():
        print("no experiments yet")
        return
    df = pd.read_csv(EXPERIMENTS_CSV)
    df = df.loc[df["status"] == "ok"]
    if zone_filter:
        df = df.loc[df["zone"] == zone_filter]
    cols = ["ts", "tag", "zone", "wall_year", "monthly_mape_pct", "annual_err_pct",
            "growth_err_pp", "hourly_mape_pct", "runtime_s"]
    print(df.sort_values("monthly_mape_pct")[cols].head(15).to_string(index=False))


def promote(tag: str) -> None:
    df = pd.read_csv(EXPERIMENTS_CSV)
    match = df.loc[(df["tag"] == tag) & (df["status"] == "ok")]
    if match.empty:
        raise SystemExit(f"no successful experiment tagged {tag!r}")
    params = json.loads(match.iloc[-1]["params"])
    rounds = int(match.iloc[-1]["rounds"])
    PARAMS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PARAMS_FILE.write_text(json.dumps({"params": params, "num_rounds": rounds}, indent=2))
    print(f"promoted {tag!r} → {PARAMS_FILE}\n{PARAMS_FILE.read_text()}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zones", nargs="+", default=["NCENT"], choices=cfg.ZONES,
                    help="default NCENT only, for speed; pass all three to confirm a winner")
    ap.add_argument("--wall", type=int, default=2022, help="train ≤wall, score wall+1")
    ap.add_argument("--rounds", type=int, default=sm.NUM_ROUNDS)
    ap.add_argument("--num-leaves", type=int)
    ap.add_argument("--learning-rate", type=float)
    ap.add_argument("--min-data-in-leaf", type=int)
    ap.add_argument("--n-fit-years", type=int, default=None,
                    help="size-index extrapolation window override; default = per-zone cfg.SIZE_EXTRAP_YEARS")
    ap.add_argument("--tag", default="untagged")
    ap.add_argument("--best", action="store_true", help="print leaderboard and exit")
    ap.add_argument("--promote", metavar="TAG", help="write TAG's params to params/shape_lgb.json")
    args = ap.parse_args()

    if args.best:
        show_best()
        return
    if args.promote:
        promote(args.promote)
        return

    params = dict(sm.LGB_PARAMS)
    for key in ("num_leaves", "learning_rate", "min_data_in_leaf"):
        v = getattr(args, key)
        if v is not None:
            params[key] = v

    t0 = time.time()
    result = run_experiment(args.zones, args.wall, params, args.rounds, args.tag,
                             n_fit_years=args.n_fit_years)
    append_leaderboard(result)
    print(f"\ntotal {time.time() - t0:.0f}s → appended to {EXPERIMENTS_CSV}")
    show_best()


if __name__ == "__main__":
    main()
