import pandas as pd
import pytest

from pfa import config
from pfa.extract import network_ref


@pytest.fixture
def ref_dir(tmp_path, monkeypatch):
    pd.DataFrame({
        "teid": [11, 12, None], "branch_id": [60000001, 60000002, 60000003],
        "from_bus": ["AAA", "BBB", "CCC"], "to_bus": ["XXX", "YYY", "ZZZ"],
        "ckt": ["1", "1", "1"], "default_status_final": ["Closed"] * 3,
    }).to_csv(tmp_path / config.BRANCH_MAP_FILE, index=False)
    pd.DataFrame({
        "PsseType": ["Bus", "Bus", "Bus", "Line"],
        "BusNumber1": [1, 1, 2, 3],
        "Name": ["A (CN1) 138kV", "A (CN2) 345kV", "B 69kV", "L 500kV"],
    }).to_csv(tmp_path / "CIM_20260101_TeidMap.csv", index=False)
    monkeypatch.setenv(config.NETWORK_REF_DIR_ENV, str(tmp_path))
    network_ref.clear_cache()
    yield tmp_path
    network_ref.clear_cache()


def test_branch_lookups_from_override_dir(ref_dir):
    assert network_ref.teid_for_branch(60000001) == 11
    assert network_ref.teid_for_branch(60000003) is None
    assert network_ref.teid_for_branch(1) is None
    assert network_ref.teids_for_endpoints(["BBB", "nope"]) == [12]
    assert network_ref.teids_for_endpoints([]) == []


def test_bus_kv_takes_max_per_bus_and_max_per_constraint(ref_dir):
    assert network_ref.bus_kv_map() == {1: 345.0, 2: 69.0}
    assert network_ref.constraint_kv(1, 2) == 345.0
    assert network_ref.constraint_kv(2, 99) == 69.0
    assert network_ref.constraint_kv(98, 99) is None


def test_loaders_cache_in_process(ref_dir):
    first = network_ref.branch_map()
    (ref_dir / config.BRANCH_MAP_FILE).unlink()
    assert network_ref.branch_map() is first


def test_missing_files_name_the_file_and_the_env_var(tmp_path, monkeypatch):
    monkeypatch.setenv(config.NETWORK_REF_DIR_ENV, str(tmp_path))
    network_ref.clear_cache()
    with pytest.raises(FileNotFoundError, match=config.BRANCH_MAP_FILE) as e:
        network_ref.branch_map()
    assert config.NETWORK_REF_DIR_ENV in str(e.value)
    with pytest.raises(FileNotFoundError, match="TeidMap") as e:
        network_ref.bus_kv_map()
    assert config.NETWORK_REF_DIR_ENV in str(e.value)
    network_ref.clear_cache()


def test_default_locations_without_override(monkeypatch):
    monkeypatch.delenv(config.NETWORK_REF_DIR_ENV, raising=False)
    assert network_ref._branch_map_path().name == config.BRANCH_MAP_FILE
    assert network_ref._teidmap_path().name.endswith("_TeidMap.csv")
