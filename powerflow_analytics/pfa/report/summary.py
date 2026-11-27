"""Console text for the study summary."""
from __future__ import annotations

from pfa.analysis.summary import StudySummary

COLS = ["CONSTRAINT", "FROMNAME", "TONAME", "TOTAL_RENT", "RENT_PRE", "RENT_POST",
        "POST_RENT_SHARE", "MEAN_SHADOW", "MAX_SHADOW", "N_RUNS_BINDING",
        "DRIVER_CLASS", "DRIVER_TICKET", "DRIVER_TICKET_STATUS"]


def console(s: StudySummary, study: int, cutoff: str, top: int, out_dir) -> str:
    ranked, base = s.ranked, s.base
    lines = [f"study {study}: {len(ranked):,} flagged constraints, {(ranked['N_RUNS_BINDING'] > 0).sum()} ever binding, "
             f"{(ranked['TOTAL_RENT'] > 0).sum()} with LP rent; cutoff {cutoff}",
             ranked[ranked["TOTAL_RENT"] > 0].head(top)[COLS].round(1).to_string(index=False),
             f"\nbase-case binders (MARGCOSTMVA): {len(base)}"]
    if len(base):
        lines.append(base.head(10).to_string(index=False))
    lines.append(f"\noutputs -> {out_dir}")
    return "\n".join(lines)
