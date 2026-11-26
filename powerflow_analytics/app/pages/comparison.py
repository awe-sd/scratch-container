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
