"""Dashboard entrypoint.

Run: uv run powerflow_analytics/app/app.py  ->  http://127.0.0.1:8050
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app as _app_package  # noqa: F401  (ensure "app" is a loaded *package* in
# sys.modules before Dash() below: Dash's page auto-discovery only prefixes
# discovered page modules with the app name when that name resolves to an
# imported package (see dash._pages._module_name_is_package). Passing the
# package name "app" here — instead of this module's own __name__, which is
# "app.app" / "__main__" depending on how it's run — makes Dash import the
# pages folder as "app.pages.explorer", the SAME sys.modules key that
# `from app.pages import explorer` uses elsewhere (e.g. in tests). Without
# this, Dash would auto-discover the page under the top-level key
# "pages.explorer" while a direct import uses "app.pages.explorer" — two
# distinct module objects for one file, each running register_page() and the
# @callback decorators, leaving dash.page_registry with two "/" entries.
import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    "app",
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
