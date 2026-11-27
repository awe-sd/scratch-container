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
    from pfa.analysis import screening as mod
    seen = []

    def fake_query(db_name, sql):
        seen.append((db_name, sql))
        return pd.DataFrame({"FN": ["1"], "TN": ["2"], "KK": ["1"], "GG": ["CTG"], "NQUAL": [3], "MAXSF": [0.5]})

    monkeypatch.setattr(sf, "query", fake_query)
    universe = pd.DataFrame({"post_binds": [1], "pre_binds": [0]}, index=["1-2-1@CTG"])
    out = mod.bulk_dispatch_nodes(universe, 14412)
    assert seen and seen[0][0] == "SHIFT_FACTORS"
    assert out.loc["1-2-1@CTG", "NQUAL"] == 3


@pytest.mark.parametrize("sql", [
    "SELECT teid, BranchId FROM AW.dbo.toAllIsos WHERE isoMarketId = 6 AND plannedStartDate > '2026-01-01'",
    "SELECT * FROM AW.dbo.toAllIsos WHERE plannedStartDate > '2026-01-01' -- isoMarketId = 6 AND teid = 1",
    "SELECT * FROM AW.dbo.toAllIsos WHERE x > 1 /* isoMarketId = 6 AND teid = 1 */",
    "SELECT * FROM AW.dbo.toAllIsos WHERE Notes = 'isoMarketId = 6 AND teid = 1'",
    "SELECT * FROM [AW].[dbo].[toAllIsos] WHERE isoMarketId = 6",
    "SELECT * FROM AW.dbo.ercotLoadView v JOIN AW.dbo.toAllIsos t ON t.x = v.x WHERE v.date > '2026-01-01'",
    "SELECT * FROM AW.dbo.TOALLISOS WHERE x=1",
    "SELECT * FROM AW.dbo.TOSTATE WHERE teid = 1",
    "SELECT * FROM AW.dbo.toState s JOIN AW.dbo.toAllIsos t ON t.s = s.toStateId WHERE s.toStateId = 5",
])
def test_outage_query_rejected_cases(fake_db, sql):
    with pytest.raises(ValueError, match="scoped"):
        mssql.query(sql)
    assert fake_db == []


@pytest.mark.parametrize("sql", [
    "SELECT fromDate, toDate FROM AW.dbo.somethingElse WHERE fromDate > '2026-01-01'",
    "SELECT a AS toBusNum FROM AW.dbo.ercotLoadView WHERE date = '2026-01-01'",
    "SELECT * FROM [AW].[dbo].[toAllIsos] WHERE isoMarketId IN (6) AND BranchId IN (1, 2)",
    "SELECT * FROM AW.dbo.ercotLoadView v JOIN AW.dbo.toAllIsos t ON t.isoMarketId = 6 AND t.teid = 3 WHERE v.date > '2026-01-01'",
    "select * from aw.dbo.toallisos where isomarketid=6 and teid=3",
])
def test_outage_query_accepted_cases(fake_db, sql):
    mssql.query(sql)
    assert fake_db == [(sql, "AW")]


def test_every_current_caller_sql_passes_the_guard(monkeypatch):
    import awconnect.db
    from pfa.extract import load, outages, renewables
    from pfa.analysis import headroom_plots

    sent = []
    monkeypatch.setattr(config, "configure", lambda: None)
    monkeypatch.setattr(awconnect.db, "getDfFromAwDb",
                        lambda sql, database="AW": sent.append(sql) or pd.DataFrame({"date": [], "he": [], "ERCOT_ALL_LD": []}))
    outages.lookup_branch_tickets(1, "2026-09-01", "2026-09-30")
    outages.lookup_branch_tickets(1, "2026-09-01", "2026-09-30", teid=5)
    outages.ticket_history("ONC1", 1)
    load._query_load_view(2025, "09-01", "09-30")
    renewables.wind_region_hourly("2026-01-01", "2026-02-01", "West")
    renewables.solar_hourly("2026-01-01", "2026-02-01")
    headroom_plots._fetch_load("2026-01-01", "2026-02-01")
    assert len(sent) == 7 and sum("toAllIsos" in q for q in sent) == 3


@pytest.mark.parametrize("sql", [
    "SELECT * FROM dbo.TOSTATE WHERE toStateId = 5",
    "SELECT * FROM AW.dbo.toStatus WHERE toStatusId IN (1, 2)",
    "SELECT * FROM AW.dbo.TOREASON WHERE toReasonId = 3",
])
def test_dimension_table_by_key_lookup_allowed(fake_db, sql):
    mssql.query(sql)
    assert fake_db == [(sql, "AW")]


def test_comparison_report_lookup_error_is_recorded_per_constraint(monkeypatch):
    from pfa.analysis import study_compare as mod

    def find_configs(study, f, t, ctg):
        if ctg == "BAD":
            raise RuntimeError("boom")
        return pd.DataFrame()

    best = pd.DataFrame({"SOURCENAME": ["S"], "SINKNAME": ["K"], "OPTIONPRICE": [1.5], "AVG_SF": [0.25]})
    monkeypatch.setattr(mod.fastscan, "find_configs", find_configs)
    monkeypatch.setattr(mod.popt, "best_paths", lambda study, c: best if c.endswith("@GOOD") else None)
    new = pd.DataFrame({"CONSTRAINT": ["1-2-1@BAD", "1-2-1@GOOD", "1-2-1@NONE"]})
    out = mod.enrich_new(new, 14412, 3)
    assert out.loc[0, "FASTSCAN_MAX_NEG"] == "lookup failed: boom"
    assert out.loc[1, "BEST_PATH"] == "S→K $1.50 @SF 0.25"
    assert pd.isna(out.loc[2, "BEST_PATH"]) and pd.isna(out.loc[2, "FASTSCAN_MAX_NEG"])
