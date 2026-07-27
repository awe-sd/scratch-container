import pandas as pd


def test_build_graph_nodes_and_edges(tests_dir):
    from branch_tracking.pipeline.network import build_graph
    cim = pd.read_csv(tests_dir / "fixtures" / "cim_slice.csv", dtype=str)
    status = pd.DataFrame({"teid": ["280447", "280444"],
                           "default_status": ["Closed", "Closed"]})
    g = build_graph(cim, status)
    # 5 buses become nodes (13429,13441,13440,24107,99999)
    assert g.number_of_nodes() == 5
    # 4 edges: 3 transformer windings + 1 line
    assert g.number_of_edges() == 4
    # the star bus connects exactly the 3 windings
    assert g.degree("24107") == 3
    # edge attrs carry teid + joined status
    teids = {d["teid"]: d for _, _, d in g.edges(data=True)}
    assert teids["280447"]["default_status"] == "Closed"
    assert teids["280447"]["device_type"] == "Transformer"
    assert teids["280453"]["default_status"] is None  # not in status frame
    assert teids["700001"]["device_type"] == "Branch"


def test_transformer_winding_groups(tests_dir):
    from branch_tracking.pipeline.network import transformer_winding_groups
    cim = pd.read_csv(tests_dir / "fixtures" / "cim_slice.csv", dtype=str)
    groups = transformer_winding_groups(cim)
    assert len(groups) == 1
    grp = groups[0]
    assert grp["substation"] == "SNDSW"
    assert grp["star_bus"] == "24107"
    assert grp["ckt"] == "2"
    assert set(grp["winding_teids"]) == {"280447", "280444", "280453"}


def test_real_bus_not_treated_as_star(tests_dir):
    # bus 13429 carries a transformer winding AND a line -> not an internal
    # star, so it must never appear as a group's star_bus.
    from branch_tracking.pipeline.network import transformer_winding_groups
    cim = pd.read_csv(tests_dir / "fixtures" / "cim_slice.csv", dtype=str)
    stars = {g["star_bus"] for g in transformer_winding_groups(cim)}
    assert "13429" not in stars


def _status(pairs):
    return pd.DataFrame(pairs, columns=["teid", "default_status"])


def test_infer_all_closed_yields_inferred_closed(tests_dir):
    from branch_tracking.pipeline.network import infer_tertiary_status
    cim = pd.read_csv(tests_dir / "fixtures" / "cim_slice.csv", dtype=str)
    status = _status([("280447", "Closed"), ("280444", "Closed")])  # 280453 missing
    out = infer_tertiary_status(cim, status)
    row = out[out["teid"] == "280453"].iloc[0]
    assert row["inferred_status"] == "Closed"
    assert row["source"] == "inferred_transformer_winding"
    assert row["flag"] == ""


def test_infer_conflict_flags(tests_dir):
    from branch_tracking.pipeline.network import infer_tertiary_status
    cim = pd.read_csv(tests_dir / "fixtures" / "cim_slice.csv", dtype=str)
    status = _status([("280447", "Closed"), ("280444", "Open")])
    out = infer_tertiary_status(cim, status)
    row = out[out["teid"] == "280453"].iloc[0]
    assert pd.isna(row["inferred_status"]) or row["inferred_status"] is None
    assert row["flag"] == "conflict"


def test_infer_all_open_flags(tests_dir):
    from branch_tracking.pipeline.network import infer_tertiary_status
    cim = pd.read_csv(tests_dir / "fixtures" / "cim_slice.csv", dtype=str)
    status = _status([("280447", "Open"), ("280444", "Open")])
    out = infer_tertiary_status(cim, status)
    row = out[out["teid"] == "280453"].iloc[0]
    assert row["flag"] == "all_siblings_open"


def test_infer_no_evidence(tests_dir):
    from branch_tracking.pipeline.network import infer_tertiary_status
    cim = pd.read_csv(tests_dir / "fixtures" / "cim_slice.csv", dtype=str)
    status = _status([])  # nobody in the group has status
    out = infer_tertiary_status(cim, status)
    assert set(out["flag"]) == {"no_evidence"}
    assert len(out) == 3


def test_multigroup_winding_deduped_to_one_row(tests_dir):
    # WX (911002) sits between two star buses 901 & 902, so it is in two groups.
    # Only WA (911001) has status Closed; WB (911003) is unknown. WX must appear
    # exactly once, inferred Closed (Closed wins over the no_evidence group).
    from branch_tracking.pipeline.network import infer_tertiary_status
    cim = pd.read_csv(tests_dir / "fixtures" / "cim_multigroup_slice.csv", dtype=str)
    status = pd.DataFrame([("911001", "Closed")], columns=["teid", "default_status"])
    out = infer_tertiary_status(cim, status)
    wx = out[out["teid"] == "911002"]
    assert len(wx) == 1
    assert wx.iloc[0]["inferred_status"] == "Closed"
