"""Systematic SPV/developer resolution for a queue project — bulk sources, no guessing.

The ERCOT GIS report does NOT publish the interconnecting entity, and queue names are
often codenames ("Operation Sunshine") or spelled differently from the legal SPV
("Shepard" vs "Sheppard"). This tool resolves candidates from two systematic sources:

1. EIA-860M planned/operating inventory (data/reference/eia860m_latest.xlsx):
   deterministic join on state=TX + county + prime-mover compatibility + MW tolerance
   (or plant-name/queue-name substring either way). Yields Entity Name (the operating
   company, usually the SPV or its developer), plant lat/lon, EIA status, planned COD.
2. The local PUCT IA-docket index (built by `puct.py index`): filing descriptions have
   the shape "... between <TSP> and <SPV, LLC> (<alias>)" — the non-TSP party is an SPV
   candidate whenever the queue name appears anywhere in the description, or the
   parenthetical alias matches the queue name.

Every candidate prints with its provenance. VERIFY before citing:
  uv run gis-research/scripts/research_tools/puct.py match <INR> --key "<candidate>" --dir <sources/>
(INR-in-PDF = confirmed). Candidates are leads, not conclusions.

Usage:
  uv run gis-research/scripts/research_tools/spv.py resolve 26INR0255
  uv run gis-research/scripts/research_tools/spv.py resolve 26INR0255 --mw-tol 0.10
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]  # gis-research/
EIA_FILE = BASE / "data" / "reference" / "eia860m_latest.xlsx"
INDEX_FILE = BASE / "research" / "_reference" / "puct_ia_docket_index.json"

# queue technology code -> compatible EIA prime-mover codes
PM_COMPAT = {"PV": {"PV"}, "WT": {"WT"}, "BA": {"BA", "ES"},
             "CC": {"CA", "CT", "CS", "CC"}, "GT": {"GT", "CT"},
             "IC": {"IC"}, "ST": {"ST", "CA"}}

# recognized transmission/utility parties — the OTHER side of an IA is the SPV
TSP_WORDS = re.compile(
    r"oncor|electric transmission texas|centerpoint|cehe|aep texas|lcra|"
    r"texas.new mexico|tnmp|lone star transmission|wind energy transmission|wett|"
    r"cross texas|ctt\b|brazos electric|cps energy|city public service|"
    r"south texas electric|stec|sharyland|garland|rayburn country|austin energy|"
    r"city of |denton|bryan texas utilities|greenville|kerrville|brownsville", re.I)


def queue_row(inr: str):
    import pandas as pd
    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    latest = df[df.fileDate == df.fileDate.max()]
    row = latest[latest.INR == inr]
    if row.empty:
        raise SystemExit(f"{inr} not in latest snapshot")
    return row.iloc[0]


def from_eia860m(r, mw_tol: float) -> list[dict]:
    import pandas as pd
    if not EIA_FILE.exists():
        print(f"  [no {EIA_FILE} — download EIA-860M and place it there]")
        return []
    out = []
    qname = re.sub(r"\s*\(.*\)\s*$", "", str(r.projectName)).strip().lower()
    compat = PM_COMPAT.get(str(r.technology).upper(), None)
    for sheet in ("Planned", "Operating"):
        df = pd.read_excel(EIA_FILE, sheet_name=sheet, skiprows=2)
        tx = df[(df["Plant State"] == "TX")].copy()
        tx = tx[tx["County"].astype(str).str.strip().str.lower()
                == str(r.county).strip().lower()]
        if compat:
            tx = tx[tx["Prime Mover Code"].astype(str).str.upper().isin(compat)]
        # aggregate units to plant level (multi-unit plants list one row per generator)
        for pid, g in tx.groupby("Plant ID"):
            plant = str(g["Plant Name"].iloc[0])
            mw = g["Nameplate Capacity (MW)"].sum()
            name_hit = (qname and (qname in plant.lower() or plant.lower() in qname))
            mw_hit = abs(mw - float(r.capacityMw)) <= max(1.0, mw_tol * float(r.capacityMw))
            if not (name_hit or mw_hit):
                continue
            out.append({
                "source": f"eia860m/{sheet}",
                "why": ("plant-name match" if name_hit else
                        f"county+prime-mover+MW within {mw_tol:.0%}"),
                "entity": str(g["Entity Name"].iloc[0]),
                "plant": plant, "mw": round(float(mw), 1),
                "status": str(g["Status"].iloc[0])[:60] if "Status" in g else "",
                "lat": round(float(g["Latitude"].iloc[0]), 5) if pd.notna(g["Latitude"].iloc[0]) else None,
                "lon": round(float(g["Longitude"].iloc[0]), 5) if pd.notna(g["Longitude"].iloc[0]) else None,
                "planned": (f"{int(g['Planned Operation Year'].iloc[0])}-"
                            f"{int(g['Planned Operation Month'].iloc[0]):02d}"
                            if sheet == "Planned" and pd.notna(g["Planned Operation Year"].iloc[0]) else ""),
            })
    return out


def from_puct_index(r) -> list[dict]:
    if not INDEX_FILE.exists():
        print("  [no docket index — run `puct.py index` first]")
        return []
    idx = json.loads(INDEX_FILE.read_text())["filings"]
    qname = re.sub(r"\s*\(.*\)\s*$", "", str(r.projectName)).strip().lower()
    out = []
    for f in idx:
        desc = f["description"]
        if qname not in desc.lower():
            continue
        # split "between X and Y" and take the non-TSP side as the SPV candidate
        m = re.search(r"between\s+(.{3,80}?)\s+and\s+(.{3,80}?)(?:\s*\(|,?\s*$|\s+for\b)",
                      desc, re.I)
        spv = None
        if m:
            a, b = m.group(1).strip(), m.group(2).strip()
            spv = b if TSP_WORDS.search(a) else a if TSP_WORDS.search(b) else None
        out.append({"source": "puct-index", "item": f["item"], "filed": f["filed"],
                    "why": "queue name in filing description",
                    "entity": spv or "(parse failed — read description)",
                    "desc": desc[:110]})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("resolve", help="list SPV/developer candidates for an INR")
    p.add_argument("inr")
    p.add_argument("--mw-tol", type=float, default=0.05,
                   help="MW tolerance as a fraction for the EIA join (default 5%%)")
    a = ap.parse_args()

    r = queue_row(a.inr)
    print(f"{a.inr}  '{r.projectName}'  {r.county} Co  {r.capacityMw} MW  "
          f"{r.fuel}/{r.technology}")
    cands = from_eia860m(r, a.mw_tol) + from_puct_index(r)
    if not cands:
        print("no systematic candidate. Remaining sources are fuel-specific registries "
              "(FAA OE/AAA sponsors for wind, TCEQ permit applicants for thermal, "
              "Ch.313/JETI applicants for solar) and TX SOS/Comptroller entity search — "
              "record whatever SPV you find in triage_findings.json spv_name.")
        return
    for c in cands:
        line = f"  [{c['source']}] {c['entity']}  ({c['why']})"
        if c.get("plant"):
            line += f"  plant='{c['plant']}' {c['mw']} MW"
        if c.get("planned"):
            line += f" planned={c['planned']}"
        if c.get("lat"):
            line += f" @ {c['lat']},{c['lon']}"
        if c.get("item"):
            line += f"  filing 35077-{c['item']} {c['filed']}: {c['desc']}"
        print(line)
    print("\nverify a candidate: puct.py match " + a.inr +
          " --key \"<entity>\" --dir <sources/>  (INR-in-PDF = confirmed)")


if __name__ == "__main__":
    main()
