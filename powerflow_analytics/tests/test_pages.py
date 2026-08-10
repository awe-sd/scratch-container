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


def test_page_registry_has_exactly_one_explorer_entry():
    """Regression test: importing app.app (Dash auto-discovers the pages
    folder) and importing app.pages.explorer directly (as this test module's
    own top-level `from app.pages import explorer` does) must resolve to the
    SAME module object under the SAME dash.page_registry key. If they didn't,
    register_page() and the module's two @callback decorators would each run
    twice, leaving two registry entries both claiming path "/". Checking the
    registry dict's keys (not a set of paths, which would collapse duplicate
    keys with the same path into one and hide the bug) is the point here.
    """
    from app.app import app  # noqa: F401
    import dash

    explorer_entries = {
        key: entry for key, entry in dash.page_registry.items()
        if entry["path"] == "/"
    }
    assert len(explorer_entries) == 1, (
        f"expected exactly one page_registry entry for path '/', "
        f"got {list(explorer_entries.keys())}"
    )
    # The direct import (used by this test module's own import statement above)
    # must be the identical module object dash registered — not a second copy.
    (registered_module,) = [
        dash.page_registry[k]["module"] for k in explorer_entries
    ]
    assert sys.modules[registered_module] is explorer


def test_load_grid_callback_returns_rows_and_info(monkeypatch):
    bundle = _bundle()
    monkeypatch.setattr(explorer.data, "load_study", lambda sid: bundle)

    row_data, info = explorer._load_grid(bundle.study_id)

    assert row_data, "expected non-empty rowData from a bundle with a binding constraint"
    assert row_data[0]["CONSTRAINT"] == "10-11-1@CTGA"
    assert bundle.study_name in info
    assert str(bundle.n_runs) in info


def test_load_grid_callback_handles_no_study_selected():
    row_data, info = explorer._load_grid(None)
    assert row_data == []
    assert "no analyzed studies" in info.lower()


def test_drilldown_callback_returns_figure_and_tables(monkeypatch):
    bundle = _bundle()
    monkeypatch.setattr(explorer.data, "load_study", lambda sid: bundle)
    selected = [{"CONSTRAINT": "10-11-1@CTGA"}]

    fig, mu_rows, tf_rows = explorer._drilldown(selected, bundle.study_id)

    assert len(fig.data) >= 1
    assert mu_rows and mu_rows[0]["LABEL"] == "U1"
    assert tf_rows and tf_rows[0]["OUTAGE_GROUP"] == "X - Y"


def test_drilldown_callback_handles_no_selection():
    fig, mu_rows, tf_rows = explorer._drilldown(None, 99)
    assert mu_rows == [] and tf_rows == []


def test_compare_ranked():
    from app.pages import comparison
    a = pd.DataFrame({
        "CONSTRAINT": ["c1", "c2"], "FROMNAME": ["A", "C"], "TONAME": ["B", "D"],
        "N_RUNS_BINDING": [2, 1], "PCT_RUNS_BINDING": [20.0, 10.0],
        "MAX_PCT": [120.0, 105.0], "SCORE": [40.0, 10.0], "DRIVER_CLASS": ["baseline", "baseline"],
    })
    b = pd.DataFrame({
        "CONSTRAINT": ["c1", "c3"], "FROMNAME": ["A", "E"], "TONAME": ["B", "F"],
        "N_RUNS_BINDING": [4, 3], "PCT_RUNS_BINDING": [40.0, 30.0],
        "MAX_PCT": [130.0, 110.0], "SCORE": [80.0, 30.0], "DRIVER_CLASS": ["baseline", "baseline"],
    })
    out = comparison.compare_ranked(a, b).set_index("CONSTRAINT")
    assert out.loc["c1", "STATUS"] == "both" and out.loc["c1", "DELTA_PCT"] == 20.0
    assert out.loc["c2", "STATUS"] == "only_a" and out.loc["c2", "DELTA_PCT"] == -10.0
    assert out.loc["c3", "STATUS"] == "only_b" and out.loc["c3", "DELTA_PCT"] == 30.0
    assert out.index[0] == "c3" or abs(out["DELTA_PCT"]).is_monotonic_decreasing
