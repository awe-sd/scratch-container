"""Resolved default_status: DAM PSSE dominant status vs. auction fallback.

Pure function extracted verbatim from build_final_branch_table.py:main's
resolved-status block. See that script's module docstring for the full
rationale.
"""
import pandas as pd


def resolve_default_status(table: pd.DataFrame) -> pd.DataFrame:
    """Adds default_status (DAM PSSE inService dominant status is the
    primary indicator; the auction-based value is only a fallback where
    DAM has no coverage; blank when neither knows) and
    default_status_source ("dampsse_inservice" / "auction_fallback" / NA).
    From build_final_branch_table.py:main."""
    table = table.copy()
    table["default_status"] = table["dampsse_default_status"].fillna(
        table["implied_default_status"]
    )
    table["default_status_source"] = pd.NA
    table.loc[table["dampsse_default_status"].notna(), "default_status_source"] = "dampsse_inservice"
    table.loc[
        table["dampsse_default_status"].isna() & table["implied_default_status"].notna(),
        "default_status_source",
    ] = "auction_fallback"
    return table
