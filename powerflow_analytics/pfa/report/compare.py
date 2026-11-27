"""Study comparison page: persisting / new / dropped constraint tables."""
from __future__ import annotations

import pandas as pd

from pfa.report import html

PERSIST_COLS = ["CONSTRAINT", "FROMNAME", "TONAME", "KV345", "LIMIT_MVA", "LAM_P50", "P_BIND_18",
                "USD_MWH_P50", "RENT_SCORE", "USD_MWH_P50_A", "RENT_SCORE_A",
                "DRIVER_A", "TICKET_A", "TICKET_STATUS_A"]
NEW_COLS = ["CONSTRAINT", "FROMNAME", "TONAME", "KV345", "LIMIT_MVA", "LAM_P50", "P_BIND_18",
            "USD_MWH_P50", "RENT_SCORE", "N_RUNS_BINDING", "FASTSCAN_MAX_NEG", "BEST_PATH"]
DROPPED_COLS = ["CONSTRAINT", "FROMNAME", "TONAME", "KV345", "RENT_SCORE", "TICKET", "TICKET_STATUS"]


def present(df: pd.DataFrame, cols: list[str]) -> list[str]:
    return [c for c in cols if c in df.columns]


def _cols(df: pd.DataFrame, cols: list[str]) -> list[html.Col]:
    names = present(df, cols)
    return [html.Col(c, c, "text", "l" if i in (0, 1, 2, len(names) - 1) else "r") for i, c in enumerate(names)]


def _table(df: pd.DataFrame, cols: list[str]) -> str:
    return html.table(df, _cols(df, cols), row_class=lambda r: "hi" if r.get("KV345") else "")


def render(study_a: int, study_b: int, month: str, min_bind: int,
           persist: pd.DataFrame, new: pd.DataFrame, dropped: pd.DataFrame, generated: str) -> str:
    persist = persist.rename(columns={"DRIVER": "DRIVER_B", "TICKET": "TICKET_B"})
    body = "\n".join([
        html.paragraph(
            f"Study {study_b} includes implied (breaker) outages. Binding ≥ {min_bind} runs, LP-priced, "
            f"penalty-tier λ excluded. $/MWh per 1.0 SF over the 5x16 block; Rent score = P50 $/MWh × limit MVA. "
            f"<b>345 kV rows highlighted.</b>", "meta"),
        html.section(f"Persisting constraints ({len(persist)}) — bind in BOTH studies (highest confidence)",
                     html.note(f"_A columns = study {study_a} values; tickets were verified in study {study_a}."),
                     _table(persist, PERSIST_COLS)),
        html.section(f"New in study {study_b} ({len(new)}) — implied/breaker-outage driven",
                     html.note("No outage ticket exists to verify (drivers are implied breaker states). "
                               "Evidence: fast-scan max % of historical hours with negative headroom on this topology, and the "
                               "cheapest completed path-opt path (option $/MWh @ avg SF) where a run exists."),
                     _table(new, NEW_COLS)),
        html.section(f"Dropped vs study {study_a} ({len(dropped)}) — bound in {study_a} only", _table(dropped, DROPPED_COLS)),
    ])
    return html.page(f"Study {study_b} vs {study_a} — CRR constraint comparison ({month})", body, generated=generated)
