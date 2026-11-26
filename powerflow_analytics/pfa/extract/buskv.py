"""Bus-number -> nominal kV map, parsed from the CIM TeidMap export.

The TeidMap bus rows carry the voltage in the Name field ("PERRIN_T8 (CN1)
138kV"). Constraint kV = max of its two endpoint buses (transformers span
levels; the higher side names the constraint's class).
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .. import config

TEIDMAP_GLOB = "CIM_*_TeidMap.csv"
_kv_map: dict[int, float] | None = None


def _teidmap_path() -> Path:
    data_dir = config.PROJECT_ROOT.parent / "branch_tracking" / "data"
    paths = sorted(data_dir.glob(TEIDMAP_GLOB))
    if not paths:
        raise FileNotFoundError(f"no {TEIDMAP_GLOB} under {data_dir}")
    return paths[-1]  # latest export


def bus_kv_map() -> dict[int, float]:
    global _kv_map
    if _kv_map is None:
        df = pd.read_csv(_teidmap_path(), usecols=["PsseType", "BusNumber1", "Name"])
        df = df[(df["PsseType"] == "Bus") & df["Name"].notna()]
        kv = df["Name"].str.extract(r"([\d.]+)kV\s*$")[0].astype(float)
        m = pd.DataFrame({"bus": df["BusNumber1"].astype(int), "kv": kv}).dropna()
        _kv_map = m.groupby("bus")["kv"].max().to_dict()
    return _kv_map


def constraint_kv(fromnum: int, tonum: int) -> float | None:
    m = bus_kv_map()
    kvs = [m.get(int(fromnum)), m.get(int(tonum))]
    kvs = [k for k in kvs if k is not None]
    return max(kvs) if kvs else None
