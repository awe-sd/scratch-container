import pandas as pd


def test_normalize_strips_and_uppercases():
    from branch_tracking.pipeline.naming import normalize_name
    assert normalize_name("6520_G") == "6520G"
    assert normalize_name("6520__G") == "6520G"      # underscore drift
    assert normalize_name("LINE_1_1") == normalize_name("LINE1_1")  # known collision
    assert normalize_name("BLANK") is None            # placeholder -> unknown
    assert normalize_name(None) is None
    assert normalize_name(float("nan")) is None


def test_names_relate_substring_containment():
    from branch_tracking.pipeline.naming import names_relate, normalize_name
    assert names_relate(normalize_name("T1"), normalize_name("BKSLESST1"))
    assert names_relate(normalize_name("EXCSWMR2H"), normalize_name("MR2H"))
    assert not names_relate(normalize_name("CB_1814"), normalize_name("AT2H"))  # teid=113628
    assert not names_relate(None, "ANYTHING")


def test_unit_and_leg_extraction():
    from branch_tracking.pipeline.naming import unit_and_leg
    assert unit_and_leg("CMNSWAXFMR1H") == ("1", "H")
    assert unit_and_leg("SNDSWMR2L") == ("2", "L")
    assert unit_and_leg("MDOAT1") == ("1", None)
    assert unit_and_leg("SNDSWAXFMR1LH") == ("1", "L")  # '1L-H' style: leg is L
    assert unit_and_leg("NODIGITS") == (None, None)


def test_pick_by_leg_prefers_matching_unit_and_leg():
    from branch_tracking.pipeline.naming import pick_by_leg
    cands = pd.DataFrame({
        "name_norm": ["SNDSWMR1H", "SNDSWMR1L", "SNDSWMR2H", "SNDSWMR2L"],
        "ercotDampsseId": [1, 2, 3, 4],
    })
    got = pick_by_leg("SNDSWAXFMR1LH", cands)   # our low-side teid
    assert got is not None and got["name_norm"] == "SNDSWMR1L"
    got = pick_by_leg("SNDSWAXFMR1HH", cands)   # our high-side teid
    assert got is not None and got["name_norm"] == "SNDSWMR1H"
    assert pick_by_leg("NOUNIT", cands) is None
