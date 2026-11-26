import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
import deep_worker as dw

CSV_FIELDS = ["rank", "inr", "project", "mw", "months_to_cod", "paper_score",
              "decision", "priority", "already_deep_scanned", "promoted_by_triage"]


def _write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _row(rank, inr, project, scanned) -> dict:
    return {"rank": rank, "inr": inr, "project": project, "mw": 100.0,
            "months_to_cod": 3.0, "paper_score": 20, "decision": "deep_candidate",
            "priority": 33.3, "already_deep_scanned": str(scanned),
            "promoted_by_triage": "False"}


def test_queue_candidates_skips_already_scanned(tmp_path):
    csv_path = tmp_path / "deep_queue_v2.csv"
    _write_csv(csv_path, [
        _row(1, "20INR0001", "Alpha", True),    # already scanned -- skip
        _row(2, "20INR0002", "Bravo", False),   # candidate
        _row(3, "20INR0003", "Charlie", False), # candidate
    ])
    assert dw.queue_candidates(csv_path) == ["20INR0002", "20INR0003"]


def test_next_inr_from_csv_picks_first_candidate_with_research_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(dw, "BASE", tmp_path)
    csv_path = tmp_path / "deep_queue_v2.csv"
    _write_csv(csv_path, [
        _row(1, "20INR0001", "Alpha", True),
        _row(2, "20INR0002", "Bravo", False),
        _row(3, "20INR0003", "Charlie", False),
    ])
    # only Bravo has a research dir on disk (Charlie was never triaged)
    (tmp_path / "research" / "20INR0002_bravo").mkdir(parents=True)

    pick = dw.next_inr_from_csv(csv_path)
    assert pick is not None
    inr, d, attempts = pick
    assert inr == "20INR0002"
    assert d == tmp_path / "research" / "20INR0002_bravo"
    assert attempts == 0


def test_next_inr_from_csv_skips_done_and_claimed(tmp_path, monkeypatch):
    monkeypatch.setattr(dw, "BASE", tmp_path)
    csv_path = tmp_path / "deep_queue_v2.csv"
    _write_csv(csv_path, [
        _row(1, "20INR0002", "Bravo", False),
        _row(2, "20INR0003", "Charlie", False),
    ])
    bravo = tmp_path / "research" / "20INR0002_bravo"
    charlie = tmp_path / "research" / "20INR0003_charlie"
    bravo.mkdir(parents=True)
    charlie.mkdir(parents=True)
    (bravo / "findings.json").write_text("{}")  # already done -- skip to Charlie

    pick = dw.next_inr_from_csv(csv_path)
    assert pick is not None and pick[0] == "20INR0003"

    # now claim Charlie (fresh) -- queue should go dry
    (charlie / ".deep_claim").write_text(json.dumps({"attempts": 0, "ts": time.time()}))
    assert dw.next_inr_from_csv(csv_path) is None
