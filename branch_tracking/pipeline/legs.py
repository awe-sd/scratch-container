"""Transformer leg classification/pairing helpers, extracted verbatim from
scripts/build_transformer_leg_map.py.

Pure functions only -- DB loaders, CSV writes, and print/report bookkeeping
stay in the script wrapper. See that script's module docstring for the
full rationale (the three leg-pairing cases). No logic here should diverge
from the original script -- behavioral equivalence rests on verbatim
extraction from build_transformer_leg_map.py plus tests/test_legs.py.
This module is NOT covered by the golden byte-identity gate
(tests/test_goldens.py): its consuming script is DB-dependent and isn't
among the scripts that gate re-runs.
"""
import re

import pandas as pd

from .mapping import HIGH_SIDE_RE

# --- build_transformer_leg_map.py:38-44 ---

LOW_SIDE_RE_STR = r"(_?LOSIDE|_?LOW|_?L)$"
LEG_STRIP_RE_STR = r"(_?HISIDE|_?HIGH|_?H|_?LOSIDE|_?LOW|_?L)$"

LOW_SIDE_RE = re.compile(LOW_SIDE_RE_STR, re.IGNORECASE)
LEG_STRIP_RE = re.compile(LEG_STRIP_RE_STR, re.IGNORECASE)


# --- build_transformer_leg_map.py:47-54 ---


def classify_leg(op_eqcode):
    s = str(op_eqcode).strip()
    if HIGH_SIDE_RE.search(s):
        return "H"
    if LOW_SIDE_RE.search(s):
        return "L"
    return None


# --- build_transformer_leg_map.py:56-58 ---


def base_name(op_eqcode):
    return LEG_STRIP_RE.sub("", str(op_eqcode).strip().upper())


# --- build_transformer_leg_map.py:60-65 ---


def bus_pair(row, from_col="FromName", to_col="ToName"):
    a, b = row[from_col], row[to_col]
    if pd.isna(a) or pd.isna(b):
        return None
    return frozenset([str(a), str(b)])


# --- build_transformer_leg_map.py:85-87 ---


def pick_best(rows, prefer_col="branchID"):
    return rows.sort_values(prefer_col, ascending=False).iloc[0]
