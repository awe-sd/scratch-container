import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
import search


def test_backoff_to_30s_when_window_over_half_full(tmp_path, monkeypatch):
    """Fleet-risk fix: once the sliding-hour window already holds > half MAX_PER_HOUR
    stamps, the effective min interval rises from 3s to 30s -- prevents a burst of
    concurrent agents from exhausting the fleet hour-cap in minutes."""
    throttle = tmp_path / ".search_throttle.json"
    monkeypatch.setattr(search, "THROTTLE", throttle)
    now = time.time()
    stamps = [now - 1] * 61  # > MAX_PER_HOUR/2 (60), still well under the 120 cap
    throttle.write_text(json.dumps({"stamps": stamps}))
    slept = []
    monkeypatch.setattr(search.time, "sleep", lambda s: slept.append(s))
    search._throttle_and_budget()
    assert slept and 25 < slept[0] <= 30


def test_normal_3s_interval_when_window_not_half_full(tmp_path, monkeypatch):
    throttle = tmp_path / ".search_throttle.json"
    monkeypatch.setattr(search, "THROTTLE", throttle)
    now = time.time()
    stamps = [now - 0.1] * 5  # well under MAX_PER_HOUR/2
    throttle.write_text(json.dumps({"stamps": stamps}))
    slept = []
    monkeypatch.setattr(search.time, "sleep", lambda s: slept.append(s))
    search._throttle_and_budget()
    assert slept and 0 < slept[0] <= 3.1


def test_budget_exhausted_exits_2(tmp_path, monkeypatch):
    throttle = tmp_path / ".search_throttle.json"
    monkeypatch.setattr(search, "THROTTLE", throttle)
    now = time.time()
    throttle.write_text(json.dumps({"stamps": [now] * search.MAX_PER_HOUR}))
    try:
        search._throttle_and_budget()
        assert False, "expected SystemExit"
    except SystemExit as e:
        assert e.code == 2
