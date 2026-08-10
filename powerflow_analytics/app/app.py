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
