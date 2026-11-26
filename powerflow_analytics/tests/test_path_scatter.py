import numpy as np
import pandas as pd

from pfa.analysis import path_scatter as ps


def test_sf_stats_ignores_dead_periods():
    S = np.array([[0.1, np.nan, 0.3], [np.nan, np.nan, np.nan]], dtype=np.float32)
    st = ps.sf_stats(S)
    assert st.loc[0, "BINDINGPAIRCOUNT"] == 2
    assert np.isclose(st.loc[0, "MIN_SF"], 0.1) and np.isclose(st.loc[0, "AVG_SF"], 0.2)
    assert np.isnan(st.loc[1, "MIN_SF"])


def test_find_pairs_complementary_legs():
    pool = pd.DataFrame({"OPTIONPRICE": [1.0, 1.0], "VALUE_REQ": [2.0, 2.0]})
    S = {"a": np.array([[0.3, 0.3], [-0.1, -0.1]], dtype=np.float32),
         "b": np.array([[-0.1, -0.1], [0.3, 0.3]], dtype=np.float32)}
    out = ps.find_pairs(pool, S, ["a", "b"], floor=0.1)
    assert len(out) == 1 and np.isclose(out.loc[0, "MIN_SF_a"], 0.2) and np.isclose(out.loc[0, "PRICE"], 2.0)


def test_dedup_multi_collapses_aliases():
    df = pd.DataFrame({"SOURCENAME": ["B", "A", "C"], "SINKNAME": ["X", "X", "Y"],
                       "OPTIONPRICE": [1.0, 1.0, 2.0], "MIN_SF_k": [0.1, 0.1, 0.1]})
    out = ps.dedup_multi(df, ["MIN_SF_k", "OPTIONPRICE"])
    assert len(out) == 2 and out.set_index("SOURCENAME").loc["A", "ALIAS_COUNT"] == 2
