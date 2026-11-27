import pandas as pd
import pytest

import mismatch_analysis as ma
from compare_validation_shifts import classify


def raw_frame(rows):
    """rows: (psenshiftid, cpnodeid, psens_raw, ref_psen, dart_psen, simhour)"""
    df = pd.DataFrame(rows, columns=["psenshiftid", "cpnodeid", "psens_raw", "ref_psen", "dart_psen", "simhour"])
    df["cpnode_name"] = "N" + df["cpnodeid"].astype(str)
    df["simdate"] = "2026-06-01"
    df["topologyid"] = df["psenshiftid"]
    df["runbegintime"] = "t"
    return df


def test_sign_positive_and_negative_per_topology():
    raw = raw_frame([(1, 10, 0.5, 0.0, 0.5, 1), (1, 11, 0.2, 0.0, 0.2, 1),
                     (2, 10, 0.5, 0.0, -0.5, 2), (2, 11, 0.2, 0.0, -0.2, 2)])
    df, meta = ma.resolve_signs_and_offset(raw, 0.02)
    assert df.groupby("psenshiftid")["sign"].first().to_dict() == {1: 1, 2: -1}
    assert meta["n_topo_sign_pos"] == 1 and meta["n_topo_sign_neg"] == 1 and meta["mixed_sign"]
    assert meta["sign_agreement_rate"] == 0.5
    assert (df["abs_diff"] < 1e-12).all()
    assert (df["study_psen"] == df["sign"] * df["psens_raw"]).all()


def test_tie_prefers_positive_sign():
    raw = raw_frame([(1, 10, 0.0, 0.0, 0.0, 1)])
    df, _ = ma.resolve_signs_and_offset(raw, 0.02)
    assert df["sign"].iloc[0] == 1


@pytest.mark.parametrize("guard,unresolved", [(0.02, False), (0.0199, True)])
def test_sign_guard_boundary(guard, unresolved):
    # both signs miss by 0.02 -> min_mae = 0.02; unresolved only when strictly greater
    raw = raw_frame([(1, 10, 0.0, 0.0, 0.02, 1)])
    df, meta = ma.resolve_signs_and_offset(raw, guard)
    assert bool(df["SIGN_UNRESOLVED"].iloc[0]) is unresolved
    assert df["sign"].iloc[0] == 1  # unresolved keeps +1
    assert meta["n_sign_unresolved"] == int(unresolved)


def offset_raw(n_off=0):
    n = 10
    rows = [(1, c, 0.1, 0.0, 0.1 - 0.01, 1) for c in range(n)]  # constant diff +0.01
    for c in range(n_off):
        rows[c] = (1, c, 0.1, 0.0, 0.1 - 0.05, 1)
    return raw_frame(rows)


def test_ref_offset_applied_when_constant_bias():
    df, meta = ma.resolve_signs_and_offset(offset_raw(), 0.02)
    assert meta["ref_offset"] and meta["bias_raw"] == pytest.approx(0.01)
    assert df["diff_adj"].abs().max() < 1e-12
    assert df["diff_before_offset"].iloc[0] == pytest.approx(0.01)


def test_ref_offset_requires_90pct_nodes_in_band():
    _, many = ma.resolve_signs_and_offset(offset_raw(5), 0.02)
    assert many["share_cpnodes_in_offset_band"] < 0.90 and many["ref_offset"] is False


def test_no_offset_when_bias_small_vs_mae():
    raw = raw_frame([(1, 10, 0.1, 0.0, 0.1 - 0.01, 1), (1, 11, 0.1, 0.0, 0.1 + 0.01, 1)])
    _, meta = ma.resolve_signs_and_offset(raw, 0.02)
    assert meta["ref_offset"] is False


CONFIGS = pd.DataFrame({"TOPOLOGYSHIFTSETID": [7], "BRANCHLABEL": ["B"], "CTGLABEL": ["C"]})
META = {"n_topo_sign_pos": 10, "n_topo_sign_neg": 0, "sign_agreement_rate": 1.0, "mixed_sign": False,
        "n_sign_unresolved": 0, "ref_offset": False, "bias_raw": 0.0}


def adj_frame(diffs, psenshiftid=1, simhour=1):
    """Frame shaped like resolve_signs_and_offset output, abs_diff set directly."""
    n = len(diffs)
    return pd.DataFrame({
        "psenshiftid": psenshiftid, "simdate": "2026-06-01", "simhour": simhour,
        "cpnodeid": range(n), "cpnode_name": [f"N{i}" for i in range(n)],
        "abs_diff": diffs, "diff_adj": diffs, "diff_before_offset": diffs,
        "topologyid": 1, "runbegintime": "t", "SIGN_UNRESOLVED": False,
        "study_psen": 0.0, "ref_psen": 0.0, "dart_psen": 0.0,
    })


@pytest.mark.parametrize("n_bad,is_bad", [(0, False), (1, True)])
def test_hour_bad_share_boundary_ge(n_bad, is_bad):
    # 20 nodes: 1 mismatching = share 0.05 == hour_bad_share -> BAD (>=)
    diffs = [0.5] * n_bad + [0.0] * (20 - n_bad)
    th = ma.build_topology_hour_table({7: adj_frame(diffs)}, CONFIGS, 0.01, 0.05)
    assert bool(th["BAD"].iloc[0]) is is_bad


def test_rank_tol_is_strict_greater():
    th = ma.build_topology_hour_table({7: adj_frame([0.01, 0.0100001, 0.0])}, CONFIGS, 0.01, 0.05)
    assert th["n_mismatch_nodes"].iloc[0] == 1


@pytest.mark.parametrize("mism_hours,counted", [(1, 1), (0, 0)])
def test_node_rate_boundary_ge(mism_hours, counted):
    # one node over 10 topology-hours; rate 0.1 == node_rate 0.10 -> counted (>=)
    df = pd.concat([adj_frame([0.5 if h < mism_hours else 0.0], simhour=h + 1, psenshiftid=100 + h)
                    for h in range(10)], ignore_index=True)
    th = ma.build_topology_hour_table({7: df}, CONFIGS, 0.01, 0.05)
    summary, _ = ma.build_constraint_summary({7: df}, {7: META}, CONFIGS, th, 0.01, 0.10)
    assert summary["n_distinct_cpnodes_mismatching_junewide"].iloc[0] == counted
    assert summary["bad_clock_hours"].iloc[0] == mism_hours
    assert summary["tot_clock_hours"].iloc[0] == 10


def node_label(spec):
    """spec: (set_id, simdate, simhour, cpnodeid) bad rows; three evaluated sets."""
    raws = {s: adj_frame([0.0, 0.0], psenshiftid=s) for s in (1, 2, 3)}
    bm = pd.DataFrame([{"set_id": s, "simdate": d, "simhour": h, "cpnodeid": c, "cpnode_name": f"N{c}",
                        "abs_diff": 0.5, "branchlabel": f"B{s}", "ctglabel": "C"} for s, d, h, c in spec])
    nd = ma.build_node_day_matrix(raws, bm)
    return ma.build_node_summary(raws, bm, nd).set_index("cpnodeid")["label"].to_dict()


def test_node_label_constraint_specific():
    assert node_label([(1, "2026-06-01", 1, 0), (1, "2026-06-01", 2, 0)]) == {0: "CONSTRAINT_SPECIFIC"}


def test_node_label_single_bad_hour_not_a_member():
    assert node_label([(1, "2026-06-01", 1, 0)]) == {}


def test_node_label_systemic_needs_half_constraints_and_3_days():
    spec = [(s, f"2026-06-0{d}", h, 0) for s in (1, 2) for d in (1, 2, 3) for h in (1, 2)]
    assert node_label(spec)[0] == "SYSTEMIC_NODE"


def test_node_label_mixed_when_few_days():
    spec = [(s, "2026-06-01", h, 0) for s in (1, 2) for h in (1, 2)]
    assert node_label(spec)[0] == "MIXED"


def test_classify_ok_and_strict_boundaries():
    cp, tp = pd.DataFrame({"n_bad_02": [0]}), pd.DataFrame({"max_abs": [0.019]})
    assert classify({"mae": 0.004, "max_abs": 0.019, "bias": 0.0}, tp, cp) == "OK"
    assert classify({"mae": 0.005, "max_abs": 0.019, "bias": 0.0}, tp, cp) == "DIFFUSE"
    assert classify({"mae": 0.004, "max_abs": 0.02, "bias": 0.0}, tp, cp) != "OK"


def test_classify_localized_nodes():
    s = {"mae": 0.01, "max_abs": 0.3, "bias": 0.0}
    cp = pd.DataFrame({"n_bad_02": [5] * 10 + [0] * 90})
    assert classify(s, pd.DataFrame({"max_abs": [0.3] * 5}), cp) == "LOCALIZED_NODES"


def test_classify_localized_topologies():
    s = {"mae": 0.01, "max_abs": 0.3, "bias": 0.0}
    cp = pd.DataFrame({"n_bad_02": [1] * 100})
    assert classify(s, pd.DataFrame({"max_abs": [0.3] + [0.0] * 9}), cp) == "LOCALIZED_TOPOLOGIES"


def test_classify_systematic_vs_diffuse():
    cp = pd.DataFrame({"n_bad_02": [1] * 100})
    tp = pd.DataFrame({"max_abs": [0.3] * 10})
    assert classify({"mae": 0.01, "max_abs": 0.3, "bias": 0.0051}, tp, cp) == "SYSTEMATIC"
    assert classify({"mae": 0.01, "max_abs": 0.3, "bias": 0.005}, tp, cp) == "DIFFUSE"
