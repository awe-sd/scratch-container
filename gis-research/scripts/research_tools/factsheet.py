"""Deterministic per-project fact sheet + paper score — pipeline v2 stage 0.

Assembles everything answerable locally (queue, EIA, SPV, registries, IA join table)
into factsheet.json/.md and computes a PAPER SCORE 0-100 (high = paper). Gate:
  paper_score >= 50                          -> paper_kill (triage dismisses, no deep)
  < 50 and (reality signal or COD<18mo or MW>=200) -> deep_candidate,
                                                priority = MW * 1/max(months_to_cod, 1)
  otherwise                                  -> ambiguous (triage judgment)
Triage may adjust the score +/-15 ONLY with a cited source (recorded in
triage_findings.json.score_adjustment). No LLM in this tool. Spec:
docs/superpowers/specs/2026-07-19-pipeline-v2-design.md
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd

import ch313
import eia_history as eh
import puct
import queue_history as qh

BASE = Path(__file__).resolve().parents[2]  # gis-research/
PARQUET = BASE / "data" / "ercot_generation_interconnect.parquet"


def score(f: dict) -> tuple[int, list[dict]]:
    F: list[dict] = []

    def add(cond, factor, points, detail=""):
        if cond:
            F.append({"factor": factor, "points": points, "detail": detail})

    slips = f.get("cod_slips") or 0
    if slips >= 3:
        pts = min(20, 6 + 2 * (slips - 3))
        add(True, "cod_slips", pts, f"{slips} COD slips")
    dq = f.get("eia_cod_delta_quarters")
    add(dq is not None and dq >= 2, "eia_cod_divergence", 15,
        f"EIA planned COD {dq} quarters after queue COD" if dq else "")
    add(f.get("dropped_scope") == "plant", "dropped_from_860m_plant", 25,
        "whole plant vanished from 860M")
    add(f.get("dropped_scope") == "units", "dropped_from_860m_units", 10,
        "unit(s) vanished from 860M")
    add(f.get("ia_signed") and not f.get("ia_verified_pdf")
        and not (f.get("ia_join_items") or 0), "no_verified_ia", 10,
        "iaSigned claimed but no IA found on disk or in the docket join table")
    add((f.get("fis_requested_years_ago") or 0) > 2 and not f.get("fis_approved"),
        "fis_stalled", 10, "FIS requested >2y ago, never approved")
    add((f.get("queue_age_years") or 0) > 4 and not f.get("synced"),
        "queue_aged_no_sync", 10, "in queue >4y without sync approval")
    add(not f.get("spv_resolved"), "spv_unresolvable", 10,
        "no SPV via spv.py or any registry")
    mtc = f.get("months_to_cod")
    add(not f.get("in_eia") and mtc is not None and mtc < 18,
        "not_in_eia_near_cod", 10, "absent from EIA with claimed COD <18mo out")
    return min(100, sum(x["points"] for x in F)), F


def gate(paper_score: int, f: dict) -> dict:
    mtc = f.get("months_to_cod")
    mw = f.get("capacity_mw") or 0.0
    if paper_score >= 50:
        return {"decision": "paper_kill", "priority": None,
                "reason": f"paper_score {paper_score} >= 50"}
    real = bool(f.get("reality_signals")) or (mtc is not None and mtc < 18) or mw >= 200
    if real:
        pri = round(mw * (1.0 / max(mtc if mtc is not None else 24.0, 1.0)), 2)
        return {"decision": "deep_candidate", "priority": pri,
                "reason": "reality signal / near COD / large MW"}
    return {"decision": "ambiguous", "priority": None,
            "reason": f"paper_score {paper_score} < 50 but no reality trigger"}


def _quarters_between(ym_a: str, ym_b: str) -> float:
    """Quarters from a (queue COD, 'YYYY-MM') to b (EIA planned COD)."""
    ay, am = int(ym_a[:4]), int(ym_a[5:7])
    by, bm = int(ym_b[:4]), int(ym_b[5:7])
    return round(((by - ay) * 12 + (bm - am)) / 3.0, 1)


def facts_from_parts(queue: dict, eia_status: str, eia_payload: dict | None,
                     spv_resolved: bool, verified_ia_pdfs: int, join_items: int) -> dict:
    signals = []
    dropped = None
    delta_q = None
    if eia_status == "ok" and eia_payload:
        st = (eia_payload.get("status_history") or [{}])[-1].get("value", "") or ""
        if st.startswith(("(U", "(V")):
            signals.append("eia_under_construction")
        if any(c.get("value") for c in eia_payload.get("operating_date_history") or []):
            signals.append("eia_operating_date")
        d = eia_payload.get("dropped_from_860m")
        dropped = d.get("scope") if d else None
        eia_cod = (eia_payload.get("planned_cod_history") or [{}])[-1].get("value")
        if eia_cod and queue.get("queue_cod_ym"):
            delta_q = _quarters_between(queue["queue_cod_ym"], eia_cod)
    if verified_ia_pdfs:
        signals.append("verified_ia_on_disk")
    if queue.get("fis_approved"):
        signals.append("fis_approved")
    return {
        "cod_slips": queue.get("cod_slips", 0),
        "eia_cod_delta_quarters": delta_q,
        "dropped_scope": dropped,
        "ia_signed": bool(queue.get("ia_signed")),
        "ia_verified_pdf": verified_ia_pdfs > 0,
        "ia_join_items": join_items,
        "fis_requested_years_ago": queue.get("fis_requested_years_ago"),
        "fis_approved": bool(queue.get("fis_approved")),
        "queue_age_years": queue.get("queue_age_years", 0.0),
        "synced": bool(queue.get("synced")),
        "spv_resolved": spv_resolved,
        "in_eia": eia_status == "ok",
        "months_to_cod": queue.get("months_to_cod"),
        "capacity_mw": queue.get("capacity_mw", 0.0),
        "reality_signals": signals,
    }


# ---- context (load once, reuse across INRs) -------------------------------

def load_ctx() -> dict:
    """Preload every parquet/table facts_from_parts/build needs — one read each,
    reused across every INR in a bulk (--all) run."""
    hist = pd.read_parquet(PARQUET)
    queue_latest = hist[hist.fileDate == hist.fileDate.max()]
    gen = pd.read_parquet(eh.GEN_PQ)
    county_map = eh.plant_county_map()

    spv: dict[str, list[dict]] = {}
    spv_path = BASE / "research" / "_reference" / "spv_candidates.csv"
    if spv_path.exists():
        with open(spv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                spv.setdefault(row["inr"], []).append(row)

    ch313_rows = json.loads(ch313.CH313_FILE.read_text())["rows"] if ch313.CH313_FILE.exists() else []
    jeti_rows = json.loads(ch313.JETI_FILE.read_text())["rows"] if ch313.JETI_FILE.exists() else []
    faa_file = BASE / "data" / "reference" / "faa_oe_cases_tx.json"
    faa_cases = json.loads(faa_file.read_text())["cases"] if faa_file.exists() else []

    return {
        "hist": hist, "queue_latest": queue_latest, "gen": gen, "county_map": county_map,
        "spv": spv, "ch313_rows": ch313_rows, "jeti_rows": jeti_rows, "faa_cases": faa_cases,
        "parquet_mtime": PARQUET.stat().st_mtime,
    }


def _registry_tool(fuel: str, technology: str) -> str:
    """WIN -> faa (turbine OE/AAA cases); SOL or OTH-BA (battery) -> ch313/JETI (value-limitation
    filings key on school district, not county); GAS -> tceq (not queried at factsheet stage);
    else no local registry applies."""
    fuel = re.sub(r"\s+", "", (fuel or "")).upper()
    technology = re.sub(r"\s+", "", (technology or "")).upper()
    if fuel == "WIN":
        return "faa"
    if fuel == "SOL" or (fuel == "OTH" and technology == "BA"):
        return "ch313"
    if fuel == "GAS":
        return "tceq"
    return "none"


def _registry_hits(tool: str, project: str, county: str | None, ctx: dict) -> list[dict]:
    """Local-reference-only lookups (no network): ch313/JETI name-substring overlap via
    ch313._score, or FAA OE/AAA case county string match. tceq/none -> no local hits at
    this stage (tceq is a live per-county query, out of scope for bulk factsheet runs)."""
    if tool == "ch313":
        hits = []
        for prog, rows, name_key, district_key in (
                ("Ch.313", ctx["ch313_rows"], "applicant", "district"),
                ("JETI", ctx["jeti_rows"], "applicant", "school_district")):
            for row in rows:
                s = ch313._score(project, row.get(name_key, "") or "")
                if s > 0:
                    hits.append({"program": prog, "applicant": row.get(name_key, ""),
                                 "district": row.get(district_key, ""), "score": s})
        hits.sort(key=lambda h: -h["score"])
        return hits
    if tool == "faa":
        county_u = (county or "").strip().upper()
        if not county_u:
            return []
        return [{"asn": c.get("asn"), "sponsor": c.get("sponsor"),
                 "county": c.get("county"), "status": c.get("status")}
                for c in ctx["faa_cases"] if (c.get("county") or "").strip().upper() == county_u]
    return []  # tceq | none


# ---- build ------------------------------------------------------------------

def build(inr: str, ctx: dict) -> dict:
    """Assemble the factsheet payload for one INR from preloaded ctx (see load_ctx).
    Operates on the LATEST queue snapshot only — a project absent from it (delisted/
    cancelled) gets no factsheet; a stale historical row would feed a wrong COD/status
    into score/gate and leak a non-enum 'not_in_queue' into eia.status."""
    hist = ctx["hist"]
    proj_hist = hist[hist.INR == inr].sort_values("fileDate")
    if proj_hist.empty:
        raise SystemExit(f"INR {inr!r} not found in the queue parquet")

    latest_rows = ctx["queue_latest"][ctx["queue_latest"].INR == inr]
    if latest_rows.empty:
        raise SystemExit(f"{inr} not in latest queue snapshot — project delisted/cancelled; "
                          "no factsheet")
    r = latest_rows.iloc[0]

    def _d(col):
        v = r.get(col) if col in r else None
        return None if pd.isna(v) else str(v)[:10]

    project = str(r.get("projectName"))
    county = None if pd.isna(r.get("county")) else str(r.get("county"))
    fuel = str(r.get("fuel"))
    technology = str(r.get("technology"))
    capacity_mw = 0.0 if pd.isna(r.get("capacityMw")) else round(float(r.get("capacityMw")), 2)
    queue_cod = _d("projectCod")

    fin_sec = r.get("financialSecurityAndNoticeToProceedProvided")
    milestones = {
        "screeningStudyComplete": _d("screeningStudyComplete"),
        "fisApproved": _d("fisApproved"),
        "iaSigned": _d("iaSigned"),
        "financial_security": None if pd.isna(fin_sec) else str(fin_sec),
    }

    # cod_slips: reuse queue_history's change-point logic (same drift definition as
    # queue_history.py's own "N reported-COD change(s)" tally) across the FULL history.
    cod_runs = qh.track_changes(proj_hist, "projectCod")
    cod_slips = max(len([c for c in cod_runs if c["value"]]) - 1, 0)

    today = dt.date.today()
    months_to_cod = None
    if queue_cod:
        cy, cm, cd = (int(x) for x in queue_cod.split("-"))
        months_to_cod = round((dt.date(cy, cm, cd) - today).days / 30.4, 2)

    first_seen = proj_hist["fileDate"].iloc[0]
    queue_age_years = round((today - first_seen).days / 365.25, 2)

    fis_requested_years_ago = None
    if "fisRequested" in hist.columns:
        fr = r.get("fisRequested")
        if pd.notna(fr):
            fis_requested_years_ago = round((today - fr).days / 365.25, 2)

    queue_facts = {
        "cod_slips": cod_slips,
        "months_to_cod": months_to_cod,
        "capacity_mw": capacity_mw,
        "ia_signed": bool(pd.notna(r.get("iaSigned"))),
        "fis_approved": bool(pd.notna(r.get("fisApproved"))),
        "fis_requested_years_ago": fis_requested_years_ago,
        "queue_age_years": queue_age_years,
        "synced": bool(pd.notna(r.get("approvedForSynchronization"))),
        "queue_cod_ym": queue_cod[:7] if queue_cod else None,
    }

    eia_status, eia_payload = eh.resolve(inr, ctx["gen"], ctx["county_map"], ctx["queue_latest"])

    spv_rows = ctx["spv"].get(inr, [])
    spv_csv_resolved = any((row.get("entity") or "").strip() for row in spv_rows)
    tool = _registry_tool(fuel, technology)
    registry_hits = _registry_hits(tool, project, county, ctx)
    spv_resolved = spv_csv_resolved or bool(registry_hits)

    proj_dirs = sorted((BASE / "research").glob(f"{inr}_*"))
    proj_dir = proj_dirs[0] if proj_dirs else None
    verified_pdfs = 0
    if proj_dir is not None:
        pdfs = glob.glob(str(proj_dir / "sources" / "*puct*.pdf"))
        verified_pdfs = len([p for p in pdfs if not Path(p).name.startswith("unverified_")])
    join_ct = len(puct.join_items(inr))

    facts = facts_from_parts(queue_facts, eia_status,
                             eia_payload if eia_status == "ok" else None,
                             spv_resolved, verified_pdfs, join_ct)
    paper_score, factors = score(facts)
    g = gate(paper_score, facts)

    eia_block = {
        "status": eia_status,
        "plant_id": eia_payload.get("plant_id") if eia_status == "ok" else None,
        "entity": eia_payload.get("entity") if eia_status == "ok" else None,
        "planned_cod": ((eia_payload.get("planned_cod_history") or [{}])[-1].get("value")
                        if eia_status == "ok" else None),
        "cod_delta_quarters": facts["eia_cod_delta_quarters"],
        "dropped_scope": facts["dropped_scope"],
        "coords": ([eia_payload["eia_lat"], eia_payload["eia_lon"]]
                   if eia_status == "ok" and eia_payload.get("eia_lat") is not None else None),
    }

    return {
        "inr": inr,
        "generated": str(today),
        "project": project,
        "county": county,
        "fuel": fuel,
        "technology": technology,
        "capacity_mw": capacity_mw,
        "queue_cod": queue_cod,
        "milestones": milestones,
        "cod_slips": cod_slips,
        "eia": eia_block,
        "spv": {"resolved": spv_resolved,
                "candidates": [{"source": row.get("source"), "entity": row.get("entity"),
                                "detail": row.get("detail")} for row in spv_rows]},
        "registry": {"tool": tool, "hits": registry_hits},
        "ia": {"signed": queue_facts["ia_signed"], "verified_pdfs": verified_pdfs, "join_items": join_ct},
        "reality_signals": facts["reality_signals"],
        "paper_score": paper_score,
        "score_factors": factors,
        "gate": g,
    }


# ---- rendering + write ------------------------------------------------------

def render_md(res: dict) -> str:
    lines = [f"# Factsheet — {res['project']} ({res['inr']})",
             f"{res['county']} Co · {res['fuel']}/{res['technology']} · {res['capacity_mw']} MW · "
             f"queue COD {res['queue_cod']} · generated {res['generated']}", ""]

    g = res["gate"]
    pri = f"  (priority {g['priority']})" if g.get("priority") is not None else ""
    lines += [f"## Paper score: {res['paper_score']} -> **{g['decision']}**{pri}", g["reason"], ""]
    if res["score_factors"]:
        lines += ["| Factor | Points | Detail |", "|---|---|---|"]
        lines += [f"| {f['factor']} | {f['points']} | {f['detail']} |" for f in res["score_factors"]]
    else:
        lines.append("_no scoring factors triggered_")
    lines.append("")

    lines += ["## Reality signals",
              (", ".join(res["reality_signals"]) if res["reality_signals"] else "_none_"), ""]

    lines += ["## EIA-860M", f"status: {res['eia']['status']}"]
    if res["eia"]["status"] == "ok":
        lines += [f"plant {res['eia']['plant_id']}  '{res['eia']['entity']}'",
                  f"planned COD: {res['eia']['planned_cod']}  "
                  f"(delta {res['eia']['cod_delta_quarters']} quarters vs queue COD)",
                  f"coords: {res['eia']['coords']}"]
        if res["eia"]["dropped_scope"]:
            lines.append(f"**DROPPED_FROM_860M** scope={res['eia']['dropped_scope']}")
    lines.append("")

    lines += ["## SPV / registry", f"spv resolved: {res['spv']['resolved']}"]
    for c in res["spv"]["candidates"]:
        lines.append(f"- ({c.get('source')}) {c.get('entity')} — {c.get('detail')}")
    lines.append(f"registry tool: {res['registry']['tool']}")
    for h in res["registry"]["hits"]:
        lines.append(f"- {h}")
    lines.append("")

    lines += ["## IA",
              f"signed (queue-claimed): {res['ia']['signed']}  ·  "
              f"verified PDFs on disk: {res['ia']['verified_pdfs']}  ·  "
              f"docket join-table items: {res['ia']['join_items']}", ""]

    m = res["milestones"]
    lines += ["## Milestones",
              f"- screeningStudyComplete: {m['screeningStudyComplete'] or '—'}",
              f"- fisApproved: {m['fisApproved'] or '—'}",
              f"- iaSigned: {m['iaSigned'] or '—'}",
              f"- financial_security: {m['financial_security']}"]
    return "\n".join(lines) + "\n"


def write_outputs(inr: str, res: dict) -> Path:
    """--write target: research/<INR>_*/factsheet.{json,md} when a research dir already
    exists (triaged project); else research/_factsheets/<INR>.{json,md} (untriaged)."""
    hits = sorted((BASE / "research").glob(f"{inr}_*"))
    if hits:
        out_dir, json_name, md_name = hits[0], "factsheet.json", "factsheet.md"
    else:
        out_dir = BASE / "research" / "_factsheets"
        out_dir.mkdir(parents=True, exist_ok=True)
        json_name, md_name = f"{inr}.json", f"{inr}.md"
    (out_dir / json_name).write_text(json.dumps(res, indent=1, default=str))
    (out_dir / md_name).write_text(render_md(res))
    return out_dir


# ---- CLI ---------------------------------------------------------------------

def _print_report(res: dict) -> None:
    print(f"{res['inr']} '{res['project']}'  {res['county']} Co  {res['fuel']}/{res['technology']}  "
          f"{res['capacity_mw']} MW  queue COD {res['queue_cod']}")
    g = res["gate"]
    pri = f"  priority={g['priority']}" if g.get("priority") is not None else ""
    print(f"paper_score={res['paper_score']}  gate={g['decision']}{pri}  ({g['reason']})")
    for f in res["score_factors"]:
        print(f"  [+{f['points']}] {f['factor']}: {f['detail']}")
    print(f"reality signals: {', '.join(res['reality_signals']) if res['reality_signals'] else 'none'}")
    e = res["eia"]
    if e["status"] == "ok":
        print(f"EIA: plant {e['plant_id']} '{e['entity']}'  planned COD {e['planned_cod']}  "
              f"delta {e['cod_delta_quarters']}q  dropped_scope={e['dropped_scope']}")
    else:
        print(f"EIA: {e['status']}")
    print(f"SPV resolved={res['spv']['resolved']}  registry={res['registry']['tool']} "
          f"({len(res['registry']['hits'])} hits)")
    print(f"IA: signed={res['ia']['signed']}  verified_pdfs={res['ia']['verified_pdfs']}  "
          f"join_items={res['ia']['join_items']}")


def run_all(ctx: dict, limit: int | None) -> None:
    # inrs is drawn straight from queue_latest, so build()'s "not in latest snapshot"
    # SystemExit can never fire here — every INR iterated is by construction present.
    inrs = sorted(ctx["queue_latest"].INR.unique())
    n_built = n_skip = n_kill = n_deep = n_amb = 0
    for inr in inrs:
        if limit is not None and n_built >= limit:
            break
        hits = sorted((BASE / "research").glob(f"{inr}_*"))
        if not hits:
            continue
        fs_path = hits[0] / "factsheet.json"
        if fs_path.exists() and fs_path.stat().st_mtime > ctx["parquet_mtime"]:
            n_skip += 1
            continue
        res = build(inr, ctx)
        write_outputs(inr, res)
        decision = res["gate"]["decision"]
        print(f"{inr}  {res['paper_score']}  {decision}")
        n_built += 1
        n_kill += decision == "paper_kill"
        n_deep += decision == "deep_candidate"
        n_amb += decision == "ambiguous"
    print(f"built {n_built}  paper_kill {n_kill}  deep_candidate {n_deep}  ambiguous {n_amb}  "
          f"skipped(up-to-date) {n_skip}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inr", nargs="?", default=None, help="e.g. 24INR0281")
    ap.add_argument("--write", action="store_true",
                    help="write factsheet.json + factsheet.md into the project research dir")
    ap.add_argument("--all", action="store_true",
                    help="build for every triaged project (has a research/<INR>_* dir) in the "
                         "latest queue snapshot; always writes (resumable)")
    ap.add_argument("--limit", type=int, default=None, help="cap projects built in --all mode")
    a = ap.parse_args()

    if not a.inr and not a.all:
        raise SystemExit("need an INR, or --all")

    ctx = load_ctx()

    if a.all:
        run_all(ctx, a.limit)
        return

    res = build(a.inr, ctx)
    _print_report(res)
    if a.write:
        out_dir = write_outputs(a.inr, res)
        print(f"wrote {out_dir}/factsheet.json (+ .md)")


if __name__ == "__main__":
    main()
