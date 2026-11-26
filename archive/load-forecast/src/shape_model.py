"""Task 04: per-zone LightGBM shape model on per-unit hourly load.

Target: load_mw / size_idx[year]  (per-unit load in base-year-equivalent MW —
the absolute scale lives in the model output; scenarios re-scale by
size_idx[system_year]).

Hard rules enforced here (CLAUDE.md): NOTHING date-indexed in the features,
uri hours excluded from training, train wall ≤ TRAIN_END. Growth lives only
in size_idx.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg

MODEL_DIR = cfg.DERIVED_DIR / "models"

FEATURES = [
    "temp_f_popwt",
    "temp_f_avg24",
    "temp_f_ewm3d",
    "dewpoint_f_popwt",
    "hour",
    "month",
    "weekday",
    "holiday",
]

LGB_PARAMS = {
    "objective": "regression",
    "metric": "l2",
    "num_leaves": 63,
    "learning_rate": 0.05,
    "min_data_in_leaf": 50,
    "verbosity": -1,
    "seed": 7,
    # 8 GiB cgroup cap shared with IDE daemons — bound histogram memory.
    # A --loyo run at default threads pushed the container to 7.6/8.0 GiB.
    "num_threads": 4,
}
NUM_ROUNDS = 600


def calendar_features(ts_local: pd.Series) -> pd.DataFrame:
    """hour/month/weekday/holiday from the hour-ending label. The 'day' a row
    belongs to is (ts - 1h).date — he=24 stays on its own date."""
    day = (ts_local - pd.Timedelta(hours=1)).dt.normalize()
    hol = USFederalHolidayCalendar().holidays(start=day.min(), end=day.max())
    return pd.DataFrame(
        {
            "hour": ts_local.dt.hour,  # 0 == HE24
            "month": day.dt.month,
            "weekday": day.dt.dayofweek,
            "holiday": day.isin(hol).astype(int),
        },
        index=ts_local.index,
    )


def build_frame(
    load_hourly: pd.DataFrame, zone_weather_hourly: pd.DataFrame, size_index: pd.DataFrame, zone: str
) -> pd.DataFrame:
    """Merge one zone's load + weather + size_idx into a model frame with
    columns: ts_local, target_pu, event_flag, FEATURES."""
    ld = load_hourly.loc[load_hourly["weather_zone"] == zone, ["ts_local", "load_mw", "event_flag"]]
    wx = zone_weather_hourly.loc[
        zone_weather_hourly["weather_zone"] == zone,
        ["ts_local", "temp_f_popwt", "dewpoint_f_popwt", "temp_f_avg24", "temp_f_ewm3d"],
    ]
    df = ld.merge(wx, on="ts_local", how="inner")
    n_unmatched = len(ld) - len(df)
    if n_unmatched:
        print(f"[{zone}] build_frame: {n_unmatched:,} load hours had no weather match — dropped")
    # year attribution via (ts − 1h) so HE24 of Dec 31 gets ITS OWN year's
    # size_idx, not the next year's (which past the wall is extrapolated)
    year = (df["ts_local"] - pd.Timedelta(hours=1)).dt.year
    idx = size_index.loc[size_index["weather_zone"] == zone].set_index("year")["size_idx"]
    df["size_idx"] = year.map(idx)
    n_before = len(df)
    df = df.dropna(subset=["load_mw", "size_idx", "temp_f_popwt"])
    if len(df) < n_before:
        print(f"[{zone}] build_frame: {n_before - len(df):,} rows dropped for NaN load/idx/temp")
    df["target_pu"] = df["load_mw"] / df["size_idx"]
    df = pd.concat([df, calendar_features(df["ts_local"])], axis=1)
    return df[["ts_local", "target_pu", "event_flag"] + FEATURES].reset_index(drop=True)


def _train_mask(df: pd.DataFrame, train_end: str | None = None) -> pd.Series:
    """Train wall + event exclusion. The wall compares the (ts − 1h) DAY so all
    24 hours of Dec 31 of the wall year stay in training (a raw ts_local
    comparison silently drops that whole day: HE1 of Dec 31 is labeled 01:00,
    which is > '2024-12-31' parsed as midnight). uri and outage hours are
    excluded; covid stays at normal weight in the shape fit (CLAUDE.md rule 3).
    """
    day = (df["ts_local"] - pd.Timedelta(hours=1)).dt.normalize()
    flags = df["event_flag"].fillna("")
    return (day <= (train_end or cfg.TRAIN_END)) & ~flags.isin(["uri", "outage"])


def train_zone(
    frame: pd.DataFrame,
    num_rounds: int = NUM_ROUNDS,
    train_end: str | None = None,
    params: dict | None = None,
) -> lgb.Booster:
    df = frame.loc[_train_mask(frame, train_end=train_end)]
    dtrain = lgb.Dataset(df[FEATURES], label=df["target_pu"])
    return lgb.train(params or LGB_PARAMS, dtrain, num_boost_round=num_rounds)


def loyo_mape(frame: pd.DataFrame, num_rounds: int = NUM_ROUNDS) -> pd.DataFrame:
    """Leave-one-year-out CV inside the train window. Returns year, mape, n."""
    df = frame.loc[_train_mask(frame)].copy()
    df["year"] = df["ts_local"].dt.year
    rows = []
    for year in sorted(df["year"].unique()):
        tr, te = df.loc[df["year"] != year], df.loc[df["year"] == year]
        booster = lgb.train(LGB_PARAMS, lgb.Dataset(tr[FEATURES], label=tr["target_pu"]), num_boost_round=num_rounds)
        pred = booster.predict(te[FEATURES])
        mape = float(np.mean(np.abs(pred - te["target_pu"]) / te["target_pu"]))
        rows.append({"year": int(year), "mape": mape, "n": len(te)})
    return pd.DataFrame(rows)


def check_monotone_above(
    booster: lgb.Booster, frame: pd.DataFrame, temp_from: float = 78.0
) -> tuple[bool, pd.DataFrame]:
    """Task 04 acceptance: partial dependence on temp must be monotone
    non-decreasing above ~78°F. Sweeps a hot-spell temperature (spot + avg24 +
    ewm3d moved together) over a fixed row sample; small numeric wiggle
    (<0.1% of level) is tolerated."""
    sample = frame[FEATURES].sample(n=min(2000, len(frame)), random_state=0).copy()
    grid = np.arange(temp_from, 107.0, 2.0)
    means = []
    for t in grid:
        s = sample.copy()
        s["temp_f_popwt"] = t
        s["temp_f_avg24"] = t
        s["temp_f_ewm3d"] = t
        means.append(float(booster.predict(s[FEATURES]).mean()))
    pd_curve = pd.DataFrame({"temp_f": grid, "pred_pu_mean": means})
    tol = 0.001 * float(np.mean(means))
    ok = bool((np.diff(means) >= -tol).all())
    return ok, pd_curve


def save_model(booster: lgb.Booster, zone: str, meta: dict | None = None) -> Path:
    """Persist model + version manifest (features, params, rounds, data span)."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    path = MODEL_DIR / f"shape_{zone}.txt"
    booster.save_model(str(path))
    manifest = {"features": FEATURES, "params": LGB_PARAMS, "num_rounds": NUM_ROUNDS}
    manifest.update(meta or {})
    (MODEL_DIR / f"shape_{zone}_features.json").write_text(json.dumps(manifest, default=str))
    return path


def load_model(zone: str) -> lgb.Booster:
    path = MODEL_DIR / f"shape_{zone}.txt"
    manifest = json.loads((MODEL_DIR / f"shape_{zone}_features.json").read_text())
    saved = manifest["features"] if isinstance(manifest, dict) else manifest
    if saved != FEATURES:
        raise ValueError(f"{zone}: saved feature list {saved} != current {FEATURES} — retrain")
    return lgb.Booster(model_file=str(path))


def predict_per_unit(booster: lgb.Booster, feature_frame: pd.DataFrame) -> np.ndarray:
    return booster.predict(feature_frame[FEATURES])
