"""Thin Snowflake query wrapper with column validation."""
from __future__ import annotations

import pandas as pd

from . import config


def query(db_name: str, sql: str) -> pd.DataFrame:
    config.configure()
    from awconnect import snowflake

    return snowflake.performQuery(db_name, sql, warehouse=config.WAREHOUSE, logInfo=False)


def validate_columns(df: pd.DataFrame, expected: list[str], source: str) -> None:
    """Fail loudly if a source table stopped carrying the columns we rely on."""
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise RuntimeError(
            f"{source}: expected columns missing {missing}; observed columns: {list(df.columns)}. "
            "The source table schema likely changed — update the reader."
        )
