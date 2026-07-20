import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
import factsheet


def test_facts_from_parts_reality_signals():
    eia_payload = {"status_history": [{"value": "(U) Under construction, <=50%"}],
                   "planned_cod_history": [{"value": "2027-05"}],
                   "plant_id": 69364, "entity": "Red Egret, LLC",
                   "dropped_from_860m": None, "eia_lat": 29.4, "eia_lon": -95.0}
    facts = factsheet.facts_from_parts(
        queue={"cod_slips": 6, "months_to_cod": 2.0, "capacity_mw": 310.0,
               "ia_signed": True, "fis_approved": True, "fis_requested_years_ago": 1.0,
               "queue_age_years": 2.0, "synced": False, "queue_cod_ym": "2026-08"},
        eia_status="ok", eia_payload=eia_payload,
        spv_resolved=True, verified_ia_pdfs=2, join_items=2)
    assert "eia_under_construction" in facts["reality_signals"]
    assert "verified_ia_on_disk" in facts["reality_signals"]
    assert facts["eia_cod_delta_quarters"] == 3.0   # 2026-08 -> 2027-05 = 3 quarters
    assert facts["in_eia"] is True and facts["dropped_scope"] is None
