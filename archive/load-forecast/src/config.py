"""Central config for the load-forecast project.

DB rules (see load-forecast/CLAUDE.md): awconnect profile read_only, SQL Server
queries strictly sequential and date-bounded, extract-once → parquet cache under
data/raw/, analysis reads cache only.
"""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DERIVED_DIR = PROJECT_ROOT / "data" / "derived"

AWS_PROFILE = "read_only"

# Zones in scope for v0 (CLAUDE.md). Raw pulls keep every zone column so the
# cache never has to be re-pulled if scope widens.
ZONES = ["NCENT", "COAST", "SCENT"]

# ercotLoadView column per zone (confirmed in powerflow_analytics/pfa/extract/load.py).
ZONE_COLUMNS = {
    "NCENT": "WZ_NORTH_CENTRAL_LD",
    "COAST": "WZ_COAST_LD",
    "SCENT": "WZ_SOUTH_CENTRAL_LD",
    "NORTH": "WZ_NORTH_LD",
    "SOUTH": "WZ_SOUTHERN_LD",
    "EAST": "WZ_EAST_LD",
    "FWEST": "WZ_FAR_WEST_LD",
    "WEST": "WZ_WEST_LD",
}
SYSTEM_COLUMN = "ERCOT_ALL_LD"

HISTORY_START_YEAR = 2015
TRAIN_END = "2024-12-31"  # hard train/test wall — nothing after this enters a fit
BASE_YEAR = 2019  # size_idx = 1.0 here (pre-COVID, pre-Uri)

# Size-index extrapolation window (last N fitted year-effects), per zone.
# From experiments nfit3/nfit6 (2026-08-14, docs/training_log.md): NCENT and
# COAST track recent acceleration better with 3; SCENT's one-off 2022 boom
# overweights a 3-point fit (growth error +0.93 → +4.26 pp) — keep 6.
SIZE_EXTRAP_YEARS = {"NCENT": 3, "COAST": 3, "SCENT": 6}

# Event windows (CLAUDE.md hard rules): uri excluded from ALL fitting;
# covid downweighted to 0.25 in size-index fitting only.
URI_WINDOW = ("2021-02-10", "2021-02-20")
COVID_WINDOW = ("2020-03-01", "2020-06-30")
COVID_WEIGHT = 0.25

# Outage-suppression windows: served load ≠ demand (storm outages), so these
# hours carry no weather-response signal. Zone-scoped; excluded from ALL
# fitting (shape and size), like uri. Identified 2026-08-14 (Opus review D3):
# COAST July 2024 daily energy ran 13-51% below adjacent years.
OUTAGE_WINDOWS = [
    ("2024-05-16", "2024-05-19", frozenset({"COAST"})),  # Houston derecho
    ("2024-07-08", "2024-07-21", frozenset({"COAST"})),  # Hurricane Beryl
]

_configured = False


def configure() -> None:
    """awconnect.configure(), idempotent."""
    global _configured
    if not _configured:
        import awconnect

        awconnect.configure(AWS_PROFILE)
        _configured = True
