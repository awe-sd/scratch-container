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
