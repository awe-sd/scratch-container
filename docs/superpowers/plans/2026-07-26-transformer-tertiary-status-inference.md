# Transformer Tertiary-Winding Status Inference Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recover `default_status` for the ~430 3-winding-transformer tertiary stubs by building a light CIM network graph and propagating status from the sibling windings of each physical transformer.

**Architecture:** A new pure-logic module `pipeline/network.py` builds an in-memory NetworkX `MultiGraph` from the CIM export (buses = nodes, lines + transformer windings = edges tagged with `teid`/`default_status`) and exposes a winding-grouping helper keyed on `(Substation1, star bus, CircuitIdentifier)`. A new adhoc script consumes the grouping to infer tertiary status under an all-agree-else-flag rule, writing a review CSV. Nothing mutates `branch_tracking_table.csv`; no DB access.

**Tech Stack:** Python 3.12+, pandas, networkx (new dependency), pytest.

## Global Constraints

- Python `requires-python = ">=3.12"`; run everything via `uv run` (never bare `python`/`pip`).
- Hard rule: this folder produces only SQL DDL and CSV outputs. No DB writes, no `INSERT`/`dfInsert*`. This feature is DB-free entirely (reads local CSVs only).
- Pipeline modules live in `branch_tracking/pipeline/`, are pure logic (no DB, no I/O beyond being handed DataFrames), import siblings via `from .config import ...` / `from .network import ...`, and set `REPO_ROOT = Path(__file__).resolve().parents[2]`.
- Tests live in `branch_tracking/tests/`, are DB-free and fixture-based, use the `repo_root` / `tests_dir` fixtures from `conftest.py`, and run via `uv run pytest` from the repo root (`testpaths = ["branch_tracking/tests"]`).
- Status vocabulary: `default_status` values are `"Closed"` (in service) / `"Open"`; missing = blank/NaN.
- CIM export path: `branch_tracking/data/CIM_Jul_ML1_1_07142026_Redacted_20260801-003000_TeidMap.csv`. Consolidated table: `branch_tracking/output/branch_tracking_table.csv`.
- Authoritative winding-group key: `(Substation1, star bus, CircuitIdentifier)`. The star bus is the bus common to every winding in the group (do NOT hardcode `BusNumber2`).

---

### Task 1: Add `networkx` dependency

**Files:**
- Modify: `pyproject.toml` (dependencies list)
- Modify: `uv.lock` (regenerated)

**Interfaces:**
- Consumes: nothing.
- Produces: `import networkx as nx` available to later tasks.

- [ ] **Step 1: Add networkx to dependencies**

In `pyproject.toml`, add `"networkx>=3.4"` to the `[project].dependencies` list (keep the existing `pandas`, `pdfplumber`, `pillow`, `pypdf` entries; alphabetical-ish order is fine):

```toml
dependencies = [
    "networkx>=3.4",
    "pandas>=3.0.3",
    "pdfplumber>=0.11.10",
    "pillow>=12.3.0",
    "pypdf>=6.14.2",
]
```

- [ ] **Step 2: Lock and install**

Run: `uv lock && uv sync`
Expected: `networkx` resolves and installs; no errors.

- [ ] **Step 3: Verify import**

Run: `uv run python -c "import networkx as nx; print(nx.__version__)"`
Expected: prints a version >= 3.4.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "deps: add networkx for CIM topology graph"
```

---

### Task 2: `pipeline/network.py` — build the topology graph

**Files:**
- Create: `branch_tracking/pipeline/network.py`
- Test: `branch_tracking/tests/test_network.py`
- Test fixture: `branch_tracking/tests/fixtures/cim_slice.csv`

**Interfaces:**
- Consumes: nothing from earlier tasks (Task 1 only provides the library).
- Produces:
  - `build_graph(cim: pd.DataFrame, status: pd.DataFrame | None = None) -> networkx.MultiGraph`
    - `cim`: CIM export rows (all `PsseType`s). Uses `PsseType`, `BusNumber1`, `BusNumber2`, `BusName1`, `BusName2`, `Substation1`, `Substation2`, `TransmissionElementId`, `CircuitIdentifier`, `Name`, `GroupName`.
    - `status`: optional frame with columns `teid`, `default_status`; when given, each edge gets a `default_status` attr (else `None`).
    - Nodes keyed by bus number string; node attrs: `name`, `substation`. Edges added for every `PsseType in {"Branch","Transformer"}` row between `BusNumber1` and `BusNumber2`; edge attrs: `teid`, `device_type` (the `PsseType`), `ckt` (`CircuitIdentifier`), `substation` (`Substation1`), `name` (`Name`), `default_status`.

- [ ] **Step 1: Write the fixture**

Create `branch_tracking/tests/fixtures/cim_slice.csv` with a header matching the real CIM columns (`RunRefId,NodeType,PsseType,RdfId,BusNumber1,BusNumber2,BusName1,BusName2,Substation1,Substation2,BusNumber3,BusName3,Substation3,CircuitIdentifier,Name,TransmissionElementId,GroupName,EquipmentName,OpEqName,CimEnvironment`) and these rows (one 3-winding transformer MR1 at SNDSW sharing star bus 24107 ckt 2, plus one ordinary line):

```
r,bus,Bus,rid1,13429,0,SNDSW_345,,SNDSW,,0,,,2,SNDSW_345 138kV,900001,SNDSW,B345,B345,PROD
r,bus,Bus,rid2,13441,0,SNDSW_138,,SNDSW,,0,,,2,SNDSW_138 138kV,900002,SNDSW,B138,B138,PROD
r,bus,Bus,rid3,13440,0,SNDSW_13,,SNDSW,,0,,,2,SNDSW_13 13kV,900003,SNDSW,B13,B13,PROD
r,bus,Bus,rid4,24107,0,SNDSW1_1,,SNDSW,,0,,,2,SNDSW1_1 1kV,900004,SNDSW,STAR,STAR,PROD
r,br,Transformer,rid5,13429,24107,SNDSW_345,SNDSW1_1,SNDSW,SNDSW,0,,,2,MR1H 345kV-1kV,280447,SNDSW,MR1H,SNDSW_MR1H,PROD
r,br,Transformer,rid6,13441,24107,SNDSW_138,SNDSW1_1,SNDSW,SNDSW,0,,,2,MR1L 138kV-1kV,280444,SNDSW,MR1L,SNDSW_MR1L,PROD
r,br,Transformer,rid7,13440,24107,SNDSW_13,SNDSW1_1,SNDSW,SNDSW,0,,,2,MR1T 13.8kV-1kV,280453,SNDSW,MR1T,SNDSW_MR1T,PROD
r,br,Branch,rid8,13429,99999,SNDSW_345,OTHER_345,SNDSW,OTHER,0,,,1,SNDSW-OTHER 345kV,700001,LINEGRP,L1,L1,PROD
```

- [ ] **Step 2: Write the failing test**

```python
# branch_tracking/tests/test_network.py
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
```

- [ ] **Step 3: Run test to verify it fails**

Run: `uv run pytest branch_tracking/tests/test_network.py -v`
Expected: FAIL with `ModuleNotFoundError` / `cannot import name 'build_graph'`.

- [ ] **Step 4: Implement `network.py`**

```python
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest branch_tracking/tests/test_network.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add branch_tracking/pipeline/network.py branch_tracking/tests/test_network.py branch_tracking/tests/fixtures/cim_slice.csv
git commit -m "feat(network): build in-memory CIM topology graph from the export"
```

---

### Task 3: `pipeline/network.py` — winding-group helper

**Files:**
- Modify: `branch_tracking/pipeline/network.py`
- Test: `branch_tracking/tests/test_network.py` (add a test)

**Interfaces:**
- Consumes: `build_graph` from Task 2; the same `cim` frame.
- Produces:
  - `transformer_winding_groups(cim: pd.DataFrame) -> list[dict]`
    - Returns one dict per physical multi-winding transformer:
      `{"substation": str, "star_bus": str, "ckt": str, "winding_teids": list[str]}`.
    - Grouping key: transformer rows sharing `(Substation1, star bus, CircuitIdentifier)`, where **star bus** is the bus common to every winding in the candidate group. Implementation: group `Transformer` rows by `(Substation1, CircuitIdentifier)`, then within each, find the bus number appearing in every row's `{BusNumber1, BusNumber2}`; that common bus is the star bus. Only emit groups with >= 2 windings that share a single common bus.

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest branch_tracking/tests/test_network.py::test_transformer_winding_groups -v`
Expected: FAIL with `cannot import name 'transformer_winding_groups'`.

- [ ] **Step 3: Implement the helper**

Append to `branch_tracking/pipeline/network.py`:

```python
def transformer_winding_groups(cim: pd.DataFrame) -> list[dict]:
    xf = cim[cim["PsseType"] == "Transformer"].copy()
    groups = []
    for (sub, ckt), g in xf.groupby(["Substation1", "CircuitIdentifier"], dropna=False):
        if len(g) < 2:
            continue
        bus_sets = [
            {_clean(r["BusNumber1"]), _clean(r["BusNumber2"])} - {None}
            for _, r in g.iterrows()
        ]
        common = set.intersection(*bus_sets) if bus_sets else set()
        if len(common) != 1:
            continue  # no single shared star bus -> not one physical unit
        star = next(iter(common))
        groups.append({
            "substation": _clean(sub),
            "star_bus": star,
            "ckt": _clean(ckt),
            "winding_teids": [_clean(t) for t in g["TransmissionElementId"]],
        })
    return groups
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest branch_tracking/tests/test_network.py -v`
Expected: PASS (both tests).

- [ ] **Step 5: Commit**

```bash
git add branch_tracking/pipeline/network.py branch_tracking/tests/test_network.py
git commit -m "feat(network): group transformer windings by (substation, star bus, ckt)"
```

---

### Task 4: `pipeline/network.py` — tertiary status inference logic

**Files:**
- Modify: `branch_tracking/pipeline/network.py`
- Test: `branch_tracking/tests/test_network.py` (add tests)

**Interfaces:**
- Consumes: `transformer_winding_groups` (Task 3).
- Produces:
  - `infer_tertiary_status(cim: pd.DataFrame, status: pd.DataFrame) -> pd.DataFrame`
    - `status`: frame with `teid`, `default_status` (the consolidated table's resolved status).
    - Returns one row per winding that is missing status in an otherwise-known group, columns:
      `teid, substation, star_bus, ckt, inferred_status, source, sibling_teids, sibling_statuses, flag`.
    - Rule per group with >= 1 known and >= 1 missing winding:
      - known siblings all `"Closed"` → each missing winding: `inferred_status="Closed"`, `source="inferred_transformer_winding"`, `flag=""`.
      - known siblings conflict (mix of Closed/Open) → `inferred_status=None`, `flag="conflict"`.
      - known siblings all `"Open"` → `inferred_status=None`, `flag="all_siblings_open"`.
    - Groups with no known winding → each missing winding emitted with `flag="no_evidence"`, `inferred_status=None`.
    - `sibling_statuses` is a `;`-joined list of the known siblings' statuses; `sibling_teids` a `;`-joined list of known sibling teids.

- [ ] **Step 1: Write the failing tests**

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest branch_tracking/tests/test_network.py -k infer -v`
Expected: FAIL with `cannot import name 'infer_tertiary_status'`.

- [ ] **Step 3: Implement the inference**

Append to `branch_tracking/pipeline/network.py`:

```python
def infer_tertiary_status(cim: pd.DataFrame, status: pd.DataFrame) -> pd.DataFrame:
    smap = {}
    for t, d in zip(status["teid"], status["default_status"]):
        t = _clean(t)
        d = _clean(d)
        if t is not None and d is not None:
            smap[t] = d

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
                "substation": grp["substation"],
                "star_bus": grp["star_bus"],
                "ckt": grp["ckt"],
                "inferred_status": inferred,
                "source": source,
                "sibling_teids": sib_teids,
                "sibling_statuses": sib_statuses,
                "flag": flag,
            })
    return pd.DataFrame(rows, columns=[
        "teid", "substation", "star_bus", "ckt", "inferred_status", "source",
        "sibling_teids", "sibling_statuses", "flag",
    ])
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest branch_tracking/tests/test_network.py -v`
Expected: PASS (all network tests).

- [ ] **Step 5: Commit**

```bash
git add branch_tracking/pipeline/network.py branch_tracking/tests/test_network.py
git commit -m "feat(network): infer tertiary winding status (all-agree-else-flag)"
```

---

### Task 5: `scripts/adhoc/infer_tertiary_status.py` — script wrapper + real-data run

**Files:**
- Create: `branch_tracking/scripts/adhoc/infer_tertiary_status.py`
- Output (generated): `branch_tracking/output/inferred_tertiary_status.csv`

**Interfaces:**
- Consumes: `build_graph` is not needed here; uses `infer_tertiary_status` from `pipeline/network.py`. Reads the CIM CSV and `branch_tracking_table.csv` from disk.
- Produces: the review CSV; a printed summary. No return value.

- [ ] **Step 1: Write the script**

```python
"""Infer default_status for 3-winding-transformer tertiary stubs that have no
branch_id (hence no DAM/auction status), by propagating from their sibling
windings. Pure local-file analysis -- reads the CIM export + the consolidated
branch_tracking_table, writes a review CSV. No DB, writes only to output/.

Grouping + rule live in pipeline/network.py (all-agree-else-flag). This wrapper
is I/O + a summary print only. Folding the results into branch_tracking_table
is a SEPARATE follow-up, deliberately not done here.

Run: uv run branch_tracking/scripts/adhoc/infer_tertiary_status.py
"""
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
CIM_CSV = REPO_ROOT / "branch_tracking/data/CIM_Jul_ML1_1_07142026_Redacted_20260801-003000_TeidMap.csv"
TABLE_CSV = REPO_ROOT / "branch_tracking/output/branch_tracking_table.csv"
OUTPUT_CSV = REPO_ROOT / "branch_tracking/output/inferred_tertiary_status.csv"


def main():
    import sys
    sys.path.insert(0, str(REPO_ROOT))
    from branch_tracking.pipeline.network import infer_tertiary_status

    cim = pd.read_csv(CIM_CSV, dtype=str)
    table = pd.read_csv(TABLE_CSV, dtype=str)
    status = table[["teid", "default_status"]]

    out = infer_tertiary_status(cim, status)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_CSV, index=False)

    print("=== tertiary-winding status inference ===")
    print(f"windings emitted: {len(out)}")
    print("by flag:")
    print(out["flag"].replace("", "inferred_closed").value_counts().to_string())
    recovered = out[out["inferred_status"].notna()]
    print(f"\nrecovered with a status: {len(recovered)}")
    print(f"Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script**

Run: `uv run branch_tracking/scripts/adhoc/infer_tertiary_status.py`
Expected: prints a summary; `inferred_closed` count in the low-400s (~430), plus `conflict`/`all_siblings_open`/`no_evidence` buckets; writes the CSV.

- [ ] **Step 3: Sanity-check the output against the known SNDSW case**

Run: `uv run python -c "import pandas as pd; d=pd.read_csv('branch_tracking/output/inferred_tertiary_status.csv', dtype=str); print(d[d.teid=='280453'].to_string())"`
Expected: teid `280453` (MR1T) present with `inferred_status=Closed`, `source=inferred_transformer_winding`, empty flag, siblings `280447;280444` (or reverse) both `Closed`.

- [ ] **Step 4: Cross-check the recovered count against the gap worklist**

Run: `uv run python -c "import pandas as pd; d=pd.read_csv('branch_tracking/output/inferred_tertiary_status.csv', dtype=str); print('recovered:', d.inferred_status.notna().sum())"`
Expected: recovered count is ~430 and does not exceed the 451 `transformer_tertiary_stub` teids from `status_gaps_worklist.csv`.

- [ ] **Step 5: Commit**

```bash
git add branch_tracking/scripts/adhoc/infer_tertiary_status.py branch_tracking/output/inferred_tertiary_status.csv
git commit -m "feat(adhoc): infer tertiary-winding status -> inferred_tertiary_status.csv"
```

---

### Task 6: Documentation

**Files:**
- Modify: `branch_tracking/CLAUDE.md` (Code layout + Scripts sections)

**Interfaces:**
- Consumes: nothing.
- Produces: nothing (docs only).

- [ ] **Step 1: Document the new module and script**

In `branch_tracking/CLAUDE.md`, under the `pipeline/` layout bullet add `network` to the module list, and under the Scripts section add:

```
- `scripts/adhoc/infer_tertiary_status.py` — infers `default_status` for 3-winding-transformer tertiary stubs (no branch_id, hence no DAM/auction status) by propagating from sibling windings grouped on `(substation, star connectivity bus, CircuitIdentifier)`, all-agree-else-flag. Output: `output/inferred_tertiary_status.csv` (review artifact; NOT yet folded into `branch_tracking_table.csv`). Logic in `pipeline/network.py`.
```

- [ ] **Step 2: Run the full suite as a regression gate**

Run: `uv run pytest`
Expected: all tests pass (existing 20 + the new network tests).

- [ ] **Step 3: Commit**

```bash
git add branch_tracking/CLAUDE.md
git commit -m "docs: describe network.py + tertiary-status inference script"
```

---

## Self-Review

**Spec coverage:**
- Light NetworkX graph (buses/nodes, lines+windings/edges, teid+status attrs) → Task 2. ✓
- Winding-group id via `(substation, star bus, ckt)`, star bus = common bus not hardcoded → Task 3. ✓
- All-agree-else-flag inference; conflict/all-open/no-evidence flags → Task 4. ✓
- Review CSV output, no table mutation → Task 5. ✓
- `networkx` dependency added → Task 1. ✓
- DB-free fixture tests for graph/grouping/inference → Tasks 2–4. ✓
- Non-goals (no gen-plant-internal, no table fold, no graph persistence, no DB) respected across all tasks. ✓

**Placeholder scan:** No TBD/TODO; every code step has concrete code. ✓

**Type consistency:** `build_graph`, `transformer_winding_groups` (returns list of dicts with `substation`/`star_bus`/`ckt`/`winding_teids`), `infer_tertiary_status` (returns the 9-column frame) are used consistently across Tasks 2–5. Script reads `default_status` from the table and passes `teid,default_status` as `status`, matching each function's contract. ✓
