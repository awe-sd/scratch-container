
import pandas as pd


from pfa.extract import popt


def test_best_paths_uses_exact_branch_label_when_resolved(monkeypatch):
    calls = []

    def fake_query(db_name, sql):
        calls.append((db_name, sql))
        if "OUTBRANCH2" in sql:
            return pd.DataFrame({"LABEL": ["35100_A"]})
        # the PATHOPTDETAILVIEW query must filter on the exact label, not a
        # pattern match that could also grab an unrelated single-token label
        assert "BRANCHLABEL IN ('35100_A')" in sql
        assert "BOWFMR1" not in sql
        return pd.DataFrame({
            "SOURCENAME": ["WCPP_CT1"], "SINKNAME": ["CHISMGRD_RN"],
            "OPTIONPRICE": [2.24], "AVG_SF": [0.31], "WAVG_DOLLAR_MWH": [61.0],
            "PRICE_PER_SF": [7.23],
        })

    monkeypatch.setattr(popt.sf, "query", fake_query)
    df = popt.best_paths(14411, "1436-2081-1@DWCSRAM5")
    assert df is not None
    assert df.iloc[0]["SOURCENAME"] == "WCPP_CT1"
    assert df.iloc[0]["SINKNAME"] == "CHISMGRD_RN"


def test_label_lookup_uses_from_to_and_ckt(monkeypatch):
    seen = []

    def fake_query(db_name, sql):
        seen.append(sql)
        return pd.DataFrame({"LABEL": ["35100_A", "35100_B"]}) if "OUTBRANCH2" in sql else pd.DataFrame()

    monkeypatch.setattr(popt.sf, "query", fake_query)
    popt.best_paths(14411, "1436-2081-2@DWCSRAM5")
    assert "FROMNUM = 1436 AND TONUM = 2081 AND TRIM(CKT) = '2'" in seen[0]
    assert "BRANCHLABEL IN ('35100_A', '35100_B')" in seen[1]


def test_unresolved_label_returns_none_and_never_queries_paths(monkeypatch):
    seen = []

    def fake_query(db_name, sql):
        seen.append(sql)
        return pd.DataFrame()  # no label found for this branch

    monkeypatch.setattr(popt.sf, "query", fake_query)
    assert popt.best_paths(14411, "1436-2081-1@DWCSRAM5") is None
    assert len(seen) == 1 and "PATHOPTDETAILVIEW" not in seen[0]
