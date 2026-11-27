import pandas as pd


from build_screening_report import (  # noqa: E402
    classify_constraint, pre_post_bind_rates,
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
