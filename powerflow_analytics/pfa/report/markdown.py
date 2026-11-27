"""Markdown helpers shared by the text reports."""
from __future__ import annotations

import pandas as pd


def table(df: pd.DataFrame, cols: list[str] | None = None, n: int | None = None, floats: str = ".3f") -> str:
    """Pipe table of the first n rows of `cols` that exist in df; floats formatted with `floats`."""
    d = df if cols is None else df[[c for c in cols if c in df]]
    d = d if n is None else d.head(n)
    lines = ["| " + " | ".join(d.columns) + " |", "|" + "---|" * len(d.columns)]
    for row in d.itertuples(index=False):
        lines.append("| " + " | ".join(format(v, floats) if isinstance(v, float) else str(v) for v in row) + " |")
    return "\n".join(lines)


def heading(text: str, level: int = 2) -> str:
    return f"{'#' * level} {text}"


def code_block(text: str) -> str:
    return f"```\n{text}\n```"
