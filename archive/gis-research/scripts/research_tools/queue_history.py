"""Per-project milestone timeline from the full GIS monthly-report history (local parquet).

Every monthly ERCOT GIS report since 2014 is in the parquet, so a project's complete
milestone/COD-drift history is derivable locally — no web research needed. Writes
`timeline.json` + terse `timeline.md` into the project research dir.

Usage:
  uv run gis-research/scripts/research_tools/queue_history.py 23INR0086 \
      [--out-dir gis-research/research/23INR0086_hanson-solar]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]
PARQUET = BASE / "data" / "ercot_generation_interconnect.parquet"

MILESTONES = [
    ("screeningStudyStarted", "Screening started"),
    ("screeningStudyComplete", "Screening complete"),
    ("fisRequested", "FIS requested"),
    ("fisApproved", "FIS approved"),
    ("iaSigned", "IA signed"),
    ("meetsSection691", "Meets 6.9(1)"),
    ("meetsAllSection69", "Meets all 6.9"),
    ("constructionStart", "Construction start (reported)"),
    ("constructionEnd", "Construction end (reported)"),
    ("approvedForEnergization_", "Approved for energization"),   # col name fixed below
    ("approvedForSynchronization", "Approved for synchronization"),
    ("approvedForCommercialOperation", "Commercial operation approved"),
]


def track_changes(hist: pd.DataFrame, col: str) -> list[dict]:
    """Value history of `col` across monthly snapshots: [{value, from, to}] runs."""
    runs: list[dict] = []
    for _, row in hist.iterrows():
        v = row[col]
        v = None if pd.isna(v) else str(v)[:10] if "date" in col.lower() or col == "projectCod" else v
        fd = str(row["fileDate"])[:10]
        if runs and runs[-1]["value"] == v:
            runs[-1]["to"] = fd
        else:
            runs.append({"value": v, "from": fd, "to": fd})
    return runs


def build(inr: str, out_dir: Path) -> None:
    df = pd.read_parquet(PARQUET)
    hist = df[df["INR"] == inr].sort_values("fileDate").copy()
    if hist.empty:
        raise SystemExit(f"INR {inr!r} not found in parquet")

    first_seen = str(hist["fileDate"].min())[:10]
    last_seen = str(hist["fileDate"].max())[:10]

    # milestone achieved date = value in the LATEST snapshot; also record when it first
    # appeared in the monthly reports (report lag / retro-dating is itself a signal).
    latest = hist.iloc[-1]
    milestones = []
    for col, label in MILESTONES:
        col = "ApprovedForEnergization" if col == "approvedForEnergization_" else col
        val = latest.get(col)
        achieved = None if pd.isna(val) else str(val)[:10]
        first_reported = None
        if achieved is not None:
            nonnull = hist[hist[col].notna()]
            first_reported = str(nonnull["fileDate"].iloc[0])[:10] if len(nonnull) else None
        milestones.append({"milestone": label, "achieved": achieved,
                           "first_in_report": first_reported})

    cod_runs = track_changes(hist, "projectCod")
    cap_runs = track_changes(hist, "capacityMw")
    phase_runs = track_changes(hist, "ginrStudyPhase")

    out = {
        "inr": inr,
        "project": latest.get("projectName"),
        "first_seen_in_reports": first_seen,
        "last_seen_in_reports": last_seen,
        "snapshots": len(hist),
        "milestones": milestones,
        "reported_cod_history": cod_runs,
        "capacity_history": cap_runs,
        "study_phase_history": phase_runs,
        "financial_security_latest": latest.get("financialSecurityAndNoticeToProceedProvided"),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "timeline.json").write_text(json.dumps(out, indent=1, default=str))

    md = [f"# Queue timeline — {out['project']} ({inr})",
          f"In reports {first_seen} → {last_seen} ({len(hist)} monthly snapshots)", ""]
    md.append("| Milestone | Achieved | First in report |")
    md.append("|---|---|---|")
    for m in milestones:
        md.append(f"| {m['milestone']} | {m['achieved'] or '—'} | {m['first_in_report'] or '—'} |")
    md += ["", "## Reported COD drift", "", "| COD | Held from | Until |", "|---|---|---|"]
    for r in cod_runs:
        md.append(f"| {r['value'] or '—'} | {r['from']} | {r['to']} |")
    if len(cap_runs) > 1:
        md += ["", "## Capacity changes", "", "| MW | From | Until |", "|---|---|---|"]
        md += [f"| {r['value']} | {r['from']} | {r['to']} |" for r in cap_runs]
    (out_dir / "timeline.md").write_text("\n".join(md) + "\n")
    drift = len([r for r in cod_runs if r["value"]]) - 1
    print(f"wrote {out_dir}/timeline.json + timeline.md — {len(hist)} snapshots, "
          f"{max(drift,0)} reported-COD change(s)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("inr")
    ap.add_argument("--out-dir", type=Path, default=None,
                    help="default: gis-research/research/<match on INR>*")
    a = ap.parse_args()
    out_dir = a.out_dir
    if out_dir is None:
        hits = sorted((BASE / "research").glob(f"{a.inr}_*"))
        if not hits:
            raise SystemExit(f"no research dir matching {a.inr}_* — pass --out-dir")
        out_dir = hits[0]
    build(a.inr, out_dir)


if __name__ == "__main__":
    main()
