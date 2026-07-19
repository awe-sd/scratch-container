"""Build the deep-scan queue from ALL triage results on disk, anytime.

Scans research/*/triage_findings.json for deep_scan_recommended=true, drops projects
that already have a deep scan (findings.json present), sorts by capacity (largest first),
and writes research/_batches/deep_queue_all.txt — the file run_batch.py --mode deep
--inrs-file consumes. Safe to re-run while triage batches are still going.

Usage:
  uv run gis-research/scripts/research_tools/make_deep_queue.py
  uv run gis-research/scripts/research_tools/make_deep_queue.py --min-mw 200
  # then, after pruning lines you don't want:
  uv run gis-research/scripts/research_tools/run_batch.py --name deep-pass-1 \
      --mode deep --inrs-file gis-research/research/_batches/deep_queue_all.txt --concurrency 3
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]  # gis-research/


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-mw", type=float, default=None)
    ap.add_argument("--out", default=str(BASE / "research" / "_batches" / "deep_queue_all.txt"))
    a = ap.parse_args()

    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    latest = df[df.fileDate == df.fileDate.max()]
    mw = dict(zip(latest.INR, latest.capacityMw))
    cod = dict(zip(latest.INR, latest.projectCod.astype(str).str[:10]))

    rows, done_deep, not_flagged = [], 0, 0
    for tf in sorted(BASE.glob("research/*/triage_findings.json")):
        try:
            t = json.loads(tf.read_text())
        except json.JSONDecodeError:
            continue
        if not t.get("deep_scan_recommended"):
            not_flagged += 1
            continue
        if (tf.parent / "findings.json").exists():
            done_deep += 1
            continue
        inr = t.get("inr") or tf.parent.name.split("_")[0]
        if a.min_mw and mw.get(inr, 0) < a.min_mw:
            continue
        focus = "; ".join(t.get("deep_scan_focus", [])[:1])
        rows.append((mw.get(inr, 0), inr, t.get("project", ""), cod.get(inr, "?"), focus))

    rows.sort(reverse=True)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# deep-scan queue (all triaged dirs) — prune freely, then:",
             "#   uv run gis-research/scripts/research_tools/run_batch.py --name deep-pass-1 "
             f"--mode deep --inrs-file {out} --concurrency 3"]
    lines += [f"{inr}  # {m:7.1f} MW  COD {c}  {name} — {focus}"
              for m, inr, name, c, focus in rows]
    out.write_text("\n".join(lines) + "\n")
    print(f"{len(rows)} queued ({not_flagged} not flagged, {done_deep} already deep-scanned)")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
