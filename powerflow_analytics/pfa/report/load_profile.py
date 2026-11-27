"""Median ERCOT load profile: figure and page."""
from __future__ import annotations

import datetime as dt

import pandas as pd
import plotly.graph_objects as go

from pfa.report import html


def mon(mmdd: str) -> str:
    return dt.date(2000, int(mmdd[:2]), 1).strftime("%b").lower()


def build_figure(df, start_mmdd: str, end_mmdd: str, zone: str = "ERCOT") -> go.Figure:
    fig = go.Figure()
    for year in sorted(df["year"].unique()):
        sub = df[df["year"] == year].sort_values("he")
        fig.add_trace(
            go.Scatter(
                x=sub["he"],
                y=sub["median_load_gw"],
                mode="lines+markers",
                name=str(year),
            )
        )
    zone_label = "ERCOT system" if zone == "ERCOT" else f"{zone} LZ"
    fig.update_layout(
        title=f"{zone_label} median load by hour, {mon(start_mmdd).title()} {start_mmdd[3:]}-{end_mmdd[3:]}",
        xaxis_title="Hour Ending (HE)",
        yaxis_title="Median load (GW)",
        hovermode="x unified",
        xaxis=dict(dtick=1, range=[0.5, 24.5]),
        template="plotly_white",
    )
    return fig


def table(df: pd.DataFrame) -> pd.DataFrame:
    """Hour-ending x year grid of median load (GW), as printed."""
    return df.pivot(index="he", columns="year", values="median_load_gw").round(2)


def render(fig: go.Figure) -> str:
    return html.page(fig.layout.title.text, html.figure(fig, True))
