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

--v2 (pipeline v2, additive — legacy behavior above is unchanged without the flag):
Reads every research/<INR>_*/factsheet.json (written by factsheet.py --all), keeps
gate.decision == "deep_candidate", sorts by gate.priority desc, and writes
research/_reference/deep_queue_v2.csv — the ranked, gate-filtered user-review artifact
for the deep-scan relaunch decision.
  uv run gis-research/scripts/research_tools/make_deep_queue.py --v2
"""

from __future__ import annotations

import argparse
import csv as csvmod
import datetime as dt
import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]  # gis-research/
DEEP_SCAN_COST = 4.64  # $/scan, Sonnet deep mean (see gis-research/CLAUDE.md)


def _months_to_cod(queue_cod: str | None, generated: str) -> float | None:
    """Same formula factsheet.py used to derive gate.priority, anchored on the
    factsheet's own 'generated' date so months_to_cod stays consistent with the
    persisted priority number even if this queue is rebuilt on a later date."""
    if not queue_cod:
        return None
    cy, cm, cd = (int(x) for x in queue_cod.split("-"))
    gy, gm, gd = (int(x) for x in generated.split("-"))
    return round((dt.date(cy, cm, cd) - dt.date(gy, gm, gd)).days / 30.4, 2)


def build_v2(out_path: Path) -> None:
    rows = []
    n_total = 0
    for fp in sorted(BASE.glob("research/*/factsheet.json")):
        if fp.parent.name.startswith("_"):
            continue
        n_total += 1
        try:
            f = json.loads(fp.read_text())
        except json.JSONDecodeError:
            continue
        g = f.get("gate") or {}
        if g.get("decision") != "deep_candidate":
            continue
        already = (fp.parent / "findings.json").exists()
        rows.append({
            "inr": f.get("inr"),
            "project": f.get("project"),
            "mw": f.get("capacity_mw"),
            "months_to_cod": _months_to_cod(f.get("queue_cod"), f.get("generated")),
            "paper_score": f.get("paper_score"),
            "decision": g.get("decision"),
            "priority": g.get("priority"),
            "already_deep_scanned": already,
        })

    rows.sort(key=lambda r: (r["priority"] if r["priority"] is not None else -1), reverse=True)
    for i, r in enumerate(rows, start=1):
        r["rank"] = i

    cols = ["rank", "inr", "project", "mw", "months_to_cod", "paper_score",
            "decision", "priority", "already_deep_scanned"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csvmod.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    not_scanned = [r for r in rows if not r["already_deep_scanned"]]
    total_mw_not_scanned = sum(r["mw"] or 0 for r in not_scanned)
    print(f"{n_total} factsheets scanned  ->  {len(rows)} deep_candidate  "
          f"({len(rows) - len(not_scanned)} already deep-scanned, {len(not_scanned)} not)")
    print(f"top 15 by priority:")
    print(f"{'rank':>4}  {'inr':10}  {'project':32}  {'mw':>8}  {'mo_cod':>7}  "
          f"{'score':>5}  {'priority':>9}  scanned")
    for r in rows[:15]:
        print(f"{r['rank']:>4}  {r['inr']:10}  {(r['project'] or '')[:32]:32}  "
              f"{(r['mw'] or 0):>8.1f}  {(r['months_to_cod'] if r['months_to_cod'] is not None else float('nan')):>7.1f}  "
              f"{r['paper_score']:>5}  {r['priority']:>9.2f}  {r['already_deep_scanned']}")
    print(f"totals: {len(rows)} deep_candidate, {total_mw_not_scanned:.1f} MW not yet scanned")
    print(f"estimated spend to clear not-yet-scanned rows: "
          f"{len(not_scanned)} x ${DEEP_SCAN_COST} = ${len(not_scanned) * DEEP_SCAN_COST:.2f}")
    print(f"wrote {out_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-mw", type=float, default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--v2", action="store_true",
                    help="pipeline-v2 mode: rank factsheet.json deep_candidates by "
                         "gate.priority -> research/_reference/deep_queue_v2.csv")
    a = ap.parse_args()

    if a.v2:
        out = Path(a.out) if a.out else BASE / "research" / "_reference" / "deep_queue_v2.csv"
        build_v2(out)
        return

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
    out = Path(a.out) if a.out else BASE / "research" / "_batches" / "deep_queue_all.txt"
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
