import importlib.util
import threading
import time
from pathlib import Path

import pandas as pd
import pytest

from pfa import config, mssql, sf

SCOPED = "SELECT * FROM AW.dbo.toAllIsos WHERE isoMarketId = 6 AND teid = 12"
UNSCOPED = "SELECT * FROM AW.dbo.toAllIsos WHERE plannedStartDate > '2026-01-01'"


@pytest.fixture
def fake_db(monkeypatch):
    import awconnect.db

    calls = []

    def fake(sql, database="AW"):
        calls.append((sql, database))
        return pd.DataFrame({"x": [1]})

    monkeypatch.setattr(config, "configure", lambda: None)
    monkeypatch.setattr(awconnect.db, "getDfFromAwDb", fake)
    return calls


def test_unscoped_outage_query_rejected_before_sending(fake_db):
    with pytest.raises(ValueError, match="scoped"):
        mssql.query(UNSCOPED)
    with pytest.raises(ValueError):
        mssql.query("SELECT * FROM aw.dbo.TOALLISOS WHERE isoMarketId = 6")
    with pytest.raises(ValueError):
        mssql.query("SELECT * FROM AW.dbo.toState WHERE teid = 1")
    assert fake_db == []


def test_scoped_outage_query_passes_sql_unchanged(fake_db):
    df = mssql.query(SCOPED)
    assert df["x"].tolist() == [1]
    assert fake_db == [(SCOPED, "AW")]


def test_non_outage_query_needs_no_scope(fake_db):
    sql = "SELECT * FROM AW.dbo.ercotLoadView WHERE date = '2026-01-01'"
    mssql.query(sql)
    assert fake_db == [(sql, "AW")]


def test_queries_from_two_threads_never_overlap(monkeypatch):
    import awconnect.db

    events = []

    def slow(sql, database="AW"):
        events.append("enter")
        time.sleep(0.05)
        events.append("exit")
        return pd.DataFrame()

    monkeypatch.setattr(config, "configure", lambda: None)
    monkeypatch.setattr(awconnect.db, "getDfFromAwDb", slow)
    threads = [threading.Thread(target=mssql.query, args=("SELECT 1",)) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert events == ["enter", "exit", "enter", "exit"]


def test_stage2_dispatch_nodes_goes_through_sf_query(monkeypatch):
    path = Path(__file__).resolve().parents[1] / "scripts" / "build_stage2_list.py"
    spec = importlib.util.spec_from_file_location("build_stage2_list", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    seen = []

    def fake_query(db_name, sql):
        seen.append((db_name, sql))
        return pd.DataFrame({"FN": ["1"], "TN": ["2"], "KK": ["1"], "GG": ["CTG"], "NQUAL": [3], "MAXSF": [0.5]})

    monkeypatch.setattr(sf, "query", fake_query)
    universe = pd.DataFrame({"post_binds": [1], "pre_binds": [0]}, index=["1-2-1@CTG"])
    out = mod.bulk_dispatch_nodes(universe, 14412)
    assert seen and seen[0][0] == "SHIFT_FACTORS"
    assert out.loc["1-2-1@CTG", "NQUAL"] == 3
