import numpy as np
import pandas as pd
import pytest

from pfa.analysis import screening
from pfa.analysis.screening import Thresholds, classify, detect_flips, stage2_gate


def _row(**kw):
    base = dict(pre_binds=0, post_binds=5, share=0.5, lam_p50=20.0, lam_iqr=5.0, penalty_share=0.0, NQUAL=3)
    base.update(kw)
    return base


def _cls(**kw):
    return classify(pd.DataFrame([_row(**kw)], index=["1-2-1@X"]))["class"].iloc[0]


# --- class rules -------------------------------------------------------------

def test_class_a_post_only_with_share_and_nodes():
    assert _cls() == "A target"


def test_class_d_pre_binds_never_post():
    assert _cls(pre_binds=2, post_binds=0) == "D bearish"


def test_class_d_not_when_never_binds_pre():
    assert _cls(pre_binds=0, post_binds=0, share=0.5) != "D bearish"


@pytest.mark.parametrize("share,expected", [(-0.101, "D bearish"), (-0.10, "weak"), (-0.05, "weak")])
def test_bearish_share_boundary(share, expected):
    assert _cls(share=share) == expected


def test_class_d_beats_c_and_b():
    assert _cls(share=-0.5, NQUAL=0, pre_binds=9) == "D bearish"


@pytest.mark.parametrize("nqual,expected", [(0, "C no-dispatch"), (1, "C no-dispatch"), (2, "A target")])
def test_nqual_boundary(nqual, expected):
    assert _cls(NQUAL=nqual) == expected


def test_penalty_share_boundary_strictly_greater():
    assert _cls(penalty_share=0.4) == "A target"
    assert _cls(penalty_share=0.41) == "C no-dispatch"


def test_penalty_share_threshold_is_configurable():
    df = pd.DataFrame([_row(penalty_share=0.3)], index=["1-2-1@X"])
    assert classify(df, Thresholds(penalty_share_max=0.2))["class"].iloc[0] == "C no-dispatch"


def test_flatness_test_needs_tier_median_and_small_iqr():
    assert _cls(lam_p50=3500.0, lam_iqr=0.5) == "C no-dispatch"
    assert _cls(lam_p50=3500.0, lam_iqr=1.0) == "A target"
    assert _cls(lam_p50=3499.0, lam_iqr=0.0) == "A target"
    assert _cls(lam_p50=500.0, lam_iqr=0.0) == "C no-dispatch"


def test_missing_penalty_inputs_do_not_trip_c():
    assert _cls(lam_p50=np.nan, lam_iqr=np.nan, penalty_share=np.nan) == "A target"


@pytest.mark.parametrize("pre,post,expected", [
    (1, 2, "B baseline"),   # pre == 0.5*post
    (1, 3, "A target"),     # pre < 0.5*post
    (2, 4, "B baseline"),
    (3, 4, "B baseline"),
    (1, 1, "B baseline"),   # max(1, ...) floor
])
def test_baseline_rule(pre, post, expected):
    assert _cls(pre_binds=pre, post_binds=post) == expected


def test_baseline_needs_at_least_one_pre_bind():
    assert _cls(pre_binds=0, post_binds=1) == "A target"


@pytest.mark.parametrize("share,expected", [(0.25, "A target"), (0.2499, "weak"), (np.nan, "weak")])
def test_class_a_share_boundary(share, expected):
    assert _cls(share=share) == expected


def test_class_a_share_is_fixed_regardless_of_gate_share_min():
    df = pd.DataFrame([_row(share=0.2)], index=["1-2-1@X"])
    assert classify(df, Thresholds(share_min=0.1))["class"].iloc[0] == "weak"


# --- flips -------------------------------------------------------------------

def _universe(rows):
    df = pd.DataFrame(rows).set_index("c")
    df["FROMNAME"] = "F"
    df["TONAME"] = "T"
    return df


def test_flip_shared_bus_different_line_different_contingency():
    df = _universe([
        dict(c="1-2-1@CTGA", FROMNUM=1, TONUM=2, pre_binds=3, post_binds=0, **{"class": "D bearish"}),
        dict(c="2-3-1@CTGB", FROMNUM=2, TONUM=3, pre_binds=0, post_binds=4, **{"class": "A target"}),
    ])
    fl = detect_flips(df)
    assert len(fl) == 1
    r = fl.iloc[0]
    assert (r.fades, r.emerges, r.shared_bus, r.pre, r.post) == ("1-2-1@CTGA", "2-3-1@CTGB", 2, 3, 4)


def test_no_flip_when_same_line_other_contingency():
    df = _universe([
        dict(c="1-2-1@CTGA", FROMNUM=1, TONUM=2, pre_binds=3, post_binds=0, **{"class": "D bearish"}),
        dict(c="1-2-1@CTGB", FROMNUM=1, TONUM=2, pre_binds=0, post_binds=4, **{"class": "A target"}),
    ])
    assert detect_flips(df).empty


def test_no_flip_without_shared_bus():
    df = _universe([
        dict(c="1-2-1@CTGA", FROMNUM=1, TONUM=2, pre_binds=3, post_binds=0, **{"class": "D bearish"}),
        dict(c="5-6-1@CTGA", FROMNUM=5, TONUM=6, pre_binds=0, post_binds=4, **{"class": "A target"}),
    ])
    assert detect_flips(df).empty


def test_no_flip_when_emerging_binder_also_bound_pre():
    df = _universe([
        dict(c="1-2-1@CTGA", FROMNUM=1, TONUM=2, pre_binds=3, post_binds=0, **{"class": "D bearish"}),
        dict(c="2-3-1@CTGB", FROMNUM=2, TONUM=3, pre_binds=1, post_binds=4, **{"class": "A target"}),
    ])
    assert detect_flips(df).empty


def test_flip_dedup_and_sort_by_post_desc():
    df = _universe([
        dict(c="1-2-1@CTGA", FROMNUM=1, TONUM=2, pre_binds=3, post_binds=0, **{"class": "D bearish"}),
        dict(c="2-1-2@CTGB", FROMNUM=2, TONUM=1, pre_binds=0, post_binds=2, **{"class": "weak"}),  # shares both buses
        dict(c="2-3-1@CTGB", FROMNUM=2, TONUM=3, pre_binds=0, post_binds=7, **{"class": "A target"}),
    ])
    fl = detect_flips(df)
    assert list(fl.emerges) == ["2-3-1@CTGB", "2-1-2@CTGB"]
    assert fl.emerges.is_unique


# --- gate --------------------------------------------------------------------

def _gate_row(c, **kw):
    base = {"c": c, "class": "A target", "share": 0.5, "post_days": 4, "RENT_POST": 300_000, "NQUAL": 3,
            "post_binds": 10, "lam_p50_gate": 150.0}
    base.update(kw)
    return base


def _gate(rows, flips=None, **th):
    df = pd.DataFrame(rows).set_index("c")
    fl = flips if flips is not None else pd.DataFrame()
    return stage2_gate(df, fl, Thresholds(**th))


def test_gate_passes_clean_row():
    out = _gate([_gate_row("a")])
    assert list(out.index) == ["a"] and not out.flip_exempt.iloc[0] and not out.thin_intensity.iloc[0]


def test_gate_only_class_a():
    assert _gate([_gate_row("a", **{"class": "B baseline"})]).empty


@pytest.mark.parametrize("col,ok,bad", [
    ("share", 0.25, 0.2499),
    ("post_days", 3, 2),
    ("RENT_POST", 200_000, 199_999),
    ("NQUAL", 2, 1),
])
def test_gate_threshold_boundaries(col, ok, bad):
    assert len(_gate([_gate_row("a", **{col: ok})])) == 1
    assert _gate([_gate_row("a", **{col: bad})]).empty


def test_gate_thresholds_are_parameters():
    assert len(_gate([_gate_row("a", RENT_POST=100_000)], rent_min=50_000)) == 1
    assert _gate([_gate_row("a", NQUAL=3)], nqual_min=4).empty


@pytest.mark.parametrize("post_binds,lam,kept,thin", [
    (4, 150.0, True, True),     # 600 = hard floor, below full -> thin
    (4, 149.9, False, False),   # 599.6 -> dropped
    (10, 100.0, True, False),   # 1000 = full pass
    (10, 99.0, True, True),     # 990 -> thin
])
def test_gate_intensity_bands(post_binds, lam, kept, thin):
    out = _gate([_gate_row("a", post_binds=post_binds, lam_p50_gate=lam)])
    assert (len(out) == 1) == kept
    if kept:
        assert bool(out.thin_intensity.iloc[0]) == thin


def test_gate_flip_target_rescued_and_flagged_exempt():
    flips = pd.DataFrame({"emerges": ["a"]})
    out = _gate([_gate_row("a", post_binds=1, lam_p50_gate=10.0)], flips)
    assert list(out.index) == ["a"]
    assert out.flip_exempt.iloc[0] and not out.thin_intensity.iloc[0]


def test_gate_flip_target_still_needs_gate_columns():
    flips = pd.DataFrame({"emerges": ["a"]})
    assert _gate([_gate_row("a", NQUAL=1, post_binds=1)], flips).empty


def test_gate_flip_target_above_hard_floor_not_exempt():
    flips = pd.DataFrame({"emerges": ["a"]})
    out = _gate([_gate_row("a", post_binds=4, lam_p50_gate=200.0)], flips)
    assert not out.flip_exempt.iloc[0]


def test_gate_sorted_by_rent_desc():
    out = _gate([_gate_row("a", RENT_POST=250_000), _gate_row("b", RENT_POST=900_000)])
    assert list(out.index) == ["b", "a"]


def test_intensity_dropped_lists_hard_floor_losers_not_flip_targets():
    df = pd.DataFrame([_gate_row("a", post_binds=1, lam_p50_gate=10.0), _gate_row("b", post_binds=1, lam_p50_gate=10.0),
                       _gate_row("c")]).set_index("c")
    out = screening.intensity_dropped(df, pd.DataFrame({"emerges": ["b"]}))
    assert list(out.index) == ["a"]
