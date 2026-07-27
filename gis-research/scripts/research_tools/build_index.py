"""Rebuild the research index: scan research/*/findings.json -> index.json + INDEX.md.

`index.json` is the programmatic search surface (jq / pandas / agent grep); INDEX.md is the
human table. Re-run after any project research completes or is refreshed.

Usage:
  uv run gis-research/scripts/research_tools/build_index.py
"""

from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
RESEARCH = BASE / "research"


def main() -> None:
    rows = []
    for fj in sorted(RESEARCH.glob("*/findings.json")):
        d = json.loads(fj.read_text())
        proj_dir = fj.parent
        tl = {}
        if (proj_dir / "timeline.json").exists():
            tl = json.loads((proj_dir / "timeline.json").read_text())
        cod_changes = max(len([r for r in tl.get("reported_cod_history", []) if r["value"]]) - 1, 0)
        rows.append({
            "inr": d.get("inr"),
            "project": d.get("project"),
            "dir": proj_dir.name,
            "researched_at": d.get("researched_at"),
            "verdict": d.get("real_project_verdict"),
            "construction": d.get("construction", {}).get("verdict"),
            "first_activity_seen": d.get("construction", {}).get("first_activity_seen"),
            "site_lat": d.get("site", {}).get("lat"),
            "site_lon": d.get("site", {}).get("lon"),
            "site_confidence": d.get("site", {}).get("confidence"),
            "cod_reported": d.get("cod_assessment", {}).get("reported"),
            "cod_independent": d.get("cod_assessment", {}).get("independent"),
            "drift_risk": d.get("cod_assessment", {}).get("drift_risk"),
            "queue_cod_changes": cod_changes,
            "owner_chain": " > ".join(e.get("entity", "") for e in d.get("llc_chain", [])),
            "land_tenure": (d["land_tenure"].get("status") if isinstance(d.get("land_tenure"), dict) else d.get("land_tenure")),
        })

    (RESEARCH / "index.json").write_text(json.dumps(rows, indent=1))

    md = ["# Research index", "",
          f"{len(rows)} project(s) researched. Programmatic search: `research/index.json`.", "",
          "| INR | Project | Verdict | Constr. | COD rep→ind | Drift | Queue COD Δ | Brief |",
          "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['inr']} | {r['project']} | {r['verdict']} | {r['construction']} "
                  f"| {r['cod_reported']} → {r['cod_independent']} | {r['drift_risk']} "
                  f"| {r['queue_cod_changes']} | [brief]({r['dir']}/brief.html) |")
    (RESEARCH / "INDEX.md").write_text("\n".join(md) + "\n")
    print(f"indexed {len(rows)} project(s) -> research/index.json + research/INDEX.md")


if __name__ == "__main__":
    main()
