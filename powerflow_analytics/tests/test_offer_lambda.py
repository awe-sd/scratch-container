import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pfa.analysis import offer_lambda


def test_sced_names_disambiguates_multi_unit_bus():
    """A bus with several units (e.g. a 3-train CC) must resolve each
    (BUSNUM, ID) to its own SCED name via the ID-suffix match, not an
    arbitrary sibling's — the bug the old BUSNAME-only dedup had."""
    pair = pd.DataFrame({
        "BUSNUM": [1, 1, 1, 2],
        "ID": ["1", "2", "3", "1"],
        "SIDE": ["up"] * 4,
        "DIFF_MW": [10.0] * 4,
    })
    bus_names = pd.DataFrame({"BUSNUM": [1, 2], "BUSNAME": ["JCKCNTY5", "OTHERBUS"]})
    genunit = pd.DataFrame({
        "GENUNITID": [66000414, 66000415, 66000416, 66000500],
        "BUSNAME": ["JCKCNTY5", "JCKCNTY5", "JCKCNTY5", "OTHERBUS"],
    })
    scedname = pd.DataFrame({
        "GENUNITID": [66000414, 66000415, 66000416, 66000500],
        "NAME": ["JCKCNTY2_CC1_1", "JCKCNTY2_CC1_2", "JCKCNTY2_CC1_3", "SOLO_UNIT_1"],
        "KIND": ["GEN"] * 4,
    })
    out = offer_lambda.sced_names(pair, bus_names, genunit, scedname).set_index(["BUSNUM", "ID"])
    assert out.loc[(1, "1"), "SCED"] == "JCKCNTY2_CC1"
    assert out.loc[(1, "2"), "SCED"] == "JCKCNTY2_CC1"
    assert out.loc[(1, "3"), "SCED"] == "JCKCNTY2_CC1"
    assert out.loc[(1, "1"), "NAME"] == "JCKCNTY2_CC1_1"
    assert out.loc[(1, "2"), "NAME"] == "JCKCNTY2_CC1_2"
    assert out.loc[(2, "1"), "SCED"] == "SOLO_UNIT"


def test_sced_names_falls_back_when_no_id_suffix_match():
    """When the suffix convention doesn't line up, still resolve a
    single-unit bus rather than dropping it (matches the pre-fix behavior
    for the buses where BUSNAME-only lookup was already correct)."""
    pair = pd.DataFrame({"BUSNUM": [9], "ID": ["UN"], "SIDE": ["up"], "DIFF_MW": [10.0]})
    bus_names = pd.DataFrame({"BUSNUM": [9], "BUSNAME": ["SOLOBUS"]})
    genunit = pd.DataFrame({"GENUNITID": [1], "BUSNAME": ["SOLOBUS"]})
    scedname = pd.DataFrame({"GENUNITID": [1], "NAME": ["SOLOBUS_GEN_1"], "KIND": ["GEN"]})
    out = offer_lambda.sced_names(pair, bus_names, genunit, scedname)
    assert out["SCED"].iloc[0] == "SOLOBUS_GEN"


def test_dispatch_screen_no_coverage_returns_none(monkeypatch):
    monkeypatch.setattr(offer_lambda.sf, "query", lambda *a, **k: pd.DataFrame())
    assert offer_lambda.dispatch_screen(14411, "1436-2081-1@DWCSRAM5") is None


def test_dispatch_screen_flags_lz_wz_and_radial_only():
    shifts = pd.DataFrame({
        "DEVICE_TYPE": ["LOAD", "GEN"],
        "NAME": ["LZ_HOUSTON", "RADIAL_GEN"],
        "LABEL": [None, None],
        "BUSNUM": [1, 2],
        "PSENS": [0.5, 0.95],
        "ISRADIAL": [0.0, 0.0],
        "STATUS": ["Closed", "YES"],
    })

    def fake_dispatchable_shifts(study_id, constraint):
        return shifts

    import pfa.analysis.offer_lambda as ol
    orig = ol.dispatchable_shifts
    ol.dispatchable_shifts = fake_dispatchable_shifts
    try:
        result = ol.dispatch_screen(14411, "8186-8913-1@STHRSCH8")
    finally:
        ol.dispatchable_shifts = orig
    assert result is not None
    assert "unenforceable" in result


def test_dispatch_screen_passes_when_a_dispatchable_device_exists():
    shifts = pd.DataFrame({
        "DEVICE_TYPE": ["LOAD", "GEN"],
        "NAME": ["LZ_HOUSTON", "NORMAL_GEN"],
        "LABEL": [None, None],
        "BUSNUM": [1, 2],
        "PSENS": [0.5, 0.4],
        "ISRADIAL": [0.0, 0.0],
        "STATUS": ["Closed", "YES"],
    })

    import pfa.analysis.offer_lambda as ol
    orig = ol.dispatchable_shifts
    ol.dispatchable_shifts = lambda study_id, constraint: shifts
    try:
        result = ol.dispatch_screen(14411, "1436-2081-1@DWCSRAM5")
    finally:
        ol.dispatchable_shifts = orig
    assert result is None
