import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
import puct


def test_join_items_finds_docket_items(tmp_path, monkeypatch):
    join = {"1151": {"filed": "1/2/2024", "description": "SGIA Samson3", "inrs": ["23INR0086"]},
            "999": {"filed": "1/1/2020", "description": "other", "inrs": ["20INR0001"]}}
    f = tmp_path / "puct_inr_join.json"
    f.write_text(json.dumps(join))
    monkeypatch.setattr(puct, "INR_JOIN_FILE", f)
    items = puct.join_items("23INR0086")
    assert items == [{"item": "1151", "filed": "1/2/2024", "description": "SGIA Samson3"}]
    assert puct.join_items("99INR9999") == []


def test_join_items_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(puct, "INR_JOIN_FILE", tmp_path / "absent.json")
    assert puct.join_items("23INR0086") == []
