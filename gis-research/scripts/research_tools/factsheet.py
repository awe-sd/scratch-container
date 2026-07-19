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
