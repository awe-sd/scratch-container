def test_is_high_side_matches_all_spellings():
    from branch_tracking.pipeline.mapping import is_high_side
    assert is_high_side("BTTSW_AXFMR1_HISIDE")
    assert is_high_side("X_HIGH")
    assert is_high_side("DIB_MT2H")
    assert not is_high_side("DIB_MT2L")
    assert not is_high_side("BTTSW_AXFMR1_LOSIDE")


def test_fuzzy_ratio_vealmoor_case():
    from branch_tracking.pipeline.mapping import fuzzy_ratio
    # VEALMOOR_VLM7TR2H vs VEALMOOR_VLMTR2L: same asset, name drift
    assert fuzzy_ratio("VEALMOOR_VLM7TR2H", "VEALMOOR_VLMTR2H") > 0.9
