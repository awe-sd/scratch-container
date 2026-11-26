import pandas as pd

from pfa.constraint_id import ConstraintId
from pfa.extract import shifts

CID = ConstraintId.parse("1436-2081-1@DWCSRAM5")


def _fake(monkeypatch, canned):
    calls = []

    def q(db, sql):
        calls.append((db, sql))
        return canned

    monkeypatch.setattr(shifts.sf, "query", q)
    return calls


def _scoped(sql):
    return ("STUDYID" in sql and "14412" in sql and "FROMNUM" in sql and "1436" in sql
            and "TONUM" in sql and "2081" in sql and "CKT" in sql and "'1'" in sql
            and "CTGLABEL" in sql and "'DWCSRAM5'" in sql)


def test_constraint_scoped_readers_carry_study_and_constraint(monkeypatch):
    canned = pd.DataFrame({"X": [1]})
    cases = [
        (lambda: shifts.bus_sf_for_buses(14412, CID, [5, 6]), "BUS_SHIFTS_VIEW", "BUSNUM IN (5,6)"),
        (lambda: shifts.bus_sf_all_buses(14412, CID), "BUS_SHIFTS_VIEW", "NOT IN ('LZ_', 'WZ_')"),
        (lambda: shifts.cpnode_sf_by_name(14412, CID, ["A", "B"]), "CPNODE_SHIFTS_VIEW", "NAME IN ('A','B')"),
        (lambda: shifts.cpnode_psens_by_id(14412, CID, [3, 4]), "CPNODE_SHIFTS_VIEW", "CPNODEID IN (3,4)"),
        (lambda: shifts.cpnode_live_nodes(14412, CID), "CPNODE_SHIFTS_VIEW", "DEADBUS=0"),
        (lambda: shifts.cpnode_qualifying_count(14412, CID, 0.03, 0.9), "CPNODE_SHIFTS_VIEW", "ABS(PSENS) >= 0.03"),
        (lambda: shifts.cpnode_pair_counts(14412, CID, 0.1, 0.5), "CPNODE_SHIFTS_VIEW", "ABS(PSENS) < 0.5"),
    ]
    for call, view, extra in cases:
        calls = _fake(monkeypatch, canned)
        assert call() is canned
        db, sql = calls[0]
        assert db == "SHIFT_FACTORS" and view in sql and extra in sql and _scoped(sql), sql


def test_bulk_readers_build_constraint_tuples(monkeypatch):
    canned = pd.DataFrame({"N_QUAL": [1]})
    calls = _fake(monkeypatch, canned)
    out = shifts.cpnode_dispatch_features(14412, ["1436-2081-1@DWCSRAM5", "7-8-A@B'C"], 0.03, 0.9, 0.1, 0.5)
    sql = calls[0][1]
    assert out is canned
    assert "(1436, 2081, '1', 'DWCSRAM5')" in sql and "'B''C'" in sql and "STUDYID = 14412" in sql
    assert shifts.cpnode_dispatch_features(14412, [], 0.03, 0.9, 0.1, 0.5).empty

    calls = _fake(monkeypatch, canned)
    assert shifts.cpnode_dispatch_nodes(14412, ["1436-2081-1@DWCSRAM5"], 0.03, 0.9) is canned
    sql = calls[0][1]
    assert "('1436','2081','1','DWCSRAM5')" in sql and "BETWEEN 0.03 AND 0.9" in sql and "STUDYID=14412" in sql


def test_psenshiftid_readers(monkeypatch):
    canned = pd.DataFrame({"X": [1]})
    calls = _fake(monkeypatch, canned)
    assert shifts.node_shift_factors(77) is canned
    assert "PSENSHIFTID = 77" in calls[0][1] and "DEADBUS = 0" in calls[0][1]
    calls = _fake(monkeypatch, canned)
    assert shifts.node_shift_factors_multi([77, 78]) is canned
    assert "PSENSHIFTID IN (77,78)" in calls[0][1]
