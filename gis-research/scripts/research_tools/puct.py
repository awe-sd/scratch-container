"""PUCT Interchange search + document download — programmatic, throttled, retry-safe.

Why this exists: interconnection agreements are NOT docketed under the project's name.
They are informational filings inside the TRANSMISSION PROVIDER's standing docket
(Subst. R. §25.195(e) — e.g. Oncor files all its ERCOT IAs under control 35077), so
`FilingParty=<project>` returns 0 records. The field that finds them is
**FilingDescription** (free text over the filing description line). Ad-hoc WebFetch
against the portal also trips its rate limiter (HTTP 402); this tool throttles across
processes and retries with backoff, so parallel research agents can share it.

Agent usage (run from repo root with `uv run`):
  puct.py ia "Moccasin Solar" --dir gis-research/research/<proj>/sources --signed 2024-09-06
      One-shot: search FilingDescription -> walk matching filings -> download the
      interconnection-agreement PDFs into --dir. Prints saved paths. START HERE.
      Pass --signed <iaSigned from the identity packet>: on 0 hits it browses the
      central docket around that date so you can spot the SPV under another name.
  puct.py search "Moccasin Solar" [--field desc|party|style]
      List matching controls (control#, utility, case style).
  puct.py filings 35077 [--match "Hanson"] [--party CenterPoint]
                        [--from 2024-01-01 --to 2024-06-30]
      List filing items inside a control (item#, date, party, description).
  puct.py docs 35077 1682
      List documents for one item (id, pages, format, url).
  puct.py fetch 35077 1682 --dir <sources_dir>
      Download that item's PDFs.

Exit 0 with "0 results" lines is a *finding* (log it as negative evidence), not an error.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import html as htmllib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

import requests

BASE_URL = "https://interchange.puc.texas.gov"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) research-agent/1.0"}
# certifi in this venv can't build interchange.puc.texas.gov's chain; the system
# bundle can (curl works). Prefer it when present.
_SYS_CA = "/etc/ssl/certs/ca-certificates.crt"
VERIFY = _SYS_CA if os.path.exists(_SYS_CA) else True
FIELD = {"desc": "FilingDescription", "party": "FilingParty", "style": "Description"}
# THE central docket: every ERCOT TSP (Oncor, ETT, CenterPoint, AEP, LCRA, TNMP, ...)
# files its executed IAs as informational filings under this one control number
# (verified 2026-07-19: 2,530 filings, parties span all TSPs). There is no per-TSP docket.
IA_DOCKET = "35077"
THROTTLE_LOCK = Path(tempfile.gettempdir()) / ".puct_throttle.lock"
MIN_INTERVAL = 2.0          # seconds between requests, shared across ALL processes
RETRIES = (5, 15, 45)       # backoff on 402/429/5xx — the portal 402s when hammered
IA_WORDS = re.compile(r"interconnection agreement|amendment .* interconnection|"
                      r"generation interconnection", re.I)


def _throttle() -> None:
    """Cross-process rate limit: flock a shared file, sleep out the interval."""
    THROTTLE_LOCK.touch(exist_ok=True)
    with THROTTLE_LOCK.open("r+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            last = float(fh.read().strip() or 0)
        except ValueError:
            last = 0.0
        wait = last + MIN_INTERVAL - time.time()
        if wait > 0:
            time.sleep(wait)
        fh.seek(0), fh.truncate(), fh.write(str(time.time()))


def get(url: str, **kw) -> requests.Response:
    for i, backoff in enumerate((*RETRIES, None)):
        _throttle()
        try:
            r = requests.get(url, headers=UA, timeout=60, verify=VERIFY, **kw)
        except requests.RequestException as e:
            if backoff is None:
                raise
            print(f"  [{e.__class__.__name__} — retry in {backoff}s]", file=sys.stderr)
            time.sleep(backoff)
            continue
        if r.status_code in (402, 429) or r.status_code >= 500:
            if backoff is None:
                r.raise_for_status()
            print(f"  [HTTP {r.status_code} — rate-limited, retry in {backoff}s]", file=sys.stderr)
            time.sleep(backoff)
            continue
        r.raise_for_status()
        return r
    raise RuntimeError("unreachable")


def _rows(page_html: str) -> list[tuple[list[str], list[str]]]:
    """(cell_texts, hrefs) per <tr> of the first results table."""
    m = re.search(r"<table[^>]*>(.*?)</table>", page_html, re.S)
    if not m:
        return []
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(1), re.S):
        cells = [htmllib.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c))).strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        links = [htmllib.unescape(u) for u in re.findall(r'href="([^"]+)"', tr)]
        if cells:
            out.append((cells, links))
    return out


def search(query: str, field: str = "desc") -> list[dict]:
    params = {"UtilityType": "A", "ItemMatch": "1", "DocumentType": "ALL",
              FIELD[field]: query}
    r = get(f"{BASE_URL}/search/search/", params=params)
    hits = []
    for cells, links in _rows(r.text):
        ctrl = next((re.search(r"ControlNumber=(\d+)", u).group(1)
                     for u in links if "ControlNumber=" in u), None)
        if ctrl and len(cells) >= 4:
            hits.append({"control": ctrl, "n_filings": cells[1],
                         "utility": cells[2], "style": cells[3]})
    return hits


def filings(control: str, query: str | None = None, field: str = "desc",
            party: str | None = None, date_from: str | None = None,
            date_to: str | None = None) -> list[dict]:
    params = {"ControlNumber": control, "UtilityType": "A", "ItemMatch": "Equal",
              "DocumentType": "ALL"}
    if query:
        params[FIELD[field]] = query
    if party:
        params["FilingParty"] = party
    if date_from:
        params["DateFiledFrom"] = _mdy(date_from)
    if date_to:
        params["DateFiledTo"] = _mdy(date_to)
    r = get(f"{BASE_URL}/search/filings/", params=params)
    out = []
    for cells, links in _rows(r.text):
        if len(cells) >= 5 and cells[0].isdigit():
            out.append({"item": cells[0], "filed": cells[1], "party": cells[2],
                        "type": cells[3], "description": cells[4]})
    m = re.search(r"(\d+) filing", r.text)
    if m and int(m.group(1)) > len(out):
        print(f"  [NOTE: {m.group(1)} filings match but only {len(out)} parsed "
              "(first page) — narrow with --from/--to or --match]", file=sys.stderr)
    return out


def _mdy(iso: str) -> str:
    """The portal's date inputs want MM/DD/YYYY; accept ISO too."""
    try:
        return dt.date.fromisoformat(iso).strftime("%m/%d/%Y")
    except ValueError:
        return iso


def documents(control: str, item: str) -> list[dict]:
    r = get(f"{BASE_URL}/search/documents/", params={"controlNumber": control,
                                                     "itemNumber": item})
    docs = []
    for cells, links in _rows(r.text):
        url = next((u for u in links if "/Documents/" in u), None)
        if url and len(cells) >= 3:
            docs.append({"id": cells[0], "pages": cells[1], "format": cells[2],
                         "url": url if url.startswith("http") else BASE_URL + url})
    return docs


def slug(s: str, n: int = 48) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:n]


# ---------------------------------------------------------------------------
# Systematic INR -> IA matching (no dates, no fuzzy scores).
#
# The queue's iaSigned date is self-reported to ERCOT and often stale, so date
# windows are NOT a join key. Instead: snapshot the ENTIRE central docket once
# (2 requests — the portal serves 2,000 rows/page; ItemMatch 3 = "greater than"),
# match filing descriptions by EXACT substrings of authoritative names (queue
# projectName + spv_name/developer/public_project_name from the triage pass),
# then CONFIRM by finding the INR string inside the downloaded PDF text —
# ERCOT SGIAs reference the GINR number (e.g. "23INR0086") in the agreement.
# ---------------------------------------------------------------------------
BASE = Path(__file__).resolve().parents[2]  # gis-research/
INDEX_FILE = BASE / "research" / "_reference" / "puct_ia_docket_index.json"
PAGE_SIZE = 2000


def build_index() -> list[dict]:
    rows: list[dict] = []
    last = 0
    while True:
        params = {"ControlNumber": IA_DOCKET, "UtilityType": "A",
                  "DocumentType": "ALL"}
        if last:
            params.update({"ItemNumber": str(last), "ItemMatch": "3"})  # 3 = greater-than
        r = get(f"{BASE_URL}/search/filings/", params=params)
        page = [{"item": c[0], "filed": c[1], "party": c[2], "type": c[3],
                 "description": c[4]}
                for c, _ in _rows(r.text) if c and c[0].isdigit()]
        rows += page
        if len(page) < PAGE_SIZE:
            break
        last = max(int(p["item"]) for p in page)
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps({"docket": IA_DOCKET,
                                      "fetched": str(dt.date.today()),
                                      "filings": rows}, indent=0))
    print(f"indexed {len(rows)} filings of docket {IA_DOCKET} -> {INDEX_FILE}")
    return rows


def load_index(refresh: bool = False) -> list[dict]:
    if not refresh and INDEX_FILE.exists():
        return json.loads(INDEX_FILE.read_text())["filings"]
    return build_index()


# Generic trailing tokens that queue names carry but filing descriptions often omit
# ("Red Egret BESS" is filed as "Red Egret, LLC"). Stripping them is a DEFINED
# transformation — precision comes from the INR-in-PDF verification step, not the key.
GENERIC_TAIL = re.compile(
    r"\s+(BESS|Solar|Wind|Storage|Battery|Batteries|Energy|Center|Centre|Project|"
    r"Hybrid|Power|Station|Gas|Repower|Facility|Farm|Park|[IVX]+|\d+|[A-Z])$", re.I)


def _tail_stripped(name: str) -> list[str]:
    """name minus generic tail tokens, iteratively: 'Aldrin 138 BESS' -> 'Aldrin 138'
    -> 'Aldrin'. Keep variants that stay distinctive (>=8 chars or >=2 words)."""
    out, cur = [], name
    while True:
        nxt = GENERIC_TAIL.sub("", cur).strip()
        if nxt == cur or not nxt:
            break
        if len(nxt) >= 8 or len(nxt.split()) >= 2:
            out.append(nxt)
        cur = nxt
    # final single-word stem is still useful when reasonably long ("Aldrin", "Twinwood")
    if cur and cur not in out and len(cur) >= 6 and cur.lower() != name.lower():
        out.append(cur)
    return out


def match_keys(inr: str, extra: list[str]) -> list[str]:
    """Exact-substring keys from authoritative sources: queue + triage findings.
    Each key is a defined transformation of an authoritative name — never a guess."""
    keys = list(extra)
    import pandas as pd  # lazy — only the match path needs it
    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    latest = df[df.fileDate == df.fileDate.max()]
    row = latest[latest.INR == inr]
    if not row.empty:
        name = re.sub(r"\s*\(.*\)\s*$", "", str(row.iloc[0].projectName)).strip()
        keys.append(name)
        keys += _tail_stripped(name)
    for d in BASE.glob(f"research/{inr}_*/triage_findings.json"):
        try:
            t = json.loads(d.read_text())
        except json.JSONDecodeError:
            continue
        for k in ("spv_name", "developer", "public_project_name", "queue_name"):
            v = t.get(k)
            if isinstance(v, str) and len(v) >= 5:
                base = re.sub(r",?\s+(LLC|L\.L\.C\.|Inc\.?|LP)$", "", v, flags=re.I)
                keys.append(base)
                keys += _tail_stripped(base)
    # dedupe, keep order, drop too-generic keys
    seen, out = set(), []
    for k in keys:
        k = k.strip()
        if len(k) >= 5 and k.lower() not in seen:
            seen.add(k.lower())
            out.append(k)
    return out


def pdf_text(path: Path) -> str:
    try:
        import pypdf
        return "".join(p.extract_text() or "" for p in pypdf.PdfReader(path).pages)
    except Exception:
        return ""


def cmd_match(inr: str, out_dir: Path | None, extra_keys: list[str],
              refresh: bool = False) -> int:
    idx = load_index(refresh)
    keys = match_keys(inr, extra_keys)
    print(f"match keys for {inr}: {keys}")
    cands = []
    for f in idx:
        best = max((len(k) for k in keys if k.lower() in f["description"].lower()),
                   default=0)
        if best:
            cands.append((best, f))
    # longest matched key first — a specific name beats a coincidental short stem
    cands.sort(key=lambda x: -x[0])
    cands = [f for _, f in cands]
    print(f"{len(cands)} candidate filing(s) by exact name match:")
    for f in cands:
        print(f"  {IA_DOCKET}-{f['item']}  {f['filed']}  {f['description'][:120]}")
    if not cands:
        print("no exact-name candidate. Next systematic step: find the SPV's legal name "
              "(TX SOS / Comptroller / county records), then re-run with "
              f"`puct.py match {inr} --key \"<SPV name>\"`. Do NOT guess by date.")
        return 0
    if out_dir is None:
        print("(dry run — pass --dir to download + verify)")
        return 0
    # secondary deterministic evidence for older SGIAs that omit the GINR number
    county = mw = None
    import pandas as pd
    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    latest = df[df.fileDate == df.fileDate.max()]
    row = latest[latest.INR == inr]
    if not row.empty:
        county = str(row.iloc[0].county or "").strip()
        mw = row.iloc[0].capacityMw
    for f in cands[:6]:
        saved = fetch_item(IA_DOCKET, f["item"], out_dir, desc=f["description"])
        for p in saved:
            txt = pdf_text(p).lower()
            mw_hit = bool(mw) and (f"{mw:g}" in txt or f"{int(mw)}" in txt)
            county_hit = bool(county) and county.lower() in txt
            if inr.lower() in txt:
                verdict = "CONFIRMED (INR found in document text)"
            elif not txt.strip():
                verdict = "UNVERIFIED (image-only PDF — no text layer; verify visually)"
            elif county_hit and mw_hit:
                verdict = f"PROBABLE (county '{county}' + {mw:g} MW in text; INR absent)"
            else:
                verdict = "UNCONFIRMED (INR not in text — check parties/POI page)"
            if verdict.startswith(("UNCONFIRMED", "UNVERIFIED")):
                # visible flag on disk so a wrong-project PDF is never mistaken for evidence
                marked = p.with_name("unverified_" + p.name)
                p.rename(marked)
                p = marked
            print(f"  -> {p.name}: {verdict}")
    return 0


def fetch_item(control: str, item: str, out_dir: Path, desc: str = "") -> list[Path]:
    """Download every PDF of one filing item into out_dir (skips ZIP/native)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for d in documents(control, item):
        if d["format"].upper() != "PDF":
            continue
        name = f"{dt.date.today()}_puct_{control}-{item}_{slug(desc) or 'filing'}.pdf"
        dest = out_dir / name
        if dest in saved:  # multi-PDF filing item: same desc — suffix the extras with the
            # doc id (else they'd collide: silently skipped, and cmd_match would verify the
            # same path twice — renaming it unverified_ mid-loop then FileNotFoundError)
            dest = out_dir / name.replace(".pdf", f"_{d['id']}.pdf")
        if dest.exists():
            print(f"exists: {dest}")
            saved.append(dest)
            continue
        r = get(d["url"])
        dest.write_bytes(r.content)
        print(f"saved: {dest} ({len(r.content)//1024} KB, {d['pages']})")
        saved.append(dest)
    return saved


def cmd_ia(query: str, out_dir: Path, max_controls: int = 3,
           signed: str | None = None) -> int:
    """One-shot IA hunt: search -> filings -> download IA-looking PDFs."""
    hits = search(query)
    print(f"{len(hits)} control(s) match FilingDescription='{query}'")
    # A generic word ("Shepard") also matches decades-old rate cases — walk dockets
    # whose case style is about interconnection agreements first, the rest after.
    ia_style = [h for h in hits if "INTERCONNECTION" in h["style"].upper()]
    rest = [h for h in hits if h not in ia_style]
    n_saved = 0
    for h in (ia_style + rest)[:max_controls]:
        print(f"control {h['control']} [{h['utility']}] {h['style'][:90]}")
        for f in filings(h["control"], query):
            is_ia = bool(IA_WORDS.search(f["description"]))
            tag = "IA " if is_ia else "    "
            print(f"  {tag}{h['control']}-{f['item']}  {f['filed']}  {f['party'][:40]}  "
                  f"{f['description'][:100]}")
            if is_ia:
                n_saved += len(fetch_item(h["control"], f["item"], out_dir,
                                          desc=f["description"]))
    if n_saved:
        return 0
    print("no IA PDF downloaded — try shorter name fragments (drop 'LLC', roman "
          "numerals, 'Solar'/'BESS' suffixes). A negative result is evidence: log it.")
    if signed:
        # Informational filings lag the signature by weeks-to-months and may name an
        # unrecognizable SPV — browse the central docket around the signed date so the
        # researcher can eyeball counterparty names.
        d0 = dt.date.fromisoformat(signed)
        d1 = d0 + dt.timedelta(days=180)
        print(f"\nfallback: ALL filings in docket {IA_DOCKET} between {d0} and {d1} "
              "(IA was signed then — look for the project's SPV name):")
        for f in filings(IA_DOCKET, date_from=str(d0), date_to=str(d1)):
            print(f"  {IA_DOCKET}-{f['item']}  {f['filed']}  {f['description'][:130]}")
        print("match found? -> puct.py fetch " + IA_DOCKET + " <item> --dir <sources>")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("index", help="snapshot the whole central IA docket locally")

    p = sub.add_parser("match", help="systematic INR->IA match via local index + "
                                     "exact keys + INR-in-PDF verification")
    p.add_argument("inr")
    p.add_argument("--dir", default=None, help="download+verify into this dir")
    p.add_argument("--key", action="append", default=[],
                   help="extra exact match key (SPV/LLC name); repeatable")
    p.add_argument("--refresh", action="store_true", help="re-fetch the docket index")

    p = sub.add_parser("ia", help="one-shot: search + download IA PDFs")
    p.add_argument("query")
    p.add_argument("--dir", required=True)
    p.add_argument("--max-controls", type=int, default=3)
    p.add_argument("--signed", default=None, metavar="YYYY-MM-DD",
                   help="iaSigned date from the queue; on 0 hits, browse the central "
                        "docket signed..signed+180d so you can spot the SPV name")

    p = sub.add_parser("search", help="find controls")
    p.add_argument("query")
    p.add_argument("--field", choices=FIELD, default="desc")

    p = sub.add_parser("filings", help="list items in a control")
    p.add_argument("control")
    p.add_argument("--match", default=None, help="narrow by FilingDescription")
    p.add_argument("--party", default=None, help="narrow by FilingParty (e.g. CenterPoint)")
    p.add_argument("--from", dest="date_from", default=None, metavar="YYYY-MM-DD")
    p.add_argument("--to", dest="date_to", default=None, metavar="YYYY-MM-DD")

    p = sub.add_parser("docs", help="list documents of an item")
    p.add_argument("control")
    p.add_argument("item")

    p = sub.add_parser("fetch", help="download an item's PDFs")
    p.add_argument("control")
    p.add_argument("item")
    p.add_argument("--dir", required=True)
    p.add_argument("--desc", default="", help="hint for the saved filename")

    a = ap.parse_args()
    if a.cmd == "index":
        build_index()
    elif a.cmd == "match":
        sys.exit(cmd_match(a.inr, Path(a.dir) if a.dir else None, a.key, a.refresh))
    elif a.cmd == "ia":
        sys.exit(cmd_ia(a.query, Path(a.dir), a.max_controls, a.signed))
    elif a.cmd == "search":
        for h in search(a.query, a.field):
            print(f"{h['control']}  filings={h['n_filings']}  [{h['utility']}]  {h['style'][:100]}")
    elif a.cmd == "filings":
        for f in filings(a.control, a.match, party=a.party,
                         date_from=a.date_from, date_to=a.date_to):
            print(f"{a.control}-{f['item']}  {f['filed']}  {f['party'][:40]}  {f['description'][:140]}")
    elif a.cmd == "docs":
        for d in documents(a.control, a.item):
            print(f"{d['id']}  {d['format']}  {d['pages']}  {d['url']}")
    elif a.cmd == "fetch":
        fetch_item(a.control, a.item, Path(a.dir), a.desc)


if __name__ == "__main__":
    main()
