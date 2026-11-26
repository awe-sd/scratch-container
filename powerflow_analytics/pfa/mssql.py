"""The one door to SQL Server: read-only, strictly one query at a time, outage tables scoped."""
from __future__ import annotations

import re
import threading

import pandas as pd

from . import config

_LOCK = threading.Lock()
_ISO_PREDICATE = re.compile(r"isoMarketId", re.IGNORECASE)
_DEVICE_PREDICATE = re.compile(r"\b(BranchId|teid)\b", re.IGNORECASE)


def _check_outage_scope(sql: str) -> None:
    # Unscoped scans of the to* outage tables hang the server.
    reads_outage = re.search(r"toAllIsos", sql, re.IGNORECASE) or re.search(r"\bto[A-Z]\w*", sql)
    if reads_outage and not (_ISO_PREDICATE.search(sql) and _DEVICE_PREDICATE.search(sql)):
        raise ValueError(
            "SQL Server outage-table query must be scoped: include an isoMarketId predicate and a "
            "BranchId or teid predicate (unscoped toAllIsos scans hang the server)."
        )


def query(sql: str, database: str = "AW") -> pd.DataFrame:
    _check_outage_scope(sql)
    config.configure()
    from awconnect import db

    with _LOCK:
        return db.getDfFromAwDb(sql, database=database)
