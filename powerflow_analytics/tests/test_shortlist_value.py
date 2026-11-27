import pandas as pd

from pfa.analysis import shortlist_value as sv
from pfa.analysis.shortlist_value import coverage_and_days, month_bind_dates


def _synthetic_runs():
    return pd.DataFrame({"RUNID": [1, 2, 3, 4], "SIMDATE": ["2026-08-01", "2026-08-02", "2026-09-16", "2026-09-17"]})


def _synthetic_ctgviol(binding_runids):
    return pd.DataFrame([
        {"RUNID": rid, "FROMNUM": 100, "TONUM": 200, "CKT": "1", "CTGLABEL": "X",
         "LIMVIOLPCT": 100.0 if rid in binding_runids else 50.0}
        for rid in [1, 2, 3, 4]
    ])


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


class _FakeCache:
    def __init__(self, study):
        pass

    def load(self, table, columns=None):
        if table == "opfrun":
            return _synthetic_runs()
        if table == "outctgviol2":
            return _synthetic_ctgviol({3})
        return pd.DataFrame(columns=columns or [])


def test_value_shortlist_lookup_failure_is_visible_and_run_continues(monkeypatch, tmp_path):
    from pfa import config
    from pfa.analysis.screening import ScreeningResult, Thresholds

    (tmp_path / "study_1").mkdir()
    pd.DataFrame({"CONSTRAINT": ["100-200-1@X", "100-200-1@Y"], "DRIVER_TICKET": [None, None],
                  "DRIVER_TICKET_START": [None, None], "DRIVER_TICKET_END": [None, None]}
                 ).to_csv(tmp_path / "study_1" / "ranked_constraints.csv", index=False)
    monkeypatch.setattr(config, "OUTPUT_ROOT", tmp_path)
    monkeypatch.setattr(sv, "StudyCache", _FakeCache)
    monkeypatch.setattr(sv.gen_mapping, "fetch_genunit_sced_name", lambda: pd.DataFrame())
    monkeypatch.setattr(sv.marginal_units, "bus_name_map", lambda b: {})

    def fake_value_row(study, c, *a):
        if c.endswith("@Y"):
            raise RuntimeError("boom")
        return {"_status": "no fast-scan config"}

    monkeypatch.setattr(sv, "value_row", fake_value_row)
    short = pd.DataFrame({"x": [1, 2]}, index=["100-200-1@X", "100-200-1@Y"])
    res = ScreeningResult(1, "2026-09-15", Thresholds(), pd.Series(dtype=float), short, pd.DataFrame(), short, short)
    out = sv.value_shortlist(res, "2026-09")
    assert list(out.columns[:1]) == ["x"] and set(sv.value_columns("2026-09")) <= set(out.columns)
    assert out.loc["100-200-1@X", "status"] == "no fast-scan config"
    assert out.loc["100-200-1@X", "coverage"] == "0.5(days-proxy)"
    assert out.loc["100-200-1@Y", "status"] == "lookup failed: RuntimeError: boom"
