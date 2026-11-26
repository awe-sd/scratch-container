"""teid -> branch_id duplicate-resolution logic, extracted verbatim from
scripts/build_teid_branchid_map.py.

Pure functions/passes only -- DB loaders, CSV writes, and print/report
bookkeeping stay in the script wrapper. See that script's module docstring
for the full rationale of each resolution tier (opeqcode-exact match,
exact-duplicate collapse, fuzzy match, high-side + latest-id catch-all).
No logic here should diverge from the original script -- behavioral
equivalence rests on verbatim extraction from build_teid_branchid_map.py
plus tests/test_mapping.py. This module is NOT covered by the golden
byte-identity gate (tests/test_goldens.py): its consuming script is
DB-dependent and isn't among the scripts that gate re-runs.
"""
import re
from difflib import SequenceMatcher

from .config import FUZZY_MIN_TOP_RATIO, FUZZY_MIN_MARGIN

# --- build_teid_branchid_map.py:102-103 ---


def fuzzy_ratio(a, b):
    return SequenceMatcher(None, str(a).strip().upper(), str(b).strip().upper()).ratio()


# --- build_teid_branchid_map.py:106-110 ---

HIGH_SIDE_RE = re.compile(r"(_?HISIDE|_?HIGH|_?H)$", re.IGNORECASE)


def is_high_side(op_eqcode):
    return bool(HIGH_SIDE_RE.search(str(op_eqcode).strip()))


# --- build_teid_branchid_map.py:main, lines 182-262 ---
# Extracted verbatim: the four layered duplicate-resolution passes, run in
# order, over a `merged` frame that already has `match_status` ("matched" /
# "unmatched" / "duplicate_match") and `opeq_agrees` columns populated by
# the caller. Returns the same frame with match_status resolved further
# where possible (duplicate_resolved_by_opeqcode /
# duplicate_resolved_exact_duplicate / duplicate_resolved_by_fuzzy_match /
# duplicate_resolved_by_latest_id) and non-winning duplicate rows dropped.


def resolve_duplicates(candidates_frame):
    merged = candidates_frame

    # Resolve duplicate_match groups where exactly one candidate's
    # OP_EQCODE agrees with the CIM OpEqName -- drop the other candidate
    # row(s) and reclassify. Recompute n_agree fresh after each boolean
    # mask rather than reusing masks across a row-dropping step, to avoid
    # stale-index alignment bugs.
    is_dup = merged["match_status"] == "duplicate_match"
    n_agree = merged.groupby("teid")["opeq_agrees"].transform("sum")
    drop_mask = is_dup & (n_agree == 1) & ~merged["opeq_agrees"]
    merged = merged.loc[~drop_mask].reset_index(drop=True)

    is_dup = merged["match_status"] == "duplicate_match"
    n_agree = merged.groupby("teid")["opeq_agrees"].transform("sum")
    resolved_mask = is_dup & (n_agree == 1) & merged["opeq_agrees"]
    merged.loc[resolved_mask, "match_status"] = "duplicate_resolved_by_opeqcode"

    # Exact-duplicate resolver: groups where 2+ candidates agree with
    # OpEqName are the same element entered more than once. Drop any
    # non-agreeing candidate in those groups first (clearly wrong), then
    # keep only the highest branch_id among the agreeing copies.
    is_dup = merged["match_status"] == "duplicate_match"
    n_agree = merged.groupby("teid")["opeq_agrees"].transform("sum")
    multi_agree_group = is_dup & (n_agree > 1)
    drop_non_agreeing_in_multi = multi_agree_group & ~merged["opeq_agrees"]
    merged = merged.loc[~drop_non_agreeing_in_multi].reset_index(drop=True)

    is_dup = merged["match_status"] == "duplicate_match"
    n_agree = merged.groupby("teid")["opeq_agrees"].transform("sum")
    multi_agree_group = is_dup & (n_agree > 1)
    max_branch_id_in_group = merged.groupby("teid")["branch_id"].transform("max")
    drop_non_max_in_multi = multi_agree_group & (merged["branch_id"] != max_branch_id_in_group)
    merged = merged.loc[~drop_non_max_in_multi].reset_index(drop=True)

    is_dup = merged["match_status"] == "duplicate_match"
    still_multi = is_dup & (merged.groupby("teid")["teid"].transform("count") == 1)
    merged.loc[still_multi, "match_status"] = "duplicate_resolved_exact_duplicate"

    # Fuzzy-match resolver: for remaining duplicate_match (zero-agree)
    # groups, rank candidates by string similarity to OpEqName and accept
    # the top one only if it clears a quality floor AND is clearly
    # separated from the runner-up (see docstring point 4 for calibration).
    is_dup = merged["match_status"] == "duplicate_match"
    merged["fuzzy_ratio"] = 0.0
    merged.loc[is_dup, "fuzzy_ratio"] = merged.loc[is_dup].apply(
        lambda r: fuzzy_ratio(r["OP_EQCODE"], r["OpEqName"]), axis=1
    )
    ranked = merged.loc[is_dup].sort_values("fuzzy_ratio", ascending=False)
    top_ratio = ranked.groupby("teid")["fuzzy_ratio"].transform("max")
    second_ratio = ranked.groupby("teid")["fuzzy_ratio"].transform(
        lambda s: s.iloc[1] if len(s) > 1 else 0.0
    )
    is_top = ranked["fuzzy_ratio"] == top_ratio
    fuzzy_resolvable = (top_ratio >= FUZZY_MIN_TOP_RATIO) & (
        (top_ratio - second_ratio) >= FUZZY_MIN_MARGIN
    )
    drop_non_top_in_resolvable = ranked.index[(fuzzy_resolvable & ~is_top)]
    merged = merged.drop(index=drop_non_top_in_resolvable).reset_index(drop=True)

    is_dup = merged["match_status"] == "duplicate_match"
    still_multi = is_dup & (merged.groupby("teid")["teid"].transform("count") == 1)
    merged.loc[still_multi, "match_status"] = "duplicate_resolved_by_fuzzy_match"

    # High-side + latest-id catch-all: teid is the grain (1:1). Everything
    # still duplicate_match here is a Transformer (100% of the 176 at the
    # prior baseline) -- prefer the high-side ('_H'/'HIGH') leg where the
    # group has one; drop any non-high-side candidate when that's the case.
    is_dup = merged["match_status"] == "duplicate_match"
    merged["is_high_side"] = merged["OP_EQCODE"].apply(is_high_side)
    has_high_side = merged.groupby("teid")["is_high_side"].transform("any")
    drop_non_high_side = is_dup & has_high_side & ~merged["is_high_side"]
    merged = merged.loc[~drop_non_high_side].reset_index(drop=True)

    # Whatever's left per teid (a single high-side row, multiple high-side
    # candidates, or no H/L naming at all e.g. parallel-unit banks like
    # 'XFMR21'/'XFMR22') -- keep the highest (latest) branch_id.
    is_dup = merged["match_status"] == "duplicate_match"
    max_branch_id_in_group = merged.groupby("teid")["branch_id"].transform("max")
    drop_non_max = is_dup & (merged["branch_id"] != max_branch_id_in_group)
    merged = merged.loc[~drop_non_max].reset_index(drop=True)

    is_dup = merged["match_status"] == "duplicate_match"
    merged.loc[is_dup, "match_status"] = "duplicate_resolved_by_latest_id"

    return merged
