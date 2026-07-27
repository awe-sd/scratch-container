"""Light in-memory CIM topology graph: buses are nodes, Branch/Transformer
rows are edges. Built from the CIM export DataFrame; pure logic, no DB, no
file I/O (callers hand it DataFrames). The reusable substrate for
winding-group status inference (windings.py / infer_tertiary_status.py) and
future connectivity work.

Parallel circuits between the same bus pair are common, so the graph is a
MultiGraph. Each edge carries its teid, device type, circuit id, substation,
name, and (optionally joined) default_status.
"""
from collections import OrderedDict

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
            _clean(t): _clean(d)
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


def transformer_winding_groups(cim: pd.DataFrame) -> list[dict]:
    """Group transformer windings by their internal star (connectivity) bus,
    using the topology graph. A star bus is a graph node of degree >= 2 whose
    incident edges are ALL transformer windings (no line edges) -- a purely
    internal node, never a real transmission bus. Column-agnostic (the star may
    sit in BusNumber1 or BusNumber2) and splits co-located transformers, each of
    which has its own star bus.
    """
    g = build_graph(cim)
    groups = []
    for node in g.nodes():
        incident = list(g.edges(node, data=True))
        if len(incident) < 2:
            continue
        if not all(d.get("device_type") == "Transformer" for _, _, d in incident):
            continue
        teids = [d.get("teid") for _, _, d in incident]
        substation = next((d.get("substation") for _, _, d in incident if d.get("substation")), None)
        ckt = next((d.get("ckt") for _, _, d in incident if d.get("ckt")), None)
        groups.append({
            "substation": substation,
            "star_bus": node,
            "ckt": ckt,
            "winding_teids": teids,
        })
    return groups


def infer_tertiary_status(cim: pd.DataFrame, status: pd.DataFrame) -> pd.DataFrame:
    smap = {}
    for t, d in zip(status["teid"], status["default_status"]):
        t = _clean(t)
        d = _clean(d)
        if t is not None and d is not None:
            smap[t] = d

    name_map = {d.get("teid"): d.get("name") for _, _, d in build_graph(cim).edges(data=True)}

    rows = []
    for grp in transformer_winding_groups(cim):
        teids = grp["winding_teids"]
        known = [(t, smap[t]) for t in teids if t in smap]
        missing = [t for t in teids if t not in smap]
        if not missing:
            continue

        known_statuses = [s for _, s in known]
        sib_teids = ";".join(t for t, _ in known)
        sib_statuses = ";".join(known_statuses)

        if not known:
            flag, inferred, source = "no_evidence", None, None
        elif all(s == "Closed" for s in known_statuses):
            flag, inferred, source = "", "Closed", "inferred_transformer_winding"
        elif all(s == "Open" for s in known_statuses):
            flag, inferred, source = "all_siblings_open", None, None
        else:
            flag, inferred, source = "conflict", None, None

        for t in missing:
            rows.append({
                "teid": t,
                "winding_name": name_map.get(t),
                "substation": grp["substation"],
                "star_bus": grp["star_bus"],
                "ckt": grp["ckt"],
                "inferred_status": inferred,
                "source": source,
                "sibling_teids": sib_teids,
                "sibling_statuses": sib_statuses,
                "flag": flag,
            })
    # A winding whose both endpoint buses are internal star buses (e.g. a VFT
    # converter) lands in two groups -> the same teid emitted twice. Collapse to
    # one row per teid. Inference only ever yields "Closed" or None, so a
    # concrete Closed from any group wins; otherwise keep the first (flagged) row.
    by_teid = OrderedDict()
    for r in rows:
        by_teid.setdefault(r["teid"], []).append(r)
    deduped = []
    for _teid, rs in by_teid.items():
        closed = [r for r in rs if r["inferred_status"] == "Closed"]
        if closed:
            keep = dict(closed[0])
            merged_sibs = sorted({s for r in closed for s in (r["sibling_teids"] or "").split(";") if s})
            keep["sibling_teids"] = ";".join(merged_sibs)
            keep["sibling_statuses"] = ";".join(smap.get(s, "") for s in merged_sibs)
            deduped.append(keep)
        else:
            deduped.append(rs[0])
    rows = deduped

    return pd.DataFrame(rows, columns=[
        "teid", "substation", "star_bus", "ckt", "winding_name", "inferred_status", "source",
        "sibling_teids", "sibling_statuses", "flag",
    ])
