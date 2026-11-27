"""Shadow-price module: qualification rule, formula, SCED-name mapping, depth curve, pair price."""
from __future__ import annotations

import pandas as pd
import pytest

from pfa.analysis import shadow_price
from pfa.analysis.shadow_price import lambda_at_depth, lambda_depth_curve

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
    out = shadow_price.sced_names(pair, bus_names, genunit, scedname).set_index(["BUSNUM", "ID"])
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
    out = shadow_price.sced_names(pair, bus_names, genunit, scedname)
    assert out["SCED"].iloc[0] == "SOLOBUS_GEN"




# Synthetic relief set: two UP units (negative SF), one DOWN unit (positive SF).
UP = [
    {"sced": "UP1", "sf": -0.5, "price": 20.0, "avail": 50.0},
    {"sced": "UP2", "sf": -0.3, "price": 30.0, "avail": 100.0},
]
DOWN = [
    {"sced": "DN1", "sf": 0.4, "price": 10.0, "avail": 80.0},
]

# By hand:
#   UP1/DN1: dsf = 0.4 - (-0.5) = 0.9, lambda = (20-10)/0.9 = 11.11
#   UP2/DN1: dsf = 0.4 - (-0.3) = 0.7, lambda = (30-10)/0.7 = 28.57
# Greedy always prefers the cheaper pair first (UP1/DN1, lambda=11.11):
#   consumes min(50, 80) = 50 MW of generation * dsf 0.9 = 45 MW of flow.
#   UP1 exhausted; DN1 has 30 MW of generation headroom left.
# Then UP2/DN1 (lambda=28.57) is the only pair left:
#   consumes min(100, 30) = 30 MW * dsf 0.7 = 21 MW of flow -> depth 45 -> 66.
#   DN1 exhausted; stack empties.


def test_pair_stack_two_step_curve():
    curve = lambda_depth_curve(UP, DOWN, max_depth=500)
    assert len(curve) == 2
    assert curve[0]["depth_lo"] == 0.0
    assert round(curve[0]["depth_hi"], 2) == 45.0
    assert curve[0]["lambda"] == round(10.0 / 0.9, 2)
    assert round(curve[1]["depth_hi"], 2) == 66.0
    assert curve[1]["lambda"] == round(20.0 / 0.7, 2)


def test_lambda_nondecreasing_in_depth():
    curve = lambda_depth_curve(UP, DOWN, max_depth=500)
    lambdas = [s["lambda"] for s in curve]
    assert lambdas == sorted(lambdas)


def test_negative_priced_pair_floors_at_zero_not_negative():
    """Regression for the study-14412 bug on 3380-3390-1@DPNAONA5: when the
    UP mover's offer is CHEAPER than the DOWN mover's offer, the raw
    (u.price - d.price)/dsf is negative. By LP duality a binding max-flow
    constraint's shadow price can never be negative (the LP would take a
    genuinely profitable redispatch on its own, constraint or not) — that
    pair is free relief, not "negative-cost" relief, and must be recorded as
    lambda=0, not a negative number. It should still be preferred (consumed
    first) precisely because it's free."""
    up = [{"sced": "CHEAP_UP", "sf": -0.2, "price": 5.0, "avail": 40.0}]
    down = [{"sced": "EXPENSIVE_DOWN", "sf": 0.2, "price": 80.0, "avail": 40.0}]
    curve = lambda_depth_curve(up, down, max_depth=500)
    assert len(curve) == 1
    assert curve[0]["lambda"] == 0.0
    assert curve[0]["lambda"] >= 0.0


def test_free_pair_consumed_before_a_pricier_one():
    """A free (negative-raw-lambda) pair must still be exhausted before a
    genuinely-priced one, so the curve stays non-decreasing after flooring."""
    up = [
        {"sced": "FREE_UP", "sf": -0.2, "price": 5.0, "avail": 10.0},   # vs DOWN1: free
        {"sced": "PRICEY_UP", "sf": -0.2, "price": 50.0, "avail": 100.0},
    ]
    down = [{"sced": "DOWN1", "sf": 0.2, "price": 80.0, "avail": 10.0}]
    curve = lambda_depth_curve(up, down, max_depth=500)
    assert curve[0]["pair"].startswith("DOWN1")
    assert curve[0]["lambda"] == 0.0
    lambdas = [s["lambda"] for s in curve]
    assert lambdas == sorted(lambdas)


def test_lambda_at_depth_lookup():
    curve = lambda_depth_curve(UP, DOWN, max_depth=500)
    assert lambda_at_depth(curve, 25) == round(10.0 / 0.9, 2)
    assert lambda_at_depth(curve, 50) == round(20.0 / 0.7, 2)
    assert lambda_at_depth(curve, 60) == round(20.0 / 0.7, 2)
    # beyond the curve entirely (stacks exhausted at 66) -> None: this
    # relief set genuinely cannot supply that much relief, it is not
    # "priced at the last band forever"
    assert lambda_at_depth(curve, 1000) is None


def test_qualifying_band_edges_are_inclusive_and_symmetric():
    sf = pd.Series([0.0299, 0.03, -0.03, 0.5, 0.9, -0.9, 0.9001, -0.9001])
    assert shadow_price.qualifying(sf).tolist() == [False, True, True, True, True, True, False, False]
    assert (shadow_price.MIN_SF, shadow_price.MAX_SF) == (0.03, 0.9)
    assert (shadow_price.PAIR_MIN_SF, shadow_price.PAIR_MAX_SF) == (0.1, 0.5)


def test_offer_lambda_capped():
    lo, hi = shadow_price.offer_lambda_range(7.0, 60.0, 0.18)
    assert round(lo, 1) == 38.9 and round(hi, 1) == 333.3
    assert shadow_price.offer_lambda_range(2000.0, 3000.0, 0.1)[1] == shadow_price.PRICE_CAP
    with pytest.raises(ValueError):
        shadow_price.offer_lambda_range(1.0, 2.0, 0.0)


def test_clamp_price_floors_and_caps():
    assert shadow_price.clamp_price(-3.0) == 0.0
    assert shadow_price.clamp_price(1e9) == shadow_price.PRICE_CAP


def _pair_inputs(p60_up, p90_up, p60_down):
    up = pd.DataFrame({"SCED": ["UP1"], "SF": [-0.5]})
    down = pd.DataFrame({"SCED": ["DN1"], "SF": [0.4]})
    offers = pd.DataFrame({"P60": [p60_up, p60_down], "P90": [p90_up, p60_down]}, index=["UP1", "DN1"])
    return up, down, offers


def test_pair_price_matches_first_curve_step_for_one_up_one_down():
    """Same P60 offers, one up and one down unit: the pair floor equals the curve's first step
    (pair rounds to 1 decimal, the curve to 2); the pair ceiling uses P90 of the up unit."""
    up, down, offers = _pair_inputs(20.0, 29.0, 10.0)
    est = shadow_price.pair_price(up, down, offers)
    curve = lambda_depth_curve([{"sced": "UP1", "sf": -0.5, "price": 20.0, "avail": 50.0}],
                               [{"sced": "DN1", "sf": 0.4, "price": 10.0, "avail": 80.0}])
    assert est["lam_lo"] == round(curve[0]["lambda"], 1) == 11.1
    assert est["lam_hi"] == round(19.0 / 0.9, 1)
    assert est["dsf"] == 0.9 and est["pair"] == "DN1↓/UP1↑ → DN1↓/UP1↑"


def test_pair_price_floors_negative_spread_and_caps_like_the_curve():
    up, down, offers = _pair_inputs(5.0, 5.0, 80.0)
    est = shadow_price.pair_price(up, down, offers)
    curve = lambda_depth_curve([{"sced": "UP1", "sf": -0.5, "price": 5.0, "avail": 10.0}],
                               [{"sced": "DN1", "sf": 0.4, "price": 80.0, "avail": 10.0}])
    assert est["lam_lo"] == curve[0]["lambda"] == 0.0
    up, down, offers = _pair_inputs(9000.0, 9000.0, 0.0)
    assert shadow_price.pair_price(up, down, offers)["lam_hi"] == shadow_price.PRICE_CAP


def test_pair_price_requires_dsf_of_at_least_0_02():
    up = pd.DataFrame({"SCED": ["UP1"], "SF": [0.1]})
    down = pd.DataFrame({"SCED": ["DN1"], "SF": [0.11]})
    offers = pd.DataFrame({"P60": [20.0, 10.0], "P90": [20.0, 10.0]}, index=["UP1", "DN1"])
    assert shadow_price.pair_price(up, down, offers) is None


# ---- offer key: CPNODE id route primary, SCED-name route fallback ----

def _map_inputs():
    pair = pd.DataFrame({"BUSNUM": [1, 2, 3, 4], "ID": ["1", "1", "1", "1"], "SIDE": ["up"] * 4, "DIFF_MW": [1.0] * 4})
    bus_names = pd.DataFrame({"BUSNUM": [1, 2, 3, 4], "BUSNAME": ["B1", "B2", "B3", "B4"]})
    genunit = pd.DataFrame({
        "GENUNITID": [11, 12, 13, 14], "BUSNAME": ["B1", "B2", "B3", "B4"],
        "CPNODEID": [101.0, 102.0, None, 104.0],
        "CPNODENAME": ["RN_PLANT_A", None, None, "NODE_NO_SCED"],  # 102: CPNODEID has no CPNODE row; 103: null id
    })
    scedname = pd.DataFrame({"GENUNITID": [11, 12, 13], "NAME": ["PLANT_A_1", "PEAKER_2_1", "OLD_UNIT_1"], "KIND": ["GEN"] * 3})
    return pair, bus_names, genunit, scedname


def test_sced_names_uses_cpnode_name_and_records_route():
    out = shadow_price.sced_names(*_map_inputs()).set_index("BUSNUM")
    assert out.loc[1, "SCED"] == "RN_PLANT_A" and out.loc[1, "OFFER_ROUTE"] == "cpnode"
    assert out.loc[1, "SCED_NAME"] == "PLANT_A"  # the name route's key stays available


def test_sced_names_falls_back_to_name_when_cpnodeid_null_or_unresolved():
    out = shadow_price.sced_names(*_map_inputs()).set_index("BUSNUM")
    assert out.loc[2, "SCED"] == "PEAKER_2" and out.loc[2, "OFFER_ROUTE"] == "name"
    assert out.loc[3, "SCED"] == "OLD_UNIT" and out.loc[3, "OFFER_ROUTE"] == "name"


def test_sced_names_maps_a_node_with_no_sced_row_and_leaves_unknown_unmapped():
    pair, bus_names, genunit, scedname = _map_inputs()
    out = shadow_price.sced_names(pair, bus_names, genunit, scedname).set_index("BUSNUM")
    assert out.loc[4, "SCED"] == "NODE_NO_SCED" and out.loc[4, "OFFER_ROUTE"] == "cpnode"
    no_cp = shadow_price.sced_names(pair, bus_names, genunit.drop(columns="CPNODENAME"), scedname).set_index("BUSNUM")
    assert (no_cp["OFFER_ROUTE"].dropna() == "name").all() and pd.isna(no_cp.loc[4, "SCED"])


def _relief_fixture(monkeypatch, offered):
    """Units 1 and 2 share one resource node (many-to-one, same side); unit 3 is a combined cycle whose CPNODE name has no offers."""
    gen = pd.DataFrame({"BUSNUM": [1, 2, 3], "ID": ["1", "1", "1"], "FUELTYPE": ["NG", "NG", "NG"], "MW": [1.0] * 3, "MWMAX": [2.0] * 3})
    bus_names = pd.DataFrame({"BUSNUM": [1, 2, 3], "BUSNAME": ["B1", "B2", "B3"]})
    genunit = pd.DataFrame({"GENUNITID": [11, 12, 13], "BUSNAME": ["B1", "B2", "B3"], "CPNODEID": [1.0, 1.0, 2.0],
                            "CPNODENAME": ["RN_SHARED", "RN_SHARED", "CC_UNIT_NODE"]})
    scedname = pd.DataFrame({"GENUNITID": [11, 12, 13], "NAME": ["SHARED_G1_1", "SHARED_G2_1", "PLANT_CC1_1"], "KIND": ["GEN"] * 3})
    monkeypatch.setattr(shadow_price.shifts, "bus_sf_all_buses",
                        lambda *a, **k: pd.DataFrame({"BUSNUM": [1, 2, 3], "SF": [-0.30, -0.20, -0.10]}))
    asked = []

    def cap(points, hours=(7, 22)):
        asked.append(set(points))
        idx = [p for p in points if p in offered]
        return pd.DataFrame({"P60": 10.0, "HSL": 100.0, "LSL": 0.0, "AWARDED": 0.0}, index=pd.Index(idx, name="SETTLEMENTPOINTNAME"))

    monkeypatch.setattr(shadow_price, "dam_capacity", cap)
    return shadow_price.relief_set(1, "1-2-1@X", gen, bus_names, genunit, scedname), asked


def test_relief_set_many_to_one_counts_a_shared_offer_curve_once(monkeypatch):
    rs, _ = _relief_fixture(monkeypatch, {"RN_SHARED", "PLANT_CC1"})
    shared = rs.units[rs.units["SCED"] == "RN_SHARED"]
    assert len(shared) == 1 and shared["SF"].iloc[0] == -0.30  # strongest |SF| kept
    assert [b["sced"] for b in rs.up].count("RN_SHARED") == 1


def test_relief_set_cpnode_key_without_offers_falls_back_to_name_key(monkeypatch):
    rs, asked = _relief_fixture(monkeypatch, {"RN_SHARED", "PLANT_CC1"})
    cc = rs.units.set_index("SCED").loc["PLANT_CC1"]
    assert cc["OFFER_ROUTE"] == "name" and "PLANT_CC1" in rs.capacity.index
    assert rs.units.set_index("SCED").loc["RN_SHARED", "OFFER_ROUTE"] == "cpnode"
    assert {"CC_UNIT_NODE", "PLANT_CC1"} <= asked[0]  # both candidate keys are looked up in one pull


def test_relief_set_keeps_cpnode_route_when_neither_key_has_offers(monkeypatch):
    rs, _ = _relief_fixture(monkeypatch, set())
    assert set(rs.units["OFFER_ROUTE"]) == {"cpnode"} and rs.capacity.empty
