import pandas as pd
import pytest


@pytest.fixture()
def fixtures(tests_dir):
    fx = tests_dir / "fixtures"
    return (
        pd.read_csv(fx / "dampsse_def_slice.csv"),
        pd.read_csv(fx / "dampsse_agg_slice.csv"),
        pd.read_csv(fx / "our_teids_slice.csv"),
        pd.read_csv(fx / "stations.csv"),
    )


def test_compute_inservice_status_majority():
    from branch_tracking.pipeline.dampsse import compute_inservice_status
    agg = pd.DataFrame({"ercotDampsseId": [1, 2],
                        "n_hours": [100, 100], "n_inservice": [99, 10]})
    out = compute_inservice_status(agg)
    assert list(out["dampsse_default_status"]) == ["Closed", "Open"]
    assert out["pct_inservice"].tolist() == [0.99, 0.10]


def test_fallback_maps_sndsw_legs_to_matching_units(fixtures):
    from branch_tracking.pipeline.dampsse import (
        map_fallback_tiers, prepare_pool, prepare_unmapped,
    )
    dampsse_def, agg, ours, stations = fixtures
    pool = prepare_pool(dampsse_def, stations, claimed_ids=set())
    unmapped = prepare_unmapped(ours)
    mappings, diagnosis = map_fallback_tiers(unmapped, pool, agg, ckt_by_id={})
    got = mappings.set_index("teid")["dampsse_name_raw"].to_dict()
    assert got.get(280444) == "SNDSW_MR1L"   # low-side teid -> MR1L
    assert got.get(280447) == "SNDSW_MR1H"   # high-side teid -> MR1H
    assert got.get(279293) == "CMNSW_MR1H"


def test_mulberry_stays_ambiguous_without_consensus(fixtures):
    from branch_tracking.pipeline.dampsse import (
        map_fallback_tiers, prepare_pool, prepare_unmapped,
    )
    dampsse_def, agg, ours, stations = fixtures
    pool = prepare_pool(dampsse_def, stations, claimed_ids=set())
    unmapped = prepare_unmapped(ours)
    mappings, diagnosis = map_fallback_tiers(unmapped, pool, agg, ckt_by_id={})
    assert 720535 in set(diagnosis["teid"])  # MULBERRY must NOT auto-resolve
