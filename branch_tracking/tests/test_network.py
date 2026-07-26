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
