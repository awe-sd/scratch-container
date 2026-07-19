"""EIA-860M reported history for one queue project — the independent 2nd source.

The ERCOT GIS queue holds what the DEVELOPER reports to ERCOT; EIA-860M holds what the
operating entity reports to EIA, monthly. Comparing the two histories (planned COD,
capacity, status) catches stale queue claims — e.g. queue says COD 2026-08 while EIA has
reported "under construction, ≤50%, planned 2027-05" for seven straight months.

Data: gis-research/data/eia_generator_tx.parquet — TX slice of AW.dbo.eiaGenerator
(monthly snapshots, 2022-04 →), denormalized with plant/entity/status lookups. Refresh with
`eia_snapshot.py`. The slice also carries MWh storage energy capacity, coordinates, and
county (all from the DB) — surfaced here as an additive cross-check.

Signals reported (all deterministic, no fuzzy matching):
  planned COD / capacity MW / status  — monthly change-point histories (as before)
  energy capacity MWh                 — for storage; from nameplateEnergyCapacity
  operating date                      — EIA's actual in-service date once the unit flips to OP
  DROPPED_FROM_860M                   — the matched plant/units vanished from the newest
                                        snapshot: a strong withdrawal/cancellation signal
                                        (presence/absence by (plantId, generatorId) key)

Usage (agents: run from repo root with `uv run`):
  eia_history.py 24INR0281                 # locate plant by name/county+MW, print history
  eia_history.py 24INR0281 --plant-id 66043   # explicit plant, skip matching
  eia_history.py 24INR0281 --write         # also write <proj_dir>/eia_history.json

Plant matching is deterministic (same rules as spv.py): queue-name/plant-name substring
either way, or county+prime-mover+MW within 5%. Multiple candidates are LISTED, never
guessed — re-run with --plant-id.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]  # gis-research/
GEN_PQ = BASE / "data" / "eia_generator_tx.parquet"

PM_COMPAT = {"PV": {"PV"}, "WT": {"WT"}, "BA": {"BA", "ES"},
             "CC": {"CA", "CT", "CS", "CC"}, "GT": {"GT", "CT"},
             "IC": {"IC"}, "ST": {"ST", "CA"}}


def load_queue_latest() -> pd.DataFrame:
    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    return df[df.fileDate == df.fileDate.max()]


def queue_row(inr: str, latest: pd.DataFrame | None = None):
    """Latest-snapshot queue row for an INR, or None if absent (does not raise)."""
    if latest is None:
        latest = load_queue_latest()
    row = latest[latest.INR == inr]
    return None if row.empty else row.iloc[0]


def plant_county_map() -> dict[int, str]:
    """plantId -> county, from the 860M workbook. Kept as the matching source for byte-exact
    backward compatibility; eiaGenerator now also carries county but is NOT used for matching."""
    xlsx = BASE / "data" / "reference" / "eia860m_latest.xlsx"
    if not xlsx.exists():
        return {}
    out = {}
    for sheet in ("Planned", "Operating"):
        df = pd.read_excel(xlsx, sheet_name=sheet, skiprows=2,
                           usecols=["Plant ID", "County", "Plant State"])
        for t in df[df["Plant State"] == "TX"].itertuples():
            try:
                out[int(t._1)] = str(t.County).strip().lower()
            except (ValueError, TypeError):
                continue
    return out


def find_plant(gen: pd.DataFrame, r, county_map: dict | None = None) -> list[tuple[int, str, str]]:
    """Candidate (plantId, plantName, why) — deterministic rules only.
    A name match beats everything; the MW rule needs the county to agree too."""
    latest = gen[gen.reportDate == gen.reportDate.max()]
    qname = re.sub(r"\s*\(.*\)\s*$", "", str(r.projectName)).strip().lower()
    compat = PM_COMPAT.get(str(r.technology).upper())
    county = plant_county_map() if county_map is None else county_map
    qcounty = str(r.county).strip().lower()
    named, by_mw = {}, {}
    for pid, g in latest.groupby("plantId"):
        pname = str(g.eiaPlantName.iloc[0])
        if qname in pname.lower() or pname.lower() in qname:
            named[pid] = (pname, "name match")
            continue
        if county.get(int(pid)) != qcounty:
            continue
        if compat and not g.primeMoverCode.astype(str).str.upper().isin(compat).any():
            continue
        mw = g.nameplateCapacity.sum()
        if abs(mw - float(r.capacityMw)) <= max(1.0, 0.05 * float(r.capacityMw)):
            by_mw[pid] = (pname, f"county+prime-mover+MW within 5% ({mw:g} vs {r.capacityMw:g})")
    out = named or by_mw
    return [(pid, n, why) for pid, (n, why) in out.items()]


def change_points(hist: pd.DataFrame, col_fn) -> list[dict]:
    """Collapse a monthly series into value-change intervals."""
    rows = []
    for rd, g in hist.groupby("reportDate"):
        rows.append((str(rd)[:10], col_fn(g)))
    out = []
    for rd, val in rows:
        if not out or out[-1]["value"] != val:
            out.append({"value": val, "from": rd, "to": rd})
        else:
            out[-1]["to"] = rd
    return out


def _ym(y, m):
    return f"{int(y)}-{int(m):02d}" if pd.notna(y) and y else None


def drop_signal(hist: pd.DataFrame, dataset_latest) -> dict | None:
    """Detect a plant/unit that has vanished from the newest snapshot — deterministic
    presence/absence by (plantId, generatorId) key (no name matching). Returns None when
    every unit of the plant is still present in the latest snapshot.

    scope='plant'  the whole plant is gone from the latest snapshot (strong cancellation);
    scope='units'  the plant still reports, but some units dropped (partial withdrawal, e.g.
                   a BESS unit removed from a solar+storage plant, or a retirement).
    All date comparisons are date-object vs date-object (never date vs string)."""
    plant_last = hist.reportDate.max()
    per_gen_last = hist.groupby("generatorId").reportDate.max()

    def unit_rows(gids):
        rows = []
        for gid in gids:
            ld = per_gen_last[gid]
            st = hist[(hist.generatorId == gid) & (hist.reportDate == ld)]
            rows.append({"generator_id": str(gid), "last_seen": str(ld)[:10],
                         "last_status": str(st.eiaStatus.iloc[0]) if len(st) else None})
        return sorted(rows, key=lambda d: d["generator_id"])

    if plant_last < dataset_latest:  # entire plant absent from the latest snapshot
        return {"scope": "plant", "last_seen": str(plant_last)[:10],
                "dataset_latest": str(dataset_latest)[:10],
                "dropped_units": unit_rows(list(per_gen_last.index))}

    dropped = [gid for gid, ld in per_gen_last.items() if ld < dataset_latest]
    if not dropped:
        return None
    return {"scope": "units",
            "last_seen": str(max(per_gen_last[g] for g in dropped))[:10],
            "dataset_latest": str(dataset_latest)[:10],
            "dropped_units": unit_rows(dropped)}


def build_record(inr: str, r, gen: pd.DataFrame, pid: int, why: str) -> dict:
    """The eia_history.json payload for a resolved (INR -> plant) match."""
    hist = gen[gen.plantId == pid].sort_values("reportDate")
    dataset_latest = gen.reportDate.max()
    last = hist[hist.reportDate == hist.reportDate.max()].iloc[0]

    def cod(g):
        return _ym(g.plannedOperationYear.max(), g.plannedOperationMonth.max())

    def cap(g):
        return round(float(g.nameplateCapacity.sum()), 1)

    def cap_mwh(g):
        vals = g.nameplateEnergyCapacity.dropna() if "nameplateEnergyCapacity" in g else pd.Series([], dtype=float)
        return round(float(vals.sum()), 1) if len(vals) else None

    def op_date(g):
        return _ym(g.operatingYear.max(), g.operatingMonth.max())

    def status(g):
        return str(g.eiaStatus.iloc[0])

    status_hist = change_points(hist, status)
    drop = drop_signal(hist, dataset_latest)
    if drop and drop["scope"] == "plant":
        # the plant's monthly series ends -> terminal status entry; "to" = the snapshot
        # where absence was observed (keeps the value/from/to change-point schema intact)
        status_hist.append({"value": "DROPPED_FROM_860M", "from": drop["last_seen"],
                            "to": drop["dataset_latest"], "last_seen": drop["last_seen"]})

    result = {
        "inr": inr, "plant_id": int(pid), "plant_name": str(last.eiaPlantName),
        "entity": str(last.eiaEntityName), "matched_by": why,
        "first_report": str(hist.reportDate.min())[:10],
        "last_report": str(hist.reportDate.max())[:10],
        "planned_cod_history": change_points(hist, cod),
        "capacity_history": change_points(hist, cap),
        "status_history": status_hist,
        "queue_reported_cod": str(r.projectCod)[:10],
        # --- additive fields (schema review 2026-07-19) -------------------------------
        "energy_capacity_mwh_history": change_points(hist, cap_mwh),
        "operating_date_history": change_points(hist, op_date),
        "eia_county": str(last.county) if "county" in hist and pd.notna(last.county) else None,
        "eia_lat": round(float(last.latitude), 5) if "latitude" in hist and pd.notna(last.latitude) else None,
        "eia_lon": round(float(last.longitude), 5) if "longitude" in hist and pd.notna(last.longitude) else None,
        "dropped_from_860m": drop,
    }
    return result


def resolve(inr, gen, county_map, queue_latest, plant_id=None):
    """(status, payload) for an INR — the batch-safe core. status in
    {ok, not_in_queue, not_in_eia, ambiguous}. Loads nothing (caller preloads inputs)."""
    r = queue_row(inr, queue_latest)
    if r is None:
        return "not_in_queue", {"inr": inr}
    cands = [(plant_id, "", "--plant-id")] if plant_id else find_plant(gen, r, county_map)
    if not cands:
        return "not_in_eia", {"inr": inr, "project": str(r.projectName)}
    if len(cands) > 1 and not plant_id:
        return "ambiguous", {"inr": inr, "project": str(r.projectName), "candidates": cands}
    pid, _, why = cands[0]
    if not (gen.plantId == pid).any():  # e.g. a wrong/typo'd --plant-id
        return "not_in_eia", {"inr": inr, "project": str(r.projectName)}
    return "ok", build_record(inr, r, gen, pid, why)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inr")
    ap.add_argument("--plant-id", type=int, default=None)
    ap.add_argument("--write", action="store_true",
                    help="write eia_history.json into the project research dir")
    a = ap.parse_args()

    gen = pd.read_parquet(GEN_PQ)
    queue_latest = load_queue_latest()
    county_map = plant_county_map()
    status, payload = resolve(a.inr, gen, county_map, queue_latest, a.plant_id)

    if status == "not_in_queue":
        raise SystemExit(f"{a.inr} not in latest queue snapshot")
    if status == "not_in_eia":
        print(f"{a.inr} '{payload['project']}': NOT in EIA-860M (TX slice) — normal for "
              "early-stage projects; this is negative evidence, log it.")
        return
    if status == "ambiguous":
        print(f"{len(payload['candidates'])} plant candidates — pick one and re-run with --plant-id:")
        for pid, n, why in payload["candidates"]:
            print(f"  --plant-id {pid}  '{n}'  ({why})")
        return

    res = payload
    print(f"{a.inr} '{queue_row(a.inr, queue_latest).projectName}'  <-  EIA plant "
          f"{res['plant_id']} '{res['plant_name']}'  entity '{res['entity']}' ({res['matched_by']})")
    print(f"reports {res['first_report']} -> {res['last_report']}")
    print(f"queue-reported COD: {res['queue_reported_cod']}")
    labels = [("planned_cod_history", "EIA planned COD"),
              ("capacity_history", "EIA capacity MW"),
              ("status_history", "EIA status")]
    if any(c["value"] is not None for c in res["energy_capacity_mwh_history"]):
        labels.insert(2, ("energy_capacity_mwh_history", "EIA energy capacity MWh"))
    if any(c["value"] is not None for c in res["operating_date_history"]):
        labels.append(("operating_date_history", "EIA operating date (actual)"))
    for key, label in labels:
        print(f"{label}:")
        for c in res[key]:
            print(f"  {c['value']}  ({c['from']} -> {c['to']})")
    if res["eia_lat"] is not None:
        print(f"EIA coordinates: {res['eia_lat']}, {res['eia_lon']}  ({res['eia_county']} Co)")
    d = res["dropped_from_860m"]
    if d and d["scope"] == "plant":
        print(f"DROPPED_FROM_860M: plant last seen {d['last_seen']} (dataset latest "
              f"{d['dataset_latest']}) — vanished from 860M, strong withdrawal/cancellation signal")
    elif d and d["scope"] == "units":
        gids = ", ".join(u["generator_id"] for u in d["dropped_units"])
        print(f"DROPPED_FROM_860M: {len(d['dropped_units'])} unit(s) [{gids}] last seen "
              f"{d['last_seen']} — plant still listed, partial withdrawal")

    if a.write:
        hits = sorted(BASE.glob(f"research/{a.inr}_*"))
        if not hits:
            raise SystemExit(f"no research dir matching {a.inr}_*")
        out = hits[0] / "eia_history.json"
        out.write_text(json.dumps(res, indent=1))
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
