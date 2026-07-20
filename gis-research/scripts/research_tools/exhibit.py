"""Find and render map/exhibit pages inside agreement PDFs — never guess past a map.

Agreement documents on disk (IA attachments, Ch.313/JETI exhibits, permit maps) very
often contain the project's location as a MAP or legal description the text layer
mangles. Twice (Indigo 21INR0031 Attachment C-3, Adamstown 21INR0210 Exhibit B) agents
guessed a site while the answer sat in sources/. This tool makes checking systematic:

  exhibit.py list <pdf>            # pages whose text smells like an exhibit/map/legal
  exhibit.py render <pdf> -p 42,141 [--dpi 170]
                                   # -> <pdf_dir>/<pdfstem>_pNN.png  (Read the PNGs!)
  exhibit.py scan <project_dir>    # run list over every sources/*.pdf, print hits

Agent usage: run `scan` in D1 for every agreement PDF in sources/, `render` the hits,
Read each PNG, and record used pages in findings.json `site.map_artifacts`.
Deterministic keyword matching only; rendering is local (pymupdf), no network.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

KEYS = re.compile(
    r"exhibit|attachment [a-z]-?\d|overview map|survey map|site plan|boundary|"
    r"metes and bounds|legal description|reinvestment zone|improvement.{0,20}map|"
    r"parcel map|location map|one-line", re.I)
STRONG = re.compile(r"map|boundar|survey|site plan|metes|legal description", re.I)


def pages_of_interest(pdf: Path) -> list[tuple[int, str]]:
    import fitz
    doc = fitz.open(pdf)
    out = []
    for n in range(len(doc)):
        t = doc[n].get_text() or ""
        if KEYS.search(t) and STRONG.search(t):
            head = " ".join(t.split())[:90]
            out.append((n + 1, head))
        elif len(t.strip()) < 40 and doc[n].get_images():
            out.append((n + 1, "(image-only page — likely a full-page map/scan)"))
    return out


def cmd_list(pdf: Path) -> None:
    hits = pages_of_interest(pdf)
    print(f"{pdf.name}: {len(hits)} candidate page(s)")
    for n, head in hits:
        print(f"  p{n}: {head}")
    if not hits:
        print("  (none — no exhibit/map keywords and no image-only pages)")


def cmd_render(pdf: Path, pages: list[int], dpi: int) -> None:
    import fitz
    doc = fitz.open(pdf)
    for p in pages:
        if not 1 <= p <= len(doc):
            print(f"  p{p}: out of range (1-{len(doc)})")
            continue
        out = pdf.parent / f"{pdf.stem[:60]}_p{p}.png"
        doc[p - 1].get_pixmap(dpi=dpi).save(out)
        print(f"rendered: {out} ({out.stat().st_size // 1024} KB)")


def cmd_scan(proj_dir: Path) -> None:
    pdfs = sorted((proj_dir / "sources").glob("*.pdf"))
    if not pdfs:
        print(f"no PDFs under {proj_dir}/sources")
        return
    for pdf in pdfs:
        try:
            cmd_list(pdf)
        except Exception as e:
            print(f"{pdf.name}: unreadable ({e.__class__.__name__})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("list");   p1.add_argument("pdf", type=Path)
    p2 = sub.add_parser("render"); p2.add_argument("pdf", type=Path)
    p2.add_argument("-p", "--pages", required=True,
                    help="comma-separated page numbers (1-based)")
    p2.add_argument("--dpi", type=int, default=170)
    p3 = sub.add_parser("scan");   p3.add_argument("project_dir", type=Path)
    a = ap.parse_args()
    if a.cmd == "list":
        cmd_list(a.pdf)
    elif a.cmd == "render":
        cmd_render(a.pdf, [int(x) for x in a.pages.split(",")], a.dpi)
    elif a.cmd == "scan":
        cmd_scan(a.project_dir)


if __name__ == "__main__":
    sys.exit(main())
