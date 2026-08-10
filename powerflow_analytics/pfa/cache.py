"""Per-study parquet cache with a DuckDB view layer."""
from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from . import config


class StudyCache:
    def __init__(self, study_id: int):
        self.study_id = study_id
        self.dir = config.study_cache_dir(study_id)

    def path(self, table: str) -> Path:
        return self.dir / f"{table.lower()}.parquet"

    def has(self, table: str) -> bool:
        return self.path(table).exists()

    def save(self, table: str, df: pd.DataFrame) -> Path:
        p = self.path(table)
        df.to_parquet(p, index=False)
        return p

    def load(self, table: str) -> pd.DataFrame:
        p = self.path(table)
        if not p.exists():
            raise FileNotFoundError(
                f"{p} not cached — run scripts/pull_study.py --study {self.study_id} first"
            )
        return pd.read_parquet(p)

    def duckdb(self) -> duckdb.DuckDBPyConnection:
        """In-memory DuckDB with one view per cached table."""
        con = duckdb.connect()
        for p in sorted(self.dir.glob("*.parquet")):
            con.execute(f"CREATE VIEW {p.stem} AS SELECT * FROM read_parquet('{p}')")
        return con
