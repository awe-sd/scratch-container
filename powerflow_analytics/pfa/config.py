"""Central configuration for powerflow_analytics."""
from __future__ import annotations

from pathlib import Path

ISO_MARKET_ID = 6  # ERCOT
AWS_PROFILE = "read_only"
WAREHOUSE = "AI_READ_ONLY"
FLOW_ANALYSIS_DB = "AW"
FLOW_ANALYSIS = f"{FLOW_ANALYSIS_DB}.FLOW_ANALYSIS"  # fast-scan tables

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_ROOT = PROJECT_ROOT / "cache"
OUTPUT_ROOT = PROJECT_ROOT / "output"

# network reference files (frozen branch_tracking export); PFA_NETWORK_REF_DIR points both at one directory
NETWORK_REF_DIR_ENV = "PFA_NETWORK_REF_DIR"
BRANCH_MAP_DIR = PROJECT_ROOT.parent / "archive" / "branch_tracking" / "output"
BRANCH_MAP_FILE = "branch_tracking_table_final.csv"
TEIDMAP_DIR = PROJECT_ROOT.parent / "archive" / "branch_tracking" / "data"
TEIDMAP_GLOB = "CIM_*_TeidMap.csv"

_configured = False


def configure() -> None:
    """awconnect.configure(), idempotent."""
    global _configured
    if not _configured:
        import awconnect

        awconnect.configure(AWS_PROFILE)
        _configured = True


def study_cache_dir(study_id: int) -> Path:
    d = CACHE_ROOT / f"study_{study_id}"
    d.mkdir(parents=True, exist_ok=True)
    return d
