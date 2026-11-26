"""Dump per-slide text from a .pptx by unzipping and joining <a:t> runs in
document order. No python-pptx dependency needed.

Usage: uv run python scripts/extract_pptx_text.py <path/to/deck.pptx>
Prints "=== slideN.xml ===" then each text run on its own line, in slide
order (slide1, slide2, ... slide10, not lexicographic slide10 < slide2).
"""
import re
import sys
import zipfile
from pathlib import Path


def slide_sort_key(name: str) -> int:
    m = re.search(r"slide(\d+)\.xml$", name)
    return int(m.group(1)) if m else 10**9


def extract(pptx_path: str) -> None:
    with zipfile.ZipFile(pptx_path) as z:
        slide_names = [
            n for n in z.namelist()
            if re.match(r"ppt/slides/slide\d+\.xml$", n)
        ]
        slide_names.sort(key=slide_sort_key)
        for name in slide_names:
            xml = z.read(name).decode("utf-8", errors="replace")
            texts = re.findall(r"<a:t>(.*?)</a:t>", xml, re.DOTALL)
            print(f"=== {name} ===")
            for t in texts:
                t = t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                if t.strip():
                    print(t)
            print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: extract_pptx_text.py <path/to/deck.pptx>", file=sys.stderr)
        sys.exit(1)
    extract(sys.argv[1])
