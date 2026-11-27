import pandas as pd

from pfa.analysis import lambda_dist, study_compare
from pfa.report import compare as compare_report
from pfa.report import lambda_dist as lambda_report
from pfa.report import load_profile, value


def test_lambda_report_stops_where_the_analysis_stopped():
    r = lambda_dist.LambdaDist(1, "1-2-1@X")
    assert lambda_report.text(r).endswith("no relief-set units found (SF band empty or unmapped)")
    r.stage = "offers"
    assert lambda_report.text(r).endswith("no DAM offer/capacity data for mapped resources")


def test_lambda_report_full_distribution():
    disp = pd.DataFrame({c: [1] for c in ["BUSNUM", "ID", "SIDE", "SF", "SCED", "IS_RENEWABLE", "P60", "HSL", "AWARDED", "LSL"]})
    r = lambda_dist.LambdaDist(1, "1-2-1@X", "done", disp, 2, 3, 1, [(25, 10.0), (50, None)], 7, 120.4,
                               {"n_hours": 10, "n_priced": 8, "n_unpriceable": 2, "exhaustion_depth_mw": 90.0},
                               {"P25": 1, "P50": 2, "P75": 3, "P90": 4, "max": 5, "n": 8},
                               [("solar", {"P50": 1, "P90": 2, "n": 3}), ("dark", None)])
    t = lambda_report.text(r)
    assert "UP stack: 2 units, DOWN stack: 3 units (1 curtailment)" in t and "lambda=$10.0" in t and "lambda=n/a" in t
    assert "exhausts at D=90.0 MW of flow (120 MW of paired capacity)" in t and "dark: no priced hours" in t.replace("  dark", " dark")


def test_value_fact_sheet_and_mark_table():
    fs = value.fact_sheet({"constraint": "k", "study_id": 1, "n_binding_cases": 2, "n_total_cases": 5, "n_total_study_runs": 9,
                           "lambda_stats": {"mean": 3.0}, "marginal_units": [{"u": 1}]})
    assert "binding cases: 2 / 5 rows flagged" in fs and "    mean: 3.0" in fs and '{"u": 1}' in fs
    import types
    stats = types.SimpleNamespace(n_window_runs=2, p_bind={18: 0.504}, lam=pd.DataFrame({"p50": [12.34]}, index=[18]))
    table = pd.DataFrame({"lam_col": ["p50"], "sf": [1.0], "outage_onpeak_days": [5], "rent_per_mw_month": [1.0], "dollars_per_mwh": [2.0]})
    t = value.monthly_mark("k", ("2026-09-16", "2026-10-02"), stats, table)
    assert "(2 runs in window)" in t and "P(bind | sim hour): {18: 0.5}" in t and "12.3" in t and "dollars_per_mwh" in t


def test_compare_studies_splits_persisting_new_dropped(monkeypatch):
    def frame(keys):
        return pd.DataFrame({"CONSTRAINT": keys, "USD_MWH_P50": 1.0, "RENT_SCORE": range(len(keys), 0, -1),
                             "TICKET": "t", "TICKET_STATUS": "s", "DRIVER": "d"})
    monkeypatch.setattr(study_compare, "study_frame", lambda s, m: frame(["a", "b"] if s == 1 else ["b", "c"]))
    monkeypatch.setattr(study_compare, "enrich_new", lambda new, study, top: new)
    c = study_compare.compare_studies(1, 2, (2026, 9))
    assert list(c.persist["CONSTRAINT"]) == ["b"] and list(c.new["CONSTRAINT"]) == ["c"] and list(c.dropped["CONSTRAINT"]) == ["a"]
    assert "USD_MWH_P50_A" in c.persist.columns
    assert compare_report.console_new(c.new, 5).startswith("CONSTRAINT")


def test_load_profile_table_and_page():
    df = pd.DataFrame({"year": [2024, 2025], "he": [1, 1], "median_load_gw": [30.123, 31.0]})
    assert load_profile.table(df).loc[1, 2024] == 30.12
    fig = load_profile.build_figure(df, "09-16", "09-30")
    assert "Plotly.newPlot" in load_profile.render(fig) and load_profile.mon("09-16") == "sep"
