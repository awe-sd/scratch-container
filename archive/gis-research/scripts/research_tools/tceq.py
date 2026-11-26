"""TCEQ air-permit applicants for thermal/gas queue projects — Central Registry resolver.

An NSR (New Source Review) air permit application names the operating SPV, so for a
gas/thermal queue project the TCEQ air permit is a direct SPV/owner lead. TCEQ's
Central Registry is published as UNGATED Socrata datasets on data.texas.gov
("Central Registry Files", split into 5 regional tables), queryable server-side with
SoQL. Fields used:
  reg_ent_name            facility / regulated-entity name
  re_phys_loc_addr_county COUNTY (the filter key)
  princ_legal_name        customer / owning entity = SPV candidate
  program_code            AIRNSR = air New Source Review, AIROP = operating,
                          AIREI = emissions inventory
  additional_id_text      permit / registration number (e.g. PSDTX1468, 87225)
  reg_ent_status_txt      status (ACTIVE / ...)

Each Texas county lives in exactly ONE regional table, so `resolve` does a LIVE,
county-scoped SoQL query (returns only that county's air entities — a few hundred
rows max). A full statewide air-permit BULK download (~300k rows) was rejected as too
heavy for data/reference/; instead `refresh` caches a small county->table routing map
so resolve hits the one right table.

Agent usage (run from repo root with `uv run`):
  tceq.py refresh                          build the county->table routing map (reference/)
  tceq.py resolve 28INR0108                county + name-token air-permit search for the INR
  tceq.py resolve --county Grayson --keyword Rayburn      no INR

A miss prints an explicit negative-evidence line.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
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
ROUTES = REF / "tceq_county_region.json"
API = "https://data.texas.gov/resource/{}.json"
DATASETS = {"North Texas": "5eqq-7nad", "Dallas/Fort Worth": "t34q-qzi3",
            "Central Texas": "msah-s2rv", "Coastal & East Texas": "tzyg-j7q4",
            "Border & Permian Basin": "9iad-hrn8"}
COUNTY_COL = "re_phys_loc_addr_county"

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) research-agent/1.0"}
_SYS_CA = "/etc/ssl/certs/ca-certificates.crt"
VERIFY = _SYS_CA if os.path.exists(_SYS_CA) else True
THROTTLE_LOCK = Path(tempfile.gettempdir()) / ".tceq_throttle.lock"
MIN_INTERVAL = 2.0
RETRIES = (5, 15, 45)
# tokens too generic to discriminate a facility by name
STOP = {"GAS", "ENERGY", "STATION", "POWER", "PLANT", "PROJECT", "CENTER", "CENTRE",
        "GENERATION", "GENERATING", "FACILITY", "LLC", "LP", "INC", "THE", "II", "III",
        "SOLAR", "WIND", "STORAGE", "BATTERY", "BESS", "DUE", "DILIGENCE", "TEF"}


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
            r = requests.get(url, headers=UA, timeout=90, verify=VERIFY, **kw)
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


# ---- refresh: county -> dataset routing map ------------------------------
def refresh() -> int:
    routes = {}
    for region, dsid in DATASETS.items():
        r = get(API.format(dsid), params={"$select": COUNTY_COL,
                                           "$group": COUNTY_COL, "$limit": "400"})
        for row in r.json():
            c = (row.get(COUNTY_COL) or "").strip().upper()
            if c:
                routes.setdefault(c, {"region": region, "dataset": dsid})
        print(f"  {region} ({dsid}): {len(r.json())} counties")
    REF.mkdir(parents=True, exist_ok=True)
    ROUTES.write_text(json.dumps({"source": "data.texas.gov Central Registry Files",
                                  "fetched": str(dt.date.today()),
                                  "datasets": DATASETS, "routes": routes}, indent=0))
    print(f"tceq routing: {len(routes)} counties -> {ROUTES}")
    return len(routes)


def _route(county: str) -> tuple[str, str, str]:
    """(dataset_id, region, provenance) for a county; probe live if no cached map."""
    cty = county.strip().upper()
    if ROUTES.exists():
        d = json.loads(ROUTES.read_text())
        hit = d.get("routes", {}).get(cty)
        if hit:
            return hit["dataset"], hit["region"], f"{ROUTES.name} (fetched {d.get('fetched')})"
    for region, dsid in DATASETS.items():
        r = get(API.format(dsid), params={COUNTY_COL: cty,
                                           "$select": "count(ref_num_txt)"})
        if r.json() and int(r.json()[0].get("count_ref_num_txt", 0)) > 0:
            return dsid, region, "live probe (no routing map cached)"
    return "", "", "live probe"


# ---- resolve -------------------------------------------------------------
def _tokens(name: str) -> list[str]:
    name = re.sub(r"\(.*?\)", " ", str(name))
    toks = [t for t in re.split(r"[^A-Za-z0-9]+", name.upper())
            if len(t) >= 4 and t not in STOP]
    return list(dict.fromkeys(toks))


def _queue_row(inr: str):
    import pandas as pd
    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    latest = df[df.fileDate == df.fileDate.max()]
    row = latest[latest.INR == inr]
    if row.empty:
        raise SystemExit(f"{inr} not in latest snapshot")
    return row.iloc[0]


# names that mark a generation/thermal facility — the fallback when the project name
# doesn't match, so we surface power plants (not gas stations / flea markets)
GEN_WORDS = ["POWER", "ENERGY", "GENERAT", "ELECTRIC", "COGEN", "TURBINE", "PEAK"]


def _query(dsid: str, county: str, tokens: list[str], cols=("reg_ent_name",
           "princ_legal_name"), limit: int = 200, program: str = "AIR") -> list[dict]:
    where = f"starts_with(program_code, '{program}')"
    if tokens:
        ors = " OR ".join(f"upper({c}) like '%{t}%'" for t in tokens for c in cols)
        where += f" AND ({ors})"
    r = get(API.format(dsid), params={COUNTY_COL: county.upper(),
                                      "$where": where, "$limit": str(limit)})
    return r.json()


def resolve(inr: str | None, county: str | None, keyword: str | None,
            program: str = "AIR") -> int:
    if inr:
        r = _queue_row(inr)
        county = str(r.county or "").strip()
        tokens = _tokens(r.projectName)
        print(f"{inr}  '{r.projectName}'  {county} Co  {r.capacityMw} MW  {r.fuel}/{r.technology}")
    else:
        tokens = _tokens(keyword) if keyword else []
    if not county:
        raise SystemExit("resolve needs an INR or --county")

    dsid, region, prov = _route(county)
    if not dsid:
        print(f"NEGATIVE EVIDENCE: county '{county}' not found in any TCEQ regional table.")
        return 0
    print(f"provenance: data.texas.gov {region} table {dsid}; routing via {prov}; "
          f"queried {dt.date.today()}. tokens={tokens or '(none — all AIR entities)'}")

    rows = _query(dsid, county, tokens, program=program)
    if not rows:
        rows = _query(dsid, county, GEN_WORDS, cols=("reg_ent_name",), program=program)
        print(f"  (no '{'/'.join(tokens) or '<name>'}' hit; showing generation-type "
              f"AIR facilities in {county} County — POWER/ENERGY/ELECTRIC/...)")
    if not rows:
        print(f"NEGATIVE EVIDENCE: no name-matched or generation-type AIR entity in "
              f"{county} County. For a very new queue project the SPV may not have filed "
              "an NSR permit yet (airPermit often 'Not Required'/pending) — negative evidence.")
        return 0

    # The flat Central Registry view cross-joins a regulated entity's program IDs against
    # ALL its customer affiliations, so a permit# is NOT tied to one owner — decouple into
    # distinct facilities, distinct AIR permits, and distinct owner (SPV) candidates.
    facilities = sorted({(x.get("reg_ent_name"), x.get("reg_ent_status_txt")) for x in rows})
    permits = sorted({(x.get("program_code"), x.get("additional_id_text")) for x in rows
                      if x.get("additional_id_text")})
    owners = sorted({x.get("princ_legal_name") for x in rows if x.get("princ_legal_name")})

    def _cap(items, n):
        extra = len(items) - n
        return items[:n], (f"  ... (+{extra} more)" if extra > 0 else None)

    fac, fx = _cap(facilities, 40)
    print(f"facilities ({len(facilities)}): " + "; ".join(f"{n} [{s}]" for n, s in fac))
    if fx:
        print(fx)
    perm, px = _cap(permits, 60)
    print(f"AIR permits/registrations ({len(permits)}): "
          + ", ".join(f"{p} #{i}" for p, i in perm) + (px or ""))
    own, ox = _cap(owners, 40)
    print(f"owner / customer legal names ({len(owners)}) — SPV candidates:")
    for o in own:
        print(f"  {o}")
    if ox:
        print(ox)
    print("\nNOTE: an existing facility of the same name may be a co-located PREDECESSOR "
          "(different owner) — treat owners as leads, not confirmation. Permit# and owner "
          "are separate affiliations of the entity, not paired.")
    print("verify the SPV: puct.py match " + (inr or "<INR>") +
          " --key \"<owner or entity>\" --dir <sources/>  (INR-in-PDF = confirmed).")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("refresh", help="cache the county->regional-table routing map")
    p = sub.add_parser("resolve", help="air-permit applicants for an INR / county")
    p.add_argument("inr", nargs="?", default=None)
    p.add_argument("--county", default=None, help="county (no INR)")
    p.add_argument("--keyword", default=None, help="name tokens to match (with --county)")
    p.add_argument("--storm", action="store_true",
                   help="search construction-STORMWATER NOIs instead of air permits: "
                        "EVERY >1-acre construction site files one (names the EPC, site "
                        "address, start date) — THE construction-started proof for solar "
                        "(Cachena/Clear Fork lesson 2026-07-20)")
    a = ap.parse_args()
    if a.cmd == "refresh":
        refresh()
    elif a.cmd == "resolve":
        if not (a.inr or a.county):
            raise SystemExit("resolve needs an INR or --county")
        sys.exit(resolve(a.inr, a.county, a.keyword,
                         program="STORM" if a.storm else "AIR"))


if __name__ == "__main__":
    main()
