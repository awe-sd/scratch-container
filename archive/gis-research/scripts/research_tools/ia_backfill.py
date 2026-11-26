"""Backfill IA PDFs for already-researched projects using puct.py — no LLM involved.

Walks research dirs that have a completed deep scan (findings.json), skips ones that
already hold a PUCT IA PDF, and for the rest runs the puct.py IA hunt on the project
name. Deterministic and throttled (shared 2s interval), so it is safe to run while
other work is going on. Misses land in a CSV for the deep re-run agents to chase with
the --signed date-window fallback.

Usage:
  uv run gis-research/scripts/research_tools/ia_backfill.py            # deep-scanned dirs
  uv run gis-research/scripts/research_tools/ia_backfill.py --all      # every researched dir
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import puct  # noqa: E402

BASE = Path(__file__).resolve().parents[2]  # gis-research/


def has_ia(d: Path) -> bool:
    if list((d / "sources").glob("*puct*.pdf")) if (d / "sources").exists() else []:
        return True
    for fname in ("findings.json",):
        f = d / fname
        if f.exists():
            try:
                cs = json.loads(f.read_text()).get("contractual_schedule") or {}
            except json.JSONDecodeError:
                continue
            if cs.get("source_docs") or any(x.get("artifact")
                                            for x in cs.get("documents", [])):
                return True
    return False


def project_name(d: Path) -> str:
    for fname in ("findings.json", "triage_findings.json"):
        f = d / fname
        if f.exists():
            try:
                n = json.loads(f.read_text()).get("project")
                if n:
                    return n
            except json.JSONDecodeError:
                pass
    # dir slug fallback: 26INR0269_moccasin-solar -> "moccasin solar"
    return d.name.split("_", 1)[-1].replace("-", " ")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all", action="store_true",
                    help="also sweep triage-only dirs (default: deep-scanned only)")
    ap.add_argument("--out", default=str(BASE / "research" / "_batches" / "ia_backfill.csv"))
    a = ap.parse_args()

    marker = "triage_findings.json" if a.all else "findings.json"
    dirs = sorted(p.parent for p in BASE.glob(f"research/*/{marker}"))
    rows = []
    n_had = n_hit = n_miss = 0
    for d in dirs:
        inr = d.name.split("_")[0]
        if has_ia(d):
            n_had += 1
            continue
        name = project_name(d)
        # strip suffixes that never appear in filing descriptions verbatim
        query = re.sub(r"\s*\(.*\)\s*$", "", name).strip()
        try:
            hits = puct.search(query)
            ia_style = [h for h in hits if "INTERCONNECTION" in h["style"].upper()]
            saved: list[Path] = []
            for h in ia_style[:2]:
                for f in puct.filings(h["control"], query):
                    if puct.IA_WORDS.search(f["description"]):
                        saved += puct.fetch_item(h["control"], f["item"],
                                                 d / "sources", desc=f["description"])
            status = "hit" if saved else "miss"
        except Exception as e:  # keep sweeping; record the error
            status, saved = f"error:{e.__class__.__name__}", []
        if saved:
            n_hit += 1
        else:
            n_miss += 1
        rows.append({"inr": inr, "project": name, "status": status,
                     "n_pdfs": len(saved)})
        print(f"{inr}  {status:14s}  {name[:60]}", flush=True)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["inr", "project", "status", "n_pdfs"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nswept {len(dirs)} dirs: {n_had} already had IA, {n_hit} backfilled, "
          f"{n_miss} still missing (see {out})")


if __name__ == "__main__":
    main()
