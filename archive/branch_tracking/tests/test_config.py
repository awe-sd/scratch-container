import pandas as pd


def test_config_values():
    from branch_tracking.pipeline import config as c
    assert c.ISOMARKETID_ERCOT == 6
    assert c.REASON_NEW_EQUIPMENT == 4 and c.REASON_RETIREMENT == 9
    assert c.DEFAULT_IN_SERVICE_DATE == pd.Timestamp("1990-01-01")
    assert c.DEFAULT_RETIREMENT_DATE == pd.Timestamp("2099-12-31")
    assert c.CHAIN_GAP_TOLERANCE == pd.Timedelta(days=3)
    assert c.STATUS_CONTRADICTION_MIN_ROWS == 5
    assert "cancl" in c.INVALID_STATUS_KEYWORDS and "withd" in c.INVALID_STATUS_KEYWORDS
    assert "BLANK" in c.PLACEHOLDER_NAMES
    assert c.FILETYPE_FOR_DEVICE == {"Line": 1, "Transformer": 2}
    assert c.WINDOW_DAYS == 730 and c.CKT_WINDOW_DAYS == 90
    assert c.AWDATEID_ANCHOR[0] == 44926
    assert (c.OUTPUT_DIR / "branch_tracking_table.csv").exists()
