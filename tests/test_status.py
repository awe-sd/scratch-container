import pandas as pd


def test_resolve_default_status_hierarchy():
    from branch_tracking.pipeline.status import resolve_default_status
    t = pd.DataFrame({
        "dampsse_default_status": ["Open", None, None],
        "implied_default_status": ["Closed", "Closed", None],
    })
    out = resolve_default_status(t)
    assert list(out["default_status"]) == ["Open", "Closed", None] or \
           out["default_status"].tolist()[:2] == ["Open", "Closed"] and pd.isna(out["default_status"].iloc[2])
    assert out["default_status_source"].tolist()[:2] == ["dampsse_inservice", "auction_fallback"]
    assert pd.isna(out["default_status_source"].iloc[2])
