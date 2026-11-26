# powerflow_analytics Dash Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dash dashboard over the powerflow_analytics local cache: a constraint-explorer page (ranked binding constraints with drill-down) and a study-comparison page.

**Architecture:** The `pfa` package (already built and committed) pulls SCOPF study output into `powerflow_analytics/cache/study_<id>/*.parquet` and `scripts/build_report.py` writes analysis CSVs to `powerflow_analytics/output/study_<id>/`. The dashboard is a standalone multi-page Dash app in `powerflow_analytics/app/` that reads ONLY those local files — it never queries Snowflake or SQL Server. A thin data module (`app/data.py`) loads and memoizes per-study bundles; pages consume it.

**Tech Stack:** Python 3.13 via `uv` (repo root `/workspaces/scratch-workspace`), Dash multi-page (`dash.register_page`), dash-bootstrap-components (BOOTSTRAP theme), dash-ag-grid, plotly, pandas, pytest.

## Global Constraints

- Always run Python via `uv run ...` from the repo root; add deps with `uv add <pkg>` (never bare pip).
- The dashboard must NEVER query Snowflake or SQL Server — local `cache/` + `output/` files only (spec: "Dash never queries Snowflake in callbacks").
- Component preference: dash-bootstrap-components > raw html; tables are dash-ag-grid `AgGrid`.
- Studies appear in the UI only if BOTH `powerflow_analytics/cache/study_<id>/` and `powerflow_analytics/output/study_<id>/ranked_constraints.csv` exist (i.e. pulled AND analyzed). Study 14411 is the dev fixture.
- Constraint identity string everywhere: `"<FROMNUM>-<TONUM>-<CKT>@<CTGLABEL>"` (column `CONSTRAINT` in the CSVs).
- Do not modify anything under `powerflow_analytics/pfa/` except where a task explicitly says so.
- Commit after each passing task; commit messages end with the Claude Code trailer.

## File Structure

```
powerflow_analytics/
├── app/
│   ├── __init__.py          (empty)
│   ├── data.py              # Task 1: per-study bundle loader (cache + output CSVs)
│   ├── app.py               # Task 2: Dash app shell, page registry, navbar
│   └── pages/
│       ├── __init__.py      (empty)
│       ├── explorer.py      # Task 2: ranked grid + drill-down
│       └── comparison.py    # Task 3: two-study constraint deltas
├── tests/
│   ├── test_analysis.py     (exists)
│   └── test_app_data.py     # Task 1
└── README.md                # Task 3: run instructions
```

---

### Task 1: Data access layer for the dashboard

**Files:**
- Create: `powerflow_analytics/app/__init__.py` (empty), `powerflow_analytics/app/data.py`
- Test: `powerflow_analytics/tests/test_app_data.py`
- Modify: none

**Interfaces:**
- Consumes: `pfa.config.CACHE_ROOT` / `pfa.config.OUTPUT_ROOT` (Path constants), `pfa.analysis.constraints.binding_hours(ctgviol_df, runs_df)` (existing; returns columns CONSTRAINT, RUNID, SIMDATE, SIMHOUR, LIMVIOLPCT).
- Produces (Tasks 2–3 rely on these exact names):
  - `list_studies() -> list[int]` — sorted study ids with both cache dir and `ranked_constraints.csv` present
  - `load_study(study_id: int) -> StudyBundle` — memoized (`functools.lru_cache`)
  - `@dataclass StudyBundle` with fields: `study_id: int`, `study_name: str`, `ranked: pd.DataFrame` (ranked_constraints.csv), `marginal_units: pd.DataFrame`, `tofinder: pd.DataFrame` (tofinder_summary.csv), `binding: pd.DataFrame` (binding_hours output), `n_runs: int`

- [ ] **Step 1: Write the failing tests**

```python
# powerflow_analytics/tests/test_app_data.py
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import data


@pytest.fixture
def fake_study(tmp_path, monkeypatch):
    """Minimal cache + output for study 99: enough for a StudyBundle."""
    cache = tmp_path / "cache" / "study_99"
    out = tmp_path / "output" / "study_99"
    cache.mkdir(parents=True)
    out.mkdir(parents=True)

    pd.DataFrame({"STUDYID": [99], "STUDYNAME": ["TEST_V1"], "PTOID": [1504]}).to_parquet(
        cache / "opfstudy.parquet", index=False
    )
    pd.DataFrame({"RUNID": [1, 2], "SIMDATE": ["2026-09-01", "2026-09-01"], "SIMHOUR": [1, 2]}).to_parquet(
        cache / "opfrun.parquet", index=False
    )
    pd.DataFrame({
        "RUNID": [1, 2], "FROMNUM": [10, 10], "TONUM": [11, 11], "CKT": ["1", "1"],
        "CTGLABEL": ["CTGA", "CTGA"], "LIMVIOLPCT": [120.0, 80.0],
        "FROMNAME": ["A", "A"], "TONAME": ["B", "B"],
    }).to_parquet(cache / "outctgviol2.parquet", index=False)

    pd.DataFrame({"CONSTRAINT": ["10-11-1@CTGA"], "N_RUNS_BINDING": [1], "SCORE": [21.0]}).to_csv(
        out / "ranked_constraints.csv", index=False
    )
    pd.DataFrame({"CONSTRAINT": ["10-11-1@CTGA"], "BUSNUM": [100], "DIFF_MW": [30.0]}).to_csv(
        out / "marginal_units.csv", index=False
    )
    pd.DataFrame({"CONSTRAINT": ["10-11-1@CTGA"], "OUTAGE_GROUP": ["X - Y"], "MEAN_FLOWDELTA": [40.0]}).to_csv(
        out / "tofinder_summary.csv", index=False
    )

    monkeypatch.setattr(data, "CACHE_ROOT", tmp_path / "cache")
    monkeypatch.setattr(data, "OUTPUT_ROOT", tmp_path / "output")
    data.load_study.cache_clear()
    yield 99
    data.load_study.cache_clear()


def test_list_studies(fake_study, tmp_path):
    # cache-only study (no output) must NOT appear
    (tmp_path / "cache" / "study_50").mkdir()
    assert data.list_studies() == [99]


def test_load_study_bundle(fake_study):
    b = data.load_study(99)
    assert b.study_name == "TEST_V1"
    assert b.n_runs == 2
    assert list(b.ranked["CONSTRAINT"]) == ["10-11-1@CTGA"]
    assert len(b.marginal_units) == 1 and len(b.tofinder) == 1
    # binding profile: only the LIMVIOLPCT >= 99.5 row survives, joined to run hours
    assert list(b.binding["SIMHOUR"]) == [1]
    assert b.binding["CONSTRAINT"].iloc[0] == "10-11-1@CTGA"


def test_load_study_memoized(fake_study):
    assert data.load_study(99) is data.load_study(99)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest powerflow_analytics/tests/test_app_data.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app'` (or ImportError on `data`).

- [ ] **Step 3: Implement `app/data.py`**

Create empty `powerflow_analytics/app/__init__.py`, then:

```python
# powerflow_analytics/app/data.py
"""Read-only data access for the dashboard: local cache + analysis CSVs only.

No Snowflake / SQL Server access from the app — pull and analyze first:
  uv run powerflow_analytics/scripts/pull_study.py --study <id>
  uv run powerflow_analytics/scripts/build_report.py --study <id> --tickets
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pfa.analysis import constraints
from pfa.config import CACHE_ROOT, OUTPUT_ROOT  # re-bound at module level so tests can monkeypatch

CACHE_ROOT = CACHE_ROOT
OUTPUT_ROOT = OUTPUT_ROOT


@dataclass(frozen=True)
class StudyBundle:
    study_id: int
    study_name: str
    ranked: pd.DataFrame
    marginal_units: pd.DataFrame
    tofinder: pd.DataFrame
    binding: pd.DataFrame  # per binding row: CONSTRAINT, RUNID, SIMDATE, SIMHOUR, LIMVIOLPCT
    n_runs: int


def list_studies() -> list[int]:
    out = []
    for d in sorted(CACHE_ROOT.glob("study_*")):
        try:
            sid = int(d.name.removeprefix("study_"))
        except ValueError:
            continue
        if (OUTPUT_ROOT / d.name / "ranked_constraints.csv").exists():
            out.append(sid)
    return out


@lru_cache(maxsize=8)
def load_study(study_id: int) -> StudyBundle:
    cache = CACHE_ROOT / f"study_{study_id}"
    out = OUTPUT_ROOT / f"study_{study_id}"
    study = pd.read_parquet(cache / "opfstudy.parquet")
    runs = pd.read_parquet(cache / "opfrun.parquet")
    ctgviol = pd.read_parquet(cache / "outctgviol2.parquet")
    return StudyBundle(
        study_id=study_id,
        study_name=str(study["STUDYNAME"].iloc[0]),
        ranked=pd.read_csv(out / "ranked_constraints.csv"),
        marginal_units=pd.read_csv(out / "marginal_units.csv"),
        tofinder=pd.read_csv(out / "tofinder_summary.csv"),
        binding=constraints.binding_hours(ctgviol, runs),
        n_runs=int(runs["RUNID"].nunique()),
    )
```

Note: `lru_cache` requires the test to compare identity (`is`), which Step 1 does. `monkeypatch.setattr(data, "CACHE_ROOT", ...)` works because the module re-binds the names locally and every function reads the module globals at call time — do not import the paths inside the functions.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest powerflow_analytics/tests/test_app_data.py -v`
Expected: 3 PASS. Also run the existing suite: `uv run python -m pytest powerflow_analytics/tests/ -q` — all pass.

- [ ] **Step 5: Commit**

```bash
git add powerflow_analytics/app powerflow_analytics/tests/test_app_data.py
git commit -m "feat(powerflow_analytics): dashboard data layer (study bundles from local cache)"
```

---

### Task 2: Dash app shell + constraint explorer page

**Files:**
- Create: `powerflow_analytics/app/app.py`, `powerflow_analytics/app/pages/__init__.py` (empty), `powerflow_analytics/app/pages/explorer.py`
- Modify: `pyproject.toml` via `uv add dash dash-bootstrap-components dash-ag-grid`
- Test: extend `powerflow_analytics/tests/test_app_data.py` is NOT needed; add `powerflow_analytics/tests/test_pages.py`

**Interfaces:**
- Consumes: `app.data.list_studies()`, `app.data.load_study(study_id) -> StudyBundle` (fields per Task 1).
- Produces: `explorer.ranked_columndefs` (list of AG Grid column defs), pure helpers `explorer.binding_profile_figure(bundle, constraint) -> plotly.graph_objects.Figure` and `explorer.drilldown_tables(bundle, constraint) -> tuple[list[dict], list[dict]]` (marginal-unit row dicts, tofinder row dicts) — kept as module-level pure functions so they are unit-testable without a running server.

- [ ] **Step 1: Add dependencies**

Run: `uv add dash dash-bootstrap-components dash-ag-grid`
Expected: resolves and installs without error.

- [ ] **Step 2: Write the failing tests**

```python
# powerflow_analytics/tests/test_pages.py
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
```

(The comparison page arrives in Task 3; the last assert passes with explorer alone because of the `or "/" in paths` clause — leave it as written.)

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run python -m pytest powerflow_analytics/tests/test_pages.py -v`
Expected: FAIL with ImportError (`app.pages.explorer` missing).

- [ ] **Step 4: Implement the shell and explorer page**

```python
# powerflow_analytics/app/app.py
"""Dashboard entrypoint.

Run: uv run powerflow_analytics/app/app.py  ->  http://127.0.0.1:8050
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder=str(Path(__file__).parent / "pages"),
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="powerflow analytics",
)

navbar = dbc.NavbarSimple(
    brand="powerflow analytics — SCOPF → CRR",
    children=[
        dbc.NavItem(dbc.NavLink("Explorer", href="/")),
        dbc.NavItem(dbc.NavLink("Comparison", href="/comparison")),
    ],
    color="dark", dark=True, className="mb-3",
)

app.layout = dbc.Container([navbar, dash.page_container], fluid=True)

if __name__ == "__main__":
    app.run(debug=True)
```

```python
# powerflow_analytics/app/pages/explorer.py
"""Constraint explorer: ranked binding constraints with per-constraint drill-down."""
from __future__ import annotations

import dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from app import data

dash.register_page(__name__, path="/", name="Explorer")

ranked_columndefs = [
    {"field": "CONSTRAINT", "pinned": "left", "width": 220},
    {"field": "FROMNAME", "headerName": "From"},
    {"field": "TONAME", "headerName": "To"},
    {"field": "N_RUNS_BINDING", "headerName": "# runs binding", "type": "numericColumn"},
    {"field": "PCT_RUNS_BINDING", "headerName": "% runs", "type": "numericColumn",
     "valueFormatter": {"function": "d3.format('.1f')(params.value)"}},
    {"field": "MAX_PCT", "headerName": "max %", "type": "numericColumn",
     "valueFormatter": {"function": "d3.format('.1f')(params.value)"}},
    {"field": "MEAN_EXCESS", "headerName": "mean excess", "type": "numericColumn",
     "valueFormatter": {"function": "d3.format('.2f')(params.value)"}},
    {"field": "SCORE", "type": "numericColumn",
     "valueFormatter": {"function": "d3.format('.0f')(params.value)"}},
    {"field": "DRIVER_CLASS", "headerName": "driver"},
    {"field": "DRIVER_TICKET", "headerName": "ticket"},
]


def binding_profile_figure(bundle: data.StudyBundle, constraint: str) -> go.Figure:
    df = bundle.binding[bundle.binding["CONSTRAINT"] == constraint]
    if df.empty:
        return go.Figure()
    fig = px.scatter(
        df, x="SIMDATE", y="SIMHOUR", color="LIMVIOLPCT",
        color_continuous_scale="OrRd",
        labels={"SIMDATE": "sim date", "SIMHOUR": "hour", "LIMVIOLPCT": "loading %"},
    )
    fig.update_layout(margin=dict(l=40, r=10, t=30, b=40), height=320,
                      title=f"Binding hours — {constraint}")
    return fig


def drilldown_tables(bundle: data.StudyBundle, constraint: str) -> tuple[list[dict], list[dict]]:
    mu = bundle.marginal_units[bundle.marginal_units["CONSTRAINT"] == constraint]
    tf = bundle.tofinder[bundle.tofinder["CONSTRAINT"] == constraint]
    return mu.to_dict("records"), tf.to_dict("records")


def layout():
    studies = data.list_studies()
    return dbc.Container([
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                id="explorer-study",
                options=[{"label": f"{s} — {data.load_study(s).study_name}", "value": s} for s in studies],
                value=studies[0] if studies else None, clearable=False,
            ), width=4),
            dbc.Col(html.Div(id="explorer-study-info"), width=8),
        ], className="mb-2"),
        dag.AgGrid(
            id="explorer-grid", columnDefs=ranked_columndefs, rowData=[],
            dashGridOptions={"rowSelection": "single", "pagination": True,
                             "paginationPageSize": 20},
            columnSize="sizeToFit", style={"height": 480},
        ),
        html.Hr(),
        dbc.Row([
            dbc.Col(dcc.Graph(id="explorer-profile"), width=5),
            dbc.Col([
                html.H6("Marginal units (differential redispatch, MW)"),
                dag.AgGrid(id="explorer-mu", rowData=[], columnDefs=[
                    {"field": "LABEL"}, {"field": "BUSNAME", "headerName": "bus"},
                    {"field": "FUELTYPE", "headerName": "fuel"},
                    {"field": "DIFF_MW", "headerName": "ΔMW when binding", "type": "numericColumn",
                     "valueFormatter": {"function": "d3.format('.1f')(params.value)"}},
                ], columnSize="sizeToFit", style={"height": 200}),
                html.H6("Top outage groups (tofinder)", className="mt-2"),
                dag.AgGrid(id="explorer-tf", rowData=[], columnDefs=[
                    {"field": "OUTAGE_GROUP", "flex": 2},
                    {"field": "MEAN_FLOWDELTA", "headerName": "mean ΔMW", "type": "numericColumn",
                     "valueFormatter": {"function": "d3.format('.1f')(params.value)"}},
                    {"field": "FLOW_FRAC", "headerName": "flow frac", "type": "numericColumn",
                     "valueFormatter": {"function": "d3.format('.2f')(params.value)"}},
                ], columnSize="sizeToFit", style={"height": 200}),
            ], width=7),
        ]),
    ], fluid=True)


@callback(
    Output("explorer-grid", "rowData"),
    Output("explorer-study-info", "children"),
    Input("explorer-study", "value"),
)
def _load_grid(study_id):
    if study_id is None:
        return [], "No analyzed studies found — run pull_study.py + build_report.py first."
    b = data.load_study(int(study_id))
    binding = b.ranked[b.ranked["N_RUNS_BINDING"] > 0]
    info = f"{b.study_name}: {b.n_runs} runs, {len(binding)} constraints ever binding"
    return binding.to_dict("records"), info


@callback(
    Output("explorer-profile", "figure"),
    Output("explorer-mu", "rowData"),
    Output("explorer-tf", "rowData"),
    Input("explorer-grid", "selectedRows"),
    Input("explorer-study", "value"),
)
def _drilldown(selected, study_id):
    if not selected or study_id is None:
        return go.Figure(), [], []
    b = data.load_study(int(study_id))
    constraint = selected[0]["CONSTRAINT"]
    mu, tf = drilldown_tables(b, constraint)
    return binding_profile_figure(b, constraint), mu, tf
```

Create empty `powerflow_analytics/app/pages/__init__.py`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run python -m pytest powerflow_analytics/tests/test_pages.py powerflow_analytics/tests/test_app_data.py -v`
Expected: all PASS.

- [ ] **Step 6: Smoke-run the server against real study 14411**

Run: `timeout 20 uv run powerflow_analytics/app/app.py & sleep 8 && curl -s http://127.0.0.1:8050/ | head -c 200; wait`
Expected: HTML containing `<title>powerflow analytics</title>`; server exits when timeout ends. (If port 8050 is busy, `app.run(debug=True, port=8051)` temporarily — do not commit a port change.)

- [ ] **Step 7: Commit**

```bash
git add powerflow_analytics/app powerflow_analytics/tests/test_pages.py pyproject.toml uv.lock
git commit -m "feat(powerflow_analytics): Dash shell + constraint explorer page"
```

---

### Task 3: Study comparison page + README

**Files:**
- Create: `powerflow_analytics/app/pages/comparison.py`, `powerflow_analytics/README.md`
- Test: extend `powerflow_analytics/tests/test_pages.py`

**Interfaces:**
- Consumes: `app.data.list_studies()`, `app.data.load_study()`; `StudyBundle.ranked` columns CONSTRAINT, FROMNAME, TONAME, N_RUNS_BINDING, PCT_RUNS_BINDING, MAX_PCT, SCORE, DRIVER_CLASS.
- Produces: pure helper `comparison.compare_ranked(ranked_a, ranked_b) -> pd.DataFrame` with columns CONSTRAINT, FROMNAME, TONAME, `PCT_A`, `PCT_B`, `DELTA_PCT` (=PCT_B−PCT_A, missing side treated as 0), `SCORE_A`, `SCORE_B`, `STATUS` (`both` / `only_a` / `only_b`), sorted by |DELTA_PCT| descending.

- [ ] **Step 1: Write the failing test**

Append to `powerflow_analytics/tests/test_pages.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m pytest powerflow_analytics/tests/test_pages.py::test_compare_ranked -v`
Expected: FAIL with ImportError (`app.pages.comparison` missing).

- [ ] **Step 3: Implement the comparison page**

```python
# powerflow_analytics/app/pages/comparison.py
"""Compare binding constraints across two analyzed studies."""
from __future__ import annotations

import dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, callback, dcc, html

from app import data

dash.register_page(__name__, path="/comparison", name="Comparison")

_KEEP = ["CONSTRAINT", "FROMNAME", "TONAME", "PCT_RUNS_BINDING", "SCORE"]


def compare_ranked(ranked_a: pd.DataFrame, ranked_b: pd.DataFrame) -> pd.DataFrame:
    a = ranked_a[ranked_a["N_RUNS_BINDING"] > 0][_KEEP].rename(
        columns={"PCT_RUNS_BINDING": "PCT_A", "SCORE": "SCORE_A"})
    b = ranked_b[ranked_b["N_RUNS_BINDING"] > 0][_KEEP].rename(
        columns={"PCT_RUNS_BINDING": "PCT_B", "SCORE": "SCORE_B"})
    m = a.merge(b, on="CONSTRAINT", how="outer", suffixes=("", "_B"))
    for side in ("FROMNAME", "TONAME"):
        if f"{side}_B" in m.columns:
            m[side] = m[side].fillna(m[f"{side}_B"])
            m = m.drop(columns=f"{side}_B")
    m["STATUS"] = "both"
    m.loc[m["PCT_B"].isna(), "STATUS"] = "only_a"
    m.loc[m["PCT_A"].isna(), "STATUS"] = "only_b"
    m[["PCT_A", "PCT_B", "SCORE_A", "SCORE_B"]] = m[
        ["PCT_A", "PCT_B", "SCORE_A", "SCORE_B"]].fillna(0.0)
    m["DELTA_PCT"] = m["PCT_B"] - m["PCT_A"]
    return m.reindex(m["DELTA_PCT"].abs().sort_values(ascending=False).index).reset_index(drop=True)


_columndefs = [
    {"field": "CONSTRAINT", "pinned": "left", "width": 220},
    {"field": "FROMNAME", "headerName": "From"}, {"field": "TONAME", "headerName": "To"},
    {"field": "STATUS"},
    {"field": "PCT_A", "headerName": "% runs (A)", "type": "numericColumn",
     "valueFormatter": {"function": "d3.format('.1f')(params.value)"}},
    {"field": "PCT_B", "headerName": "% runs (B)", "type": "numericColumn",
     "valueFormatter": {"function": "d3.format('.1f')(params.value)"}},
    {"field": "DELTA_PCT", "headerName": "Δ % runs", "type": "numericColumn",
     "valueFormatter": {"function": "d3.format('+.1f')(params.value)"}},
    {"field": "SCORE_A", "type": "numericColumn",
     "valueFormatter": {"function": "d3.format('.0f')(params.value)"}},
    {"field": "SCORE_B", "type": "numericColumn",
     "valueFormatter": {"function": "d3.format('.0f')(params.value)"}},
]


def layout():
    studies = data.list_studies()
    opts = [{"label": f"{s} — {data.load_study(s).study_name}", "value": s} for s in studies]
    return dbc.Container([
        dbc.Row([
            dbc.Col([html.Small("Study A"), dcc.Dropdown(id="cmp-a", options=opts,
                     value=studies[0] if studies else None, clearable=False)], width=4),
            dbc.Col([html.Small("Study B"), dcc.Dropdown(id="cmp-b", options=opts,
                     value=studies[-1] if studies else None, clearable=False)], width=4),
        ], className="mb-2"),
        dag.AgGrid(id="cmp-grid", columnDefs=_columndefs, rowData=[],
                   dashGridOptions={"pagination": True, "paginationPageSize": 25},
                   columnSize="sizeToFit", style={"height": 600}),
    ], fluid=True)


@callback(Output("cmp-grid", "rowData"), Input("cmp-a", "value"), Input("cmp-b", "value"))
def _compare(a, b):
    if a is None or b is None:
        return []
    df = compare_ranked(data.load_study(int(a)).ranked, data.load_study(int(b)).ranked)
    return df.to_dict("records")
```

- [ ] **Step 4: Write README**

```markdown
# powerflow_analytics

SCOPF study results → CRR opportunity finder. See `CLAUDE.md` for conventions
and `docs/superpowers/specs/2026-08-10-powerflow-analytics-design.md` for the design.

## Workflow

1. Pull a study into the local cache (Snowflake, one-time per study):
   `uv run powerflow_analytics/scripts/pull_study.py --study 14411`
2. Analyze it (writes CSVs to `output/study_14411/`):
   `uv run powerflow_analytics/scripts/build_report.py --study 14411 --tickets`
3. Dashboard (reads only local files):
   `uv run powerflow_analytics/app/app.py` → http://127.0.0.1:8050
   - **Explorer**: ranked binding constraints; click a row for binding-hours
     profile, marginal units, and tofinder outage evidence.
   - **Comparison**: constraint deltas between two analyzed studies.

## Tests

`uv run python -m pytest powerflow_analytics/tests/ -q`
```

- [ ] **Step 5: Run all tests**

Run: `uv run python -m pytest powerflow_analytics/tests/ -q`
Expected: all PASS (including `test_app_imports_and_registers_pages`, which now sees both pages).

- [ ] **Step 6: Smoke-run both pages**

Run: `timeout 20 uv run powerflow_analytics/app/app.py & sleep 8 && curl -s http://127.0.0.1:8050/comparison | head -c 200; wait`
Expected: HTML response (Dash renders pages client-side; a 200 with the app shell is sufficient).

- [ ] **Step 7: Commit**

```bash
git add powerflow_analytics/app/pages/comparison.py powerflow_analytics/README.md powerflow_analytics/tests/test_pages.py
git commit -m "feat(powerflow_analytics): study comparison page + README"
```
