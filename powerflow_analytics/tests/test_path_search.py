import numpy as np
import pandas as pd

from pfa.analysis import path_search as ps
from pfa.report import path_search as rpt


def test_sf_stats_ignores_dead_periods():
    S = np.array([[0.1, np.nan, 0.3], [np.nan, np.nan, np.nan]], dtype=np.float32)
    st = ps.sf_stats(S)
    assert st.loc[0, "BINDINGPAIRCOUNT"] == 2
    assert np.isclose(st.loc[0, "MIN_SF"], 0.1) and np.isclose(st.loc[0, "AVG_SF"], 0.2)
    assert np.isnan(st.loc[1, "MIN_SF"])


def test_find_pairs_complementary_legs():
    pool = pd.DataFrame({"OPTIONPRICE": [1.0, 1.0], "VALUE_REQ": [2.0, 2.0]})
    S = {"a": np.array([[0.3, 0.3], [-0.1, -0.1]], dtype=np.float32),
         "b": np.array([[-0.1, -0.1], [0.3, 0.3]], dtype=np.float32)}
    out = ps.find_pairs(pool, S, ["a", "b"], floor=0.1)
    assert len(out) == 1 and np.isclose(out.loc[0, "MIN_SF_a"], 0.2) and np.isclose(out.loc[0, "PRICE"], 2.0)


def test_dedup_multi_collapses_aliases():
    df = pd.DataFrame({"SOURCENAME": ["B", "A", "C"], "SINKNAME": ["X", "X", "Y"],
                       "OPTIONPRICE": [1.0, 1.0, 2.0], "MIN_SF_k": [0.1, 0.1, 0.1]})
    out = ps.dedup_multi(df, ["MIN_SF_k", "OPTIONPRICE"])
    assert len(out) == 2 and out.set_index("SOURCENAME").loc["A", "ALIAS_COUNT"] == 2


def _spec(labels, required, holidays=(), short=()):
    return ps.PathSpec(study=2, runs={l: i for i, l in enumerate(labels)}, value_only={}, constraints={}, required=list(required),
                       short=list(short), floor=0.05, pool=10, holidays=frozenset(holidays))


def _multi_result(labels, required, spsum, dates=None, holidays=(), hol_periods=(), ctx_sum=None):
    import types
    n = len(next(iter(spsum.values())))
    per = pd.DataFrame({"TOPOLOGYID": range(n), "DATES": dates or [f"2026-12-{i + 1:02d}" for i in range(n)]})
    for l in labels:
        per[f"LIVE_{l}"], per[f"SPSUM_{l}"] = True, spsum.get(l, [0.0] * n)
    sf = {f"{k}_{l}": [0.2, 0.3] for l in labels for k in ("MIN_SF", "AVG_SF")}
    cand = pd.DataFrame({"SOURCENAME": ["A", "B"], "SINKNAME": ["C", "D"], "OPTIONPRICE": [1.0, 2.0], "VO_SHARE": [0.1, 0.2], **sf})
    empty = pd.DataFrame()
    spec = _spec(labels, required, holidays)
    return types.SimpleNamespace(
        spec=spec, po_study=1, ctg_label="CTG", n_runs=5, per=per, cand=cand, fam=cand, nm=cand, ov=cand, ptt=empty, pairs=empty,
        counts=empty, repro=empty, ctx_sum=ctx_sum, sp_tab=pd.DataFrame({"constraint": labels, "n_runs_with_sp": [1] * len(labels)}),
        price_cons=pd.DataFrame({"ok": [True]}), corr_o=pd.DataFrame({"x": [1.0]}), corr_u=pd.DataFrame({"x": [1.0]}),
        floors={0.05: 1}, floors_b={0.05: 1}, hs={"floor": 0.05}, holiday_periods=list(hol_periods),
        holiday_binding=ps.holiday_binding(ctx_sum, per, labels, holidays))


def _multi_html(*a, **k):
    return rpt.multi_html(_multi_result(*a, **k))


def test_multi_report_one_required_leg():
    html = _multi_html(["X1"], ["X1"], {"X1": [1.0, 0.0]})
    assert "never co-bind" not in html and "co-bind in" not in html and "one required constraint only" in html


def test_multi_report_never_binding_leg_does_not_crash():
    html = _multi_html(["X1", "X2"], ["X1", "X2"], {"X1": [1.0, 0.0]})
    assert "No binding period for X2" in html and "never co-bind" not in html


def test_multi_report_cobind_is_computed_and_no_14966_text():
    html = _multi_html(["X1", "X2"], ["X1", "X2"], {"X1": [1.0, 0.0], "X2": [2.0, 3.0]})
    assert "X1 and X2 co-bind in 1 of 2 periods" in html and "never co-bind" not in html
    assert "Blessing" not in html and "JCK" not in html and "PCT_RN" not in html
    html = _multi_html(["X1", "X2"], ["X1", "X2"], {"X1": [1.0, 0.0], "X2": [0.0, 3.0]})
    assert "X1 and X2 never co-bind" in html


def test_multi_report_three_required_legs_say_three():
    html = _multi_html(["X1", "X2", "X3"], ["X1", "X2", "X3"], {"X1": [1.0, 0.0], "X2": [0.0, 1.0], "X3": [0.0, 1.0]})
    assert "counts the three required constraints only" in html


def test_holiday_line_miss_states_no_binding_runs():
    r = _multi_result(["X1"], ["X1"], {"X1": [1.0, 0.0]}, holidays=["2026-12-25"], hol_periods=[1],
                      dates=["2026-12-01", "2026-12-25"])
    text = "\n".join(rpt.multi_caveats(r))
    assert "The Dec 25 topology is one of the 2 PathOpt periods; no binding runs fall on it." in text


def test_holiday_line_hit_states_the_count_from_binding_runs():
    ctx = pd.DataFrame({"constraint": ["X1", "X2"], "onpeak_binding_on_holiday": [2, 0]})
    r = _multi_result(["X1", "X2"], ["X1", "X2"], {"X1": [1.0, 0.0], "X2": [0.0, 1.0]}, holidays=["2026-12-25"], hol_periods=[1],
                      dates=["2026-12-01", "2026-12-25"], ctx_sum=ctx)
    text = "\n".join(rpt.multi_caveats(r))
    assert "2 binding runs fall on a listed holiday (X1: 2)" in text and "no binding runs" not in text


def test_holiday_binding_falls_back_to_period_dates_without_study_runs():
    per = pd.DataFrame({"DATES": ["2026-12-01", "2026-12-25"], "SPSUM_X1": [0.0, 4.0]})
    assert ps.holiday_binding(None, per, ["X1"], {"2026-12-25"}) == {"basis": "periods", "by_leg": {"X1": 1}, "total": 1}
    assert ps.holiday_binding(None, per, ["X1"], {"2026-12-26"})["total"] == 0


def test_no_holidays_means_no_holiday_line():
    text = "\n".join(rpt.multi_caveats(_multi_result(["X1"], ["X1"], {"X1": [1.0, 0.0]})))
    assert "holiday filter effect" not in text


def test_readme_records_the_actual_command():
    r = _multi_result(["X1"], ["X1"], {"X1": [1.0, 0.0]})
    cmd = rpt.invocation(["pfa paths", "--study", "14966", "--constraints", "A=1-2-1@X Y"])
    assert cmd == "pfa paths --study 14966 --constraints 'A=1-2-1@X Y'"
    readme = rpt.multi_readme(r, cmd)
    assert cmd in readme and "scripts/pathopt_scatter.py" not in readme
    assert rpt.invocation(["/x/scripts/pathopt_scatter.py", "--study", "1"]) == "/x/scripts/pathopt_scatter.py --study 1"


def _spread_result(both, n=4, long_binds=2, short_binds=2):
    import types
    cand = pd.DataFrame({"SOURCENAME": ["A"], "SINKNAME": ["B"], "OPTIONPRICE": [1.0], "MIN_SF_L": [0.2], "AVG_SF_L": [0.3],
                         "VALUE_LONG": [0.5], "FAMILY_SIZE": [1], "FAMILY_MEMBERS": ["A"]})
    d = ps.SpreadDirection("L", ["S"], {0.02: {"long_only": 1}}, 10, cand, cand, 1, 0.5, 20, 0.1,
                           {"n_both": both, "n_periods": n, "long_binds": long_binds, "short_binds": short_binds}, "c.csv", cand)
    empty = pd.DataFrame({"a": [1]})
    return types.SimpleNamespace(spec=_spec(["L", "S"], ["L"], short=["S"]), po_study=1, n_runs=3, n_periods=n, directions=[d],
                                 comp=empty, co_live=empty, sp_scale={"L": 1.0, "S": 2.0}, live_counts={"L": 3, "S": 3})


def test_spread_without_cobinding_keeps_never_co_bind_sentence_and_no_warning():
    r = _spread_result(0)
    html = rpt.spread_html(r)
    assert "valid because L and S never co-bind" in html and 'class="warning"' not in html


def test_spread_with_cobinding_warns_and_says_overstated():
    r = _spread_result(2)
    html = rpt.spread_html(r)
    assert html.index('class="warning"') < html.index("Top families")
    assert "co-bind in 2 of 4 periods" in html and "overstated" in html and "never co-bind" not in html
    assert "NOT valid in the 2 of 4 periods" in html
    assert "> WARNING: Long L / short S: the legs co-bind in 2 of 4 periods" in rpt.spread_readme(r, "pfa paths")


def test_spread_cobind_counts_periods_where_both_have_shadow_price():
    w = {"L": [1.0, 0.0, 2.0, 0.0], "S": [0.0, 0.0, 3.0, 1.0], "S2": [0.0, 0.0, 0.0, 0.0]}
    assert ps.spread_cobind(w, "L", ["S"]) == {"n_both": 1, "n_periods": 4, "long_binds": 2, "short_binds": 2}
    assert ps.spread_cobind(w, "L", ["S2"])["n_both"] == 0


def test_pathspec_parsing_defaults_required_to_all_but_last():
    s = ps.PathSpec.from_strings(study=1, runs="A=1,B=2,C=3", value_only="V=9", required=None, short=None, constraints="A=1-2-1@X",
                                 floor=0.05, pool=5, holidays="2026-12-25,2026-01-01")
    assert s.required == ["A", "B"] and s.all_labels == ["A", "B", "C", "V"] and s.constraints["A"] == (1, 2, "1", "X")
    assert s.holidays == {"2026-12-25", "2026-01-01"}
