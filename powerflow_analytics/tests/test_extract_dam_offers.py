import pandas as pd
import pytest

from pfa.extract import dam_offers


def _fake(monkeypatch, canned):
    calls = []

    def q(db, sql):
        calls.append((db, sql))
        return canned

    monkeypatch.setattr(dam_offers.sf, "query", q)
    return calls


def test_latest_curves_at_hours_scopes_points_hours_window(monkeypatch):
    canned = pd.DataFrame({"SETTLEMENTPOINTNAME": ["A"]})
    calls = _fake(monkeypatch, canned)
    out = dam_offers.latest_curves_at_hours(["A", "B'x", None], hours=(12, 18))
    sql = calls[0][1]
    assert out is canned
    assert "ERCOT60DDAMGENRESOURCE" in sql and "DATEADD(day, -14" in sql
    assert "HOURENDING IN (12,18)" in sql and "'Bx'" in sql and "'A'" in sql and "CURVEPRICE10" in sql
    assert dam_offers.latest_curves_at_hours([]).empty


def test_latest_capacity_rows_scope_and_truncation_guard(monkeypatch):
    canned = pd.DataFrame({"SETTLEMENTPOINTNAME": ["A"]})
    calls = _fake(monkeypatch, canned)
    assert dam_offers.latest_capacity_rows(["A"], 7, 22) is canned
    sql = calls[0][1]
    assert "HOURENDING BETWEEN 7 AND 22" in sql and "AWARDEDQUANTITY" in sql and "SETTLEMENTPOINTNAME IN ('A')" in sql
    big = pd.DataFrame({"SETTLEMENTPOINTNAME": ["A"] * dam_offers.CAPACITY_ROW_LIMIT})
    _fake(monkeypatch, big)
    with pytest.raises(RuntimeError):
        dam_offers.latest_capacity_rows(["A"])


def test_resolve_genids_quotes_the_pattern(monkeypatch):
    calls = _fake(monkeypatch, pd.DataFrame({"GENID": [7], "RESOURCENAME": ["X"]}))
    assert dam_offers._resolve_genids("O'NEAL%") == [7]
    assert "ILIKE 'O''NEAL%'" in calls[0][1]


def test_latest_delivery_date_and_point_coverage_scope(monkeypatch):
    calls = _fake(monkeypatch, pd.DataFrame({"D": [pd.Timestamp("2026-09-26")]}))
    assert str(dam_offers.latest_delivery_date()) == "2026-09-26"
    assert "MAX(DELIVERYDATE)" in calls[0][1]
    calls = _fake(monkeypatch, pd.DataFrame({"settlementpointname": ["A"], "n_all": [3]}))
    out = dam_offers.point_coverage(["A", "B'x"])
    sql = calls[0][1]
    assert "SETTLEMENTPOINTNAME IN (" in sql and "'Bx'" in sql and "GROUP BY SETTLEMENTPOINTNAME" in sql
    assert list(out.columns) == ["SETTLEMENTPOINTNAME", "N_ALL"]
    assert dam_offers.point_coverage([]).empty
