"""Texas Comptroller Chapter 313 agreements + JETI applicants — bulk registry resolver.

Why this exists: for solar/storage queue projects the SPV usually files a school
property-tax value-limitation agreement under its LEGAL name ("Hanson Solar, LLC"),
which the queue codename ("Hanson Solar") is an exact substring of. Two public
Comptroller lists carry that entity name:
  - Chapter 313 (the program EXPIRED 2022-12-31, so this is a static historical list
    of ~740 agreements): the "Agreement Documents" table at comptroller.texas.gov,
    with per-agreement pages at agreement-docs-details.php?id=NNNN.
  - JETI (Jobs, Energy, Technology & Innovation Act — the 2024- successor): the
    Comptroller open-data API (open-data/v1/tables/jeti), pages application-details.php?id=J####.

NEITHER list publishes county or MW — only the SCHOOL DISTRICT. So the deterministic
join is EXACT NAME SUBSTRING (queue projectName <-> applying entity, either direction,
generic tails like 'Solar'/'LLC' stripped). County is a documented BEST-EFFORT only
(match when the school-district name contains the county — true for "Haskell CISD",
false for "Panther Creek CISD"); see --county.

The project description itself lives only inside the linked application PDFs, not in
either list — so the applicant name + the document list are the project handle.

Agent usage (run from repo root with `uv run`):
  ch313.py refresh
      Download both lists into gis-research/data/reference/. Run once; re-run to update.
  ch313.py resolve 23INR0086
      Read the queue row, list Ch.313/JETI applicants whose entity name matches the
      project name. Prints applicant, school district, app#/id, phase, docs-details
      URL, and (for the top hits) the document PDFs.
  ch313.py resolve --county Coleman        best-effort: district name contains county
  ch313.py resolve --name "Cypress Creek"  free-text applicant search, no INR

A miss is a finding: it prints an explicit negative-evidence line.
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

BASE = Path(__file__).resolve().parents[2]  # gis-research/
REF = BASE / "data" / "reference"
CH313_LIST = "https://comptroller.texas.gov/economy/development/prop-tax/ch313/agreement-docs.php"
CH313_DETAIL = "https://comptroller.texas.gov/economy/development/prop-tax/ch313/agreement-docs-details.php?id="
JETI_API = "https://api.comptroller.texas.gov/open-data/v1/tables/jeti"
JETI_DETAIL = "https://comptroller.texas.gov/economy/development/prop-tax/jeti/application-details.php?id="
CH313_FILE = REF / "ch313_agreements.json"
JETI_FILE = REF / "jeti_applications.json"

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) research-agent/1.0"}
_SYS_CA = "/etc/ssl/certs/ca-certificates.crt"
VERIFY = _SYS_CA if os.path.exists(_SYS_CA) else True
THROTTLE_LOCK = Path(tempfile.gettempdir()) / ".ch313_throttle.lock"
MIN_INTERVAL = 2.0
RETRIES = (5, 15, 45)

GENERIC_TAIL = re.compile(
    r"\s*,?\s+(LLC|L\.L\.C\.|Inc\.?|LP|L\.P\.|Ltd\.?|Corp\.?|Co\.?|Holdings|"
    r"BESS|Solar|Wind|Storage|Battery|Batteries|Energy|Center|Centre|Project|"
    r"Hybrid|Power|Station|Facility|Farm|Park|[IVX]+|\d+)$", re.I)


def _throttle() -> None:
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
    for backoff in (*RETRIES, None):
        _throttle()
        try:
            r = requests.get(url, headers=UA, timeout=60, verify=VERIFY, **kw)
        except requests.RequestException:
            if backoff is None:
                raise
            time.sleep(backoff)
            continue
        if r.status_code in (429,) or r.status_code >= 500:
            if backoff is None:
                r.raise_for_status()
            print(f"  [HTTP {r.status_code} — retry in {backoff}s]", file=sys.stderr)
            time.sleep(backoff)
            continue
        r.raise_for_status()
        return r
    raise RuntimeError("unreachable")


def _clean(s: str) -> str:
    return htmllib.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip().rstrip(",").strip()


# ---- refresh -------------------------------------------------------------
def refresh_ch313() -> int:
    html = get(CH313_LIST).text
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        if "agreement-docs-details" not in tr:
            continue
        th = re.search(r"<th[^>]*>(.*?)</th>", tr, re.S)
        tds = [_clean(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(tds) >= 5:
            rows.append({"app_no": tds[0], "applicant": tds[1],
                         "district": _clean(th.group(1)) if th else "",
                         "app_date": tds[2], "tax_year": tds[3], "phase": tds[4]})
    REF.mkdir(parents=True, exist_ok=True)
    CH313_FILE.write_text(json.dumps(
        {"source": CH313_LIST, "fetched": str(dt.date.today()), "rows": rows}, indent=0))
    print(f"ch313: {len(rows)} agreements -> {CH313_FILE}")
    return len(rows)


def refresh_jeti() -> int:
    d = get(JETI_API).json()
    rows = d.get("data", [])
    REF.mkdir(parents=True, exist_ok=True)
    JETI_FILE.write_text(json.dumps(
        {"source": JETI_API, "fetched": str(dt.date.today()),
         "lastUpdated": d.get("lastUpdated"), "downloadLink": d.get("downloadLink"),
         "rows": rows}, indent=0))
    print(f"jeti: {len(rows)} applications -> {JETI_FILE}")
    return len(rows)


# ---- matching ------------------------------------------------------------
def _cores(name: str) -> list[str]:
    """Queue name minus parentheticals, then iteratively minus generic tails."""
    name = re.sub(r"\s*\(.*?\)\s*", " ", str(name)).strip()
    out, cur = [name], name
    while cur:
        nxt = GENERIC_TAIL.sub("", cur).strip().rstrip(",").strip()
        if nxt == cur or not nxt:
            break
        if len(nxt) >= 6 or len(nxt.split()) >= 2:
            out.append(nxt)
        cur = nxt
    return list(dict.fromkeys(k for k in out if len(k) >= 6))


def _score(qname: str, applicant: str) -> int:
    """Longest exact-substring overlap (either direction); 0 = no match."""
    al = applicant.lower()
    best = max((len(k) for k in _cores(qname) if k.lower() in al), default=0)
    a_core = GENERIC_TAIL.sub("", re.sub(r",\s*$", "", applicant)).strip().lower()
    if len(a_core) >= 8 and a_core in qname.lower():
        best = max(best, len(a_core))
    return best


def _detail_pdfs(app_no: str) -> list[str]:
    try:
        html = get(CH313_DETAIL + app_no).text
    except Exception:
        return []
    urls = re.findall(r'href="([^"]*assets\.comptroller[^"]*\.pdf[^"]*)"', html, re.I)
    return list(dict.fromkeys(htmllib.unescape(u) for u in urls))


def _load(f: Path, label: str) -> tuple[dict, list]:
    if not f.exists():
        print(f"  [no {label} list — run `ch313.py refresh` first]")
        return {}, []
    d = json.loads(f.read_text())
    return d, d.get("rows", [])


def _queue_row(inr: str):
    import pandas as pd
    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    latest = df[df.fileDate == df.fileDate.max()]
    row = latest[latest.INR == inr]
    if row.empty:
        raise SystemExit(f"{inr} not in latest snapshot")
    return row.iloc[0]


# ---- resolve -------------------------------------------------------------
def resolve(inr: str | None, county: str | None, name: str | None) -> int:
    ch_meta, ch = _load(CH313_FILE, "Ch.313")
    jt_meta, jt = _load(JETI_FILE, "JETI")
    print(f"provenance: Ch.313 {CH313_FILE.name} (fetched {ch_meta.get('fetched','?')}, "
          f"{len(ch)} rows) + JETI {JETI_FILE.name} (fetched {jt_meta.get('fetched','?')}, "
          f"{len(jt)} rows). Source: comptroller.texas.gov")

    qname = qcounty = None
    if inr:
        r = _queue_row(inr)
        qname, qcounty = str(r.projectName), str(r.county or "")
        print(f"{inr}  '{qname}'  {qcounty} Co  {r.capacityMw} MW  {r.fuel}/{r.technology}")
    elif name:
        qname = name
        print(f"free-text applicant search: '{name}'")
    elif county:
        qcounty = county
        print(f"county best-effort (district-name contains '{county}'): "
              "NOTE the Comptroller lists carry school district, not county — partial only.")

    hits = []  # (score, program, applicant, district, ref_id, phase, detail_url, extra)
    for a in ch:
        if inr or name:
            s = _score(qname, a["applicant"])
            if not s:
                continue
        else:  # county mode
            if county.lower() not in a["district"].lower():
                continue
            s = 0
        hits.append((s, "Ch.313", a["applicant"], a["district"], a["app_no"],
                     a["phase"], CH313_DETAIL + a["app_no"], a.get("app_date", "")))
    for a in jt:
        applicant = a.get("applicant", "")
        district = a.get("school_district", "")
        if inr or name:
            s = _score(qname, applicant)
            if not s:
                continue
        else:
            if county.lower() not in district.lower():
                continue
            s = 0
        neg = " [NEGATIVE recommendation]" if a.get("negative") else ""
        hits.append((s, "JETI", applicant, district, a.get("id", ""),
                     "application" + neg, JETI_DETAIL + a.get("id", ""), ""))

    hits.sort(key=lambda x: -x[0])
    if not hits:
        who = f"'{qname}'" if qname else f"county '{qcounty}'"
        print(f"NEGATIVE EVIDENCE: no Ch.313 agreement or JETI application matches {who}. "
              "For a pre-2023 solar/storage SPV this suggests no value-limitation filing "
              "(or an unrecognized legal name) — record as negative evidence and try "
              "spv.py / TX SOS entity search next.")
        return 0

    print(f"{len(hits)} candidate(s):")
    for i, (s, prog, applicant, district, rid, phase, url, extra) in enumerate(hits[:12]):
        tag = f" (name overlap {s} chars)" if s else ""
        print(f"  [{prog} #{rid}] {applicant}  | district: {district} | {phase}"
              f"{(' | applied '+extra) if extra else ''}{tag}")
        print(f"      {url}")
        if prog == "Ch.313" and i < 3:
            for p in _detail_pdfs(rid):
                print(f"      doc: {p}")
    print("\nverify a candidate as the SPV: puct.py match " + (inr or "<INR>") +
          " --key \"<applicant>\" --dir <sources/>  (INR-in-PDF = confirmed). "
          "Project description/MW are inside the linked application PDFs.")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("refresh", help="download Ch.313 + JETI lists into data/reference/")
    p = sub.add_parser("resolve", help="list Ch.313/JETI applicants for an INR/county/name")
    p.add_argument("inr", nargs="?", default=None)
    p.add_argument("--county", default=None, help="best-effort county (no INR)")
    p.add_argument("--name", default=None, help="free-text applicant substring (no INR)")
    a = ap.parse_args()

    if a.cmd == "refresh":
        refresh_ch313()
        refresh_jeti()
    elif a.cmd == "resolve":
        if not (a.inr or a.county or a.name):
            raise SystemExit("resolve needs an INR, --county, or --name")
        sys.exit(resolve(a.inr, a.county, a.name))


if __name__ == "__main__":
    main()
