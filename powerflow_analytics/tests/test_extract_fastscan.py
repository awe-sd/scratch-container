import pandas as pd

from pfa.extract import fastscan


def _capture(monkeypatch, module, canned):
    calls = []

    def fake_query(db, sql):
        calls.append((db, sql))
        return canned

    monkeypatch.setattr(module.sf, "query", fake_query)
    return calls


def test_find_configs_scopes_study_branch_ctg_and_active(monkeypatch):
    canned = pd.DataFrame({"CONFIG_ID": [7], "DIRECTION": [1]})
    calls = _capture(monkeypatch, fastscan, canned)
    out = fastscan.find_configs(14412, 1436, 2081, "DWCSRAM5")
    sql = calls[0][1]
    assert "FAST_SCAN_CONFIG" in sql and "STUDY_ID = 14412" in sql
    assert "FROM_NUM = 1436" in sql and "TO_NUM = 2081" in sql
    assert "CTG_LABEL = 'DWCSRAM5'" in sql and "IS_ACTIVE" in sql
    assert out is canned


def test_config_scoped_readers_filter_on_config_id(monkeypatch):
    canned = pd.DataFrame({"TIMESTAMP": [], "HEADROOM": []})
    for fn in (fastscan.headroom_profile, fastscan.negative_headroom,
               fastscan.solar_impact, fastscan.headroom_with_curtailment):
        calls = _capture(monkeypatch, fastscan, canned)
        assert fn(99) is canned
        assert "FAST_SCAN_RESULTS" in calls[0][1] and "CONFIG_ID = 99" in calls[0][1]
    calls = _capture(monkeypatch, fastscan, canned)
    fastscan.negative_headroom(99)
    assert "HEADROOM < 0" in calls[0][1]


def test_headroom_for_month_and_window_predicates(monkeypatch):
    canned = pd.DataFrame({"TIMESTAMP": []})
    calls = _capture(monkeypatch, fastscan, canned)
    assert fastscan.headroom_for_month(5, 9) is canned
    assert "CONFIG_ID = 5" in calls[0][1] and "MONTH(TIMESTAMP) = 9" in calls[0][1]
    calls = _capture(monkeypatch, fastscan, canned)
    assert fastscan.headroom_window(5, "2026-04-01", "2026-09-28") is canned
    sql = calls[0][1]
    assert "CONFIG_ID = 5" in sql and "TIMESTAMP >= '2026-04-01'" in sql and "TIMESTAMP < '2026-09-28'" in sql
    assert "HEADROOM_RT" in sql
