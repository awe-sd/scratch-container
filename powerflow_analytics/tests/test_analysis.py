import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pfa.analysis import constraints, drivers, marginal_units


def _ctgviol():
    return pd.DataFrame({
        "RUNID": [1, 2, 3, 1, 2],
        "FROMNUM": [10, 10, 10, 20, 20],
        "TONUM": [11, 11, 11, 21, 21],
        "CKT": ["1"] * 5,
        "CTGLABEL": ["CTGA"] * 3 + ["CTGB"] * 2,
        "BRANCHNAME": ["BR1"] * 3 + ["BR2"] * 2,
        "BRANCHID": [60000001] * 3 + [60000002] * 2,
        "LIMVIOLPCT": [100.0, 120.0, 80.0, 99.6, 50.0],
        "LIMVIOLLIMIT": [100.0] * 5,
        "FROMNAME": ["A"] * 3 + ["C"] * 2,
        "TONAME": ["B"] * 3 + ["D"] * 2,
    })


def _runs():
    return pd.DataFrame({"RUNID": [1, 2, 3, 4], "SIMDATE": ["2026-09-01"] * 4, "SIMHOUR": [1, 2, 3, 4]})


def test_rank_constraints():
    r = constraints.rank_constraints(_ctgviol(), _runs())
    assert len(r) == 2
    top = r.iloc[0]
    assert top["CONSTRAINT"] == "10-11-1@CTGA"
    assert top["N_RUNS_BINDING"] == 2  # runs 1 and 2 (>=99.5), not run 3
    assert top["PCT_RUNS_BINDING"] == 50.0
    assert r.iloc[1]["N_RUNS_BINDING"] == 1  # 99.6 counts as binding


def test_marginal_units_differential():
    gen = pd.DataFrame({
        "RUNID": [1, 2, 3, 4] * 2,
        "BUSNUM": [100] * 4 + [200] * 4,
        "ID": ["1"] * 8,
        "LABEL": ["U1"] * 4 + ["U2"] * 4,
        "GENSTATUS": [0] * 8,
        "UNITTYPE": ["GT"] * 8,
        "FUELTYPE": ["NG"] * 8,
        "ZONENAME": ["Z"] * 8,
        "MW": [50.0] * 8,
        "MWMAX": [100.0] * 8,
        # U1 redispatches +30 only in binding runs (1,2); U2 never moves
        "LPDELTAMW": [30.0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    })
    mu = marginal_units.marginal_units_for_constraint(_ctgviol(), gen, "10-11-1@CTGA")
    assert mu.iloc[0]["BUSNUM"] == 100
    assert mu.iloc[0]["DIFF_MW"] == 30.0
    assert mu.iloc[0]["N_BINDING_RUNS"] == 2


def test_add_shadow_prices():
    ranked = constraints.rank_constraints(_ctgviol(), _runs())
    outcon = pd.DataFrame({
        "RUNID": [1, 2, 3],
        "FROMNUM": [10, 10, 10], "TONUM": [11, 11, 11], "CKT": ["1", "1", "1"],
        "LPOPFCTGID": ["CTGA", "CTGA", "CTGA"],
        "OPFCNLAMBDA": [100.0, 300.0, 200.0],
        "LPBASICVARID": ["Gen 5 #1 MW Control", "Gen 5 #1 MW Control", "Gen 7 #1 MW Control"],
    })
    out = constraints.add_shadow_prices(ranked, outcon).set_index("CONSTRAINT")
    assert out.loc["10-11-1@CTGA", "N_RUNS_SHADOW"] == 3
    assert out.loc["10-11-1@CTGA", "MEAN_SHADOW"] == 200.0
    assert out.loc["10-11-1@CTGA", "MAX_SHADOW"] == 300.0
    assert out.loc["10-11-1@CTGA", "TOP_MARGINAL_VAR"] == "Gen 5 #1 MW Control"
    assert out.loc["20-21-1@CTGB", "N_RUNS_SHADOW"] == 0
    assert pd.isna(out.loc["20-21-1@CTGB", "MEAN_SHADOW"])


def test_congestion_rent_with_cutoff():
    runs = pd.DataFrame({
        "RUNID": [1, 2, 3, 4],
        "SIMDATE": ["2026-09-01", "2026-09-10", "2026-09-20", "2026-09-25"],
        "SIMHOUR": [1, 2, 3, 4],
    })
    outcon = pd.DataFrame({
        "RUNID": [1, 3],
        "FROMNUM": [10, 10], "TONUM": [11, 11], "CKT": ["1", "1"],
        "LPOPFCTGID": ["CTGA", "CTGA"],
        "OPFCNLAMBDA": [50.0, 100.0],
        "LPBASICVARID": ["Gen 5 #1 MW Control"] * 2,
    })
    # limit is 100 MW in _ctgviol for the 10-11-1@CTGA rows (runs 1,2,3)
    rent = constraints.congestion_rent(_ctgviol(), outcon, runs, cutoff_date="2026-09-15")
    row = rent.set_index("CONSTRAINT").loc["10-11-1@CTGA"]
    assert row["RENT_PRE"] == 50.0 * 100.0        # run 1 (Sep 1)
    assert row["RENT_POST"] == 100.0 * 100.0      # run 3 (Sep 20)
    assert row["TOTAL_RENT"] == 15000.0
    assert abs(row["POST_RENT_SHARE"] - 2 / 3) < 1e-9


def test_classify_constraints_ticket_path():
    ranked = constraints.rank_constraints(_ctgviol(), _runs())
    tf = pd.DataFrame({
        "RUNID": [1, 2],
        "FROMNUM_TARGET": [10, 10], "TONUM_TARGET": [11, 11], "CKT_TARGET": ["1", "1"],
        "CTGLABEL": ["CTGA", "CTGA"],
        "OUTAGE_GROUP_ID": [7, 7],
        "OUTAGE_GROUP": ["X 138kV - Y 138kV"] * 2,
        "OUTBRANCHLABEL": ["XY"] * 2,
        "BRANCHID_OUTAGE": [60000099] * 2,
        "FROMNUM_OUTAGE": [30] * 2, "TONUM_OUTAGE": [31] * 2, "CKT_OUTAGE": ["1"] * 2,
        "FLOWDELTA": [40.0, 45.0],
        "PREGROUPOUTLINEFLOW": [100.0, 100.0],
    })
    tf_sum = drivers.tofinder_summary(tf)

    def fake_lookup(branch_id, start, end):
        assert branch_id == 60000099
        return pd.DataFrame({"outageIdentifier": ["TCK123"]})

    out = drivers.classify_constraints(ranked, tf_sum, fake_lookup, ("2026-09-01", "2026-09-30"))
    by_c = out.set_index("CONSTRAINT")
    assert by_c.loc["10-11-1@CTGA", "DRIVER_CLASS"] == "outage-driven"
    assert by_c.loc["10-11-1@CTGA", "DRIVER_TICKET"] == "TCK123"
    assert by_c.loc["20-21-1@CTGB", "DRIVER_CLASS"] == "baseline"

    out2 = drivers.classify_constraints(ranked, tf_sum, None, None)
    assert out2.set_index("CONSTRAINT").loc["10-11-1@CTGA", "DRIVER_CLASS"] == "topology-suspect"
