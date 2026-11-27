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


def _multi_result(labels, required, spsum, dates=None, holidays=(), hol_periods=(), ctx_sum=None, ctx=None):
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
        holiday_binding=ps.holiday_binding(ctx_sum, per, labels, holidays, ctx))


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


def _ctx(n_onpeak, n_holiday):
    """Context-study runs frame as run_multi builds it: ONPEAK flag and HOLIDAY flag per run."""
    return pd.DataFrame({"ONPEAK": [True] * n_onpeak, "HOLIDAY": [i < n_holiday for i in range(n_onpeak)]})


def test_holiday_line_periods_grain_when_no_study_runs_were_read():
    r = _multi_result(["X1", "X2"], ["X1", "X2"], {"X1": [1.0, 0.0, 2.0], "X2": [0.0, 1.0, 0.0]}, holidays=["2026-12-25"], hol_periods=[2],
                      dates=["2026-12-01", "2026-12-10,2026-12-11", "2026-12-24,2026-12-25"])
    text = "\n".join(rpt.multi_caveats(r))
    assert ("Dec 25: holiday filter effect" in text and "The Dec 25 topology is one of the 3 PathOpt periods (study 1); "
            "1 binding periods fall on a listed holiday (X1: 1)" in text)
    assert "In study" not in text


def test_holiday_line_runs_grain_names_the_context_study_and_its_run_counts():
    ctx_sum = pd.DataFrame({"constraint": ["X1", "X2"], "onpeak_binding_on_holiday": [2, 0]})
    r = _multi_result(["X1", "X2"], ["X1", "X2"], {"X1": [1.0, 0.0], "X2": [0.0, 1.0]}, holidays=["2026-12-25"], hol_periods=[1],
                      dates=["2026-12-01", "2026-12-25"], ctx_sum=ctx_sum, ctx=_ctx(160, 16))
    text = "\n".join(rpt.multi_caveats(r))
    assert "In study 2, 16 of the 160 on-peak runs fall on a listed holiday; 2 binding runs fall on a listed holiday (X1: 2)" in text
    assert "The Dec 25 topology is one of the 2 PathOpt periods (study 1)." in text and "binding periods" not in text


def test_holiday_line_runs_grain_with_no_binding_run_on_the_holiday():
    ctx_sum = pd.DataFrame({"constraint": ["X1"], "onpeak_binding_on_holiday": [0]})
    r = _multi_result(["X1"], ["X1"], {"X1": [1.0, 0.0]}, holidays=["2026-12-25"], hol_periods=[1],
                      dates=["2026-12-01", "2026-12-25"], ctx_sum=ctx_sum, ctx=_ctx(100, 8))
    text = "\n".join(rpt.multi_caveats(r))
    assert "In study 2, 8 of the 100 on-peak runs fall on a listed holiday; no binding runs fall on a listed holiday." in text


def test_holiday_listed_but_outside_the_data_window_prints_nothing():
    ctx_sum = pd.DataFrame({"constraint": ["X1"], "onpeak_binding_on_holiday": [0]})
    r = _multi_result(["X1"], ["X1"], {"X1": [1.0, 0.0]}, holidays=["2027-01-01"], hol_periods=[],
                      dates=["2026-12-01", "2026-12-02"], ctx_sum=ctx_sum, ctx=_ctx(100, 0))
    text = "\n".join(rpt.multi_caveats(r))
    assert "listed holiday" not in text and "holiday filter effect" not in text
    r = _multi_result(["X1"], ["X1"], {"X1": [1.0, 0.0]}, holidays=["2027-01-01"], hol_periods=[], dates=["2026-12-01", "2026-12-02"])
    assert "listed holiday" not in "\n".join(rpt.multi_caveats(r))


def test_holiday_binding_falls_back_to_period_dates_without_study_runs():
    per = pd.DataFrame({"DATES": ["2026-12-01", "2026-12-24,2026-12-25"], "SPSUM_X1": [0.0, 4.0]})
    assert ps.holiday_binding(None, per, ["X1"], {"2026-12-25"}) == {"basis": "periods", "by_leg": {"X1": 1}, "total": 1}
    assert ps.holiday_binding(None, per, ["X1"], {"2026-12-26"})["total"] == 0


def test_no_holidays_means_no_holiday_line():
    text = "\n".join(rpt.multi_caveats(_multi_result(["X1"], ["X1"], {"X1": [1.0, 0.0]})))
    assert "holiday filter effect" not in text


def test_readme_records_the_actual_command():
    r = _multi_result(["X1"], ["X1"], {"X1": [1.0, 0.0]})
    cmd = rpt.invocation(["--study", "14966", "--holidays", "2026-12-25", "--constraints", "A=1-2-1@X Y"])
    assert cmd == "uv run pfa paths --study 14966 --holidays 2026-12-25 --constraints 'A=1-2-1@X Y'"
    readme = rpt.multi_readme(r, cmd)
    assert cmd in readme and "scripts/pathopt_scatter.py" not in readme and "--holidays 2026-12-25" in readme


def _spread_result(runs_both, n_runs=6, n_both=0, n=4, long_runs=3, short_runs=3):
    import types
    cand = pd.DataFrame({"SOURCENAME": ["A"], "SINKNAME": ["B"], "OPTIONPRICE": [1.0], "MIN_SF_L": [0.2], "AVG_SF_L": [0.3],
                         "VALUE_LONG": [0.5], "FAMILY_SIZE": [1], "FAMILY_MEMBERS": ["A"]})
    cb = {"n_both": n_both, "n_periods": n, "long_binds": 2, "short_binds": 2,
          "runs_both": runs_both, "n_runs": n_runs, "long_runs": long_runs, "short_runs": short_runs}
    d = ps.SpreadDirection("L", ["S"], {0.02: {"long_only": 1}}, 10, cand, cand, 1, 0.5, 20, 0.1, cb, "c.csv", cand)
    cand2 = cand.assign(MIN_SF_S=0.2, AVG_SF_S=0.3)
    d2 = ps.SpreadDirection("S", ["L"], {0.02: {"long_only": 1}}, 10, cand2, cand2, 1, 0.5, 20, 0.1,
                            {**cb, "long_runs": short_runs, "short_runs": long_runs}, "c2.csv", cand)
    empty = pd.DataFrame({"a": [1]})
    return types.SimpleNamespace(spec=_spec(["L", "S"], ["L"], short=["S"]), po_study=1, n_runs=n_runs, n_periods=n, directions=[d, d2],
                                 comp=empty, co_live=empty, sp_scale={"L": 1.0, "S": 2.0}, live_counts={"L": 3, "S": 3})


def test_spread_without_cobinding_keeps_never_co_bind_sentence_and_no_warning():
    r = _spread_result(0)
    html = rpt.spread_html(r)
    assert "valid because L and S never co-bind" in html and 'class="warning"' not in html and "in any run" not in html


def test_spread_with_cobinding_warns_once_for_both_directions():
    r = _spread_result(2, n_both=3)
    html = rpt.spread_html(r)
    assert html.count('class="warning"') == 1 and html.index('class="warning"') < html.index("Top families")
    assert "L and S co-bind in 2 of 6 runs (3 of 4 periods; L binds in 3 runs, S in 3)" in html and "never co-bind" not in html
    assert "NOT valid in the 2 of 6 runs where L and S co-bind" in html
    readme = rpt.spread_readme(r, "uv run pfa paths --study 1")
    assert readme.count("> WARNING:") == 1 and "uv run pfa paths --study 1" in readme


def test_spread_period_overlap_without_run_overlap_does_not_warn():
    r = _spread_result(0, n_both=1)
    html = rpt.spread_html(r)
    assert 'class="warning"' not in html
    assert "valid because L and S never co-bind in any run (they share 1 of 4 periods)" in html


def _legs_from_runs(sp_runs, run_period, topo):
    """What run_spread does: per-run SP arrays -> per-period sums (weights) and the cobind dict."""
    sp = {l: pd.Series(v, dtype=float) for l, v in sp_runs.items()}
    rp = pd.Series(run_period)
    weights = {l: ps.period_sums(sp[l], rp, topo) for l in sp}
    return weights, {l: sp[l].values for l in sp}


def test_spread_cobind_shared_period_but_no_shared_run_is_not_cobinding():
    # runs 0,1 sit in period 'a'; L binds in run 0, S in run 1: the period sums overlap, no run does
    weights, sp_run = _legs_from_runs({"L": [5.0, 0.0, 0.0, 0.0], "S": [0.0, 7.0, 0.0, 2.0]}, ["a", "a", "b", "b"], ["a", "b"])
    cb = ps.spread_cobind(weights, sp_run, "L", ["S"])
    assert cb["n_both"] == 1 and cb["runs_both"] == 0 and cb["n_runs"] == 4 and (cb["long_runs"], cb["short_runs"]) == (1, 2)
    r = _spread_result(cb["runs_both"], n_runs=cb["n_runs"], n_both=cb["n_both"], n=cb["n_periods"])
    assert 'class="warning"' not in rpt.spread_html(r)


def test_spread_cobind_shared_runs_warns():
    weights, sp_run = _legs_from_runs({"L": [5.0, 3.0, 0.0, 0.0], "S": [0.0, 7.0, 0.0, 2.0]}, ["a", "a", "b", "b"], ["a", "b"])
    cb = ps.spread_cobind(weights, sp_run, "L", ["S"])
    assert cb["runs_both"] == 1 and cb["n_both"] == 1
    r = _spread_result(cb["runs_both"], n_runs=cb["n_runs"], n_both=cb["n_both"], n=cb["n_periods"])
    assert "L and S co-bind in 1 of 4 runs (1 of 2 periods" in rpt.spread_html(r)


def test_spread_cobind_any_of_several_shorts():
    weights, sp_run = _legs_from_runs({"L": [1.0, 0.0], "S": [0.0, 0.0], "S2": [1.0, 0.0]}, ["a", "b"], ["a", "b"])
    assert ps.spread_cobind(weights, sp_run, "L", ["S"])["runs_both"] == 0
    assert ps.spread_cobind(weights, sp_run, "L", ["S", "S2"])["runs_both"] == 1


def test_paths_spread_without_required_is_an_argparse_error(capsys):
    from pfa.cli import paths as cmd
    import pytest

    with pytest.raises(SystemExit) as e:
        cmd.main(["--study", "1", "--runs", "A=1,B=2", "--short", "B", "--holidays", "", "--constraints", "A=1-2-1@X"])
    assert e.value.code == 2 and "--required" in capsys.readouterr().err


def test_legacy_date_is_normalised_once_for_the_output_folder(monkeypatch, tmp_path):
    from pfa import config
    from pfa.cli import paths as cmd

    seen = {}
    monkeypatch.setattr(cmd, "run_pair", lambda args: seen.setdefault("date", args.date))
    cmd.main(["--study", "1", "--run-x", "1", "--run-y", "2", "--date", "2026-11-5", "--hour", "18"])
    assert seen["date"] == "2026-11-05"
    monkeypatch.setattr(config, "OUTPUT_ROOT", tmp_path)


def test_pathspec_parsing_defaults_required_to_all_but_last():
    s = ps.PathSpec.from_strings(study=1, runs="A=1,B=2,C=3", value_only="V=9", required=None, short=None, constraints="A=1-2-1@X",
                                 floor=0.05, pool=5, holidays="2026-12-25,2026-01-01")
    assert s.required == ["A", "B"] and s.all_labels == ["A", "B", "C", "V"] and s.constraints["A"] == (1, 2, "1", "X")
    assert s.holidays == {"2026-12-25", "2026-01-01"}
