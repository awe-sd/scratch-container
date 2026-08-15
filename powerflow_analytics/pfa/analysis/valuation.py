"""Constraint valuation in $/MWh over the 5x16 on-peak settlement block.

Method (per constraint):
1. Binding stats from the study LP (OUTCONSTRAINT2): P(bind | hour block) and
   the lambda distribution, restricted to the driving outage's window.
2. Lambda cross-check from marginal-unit offers: lambda = offer spread / delta-SF
   (the caller supplies offer quantiles; ERCOT's $5000 cap bounds the tail).
3. Normalize to $/MWh: expected rent per MW of flowgate over the month divided
   by the month's total on-peak hours (M-F 5x16, NERC holidays excluded).

Study runs sample a few hours (e.g. HE 3/12/18); each sampled hour represents
a block of on-peak hours (HOUR_BLOCKS). Scale a path by its shift factor on
the flowgate to get $/MWh of CRR path.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .constraints import constraint_key

PRICE_CAP = 5000.0

# sampled sim-hour -> number of on-peak hours it represents (16h on-peak day)
HOUR_BLOCKS = {12: 10, 18: 6}  # midday block HE7-16, evening block HE17-22

NERC_HOLIDAYS_2026 = pd.to_datetime(
    ["2026-01-01", "2026-05-25", "2026-07-04", "2026-09-07", "2026-11-26", "2026-12-25"]
)


def onpeak_days(year: int, month: int) -> pd.DatetimeIndex:
    """Business days (M-F minus NERC holidays) in a month."""
    days = pd.bdate_range(f"{year}-{month:02d}-01", pd.Timestamp(year=year, month=month, day=1)
                          + pd.offsets.MonthEnd(0))
    return days[~days.isin(NERC_HOLIDAYS_2026)]


@dataclass
class BindingStats:
    constraint: str
    p_bind: dict[int, float]          # sim hour -> P(bind) within the window
    lam: pd.DataFrame                 # per sim hour: p25/p50/p75/mean of lambda
    window: tuple[str, str] | None    # outage window the stats are conditioned on
    n_window_runs: int


def binding_stats(
    outcon: pd.DataFrame,
    runs: pd.DataFrame,
    constraint: str,
    window: tuple[str, str] | None = None,
) -> BindingStats:
    """P(bind|sim hour) and lambda distribution, within the outage window."""
    oc = outcon.rename(columns={"LPOPFCTGID": "CTGLABEL"})
    oc["CONSTRAINT"] = constraint_key(oc)
    c = oc[oc["CONSTRAINT"] == constraint].merge(
        runs[["RUNID", "SIMDATE", "SIMHOUR"]], on="RUNID"
    )
    r = runs.copy()
    if window is not None:
        in_win = (pd.to_datetime(r["SIMDATE"]) >= window[0]) & (
            pd.to_datetime(r["SIMDATE"]) <= window[1])
        r = r[in_win]
        c = c[(pd.to_datetime(c["SIMDATE"]) >= window[0])
              & (pd.to_datetime(c["SIMDATE"]) <= window[1])]
    tot = r.groupby("SIMHOUR")["RUNID"].nunique()
    bind = c.groupby("SIMHOUR")["RUNID"].nunique()
    p = (bind / tot).fillna(0.0).to_dict()
    lam = c.groupby("SIMHOUR")["OPFCNLAMBDA"].agg(
        p25=lambda s: s.quantile(0.25), p50="median",
        p75=lambda s: s.quantile(0.75), mean="mean",
    ).clip(upper=PRICE_CAP)
    return BindingStats(constraint, {int(k): float(v) for k, v in p.items()},
                        lam, window, int(r["RUNID"].nunique()))


def offer_lambda(spread_low: float, spread_high: float, delta_sf: float) -> tuple[float, float]:
    """Lambda range from marginal-unit offer spread / delta shift factor, capped."""
    if delta_sf <= 0:
        raise ValueError("delta_sf must be positive")
    return (min(spread_low / delta_sf, PRICE_CAP), min(spread_high / delta_sf, PRICE_CAP))


def dollars_per_mwh(
    stats: BindingStats,
    year: int,
    month: int,
    outage_window: tuple[str, str],
    lam_col: str = "p50",
    sf: float = 1.0,
) -> dict:
    """Expected congestion $/MWh over the month's 5x16 block, per MW at `sf`.

    rent = sum over outage business days of sum over hour blocks of
           P(bind|block) x lambda x block hours; divided by total on-peak MWh.
    """
    days = onpeak_days(year, month)
    total_onpeak_h = len(days) * 16
    win = days[(days >= outage_window[0]) & (days <= outage_window[1])]
    rent_per_day = 0.0
    for hour, block_h in HOUR_BLOCKS.items():
        p = stats.p_bind.get(hour, 0.0)
        lam = float(stats.lam[lam_col].get(hour, 0.0)) if hour in stats.lam.index else 0.0
        rent_per_day += p * lam * block_h
    total_rent = rent_per_day * len(win) * sf
    return {
        "constraint": stats.constraint,
        "onpeak_days": len(days),
        "outage_onpeak_days": len(win),
        "rent_per_mw_month": round(total_rent, 2),
        "dollars_per_mwh": round(total_rent / total_onpeak_h, 3) if total_onpeak_h else 0.0,
        "lam_col": lam_col,
        "sf": sf,
    }
