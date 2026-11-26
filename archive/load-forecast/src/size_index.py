"""Task 03: size index — weather-normalized annual load level per zone.

Model (per zone, daily granularity, weighted OLS via numpy):

    energy_mwh ~ intercept
               + piecewise-linear daily-mean temp (knots 55/65/75 °F)
               + weekday dummies + US-holiday dummy
               + YEAR FIXED EFFECTS (one level dummy per year, ref = first year)

Year fixed effects replace the original linear date trend per sdalvi's ruling
2026-08-14 (Opus review D8): a single global slope is a straight line by
construction and cannot show recent acceleration; year effects carry real
per-year level information, so the last-6-year extrapolation and the 6% y/y
sanity flag both become meaningful.

Event weights (CLAUDE.md): uri and outage days weight 0, covid days 0.25,
else 1. Train wall: only dates ≤ TRAIN_END enter the fit.

Normalization: predict a CANONICAL FULL CALENDAR (every day of every fitted
year — not just observed days, so data holes and leap days cannot bias the
level) at climate-normal temperature, sum per year, and scale to a 365.25-day
year → normalized_gwh → size_idx (BASE_YEAR = 1.0). Extrapolation: linear OLS
of normalized_gwh on year over the last 6 fitted years, source='extrapolated'.

Input contract: a daily frame per zone with columns date (datetime),
energy_mwh, temp_mean_f, event_flag (null/'uri'/'covid'/'outage').
`daily_energy_from_hourly()` builds the energy/flag half from load_hourly.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg

SIZE_INDEX_PATH = cfg.DERIVED_DIR / "size_index.parquet"

TEMP_KNOTS = (55.0, 65.0, 75.0)
MIN_HOURS_PER_DAY = 20  # below this a day is dropped; 20–25 h scaled to 24
NORMALS_YEARS = 10      # calendar-day normals window, ending at the train wall


# ---------------------------------------------------------------------------
# Daily prep
# ---------------------------------------------------------------------------


def daily_energy_from_hourly(load_hourly: pd.DataFrame, zone: str) -> pd.DataFrame:
    """Aggregate one zone's load_hourly to daily energy.

    Day = (hour-ending label − 1h).date, so HE24 stays on its own day. Days
    with 20–25 hours (DST, stray gaps) are scaled to a 24-h equivalent; days
    under MIN_HOURS_PER_DAY are dropped.
    Returns: date, energy_mwh, n_hours, event_flag.
    """
    df = load_hourly.loc[load_hourly["weather_zone"] == zone].copy()
    day = (df["ts_local"] - pd.Timedelta(hours=1)).dt.normalize()
    g = df.assign(day=day).groupby("day")
    out = g.agg(
        energy_mwh=("load_mw", "sum"),
        n_hours=("load_mw", lambda s: int(s.notna().sum())),
        event_flag=("event_flag", "first"),
    ).reset_index(names="date")
    out = out.loc[out["n_hours"] >= MIN_HOURS_PER_DAY].copy()
    out["energy_mwh"] = out["energy_mwh"] * (24.0 / out["n_hours"])
    return out.reset_index(drop=True)


def daily_zone_temp(zone_weather: pd.DataFrame, zone: str) -> pd.DataFrame:
    """Daily mean pop-weighted temp, bucketed like daily energy ((ts−1h).date)."""
    wx = zone_weather.loc[zone_weather["weather_zone"] == zone]
    day = (wx["ts_local"] - pd.Timedelta(hours=1)).dt.normalize().rename("date")
    return wx.groupby(day)["temp_f_popwt"].mean().rename("temp_mean_f").reset_index()


def build_daily(load_hourly: pd.DataFrame, zone_weather: pd.DataFrame, zone: str) -> pd.DataFrame:
    """Merged daily frame (energy + temp + flags) — the fit_zone input."""
    energy = daily_energy_from_hourly(load_hourly, zone)
    temp = daily_zone_temp(zone_weather, zone)
    return energy.merge(temp, on="date", how="inner")


def climate_normal_temp(daily_temp: pd.DataFrame, train_end: str | None = None) -> pd.DataFrame:
    """Calendar-day normal: mean over the last NORMALS_YEARS years ending at
    the train wall (explicitly windowed — does not silently widen if
    HISTORY_START_YEAR moves). Returns (mmdd, temp_norm_f); Feb 29 averages
    whatever leap years supply.
    """
    train_end = train_end or cfg.TRAIN_END
    wall_year = pd.Timestamp(train_end).year
    start_year = max(cfg.HISTORY_START_YEAR, wall_year - NORMALS_YEARS + 1)
    df = daily_temp.loc[
        (daily_temp["date"] >= f"{start_year}-01-01")
        & (daily_temp["date"] <= train_end)
    ]
    mmdd = df["date"].dt.strftime("%m-%d")
    return (
        df.assign(mmdd=mmdd)
        .groupby("mmdd")["temp_mean_f"]
        .mean()
        .rename("temp_norm_f")
        .reset_index()
    )


# ---------------------------------------------------------------------------
# Design matrix
# ---------------------------------------------------------------------------


def _holiday_dates(start, end) -> pd.DatetimeIndex:
    return USFederalHolidayCalendar().holidays(start=start, end=end)


def design_matrix(
    dates: pd.Series, temp_f: pd.Series, years: list[int]
) -> tuple[np.ndarray, list[str]]:
    """intercept | PWL temp | Mon..Sat dummies (Sun ref) | holiday |
    year effects (ref = years[0]). All dates must fall inside `years`."""
    year_of = dates.dt.year.to_numpy()
    unknown = set(np.unique(year_of)) - set(years)
    if unknown:
        raise ValueError(f"dates contain years outside the fit set: {sorted(unknown)}")

    cols: dict[str, np.ndarray] = {"intercept": np.ones(len(dates))}
    t = temp_f.to_numpy(dtype=float)
    cols["temp"] = t
    for k in TEMP_KNOTS:
        cols[f"hinge_{k:.0f}"] = np.maximum(t - k, 0.0)
    dow = dates.dt.dayofweek.to_numpy()  # Mon=0 .. Sun=6 (reference)
    for d, name in enumerate(["mon", "tue", "wed", "thu", "fri", "sat"]):
        cols[f"dow_{name}"] = (dow == d).astype(float)
    hol = _holiday_dates(dates.min(), dates.max())
    cols["holiday"] = dates.dt.normalize().isin(hol).to_numpy(dtype=float)
    for y in years[1:]:  # ref year = years[0]
        cols[f"year_{y}"] = (year_of == y).astype(float)
    names = list(cols)
    return np.column_stack([cols[n] for n in names]), names


def event_weights(event_flag: pd.Series) -> np.ndarray:
    w = np.ones(len(event_flag))
    flags = event_flag.fillna("").to_numpy()
    w[flags == "uri"] = 0.0
    w[flags == "outage"] = 0.0
    w[flags == "covid"] = cfg.COVID_WEIGHT
    return w


# ---------------------------------------------------------------------------
# Fit / normalize
# ---------------------------------------------------------------------------


@dataclass
class ZoneFit:
    zone: str
    beta: np.ndarray
    feature_names: list[str]
    years: list[int]
    r2: float  # 1 - SSE/SST, unweighted, on weight>0 days
    n_days: int

    def predict(self, dates: pd.Series, temp_f: pd.Series) -> np.ndarray:
        X, names = design_matrix(dates, temp_f, self.years)
        assert names == self.feature_names
        return X @ self.beta

    def year_effects(self) -> dict[int, float]:
        """Fitted level per year relative to the reference (first) year, MWh/day."""
        out = {self.years[0]: 0.0}
        for name, b in zip(self.feature_names, self.beta):
            if name.startswith("year_"):
                out[int(name.split("_")[1])] = float(b)
        return out


def fit_zone(daily: pd.DataFrame, zone: str, train_end: str | None = None) -> ZoneFit:
    """Weighted OLS on days ≤ train_end (default cfg.TRAIN_END). daily needs:
    date, energy_mwh, temp_mean_f, event_flag."""
    train_end = train_end or cfg.TRAIN_END
    df = daily.loc[daily["date"] <= train_end].dropna(
        subset=["energy_mwh", "temp_mean_f"]
    )
    years = sorted(df["date"].dt.year.unique().tolist())
    X, names = design_matrix(df["date"], df["temp_mean_f"], years)
    y = df["energy_mwh"].to_numpy(dtype=float)
    w = event_weights(df["event_flag"])
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)

    used = w > 0
    resid = y[used] - (X[used] @ beta)
    ss_res = float((resid**2).sum())
    ss_tot = float(((y[used] - y[used].mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot
    return ZoneFit(
        zone=zone, beta=beta, feature_names=names, years=years,
        r2=r2, n_days=int(used.sum()),
    )


def normalized_annual_gwh(
    fit: ZoneFit, daily: pd.DataFrame, train_end: str | None = None
) -> pd.DataFrame:
    """Predict a canonical FULL calendar of every fitted year at climate-normal
    temp → annual GWh, scaled to a 365.25-day year so leap years and data
    holes cannot tilt the level series."""
    train_end = train_end or cfg.TRAIN_END
    df = daily.loc[daily["date"] <= train_end].dropna(subset=["temp_mean_f"])
    normals = climate_normal_temp(df[["date", "temp_mean_f"]], train_end=train_end)

    cal = pd.DataFrame(
        {"date": pd.date_range(f"{fit.years[0]}-01-01", f"{fit.years[-1]}-12-31", freq="D")}
    )
    cal = cal.loc[cal["date"].dt.year.isin(fit.years)].reset_index(drop=True)
    cal["mmdd"] = cal["date"].dt.strftime("%m-%d")
    cal = cal.merge(normals, on="mmdd", how="left")
    if cal["temp_norm_f"].isna().any():
        missing = cal.loc[cal["temp_norm_f"].isna(), "mmdd"].unique()
        raise ValueError(f"no climate normal for calendar days: {missing}")

    cal["pred_mwh"] = fit.predict(cal["date"], cal["temp_norm_f"])
    per_year = cal.groupby(cal["date"].dt.year)["pred_mwh"].agg(["mean"])
    out = (per_year["mean"] * 365.25 / 1000.0).rename("normalized_gwh").reset_index()
    return out.rename(columns={"date": "year"})


def extrapolate(annual: pd.DataFrame, through_year: int, n_fit_years: int = 6) -> pd.DataFrame:
    """Linear OLS of normalized_gwh on year over the last n fitted years."""
    tail = annual.sort_values("year").tail(n_fit_years)
    slope, intercept = np.polyfit(tail["year"], tail["normalized_gwh"], 1)
    last = int(annual["year"].max())
    years = list(range(last + 1, through_year + 1))
    return pd.DataFrame(
        {"year": years, "normalized_gwh": [slope * y + intercept for y in years]}
    )


def build_size_index(
    daily_by_zone: dict[str, pd.DataFrame],
    through_year: int = 2028,
    out_path: Path | None = None,
    train_end: str | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Full Task 03 output across zones → canonical size_index table (saved to
    out_path, default SIZE_INDEX_PATH) + diagnostics dict (fit R², year
    effects — kept OUT of the canonical table per the no-silent-columns rule).
    train_end overrides the wall for backtesting folds."""
    out_path = out_path if out_path is not None else SIZE_INDEX_PATH
    rows, diag = [], {}
    for zone, daily in daily_by_zone.items():
        fit = fit_zone(daily, zone, train_end=train_end)
        annual = normalized_annual_gwh(fit, daily, train_end=train_end)
        annual["source"] = "fitted"
        n_fit = cfg.SIZE_EXTRAP_YEARS.get(zone, 6)
        extra = extrapolate(annual, through_year, n_fit_years=n_fit)
        extra["source"] = "extrapolated"
        both = pd.concat([annual, extra], ignore_index=True)
        base = both.loc[both["year"] == cfg.BASE_YEAR, "normalized_gwh"]
        if base.empty:
            raise ValueError(f"{zone}: base year {cfg.BASE_YEAR} missing from fit range")
        both["size_idx"] = both["normalized_gwh"] / float(base.iloc[0])
        both["weather_zone"] = zone
        rows.append(both)
        diag[zone] = {"r2": fit.r2, "n_days": fit.n_days, "year_effects": fit.year_effects()}
    out = pd.concat(rows, ignore_index=True)[
        ["weather_zone", "year", "normalized_gwh", "size_idx", "source"]
    ]
    # acceptance guardrail from the task file — warn, don't block
    for zone in out["weather_zone"].unique():
        z = out.loc[(out["weather_zone"] == zone) & (out["source"] == "fitted")]
        yoy = z.sort_values("year")["size_idx"].pct_change().abs()
        if (yoy > 0.06).any():
            print(f"WARNING {zone}: y/y size_idx move > 6% — review before trusting")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_path)
    return out, diag
