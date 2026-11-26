import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from factsheet import score, gate

PAPER = dict(cod_slips=1, eia_cod_delta_quarters=None, dropped_scope="plant",
             ia_signed=True, ia_verified_pdf=False, ia_join_items=0,
             fis_requested_years_ago=3.0, fis_approved=False, queue_age_years=5.0,
             synced=False, spv_resolved=False, in_eia=False, months_to_cod=12.0,
             capacity_mw=150.0, reality_signals=[])

REAL = dict(cod_slips=6, eia_cod_delta_quarters=3.0, dropped_scope=None,
            ia_signed=True, ia_verified_pdf=True, ia_join_items=2,
            fis_requested_years_ago=1.0, fis_approved=True, queue_age_years=2.0,
            synced=False, spv_resolved=True, in_eia=True, months_to_cod=2.0,
            capacity_mw=310.0, reality_signals=["eia_under_construction"])


def test_paper_project_scores_high():
    s, factors = score(PAPER)
    assert s >= 50
    names = {f["factor"] for f in factors}
    assert "dropped_from_860m_plant" in names and "no_verified_ia" in names


def test_real_project_scores_low_despite_slips():
    s, factors = score(REAL)   # slips + divergence alone must not cross the kill line
    assert s < 50


def test_score_capped_0_100():
    worst = dict(PAPER, cod_slips=25, eia_cod_delta_quarters=8.0)
    s, _ = score(worst)
    assert 0 <= s <= 100


def test_gate_paper_kill():
    s, _ = score(PAPER)
    g = gate(s, PAPER)
    assert g["decision"] == "paper_kill" and g["priority"] is None


def test_gate_deep_candidate_priority_mw_times_nearness():
    s, _ = score(REAL)
    g = gate(s, REAL)
    assert g["decision"] == "deep_candidate"
    assert g["priority"] == round(310.0 * (1.0 / max(2.0, 1.0)), 2)


def test_gate_ambiguous_middle():
    mid = dict(REAL, reality_signals=[], months_to_cod=30.0, capacity_mw=80.0)
    g = gate(score(mid)[0], mid)
    assert g["decision"] == "ambiguous"


def test_gate_no_signal_near_cod_is_ambiguous():
    # user-adjudicated 2026-07-20: bare months_to_cod<18 / mw>=200 no longer
    # create deep_candidate on their own -- reality_signals is now required.
    facts = dict(REAL, reality_signals=[], months_to_cod=2.0, capacity_mw=500.0)
    g = gate(score(facts)[0], facts)
    assert g["decision"] == "ambiguous" and g["priority"] is None


def test_gate_zeus_style_low_score_no_signal_is_ambiguous():
    # Zeus Mitchell ground truth: score 20 (well under the paper_kill line) with
    # no reality signals must land ambiguous, not deep_candidate or paper_kill.
    facts = dict(REAL, reality_signals=[], months_to_cod=2.0, capacity_mw=310.0)
    g = gate(20, facts)
    assert g["decision"] == "ambiguous"
    assert g["decision"] != "paper_kill"
    assert g["priority"] is None
