"""Texas Comptroller Chapter 312 abatement registry — bulk resolver (counties/cities).

Why this exists: Ch.313 (school value limitations) EXPIRED 2022-12-31 and JETI has only
~38 applications so far — but COUNTY/CITY property-tax abatements under Tax Code Ch.312
continued uninterrupted and are the abatement most post-2022 queue projects actually
sign (e.g. the Hood/Somervell "Yellow Viking" abatements and Deaf Smith's 2024 solar
abatements were all Ch.312 agreements we previously saw only via news stories). The
Comptroller publishes the data via the same open-data API family as JETI (pagination is
`?start=N`, 100/page):
    api.comptroller.texas.gov/open-data/v1/tables/ch312-abatement         (agreements)
    api.comptroller.texas.gov/open-data/v1/tables/ch312-abatement-report  (post-abatement
        annual reports — retains EXPIRED agreements the main table purges; 0 id overlap)
plus bulk CSVs on assets.comptroller.texas.gov (the -detail CSV carries per-year %s).

Unlike Ch.313/JETI (school district only), rows carry a DIRECT county signal ("Lead
Taxing Unit Name" / CAD name), the Reinvestment Zone name (often contains the project
name), and the property owner (often the SPV legal name). ~250 rows also link the actual
filed abatement-agreement PDF (assets.comptroller.texas.gov/{dat,open-data}/ch312/...).

PURGE RECOVERY: the main table purges records ~3 years after expiration. Three partial
antidotes, all implemented here: (1) the report table above retains expired agreements;
(2) `archive` recovers purged rows from Wayback Machine snapshots of the bulk CSVs and
API URL (170 recovered on first run, 2026-07-21) into ch312_purged.json — append-only;
(3) `harvest` downloads every linked agreement PDF to data/reference/ch312_docs/
(gitignored, like puct_docket_pdfs) so documents survive future purges.

COVERAGE CAVEAT (document in findings, do not over-claim): the registry is populated by
CAD submissions on an ANNUAL cycle, some counties do not report at all (Somervell,
Matagorda, Crockett had 0 rows as of 2026-07). A MISS is therefore WEAK negative
evidence — "not in the Ch.312 registry" ≠ "no abatement exists". A HIT is strong.

Agent usage (run from repo root with `uv run`):
  ch312.py refresh    both API tables + both CSVs -> data/reference/
  ch312.py archive    recover purged rows from Wayback snapshots (append-only)
  ch312.py harvest    download all linked agreement PDFs -> data/reference/ch312_docs/
  ch312.py resolve 23INR0057            queue-row name + county match, all datasets
  ch312.py resolve --county "Deaf Smith"
  ch312.py resolve --name "Mule Deer"

A miss prints an explicit negative-evidence line (with the weak-negative caveat).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parents[2]  # gis-research/
REF = BASE / "data" / "reference"
API = "https://api.comptroller.texas.gov/open-data/v1/tables/"
ASSETS = "https://assets.comptroller.texas.gov/open-data-files/"
SEARCH_UI = "https://comptroller.texas.gov/economy/development/search-tools/ch312/abatements-simple.php"
CDX = "http://web.archive.org/cdx/search/cdx"

AGMT_FILE = REF / "ch312_abatements.json"
REPORT_FILE = REF / "ch312_reports.json"
PURGED_FILE = REF / "ch312_purged.json"
DETAIL_FILE = REF / "ch312_abatements_detail.csv"
DOCS_DIR = REF / "ch312_docs"

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) research-agent/1.0"}
_SYS_CA = "/etc/ssl/certs/ca-certificates.crt"
VERIFY = _SYS_CA if os.path.exists(_SYS_CA) else True

GENERIC_TAIL = re.compile(
    r"\s*,?\s+(LLC|L\.L\.C\.|Inc\.?|LP|L\.P\.|Ltd\.?|Corp\.?|Co\.?|Holdings|"
    r"BESS|Solar|Wind|Storage|Battery|Batteries|Energy|Center|Centre|Project|"
    r"Hybrid|Power|Station|Facility|Farm|Park|[IVX]+|\d+)$", re.I)


RETRIES = (10, 30, 90)


def get(url: str, timeout: int = 90) -> requests.Response:
    for backoff in (*RETRIES, None):
        try:
            r = requests.get(url, headers=UA, timeout=timeout, verify=VERIFY)
        except requests.RequestException:
            if backoff is None:
                raise
            time.sleep(backoff)
            continue
        if r.status_code == 429 or r.status_code >= 500:
            if backoff is None:
                r.raise_for_status()
            print(f"  [HTTP {r.status_code} — retry in {backoff}s]", file=sys.stderr)
            time.sleep(backoff)
            continue
        r.raise_for_status()
        return r
    raise RuntimeError("unreachable")


# ---- normalization --------------------------------------------------------
# API rows use raw column codes; CSV rows use display names. Normalize both.
def _norm_api(r: dict, kind: str) -> dict:
    return {
        "id": r.get("id", ""),
        "owner": r.get("prop_ownr_nm") or r.get("first_owner_nm") or "",
        "zone": r.get("abat_zone_nm") or "",
        "lead_unit": r.get("lead_tax_unit_nm") or "",
        "cad": r.get("locl_gov_nm") or "",
        "govt": f"{r.get('govt_name', '')} {r.get('govt_type', '')}".strip(),
        "status": r.get("abat_sta_cd") or ("report" if kind == "report" else ""),
        "base_value": r.get("prop_val_am"),
        "submitted": r.get("submt_dt") or "",
        "effective": r.get("abat_eff_dt") or "",
        "expiry": r.get("abat_xpir_dt") or "",
        "pdf": (r.get("extra_doc_path")
                or (f"https://assets.comptroller.texas.gov/dat/ch312/ch312-abatement/"
                    f"{r['pdf_id']}.pdf" if (r.get("pdf_id") or "").strip() else None)),
        "kind": kind,
    }


def _norm_csv(r: dict, kind: str) -> dict:
    return {
        "id": r.get("Record ID", ""),
        "owner": r.get("Property Owner(s) Name") or "",
        "zone": r.get("Reinvestment Zone Name") or "",
        "lead_unit": r.get("Lead Taxing Unit Name") or "",
        "cad": r.get("CAD Name (Reporting Entity)") or "",
        "govt": "",
        "status": r.get("Abatement Status") or "",
        "base_value": r.get("Base Value of Abated Property"),
        "submitted": r.get("Submission Date") or "",
        "effective": "",
        "expiry": "",
        "pdf": None,
        "kind": kind,
    }


def _paginate(table: str) -> list[dict]:
    rows, start = [], 0
    while True:
        d = get(f"{API}{table}?start={start}").json()
        page = d.get("data", [])
        if not page:
            break
        rows.extend(page)
        start += len(page)
        print(f"  {table}: {len(rows)}/{d.get('count')}", flush=True)
        if len(rows) >= d.get("count", 0):
            break
        time.sleep(1.5)
    return rows


# ---- refresh -------------------------------------------------------------
def refresh() -> None:
    REF.mkdir(parents=True, exist_ok=True)
    agmt = _paginate("ch312-abatement")
    AGMT_FILE.write_text(json.dumps(
        {"source": API + "ch312-abatement", "fetched": str(dt.date.today()),
         "rows": [_norm_api(r, "agreement") for r in agmt]}, indent=0))
    print(f"ch312 agreements: {len(agmt)} -> {AGMT_FILE}")

    rep = _paginate("ch312-abatement-report")
    REPORT_FILE.write_text(json.dumps(
        {"source": API + "ch312-abatement-report", "fetched": str(dt.date.today()),
         "rows": [_norm_api(r, "report") for r in rep]}, indent=0))
    print(f"ch312 post-abatement reports: {len(rep)} -> {REPORT_FILE}")

    r = get(ASSETS + "ch312-abatement-detail.csv", timeout=120)
    DETAIL_FILE.write_bytes(r.content)
    print(f"ch312 detail csv: {len(r.content)/1024:.0f} KB -> {DETAIL_FILE}")


# ---- archive (Wayback purge recovery, append-only) -------------------------
def archive() -> None:
    known = {x["id"] for x in _all_rows()}
    purged = {}
    if PURGED_FILE.exists():
        purged = json.loads(PURGED_FILE.read_text()).get("rows", {})
    print(f"currently known ids: {len(known)}; previously recovered: {len(purged)}")

    def keep(row: dict, snap: str) -> None:
        rid = row["id"]
        if rid and rid not in known and rid not in purged:
            row["recovered_from"] = snap
            purged[rid] = row

    def snaps(url_pat: str) -> list[tuple[str, str]]:
        r = get(f"{CDX}?url={requests.utils.quote(url_pat)}&output=json&limit=200")
        rows = r.json()
        return [(x[1], x[2]) for x in rows[1:] if x[4] == "200"]

    # bulk CSV snapshots (complete files — best source)
    for pat, parse in ((ASSETS + "ch312-abatement.csv", "summary"),
                       (ASSETS + "ch312-abatement-detail.csv", "detail")):
        for stamp, orig in snaps(pat):
            try:
                raw = get(f"https://web.archive.org/web/{stamp}id_/{orig}",
                          timeout=180).content.decode("utf-8", "replace")
            except Exception as e:
                print(f"  [snapshot {stamp} failed: {e}]")
                continue
            n0 = len(purged)
            for r in csv.DictReader(io.StringIO(raw)):
                keep(_norm_csv(r, "purged"), f"{stamp} {parse} CSV")
            print(f"  wayback {stamp} ({parse}): +{len(purged)-n0} recovered")
            time.sleep(2)

    # archived API first pages (only the bare URL is archived, ~100 rows each)
    for table in ("ch312-abatement", "ch312-abatement-report"):
        for stamp, orig in snaps(API + table):
            try:
                d = json.loads(get(
                    f"https://web.archive.org/web/{stamp}id_/{orig}", timeout=120).content)
            except Exception as e:
                print(f"  [snapshot {stamp} failed: {e}]")
                continue
            n0 = len(purged)
            for r in d.get("data", []):
                keep(_norm_api(r, "purged"), f"{stamp} API p1")
            print(f"  wayback {stamp} ({table} API): +{len(purged)-n0} recovered")
            time.sleep(2)

    PURGED_FILE.write_text(json.dumps(
        {"updated": str(dt.date.today()), "rows": purged}, indent=0))
    print(f"ch312 purged-recovered total: {len(purged)} -> {PURGED_FILE}")


# ---- harvest (download linked agreement PDFs) ------------------------------
def harvest() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    rows = _all_rows()
    todo = [x for x in rows if x.get("pdf")]
    print(f"{len(todo)} rows carry a document link")
    ok = skip = fail = 0
    for x in todo:
        dest = DOCS_DIR / f"{x['id']}.pdf"
        if dest.exists() and dest.stat().st_size > 1024:
            skip += 1
            continue
        try:
            r = get(x["pdf"], timeout=180)
            dest.write_bytes(r.content)
            ok += 1
            print(f"  {x['id']}.pdf ({len(r.content)/1024:.0f} KB) — {x['owner'][:40]}")
        except Exception as e:
            fail += 1
            print(f"  {x['id']} FAIL {e}")
        time.sleep(1.0)
    print(f"harvest done: {ok} downloaded, {skip} already present, {fail} failed "
          f"-> {DOCS_DIR}")


# ---- matching (same conventions as ch313.py) ------------------------------
def _cores(name: str) -> list[str]:
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


def _score(qname: str, candidate: str) -> int:
    cl = candidate.lower()
    best = max((len(k) for k in _cores(qname) if k.lower() in cl), default=0)
    c_core = GENERIC_TAIL.sub("", re.sub(r",\s*$", "", candidate)).strip().lower()
    if len(c_core) >= 8 and c_core in qname.lower():
        best = max(best, len(c_core))
    return best


def _all_rows() -> list[dict]:
    rows = []
    for f in (AGMT_FILE, REPORT_FILE):
        if f.exists():
            rows.extend(json.loads(f.read_text()).get("rows", []))
    if PURGED_FILE.exists():
        rows.extend(json.loads(PURGED_FILE.read_text()).get("rows", {}).values())
    return rows


def _queue_row(inr: str):
    import pandas as pd
    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    latest = df[df.fileDate == df.fileDate.max()]
    row = latest[latest.INR == inr]
    if row.empty:
        raise SystemExit(f"{inr} not in latest snapshot")
    return row.iloc[0]


def _detail_rows(record_id: str) -> list[dict]:
    if not DETAIL_FILE.exists():
        return []
    with DETAIL_FILE.open(newline="", encoding="utf-8", errors="replace") as fh:
        return [r for r in csv.DictReader(fh) if r.get("Record ID") == record_id]


def _fmt(x: dict) -> str:
    kind = {"agreement": "Ch.312", "report": "Ch.312-report", "purged": "Ch.312-PURGED"}[x["kind"]]
    extra = f" | recovered from {x['recovered_from']}" if x.get("recovered_from") else ""
    return (f"[{kind} #{x['id']}] owner: {x['owner']}"
            f" | zone: {x['zone']}"
            f" | lead unit: {x['lead_unit']} ({x['cad']})"
            f" | {x['status'] or '?'}"
            + (f" | expires {x['expiry']}" if x.get("expiry") else "")
            + (f" | doc: {x['pdf']}" if x.get("pdf") else "")
            + extra)


# ---- resolve -------------------------------------------------------------
def resolve(inr: str | None, county: str | None, name: str | None) -> int:
    rows = _all_rows()
    if not rows:
        print("  [no Ch.312 data — run `ch312.py refresh` (and `archive`) first]")
        return 1
    n_kind = {}
    for x in rows:
        n_kind[x["kind"]] = n_kind.get(x["kind"], 0) + 1
    print(f"provenance: Ch.312 open-data — {n_kind.get('agreement', 0)} live agreements + "
          f"{n_kind.get('report', 0)} post-abatement reports + "
          f"{n_kind.get('purged', 0)} Wayback-recovered purged rows. "
          "CAD-submitted, annual cycle — a MISS is weak negative evidence (see docstring)")

    qname = qcounty = None
    if inr:
        r = _queue_row(inr)
        qname, qcounty = str(r.projectName), str(r.county or "")
        print(f"{inr}  '{qname}'  {qcounty} Co  {r.capacityMw} MW  {r.fuel}/{r.technology}")
    elif name:
        qname = name
        print(f"free-text owner/zone search: '{name}'")
    else:
        qcounty = county
        print(f"county search (lead-taxing-unit/CAD contains '{county}'): NOTE city-led "
              "abatements name the CITY as lead unit — those only county-match via the "
              "CAD field; a name search is the safer net.")

    def county_hit(x: dict, co: str) -> bool:
        co = co.lower()
        return (co in x["lead_unit"].lower() or co in x["cad"].lower()
                or co in x["govt"].lower())

    hits = []
    for x in rows:
        if qname:
            s = max(_score(qname, x["owner"]), _score(qname, x["zone"]))
            if s:
                hits.append((s, x))
                continue
        if inr and qcounty and county_hit(x, qcounty):
            hits.append((0, x))
        elif county and not qname and county_hit(x, county):
            hits.append((0, x))

    hits.sort(key=lambda h: -h[0])
    if not hits:
        who = f"'{qname}'" if qname else f"county '{qcounty}'"
        print(f"NEGATIVE EVIDENCE (WEAK): no Ch.312 row (live, report, or recovered) "
              f"matches {who}. Because the registry is CAD-submitted on an annual cycle "
              "with incomplete county coverage, this does NOT rule out an abatement — "
              "check commissioners-court minutes / local news (search.py) before "
              "recording absence.")
        return 0

    named = [h for h in hits if h[0] > 0]
    print(f"{len(hits)} candidate(s)" +
          (f" ({len(named)} by name, rest county-only)" if inr else "") + ":")
    for s, x in hits[:15]:
        tag = f"  (name overlap {s} chars)" if s else ""
        print(f"  {_fmt(x)}{tag}")
        local = DOCS_DIR / f"{x['id']}.pdf"
        if local.exists():
            print(f"      local doc: {local.relative_to(BASE)}")
        if s:
            for d in _detail_rows(x["id"])[:2]:
                pct = "/".join(v for i in range(1, 11)
                               if (v := (d.get(f"Year {i} Abatement") or "").strip()))
                term = (d.get("Length of Abatement Term") or "").strip()
                if pct or term:
                    print(f"      abated %/yr: {pct or '?'}"
                          + (f" | term: {term}" if term else ""))
    if len(hits) > 15:
        print(f"  ... {len(hits) - 15} more (narrow with --name)")
    print(f"\nsearch UI (same data): {SEARCH_UI}\n"
          "verify a name hit as the SPV: puct.py match " + (inr or "<INR>") +
          " --key \"<owner>\" --dir <sources/>  (INR-in-PDF = confirmed).")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("refresh", help="both API tables + detail CSV -> data/reference/")
    sub.add_parser("archive", help="recover purged rows from Wayback snapshots (append-only)")
    sub.add_parser("harvest", help="download linked agreement PDFs -> data/reference/ch312_docs/")
    p = sub.add_parser("resolve", help="list Ch.312 abatements for an INR/county/name")
    p.add_argument("inr", nargs="?", default=None)
    p.add_argument("--county", default=None, help="county substring of lead unit/CAD (no INR)")
    p.add_argument("--name", default=None, help="free-text owner/zone substring (no INR)")
    a = ap.parse_args()

    if a.cmd == "refresh":
        refresh()
    elif a.cmd == "archive":
        archive()
    elif a.cmd == "harvest":
        harvest()
    elif a.cmd == "resolve":
        if not (a.inr or a.county or a.name):
            raise SystemExit("resolve needs an INR, --county, or --name")
        sys.exit(resolve(a.inr, a.county, a.name))


if __name__ == "__main__":
    main()
