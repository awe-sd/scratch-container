"""The one door to SQL Server: read-only, strictly one query at a time, outage tables scoped."""
from __future__ import annotations

import re
import threading

import pandas as pd

from . import config

_LOCK = threading.Lock()
_NOISE = re.compile(r"'(?:[^']|'')*'|--[^\n]*|/\*.*?\*/", re.DOTALL)
_OUTAGE_TABLE = re.compile(r"\b(?i:from|join)\s+(?:\[?\w+\]?\s*\.\s*){0,2}\[?((?i:toAllIsos|toState|toStatus|toReason)\b|to[A-Z]\w*)")
_DIMENSION_TABLES = {"tostate", "tostatus", "toreason"}
_DIMENSION_KEY = re.compile(r"\bto(?:State|Status|Reason)Id\s*(?:=|in\s*\()", re.IGNORECASE)
_AFTER_FILTER = re.compile(r"\b(?:where|on)\b(.*)", re.IGNORECASE | re.DOTALL)
_ISO_PREDICATE = re.compile(r"\bisoMarketId\s*(?:=|in\s*\()", re.IGNORECASE)
_DEVICE_PREDICATE = re.compile(r"\b(?:BranchId|teid)\s*(?:=|in\s*\()", re.IGNORECASE)


def _check_outage_scope(sql: str) -> None:
    """Text check, not a SQL parser: comments/strings stripped; a to* table after FROM/JOIN (known names case-insensitive; a by-key lookup on only toState/toStatus/toReason is allowed) needs isoMarketId and BranchId/teid predicates (=/IN) after the first WHERE/ON; it cannot tell WHICH clause or table a predicate belongs to."""
    text = _NOISE.sub(" ", sql)
    tables = {t.lower() for t in _OUTAGE_TABLE.findall(text)}
    if not tables:
        return
    m = _AFTER_FILTER.search(text)
    rest = m.group(1) if m else ""
    if tables <= _DIMENSION_TABLES and _DIMENSION_KEY.search(rest):
        return  # by-key lookup on the small toState/toStatus/toReason dimensions
    if not (_ISO_PREDICATE.search(rest) and _DEVICE_PREDICATE.search(rest)):
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
