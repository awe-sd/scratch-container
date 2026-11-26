"""Synthetic-data tests for size_index: known trend in → known size_idx out."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import config as cfg
import size_index as si


def synthetic_daily(
    start="2015-01-01",
    end="2024-12-31",
    base=200_000.0,
    trend_per_year=8_000.0,
    seed=7,
    uri_spike=0.0,
    outage_dip=0.0,
) -> pd.DataFrame:
    """Additive world matching the model family: base + trend + temp response."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start, end, freq="D")
    doy = dates.dayofyear.to_numpy()
    temp = 70 + 25 * np.sin(2 * np.pi * (doy - 105) / 365.25) + rng.normal(0, 3, len(dates))
    epoch = pd.Timestamp(f"{cfg.HISTORY_START_YEAR}-01-01")
    trend_years = (dates - epoch).days / 365.25
    cooling = np.maximum(temp - 65, 0) * 900
    heating = np.maximum(50 - temp, 0) * 400
    weekend = np.isin(dates.dayofweek, [5, 6]) * -9_000
    energy = base + trend_per_year * trend_years + cooling + heating + weekend
    energy = energy + rng.normal(0, 1_500, len(dates))

    flag = pd.Series(pd.NA, index=range(len(dates)), dtype="string")
    d = pd.Series(dates.strftime("%Y-%m-%d"))
    flag[(d >= cfg.COVID_WINDOW[0]) & (d <= cfg.COVID_WINDOW[1])] = "covid"
    flag[(d >= cfg.URI_WINDOW[0]) & (d <= cfg.URI_WINDOW[1])] = "uri"
    for w_start, w_end, _zones in cfg.OUTAGE_WINDOWS:
        flag[(d >= w_start) & (d <= w_end)] = "outage"
    if uri_spike:
        energy = np.where(flag.fillna("") == "uri", energy + uri_spike, energy)
    if outage_dip:
        energy = np.where(flag.fillna("") == "outage", energy * (1 - outage_dip), energy)
    return pd.DataFrame(
        {"date": dates, "energy_mwh": energy, "temp_mean_f": temp, "event_flag": flag}
    )


def test_fit_recovers_growth_via_year_effects():
    daily = synthetic_daily()
    fit = si.fit_zone(daily, "NCENT")
    assert fit.r2 > 0.95
    effects = fit.year_effects()
    steps = np.diff([effects[y] for y in sorted(effects)])
    # synthetic growth is 8,000 MWh/day per year — every year step should see it
    assert np.mean(steps) == pytest.approx(8_000.0, rel=0.05)
    assert all(abs(s - 8_000.0) < 1_500 for s in steps)


def test_year_effects_track_recent_acceleration():
    """The reason for year FE (review D8): a kink in recent growth must show up
    in the extrapolation slope instead of being averaged away."""
    daily = synthetic_daily()
    # triple the growth from 2021 on
    extra = (daily["date"].dt.year - 2020).clip(lower=0) * 16_000.0
    daily = daily.assign(energy_mwh=daily["energy_mwh"] + extra)
    fit = si.fit_zone(daily, "Z")
    annual = si.normalized_annual_gwh(fit, daily)
    extrap = si.extrapolate(annual, 2026)
    recent_step = float(np.diff(extrap["normalized_gwh"]).mean())
    # accelerated slope ≈ (8k + 16k) MWh/day * 365.25 / 1000 ≈ 8.8k GWh/yr;
    # last-6 window (2019-2024) straddles the kink so expect > the old 2.9k
    assert recent_step > 6_000.0


def test_uri_days_do_not_move_the_fit():
    clean = si.fit_zone(synthetic_daily(uri_spike=0.0), "Z")
    spiked = si.fit_zone(synthetic_daily(uri_spike=300_000.0), "Z")
    np.testing.assert_allclose(clean.beta, spiked.beta, rtol=1e-9)


def test_outage_days_do_not_move_the_fit():
    """Review D3/D4: a Beryl-style −40% suppression window at the end of the
    fit range must not move the fit (weight 0)."""
    clean = si.fit_zone(synthetic_daily(outage_dip=0.0), "Z")
    dipped = si.fit_zone(synthetic_daily(outage_dip=0.40), "Z")
    np.testing.assert_allclose(clean.beta, dipped.beta, rtol=1e-9)


def test_event_weights_values():
    flags = pd.Series(["uri", "outage", "covid", None], dtype="string")
    w = si.event_weights(flags)
    assert w.tolist() == [0.0, 0.0, cfg.COVID_WEIGHT, 1.0]


def test_missing_day_does_not_bias_annual_level():
    """Review D2 downstream fix: normalization predicts a canonical full
    calendar, so deleting an observed July day must leave normalized_gwh
    essentially unchanged (previously ~-0.3% on the year)."""
    daily = synthetic_daily()
    fit_full = si.fit_zone(daily, "Z")
    full = si.normalized_annual_gwh(fit_full, daily).set_index("year")["normalized_gwh"]
    holed = daily.loc[daily["date"] != "2018-07-03"]
    fit_holed = si.fit_zone(holed, "Z")
    hole = si.normalized_annual_gwh(fit_holed, holed).set_index("year")["normalized_gwh"]
    assert abs(hole[2018] / full[2018] - 1) < 0.001


def test_size_index_base_year_and_growth(tmp_path):
    daily = synthetic_daily()
    out, diag = si.build_size_index(
        {"NCENT": daily}, through_year=2028, out_path=tmp_path / "size_index.parquet"
    )
    assert diag["NCENT"]["r2"] > 0.95
    assert "fit_r2" not in out.columns  # no silent schema additions
    base = out.loc[(out["year"] == cfg.BASE_YEAR), "size_idx"]
    assert float(base.iloc[0]) == pytest.approx(1.0)
    fitted = out.loc[out["source"] == "fitted"].sort_values("year")
    assert fitted["size_idx"].is_monotonic_increasing
    # ~8 GWh/day * 365 on a ~90 TWh/yr zone → ~3%/yr; extrapolated rows exist
    extra = out.loc[out["source"] == "extrapolated", "year"].tolist()
    assert extra == [2025, 2026, 2027, 2028]
    # extrapolation continues the linear trend: constant y/y step in GWh
    steps = out.sort_values("year")["normalized_gwh"].diff().dropna()
    assert steps.std() / steps.mean() < 0.25


def test_train_wall_excludes_post_2024():
    daily = synthetic_daily(end="2026-06-30")
    # poison post-wall data — must not affect the fit
    poisoned = daily.copy()
    poisoned.loc[poisoned["date"] > cfg.TRAIN_END, "energy_mwh"] *= 100
    f_clean = si.fit_zone(synthetic_daily(end="2026-06-30"), "Z")
    f_poison = si.fit_zone(poisoned, "Z")
    np.testing.assert_allclose(f_clean.beta, f_poison.beta, rtol=1e-12)


def test_daily_energy_from_hourly_buckets_he24_correctly():
    # two full days for one zone; he=24's ts_local is next-day 00:00
    ts = []
    for day in ["2023-06-01", "2023-06-02"]:
        base = pd.Timestamp(day)
        ts += [base + pd.Timedelta(hours=h) for h in range(1, 25)]
    hourly = pd.DataFrame(
        {
            "weather_zone": "NCENT",
            "ts_local": ts,
            "load_mw": [1000.0] * 48,
            "event_flag": pd.array([pd.NA] * 48, dtype="string"),
        }
    )
    daily = si.daily_energy_from_hourly(hourly, "NCENT")
    assert len(daily) == 2
    assert daily["energy_mwh"].tolist() == [24_000.0, 24_000.0]
    assert daily["date"].dt.strftime("%Y-%m-%d").tolist() == ["2023-06-01", "2023-06-02"]


def test_daily_energy_scales_short_days_and_drops_tiny_ones():
    base = pd.Timestamp("2023-03-12")  # spring-forward-like short day
    rows = [(base + pd.Timedelta(hours=h), 1000.0) for h in range(1, 24)]  # 23 h
    tiny = [(pd.Timestamp("2023-03-13") + pd.Timedelta(hours=h), 1000.0) for h in range(1, 6)]
    hourly = pd.DataFrame(
        {
            "weather_zone": "COAST",
            "ts_local": [t for t, _ in rows + tiny],
            "load_mw": [v for _, v in rows + tiny],
            "event_flag": pd.array([pd.NA] * (len(rows) + len(tiny)), dtype="string"),
        }
    )
    daily = si.daily_energy_from_hourly(hourly, "COAST")
    assert len(daily) == 1  # 5-hour day dropped
    assert daily["energy_mwh"].iloc[0] == pytest.approx(23_000.0 * 24 / 23)


def test_climate_normal_temp_is_calendar_day_mean():
    daily = synthetic_daily()
    normals = si.climate_normal_temp(daily[["date", "temp_mean_f"]])
    jul4 = daily.loc[daily["date"].dt.strftime("%m-%d") == "07-04", "temp_mean_f"].mean()
    got = normals.loc[normals["mmdd"] == "07-04", "temp_norm_f"].iloc[0]
    assert got == pytest.approx(jul4)
