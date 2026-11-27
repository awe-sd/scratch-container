import numpy as np
import pandas as pd

from pfa.analysis import path_scatter as ps


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


def _multi_report(tmp_path, labels, required, spsum, dates=None):
    import types
    n = len(next(iter(spsum.values())))
    per = pd.DataFrame({"TOPOLOGYID": range(n), "DATES": dates or [f"2026-12-{i + 1:02d}" for i in range(n)]})
    for l in labels:
        per[f"LIVE_{l}"], per[f"SPSUM_{l}"] = True, spsum.get(l, [0.0] * n)
    sf = {f"{k}_{l}": [0.2, 0.3] for l in labels for k in ("MIN_SF", "AVG_SF")}
    cand = pd.DataFrame({"SOURCENAME": ["A", "B"], "SINKNAME": ["C", "D"], "OPTIONPRICE": [1.0, 2.0], "VO_SHARE": [0.1, 0.2], **sf})
    ov = cand.copy()
    cfg = {l: types.SimpleNamespace(STUDYID=1, CTGLABEL="CTG") for l in labels}
    args = types.SimpleNamespace(min_sf_each=0.05, holidays=None, pool=10, study=2, runs="", value_only="", constraints="")
    sp_tab = pd.DataFrame({"constraint": labels, "n_runs_with_sp": [1] * len(labels)})
    empty, corr = pd.DataFrame(), pd.DataFrame({"x": [1.0]})
    ps.build_multi_report(
        tmp_path, args, labels, required, {l: i for i, l in enumerate(labels)}, cfg, empty,
        pd.DataFrame({"ok": [True]}), empty, sp_tab, None, ov, cand, empty, empty, corr, corr, None,
        {0.05: 1}, "none", per, {0.05: 1}, {l: 1.0 for l in labels}, 5, cand, cand)
    return (tmp_path / "report.html").read_text()


def test_multi_report_one_required_leg(tmp_path):
    html = _multi_report(tmp_path, ["X1"], ["X1"], {"X1": [1.0, 0.0]})
    assert "never co-bind" not in html and "co-bind in" not in html and "one required constraint only" in html


def test_multi_report_never_binding_leg_does_not_crash(tmp_path):
    html = _multi_report(tmp_path, ["X1", "X2"], ["X1", "X2"], {"X1": [1.0, 0.0]})
    assert "No binding period for X2" in html and "never co-bind" not in html


def test_multi_report_cobind_is_computed_and_no_14966_text(tmp_path):
    html = _multi_report(tmp_path, ["X1", "X2"], ["X1", "X2"], {"X1": [1.0, 0.0], "X2": [2.0, 3.0]})
    assert "X1 and X2 co-bind in 1 of 2 periods" in html and "never co-bind" not in html
    assert "Blessing" not in html and "JCK" not in html and "PCT_RN" not in html
    html = _multi_report(tmp_path, ["X1", "X2"], ["X1", "X2"], {"X1": [1.0, 0.0], "X2": [0.0, 3.0]})
    assert "X1 and X2 never co-bind" in html
