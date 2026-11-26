"""FAA OE/AAA obstruction cases for WIND queue projects — sponsor / turbine resolver.

Wind sponsors file one FAA Obstruction Evaluation (OE/AAA) case PER TURBINE; the
sponsor IS the SPV/developer and each case carries the exact turbine lat/lon, so a
contiguous block of ~N wind-turbine cases in one county cluster = one wind farm.

*** NO PUBLIC PROGRAMMATIC PATH IS AVAILABLE AS OF 2026-07 (verified this build): ***
  - The USDOT open-data mirror of "OE/AAA Determined Cases" (Socrata dataset
    rkqu-p2bk on datahub.transportation.gov) is now PRIVATE: every API/CSV call
    returns HTTP 403 "You must be logged in to access this resource", and the dataset
    no longer appears in the public catalog. A Socrata app token does NOT help — the
    dataset is access-gated, not rate-gated.
  - The oeaaa.faa.gov external portal (case search AND case detail) is disabled by a
    government-funding lapse: every external URL returns one uniform notice page.
  - Even when up, the FAA public case API does NOT expose the sponsor name per case;
    sponsor is attributed from location + filing date + turbine count (this is how the
    Monarch Creek cluster of ~86 cases was attributed to EDF Renewables).

So this tool runs off a LOCAL CACHE and degrades to actionable deep-links:
  faa.py refresh
      Try the Socrata bulk (TX + Wind Turbine) into data/reference/faa_oe_cases_tx.json.
      On the 403 gate it says so, and instead ingests any prior FAA case pulls found
      under data/ (e.g. a per-project *_faa_oe_aaa.json) into the cache so resolve works.
  faa.py resolve 21INR0263
      Read the queue row (must be wind), filter the cache to TX wind-turbine cases
      inside the project county's bounding box (from assets/tx_counties.geojson, so a
      farm straddling a county line is captured), and print sponsors, case numbers
      (ASN), filing years, and the turbine coordinate centroid. Empty cache -> explicit
      negative evidence PLUS the oeaaa/datahub deep-link URLs to WebFetch once access
      returns, plus the wind ASN pattern (YYYY-WTW-NNNNN).
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import glob
import json
import os
import re
import statistics
import sys
import tempfile
import time
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parents[2]  # gis-research/
REF = BASE / "data" / "reference"
CACHE = REF / "faa_oe_cases_tx.json"
GEOJSON = BASE / "assets" / "tx_counties.geojson"
SOCRATA = "https://datahub.transportation.gov/resource/rkqu-p2bk.json"
OEAAA_SEARCH = "https://oeaaa.faa.gov/oeaaa/external/searchAction.jsp?action=showSearchForm"

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) research-agent/1.0"}
_SYS_CA = "/etc/ssl/certs/ca-certificates.crt"
VERIFY = _SYS_CA if os.path.exists(_SYS_CA) else True
THROTTLE_LOCK = Path(tempfile.gettempdir()) / ".faa_throttle.lock"
MIN_INTERVAL = 2.0
RETRIES = (5, 15, 45)
BBOX_BUFFER = 0.15  # deg (~13 km) — captures turbines just across the county line


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
            time.sleep(backoff)
            continue
        return r  # caller inspects status (403 gate is a finding, not an error)
    raise RuntimeError("unreachable")


# ---- cache normalization -------------------------------------------------
def _norm_case(rec: dict, sponsor: str, source: str) -> dict | None:
    """Coerce one case record to {asn,sponsor,structure,state,county,lat,lon,status,filed}."""
    def g(*keys):
        for k in keys:
            if rec.get(k) not in (None, ""):
                return rec[k]
        return None
    lat, lon = g("lat", "latitude", "lat_dec"), g("lon", "longitude", "long_dec")
    if lat is None or lon is None:
        return None
    return {"asn": g("asn", "oe_id", "study", "aeronautical_study_number") or "?",
            "sponsor": g("sponsor", "sponsor_name") or sponsor,
            "structure": (g("structure_type", "structure") or "Wind Turbine"),
            "state": (g("state", "state_filed") or "TX"),
            "county": (g("county") or "").upper(),
            "lat": float(lat), "lon": float(lon),
            "status": g("status", "final_decision") or "",
            "filed": str(g("filed", "date_accepted", "entered_date") or "")[:10],
            "src": source}


def load_cache() -> list[dict]:
    """Reference cache + any per-project *_faa_oe*.json pulls under data/."""
    cases: list[dict] = []
    if CACHE.exists():
        for rec in json.loads(CACHE.read_text()).get("cases", []):
            n = _norm_case(rec, rec.get("sponsor", ""), rec.get("src", CACHE.name))
            if n:
                cases.append(n)
    for path in glob.glob(str(BASE / "data" / "*faa_oe*.json")):
        try:
            d = json.loads(Path(path).read_text())
        except Exception:
            continue
        sponsor = " / ".join(x for x in (d.get("developer"), d.get("llc")) if x) \
            or d.get("project", Path(path).stem)
        for t in d.get("turbines", d.get("cases", [])):
            n = _norm_case(t, sponsor, Path(path).name)
            if n:
                cases.append(n)
    # dedupe by ASN — a sponsor-attributed record beats an unattributed one (live
    # Socrata cases carry no sponsor; per-project pulls do)
    best: dict[str, dict] = {}
    for c in cases:
        prev = best.get(c["asn"])
        if prev is None or (not prev["sponsor"] and c["sponsor"]):
            best[c["asn"]] = c
    return list(best.values())


def county_bbox(county: str):
    if not GEOJSON.exists():
        return None
    d = json.loads(GEOJSON.read_text())
    for f in d["features"]:
        if str(f["properties"].get("NAME", "")).lower() == county.lower():
            xs, ys = [], []
            def walk(c):
                if c and isinstance(c[0], (int, float)):
                    xs.append(c[0]), ys.append(c[1])
                else:
                    for x in c:
                        walk(x)
            walk(f["geometry"]["coordinates"])
            return (min(xs) - BBOX_BUFFER, min(ys) - BBOX_BUFFER,
                    max(xs) + BBOX_BUFFER, max(ys) + BBOX_BUFFER)
    return None


# ---- refresh -------------------------------------------------------------
def refresh() -> int:
    REF.mkdir(parents=True, exist_ok=True)
    where = ("upper(structure_type) like '%WIND TURBINE%' and "
             "(state='TX' or state_filed='TX')")
    live = []
    try:
        r = get(SOCRATA, params={"$where": where, "$limit": "50000"})
        if r.status_code == 200:
            live = r.json()
            print(f"socrata OK: {len(live)} TX wind-turbine cases")
        else:
            print(f"socrata BLOCKED: HTTP {r.status_code} — {r.text[:80]!r}. "
                  "The OE/AAA Determined-Cases dataset is private (login required); "
                  "an app token cannot unlock it. Falling back to local pulls.")
    except Exception as e:
        print(f"socrata unreachable ({e.__class__.__name__}); falling back to local pulls.")
    ingested = load_cache()  # this already merges data/*faa_oe*.json
    cases = live + [c for c in ingested if not live]
    payload = {"source": SOCRATA if live else "ingested local data/*faa_oe*.json pulls",
               "fetched": str(dt.date.today()),
               "note": "live=Socrata determined cases; else prior FAA pulls (sponsor "
                       "attributed, not per-case)", "cases": cases}
    CACHE.write_text(json.dumps(payload, indent=0))
    print(f"faa cache: {len(cases)} cases -> {CACHE}")
    return len(cases)


# ---- resolve -------------------------------------------------------------
def _queue_row(inr: str):
    import pandas as pd
    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    latest = df[df.fileDate == df.fileDate.max()]
    row = latest[latest.INR == inr]
    if row.empty:
        raise SystemExit(f"{inr} not in latest snapshot")
    return row.iloc[0]


def _deeplinks(county: str) -> None:
    from urllib.parse import quote
    dh = (SOCRATA + "?$where=" + quote(
        f"upper(structure_type) like '%WIND TURBINE%' and state='TX' and "
        f"upper(county)='{county.upper()}'"))
    print("  no case in local cache. Next steps once access is restored:")
    print(f"    - datahub (needs login): {dh}")
    print(f"    - oeaaa case search (currently shutdown-disabled): {OEAAA_SEARCH}")
    print("      search state=TX, county=" + county + ", structure=Wind Turbine, "
          "recent dates; wind ASNs look like 2024-WTW-NNNNN.")
    print("    - sponsor is NOT a per-case FAA field: attribute by the county+date "
          "cluster (a contiguous ASN block filed together = one farm's SPV).")


def resolve(inr: str) -> int:
    r = _queue_row(inr)
    county = str(r.county or "").strip()
    is_wind = str(r.fuel).upper().startswith("WIN") or str(r.technology).upper() == "WT"
    print(f"{inr}  '{r.projectName}'  {county} Co  {r.capacityMw} MW  {r.fuel}/{r.technology}")
    if not is_wind:
        print("  [not a wind project — OE/AAA per-turbine cases only exist for wind]")
    cases = load_cache()
    src = "reference cache + data/*faa_oe*.json"
    print(f"provenance: {src} ({len(cases)} TX cases loaded). Live FAA sources verified "
          "blocked 2026-07 (datahub private + oeaaa shutdown).")
    if not cases:
        print("NEGATIVE EVIDENCE: local FAA cache is empty (run `faa.py refresh`).")
        _deeplinks(county)
        return 0

    bbox = county_bbox(county)
    if bbox:
        x0, y0, x1, y1 = bbox
        hit = [c for c in cases if "WIND" in c["structure"].upper()
               and x0 <= c["lon"] <= x1 and y0 <= c["lat"] <= y1]
        how = f"within {county} county bbox (+{BBOX_BUFFER} deg buffer)"
    else:
        hit = [c for c in cases if "WIND" in c["structure"].upper()
               and c["county"] == county.upper()]
        how = f"county == {county} (no geojson bbox available)"

    if not hit:
        print(f"NEGATIVE EVIDENCE: no TX wind-turbine case {how}.")
        _deeplinks(county)
        return 0

    sponsors = sorted({c["sponsor"] for c in hit if c["sponsor"]})
    asns = sorted(c["asn"] for c in hit if c["asn"] != "?")
    years = sorted({c["filed"][:4] for c in hit if c["filed"]})
    counties = sorted({c["county"] for c in hit if c["county"]})
    clat = round(statistics.fmean(c["lat"] for c in hit), 5)
    clon = round(statistics.fmean(c["lon"] for c in hit), 5)
    print(f"{len(hit)} wind-turbine case(s) {how}:")
    print(f"  sponsor(s): {', '.join(sponsors) or '(unattributed)'}  "
          "[attributed by cluster, not a per-case FAA field]")
    if asns:
        print(f"  ASN range: {asns[0]} .. {asns[-1]}  ({len(asns)} numbered)")
    print(f"  filing year(s): {', '.join(years) or '?'}  | counties spanned: {', '.join(counties)}")
    print(f"  turbine centroid: {clat}, {clon}")
    print("\nverify the sponsor as the SPV: puct.py match " + inr +
          " --key \"<sponsor>\" --dir <sources/>  (INR-in-PDF = confirmed).")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("refresh", help="build the TX wind-case cache (Socrata or local pulls)")
    p = sub.add_parser("resolve", help="wind sponsors/turbines for an INR")
    p.add_argument("inr")
    a = ap.parse_args()
    if a.cmd == "refresh":
        refresh()
    elif a.cmd == "resolve":
        sys.exit(resolve(a.inr))


if __name__ == "__main__":
    main()
