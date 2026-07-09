from datetime import date
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "branch_tracking" / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = REPO_ROOT / "branch_tracking" / "output"

# --- build_inservice_retirement_dates.py:226-265 ---

ISOMARKETID_ERCOT = 6
REASON_NEW_EQUIPMENT = 4
REASON_RETIREMENT = 9

DEFAULT_IN_SERVICE_DATE = pd.Timestamp("1990-01-01")
DEFAULT_RETIREMENT_DATE = pd.Timestamp("2099-12-31")

# Consecutive events (sorted by date) whose gap is within this tolerance are
# treated as one continuous process re-ticketed on expiry, not separate
# events. teid=527244's chain had 0-1 minute gaps between tickets; a few
# days of buffer covers a crew resubmitting after a weekend without risking
# false-chaining of genuinely unrelated events months/years apart.
CHAIN_GAP_TOLERANCE = pd.Timedelta(days=3)

# Substring match (case-insensitive) against `status`/`ReqStatus` -- derived
# from dbo.toStatus's contents (Cancelled/Canceled/Cancl/Cancelled by
# Company, Withdrawn/Withd, Rejct, Denied, Retracted, Recalled, Annulled,
# Terminated). CancellationDate IS NOT NULL is checked separately/additionally.
INVALID_STATUS_KEYWORDS = (
    "cancel", "cancl", "withdraw", "withd", "reject", "rejct", "denied",
    "retract", "recall", "annul", "terminat",
)

# Minimum recent PTOBRANCH status rows required to trust a Closed-status
# contradiction enough to auto-revert a retirement_date -- a single
# snapshot (n_status_rows=1) showing Closed isn't strong enough evidence
# on its own, even if pct_closed=1.0 for that one row.
STATUS_CONTRADICTION_MIN_ROWS = 5

# Literal placeholder values seen in EquipmentName -- these assert nothing
# about the device, so they should be treated as "unknown" (like a NULL),
# not compared at all. Found via teid=324528's outage tagged "BLANK".
PLACEHOLDER_NAMES = {"BLANK", "NONE", "NA", "TBD", "UNKNOWN"}

# --- map_unmapped_dampsse_teids.py:64 ---

# DeviceType -> ercotDampsseFileTypeId (1=Line, 2=Transformer)
FILETYPE_FOR_DEVICE = {"Line": 1, "Transformer": 2}

# --- build_dampsse_default_status.py:53-54 ---

WINDOW_DAYS = 730  # ~2 years of hourly DA models, per the user's direction
AWDATEID_ANCHOR = (44926, date(2023, 1, 1))  # confirmed by schema exploration

# --- cache_dampsse_ckt.py:19 ---

CKT_WINDOW_DAYS = 90
