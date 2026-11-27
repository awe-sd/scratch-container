"""Network reference data: branch_id -> teid / bus names (branch_tracking table) and bus -> nominal kV
(CIM TeidMap export). The one module that knows where these files live.

Today they are CSVs from the frozen archive/branch_tracking project; set PFA_NETWORK_REF_DIR to a
directory holding both files when the source moves. The seam for a future database table is the two
private `_read_*` functions: replace their bodies, keep the public loaders.
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from .. import config

_branch_map: pd.DataFrame | None = None
_kv_map: dict[int, float] | None = None


def _missing(what: str, where: str) -> FileNotFoundError:
    return FileNotFoundError(
        f"{what} not found ({where}); set {config.NETWORK_REF_DIR_ENV} to a directory containing it")


def _ref_dir(default: Path) -> Path:
    override = os.environ.get(config.NETWORK_REF_DIR_ENV)
    return Path(override) if override else default


def _branch_map_path() -> Path:
    path = _ref_dir(config.BRANCH_MAP_DIR) / config.BRANCH_MAP_FILE
    if not path.exists():
        raise _missing("branch map", str(path))
    return path


def _teidmap_path() -> Path:
    data_dir = _ref_dir(config.TEIDMAP_DIR)
    paths = sorted(data_dir.glob(config.TEIDMAP_GLOB))
    if not paths:
        raise _missing("bus kV map", f"no {config.TEIDMAP_GLOB} under {data_dir}")
    return paths[-1]  # latest export


def _read_branch_map() -> pd.DataFrame:
    return pd.read_csv(
        _branch_map_path(),
        usecols=["teid", "branch_id", "from_bus", "to_bus", "ckt", "default_status_final"],
    )


def _read_teidmap() -> pd.DataFrame:
    return pd.read_csv(_teidmap_path(), usecols=["PsseType", "BusNumber1", "Name"])


def clear_cache() -> None:
    global _branch_map, _kv_map
    _branch_map = _kv_map = None


def branch_map() -> pd.DataFrame:
    """branch_id -> teid / bus-name map. branch_id shares the 60M id-space with AWOPF BRANCHID
    columns and teid is the authoritative device id for outage lookups, so no DB query is needed."""
    global _branch_map
    if _branch_map is None:
        df = _read_branch_map()
        df = df.dropna(subset=["branch_id"])
        df["branch_id"] = df["branch_id"].astype("int64")
        _branch_map = df.drop_duplicates("branch_id").set_index("branch_id")
    return _branch_map


def teid_for_branch(branch_id: int) -> int | None:
    m = branch_map()
    if int(branch_id) in m.index:
        t = m.loc[int(branch_id), "teid"]
        return int(t) if pd.notna(t) else None
    return None


def teids_for_endpoints(names: list[str], limit: int = 3) -> list[int]:
    """Fallback when a branch id isn't in the map (e.g. tofinder reports an
    internal transformer winding): devices touching any of these bus names.
    Star-bus names resolve a winding to its parent transformer bank."""
    names = [str(n).strip() for n in names if n and str(n).strip()]
    if not names:
        return []
    m = branch_map()
    hit = m[m["from_bus"].isin(names) | m["to_bus"].isin(names)]
    return [int(t) for t in hit["teid"].dropna().unique()[:limit]]


def bus_kv_map() -> dict[int, float]:
    """Bus number -> nominal kV; TeidMap bus rows carry the voltage in Name ("PERRIN_T8 (CN1) 138kV")."""
    global _kv_map
    if _kv_map is None:
        df = _read_teidmap()
        df = df[(df["PsseType"] == "Bus") & df["Name"].notna()]
        kv = df["Name"].str.extract(r"([\d.]+)kV\s*$")[0].astype(float)
        m = pd.DataFrame({"bus": df["BusNumber1"].astype(int), "kv": kv}).dropna()
        _kv_map = m.groupby("bus")["kv"].max().to_dict()
    return _kv_map


def constraint_kv(fromnum: int, tonum: int) -> float | None:
    """Max kV of the constraint's two endpoint buses (transformers span levels; the higher side names the class)."""
    m = bus_kv_map()
    kvs = [m.get(int(fromnum)), m.get(int(tonum))]
    kvs = [k for k in kvs if k is not None]
    return max(kvs) if kvs else None
