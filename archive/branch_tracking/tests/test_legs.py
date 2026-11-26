def test_classify_and_base_name():
    from branch_tracking.pipeline.legs import classify_leg, base_name
    assert classify_leg("DIB_MT2H") == "H"
    assert classify_leg("DIB_MT2L") == "L"
    assert base_name("DIB_MT2H") == base_name("DIB_MT2L")
