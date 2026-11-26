"""Synthetic tests for the shape model: learns weather response, excludes uri,
holds the no-date-features rule."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import config as cfg
import shape_model as sm


def synthetic_world(start="2019-01-01", end="2023-12-31", seed=11):
    """Hourly load/weather where per-unit load is a pure function of
    weather+calendar and growth is a per-year multiplier (the size_idx)."""
    rng = np.random.default_rng(seed)
    ts = pd.date_range(start, end, freq="h") + pd.Timedelta(hours=1)  # hour-ending
    doy = (ts - pd.Timedelta(hours=1)).dayofyear.to_numpy()
    hod = ts.hour.to_numpy()
    temp = (
        68
        + 22 * np.sin(2 * np.pi * (doy - 105) / 365.25)
        + 8 * np.sin(2 * np.pi * (hod - 15) / 24)
        + rng.normal(0, 1.5, len(ts))
    )
    dew = temp - 12 + rng.normal(0, 2, len(ts))
    wx = pd.DataFrame({"weather_zone": "NCENT", "ts_local": ts, "temp_f_popwt": temp, "dewpoint_f_popwt": dew})
    wx["temp_f_avg24"] = wx["temp_f_popwt"].rolling(24, min_periods=1).mean()
    wx["temp_f_ewm3d"] = wx["temp_f_popwt"].ewm(halflife=36).mean()

    per_unit = (
        14000
        + 260 * np.maximum(temp - 65, 0)
        + 90 * np.maximum(45 - temp, 0)
        + 1500 * np.sin(2 * np.pi * (hod - 17) / 24)
    )
    years = ts.year.to_numpy()
    size = {2019: 1.0, 2020: 1.03, 2021: 1.06, 2022: 1.10, 2023: 1.145}
    idx = np.vectorize(size.get)(years)
    load = per_unit * idx + rng.normal(0, 120, len(ts))
    ld = pd.DataFrame(
        {
            "weather_zone": "NCENT",
            "ts_local": ts,
            "load_mw": load,
            "event_flag": pd.array([pd.NA] * len(ts), dtype="string"),
        }
    )
    # day membership via (ts − 1h), matching pull_load.event_flag
    d = (ld["ts_local"] - pd.Timedelta(hours=1)).dt.strftime("%Y-%m-%d")
    ld.loc[(d >= cfg.URI_WINDOW[0]) & (d <= cfg.URI_WINDOW[1]), "event_flag"] = "uri"
    size_index = pd.DataFrame(
        {"weather_zone": "NCENT", "year": list(size), "size_idx": list(size.values())}
    )
    return ld, wx, size_index


def test_no_date_features():
    banned = {"year", "date", "trend", "ts", "doy", "dayofyear"}
    assert not banned & set(sm.FEATURES)


def test_frame_excludes_uri_from_training_and_learns_weather():
    ld, wx, size_index = synthetic_world()
    frame = sm.build_frame(ld, wx, size_index, "NCENT")
    # uri hours present in the frame but masked out of training
    assert (frame["event_flag"] == "uri").sum() == 11 * 24
    mask = sm._train_mask(frame)
    assert not (frame.loc[mask, "event_flag"] == "uri").any()

    # train on ≤2022, score 2023 (within train wall so mask keeps it, so
    # emulate the holdout manually)
    tr = frame.loc[mask & (frame["ts_local"] < "2023-01-01")]
    te = frame.loc[frame["ts_local"] >= "2023-01-01"]
    import lightgbm as lgb

    booster = lgb.train(
        sm.LGB_PARAMS, lgb.Dataset(tr[sm.FEATURES], label=tr["target_pu"]), num_boost_round=300
    )
    pred = sm.predict_per_unit(booster, te)
    mape = float(np.mean(np.abs(pred - te["target_pu"]) / te["target_pu"]))
    assert mape < 0.02  # synthetic world is nearly noiseless — model must nail it


def test_per_unit_target_removes_growth():
    ld, wx, size_index = synthetic_world()
    frame = sm.build_frame(ld, wx, size_index, "NCENT")
    yearly = frame.groupby(frame["ts_local"].dt.year)["target_pu"].mean()
    # per-unit means should be flat across years (growth divided out)
    assert yearly.max() / yearly.min() < 1.01


def test_train_wall_keeps_all_of_dec31_and_drops_jan1():
    ts = pd.date_range("2024-12-31 01:00", "2025-01-01 02:00", freq="h")
    df = pd.DataFrame(
        {"ts_local": ts, "event_flag": pd.array([pd.NA] * len(ts), dtype="string")}
    )
    mask = sm._train_mask(df)
    # HE1..HE24 of Dec 31 (ts 01:00..next-day 00:00) all kept
    assert mask.iloc[:24].all()
    # HE1+ of Jan 1 dropped
    assert not mask.iloc[24:].any()


def test_outage_hours_excluded_from_training():
    ts = pd.date_range("2024-07-10 01:00", periods=5, freq="h")
    df = pd.DataFrame({"ts_local": ts, "event_flag": pd.array(["outage"] * 5, dtype="string")})
    assert not sm._train_mask(df).any()


def test_monotone_check_runs_and_passes_on_learned_world():
    ld, wx, size_index = synthetic_world(end="2020-12-31")
    frame = sm.build_frame(ld, wx, size_index, "NCENT")
    booster = sm.train_zone(frame, num_rounds=150)
    ok, curve = sm.check_monotone_above(booster, frame)
    assert ok  # synthetic cooling response is strictly increasing above 65°F
    assert len(curve) > 10


def test_save_load_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(sm, "MODEL_DIR", tmp_path)
    ld, wx, size_index = synthetic_world(end="2020-12-31")
    frame = sm.build_frame(ld, wx, size_index, "NCENT")
    booster = sm.train_zone(frame, num_rounds=50)
    sm.save_model(booster, "NCENT")
    again = sm.load_model("NCENT")
    a = sm.predict_per_unit(booster, frame.head(100))
    b = sm.predict_per_unit(again, frame.head(100))
    np.testing.assert_allclose(a, b, rtol=1e-12)
