"""Step-1 screening classifier: outage-driven/dispatchable (A), baseline
binder (B), no-dispatch/unenforceable (C), outage-relieved/bearish (D).

Pure logic only (no DB access) so it can be unit-tested on synthetic
inputs — the DB-touching feature computation lives in
scripts/build_screening_report.py.
"""
from __future__ import annotations

TOP_SHARE_MIN = 0.25  # class A: top tofinder group must move this share of preflow


def classify_constraint(
    top_share: float | None,
    dispatch_ok: bool | None,
    penalty: bool,
    pre_rate: float | None,
    post_rate: float | None,
) -> tuple[str, str]:
    """Returns (class_letter, reason).

    Precedence: D (bearish — the outage relieves the constraint, or it was a
    pre-cutoff binder that the outage set makes go away) beats everything
    else, since it flips the trading direction; then A (outage-driven,
    dispatchable — the actionable long list); then C (no dispatchable relief
    exists, or the LP prices it at the penalty tier — ERCOT unlikely to run
    the outage); then B (binds anyway, outage or not); else unclassified.
    """
    if top_share is not None and top_share < 0:
        return "D", "top outage group UNLOADS the constraint (negative flow-delta share)"
    if pre_rate is not None and post_rate is not None and pre_rate > 0 and post_rate == 0:
        return "D", "bound pre-cutoff, stops binding post-cutoff with the outage set in"

    if top_share is not None and top_share >= TOP_SHARE_MIN and dispatch_ok is not False:
        return "A", "outage-driven (top group >= 25% of preflow) and dispatch screen passes"

    if penalty or dispatch_ok is False:
        reason = []
        if penalty:
            reason.append("penalty-tier LP lambda")
        if dispatch_ok is False:
            reason.append("no dispatchable relief pair")
        return "C", " + ".join(reason)

    if pre_rate is not None and post_rate is not None and post_rate > 0 and pre_rate >= 0.5 * post_rate:
        return "B", "binds pre-cutoff at >= half the post-cutoff rate (baseline, not outage-created)"

    return "U", "no class criterion matched (thin/ambiguous evidence)"
