"""Definitive docket-item -> INR join table: download every IA PDF once, extract INRs.

ERCOT SGIAs reference the GINR number ("23INR0086") in the agreement text. Harvesting
those strings from every PDF in the central docket turns IA lookup into a LOCAL JOIN —
no name matching, no dates, no fuzz. Scanned image-only PDFs yield no text (text_ok
false) and stay manual; everything else is resolved permanently.

Writes:
  data/reference/puct_docket_pdfs/<control>_<item>_<docid>.pdf   (kept for reuse)
  research/_reference/puct_inr_join.json  {item: {filed, description, inrs, pdfs, text_ok}}

Resume-safe: items already in the join table are skipped; partial table is flushed
every 20 items. Throttled via puct.py's shared 2s lock.

Usage:
  uv run gis-research/scripts/research_tools/inr_harvest.py [--min-year 2018] [--limit N]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import puct  # noqa: E402

BASE = Path(__file__).resolve().parents[2]
PDF_DIR = BASE / "data" / "reference" / "puct_docket_pdfs"
JOIN_FILE = BASE / "research" / "_reference" / "puct_inr_join.json"
INR_RE = re.compile(r"\b\d{2}INR\d{4}\b", re.I)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-year", type=int, default=2018,
                    help="skip filings older than this (queue-relevant IAs)")
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    idx = puct.load_index()
    join = json.loads(JOIN_FILE.read_text()) if JOIN_FILE.exists() else {}

    todo = [f for f in idx
            if int(f["filed"].split("/")[-1]) >= a.min_year and f["item"] not in join]
    if a.limit:
        todo = todo[:a.limit]
    print(f"{len(idx)} filings in index; {len(todo)} to harvest "
          f"(>= {a.min_year}, {len(join)} already done)", flush=True)

    for i, f in enumerate(todo):
        item = f["item"]
        entry = {"filed": f["filed"], "description": f["description"][:160],
                 "inrs": [], "pdfs": [], "text_ok": False}
        try:
            for d in puct.documents(puct.IA_DOCKET, item):
                if d["format"].upper() != "PDF":
                    continue
                dest = PDF_DIR / f"{d['id']}.pdf"
                if not dest.exists():
                    r = puct.get(d["url"])
                    dest.write_bytes(r.content)
                txt = puct.pdf_text(dest)
                if txt.strip():
                    entry["text_ok"] = True
                entry["inrs"] = sorted(set(entry["inrs"])
                                       | {m.upper() for m in INR_RE.findall(txt)})
                entry["pdfs"].append(dest.name)
        except Exception as e:  # record and keep sweeping
            entry["error"] = f"{e.__class__.__name__}: {str(e)[:120]}"
        join[item] = entry
        if (i + 1) % 20 == 0 or i + 1 == len(todo):
            JOIN_FILE.write_text(json.dumps(join))
            with_inr = sum(1 for v in join.values() if v.get("inrs"))
            print(f"{i+1}/{len(todo)} harvested; items with INRs: {with_inr}", flush=True)

    with_inr = sum(1 for v in join.values() if v.get("inrs"))
    no_text = sum(1 for v in join.values() if not v.get("text_ok") and not v.get("error"))
    errs = sum(1 for v in join.values() if v.get("error"))
    print(f"\nDONE: {len(join)} items in table; {with_inr} with INRs, "
          f"{no_text} image-only (manual), {errs} errors")
    print(f"join table: {JOIN_FILE}")


if __name__ == "__main__":
    main()
