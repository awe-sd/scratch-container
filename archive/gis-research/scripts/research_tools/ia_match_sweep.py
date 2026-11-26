"""Fetch+verify IA PDFs for every triaged project with a systematic match candidate.

Covers the projects the original ia_backfill never attempted (it swept deep-scan dirs
only): queue says iaSigned, no verified PUCT PDF on disk yet, and at least one docket
description matches an exact name key. Runs puct.py's matcher per project (download +
INR-in-PDF / county+MW verification, unverified_* renaming). No LLM involved; throttled.

Writes research/_batches/ia_match_sweep.csv (inr, project, candidates, confirmed,
probable, unverified).

Usage:
  uv run gis-research/scripts/research_tools/ia_match_sweep.py [--limit N]
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import puct  # noqa: E402

BASE = Path(__file__).resolve().parents[2]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()

    import pandas as pd
    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    latest = df[df.fileDate == df.fileDate.max()]
    qrow = {r.INR: r for r in latest.itertuples()}
    idx = puct.load_index()

    todo = []
    for tf in sorted(glob.glob(str(BASE / "research" / "*" / "triage_findings.json"))):
        d = os.path.dirname(tf)
        inr = os.path.basename(d).split("_")[0]
        r = qrow.get(inr)
        if r is None or pd.isna(r.iaSigned):
            continue
        have = [p for p in glob.glob(d + "/sources/*puct*.pdf")
                if not os.path.basename(p).startswith("unverified_")]
        if have:
            continue
        keys = puct.match_keys(inr, [])
        if any(any(k.lower() in f["description"].lower() for k in keys) for f in idx):
            todo.append((inr, d, str(r.projectName)))
    if a.limit:
        todo = todo[:a.limit]
    print(f"{len(todo)} projects to sweep", flush=True)

    rows = []
    for i, (inr, d, name) in enumerate(todo):
        src = Path(d) / "sources"
        before = set(src.glob("*.pdf")) if src.exists() else set()
        try:
            puct.cmd_match(inr, src, [])
        except Exception as e:
            rows.append({"inr": inr, "project": name, "candidates": "error",
                         "confirmed": 0, "probable": 0, "unverified": 0,
                         "note": f"{e.__class__.__name__}"})
            continue
        new = [p for p in src.glob("*.pdf") if p not in before]
        unv = sum(1 for p in new if p.name.startswith("unverified_"))
        ok = len(new) - unv
        rows.append({"inr": inr, "project": name, "candidates": len(new),
                     "confirmed": ok, "probable": 0, "unverified": unv, "note": ""})
        print(f"[{i+1}/{len(todo)}] {inr} {name[:40]}: {ok} verified, {unv} unverified",
              flush=True)

    out = BASE / "research" / "_batches" / "ia_match_sweep.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["inr", "project", "candidates", "confirmed",
                                           "probable", "unverified", "note"])
        w.writeheader()
        w.writerows(rows)
    got = sum(1 for r in rows if r["confirmed"])
    print(f"\nDONE: {len(rows)} swept, {got} projects gained a verified IA PDF -> {out}")


if __name__ == "__main__":
    main()
