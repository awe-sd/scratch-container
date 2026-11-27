import pandas as pd

from pfa.extract import gen_mapping


def _fake(monkeypatch, canned):
    calls = []

    def q(db, sql):
        calls.append((db, sql))
        return canned

    monkeypatch.setattr(gen_mapping.sf, "query", q)
    return calls


def test_fetch_cpnode_names_scopes_market_and_ids(monkeypatch):
    calls = _fake(monkeypatch, pd.DataFrame({"CPNODEID": [7, 7], "CPNODENAME": ["A", "A"]}))
    out = gen_mapping.fetch_cpnode_names([7.0, None, 9, 7])
    sql = calls[0][1]
    assert calls[0][0] == "AW" and "AW.DBO.CPNODE" in sql and "ISOMARKETID = 6" in sql and "CPNODEID IN (7,9)" in sql
    assert len(out) == 1
    assert gen_mapping.fetch_cpnode_names([None]).empty and len(calls) == 1


def test_with_cpnode_names_leaves_null_and_unresolved_ids_without_a_name(monkeypatch):
    _fake(monkeypatch, pd.DataFrame({"CPNODEID": [1], "CPNODENAME": ["RN_A"]}))
    gu = pd.DataFrame({"GENUNITID": [10, 11, 12], "CPNODEID": [1.0, 2.0, None]})
    out = gen_mapping.with_cpnode_names(gu)
    assert out["CPNODENAME"].tolist()[0] == "RN_A" and out["CPNODENAME"].isna().tolist() == [False, True, True]
    assert out["GENUNITID"].tolist() == [10, 11, 12]
