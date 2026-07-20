"""Texas Comptroller Chapter 312 abatement registry — bulk resolver (counties/cities).

Why this exists: Ch.313 (school value limitations) EXPIRED 2022-12-31 and JETI has only
~38 applications so far — but COUNTY/CITY property-tax abatements under Tax Code Ch.312
continued uninterrupted and are the abatement most post-2022 queue projects actually
sign (e.g. the Hood/Somervell "Yellow Viking" abatements and Deaf Smith's 2024 solar
abatements were all Ch.312 agreements we previously saw only via news stories). The
Comptroller publishes a registry of ~1,400 abatements via the same open-data API family
as JETI:
    api.comptroller.texas.gov/open-data/v1/tables/ch312-abatement
with bulk CSVs (summary + per-year detail) on assets.comptroller.texas.gov.

Unlike Ch.313/JETI (school district only), Ch.312 rows carry a DIRECT county signal:
"Lead Taxing Unit Name" ("Deaf Smith County") and "CAD Name" ("Hunt CAD"). Rows also
carry the Reinvestment Zone name (often contains the project name) and the property
owner (often the SPV's legal name) — two independent name-join keys.

COVERAGE CAVEAT (document in findings, do not over-claim): the registry is populated by
CAD submissions on an ANNUAL cycle (most rows stamped each December), some counties do
not report at all (Somervell, Matagorda, Crockett had 0 rows as of 2026-07), and records
are purged ~3 years after expiration. A MISS here is therefore WEAK negative evidence —
"not in the Ch.312 registry" ≠ "no abatement exists". A HIT is strong: it names the SPV,
the reinvestment zone, status, dates, base value, and per-year abatement percentages.

Agent usage (run from repo root with `uv run`):
  ch312.py refresh
      Download the summary + detail CSVs into gis-research/data/reference/.
  ch312.py resolve 23INR0057
      Read the queue row, match owner/zone names against the project name AND list all
      abatements whose lead-taxing-unit/CAD contains the queue county.
  ch312.py resolve --county "Deaf Smith"   every abatement for that county
  ch312.py resolve --name "Mule Deer"      free-text owner/zone substring

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
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parents[2]  # gis-research/
REF = BASE / "data" / "reference"
SUMMARY_CSV = "https://assets.comptroller.texas.gov/open-data-files/ch312-abatement.csv"
DETAIL_CSV = "https://assets.comptroller.texas.gov/open-data-files/ch312-abatement-detail.csv"
SEARCH_UI = "https://comptroller.texas.gov/economy/development/search-tools/ch312/abatements-simple.php"
CH312_FILE = REF / "ch312_abatements.json"
CH312_DETAIL_FILE = REF / "ch312_abatements_detail.csv"

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) research-agent/1.0"}
_SYS_CA = "/etc/ssl/certs/ca-certificates.crt"
VERIFY = _SYS_CA if os.path.exists(_SYS_CA) else True

GENERIC_TAIL = re.compile(
    r"\s*,?\s+(LLC|L\.L\.C\.|Inc\.?|LP|L\.P\.|Ltd\.?|Corp\.?|Co\.?|Holdings|"
    r"BESS|Solar|Wind|Storage|Battery|Batteries|Energy|Center|Centre|Project|"
    r"Hybrid|Power|Station|Facility|Farm|Park|[IVX]+|\d+)$", re.I)


# ---- refresh -------------------------------------------------------------
def refresh() -> int:
    r = requests.get(SUMMARY_CSV, headers=UA, timeout=120, verify=VERIFY)
    r.raise_for_status()
    rows = list(csv.DictReader(io.StringIO(r.content.decode("utf-8", "replace"))))
    REF.mkdir(parents=True, exist_ok=True)
    CH312_FILE.write_text(json.dumps(
        {"source": SUMMARY_CSV, "fetched": str(dt.date.today()), "rows": rows}, indent=0))
    print(f"ch312: {len(rows)} abatements -> {CH312_FILE}")

    r = requests.get(DETAIL_CSV, headers=UA, timeout=120, verify=VERIFY)
    r.raise_for_status()
    CH312_DETAIL_FILE.write_bytes(r.content)
    print(f"ch312 detail: {len(r.content)/1024:.0f} KB -> {CH312_DETAIL_FILE}")
    return len(rows)


# ---- matching (same conventions as ch313.py) ------------------------------
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


def _score(qname: str, candidate: str) -> int:
    """Longest exact-substring overlap (either direction); 0 = no match."""
    cl = candidate.lower()
    best = max((len(k) for k in _cores(qname) if k.lower() in cl), default=0)
    c_core = GENERIC_TAIL.sub("", re.sub(r",\s*$", "", candidate)).strip().lower()
    if len(c_core) >= 8 and c_core in qname.lower():
        best = max(best, len(c_core))
    return best


def _load() -> tuple[dict, list]:
    if not CH312_FILE.exists():
        print("  [no Ch.312 list — run `ch312.py refresh` first]")
        return {}, []
    d = json.loads(CH312_FILE.read_text())
    return d, d.get("rows", [])


def _queue_row(inr: str):
    import pandas as pd
    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    latest = df[df.fileDate == df.fileDate.max()]
    row = latest[latest.INR == inr]
    if row.empty:
        raise SystemExit(f"{inr} not in latest snapshot")
    return row.iloc[0]


def _detail_rows(record_id: str) -> list[dict]:
    if not CH312_DETAIL_FILE.exists():
        return []
    with CH312_DETAIL_FILE.open(newline="", encoding="utf-8", errors="replace") as fh:
        return [r for r in csv.DictReader(fh) if r.get("Record ID") == record_id]


def _fmt(a: dict) -> str:
    return (f"[Ch.312 #{a['Record ID']}] owner: {a['Property Owner(s) Name']}"
            f" | zone: {a['Reinvestment Zone Name']}"
            f" | lead unit: {a['Lead Taxing Unit Name']} ({a['CAD Name (Reporting Entity)']})"
            f" | {a['Abatement Status']} | base value ${a['Base Value of Abated Property']}"
            f" | submitted {a['Submission Date']}")


# ---- resolve -------------------------------------------------------------
def resolve(inr: str | None, county: str | None, name: str | None) -> int:
    meta, rows = _load()
    if not rows:
        return 1
    print(f"provenance: Ch.312 {CH312_FILE.name} (fetched {meta.get('fetched','?')}, "
          f"{len(rows)} rows). Source: comptroller.texas.gov open-data (CAD-submitted, "
          "annual cycle — a MISS is weak negative evidence, see tool docstring)")

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

    def county_hit(a: dict, co: str) -> bool:
        co = co.lower()
        return (co in (a["Lead Taxing Unit Name"] or "").lower()
                or co in (a["CAD Name (Reporting Entity)"] or "").lower())

    hits = []  # (score, row)
    for a in rows:
        owner = a.get("Property Owner(s) Name") or ""
        zone = a.get("Reinvestment Zone Name") or ""
        if qname:
            s = max(_score(qname, owner), _score(qname, zone))
            if s:
                hits.append((s, a))
                continue
        if inr and qcounty and county_hit(a, qcounty):
            hits.append((0, a))
        elif county and not qname and county_hit(a, county):
            hits.append((0, a))

    hits.sort(key=lambda x: -x[0])
    if not hits:
        who = f"'{qname}'" if qname else f"county '{qcounty}'"
        print(f"NEGATIVE EVIDENCE (WEAK): no Ch.312 registry row matches {who}. Because "
              "the registry is CAD-submitted on an annual cycle with incomplete county "
              "coverage, this does NOT rule out an abatement — check commissioners-court "
              "minutes / local news (search.py) before recording absence.")
        return 0

    named = [h for h in hits if h[0] > 0]
    print(f"{len(hits)} candidate(s)" +
          (f" ({len(named)} by name, rest county-only)" if inr else "") + ":")
    for s, a in hits[:15]:
        tag = f"  (name overlap {s} chars)" if s else ""
        print(f"  {_fmt(a)}{tag}")
        if s:  # detail (per-year percentages) only for name matches
            for d in _detail_rows(a["Record ID"])[:2]:
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
    sub.add_parser("refresh", help="download Ch.312 summary+detail CSVs into data/reference/")
    p = sub.add_parser("resolve", help="list Ch.312 abatements for an INR/county/name")
    p.add_argument("inr", nargs="?", default=None)
    p.add_argument("--county", default=None, help="county substring of lead unit/CAD (no INR)")
    p.add_argument("--name", default=None, help="free-text owner/zone substring (no INR)")
    a = ap.parse_args()

    if a.cmd == "refresh":
        refresh()
    elif a.cmd == "resolve":
        if not (a.inr or a.county or a.name):
            raise SystemExit("resolve needs an INR, --county, or --name")
        sys.exit(resolve(a.inr, a.county, a.name))


if __name__ == "__main__":
    main()
