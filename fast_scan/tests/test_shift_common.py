import re

from shift_common import dart_chain_sql, window_label


def norm(s):
    return re.sub(r"\s+", " ", s)


def test_chain_minimal_variant():
    sql = norm(dart_chain_sql("DISTINCT cd.congConstraintID", "2026-06-01", "2026-06-30", "BR", "CT"))
    assert sql.startswith("SELECT DISTINCT cd.congConstraintID FROM AW.dbo.psenShiftDef psd INNER JOIN AW.DBO.congDefConstraint cd")
    for t in ("congDefMonitor cdm", "congDefContingency cdc", "branchMonitored bm", "AW.DBO.branch b"):
        assert t in sql
    assert "PSENSHIFT ps" not in sql and "CPNODE" not in sql and "QUALIFY" not in sql
    assert "psd.isoMarketID = 6 AND psd.psenShiftTypeId = 14" in sql
    assert "psd.extractionEnd >= '2026-06-01' AND psd.extractionEnd <= '2026-06-30'" in sql
    assert "b.branchName = 'BR' AND cdc.congContName = 'CT'" in sql


def test_chain_full_variant_join_order_and_dedupe():
    sql = norm(dart_chain_sql("x", "a", "b", "BR", "CT", psenshift=True, cpnode=True, dedupe=True,
                              extra_where="AND (cp.name LIKE 'LZ$_%')"))
    order = ["psenShiftDef psd", "PSENSHIFT ps ON ps.psenshiftid = psd.psenshiftid", "congDefConstraint cd",
             "congDefMonitor cdm", "congDefContingency cdc", "branchMonitored bm", "AW.DBO.branch b",
             "CPNODE cp ON cp.cpnodeid = ps.cpnodeid"]
    pos = [sql.index(t) for t in order]
    assert pos == sorted(pos)
    assert "AND (cp.name LIKE 'LZ$_%')" in sql
    assert sql.endswith("QUALIFY ROW_NUMBER() OVER (PARTITION BY psd.psenshiftid, ps.cpnodeid ORDER BY psd.psenshiftid) = 1")


def test_window_label():
    assert window_label("2026-06-01", "2026-06-30") == "June"
    assert window_label("2026-06-01", "2026-07-02") == ""
