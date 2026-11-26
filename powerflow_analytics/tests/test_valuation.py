import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pfa.analysis import valuation


def _runs():
    # 4 sampled days x 3 hours; Sep 16-19, 2026 (Wed-Sat; the 19th is Saturday)
    rows = []
    rid = 0
    for d in ["2026-09-16", "2026-09-17", "2026-09-18", "2026-09-19"]:
        for h in (3, 12, 18):
            rid += 1
            rows.append({"RUNID": rid, "SIMDATE": d, "SIMHOUR": h})
    return pd.DataFrame(rows)


def _outcon(runs):
    # binds at HE18 on 2 of 4 days, HE12 on 1 of 4; lambda 40/80 at HE18, 20 at HE12
    bind = runs[((runs.SIMHOUR == 18) & (runs.SIMDATE.isin(["2026-09-16", "2026-09-17"])))
                | ((runs.SIMHOUR == 12) & (runs.SIMDATE == "2026-09-16"))]
    lam = {("2026-09-16", 18): 40.0, ("2026-09-17", 18): 80.0, ("2026-09-16", 12): 20.0}
    return pd.DataFrame({
        "RUNID": bind.RUNID.values,
        "FROMNUM": 10, "TONUM": 11, "CKT": "1",
        "LPOPFCTGID": "CTGA",
        "OPFCNLAMBDA": [lam[(d, h)] for d, h in zip(bind.SIMDATE, bind.SIMHOUR)],
        "LPBASICVARID": "Gen 1 #1 MW Control",
    })


def test_binding_stats_window():
    runs = _runs()
    stats = valuation.binding_stats(_outcon(runs), runs, "10-11-1@CTGA",
                                    window=("2026-09-16", "2026-09-30"))
    assert stats.p_bind[18] == 0.5 and stats.p_bind[12] == 0.25
    assert stats.lam.loc[18, "p50"] == 60.0
    assert stats.n_window_runs == 12


def test_offer_lambda_capped():
    lo, hi = valuation.offer_lambda(7.0, 60.0, 0.18)
    assert round(lo, 1) == 38.9 and round(hi, 1) == 333.3
    assert valuation.offer_lambda(2000.0, 3000.0, 0.1)[1] == valuation.PRICE_CAP
    with pytest.raises(ValueError):
        valuation.offer_lambda(1.0, 2.0, 0.0)


def test_dollars_per_mwh():
    runs = _runs()
    stats = valuation.binding_stats(_outcon(runs), runs, "10-11-1@CTGA",
                                    window=("2026-09-16", "2026-09-30"))
    out = valuation.dollars_per_mwh(stats, 2026, 9, ("2026-09-16", "2026-09-30"), "p50", sf=1.0)
    # Sep 2026: 22 business days minus Labor Day 9/7 = 21 on-peak days; window 9/16-9/30 has 11
    assert out["onpeak_days"] == 21 and out["outage_onpeak_days"] == 11
    # per day: HE12 block 0.25*20*10 + HE18 block 0.5*60*6 = 50 + 180 = 230; x11 = 2530
    assert out["rent_per_mw_month"] == 2530.0
    assert out["dollars_per_mwh"] == round(2530.0 / (21 * 16), 3)


def test_dollars_per_mwh_sf_scaling():
    runs = _runs()
    stats = valuation.binding_stats(_outcon(runs), runs, "10-11-1@CTGA",
                                    window=("2026-09-16", "2026-09-30"))
    full = valuation.dollars_per_mwh(stats, 2026, 9, ("2026-09-16", "2026-09-30"), "p50", 1.0)
    path = valuation.dollars_per_mwh(stats, 2026, 9, ("2026-09-16", "2026-09-30"), "p50", 0.31)
    assert path["dollars_per_mwh"] == pytest.approx(full["dollars_per_mwh"] * 0.31, abs=0.01)
