"""Dispatch screen: is there dispatchable relief for a constraint at all, and how many
qualifying nodes (a screening question, not a price). Band thresholds come from shadow_price.

Source is CPNODE_SHIFTS_VIEW: DEADBUS=0, NAME not LZ_/WZ_. DEVICE_SHIFTS has no rows for recent studies.
"""
from __future__ import annotations

import pandas as pd

from ..constraint_id import ConstraintId, constraint_key
from ..extract import shifts
from .shadow_price import MAX_SF, MIN_SF, PAIR_MAX_SF, PAIR_MIN_SF


def bulk_dispatch_features(study_id: int, constraints: list[str]) -> pd.DataFrame:
    """One round trip for ALL candidate constraints: qualifying dispatch node count
    (MIN_SF<=|SF|<MAX_SF) and dispatch-pair existence (PAIR_MIN_SF<=|SF|<PAIR_MAX_SF,
    opposite-sign both sides).

    One row per constraint (index CONSTRAINT) with N_QUAL and DISPATCH_OK (bool); constraints
    with no CPNODE_SHIFTS_VIEW rows are absent — callers treat that as unknown (None), not a fail.
    """
    df = shifts.cpnode_dispatch_features(study_id, constraints, MIN_SF, MAX_SF, PAIR_MIN_SF, PAIR_MAX_SF)
    if df.empty:
        return df
    df["CONSTRAINT"] = constraint_key(df)
    df["DISPATCH_OK"] = (df["N_POS_PAIR"] > 0) & (df["N_NEG_PAIR"] > 0)
    return df.set_index("CONSTRAINT")[["N_QUAL", "DISPATCH_OK"]]


def qualifying_node_count(study_id: int, constraint: str) -> int:
    """Count of dispatchable cpnodes on this constraint: MIN_SF <= |PSENS| < MAX_SF (the band the
    screening report's dispatch column uses; wider than the PAIR_MIN_SF/PAIR_MAX_SF pair test)."""
    df = shifts.cpnode_qualifying_count(study_id, ConstraintId.parse(constraint), MIN_SF, MAX_SF)
    if df is None or df.empty:
        return 0
    return int(df["N"].iloc[0] or 0)


def dispatch_screen(study_id: int, constraint: str) -> str | None:
    """'unenforceable' when no dispatchable redispatch PAIR exists for this constraint
    (no dispatchable relief — ERCOT is unlikely to run the driving outage); None otherwise.

    Relief needs a pair: one cpnode that can go up and another that can go down, i.e. PSENS of
    OPPOSITE sign inside PAIR_MIN_SF <= |PSENS| < PAIR_MAX_SF. A same-sign-only cluster is an
    unenforceable/bottled constraint (STHRSCH8: only MILTON_RN clears the band, one-sided).
    Canaries: 8186-8913-1@STHRSCH8 must tag; 1436-2081-1@DWCSRAM5 must NOT (WCPP_CT1/CT2/ST1
    positive, CHISMGRD_RN/MDWPK_RN negative).
    """
    df = shifts.cpnode_pair_counts(study_id, ConstraintId.parse(constraint), PAIR_MIN_SF, PAIR_MAX_SF)
    if df is None or df.empty:
        return None
    n_pos = int(df["N_POS"].iloc[0] or 0)
    n_neg = int(df["N_NEG"].iloc[0] or 0)
    if n_pos == 0 or n_neg == 0:
        return "unenforceable — no dispatchable relief pair (LZ/WZ/radial/renewable-noise only); ERCOT unlikely to run it"
    return None
