"""County commissioners-court minutes — harvester + keyword index + INR resolver.

Why this exists: commissioners-court minutes are the PRIMARY record of county tax
abatements, reinvestment-zone designations, and road/development agreements — the
source documents that the Comptroller's Ch.312 registry only summarizes (and which
some counties never report: Somervell, Matagorda, Crockett had 0 registry rows).
The census at data/reference/county_minutes_census.json (2026-07-21, all 195
active-queue counties, probe-verified) found 152 counties posting minutes online,
dominated by a few template families: ezTask/CIRA (58), CivicPlus (24),
CivicClerk (14), Legistar (6).

Pattern follows inr_harvest.py: download once into data/reference/county_minutes/
(gitignored), extract text, keyword-scan into a permanent join table, then resolve
per-INR. Meetings happen 1-4x/month, so re-harvest is a small incremental pull.

Platform handlers implemented: generic-pdf (ezTask/CIRA, Revize, custom PDF pages —
anything whose minutes page is "a page with PDF links") and CivicPlus AgendaCenter.
CivicClerk (JSON API) and Legistar (REST API) are phase-2 — resolve prints an
explicit not-harvested note for those counties rather than a false negative.

Agent usage (run from repo root with `uv run`):
  minutes.py harvest --county Somervell [--county ...] [--max-files 300]
  minutes.py harvest --all-supported          every census county with a live
                                              minutes URL on a supported platform
  minutes.py index [--county X]               extract text + keyword-scan new PDFs
  minutes.py resolve 21INR0520                meetings mentioning the project/SPV
                                              (county-scoped, word-boundary match)
  minutes.py resolve --name "Yellow Viking" --county Somervell

A resolve miss prints an explicit negative line that distinguishes "county not
harvested / platform unsupported / no online minutes" from a true no-mention.
Scanned-image PDFs yield no text (text_len 0 in the index) — counted and reported,
not silently skipped; OCR is out of scope.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import re
import sys
import tempfile
import time
import urllib.parse
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parents[2]  # gis-research/
CENSUS = BASE / "data" / "reference" / "county_minutes_census.json"
DOCS = BASE / "data" / "reference" / "county_minutes"
INDEX = BASE / "data" / "reference" / "county_minutes_index.json"

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) research-agent/1.0"}
THROTTLE = Path(tempfile.gettempdir()) / ".minutes_throttle.lock"
MIN_INTERVAL = 1.0
GENERIC_TERMS = ("reinvestment zone", "abatement", "solar", "wind farm", "wind project",
                 "battery", "energy storage", "interconnect")

SUPPORTED = ("eztask", "cira", "revize", "custom", "other", "easydocs", "civicplus")


def _throttle() -> None:
    THROTTLE.touch(exist_ok=True)
    with THROTTLE.open("r+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            last = float(fh.read().strip() or 0)
        except ValueError:
            last = 0.0
        wait = last + MIN_INTERVAL - time.time()
        if wait > 0:
            time.sleep(wait)
        fh.seek(0), fh.truncate(), fh.write(str(time.time()))


def get(url: str, timeout: int = 60) -> requests.Response:
    for backoff in (5, 20, None):
        _throttle()
        try:
            r = requests.get(url, headers=UA, timeout=timeout)
        except requests.RequestException:
            if backoff is None:
                raise
            time.sleep(backoff)
            continue
        if r.status_code == 429 or r.status_code >= 500:
            if backoff is None:
                r.raise_for_status()
            time.sleep(backoff)
            continue
        r.raise_for_status()
        return r
    raise RuntimeError("unreachable")


def _census() -> dict[str, dict]:
    return {r["county"]: r for r in json.loads(CENSUS.read_text())}


def _platform(row: dict) -> str:
    return (row.get("minutes_platform") or "").lower()


def _supported(row: dict) -> bool:
    p = _platform(row)
    return bool(row.get("minutes_url")) and any(s in p for s in SUPPORTED)


DATE_PATS = (
    re.compile(r"(\d{1,2})[-_./](\d{1,2})[-_./](20\d{2})"),   # M-D-YYYY
    re.compile(r"(20\d{2})[-_./](\d{1,2})[-_./](\d{1,2})"),   # YYYY-M-D
    re.compile(r"_(\d{2})(\d{2})(20\d{2})-"),                 # CivicPlus _MMDDYYYY-
)


def _date_guess(s: str) -> str | None:
    for pat in DATE_PATS:
        m = pat.search(s)
        if not m:
            continue
        a, b, c = m.groups()
        try:
            if len(a) == 4:
                y, mo, d = int(a), int(b), int(c)
            else:
                mo, d, y = int(a), int(b), int(c)
            if 2000 <= y <= 2030 and 1 <= mo <= 12 and 1 <= d <= 31:
                return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            continue
    return None


# ---- harvest --------------------------------------------------------------
def _pdf_links_generic(page_url: str) -> list[tuple[str, str]]:
    """(absolute_url, link_text) for every PDF-ish link on a minutes page."""
    html = get(page_url).text
    out = []
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.S | re.I):
        href, text = m.group(1), re.sub(r"<[^>]+>|\s+", " ", m.group(2)).strip()
        if re.search(r"\.pdf(\?|$)", href, re.I) or "/docs/" in href.lower():
            out.append((urllib.parse.urljoin(page_url, href), text))
    return list(dict.fromkeys(out))


def _pdf_links_civicplus(page_url: str, since_year: int = 2019) -> list[tuple[str, str]]:
    """CivicPlus AgendaCenter: the landing page only lists the current year, but the
    Search endpoint accepts a date range — sweep year-by-year back to since_year.
    Minutes preferred over Agendas (dedup on the _MMDDYYYY-NN meeting id)."""
    import datetime as dt
    root = re.match(r"(https?://[^/]+)", page_url).group(1)
    base = root + "/AgendaCenter"
    seen: dict[str, tuple[str, str]] = {}   # meeting-id -> (url, label)
    for year in range(dt.date.today().year, since_year - 1, -1):
        u = f"{base}/Search/?term=&CIDs=all&startDate=01/01/{year}&endDate=12/31/{year}"
        try:
            html = get(u).text
        except Exception:
            continue
        for m in re.finditer(
                r'href="(/AgendaCenter/ViewFile/(Minutes|Agenda)/(_[0-9-]+))(\?[^"]*)?"',
                html, re.I):
            href, kind, mid, query = m.groups()
            if query:            # skip ?html=true / ?packet=true variants
                continue
            # minutes win over agendas for the same meeting id
            if mid not in seen or (kind.lower() == "minutes"
                                   and "Minutes" not in seen[mid][1]):
                seen[mid] = (root + href, f"{kind} {mid}")
    return list(seen.values())


def harvest(counties: list[str] | None, all_supported: bool, max_files: int) -> None:
    census = _census()
    if all_supported:
        counties = [c for c, r in census.items()
                    if _supported(r) and r.get("v_minutes", {}).get("ok")]
        print(f"{len(counties)} counties with live, supported minutes pages")
    total_new = 0
    for co in counties:
        row = census.get(co)
        if not row:
            print(f"{co}: not in census — skipping")
            continue
        if not _supported(row):
            print(f"{co}: platform '{row.get('minutes_platform')}' not yet supported "
                  f"(phase-2: CivicClerk/Legistar APIs) — skipping")
            continue
        url = row["minutes_url"]
        try:
            links = (_pdf_links_civicplus(url) if "civicplus" in _platform(row)
                     else _pdf_links_generic(url))
        except Exception as e:
            print(f"{co}: minutes page fetch failed — {e.__class__.__name__}: {e}")
            continue
        # keep court/minutes/agenda-looking files; drop obvious non-meeting docs
        keep = [(u, t) for u, t in links
                if re.search(r"minute|agenda|court|commission", (u + " " + t), re.I)] or links
        dest = DOCS / co.replace(" ", "_")
        dest.mkdir(parents=True, exist_ok=True)
        new = 0
        for u, text in keep[:max_files]:
            name = re.sub(r"[^A-Za-z0-9._-]+", "_",
                          urllib.parse.unquote(u.split("/")[-1].split("?")[0]))[:120]
            if not name.lower().endswith(".pdf"):
                name += ".pdf"
            d = _date_guess(u) or _date_guess(text)
            if d:
                name = f"{d}_{name}"
            f = dest / name
            if f.exists() and f.stat().st_size > 1024:
                continue
            try:
                r = get(u, timeout=120)
                if not r.content[:5].startswith(b"%PDF"):
                    continue
                f.write_bytes(r.content)
                new += 1
            except Exception as e:
                print(f"  {co}: {name} FAIL {e.__class__.__name__}")
        total_new += new
        print(f"{co}: {len(keep)} candidate links, {new} new PDFs "
              f"-> {dest.relative_to(BASE)}")
    print(f"harvest done: {total_new} new PDFs")


# ---- index ----------------------------------------------------------------
def _queue():
    import pandas as pd
    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    latest = df[df.fileDate == df.fileDate.max()]
    return latest[latest.cancelDate.isna() & latest.inActiveDate.isna()
                  & latest.approvedForCommercialOperation.isna()]


def _name_keys(name: str) -> list[str]:
    """Project-name keys, ≥6 chars, word-boundary-safe (same spirit as ch312.py)."""
    name = re.sub(r"\s*\(.*?\)\s*", " ", str(name)).strip()
    keys = [name]
    core = re.sub(r"\s+(Solar|Wind|Storage|BESS|Battery|Energy|Project|Farm|Park|"
                  r"Center|Hybrid|[IVX]+|\d+|SLF)$", "", name, flags=re.I).strip()
    if core != name:
        keys.append(core)
    return [k for k in dict.fromkeys(keys) if len(k) >= 6]


def index(counties: list[str] | None) -> None:
    from pypdf import PdfReader
    idx = json.loads(INDEX.read_text()) if INDEX.exists() else {"files": {}}
    q = _queue()
    by_county: dict[str, list[tuple[str, list[str]]]] = {}
    for _, r in q.iterrows():
        co = str(r.county or "").strip()
        by_county.setdefault(co, []).append((r.INR, _name_keys(r.projectName)))

    scanned = skipped = image_only = 0
    for cdir in sorted(DOCS.iterdir()) if DOCS.exists() else []:
        co = cdir.name.replace("_", " ")
        if counties and co not in counties:
            continue
        targets = by_county.get(co, [])
        for pdf in sorted(cdir.glob("*.pdf")):
            rel = str(pdf.relative_to(BASE))
            if rel in idx["files"]:
                skipped += 1
                continue
            try:
                text = " ".join((p.extract_text() or "") for p in PdfReader(pdf).pages)
            except Exception:
                text = ""
            low = re.sub(r"\s+", " ", text).lower().strip()
            hits = {}
            for inr, keys in targets:
                found = [k for k in keys
                         if re.search(r"\b" + re.escape(k.lower()) + r"\b", low)]
                if found:
                    hits[inr] = found
            generic = [t for t in GENERIC_TERMS if t in low]
            idx["files"][rel] = {
                "county": co, "date": _date_guess(pdf.name), "text_len": len(low),
                "inr_hits": hits, "generic": generic,
            }
            scanned += 1
            if len(low) < 40:   # empty or whitespace-only extraction = image scan
                image_only += 1
            if hits:
                print(f"  HIT {rel}: {hits}")
    INDEX.write_text(json.dumps(idx, indent=0))
    n_hits = sum(1 for f in idx["files"].values() if f["inr_hits"])
    print(f"index: {scanned} scanned (+{skipped} already indexed), "
          f"{image_only} image-only (no text — OCR out of scope), "
          f"{n_hits} files with INR hits, total {len(idx['files'])} -> {INDEX}")


# ---- resolve ---------------------------------------------------------------
def resolve(inr: str | None, name: str | None, county: str | None) -> int:
    census = _census()
    idx = json.loads(INDEX.read_text()) if INDEX.exists() else {"files": {}}
    if inr:
        q = _queue()
        row = q[q.INR == inr]
        if row.empty:
            raise SystemExit(f"{inr} not in latest active queue")
        r = row.iloc[0]
        name, county = str(r.projectName), str(r.county or "").strip()
        print(f"{inr}  '{name}'  {county} Co")
    keys = _name_keys(name)

    crow = census.get(county)
    harvested = (DOCS / county.replace(" ", "_")).exists()
    files = {p: f for p, f in idx["files"].items() if f["county"] == county}
    print(f"provenance: county_minutes index — {county}: "
          f"{len(files)} indexed meeting files"
          + ("" if harvested else " (COUNTY NOT HARVESTED)"))

    matches = []
    for p, f in sorted(files.items()):
        if inr and inr in f["inr_hits"]:
            matches.append((p, f, f["inr_hits"][inr]))
            continue
        low_keys = [k for k in keys if k.lower() in " ".join(
            sum(f["inr_hits"].values(), []) if f["inr_hits"] else []).lower()]
        if low_keys:
            matches.append((p, f, low_keys))
    if not inr and name:  # free-text: live re-scan of county index by name key
        matches = [(p, f, [k for k in keys]) for p, f in sorted(files.items())
                   if any(re.search(r"\b" + re.escape(k.lower()) + r"\b",
                                    " ".join(f.get("generic", []))) for k in keys)] or matches

    if matches:
        print(f"{len(matches)} meeting file(s) mention the project:")
        for p, f, ks in matches:
            print(f"  {f.get('date') or '????-??-??'}  {p}  (matched: {', '.join(ks)})")
        return 0

    # explicit, honest negative
    if not crow:
        print(f"NEGATIVE (NO DATA): '{county}' not in the census — cannot say.")
    elif not crow.get("minutes_url"):
        print(f"NEGATIVE (NO ONLINE MINUTES): {county} County does not post minutes "
              "online per the census — check local newspaper legal notices "
              "(search.py) instead. Not evidence of no mention.")
    elif not _supported(crow):
        print(f"NEGATIVE (PLATFORM NOT HARVESTED): {county} County uses "
              f"'{crow.get('minutes_platform')}' — phase-2 handler needed. "
              "Not evidence of no mention.")
    elif not harvested:
        print(f"NEGATIVE (NOT YET HARVESTED): run "
              f"`minutes.py harvest --county \"{county}\"` first.")
    else:
        n_img = sum(1 for f in files.values() if f["text_len"] == 0)
        print(f"NEGATIVE EVIDENCE: no mention of {keys} in {len(files)} indexed "
              f"meeting files for {county} County"
              + (f" ({n_img} are image-only scans — text not extractable, real "
                 f"coverage is {len(files)-n_img} files)" if n_img else "")
              + ". Meetings older than the portal's archive are not covered.")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("harvest", help="download minutes PDFs for counties")
    h.add_argument("--county", action="append", default=None)
    h.add_argument("--all-supported", action="store_true")
    h.add_argument("--max-files", type=int, default=300)
    i = sub.add_parser("index", help="extract text + keyword-scan downloaded PDFs")
    i.add_argument("--county", action="append", default=None)
    r = sub.add_parser("resolve", help="meetings mentioning an INR/project")
    r.add_argument("inr", nargs="?", default=None)
    r.add_argument("--name", default=None)
    r.add_argument("--county", default=None)
    a = ap.parse_args()

    if a.cmd == "harvest":
        if not (a.county or a.all_supported):
            raise SystemExit("harvest needs --county or --all-supported")
        harvest(a.county, a.all_supported, a.max_files)
    elif a.cmd == "index":
        index(a.county)
    elif a.cmd == "resolve":
        if not (a.inr or (a.name and a.county)):
            raise SystemExit("resolve needs an INR, or --name with --county")
        sys.exit(resolve(a.inr, a.name, a.county))


if __name__ == "__main__":
    main()
