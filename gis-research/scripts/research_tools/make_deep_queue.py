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
for the deep-scan relaunch decision. ALSO writes research/_reference/triage_recheck_v2.txt
— every "ambiguous" INR plus any "paper_kill" INR whose triage_findings.json (v1) has
deep_scan_recommended=true (a v1/v2 conflict the user routed to a triage-v2 re-check),
one INR per line.

Recheck promotion/demotion wiring: for every factsheet, ALSO reads that project's
triage_findings.json (v2 schema) if present. gate said "ambiguous" but the (post-recheck)
triage verdict is "deep_candidate" -> PROMOTED into deep_queue_v2.csv with
promoted_by_triage=True (priority computed the same way gate() does, from this factsheet's
own MW/months_to_cod). gate said "deep_candidate" but the triage verdict is
"paper_dismissed" -> DEMOTED: excluded from deep_queue_v2.csv entirely. Promotion/demotion
counts are printed.
  uv run gis-research/scripts/research_tools/make_deep_queue.py --v2
"""

from __future__ import annotations

import argparse
import csv as csvmod
import datetime as dt
import json
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]  # gis-research/
DEEP_SCAN_COST = 4.64  # $/scan, Sonnet deep mean (see gis-research/CLAUDE.md)
RECHECK_COST = 0.35  # $/project, triage-v2 re-check (user-set 2026-07-20)


def _months_to_cod(queue_cod: str | None, generated: str) -> float | None:
    """Same formula factsheet.py used to derive gate.priority, anchored on the
    factsheet's own 'generated' date so months_to_cod stays consistent with the
    persisted priority number even if this queue is rebuilt on a later date."""
    if not queue_cod:
        return None
    cy, cm, cd = (int(x) for x in queue_cod.split("-"))
    gy, gm, gd = (int(x) for x in generated.split("-"))
    return round((dt.date(cy, cm, cd) - dt.date(gy, gm, gd)).days / 30.4, 2)


def build_v2(csv_path: Path, recheck_path: Path) -> None:
    rows = []
    ambiguous = []       # (inr, project, mw)
    conflicts = []       # (inr, project, mw) -- paper_kill but v1 triage flagged deep_scan
    n_total = n_paper_kill = n_promoted = n_demoted = 0
    for fp in sorted(BASE.glob("research/*/factsheet.json")):
        if fp.parent.name.startswith("_"):
            continue
        n_total += 1
        try:
            f = json.loads(fp.read_text())
        except json.JSONDecodeError:
            print(f"WARNING: corrupt JSON, skipping {fp}", file=sys.stderr)
            continue
        g = f.get("gate") or {}
        decision = g.get("decision")
        inr = f.get("inr")
        project = f.get("project")
        mw = f.get("capacity_mw") or 0.0
        months_to_cod = _months_to_cod(f.get("queue_cod"), f.get("generated"))

        # Read this project's triage_findings.json ONCE regardless of which gate bucket
        # it fell into -- used below both for the v1 paper_kill-conflict check (the
        # deep_scan_recommended bool) and the v2 recheck promotion/demotion check (the
        # verdict enum, written by a post-recheck triage-v2 run).
        t: dict = {}
        tf = fp.parent / "triage_findings.json"
        if tf.exists():
            try:
                t = json.loads(tf.read_text())
            except json.JSONDecodeError:
                print(f"WARNING: corrupt JSON, skipping triage_findings for "
                      f"{inr or fp.parent.name}: {tf}", file=sys.stderr)
        v2_verdict = t.get("verdict")

        if decision == "deep_candidate":
            if v2_verdict == "paper_dismissed":
                # triage-v2 recheck demoted this factsheet deep_candidate -- excluded
                n_demoted += 1
                continue
            already = (fp.parent / "findings.json").exists()
            rows.append({
                "inr": inr,
                "project": project,
                "mw": f.get("capacity_mw"),
                "months_to_cod": months_to_cod,
                "paper_score": f.get("paper_score"),
                "decision": decision,
                "priority": g.get("priority"),
                "already_deep_scanned": already,
                "promoted_by_triage": False,
            })
        elif decision == "ambiguous":
            if v2_verdict == "deep_candidate":
                # post-recheck promotion -- priority computed the same way gate() does
                n_promoted += 1
                pri = round(mw * (1.0 / max(months_to_cod if months_to_cod is not None
                                             else 24.0, 1.0)), 2)
                already = (fp.parent / "findings.json").exists()
                rows.append({
                    "inr": inr,
                    "project": project,
                    "mw": f.get("capacity_mw"),
                    "months_to_cod": months_to_cod,
                    "paper_score": f.get("paper_score"),
                    "decision": "deep_candidate",
                    "priority": pri,
                    "already_deep_scanned": already,
                    "promoted_by_triage": True,
                })
            else:
                ambiguous.append((inr, project, mw))
        elif decision == "paper_kill":
            n_paper_kill += 1
            if t.get("deep_scan_recommended"):
                conflicts.append((inr, project, mw))
        else:
            print(f"WARNING: unknown/missing gate.decision {decision!r} for "
                  f"{inr or fp.parent.name} ({fp}), skipping", file=sys.stderr)

    rows.sort(key=lambda r: (r["priority"] if r["priority"] is not None else -1), reverse=True)
    for i, r in enumerate(rows, start=1):
        r["rank"] = i

    cols = ["rank", "inr", "project", "mw", "months_to_cod", "paper_score",
            "decision", "priority", "already_deep_scanned", "promoted_by_triage"]
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csvmod.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    not_scanned = [r for r in rows if not r["already_deep_scanned"]]
    total_mw_not_scanned = sum(r["mw"] or 0 for r in not_scanned)
    print(f"{n_total} factsheets scanned  ->  {len(rows)} deep_candidate  "
          f"({len(rows) - len(not_scanned)} already deep-scanned, {len(not_scanned)} not)")
    print(f"triage-v2 recheck: {n_promoted} promoted (ambiguous -> deep_candidate), "
          f"{n_demoted} demoted (deep_candidate -> excluded)")
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
    print(f"wrote {csv_path}")

    # --- triage_recheck_v2.txt: ambiguous verdicts + v1/v2 paper_kill conflicts ---
    ambiguous.sort(key=lambda t: t[0])
    conflicts.sort(key=lambda t: t[0])
    recheck_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# triage-recheck queue v2 -- ambiguous gate() verdicts + v1/v2 paper_kill "
             "conflicts (v1 triage flagged deep_scan_recommended, v2 gate says paper_kill)",
             "#   uv run gis-research/scripts/research_tools/run_batch.py --name recheck-1 "
             f"--mode triage --inrs-file {recheck_path} --concurrency 3"]
    lines += [f"{inr}  # ambiguous  {mw:7.1f} MW  {project}"
              for inr, project, mw in ambiguous]
    lines += [f"{inr}  # paper_kill v1-conflict (v1 deep_scan_recommended=true)  "
              f"{mw:7.1f} MW  {project}"
              for inr, project, mw in conflicts]
    recheck_path.write_text("\n".join(lines) + "\n")

    n_recheck = len(ambiguous) + len(conflicts)
    print(f"\ntriage recheck: {len(ambiguous)} ambiguous + {len(conflicts)} paper_kill "
          f"v1-conflicts (of {n_paper_kill} paper_kill total) = {n_recheck} to re-check")
    print(f"estimated recheck spend: {n_recheck} x ${RECHECK_COST} = "
          f"${n_recheck * RECHECK_COST:.2f}")
    print(f"wrote {recheck_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-mw", type=float, default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--recheck-out", default=None,
                    help="--v2 only: override the triage_recheck_v2.txt path")
    ap.add_argument("--v2", action="store_true",
                    help="pipeline-v2 mode: rank factsheet.json deep_candidates by "
                         "gate.priority -> research/_reference/deep_queue_v2.csv "
                         "(+ triage_recheck_v2.txt for ambiguous/conflict INRs)")
    a = ap.parse_args()

    if a.v2:
        out = Path(a.out) if a.out else BASE / "research" / "_reference" / "deep_queue_v2.csv"
        recheck_out = (Path(a.recheck_out) if a.recheck_out
                       else BASE / "research" / "_reference" / "triage_recheck_v2.txt")
        build_v2(out, recheck_out)
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
