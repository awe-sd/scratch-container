import pandas as pd

from pfa.analysis import shortlist_value as sv
from pfa.analysis.shortlist_value import coverage_and_days, month_bind_dates


def _synthetic_runs():
    return pd.DataFrame({"RUNID": [1, 2, 3, 4], "SIMDATE": ["2026-08-01", "2026-08-02", "2026-09-16", "2026-09-17"]})


def _synthetic_ctgviol(binding_runids):
    return pd.DataFrame([
        {"RUNID": rid, "FROMNUM": 100, "TONUM": 200, "CKT": "1", "CTGLABEL": "X",
         "LIMVIOLPCT": 100.0 if rid in binding_runids else 50.0}
        for rid in [1, 2, 3, 4]
    ])


def test_month_bind_dates_proxy():
    runs = _synthetic_runs()
    cv = _synthetic_ctgviol(binding_runids={3})  # binds only one of the two post-cutoff Sept dates
    bind_days, n_sampled = month_bind_dates(cv, runs, "2026-09-15", "2026-09")
    c = "100-200-1@X"
    assert n_sampled == 2
    assert bind_days.get(c, 0) == 1


def test_coverage_ticketed_short_window_sinks():
    """Addendum: a 1-day ticketed outage must get a small coverage fraction,
    not a free pass — 1 day * 16h / 336h ~= 0.048."""
    cov, n_days, marker, thin = coverage_and_days(
        "c1", True, "2026-09-16", "2026-09-16", {}, 0, "2026-09")
    assert n_days == 1
    assert cov < 0.06
    assert thin is True
    assert marker == ""


def test_coverage_unticketed_uses_days_proxy_not_1():
    bind_days = pd.Series({"c1": 2})
    cov, n_days, marker, thin = coverage_and_days("c1", False, None, None, bind_days, 10, "2026-09")
    assert cov == 0.2
    assert marker == "(days-proxy)"
    assert thin is True  # 2 days < 3


def test_coverage_unticketed_thin_flag_clears_at_3_days():
    bind_days = pd.Series({"c1": 3})
    cov, n_days, marker, thin = coverage_and_days("c1", False, None, None, bind_days, 10, "2026-09")
    assert thin is False


def test_coverage_non_september_month():
    cov, n_days, marker, thin = coverage_and_days(
        "c1", True, "2027-03-01", "2027-03-05", {}, 0, "2027-03")
    assert n_days == 5 and cov == round(5 / 23, 3) and not thin


class _FakeCache:
    def __init__(self, study):
        pass

    def load(self, table, columns=None):
        if table == "opfrun":
            return _synthetic_runs()
        if table == "outctgviol2":
            return _synthetic_ctgviol({3}).assign(LIMVIOLLIMIT=100.0)
        if table == "outconstraint2":
            return pd.DataFrame({"RUNID": [3, 4], "FROMNUM": [100, 100], "TONUM": [200, 200], "CKT": ["1", "1"],
                                 "LPOPFCTGID": ["X", "X"], "OPFCNLAMBDA": [10.0, 500.0]})
        return pd.DataFrame(columns=columns or [])


def test_value_shortlist_lookup_failure_is_visible_and_run_continues(monkeypatch, tmp_path):
    from pfa import config
    from pfa.analysis.screening import ScreeningResult, Thresholds

    (tmp_path / "study_1").mkdir()
    pd.DataFrame({"CONSTRAINT": ["100-200-1@X", "100-200-1@Y"], "DRIVER_TICKET": [None, None],
                  "DRIVER_TICKET_START": [None, None], "DRIVER_TICKET_END": [None, None]}
                 ).to_csv(tmp_path / "study_1" / "ranked_constraints.csv", index=False)
    monkeypatch.setattr(config, "OUTPUT_ROOT", tmp_path)
    monkeypatch.setattr(sv, "StudyCache", _FakeCache)
    monkeypatch.setattr(sv.gen_mapping, "fetch_genunit_sced_name", lambda: pd.DataFrame())
    monkeypatch.setattr(sv.gen_mapping, "with_cpnode_names", lambda g: g)
    monkeypatch.setattr(sv.marginal_units, "bus_name_map", lambda b: {})
    monkeypatch.setattr(sv.dam_offers, "latest_delivery_date", lambda: pd.Timestamp("2026-09-26").date())

    def fake_value_row(study, c, *a, out=None):
        if c.endswith("@Y"):
            raise RuntimeError("boom")
        out["_status"] = "no fast-scan config"
        return out

    monkeypatch.setattr(sv, "value_row", fake_value_row)
    short = pd.DataFrame({"x": [1, 2]}, index=["100-200-1@X", "100-200-1@Y"])
    res = ScreeningResult(1, "2026-09-15", Thresholds(), pd.Series(dtype=float), short, pd.DataFrame(), short, short)
    out = sv.value_shortlist(res, "2026-09")
    assert list(out.columns[:1]) == ["x"] and set(sv.value_columns("2026-09")) <= set(out.columns)
    assert out.loc["100-200-1@X", "status"] == "no fast-scan config"
    assert out.loc["100-200-1@X", "coverage"] == "0.5(days-proxy)"
    assert out.loc["100-200-1@Y", "status"] == "lookup failed: RuntimeError: boom"


# ---------------------------------------------------------------- piece 2 --

import pytest

from pfa.analysis import shadow_price as sp
from pfa.analysis.constraints import congestion_rent


def _units(sides, n_band=None):
    return pd.DataFrame({"SCED": [f"U{i}" for i in range(len(sides))], "SIDE": sides})


def _cap(n):
    return pd.DataFrame({"P60": [1.0] * n}, index=[f"U{i}" for i in range(n)])


W = "2026-09-12..2026-09-26"


def test_offer_window_text_is_anchored_on_the_newest_date():
    assert sv.offer_window_text("2026-09-26") == W


@pytest.mark.parametrize("relief,expect", [
    (sp.ReliefSet(pd.DataFrame(), n_band=0), "no relief units in SF band"),
    (sp.ReliefSet(pd.DataFrame(), n_band=51), "51 in-band units, 0 mapped to a settlement point"),
    (sp.ReliefSet(_units(["up", "down"]), pd.DataFrame(), n_band=5), f"2 mapped units, 0 with DAM offers in {W}"),
    (sp.ReliefSet(_units(["up", "up"]), _cap(2), [], [{"x": 1}], n_band=5), "no units on the up side"),
    (sp.ReliefSet(_units(["up", "down"]), _cap(2), [{"x": 1}], [], n_band=5), "no units on the down side"),
    (sp.ReliefSet(_units(["up", "down"]), _cap(1), [], [], n_band=5), "no units on either side with a usable offer"),
])
def test_relief_status_names_the_failing_step(relief, expect):
    assert sv.relief_status(relief, W).startswith(expect)


def test_relief_status_none_when_both_stacks_have_units():
    assert sv.relief_status(sp.ReliefSet(_units(["up", "down"]), _cap(2), [{}], [{}], n_band=2), W) is None


def _patch_value_row(monkeypatch, curve_up, curve_down, need_mw, path=True):
    monkeypatch.setattr(sv.fastscan, "find_configs", lambda *a: pd.DataFrame({"CONFIG_ID": [1], "DIRECTION": [1]}))
    need = pd.DataFrame({"NEED_MW": need_mw})
    monkeypatch.setattr(sv, "fastscan_month_onpeak", lambda cid, m: (0.5, need, 100, [2022, 2024]))
    rs = sp.ReliefSet(_units(["up", "down"]), _cap(2), curve_up, curve_down, n_band=2)
    monkeypatch.setattr(sv.sp, "relief_set", lambda *a, **k: rs)
    paths = pd.DataFrame({"SOURCENAME": ["S"], "SINKNAME": ["K"], "OPTIONPRICE": [1.0], "AVG_SF": [0.3]}) if path else None
    monkeypatch.setattr(sv.popt, "best_paths", lambda *a: paths)
    monkeypatch.setattr(sv, "cpnode_sf", lambda *a: {})


def _stack(price_up, price_down, sf_up=-0.2, sf_down=0.2, avail=10.0):
    return ([{"sced": "U0", "sf": sf_up, "price": price_up, "avail": avail, "committed": True}],
            [{"sced": "U1", "sf": sf_down, "price": price_down, "avail": avail}])


def test_value_row_free_relief_gets_its_own_status_not_ok(monkeypatch):
    up, down = _stack(-5.0, 30.0)
    _patch_value_row(monkeypatch, up, down, [1.0, 2.0])
    out = sv.value_row(1, "100-200-1@X", None, None, None, None, "2026-09", W)
    assert out["_status"] == "relief set covers 100.0% of binding hours (1 curve step)"  # 1 step: never "priced at 0"
    assert out["E[lambda|bind]"] == 0.0 and out["lambda P50"] == 0 and out["lambda P90"] == 0
    assert out["_elam_high"] is None  # a $0 last step is not a ceiling


def _free_curve_inputs(n_steps):
    up = [{"sced": f"U{i}", "sf": -0.2, "price": float(-5 - i), "avail": 10.0, "committed": True} for i in range(n_steps)]
    down = [{"sced": f"D{i}", "sf": 0.2, "price": 30.0, "avail": 10.0} for i in range(n_steps)]
    return up, down


def test_value_row_priced_at_zero_only_for_a_deep_curve_covering_the_hours(monkeypatch):
    up, down = _free_curve_inputs(3)  # 3 free steps of 4 MW flow each = 12 MW
    _patch_value_row(monkeypatch, up, down, [1.0, 5.0, 9.0])
    out = sv.value_row(1, "100-200-1@X", None, None, None, None, "2026-09", W)
    assert out["_n_steps"] == 3 and out["_status"] == "priced at 0: cheapest step is free relief"


def test_value_row_thin_curve_or_mostly_unpriced_hours_says_what_the_relief_set_covers(monkeypatch):
    up, down = _free_curve_inputs(3)
    _patch_value_row(monkeypatch, up, down, [1.0] + [50.0] * 199)  # 3 steps, 99.5% of hours beyond the 12 MW curve
    out = sv.value_row(1, "100-200-1@X", None, None, None, None, "2026-09", W)
    assert out["unpriced deep hours %"] == 99.5 and out["_status"] == "relief set covers 0.5% of binding hours (3 curve steps)"
    assert out["_elam_high"] is None and out["_n_neg_hours"] == 200


def test_value_row_start_required_mw_and_share(monkeypatch):
    up, down = _stack(30.0, 10.0)
    up[0]["committed"] = False
    _patch_value_row(monkeypatch, up, down, [1.0, 2.0])
    out = sv.value_row(1, "100-200-1@X", None, None, None, None, "2026-09", W)
    assert out["_startreq_mw"] == out["_curve_mw"] == 4.0


def test_need_summary_bands_match_the_row_columns(monkeypatch):
    up, down = _stack(30.0, 10.0)
    _patch_value_row(monkeypatch, up, down, [1.0, 2.0, 3.0, 10.0])
    out = sv.value_row(1, "100-200-1@X", None, None, None, None, "2026-09", W)
    ns = sv.need_summary(sp.lambda_depth_curve(up, down), [1.0, 2.0, 3.0, 10.0])
    assert (ns["mean"], ns["p50"], ns["p90"], ns["unpriced_pct"]) == (
        out["E[lambda|bind]"], out["lambda P50"], out["lambda P90"], out["unpriced deep hours %"])
    assert ns["n_neg"] == out["_n_neg_hours"] == 4 and ns["bands"][0]["hours"] == 3 and ns["beyond_hours"] == 1 and ns["beyond_share"] == 0.25


def test_value_row_bounds_path_numbers_and_pbind_basis(monkeypatch):
    up, down = _stack(30.0, 10.0)  # lambda = 20/0.4 = 50 for 10 MW * 0.4 = 4 MW of flow
    _patch_value_row(monkeypatch, up, down, [1.0, 2.0, 3.0, 10.0])
    out = sv.value_row(1, "100-200-1@X", None, None, None, None, "2026-09", W)
    assert out["_status"] == "relief set covers 75.0% of binding hours (1 curve step)"
    assert out["E[lambda|bind]"] == 50.0 and out["unpriced deep hours %"] == 25.0  # the 10 MW hour exceeds 4 MW of capacity
    assert out["_elam_low"] == 37.5 and out["_elam_high"] == 50.0  # 3 priced hours at 50, one at 0 / at the last step
    assert out["_eff_sf"] == 0.3 and out["_sf_approx"] is True and out["_path_price"] == 1.0
    assert out["Path SF"] == "~0.300"
    assert out["_pbind_hours"] == 100 and out["_pbind_years"] == "2022, 2024"
    assert (out["_n_band"], out["_n_mapped"], out["_n_up"], out["_n_down"], out["_n_steps"]) == (2, 2, 1, 1, 1)


def test_bounds_bracket_the_existing_value():
    lo, hi, elo, ehi = sv._bounds(0.5, 0.8, 37.5, 50.0, 0.3, 1.0)
    assert (lo, hi) == (15.0, 20.0) and (elo, ehi) == (round(15 * 0.3 - 1, 2), round(20 * 0.3 - 1, 2))
    assert sv._bounds(0.5, None, 1.0, 1.0, 0.3, 1.0) == (None, None, None, None)
    assert sv._bounds(0.5, 1.0, 1.0, 2.0, None, None)[2:] == (None, None)


def test_ticket_dead_state():
    assert sv.ticket_dead_state("Rejct") == "Rejct"
    assert sv.ticket_dead_state("Apprv") is None and sv.ticket_dead_state("RatE") is None
    assert sv.ticket_dead_state("Apprv", "2026-09-20") == "Apprv"  # a cancellation date kills the ticket
    assert sv.ticket_dead_state(None, "2026-09-20") == "cancelled"
    assert sv.ticket_dead_state(float("nan")) is None


def test_binding_run_sets_and_sibling_notes():
    cv = pd.concat([
        pd.DataFrame({"RUNID": r, "FROMNUM": f, "TONUM": t, "CKT": "1", "CTGLABEL": g, "LIMVIOLPCT": 100.0})
        for f, t, g, runs in [(1, 2, "A", range(10)), (1, 2, "B", range(10)),   # identical run set, same line
                              (3, 4, "A", range(1, 11)),                         # 9/10 overlap, other line -> corridor
                              (5, 6, "A", range(20, 30)),                      # disjoint
                              (7, 8, "A", range(5))]                           # 5/10: neither
        for r in [list(runs)]])
    rs = sv.binding_run_sets(cv)
    assert rs["1-2-1@A"] == frozenset(range(10)) and len(rs) == 5
    notes = sv.sibling_notes(["1-2-1@A", "5-6-1@A", "9-9-1@Z"], rs)
    assert notes["1-2-1@A"].startswith("sibling contingency of 1-2-1@B (identical run set; do not add rents); corridor with 3-4-1@A (overlap 9/10)")
    assert "7-8-1@A" not in notes["1-2-1@A"]  # a 5-run set is too small to name a corridor
    assert notes["5-6-1@A"] == "" and notes["9-9-1@Z"] == ""


def test_rent_ex_penalty_drops_exactly_the_tier_rows():
    runs = pd.DataFrame({"RUNID": [1, 2, 3], "SIMDATE": ["2026-09-16"] * 3})
    cv = pd.DataFrame({"RUNID": [1, 2, 3], "FROMNUM": 1, "TONUM": 2, "CKT": "1", "CTGLABEL": "A", "LIMVIOLLIMIT": 100.0})
    oc = pd.DataFrame({"RUNID": [1, 2, 3], "FROMNUM": 1, "TONUM": 2, "CKT": "1", "LPOPFCTGID": "A", "OPFCNLAMBDA": [10.0, 500.0, 3500.0]})
    full = congestion_rent(cv, oc, runs, "2026-09-15").set_index("CONSTRAINT")["RENT_POST"]["1-2-1@A"]
    ex = congestion_rent(cv, oc, runs, "2026-09-15", exclude_lambda=(500.0, 3500.0)).set_index("CONSTRAINT")["RENT_POST"]["1-2-1@A"]
    assert full == 10 * 100 + 500 * 100 + 3500 * 100 and ex == 1000


def test_value_shortlist_dead_ticket_blank_coverage_and_added_columns(monkeypatch, tmp_path):
    from pfa import config
    from pfa.analysis.screening import ScreeningResult, Thresholds

    (tmp_path / "study_1").mkdir()
    pd.DataFrame({"CONSTRAINT": ["100-200-1@X"], "DRIVER_TICKET": ["T1"], "DRIVER_TICKET_STATUS": ["Rejct"],
                  "DRIVER_TICKET_START": ["2026-09-16"], "DRIVER_TICKET_END": ["2026-09-18"], "DRIVER_TICKET_CANCELLED": [None]}
                 ).to_csv(tmp_path / "study_1" / "ranked_constraints.csv", index=False)
    monkeypatch.setattr(config, "OUTPUT_ROOT", tmp_path)
    monkeypatch.setattr(sv, "StudyCache", _FakeCache)
    monkeypatch.setattr(sv.gen_mapping, "fetch_genunit_sced_name", lambda: pd.DataFrame())
    monkeypatch.setattr(sv.gen_mapping, "with_cpnode_names", lambda g: g)
    monkeypatch.setattr(sv.marginal_units, "bus_name_map", lambda b: {})
    monkeypatch.setattr(sv.dam_offers, "latest_delivery_date", lambda: pd.Timestamp("2026-09-26").date())
    monkeypatch.setattr(sv, "value_row", lambda *a, out=None: out.update(
        {"_status": "no relief units in SF band", "P(bind) Sept on-peak": 0.4, "E[lambda|bind]": 10.0, "_elam_low": 8.0,
         "_elam_high": 12.0, "_eff_sf": 0.5, "_path_price": 1.0, "_sf_approx": False}))
    short = pd.DataFrame({"x": [1]}, index=["100-200-1@X"])
    res = ScreeningResult(1, "2026-09-15", Thresholds(), pd.Series(dtype=float), short, pd.DataFrame(), short, short)
    out = sv.value_shortlist(res, "2026-09")
    r = out.loc["100-200-1@X"]
    assert r["status"] == "driver ticket Rejct" and r["valuation detail"] == "no relief units in SF band"
    assert pd.isna(r["coverage"]) and pd.isna(r["Sept value $/MWh/SF"]) and pd.isna(r["Sept value LOW $/MWh/SF"])
    assert r["Outage-day basis"] == "ticket (Rejct)" and r["Path price $/MWh"] == 1.0 and r["Path SF value"] == 0.5
    assert r["offer window"] == "2026-09-12..2026-09-26" and r["Post days sampled"] == 2
    assert r["Rent post-9/15 ex-penalty ($)"] == 1000.0  # the 500 tier row is dropped; 10 * 100
    assert set(sv.added_columns("2026-09", "2026-09-15")) <= set(out.columns)
    assert list(out.columns[:1]) == ["x"] and list(out.columns[1:14]) == sv.value_columns("2026-09")


def test_sibling_notes_parallel_element_vs_sibling_contingency_and_smaller_set_corridor():
    cv = pd.concat([
        pd.DataFrame({"RUNID": list(runs), "FROMNUM": f, "TONUM": t, "CKT": "1", "CTGLABEL": g, "LIMVIOLPCT": 100.0})
        for f, t, g, runs in [(1, 2, "A", range(10)), (3, 4, "A", range(10)),   # same ctg, different element, identical runs
                              (1, 2, "B", range(10)),                           # same element, different ctg
                              (5, 6, "C", range(100, 114)), (7, 8, "C", range(100, 113)),   # 13/13 of the smaller set
                              (9, 10, "D", range(1000, 1010)),
                              (11, 12, "E", range(100, 103))]])  # 3/3 inside C, but under the minimum run count
    notes = sv.sibling_notes(["3-4-1@A", "7-8-1@C", "5-6-1@C"], sv.binding_run_sets(cv))
    assert "parallel element of 1-2-1@A (identical run set; do not add rents)" in notes["3-4-1@A"]
    assert "sibling contingency of 1-2-1@B" in sv.sibling_notes(["1-2-1@A"], sv.binding_run_sets(cv))["1-2-1@A"]
    assert notes["7-8-1@C"] == "corridor with 5-6-1@C (overlap 13/13)"
    assert notes["5-6-1@C"] == "corridor with 7-8-1@C (overlap 13/13)"  # the 3-run set 11-12 is not named


def test_relaxation_flag_needs_high_ex_cap_p50_and_not_a_penalty_tier():
    assert sv.relaxation_flag(2010.3, 1846.4) is True
    assert sv.relaxation_flag(598.0, 598.0) is False and sv.relaxation_flag(3500.0, 1800.0) is False
    assert sv.relaxation_flag(float("nan"), float("nan")) is False


def test_bounds_blank_high_when_last_step_is_free():
    assert sv._bounds(0.3, 1.0, 0.0, None, 0.5, 2.0) == (0.0, None, -2.0, None)
