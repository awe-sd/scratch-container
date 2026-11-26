import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_high_confidence_report import lam_and_source, value_per_mwh_sf  # noqa: E402


def _row(**overrides):
    base = {
        "_lam_hi_offer": None,
        "Realized DA (hrs | P50 | max)": None,
        "_penalty": False,
        "λ LP P50": None,
        "P(bind) on-peak": 0.5,
    }
    base.update(overrides)
    return pd.Series(base)


def test_penalty_lp_p50_excluded_from_value():
    """Defect 1: a penalty-tier constraint (flat 500/3500 LP lambda) with no
    offers-based estimate and no realized history must NOT fall back to LP
    P50 for Value/Edge — that was the bug that put fake-value rows like
    8186-8913-1@STHRSCH8 at the top of the Edge board. Value must be None."""
    row = _row(_penalty=True, **{"λ LP P50": 500.0})
    lam, source = lam_and_source(row)
    assert lam is None
    assert source is None
    assert value_per_mwh_sf(row) is None


def test_non_penalty_lp_p50_still_used_as_fallback():
    """A non-penalty constraint with no offers/realized coverage should still
    fall back to LP P50 (unchanged prior behavior)."""
    row = _row(_penalty=False, **{"λ LP P50": 42.0})
    lam, source = lam_and_source(row)
    assert lam == 42.0
    assert source == "LP"
    assert value_per_mwh_sf(row) is not None


def test_realized_da_preferred_over_penalty_lp():
    """Realized DA history outranks LP P50 regardless of penalty flag."""
    row = _row(_penalty=True, **{
        "λ LP P50": 3500.0,
        "Realized DA (hrs | P50 | max)": "12 | 55.0 | 200.0",
    })
    lam, source = lam_and_source(row)
    assert lam == 55.0
    assert source == "realized"


def test_offers_based_lambda_takes_precedence():
    row = _row(_penalty=True, **{
        "λ LP P50": 3500.0,
        "Realized DA (hrs | P50 | max)": "12 | 55.0 | 200.0",
        "_lam_hi_offer": 30.5,
    })
    lam, source = lam_and_source(row)
    assert lam == 30.5
    assert source == "offers"
