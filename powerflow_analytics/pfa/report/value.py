"""Console text for `pfa value`."""
from __future__ import annotations

import json

import pandas as pd


def fact_sheet(result: dict) -> str:
    lines = [f"constraint {result['constraint']} (study {result['study_id']})",
             f"  binding cases: {result['n_binding_cases']} / {result['n_total_cases']} rows flagged "
             f"in OUTCTGVIOL2 ({result['n_total_study_runs']} total study runs)",
             "  lambda ($/MWh) over binding runs:"]
    lines += [f"    {k}: {v}" for k, v in result["lambda_stats"].items()]
    lines.append(f"  top marginal units ({len(result['marginal_units'])}):")
    lines += [f"    {json.dumps(u, default=str)}" for u in result["marginal_units"]]
    return "\n".join(lines)


def monthly_mark(key: str, window: tuple[str, str], stats, table: pd.DataFrame) -> str:
    return "\n".join([
        f"{key} — window {window[0]}..{window[1]} ({stats.n_window_runs} runs in window)",
        f"P(bind | sim hour): {({h: round(p, 2) for h, p in stats.p_bind.items()})}",
        "lambda ($/MWh):",
        stats.lam.round(1).to_string(),
        "",
        table[["lam_col", "sf", "outage_onpeak_days", "rent_per_mw_month", "dollars_per_mwh"]].to_string(index=False),
    ])


def headroom_profile(config_id: int, profile: pd.DataFrame) -> str:
    return f"fast-scan config {config_id} headroom profile:\n{profile.round(1).to_string(index=False)}"
