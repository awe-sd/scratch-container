import re

from .config import PLACEHOLDER_NAMES

import pandas as pd


def normalize_name(value):
    """Strip to uppercase alphanumeric only, so formatting drift like
    "6520_G" vs "6520__G" (extra underscore) or "GSU2_Y" vs "GSU2Y"
    doesn't defeat an otherwise-real match."""
    if pd.isna(value):
        return None
    stripped = re.sub(r"[^A-Z0-9]", "", str(value).upper())
    if not stripped or stripped in PLACEHOLDER_NAMES:
        return None
    return stripped


def names_relate(a, b):
    """True if either normalized name contains the other. Uses pd.isna
    (not `is None`) for the guard: values reaching this function often
    flow through pandas .apply()/merge, which silently upcasts a Python
    None returned by normalize_name into a float NaN inside a mixed
    object column -- an `is None` check would miss that and crash on
    `str in nan`. pd.isna(a)/pd.isna(b) is a strict superset that also
    catches genuine None, so this is safe for both callers."""
    if pd.isna(a) or pd.isna(b):
        return False
    return a in b or b in a


UNIT_LEG_RE = re.compile(r"(\d+)\s*[-_]?\s*([HLT])?(?:[-_]?[HLT])?$")


def unit_and_leg(norm_name):
    """Extract (unit_digits, leg_letter) from the tail of a normalized
    name -- e.g. CMNSWAXFMR1H -> ('1','H'), SNDSWMR2L -> ('2','L'),
    MDOAT1 -> ('1', None). Transformer teids in our data name the winding
    unit + leg at the end; DAM leg defs do the same (MR1H, AT2, XF1A...).
    Returns (None, None) when no trailing unit digit is found."""
    if not norm_name:
        return None, None
    m = re.search(r"(\d+)([HLT]?)$", norm_name)
    if not m:
        # leg letter may follow the digits with other chars stripped, e.g. '...1LH'
        m = re.search(r"(\d+)([HLT])[HLT]$", norm_name)
        if not m:
            return None, None
    return m.group(1), (m.group(2) or None)


def pick_by_leg(our_norm, candidates):
    """Among transformer candidates sharing a station pair, prefer the one
    matching our unit digit and (per the pipeline's established
    high-side-preference convention) the H leg -- our mapped BRANCH row is
    the high-side leg wherever legs were distinguishable. Returns a single
    row or None when still ambiguous."""
    unit, leg = unit_and_leg(our_norm)
    if unit is None:
        return None
    prefer_leg = leg or "H"

    def score(name_norm):
        c_unit, c_leg = unit_and_leg(name_norm)
        s = 0
        if c_unit == unit:
            s += 2
        if c_leg == prefer_leg:
            s += 2
        elif c_leg is None and prefer_leg == "H":
            s += 1  # whole-transformer def, acceptable stand-in for H
        return s

    scored = candidates.assign(_score=candidates["name_norm"].apply(score))
    top = scored["_score"].max()
    if top < 2:
        return None
    winners = scored[scored["_score"] == top]
    return winners.iloc[0] if len(winners) == 1 else None
