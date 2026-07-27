"""Shared loaders/parsers for the analytics-dev summer constraint study."""
import re
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SUMMER_26 = ("2026-05-01", "2026-07-14")
SUMMER_25 = ("2025-06-01", "2025-09-30")
AUG_25 = ("2025-08-01", "2025-08-31")

BRACKET_RE = re.compile(r"\[\s*(.+?)\s*\]")
CONT_RE = re.compile(r"CONT:\s*(\S+)")
LEAD_RE = re.compile(r"^\s*([A-Za-z0-9_\.\-]+)")


def load(name):
    return pd.read_parquet(DATA_DIR / f"{name}.parquet")


def parse_constraint_names(defc):
    """Add normalized grouping columns parsed from isoConstraintName.

    elem  : monitored element, normalized bracket text (fallback: leading token)
    cont  : contingency token after CONT:
    ckey  : elem + '|' + cont  -> the analysis grain (dedupes naming variants)
    code  : leading device code, e.g. '6945', '6053_C'
    """
    name = defc["isoConstraintName"].fillna("")

    def _elem(s):
        m = BRACKET_RE.search(s)
        if m:
            return re.sub(r"\s+", "", m.group(1)).upper()
        m = LEAD_RE.match(s)
        return m.group(1).upper() if m else s.strip().upper()

    defc = defc.copy()
    defc["elem"] = name.map(_elem)
    defc["cont"] = name.map(
        lambda s: (CONT_RE.search(s).group(1).upper() if CONT_RE.search(s) else "BASE")
    )
    defc["code"] = name.map(
        lambda s: LEAD_RE.match(s).group(1).upper() if LEAD_RE.match(s) else ""
    )
    defc["ckey"] = defc["elem"] + "|" + defc["cont"]
    return defc


def hourly_net_load():
    """ERCOT hourly actual load / wind / solar / net load, 2024+."""
    ld = load("ercotLoadView").rename(columns=str.lower)
    ld["date"] = pd.to_datetime(ld["date"])
    wind = load("windGenAct_ercotAll")
    solar = load("solarGenAct_ercotAll")
    # priceTypeID: keep RT-actual flavor; if several, prefer the one with most rows
    for df, col in ((wind, "windGen"), (solar, "solarGen")):
        df["date"] = pd.to_datetime(df["date"])
    wpt = wind.groupby("priceTypeID").size().idxmax()
    spt = solar.groupby("priceTypeID").size().idxmax()
    wind = wind[wind.priceTypeID == wpt][["date", "HE", "windGen"]]
    solar = solar[solar.priceTypeID == spt][["date", "HE", "solarGen"]]
    df = (
        ld[["date", "he", "ercot_all_ld", "wz_west_ld", "wz_far_west_ld",
            "wz_north_central_ld"]]
        .rename(columns={"he": "HE"})
        .merge(wind, on=["date", "HE"], how="left")
        .merge(solar, on=["date", "HE"], how="left")
    )
    df["windGen"] = pd.to_numeric(df["windGen"], errors="coerce")
    df["solarGen"] = pd.to_numeric(df["solarGen"], errors="coerce")
    df["ercot_all_ld"] = pd.to_numeric(df["ercot_all_ld"], errors="coerce")
    df["net_load"] = df["ercot_all_ld"] - df["windGen"].fillna(0) - df["solarGen"].fillna(0)
    return df


def wind_by_region():
    """Hourly wind MW for West / Panhandle (and the rest).

    ercotWindRegionHourly actuals stop 2026-05-14; after that only one
    short-term-forecast row per hour/region exists (HSL-based), which we
    use as a proxy. wind_is_actual marks which rows are true actuals.
    """
    w = load("ercotWindRegionHourly")
    w = w.copy()
    w["TimeStamp"] = pd.to_datetime(w["TimeStamp"])
    w["mw"] = w["avgHSLPct"] / 100.0 * w["totalInstalledCapacityMW"]
    # prefer actual rows where both exist for an hour/region
    w = (
        w.sort_values("isActual", ascending=False)
        .drop_duplicates(["TimeStamp", "windRegion"], keep="first")
    )
    w["date"] = w["TimeStamp"].dt.normalize()
    w["HE"] = w["TimeStamp"].dt.hour + 1
    piv = w.pivot_table(index=["date", "HE"], columns="windRegion", values="mw", aggfunc="mean")
    piv.columns = [f"wind_{c.lower()}" for c in piv.columns]
    act = w.groupby(["date", "HE"])["isActual"].min().rename("wind_is_actual")
    return piv.join(act).reset_index()


def between(df, col, lo, hi):
    return df[(df[col] >= lo) & (df[col] <= hi)]
