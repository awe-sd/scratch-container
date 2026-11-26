"""Find and render map/exhibit pages inside agreement PDFs — never guess past a map.

Agreement documents on disk (IA attachments, Ch.313/JETI exhibits, permit maps) very
often contain the project's location as a MAP or legal description the text layer
mangles. Twice (Indigo 21INR0031 Attachment C-3, Adamstown 21INR0210 Exhibit B) agents
guessed a site while the answer sat in sources/. This tool makes checking systematic:

  exhibit.py list <pdf>            # pages whose text smells like an exhibit/map/legal
  exhibit.py render <pdf> -p 42,141 [--dpi 170]
                                   # -> <pdf_dir>/<pdfstem>_pNN.png  (Read the PNGs!)
  exhibit.py scan <project_dir>    # run list over every sources/*.pdf, print hits
  exhibit.py sheet <pdf> [--per 4] [--dpi 110]
                                   # token-efficient full read of a big/scanned PDF:
                                   # tiles N pages per PNG + writes <stem>_sheet_index.md
                                   # (tile->pages map, per-page headline, exhibit flags).
                                   # Read the index first, then ONLY the tiles you need.

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


def cmd_sheet(pdf: Path, per: int, dpi: int) -> None:
    """Tile pages into composite PNGs (2 cols) + write an .md index for cheap Reads."""
    import fitz
    doc = fitz.open(pdf)
    hits = {n for n, _ in pages_of_interest(pdf)}
    import io
    from PIL import Image
    cols = 2
    rows = max(1, (per + cols - 1) // cols)
    lines = [f"# Sheet index — {pdf.name} ({len(doc)} pages, {per}/tile)", ""]
    tile_no = 0
    for start in range(0, len(doc), per):
        tile_no += 1
        pages = list(range(start, min(start + per, len(doc))))
        pixes = [doc[p].get_pixmap(dpi=dpi) for p in pages]
        w, h = max(px.width for px in pixes), max(px.height for px in pixes)
        canvas = Image.new("RGB", (w * cols, h * rows), "white")
        for i, px in enumerate(pixes):
            img = Image.open(io.BytesIO(px.tobytes("png")))
            canvas.paste(img, ((i % cols) * w, (i // cols) * h))
        out = pdf.parent / f"{pdf.stem[:52]}_sheet{tile_no:02d}.png"
        canvas.save(out, optimize=True)
        lines.append(f"## {out.name} — pages {pages[0]+1}-{pages[-1]+1}")
        for i, p in enumerate(pages):
            t = " ".join((doc[p].get_text() or "").split())[:70]
            flag = "  **<-- exhibit/map candidate**" if (p + 1) in hits else ""
            pos = f"({'top' if i // cols == 0 else 'row ' + str(i // cols + 1)}-{'left' if i % cols == 0 else 'right'})"
            lines.append(f"- p{p+1} {pos}: {t or '(no text layer — scanned page)'}{flag}")
        lines.append("")
    idx = pdf.parent / f"{pdf.stem[:52]}_sheet_index.md"
    idx.write_text("\n".join(lines))
    print(f"{tile_no} sheet(s) + index: {idx.name}")


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
    p4 = sub.add_parser("sheet");  p4.add_argument("pdf", type=Path)
    p4.add_argument("--per", type=int, default=4, help="pages per composite image")
    p4.add_argument("--dpi", type=int, default=110)
    a = ap.parse_args()
    if a.cmd == "list":
        cmd_list(a.pdf)
    elif a.cmd == "render":
        cmd_render(a.pdf, [int(x) for x in a.pages.split(",")], a.dpi)
    elif a.cmd == "scan":
        cmd_scan(a.project_dir)
    elif a.cmd == "sheet":
        cmd_sheet(a.pdf, a.per, a.dpi)


if __name__ == "__main__":
    sys.exit(main())
