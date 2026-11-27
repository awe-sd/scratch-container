import numpy as np
import pandas as pd

from pfa.analysis import deep_dive as dd
from pfa.report import deep_dive as dd_report

C = dict(fromnum=1, tonum=2, ckt="1", ctglabel="X", label="L1", fromname="AAA_1", toname="BBB_1", direction=1,
         key="1-2-1@X", n_binding_runs=2)


def _hours(n=24 * 30):
    return pd.date_range("2026-09-01", periods=n, freq="h")


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
    out = dd.binding_conditions(5, "2026-09-01", "2026-10-01", "2026-09")
    assert not out["empty"] and out["n_hours"] == len(ts)
    assert out["corr"]["SYSTEM_WIND_MW"] is not None
    assert set(out["hour_of_day_neg_rate"]) == set(range(24))
    assert out["driver"]["kind"] in ("wind", "load", "co", "solar")
    assert out["month_name"] == "September"


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
    out = dd.price_formation(1, C, ctg, oc, gen, pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
    assert out["lp_stats"] == {"n": 2, "n_binding_runs": 2, "mean": 255.0, "p50": 255.0, "max": 500.0, "pct_penalty_tier": 0.5}
    assert list(out["marginal_units"]["BUSNUM"]) == [7] and out["structural_lambda"] == {"error": "no offers"}


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
          "dominant_wind_region": None, "thresholds": {}, "pct_neg_onpeak_month": 1.0, "pct_neg_offpeak_month": 1.0,
          "driver": {"kind": "load", "wind_corr": None, "solar_corr": None, "peak_hour": 23}}
    res = [{"c": C, "binding": bc, "dispatch": pd.DataFrame(), "price": {"lp_stats": None, "marginal_units": pd.DataFrame(), "structural_lambda": None}}]
    md = dd_report.render_markdown(7, res, pd.DataFrame(), None)
    assert "HE24=0.900, HE17=0.500, HE1=0.100" in md and "peak stress hour=HE24" in md
