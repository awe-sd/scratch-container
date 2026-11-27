import numpy as np
import pandas as pd

from pfa.analysis import deep_dive as dd
from pfa.report import deep_dive as dd_report

C = dict(fromnum=1, tonum=2, ckt="1", ctglabel="X", label="L1", fromname="AAA_1", toname="BBB_1", direction=1,
         key="1-2-1@X", n_binding_runs=2)


def _hours(n=24 * 30):
    return pd.date_range("2026-09-01", periods=n, freq="h")


def _stub_extras(monkeypatch, ts, load_mw, pooled=(0.13, None, 1312, [2022, 2023]), cfg_end="2026-06-10"):
    load = pd.DataFrame({"date": ts.normalize().date, "he": ts.hour + 1, "load_mw": load_mw, "year": ts.year})
    monkeypatch.setattr(dd.load_reader, "get_load_window", lambda year, a, b, zone="ERCOT": load.copy())
    monkeypatch.setattr(dd.shortlist_value, "fastscan_month_onpeak", lambda cid, month: pooled)
    monkeypatch.setattr(dd.fastscan, "timestamp_span", lambda cid: (pd.Timestamp("2022-01-01"), pd.Timestamp(cfg_end), 9999))


def test_binding_conditions_wind_driven_and_hour_stays_clock_hour(monkeypatch):
    ts = _hours()
    wind_mw = np.tile(np.linspace(1000, 9000, 24), 30)
    hr = pd.DataFrame({"TIMESTAMP": ts, "HEADROOM": (wind_mw - 5000) / 100, "HEADROOM_RT": 0.0, "HEADROOM_AFTER_CURTAILMENT": 0.0})
    wind = pd.DataFrame({"TimeStamp": ts, "windRegion": "West", "avgHSLPct": wind_mw / 100.0,
                         "totalInstalledCapacityMW": 10000.0})
    solar = pd.DataFrame({"TimeStampDate": ts.normalize(), "HE": ts.hour + 1, "solarGen": 0.0, "solarMax": 1.0})
    monkeypatch.setattr(dd.fastscan, "headroom_window", lambda *a: hr.copy())
    monkeypatch.setattr(dd.renewables, "wind_region_hourly", lambda *a, **k: wind.copy())
    monkeypatch.setattr(dd.renewables, "solar_hourly", lambda *a, **k: solar.copy())
    _stub_extras(monkeypatch, ts, np.tile(np.linspace(40000, 50000, 24), 30))
    out = dd.binding_conditions(5, "2026-09-01", "2026-10-01", "2026-09")
    assert not out["empty"] and out["n_hours"] == len(ts)
    assert out["corr"]["SYSTEM_WIND_MW"] is not None
    assert set(out["hour_of_day_neg_rate"]) == set(range(24))
    assert out["driver"]["kind"] in ("wind", "solar", "load", "mixed", "none")
    assert out["month_name"] == "September"
    assert out["span"]["start"] == ts[0] and out["span"]["end"] == ts[-1] and out["n_month_hours"] == len(ts)


def test_binding_conditions_empty(monkeypatch):
    monkeypatch.setattr(dd.fastscan, "headroom_window", lambda *a: pd.DataFrame())
    assert dd.binding_conditions(5, "a", "b", "2026-09") == {"empty": True}


def test_dispatch_profile_filters_dedups_and_signs(monkeypatch):
    nodes = pd.DataFrame({"NAME": ["G1", "G1", "G2", "G3"], "CPNODEID": [1, 1, 2, 3],
                          "PSENS": [0.2, 0.2, -0.3, 0.001], "N": [10, 5, 10, 10]})
    monkeypatch.setattr(dd.shifts, "cpnode_live_nodes", lambda *a: nodes.copy())
    genunit = pd.DataFrame({"CPNODEID": [1, 2], "GENFUELTYPE": ["GAS", "WIND"], "RESOURCE_TYPE": ["CC", "WGR"]})
    out = dd.dispatch_profile(1, C, genunit, pd.DataFrame())
    assert list(out["NAME"]) == ["G2", "G1"]  # |PSENS| desc, duplicate row collapsed, G3 below MIN_SF dropped
    assert dict(zip(out["NAME"], out["RELIEF_OR_HARM"])) == {"G2": "relief (up relieves)", "G1": "harm (up loads)"}
    out = dd.dispatch_profile(1, {**C, "direction": -1}, genunit, pd.DataFrame())
    assert dict(zip(out["NAME"], out["EFFECTIVE_SIGN"])) == {"G2": 1.0, "G1": -1.0}


def test_price_formation_lp_stats_and_marginal_units(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("no offers")
    monkeypatch.setattr(dd.shadow_price, "relief_set", boom)
    ctg = pd.DataFrame({"RUNID": [1, 2, 3], "FROMNUM": 1, "TONUM": 2, "CKT": "1", "CTGLABEL": "X", "LIMVIOLPCT": [100.0, 100.0, 50.0]})
    oc = pd.DataFrame({"RUNID": [1, 2, 3], "FROMNUM": 1, "TONUM": 2, "CKT": "1", "LPOPFCTGID": "X", "OPFCNLAMBDA": [10.0, 500.0, 99.0]})
    gen = pd.DataFrame({"RUNID": [1, 1, 3], "BUSNUM": [7, 8, 7], "ID": "1", "FUELTYPE": "GAS", "MW": [5.0, 1.0, 5.0],
                        "MWMIN": [0.0, 1.0, 0.0], "MWMAX": [10.0, 10.0, 10.0], "BUSMARGCOSTMW": [20.0, 20.0, 20.0],
                        "EDMARGCOSTMW": [20.5, 20.0, 20.0]})
    monkeypatch.setattr(dd.shifts, "bus_sf_for_buses", lambda *a: pd.DataFrame({"BUSNUM": [7], "SF": [0.01]}))
    out = dd.price_formation(1, C, ctg, oc, gen, pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
    assert out["lp_stats"] == {"n": 2, "n_binding_runs": 2, "min": 10.0, "mean": 255.0, "p50": 255.0, "max": 500.0, "pct_penalty_tier": 0.5}
    assert list(out["marginal_units"]["BUSNUM"]) == [7] and out["structural_lambda"] == {"error": "no offers"}
    assert out["marginal_units"]["PRICE_SETTER"].iloc[0].startswith("no: abs(SF) < 0.03")  # SF 0.01 is below the price-setter band


def _tofinder():
    rows = []
    for key, grp, delta in [("1-2-1@X", "OUT_A", 50.0), ("1-2-1@X", "OUT_B", -20.0), ("3-4-1@Y", "AAA_LINE", 40.0)]:
        f, t, ckt = key.split("@")[0].split("-")
        rows.append({"FROMNUM_TARGET": int(f), "TONUM_TARGET": int(t), "CKT_TARGET": ckt, "CTGLABEL": key.split("@")[1],
                     "OUTAGE_GROUP": grp, "RUNID": 1, "FLOWDELTA": delta, "PREGROUPOUTLINEFLOW": 0.0})
    return pd.DataFrame(rows)


class _Cache:
    def load(self, name):
        return _tofinder()


def test_flip_attribution_sorts_by_signed_delta_and_synthesis_facts():
    c2 = {**C, "fromnum": 3, "tonum": 4, "ctglabel": "Y", "key": "3-4-1@Y", "label": "L2", "fromname": "CCC_1", "toname": "DDD_1", "direction": -1}
    flip = dd.flip_attribution(_Cache(), [C, c2])
    l1 = flip[flip["LABEL"] == "L1"]
    assert list(l1["OUTAGE_GROUP"]) == ["OUT_A", "OUT_B"]
    assert float(flip[flip["LABEL"] == "L2"]["SIGNED_FLOWDELTA"].iloc[0]) == -40.0
    d = pd.DataFrame({"NAME": ["N1"], "EFFECTIVE_SIGN": [-1.0], "PSENS": [0.1]})
    d2 = pd.DataFrame({"NAME": ["N1"], "EFFECTIVE_SIGN": [1.0], "PSENS": [-0.2]})
    facts = dd.flip_synthesis_facts([{"c": C, "dispatch": d}, {"c": c2, "dispatch": d2}], flip)
    assert facts["sign_flip"]["name"] == "N1" and not facts["c0_names_c1"] and facts["c1_names_c0"]
    text = "\n".join(dd_report._flip_synthesis(facts, flip))
    assert "opposite effect" in text and "L2's top-ranked outage groups" in text
    assert dd.flip_attribution(_Cache(), [C]).empty and dd.flip_synthesis_facts([{"c": C}], flip) is None


def test_report_labels_fastscan_hours_hour_ending():
    bc = {"empty": False, "hour_of_day_neg_rate": {0: 0.1, 23: 0.9, 16: 0.5}, "month_name": "September", "config_id": 1,
          "n_hours": 3, "n_wind_matched": 3, "n_solar_matched": 3, "corr": {}, "system_wind_cap_mw": 1.0,
          "dominant_wind_region": None, "triggers": {}, "pct_neg_onpeak_month": 1.0, "pct_neg_offpeak_month": 1.0,
          "driver": {"kind": "none", "lead": None, "wind_corr": None, "solar_corr": None, "load_corr": None, "peak_hour": 23},
          "window": {"start": "2026-04-01", "end": "2026-09-28"}, "span": {"start": pd.Timestamp("2026-04-01"), "end": pd.Timestamp("2026-04-02"), "months": "Apr"},
          "n_month_hours": 5, "n_load_matched": 3, "load_error": None, "config_span": None, "pooled_month": None}
    res = [{"c": C, "binding": bc, "dispatch": pd.DataFrame(), "price": {"lp_stats": None, "marginal_units": pd.DataFrame(), "structural_lambda": None}}]
    md = dd_report.render_markdown(7, res, pd.DataFrame(), None)
    assert "HE24=0.900, HE17=0.500, HE1=0.100" in md and "peak stress hour=HE24" in md


# ---------------------------------------------------------------- piece 5 --

def _bc(**kw):
    base = {"empty": False, "hour_of_day_neg_rate": {16: 0.5}, "month_name": "September", "config_id": 1, "n_hours": 1680,
            "n_wind_matched": 1680, "n_solar_matched": 1679, "n_load_matched": 1680, "corr": {}, "system_wind_cap_mw": 1.0,
            "dominant_wind_region": None, "triggers": {}, "pct_neg_onpeak_month": 4.0, "pct_neg_offpeak_month": 1.0,
            "driver": {"kind": "wind", "lead": 0.157, "wind_corr": -0.514, "solar_corr": -0.357, "load_corr": 0.1, "peak_hour": 16},
            "window": {"start": "2026-04-01", "end": "2026-09-28"},
            "span": {"start": pd.Timestamp("2026-04-01"), "end": pd.Timestamp("2026-06-10 23:00"), "months": "Apr-Jun"},
            "n_month_hours": 0, "load_error": None,
            "config_span": {"start": pd.Timestamp("2022-01-01"), "end": pd.Timestamp("2026-06-10 23:00"), "n_hours": 9999},
            "pooled_month": {"p_bind": 0.132, "n_onpeak_hours": 1312, "years": [2022, 2023, 2024, 2025]}}
    base.update(kw)
    return base


def _render(bc, price=None, month=None):
    price = price or {"lp_stats": None, "marginal_units": pd.DataFrame(), "structural_lambda": None}
    return dd_report.render_markdown(7, [{"c": C, "binding": bc, "dispatch": pd.DataFrame(), "price": price, "month": month}], pd.DataFrame(), None)


def test_window_without_month_hours_says_so_and_adds_pooled_history():
    md = _render(_bc())
    assert "None%" not in md
    assert "No September hours in window (fast-scan data for this config ends 2026-06-10)." in md
    assert ("Pooled history, all years (2022, 2023, 2024, 2025), September on-peak: headroom<0 in 13.2% of 1,312 on-peak hours" in md)
    assert "spanning 2026-04-01 to 2026-06-10 (Apr-Jun; requested window 2026-04-01..2026-09-28)" in md and "1,680" in md


def test_window_with_month_hours_keeps_the_window_percentages():
    md = _render(_bc(n_month_hours=300))
    assert "Window September on-peak" in md and "4.0%" in md and "No September hours in window" not in md and "Pooled history" in md


def _frame(n=2000, seed=0):
    rng = np.random.default_rng(seed)
    wind = rng.uniform(0, 10000, n)
    solar = rng.uniform(0, 8000, n)
    return pd.DataFrame({"HEADROOM": 50 - wind / 100 + rng.normal(0, 5, n), "W": wind, "S": solar, "L": 40000 + 5 * rng.normal(0, 1000, n)})


def test_trigger_levels_negative_corr_uses_a_low_percentile_and_quintiles():
    t = dd.trigger_levels(_frame(), "W")
    assert t["direction"] == "binds when high" and t["start_pctile"] == "P10" and t["start_level"] == t["p10"] < t["p50"] < t["p90"]
    assert t["p10"] > 5000  # binding hours sit at high wind; P90 would have hidden where binding starts
    rates = [q["bind_rate"] for q in t["quintiles"]]
    assert len(rates) == 5 and rates == sorted(rates) and rates[0] < 0.05 < 0.9 < rates[-1]


def test_trigger_levels_positive_corr_uses_p90():
    df = _frame().assign(HEADROOM=lambda d: d["HEADROOM"] * -1 + 50)  # headroom now rises with wind: binds when wind is low
    df["HEADROOM"] = -50 + df["W"] / 100 + np.random.default_rng(1).normal(0, 5, len(df))
    t = dd.trigger_levels(df, "W")
    assert t["direction"] == "binds when low" and t["start_pctile"] == "P90" and t["start_level"] == t["p90"] < 6000
    assert dd.trigger_levels(df.assign(L=1.0), "L")["direction"] == "no clear direction"
    assert dd.trigger_levels(df.iloc[0:0], "W") is None


def test_attribute_driver_needs_a_lead_else_mixed():
    assert dd.attribute_driver({"wind": -0.5, "solar": -0.35, "load": 0.1})["kind"] == "wind"
    assert dd.attribute_driver({"wind": -0.5, "solar": -0.45, "load": 0.1}) == {"kind": "mixed", "lead": 0.05}
    assert dd.attribute_driver({"wind": 0.1, "solar": -0.05, "load": None})["kind"] == "none"
    assert dd.attribute_driver({"wind": None, "solar": None, "load": 0.4})["kind"] == "load"
    md = _render(_bc(driver={"kind": "mixed", "lead": 0.05, "wind_corr": -0.5, "solar_corr": -0.45, "load_corr": 0.1, "peak_hour": 16}))
    assert "mixed (no single driver leads the runner-up by >= 0.1; corr with headroom: wind=-0.5, solar=-0.45, load=0.1" in md


def test_locate_on_curve():
    curve = [{"lambda": 10.0, "depth_lo": 0.0, "depth_hi": 50.0}, {"lambda": 40.0, "depth_lo": 50.0, "depth_hi": 100.0}]
    assert dd.locate_on_curve(curve, 5.0)["where"] == "below_first"
    assert dd.locate_on_curve(curve, 25.0) == {"where": "at_step", "step": 2, "depth_lo": 50.0, "depth_hi": 100.0, "step_price": 40.0}
    assert dd.locate_on_curve(curve, 99.0) == {"where": "above_last", "last_price": 40.0, "exhaustion_mw": 100.0}


def test_price_formation_lists_curve_steps_outage_flow_and_flags_up_renewables(monkeypatch):
    units = pd.DataFrame({"SCED": ["DN1", "UP_WIND"], "SIDE": ["down", "up"], "FUELTYPE": ["NG", "WND (Wind)"], "IS_RENEWABLE": [False, True]})
    cap = pd.DataFrame({"P60": [20.0, 5.0]}, index=["DN1", "UP_WIND"])
    up = [{"sced": "UP_WIND", "sf": -0.2, "price": 30.0, "avail": 10.0, "committed": True, "renewable": True}]
    down = [{"sced": "DN1", "sf": 0.2, "price": 10.0, "avail": 10.0, "renewable": False, "offer": 10.0}]
    rs = dd.shadow_price.ReliefSet(units, cap, up, down, n_band=2)
    monkeypatch.setattr(dd.shadow_price, "relief_set", lambda *a, **k: rs)
    monkeypatch.setattr(dd.shifts, "bus_sf_for_buses", lambda *a: pd.DataFrame({"BUSNUM": [7], "SF": [0.2]}))
    ctg = pd.DataFrame({"RUNID": [1], "FROMNUM": 1, "TONUM": 2, "CKT": "1", "CTGLABEL": "X", "LIMVIOLPCT": [100.0]})
    oc = pd.DataFrame({"RUNID": [1], "FROMNUM": 1, "TONUM": 2, "CKT": "1", "LPOPFCTGID": "X", "OPFCNLAMBDA": [30.0]})
    gen = pd.DataFrame({"RUNID": [1], "BUSNUM": [7], "ID": "1", "FUELTYPE": "NG", "MW": [5.0], "MWMIN": [0.0], "MWMAX": [10.0],
                        "BUSMARGCOSTMW": [20.0], "EDMARGCOSTMW": [20.0]})
    tof = pd.DataFrame({"FROMNUM_TARGET": [1, 1], "TONUM_TARGET": [2, 2], "CKT_TARGET": ["1", "1"], "CTGLABEL": ["X", "X"],
                        "OUTAGE_GROUP": ["OUT_A", "OUT_B"], "OUTAGE_GROUP_ID": [1, 2], "OUTBRANCHLABEL": ["a", "b"], "BRANCHID_OUTAGE": [1, 2],
                        "FROMNUM_OUTAGE": [3, 4], "TONUM_OUTAGE": [5, 6], "CKT_OUTAGE": ["1", "1"], "RUNID": [1, 1],
                        "FLOWDELTA": [-60.0, 10.0], "PREGROUPOUTLINEFLOW": [100.0, 100.0]})
    out = dd.price_formation(1, {**C, "direction": -1}, ctg, oc, gen, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), tof)
    sl = out["structural_lambda"]
    assert out["outage_flow"] == {"group": "OUT_A", "signed_fd": 60.0, "mean_preflow": 100.0, "n_runs": 1}
    assert sl["steps"][0]["up"] == "UP_WIND" and sl["steps"][0]["up_renewable"] and sl["steps"][0]["pair_mw"] == 10.0
    assert sl["lp_p50_on_curve"]["where"] in ("at_step", "below_first", "above_last")
    md = _render(_bc(), out)
    row = [l for l in md.splitlines() if l.startswith("|") and "UP_WIND" in l and "DN1" in l][0]
    assert [c.strip() for c in row.strip("|").split("|")][:8] == ["1", "DN1", "0.2", "10", "UP_WIND", "-0.2", "30", "0.4"]
    assert "UP unit is wind/solar: cannot increase output" in md and "does not model it as curtailment" in md
    assert "mean flow change on this line +60.0 MW in its bound sense, averaged over 1 run (" in md and "n = 1: a single run, thin" in md
    assert "not the relief needed, so it is not compared with the curve" in md and "The driving outage adds" not in md
    assert "Curve exhausted at" in md and "LP's P50 shadow price" in md and "min $30.0, P50 $30.0, max $30.0" in md


def test_marginal_unit_table_names_units_and_marks_non_price_setters(monkeypatch):
    marg = pd.DataFrame({"BUSNUM": [7, 8], "ID": ["1", "1"], "FUELTYPE": ["NG", "WND"], "N": [3, 2]})
    monkeypatch.setattr(dd.shifts, "bus_sf_for_buses", lambda *a: pd.DataFrame({"BUSNUM": [7, 8], "SF": [0.25, -0.01]}))
    out = dd.marginal_unit_table(1, {**C, "direction": 1}, marg, pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
    assert list(out["UNIT"]) == ["bus 7 #1", "bus 8 #1"]  # no name map available -> falls back to bus/id
    assert list(out["PRICE_SETTER"])[0] == "yes" and "not a price setter for this constraint" in out["PRICE_SETTER"].iloc[1]
    out = dd.marginal_unit_table(1, {**C, "direction": -1}, marg, pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
    assert list(out["SF"]) == [-0.25, 0.01]


# ------------------------------------------------------------ honesty fixes --

def _curve(steps):
    out, depth = [], 0.0
    for price, flow, committed in steps:
        out.append({"depth_lo": depth, "depth_hi": depth + flow, "lambda": price, "pair": "D↓/U↑", "dsf": 0.1, "up_committed": committed,
                    "up": "U", "down": "D", "sf_up": -0.05, "sf_down": 0.05, "price_up": 16.9, "price_down": 250.01, "pair_mw": flow / 0.1,
                    "up_renewable": False, "down_renewable": False})
        depth += flow
    return out


def _sl(curve):
    return {"shallow_lambda": 0.0, "shallow_pair": "D↓/U↑", "exhaustion_depth_mw": curve[-1]["depth_hi"], "single_step": len(curve) == 1,
            "committed_mw": 5.0, "uncommitted_mw": 0.0, "n_uncommitted_steps": 0, "deep_lambda": 40.0, "deep_pair": "D↓/U↑",
            "n_steps": len(curve), "shallow_regime": ZERO, "deep_regime": "gas-spread-priced", "steps": curve,
            "zero_step_depth_mw": 3.0, "n_zero_steps": 1, "lp_p50_on_curve": None}


ZERO = dd.ZERO_STEP_LABEL


def test_price_formation_text_does_not_call_zero_steps_free_and_prints_method_lp_range_and_open_questions():
    curve = _curve([(0.0, 3.0, True), (40.0, 5.0, True)])
    lp = {"n": 4, "n_binding_runs": 4, "min": 22.0, "mean": 50.0, "p50": 47.7, "max": 134.8, "pct_penalty_tier": 0.0}
    md = _render(_bc(), {"lp_stats": lp, "marginal_units": pd.DataFrame(), "structural_lambda": _sl(curve), "outage_flow": None})
    assert "genuinely" not in md and "free relief" not in md and "not that the relief is free" in md
    assert "$0 by the P60-offer method" in md
    assert "P60 of the up unit's offer curve minus the P60 of the down unit's offer curve, divided by the difference of their shift factors" in md
    assert "floored at 0" in md
    assert "min=$22.0, mean=$50.0, p50=$47.7, max=$134.8" in md and "min $22.0, P50 $47.7, max $134.8" in md
    assert "Depth covered by $0 steps ($0 by the P60-offer method): 3.0 MW of flow relief in 1 of 2 steps" in md
    tail = md[md.index("**Open method questions**"):].splitlines()
    assert [l for l in tail if l[:2] in ("1.", "2.", "3.", "4.")] == [
        "1. Down-side units are priced at the P60 of their offer curve rather than their marginal awarded segment.",
        "2. The cheap part of the curve includes start-required units.",
        "3. Wind/solar/storage without offers contribute no relief.",
        "4. Capacity at multi-resource settlement points is a median, not a sum."]


def test_zero_step_in_curve_table_is_flagged_with_the_method_label():
    curve = _curve([(0.0, 3.0, True), (40.0, 5.0, True)])
    md = _render(_bc(), {"lp_stats": None, "marginal_units": pd.DataFrame(), "structural_lambda": _sl(curve), "outage_flow": None})
    rows = [l for l in md.splitlines() if l.startswith("|") and "D" in l and "U" in l and "250.01" in l]
    assert ZERO in rows[0] and ZERO not in rows[1]


def test_month_need_table_matches_the_shortlist_columns_and_bands_sum_to_all_hours(monkeypatch):
    from pfa.analysis import shadow_price as sp, shortlist_value as sv
    up = [{"sced": "U0", "sf": -0.2, "price": 30.0, "avail": 10.0, "committed": True}]
    down = [{"sced": "D0", "sf": 0.2, "price": 10.0, "avail": 10.0}]
    need = [1.0, 2.0, 3.0, 10.0]
    monkeypatch.setattr(sv.fastscan, "find_configs", lambda *a: pd.DataFrame({"CONFIG_ID": [1], "DIRECTION": [1]}))
    monkeypatch.setattr(sv, "fastscan_month_onpeak", lambda cid, m: (0.5, pd.DataFrame({"NEED_MW": need}), 100, [2022]))
    units = pd.DataFrame({"SCED": ["U0", "D0"], "SIDE": ["up", "down"]})
    rs = sp.ReliefSet(units, pd.DataFrame({"P60": [1.0, 1.0]}, index=["U0", "D0"]), up, down, n_band=2)
    monkeypatch.setattr(sv.sp, "relief_set", lambda *a, **k: rs)
    monkeypatch.setattr(sv.popt, "best_paths", lambda *a: None)
    row = sv.value_row(1, "100-200-1@X", None, None, None, None, "2026-09", "w")
    m = dd.month_need_table(sp.lambda_depth_curve(up, down), {"need_mw": need, "p_bind": 0.5, "n_onpeak_hours": 100, "years": [2022]})
    assert (m["mean"], m["p50"], m["p90"], m["unpriced_pct"], m["n_neg"]) == (
        row["E[lambda|bind]"], row["lambda P50"], row["lambda P90"], row["unpriced deep hours %"], row["_n_neg_hours"])
    assert sum(b["hours"] for b in m["bands"]) + m["beyond_hours"] == m["n_neg"] == 4
    assert (m["need_p50"], m["need_max"], m["curve_depth_mw"]) == (2.5, 10.0, 4.0)
    md = _render(_bc(), {"lp_stats": None, "marginal_units": pd.DataFrame(), "structural_lambda": _sl(sp.lambda_depth_curve(up, down)),
                         "outage_flow": None}, month=m)
    assert "| beyond curve" in md and "Negative-headroom hours: 4; P(bind) 0.500 of 100 on-peak hours" in md
    assert "unpriced share 25.0%" in md and "P50 2.5 MW, P90 7.9 MW, max 10.0 MW, against the curve's 4.0 MW (curve exhausted before the P90 need)" in md


def test_trigger_suppressed_when_p10_is_at_the_floor_or_quintiles_are_not_monotonic():
    rng = np.random.default_rng(3)
    n = 3000
    solar = np.where(rng.random(n) < 0.2, 0.0, rng.uniform(0, 8000, n))  # a night floor of exactly 0 MW
    df = pd.DataFrame({"HEADROOM": 20 - solar / 100 + rng.normal(0, 3, n), "S": solar})
    at_floor = (df["S"] == 0.0) & (rng.random(n) < 0.5)
    df.loc[at_floor, "HEADROOM"] = -5.0  # some floor hours bind as well, so P10 of the binding hours is 0 MW
    t = dd.trigger_levels(df, "S")
    assert t["start_level"] is None and "floor" in t["no_clear_trigger"]
    wind = rng.uniform(0, 10000, n)
    df2 = pd.DataFrame({"W": wind, "HEADROOM": 20 - wind / 100 + np.where((wind > 4000) & (wind < 6000), 60, 0) + rng.normal(0, 3, n)})
    t2 = dd.trigger_levels(df2, "W")
    assert t2["start_level"] is None and "not monotonic" in t2["no_clear_trigger"]
    md = _render(_bc(triggers={"S": t, "W": t2}))
    assert md.count("no clear trigger (") == 2
    ok = dd.trigger_levels(_frame(), "W")
    assert ok["start_level"] is not None and ok["no_clear_trigger"] is None


def test_dispatch_wind_solar_up_relief_carries_the_curve_flag(monkeypatch):
    nodes = pd.DataFrame({"NAME": ["SLR", "GASU", "WNDH"], "CPNODEID": [1, 2, 3], "PSENS": [-0.2, -0.2, 0.2], "N": [1, 1, 1]})
    monkeypatch.setattr(dd.shifts, "cpnode_live_nodes", lambda *a: nodes)
    gu = pd.DataFrame({"CPNODEID": [1, 2, 3], "GENFUELTYPE": ["SOLAR", "GAS", "WIND"], "RESOURCE_TYPE": ["SOLAR", "GAS", "WIND"]})
    d = dd.dispatch_profile(1, {**C, "direction": 1}, gu, pd.DataFrame())
    res = [{"c": C, "binding": _bc(), "dispatch": d, "price": {"lp_stats": None, "marginal_units": pd.DataFrame(), "structural_lambda": None}}]
    out = dd_report.render_markdown(7, res, pd.DataFrame(), None)
    flagged = {l.split("|")[1].strip() for l in out.splitlines() if dd_report.UP_RENEWABLE_FLAG in l}
    assert flagged == {"SLR"}  # wind WNDH is harm (up loads), the gas unit is not wind/solar
