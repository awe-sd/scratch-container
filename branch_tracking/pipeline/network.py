"""Light in-memory CIM topology graph: buses are nodes, Branch/Transformer
rows are edges. Built from the CIM export DataFrame; pure logic, no DB, no
file I/O (callers hand it DataFrames). The reusable substrate for
winding-group status inference (windings.py / infer_tertiary_status.py) and
future connectivity work.

Parallel circuits between the same bus pair are common, so the graph is a
MultiGraph. Each edge carries its teid, device type, circuit id, substation,
name, and (optionally joined) default_status.
"""
import networkx as nx
import pandas as pd

EDGE_TYPES = ("Branch", "Transformer")


def _clean(value):
    if pd.isna(value):
        return None
    s = str(value).strip()
    return s or None


def build_graph(cim: pd.DataFrame, status: pd.DataFrame | None = None) -> nx.MultiGraph:
    status_map = {}
    if status is not None:
        status_map = {
            str(t).strip(): d
            for t, d in zip(status["teid"], status["default_status"])
        }

    g = nx.MultiGraph()

    # Nodes: every bus we see, from both the Bus rows and edge endpoints.
    buses = cim[cim["PsseType"] == "Bus"]
    for _, r in buses.iterrows():
        b = _clean(r["BusNumber1"])
        if b is not None:
            g.add_node(b, name=_clean(r["BusName1"]), substation=_clean(r["Substation1"]))

    edges = cim[cim["PsseType"].isin(EDGE_TYPES)]
    for _, r in edges.iterrows():
        b1, b2 = _clean(r["BusNumber1"]), _clean(r["BusNumber2"])
        if b1 is None or b2 is None:
            continue
        for b, name, sub in ((b1, r["BusName1"], r["Substation1"]),
                             (b2, r["BusName2"], r["Substation2"])):
            if b not in g:
                g.add_node(b, name=_clean(name), substation=_clean(sub))
        teid = _clean(r["TransmissionElementId"])
        g.add_edge(
            b1, b2,
            teid=teid,
            device_type=_clean(r["PsseType"]),
            ckt=_clean(r["CircuitIdentifier"]),
            substation=_clean(r["Substation1"]),
            name=_clean(r["Name"]),
            default_status=status_map.get(teid),
        )
    return g
