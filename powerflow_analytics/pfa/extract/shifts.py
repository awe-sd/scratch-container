"""Shift-factor views (SHIFT_FACTORS.DBO.CPNODE_SHIFTS_VIEW / BUS_SHIFTS_VIEW).

As of 2026-08-10 both views are not authorized to the read_only role; the
readers probe access and return None so downstream analysis can degrade to
the LPDELTAMW-only fallback. Once access lands, fetch_* should slice on
(ISOMARKETID, STUDYID, TOPOLOGYID) like SHIFT_FACTORS.DBO.DEVICE_SHIFTS.
"""
from __future__ import annotations

import pandas as pd

from .. import sf

CPNODE_VIEW = "SHIFT_FACTORS.DBO.CPNODE_SHIFTS_VIEW"
BUS_VIEW = "SHIFT_FACTORS.DBO.BUS_SHIFTS_VIEW"


def probe_access() -> dict[str, bool]:
    out = {}
    for name, view in [("cpnode", CPNODE_VIEW), ("bus", BUS_VIEW)]:
        try:
            sf.query("SHIFT_FACTORS", f"SELECT * FROM {view} LIMIT 1")
            out[name] = True
        except Exception:
            out[name] = False
    return out


def fetch_bus_shifts(study_id: int, topology_ids: list[int]) -> pd.DataFrame | None:
    """Bus-level shift factors for a study's topologies; None if not authorized."""
    if not probe_access()["bus"]:
        return None
    if not topology_ids:
        return None
    ids = ",".join(str(int(t)) for t in topology_ids)
    return sf.query(
        "SHIFT_FACTORS",
        f"""
        SELECT * FROM {BUS_VIEW}
        WHERE ISOMARKETID = 6 AND STUDYID = {int(study_id)}
          AND TOPOLOGYID IN ({ids})
        """,
    )
