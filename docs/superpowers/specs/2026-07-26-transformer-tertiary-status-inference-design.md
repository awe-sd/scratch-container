# Transformer tertiary-winding status inference (via a CIM network graph)

**Date:** 2026-07-26
**Scope:** branch_tracking — recover `default_status` for 3-winding-transformer
tertiary stubs that have no `branch_id` and therefore no derived status.

## Problem

`branch_tracking_table.csv` has no status for 524 of 11,443 teids. The largest
bucket is **451 `transformer_tertiary_stub` teids**: the low-voltage (~1 kV) leg
of a CIM 3-winding-transformer decomposition. These legs are a modeling
artifact — the star point is fictitious, so they never appear in `dbo.BRANCH`,
never get a `branch_id`, never get name-matched to the DAM PSSE model, and thus
carry no status. They are not a data error; they simply need their status
*inferred* from the physical transformer they belong to.

Electrical fact we exploit: the three windings of one physical transformer are
energized together. If the primary and secondary legs are in service, the
tertiary leg is in service too.

## Topology (verified against the July CIM export)

A 3-winding transformer is three CIM `Transformer` rows that share a common
internal **star (connectivity) bus** and a common `CircuitIdentifier`, all in the
same substation. Example — SNDSW:

| teid | Name | BusNumber1 | BusNumber2 (star) | CircuitIdentifier |
|---|---|---|---|---|
| 280447 | MR1H 345kV-1kV | 13429 | 24107 | 2 |
| 280444 | MR1L 138kV-1kV | 13441 | 24107 | 2 |
| 280453 | MR1T 13.8kV-1kV | 13440 | 24107 | 2 |

The star bus (24107) is a genuine modeled node (it has its own `Bus` row). It is
NOT `GroupName` (that is substation-level — up to 34 transformers) and NOT bare
`BusNumber2` alone (co-located transformers can share modeling patterns; the
`CircuitIdentifier` separates them).

**Authoritative grouping key: `(Substation1, star bus, CircuitIdentifier)`.**
Under this key the windings partition as: 378 clean 3-winding groups, 21
two-winding, 2 four-winding, 1615 singletons.

## Design

### 1. `pipeline/network.py` — light NetworkX topology graph
Pure function, no DB. Built from the CIM CSV:
- **Nodes** = buses (`BusNumber`), attrs: bus name, kV, substation.
- **Edges** = `Branch` (line) and `Transformer` (winding) rows, attrs: `teid`,
  `DeviceType`, `default_status` (joined from `branch_tracking_table.csv`).
- A parallel-edge-tolerant graph (`MultiGraph`) since two buses can have several
  circuits between them.
- Built in-memory on demand. No persisted graph artifact in this phase (can add
  GraphML export later if a downstream consumer wants it).

This graph is the reusable substrate; the tertiary inference is its first
consumer, and the generator-plant-internal problem is expected to reuse it.

### 2. Winding-group identification
A helper (in `network.py` or a small `pipeline/windings.py`) that returns, for
each physical transformer, the set of winding teids sharing
`(Substation1, star bus, CircuitIdentifier)`. In graph terms: an internal
low-kV bus whose incident edges are all transformer windings. The star bus is
identified as the bus common to all windings of the group (not assumed to be
`BusNumber2`).

### 3. `scripts/adhoc/infer_tertiary_status.py` — inference
For each group containing at least one winding **with** a known status and at
least one **without**:
- **All-agree rule:** if every status-bearing sibling is `Closed` (in service),
  set each missing winding to `Closed`, source `inferred_transformer_winding`.
- If the known siblings **conflict** (some Closed, some Open) or are **all Open**,
  do NOT infer — emit the row with a `conflict` / `all_siblings_open` flag for
  manual review. A 3-winding transformer with one energized and one open leg is
  a real operating state, not something to guess through.
- Groups where no winding has status (~21 windings) are reported as
  `no_evidence` — nothing to propagate from.

### 4. Output
`output/inferred_tertiary_status.csv`, one row per recovered/flagged winding:
`teid, substation, star_bus, ckt, winding_name, inferred_status, source,
sibling_teids, sibling_statuses, flag`. Expected ≈430 recovered `Closed`, the
rest flagged.

Folding these inferences into `branch_tracking_table.csv` (updating
`default_status` / `default_status_source`) is a **separate follow-up step**,
done only after eyeballing this CSV — not part of this spec.

## Dependencies
Add `networkx` to `pyproject.toml` dependencies (pure-Python, light).

## Testing
DB-free, fixture-based (consistent with the existing suite in
`branch_tracking/tests/`):
- `network.py`: a tiny CIM fixture (one 3-winding transformer + one line) builds
  the expected nodes/edges with correct attrs.
- grouping: the SNDSW-style fixture yields exactly the MR1 winding trio under the
  `(substation, star bus, ckt)` key; a co-located second transformer stays
  separate.
- inference: fixtures covering all-Closed → inferred Closed; Closed+Open →
  conflict flag; all-Open → flag; no-status-siblings → no_evidence.

## Non-goals
- Generator-plant-internal status (next problem, may reuse the graph).
- Mutating `branch_tracking_table.csv` (separate follow-up).
- Persisting the graph to disk.
- Any DB write (hard rule).
