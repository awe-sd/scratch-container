"""Central configuration for powerflow_analytics."""
from __future__ import annotations

from pathlib import Path

ISO_MARKET_ID = 6  # ERCOT
AWS_PROFILE = "read_only"
WAREHOUSE = "AI_READ_ONLY"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_ROOT = PROJECT_ROOT / "cache"
OUTPUT_ROOT = PROJECT_ROOT / "output"

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
