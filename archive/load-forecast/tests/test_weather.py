"""Synthetic-frame tests for the weather half of Task 02: UTC→CPT hour-ending
labels (both DST transitions), QC bounds, gap interpolation, zone feature math.
No network access anywhere in here."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pull_weather as pw
import zone_weather as zw


def make_obs(ts_utc, temps, dews=None, reports=None) -> pd.DataFrame:
    ts = pd.to_datetime(list(ts_utc), utc=True)
    temps = [np.nan if t is None else float(t) for t in temps]
    if dews is None:
        dews = [t - 10.0 if not np.isnan(t) else np.nan for t in temps]
    if reports is None:
        reports = ["FM-15"] * len(ts)
    return pd.DataFrame(
        {"ts_utc": ts, "report_type": reports, "temp_f": temps, "dewpoint_f": dews}
    )


def grid(start: str, end: str) -> pd.DatetimeIndex:
    return pd.date_range(start, end, freq="h", tz="UTC")


# ---------------------------------------------------------------- timezone ---

def test_hour_ending_conversion_normal():
    # Obs 19:53Z = 14:53 CDT covers local 14:00–15:00 → ts_local 15:00 (naive).
    obs = make_obs(["2023-08-01 19:53"], [100.0])
    out = pw.process_observations(obs, grid("2023-08-01 20:00", "2023-08-01 20:00"))
    assert list(out["ts_local"]) == [pd.Timestamp("2023-08-01 15:00")]
    assert out["ts_local"].dt.tz is None
    assert out.loc[0, "temp_f"] == 100.0
    assert out.loc[0, "qc_flag"] == "raw"


def test_fallback_duplicated_hour_keeps_first():
    # 2023-11-05: 02:00 CDT → 01:00 CST at 07:00Z. Two physical hours label
    # 02:00 local; keep the FIRST (the CDT hour, obs 06:53Z temp=52).
    ts = [f"2023-11-05 {h:02d}:53" for h in range(4, 10)]
    obs = make_obs(ts, [50, 51, 52, 53, 54, 55])
    out = pw.process_observations(obs, grid("2023-11-05 05:00", "2023-11-05 10:00"))
    labels = [t.strftime("%H:%M") for t in out["ts_local"]]
    assert labels == ["00:00", "01:00", "02:00", "03:00", "04:00"]  # 6 UTC hours → 5 rows
    two = out[out["ts_local"] == pd.Timestamp("2023-11-05 02:00")]
    assert len(two) == 1
    assert two["temp_f"].iloc[0] == 52.0  # first (CDT) hour kept, CST hour dropped
    assert (out["qc_flag"] == "raw").all()


def test_springforward_gap_absent_not_interpolated():
    # 2023-03-12: 02:00 CST → 03:00 CDT at 08:00Z. Label 03:00 never exists
    # (matches ercotLoadView: he=3 absent that day) and nothing is interpolated
    # across the jump — every row stays 'raw'.
    ts = [f"2023-03-12 {h:02d}:53" for h in range(5, 11)]
    obs = make_obs(ts, [60, 61, 62, 63, 64, 65])
    out = pw.process_observations(obs, grid("2023-03-12 06:00", "2023-03-12 11:00"))
    labels = [t.strftime("%H:%M") for t in out["ts_local"]]
    assert labels == ["00:00", "01:00", "02:00", "04:00", "05:00", "06:00"]
    assert pd.Timestamp("2023-03-12 03:00") not in set(out["ts_local"])
    assert len(out) == 6  # no physical hour lost, none fabricated
    assert (out["qc_flag"] == "raw").all()
    # the hour ending at the transition instant carries label 02:00 (ERCOT he=2)
    assert out.loc[out["ts_local"] == pd.Timestamp("2023-03-12 02:00"), "temp_f"].iloc[0] == 62.0


# ---------------------------------------------------------------------- QC ---

def test_qc_physical_bounds():
    obs = make_obs(
        ["2023-06-01 00:53", "2023-06-01 01:53", "2023-06-01 02:53",
         "2023-06-01 03:53", "2023-06-01 04:53"],
        [135.0, -40.0, 70.0, 70.0, 70.0],
        dews=[60.0, -50.0, 80.0, 72.9, -45.0],
    )
    q = pw.qc_physical(obs)
    assert np.isnan(q.loc[0, "temp_f"])          # > 130 °F impossible
    assert q.loc[0, "dewpoint_f"] == 60.0        # dew in bounds; no temp to cross-check
    assert np.isnan(q.loc[1, "temp_f"])          # < −30 °F impossible
    assert np.isnan(q.loc[1, "dewpoint_f"])      # < −30 °F impossible
    assert np.isnan(q.loc[2, "dewpoint_f"])      # 80 > 70 + 3 supersaturation
    assert q.loc[2, "temp_f"] == 70.0            # temp itself kept
    assert q.loc[3, "dewpoint_f"] == 72.9        # within the +3 °F slack
    assert np.isnan(q.loc[4, "dewpoint_f"])      # below absolute bound


def test_element_parsing_scaled_c_missing_and_qc_codes():
    s = pd.Series(["+0261,1", "+9999,9", "-0050,3", "+0000,5"])
    got = pw._element_to_f(s)
    assert got[0] == pytest.approx(78.98)   # 26.1 °C
    assert np.isnan(got[1])                 # +9999 missing sentinel
    assert np.isnan(got[2])                 # QC code 3 = erroneous
    assert got[3] == pytest.approx(32.0)    # 0.0 °C


def test_report_type_preference_and_summary_exclusion():
    # Hour 1: SOD summary (excluded), FM-16 nearer the top of hour, FM-15
    # farther — the FM-15 must still win. Hour 2: ONLY an SOD → the hour must
    # come out empty (suspect), proving summaries are truly excluded.
    obs = make_obs(
        ["2023-08-01 19:59", "2023-08-01 19:35", "2023-08-01 19:53", "2023-08-01 20:30"],
        [120.0, 88.0, 77.0, 90.0],
        dews=[10.0, 60.0, 60.0, 60.0],
        reports=["SOD", "FM-16", "FM-15", "SOD"],
    )
    out = pw.process_observations(obs, grid("2023-08-01 20:00", "2023-08-01 21:00"))
    assert len(out) == 2
    assert out.loc[0, "temp_f"] == 77.0          # FM-15 beats nearer FM-16; SOD ignored
    assert np.isnan(out.loc[1, "temp_f"])        # SOD-only hour stays empty
    assert out.loc[1, "qc_flag"] == "suspect"


# ------------------------------------------------------------ interpolation ---

def test_interp_le_3h_flagged_longer_gaps_suspect():
    g = grid("2023-06-01 01:00", "2023-06-02 00:00")  # 24 hour-ending labels
    temps = {he: float(i + 1) for i, he in enumerate(g)}  # 1..24, linear
    missing = set(list(g[5:7]) + list(g[11:16]))  # 2h gap (he 6,7), 5h gap (he 12..16)
    keep = [he for he in g if he not in missing]
    obs = make_obs([he - pd.Timedelta(minutes=7) for he in keep], [temps[he] for he in keep])
    out = pw.process_observations(obs, g).set_index("ts_local")

    short = [pd.Timestamp("2023-06-01 01:00"), pd.Timestamp("2023-06-01 02:00")]  # he 6,7 UTC → CDT −5
    for t, want in zip(short, [6.0, 7.0]):
        assert out.loc[t, "temp_f"] == pytest.approx(want)  # exact linear fill
        assert out.loc[t, "qc_flag"] == "interp"

    long = [pd.Timestamp("2023-06-01 07:00") + pd.Timedelta(hours=k) for k in range(5)]  # he 12..16
    for t in long:
        assert np.isnan(out.loc[t, "temp_f"])
        assert out.loc[t, "qc_flag"] == "suspect"

    rest = out.drop(index=short + long)
    assert (rest["qc_flag"] == "raw").all()
    assert rest["temp_f"].notna().all()


def test_edge_gap_not_interpolated_without_anchor():
    g = grid("2023-06-01 01:00", "2023-06-01 06:00")
    obs = make_obs(["2023-06-01 03:53", "2023-06-01 04:53", "2023-06-01 05:53"], [10, 11, 12])
    out = pw.process_observations(obs, g)
    # first three grid hours have no left anchor → stay suspect even though ≤3h
    assert out["qc_flag"].tolist() == ["suspect", "suspect", "suspect", "raw", "raw", "raw"]
    assert out["temp_f"].isna().tolist() == [True, True, True, False, False, False]


# ------------------------------------------------------------ zone features ---

def test_zone_feature_math_avg24_and_ewm36():
    n = 48
    z = pd.DataFrame(
        {
            "weather_zone": "NCENT",
            "ts_local": pd.date_range("2023-06-01 01:00", periods=n, freq="h"),
            "temp_f_popwt": np.arange(n, dtype=float),
            "dewpoint_f_popwt": np.zeros(n),
        }
    )
    out = zw.add_zone_features(z)
    assert np.isnan(out.loc[22, "temp_f_avg24"])                      # <24 rows
    assert out.loc[23, "temp_f_avg24"] == pytest.approx(np.mean(np.arange(24)))
    assert out.loc[24, "temp_f_avg24"] == pytest.approx(np.mean(np.arange(1, 25)))

    # adjusted EWM with halflife 36 rows: decay = 0.5 ** (1/36)
    decay = 0.5 ** (1.0 / 36.0)
    x = np.arange(n, dtype=float)
    for t in [0, 1, 10, 47]:
        wts = decay ** np.arange(t, -1, -1)
        expect = float(np.dot(wts, x[: t + 1]) / wts.sum())
        assert out.loc[t, "temp_f_ewm3d"] == pytest.approx(expect, rel=1e-9)


def test_weighted_mean_renormalizes_over_missing_stations():
    idx = pd.date_range("2023-06-01 01:00", periods=3, freq="h")
    mat = pd.DataFrame({"A": [80.0, 80.0, np.nan], "B": [90.0, np.nan, np.nan]}, index=idx)
    w = pd.Series({"A": 0.5, "B": 0.5})
    got = zw.weighted_mean(mat, w)
    assert got.iloc[0] == pytest.approx(85.0)   # both present
    assert got.iloc[1] == pytest.approx(80.0)   # B missing → renormalize to A
    assert np.isnan(got.iloc[2])                # all missing → NaN


def test_station_weights_from_crosswalk(tmp_path, monkeypatch):
    cw = pd.DataFrame(
        {
            "county_fips": ["48113", "48439", "48085"],
            "county_name": ["Dallas", "Tarrant", "Collin"],
            "weather_zone": ["NCENT", "NCENT", "NCENT"],
            "population": [2_600_000, 2_100_000, 1_100_000],
            "station_id": ["722580-13960", "722590-03927", "722590-03927"],
            "station_name": ["Love", "DFW", "DFW"],
            "dist_km": [10.0, 12.0, 30.0],
            "weight": [0.30, 0.20, 0.10],
        }
    )
    p = tmp_path / "crosswalk_county_station.csv"
    cw.to_csv(p, index=False)
    monkeypatch.setattr(zw, "CROSSWALK_PATH", p)
    weights, source = zw.get_station_weights()
    assert source == "crosswalk"
    assert weights["NCENT"]["722580-13960"] == pytest.approx(0.5)   # 0.3 / 0.6
    assert weights["NCENT"]["722590-03927"] == pytest.approx(0.5)   # (0.2+0.1) / 0.6


def test_station_weights_provisional_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(zw, "CROSSWALK_PATH", tmp_path / "nope.csv")
    weights, source = zw.get_station_weights()
    assert source == "provisional"
    assert set(weights) == {"NCENT", "COAST", "SCENT"}
    for z, w in weights.items():
        assert all(v == pytest.approx(0.5) for v in w.values())
    # corrected modern ids (722583/722435 ended 1997 per isd-history)
    assert "722580-13960" in weights["NCENT"]
    assert "722440-12918" in weights["COAST"]
