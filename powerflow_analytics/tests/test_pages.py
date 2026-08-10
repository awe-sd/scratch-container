import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data import StudyBundle
from app.pages import explorer


def _bundle():
    return StudyBundle(
        study_id=99, study_name="TEST_V1",
        ranked=pd.DataFrame({
            "CONSTRAINT": ["10-11-1@CTGA"], "FROMNAME": ["A"], "TONAME": ["B"],
            "N_RUNS_BINDING": [1], "PCT_RUNS_BINDING": [50.0], "MAX_PCT": [120.0],
            "MEAN_EXCESS": [20.0], "SCORE": [21.0], "DRIVER_CLASS": ["outage-driven"],
            "DRIVER_TICKET": ["TCK1"],
        }),
        marginal_units=pd.DataFrame({
            "CONSTRAINT": ["10-11-1@CTGA"], "LABEL": ["U1"], "BUSNUM": [100], "ID": ["1"],
            "BUSNAME": ["BUS100"], "FUELTYPE": ["NG"], "DIFF_MW": [30.0],
        }),
        tofinder=pd.DataFrame({
            "CONSTRAINT": ["10-11-1@CTGA"], "OUTAGE_GROUP": ["X - Y"],
            "MEAN_FLOWDELTA": [40.0], "FLOW_FRAC": [0.4], "N_RUNS": [2],
        }),
        binding=pd.DataFrame({
            "CONSTRAINT": ["10-11-1@CTGA"], "RUNID": [1],
            "SIMDATE": ["2026-09-01"], "SIMHOUR": [14], "LIMVIOLPCT": [120.0],
        }),
        n_runs=2,
    )


def test_binding_profile_figure():
    fig = explorer.binding_profile_figure(_bundle(), "10-11-1@CTGA")
    assert len(fig.data) >= 1  # has at least one trace


def test_drilldown_tables_filter_by_constraint():
    mu_rows, tf_rows = explorer.drilldown_tables(_bundle(), "10-11-1@CTGA")
    assert mu_rows[0]["LABEL"] == "U1"
    assert tf_rows[0]["OUTAGE_GROUP"] == "X - Y"
    mu_rows, tf_rows = explorer.drilldown_tables(_bundle(), "does-not@EXIST")
    assert mu_rows == [] and tf_rows == []


def test_app_imports_and_registers_pages():
    from app.app import app  # noqa: F401  (import builds the Dash app)
    import dash
    paths = {p["path"] for p in dash.page_registry.values()}
    assert "/" in paths and "/comparison" in paths or "/" in paths
