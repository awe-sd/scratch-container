import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
import make_deep_queue as mdq


def _write_factsheet(proj_dir: Path, *, inr: str, project: str, decision: str,
                      priority: float | None = None, mw: float = 100.0) -> None:
    proj_dir.mkdir(parents=True, exist_ok=True)
    (proj_dir / "factsheet.json").write_text(json.dumps({
        "inr": inr, "project": project, "capacity_mw": mw,
        "queue_cod": "2027-01-01", "generated": "2026-07-20",
        "paper_score": 20, "gate": {"decision": decision, "priority": priority},
    }))


def _write_triage(proj_dir: Path, verdict: str) -> None:
    (proj_dir / "triage_findings.json").write_text(json.dumps({"verdict": verdict}))


def test_build_v2_promotion_and_demotion(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(mdq, "BASE", tmp_path)
    research = tmp_path / "research"

    # 1. plain deep_candidate, no recheck -- included unchanged
    _write_factsheet(research / "20INR0001_alpha", inr="20INR0001", project="Alpha",
                      decision="deep_candidate", priority=42.0)

    # 2. PROMOTION: gate said ambiguous, triage-v2 recheck verdict says deep_candidate
    bravo_dir = research / "20INR0002_bravo"
    _write_factsheet(bravo_dir, inr="20INR0002", project="Bravo",
                      decision="ambiguous", priority=None, mw=100.0)
    _write_triage(bravo_dir, "deep_candidate")

    # 3. DEMOTION: gate said deep_candidate, triage-v2 recheck verdict says paper_dismissed
    charlie_dir = research / "20INR0003_charlie"
    _write_factsheet(charlie_dir, inr="20INR0003", project="Charlie",
                      decision="deep_candidate", priority=99.0)
    _write_triage(charlie_dir, "paper_dismissed")

    # 4. plain ambiguous, no recheck yet -- stays in the recheck queue
    _write_factsheet(research / "20INR0004_delta", inr="20INR0004", project="Delta",
                      decision="ambiguous", priority=None)

    csv_path = tmp_path / "deep_queue_v2.csv"
    recheck_path = tmp_path / "triage_recheck_v2.txt"
    mdq.build_v2(csv_path, recheck_path)

    with open(csv_path, newline="", encoding="utf-8") as fh:
        rows = {r["inr"]: r for r in csv.DictReader(fh)}

    assert set(rows) == {"20INR0001", "20INR0002"}  # charlie demoted, delta still ambiguous
    assert rows["20INR0001"]["promoted_by_triage"] == "False"
    assert rows["20INR0002"]["promoted_by_triage"] == "True"
    assert rows["20INR0002"]["decision"] == "deep_candidate"

    # promoted priority computed the same way gate() does: mw * 1/max(months_to_cod, 1)
    import datetime as dt
    mtc = round((dt.date(2027, 1, 1) - dt.date(2026, 7, 20)).days / 30.4, 2)
    expected_priority = round(100.0 * (1.0 / max(mtc, 1.0)), 2)
    assert float(rows["20INR0002"]["priority"]) == expected_priority

    recheck_text = recheck_path.read_text()
    assert "20INR0004" in recheck_text  # still-ambiguous stays queued for recheck
    assert "20INR0002" not in recheck_text  # promoted -- no longer needs a recheck
    assert "20INR0003" not in recheck_text  # demoted via deep_candidate branch, not ambiguous

    out = capsys.readouterr().out
    assert "1 promoted" in out and "1 demoted" in out


def test_build_v2_warns_on_corrupt_json_and_unknown_decision(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(mdq, "BASE", tmp_path)
    research = tmp_path / "research"

    bad_dir = research / "20INR0005_echo"
    bad_dir.mkdir(parents=True)
    (bad_dir / "factsheet.json").write_text("{not json")

    weird_dir = research / "20INR0006_foxtrot"
    _write_factsheet(weird_dir, inr="20INR0006", project="Foxtrot",
                      decision="something_new", priority=None)

    mdq.build_v2(tmp_path / "deep_queue_v2.csv", tmp_path / "triage_recheck_v2.txt")

    err = capsys.readouterr().err
    assert "corrupt JSON" in err
    assert "unknown/missing gate.decision" in err
