"""Shortlist page: one column spec drives header, filter row, body and alignment."""
from __future__ import annotations

import pandas as pd

from pfa import periods
from pfa.analysis.screening import PENALTY_TIERS, Thresholds
from pfa.analysis.shortlist_value import rent_col_name
from pfa.report import html


def columns(rent_col: str, label: str) -> list[html.Col]:
    return [
        html.Col("Label", "Label", "text", "l"),
        html.Col("From bus", "From bus", "id"),
        html.Col("From name", "From name", "text", "l"),
        html.Col("To bus", "To bus", "id"),
        html.Col("To name", "To name", "text", "l"),
        html.Col("Ckt", "Ckt", "text", "l"),
        html.Col("Contingency", "Contingency", "text", "l"),
        html.Col("Direction", "Direction", "id"),
        html.Col("Impact share", "Impact share", "num2"),
        html.Col("Pre binds", "Pre binds", "int"),
        html.Col("Post binds", "Post binds", "int"),
        html.Col("Post days (of 5)", "Post days (of 5)", "int"),
        html.Col("λ avg (all)", "lam avg", "num1"),
        html.Col("λ P50 (all)", "lam p50", "num1"),
        html.Col("λ P50 (ex-cap, gate basis)", "lam p50 gate", "num1"),
        html.Col("Dispatch nodes", "Dispatch nodes", "int"),
        html.Col(rent_col, rent_col, "money"),
        html.Col("Ticket", "Ticket", "text", "l"),
        html.Col("Status", "Status", "text", "l"),
        html.Col("Flip exempt", "Flip exempt", "bool", "l"),
        html.Col("Thin intensity", "Thin intensity", "bool", "l"),
        html.Col(f"Outage days in {label}", f"Outage days in {label}", "int"),
        html.Col("Coverage", "coverage", "text"),
        html.Col("Thin window", "thin window evidence", "text", "l"),
        html.Col(f"P(bind) {label} on-peak", f"P(bind) {label} on-peak", "num3"),
        html.Col("E[lambda|bind]", "E[lambda|bind]", "num1"),
        html.Col("lambda P50", "lambda P50", "num1"),
        html.Col("lambda P90", "lambda P90", "num1"),
        html.Col("Unpriced deep hours %", "unpriced deep hours %", "num1"),
        html.Col(f"{label} value $/MWh/SF", f"{label} value $/MWh/SF", "num3"),
        html.Col("Path", "Path", "text", "l"),
        html.Col("Path SF", "Path SF", "text"),
        html.Col("Edge $", "Edge $", "num2"),
        html.Col("Valuation status", "status", "text", "l"),
    ]


def render(rows: pd.DataFrame, study: int, cutoff: str, month: str, th: Thresholds) -> str:
    label = periods.month_label(month)
    intro = html.note(
        f"Step-1 screen output after gates (impact share &ge; {th.share_min} direction-corrected, &ge;{th.post_days_min} of 5 sampled "
        f"post-cutoff days, rent &ge; ${th.rent_min:,}, &ge;{th.nqual_min} dispatch nodes), then a soft binding-intensity band on "
        f"post_binds &times; &lambda;P50(ex-cap, post-cutoff, non-zero, non-penalty): hard floor {th.intensity_min_hard}, full pass "
        f"{th.intensity_min_full}. Rows in the soft band are kept and flagged <b>Thin intensity</b>; rows below the hard floor are "
        f"kept only if rescued by the flip-detection heuristic (<b>Flip exempt</b>). C no-dispatch (see step1_screen.csv) uses a "
        f"penalty-share test (&gt;{th.penalty_share_max*100:.0f}% of LP rows at the {PENALTY_TIERS[0]:.0f}/{PENALTY_TIERS[1]:.0f} "
        f"SCOPF penalty cap) plus the legacy flatness test. Direction = OUTBRANCHDIRECTION. Filters accept text or &gt;/&lt; on "
        f"numbers.")
    body = intro + html.table(rows, columns(rent_col_name(cutoff), label))
    return html.page(f"Stage-2 candidates — study {study}, {len(rows)} constraints", body)
