import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from pfa.analysis.screening import classify_constraint  # noqa: E402
from build_screening_report import (  # noqa: E402
    coverage_and_days, pre_post_bind_rates, month_bind_dates,
)


# ---------------------------------------------------------------------------
# classify_constraint
# ---------------------------------------------------------------------------

def test_class_a_outage_driven_dispatchable():
    cls, _ = classify_constraint(top_share=0.4, dispatch_ok=True, penalty=False,
                                 pre_rate=0.0, post_rate=0.6)
    assert cls == "A"


def test_class_a_requires_dispatch_ok_not_false():
    cls, _ = classify_constraint(top_share=0.4, dispatch_ok=False, penalty=False,
                                 pre_rate=0.0, post_rate=0.6)
    assert cls != "A"
    assert cls == "C"


def test_class_c_penalty_tier():
    cls, _ = classify_constraint(top_share=0.1, dispatch_ok=True, penalty=True,
                                 pre_rate=0.1, post_rate=0.1)
    assert cls == "C"


def test_class_c_no_dispatch_pair():
    cls, _ = classify_constraint(top_share=None, dispatch_ok=False, penalty=False,
                                 pre_rate=0.0, post_rate=0.0)
    assert cls == "C"


def test_class_d_negative_share_bearish():
    cls, _ = classify_constraint(top_share=-0.3, dispatch_ok=True, penalty=False,
                                 pre_rate=0.2, post_rate=0.2)
    assert cls == "D"


def test_class_d_beats_class_a():
    """Negative top-share (outage unloads the constraint) must win over an
    otherwise-qualifying class-A pattern — direction flips, so D takes
    precedence even if dispatch_ok/penalty would look like A."""
    cls, _ = classify_constraint(top_share=-0.4, dispatch_ok=True, penalty=False,
                                 pre_rate=0.0, post_rate=0.6)
    assert cls == "D"


def test_class_d_binds_pre_not_post():
    cls, _ = classify_constraint(top_share=0.1, dispatch_ok=True, penalty=False,
                                 pre_rate=0.5, post_rate=0.0)
    assert cls == "D"


def test_class_b_baseline_binder():
    cls, _ = classify_constraint(top_share=0.1, dispatch_ok=True, penalty=False,
                                 pre_rate=0.3, post_rate=0.5)
    assert cls == "B"


def test_class_b_requires_half_rate():
    cls, _ = classify_constraint(top_share=0.1, dispatch_ok=True, penalty=False,
                                 pre_rate=0.1, post_rate=0.5)
    assert cls != "B"


def test_unclassified_fallback():
    cls, _ = classify_constraint(top_share=None, dispatch_ok=None, penalty=False,
                                 pre_rate=0.0, post_rate=0.0)
    assert cls == "U"


# ---------------------------------------------------------------------------
# pre_post_bind_rates / month_bind_dates (synthetic frames, no DB)
# ---------------------------------------------------------------------------

def _synthetic_runs():
    return pd.DataFrame({
        "RUNID": [1, 2, 3, 4],
        "SIMDATE": ["2026-08-01", "2026-08-02", "2026-09-16", "2026-09-17"],
    })


def _synthetic_ctgviol(binding_runids):
    rows = []
    for rid in [1, 2, 3, 4]:
        rows.append({
            "RUNID": rid, "FROMNUM": 100, "TONUM": 200, "CKT": "1", "CTGLABEL": "X",
            "LIMVIOLPCT": 100.0 if rid in binding_runids else 50.0,
        })
    return pd.DataFrame(rows)


def test_pre_post_bind_rates_basic():
    runs = _synthetic_runs()
    cv = _synthetic_ctgviol(binding_runids={1, 3, 4})  # binds 1/2 pre, 2/2 post
    rate_pre, rate_post, n_pre, n_post = pre_post_bind_rates(cv, runs, "2026-09-15")
    c = "100-200-1@X"
    assert n_pre == 2 and n_post == 2
    assert rate_pre[c] == 0.5
    assert rate_post[c] == 1.0


def test_month_bind_dates_proxy():
    runs = _synthetic_runs()
    cv = _synthetic_ctgviol(binding_runids={3})  # binds only one of the two post-cutoff Sept dates
    bind_days, n_sampled = month_bind_dates(cv, runs, "2026-09-15", "2026-09")
    c = "100-200-1@X"
    assert n_sampled == 2
    assert bind_days.get(c, 0) == 1


def test_coverage_ticketed_short_window_sinks():
    """Addendum: a 1-day ticketed outage must get a small coverage fraction,
    not a free pass — 1 day * 16h / 336h ~= 0.048."""
    cov, n_days, marker, thin = coverage_and_days(
        "c1", True, "2026-09-16", "2026-09-16", {}, 0, "2026-09")
    assert n_days == 1
    assert cov < 0.06
    assert thin is True
    assert marker == ""


def test_coverage_unticketed_uses_days_proxy_not_1():
    bind_days = pd.Series({"c1": 2})
    cov, n_days, marker, thin = coverage_and_days("c1", False, None, None, bind_days, 10, "2026-09")
    assert cov == 0.2
    assert marker == "(days-proxy)"
    assert thin is True  # 2 days < 3


def test_coverage_unticketed_thin_flag_clears_at_3_days():
    bind_days = pd.Series({"c1": 3})
    cov, n_days, marker, thin = coverage_and_days("c1", False, None, None, bind_days, 10, "2026-09")
    assert thin is False


def test_coverage_non_september_month():
    cov, n_days, marker, thin = coverage_and_days(
        "c1", True, "2027-03-01", "2027-03-05", {}, 0, "2027-03")
    assert n_days == 5 and cov == round(5 / 23, 3) and not thin
