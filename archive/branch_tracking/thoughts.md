ssu# Branch Tracking Table — Development Plan

## Purpose
A topology database for tracking transmission branches over time, keyed on branch identity, with status, in-service/retirement dates, and CIM model linkage.

## Column Definitions & Source Mapping

**branch_id + teid 
Core identity columns. The table maps `teid` and `branch_id`, potentially using the branch table to cross-check the from/to bus and CKT ID.
for cross checking you will need to go from branch_id to pto_branch_id to get the branch from /to bus number but the bus name is in the branch id , there also can be duplicates in the branch table for teid, as the teid is not enforeced as primary key. 

**status**
Sourced from DAM (Day-Ahead Market), or potentially by being able to find the outage for the actual (physical) state.

**in_service_date**
From an outage-data search that fits a pattern of outage type `new` — equipment additions.

**retirement_date**
From the same outage-data search, fitting a pattern of outage type `retirement`.

> Open question flagged on both date columns: Is there a secondary source of data to confirm status — e.g., 60-Day SCED data? / DAM network model.

**default_status**
Closed or normally open.

**cim_id**
Initially just the July model, with the ability to search for the earliest entry of the TEID + RDFID + (r, x, b) pair.

## Design Notes
- The two date columns (`in_service_date`, `retirement_date`) are both derived from the same outage-data pattern search, distinguished by outage type (`new` vs. `retirement`).
- Status determination has a primary source (DAM) with a desired secondary confirmation source (60-Day SCED / DAM network model) still to be resolved.
- CIM linkage starts scoped to the July model, with logic to trace the earliest matching entry via the TEID + RDFID + electrical-parameter (r, x, b) tuple.

---

## Investigation Findings

**Everything below this line was written by an AI model (Claude, via Claude Code), not the human author of the sections above.** It documents what was empirically found while investigating the design above — treat it as evidence to check, not as settled decisions. See `scripts/` for the code that produced these numbers and `output/` for the underlying CSVs.

### Source discrepancy: SQL Server vs Snowflake

`dbo.BRANCH` (via `awconnect.db`, SQL Server) and `AW.DBO.BRANCH` (via `awconnect.snowflake`) are supposed to mirror each other but do not agree:

| | SQL Server | Snowflake |
|---|---|---|
| `BRANCH` rows, `isomarketid = 6` | 122,259 | 129,635 |
| Distinct duplicated `teid` values | 7,523 | 13,596 |
| Column casing | camelCase (`branchID`, `branchName`, ...) | ALL CAPS (`BRANCHID`, `BRANCHNAME`, ...) |
| Nullability | `branchID`/`branchName` are `NOT NULL` | shown as nullable |

**This needs to be resolved before picking a source of truth for the tracking table** — the two are not interchangeable, and it's not yet known which (if either) is authoritative.

### teid → branch_id mapping (`scripts/build_teid_branchid_map.py`)

Joined the CIM July model export's `Branch`/`Transformer` rows to SQL Server `dbo.BRANCH` on `teid`, after excluding `NodeType in ('Breaker', 'Disconnector')` (switching devices lumped under CIM `PsseType == 'Branch'`, not real lines/transformers).

- 11,443 CIM rows considered → 9,039 matched 1:1, 513 unmatched, 3,928 flagged `duplicate_match` (one CIM `teid` hitting >1 `BRANCH` row).

### Unmatched rows (513) — `scripts/analyze_unmatched.py`

None of the 513 appear to be a real gap in `BRANCH`. Two patterns explain essentially all of them:

1. **`transformer_tertiary_stub` (451/513)** — every one is a `PsseType == 'Transformer'` row whose CIM `Name` shows the low-voltage terminal at ~1kV (e.g. `MR1T 13.8kV-1kV`). This is the standard CIM 3-winding-transformer decomposition artifact: the tertiary leg to an internal star/dummy point, not a second physical branch. `BRANCH` only carries the primary/secondary 2-winding equivalent.
2. **`generation_plant_internal` (54/513)** — remaining `Branch`-type rows (`ACLineSegment`/`SeriesCompensator`) sitting inside generation-plant substations (solar `_SLR`, wind `_WND`/`_WIND`, battery `_ESS`, industrial cogen `DOWGEN`/`THW`/`RNPCOGEN`, station-load `SL`). Verified against an exact, manually-checked set of 24 substation codes — see `GEN_PLANT_SUBSTATIONS` in the script. Mostly current-limiting reactors (`OpEqName` ending `_CLR`) at generator interconnection points, i.e. collector-system equipment behind the meter.
3. **Residual (8/513)** — 2 rows (`NA_GT1`/`NA_GT2`, "GT" = gas turbine) are the same generation-plant pattern but missing substation metadata in the CIM export, so the exact-match list didn't catch them. 6 `Transformer` rows didn't fit the ~1kV rule (e.g. `VFT 17.5kV-17.5kV`, `2MP0 34.5kV-13.8kV`) — not yet explained, worth a manual look if this matters.

### Duplicate `teid` values in `BRANCH` (7,523 distinct) — `scripts/analyze_duplicate_teids.py` / `..._snowflake.py`

Open question was: are these the same physical branch re-inserted over time (harmless), or `teid` genuinely reused across unrelated branches (a real data-quality problem)?

- `BRANCH.b1`/`b2`/`ckt` turned out to be **blank for the vast majority of rows** (only populated for `BRKR`-type rows) — not usable as an identity check on their own.
- The real from/to bus numbers live in `PTOBRANCH`, joined via `branchID`. But `PTOBRANCH` has **3.78M rows for only 15,589 distinct `branchID` values** (out of 122,259 in `BRANCH`) — i.e. only ~12.7% of `BRANCH` rows have *any* `PTOBRANCH` coverage at all. Where a `branchID` does appear, it can have hundreds of rows (looks like a historical/snapshot log, no timestamp column) — deduped here by keeping the largest `ptoBranchID` (as a "latest" proxy) after excluding placeholder bus numbers (`fromNum`/`toNum` > 900,000).
- Because of that sparse coverage, most duplicate-`teid` groups can't be checked this way at all. Honest breakdown of the 7,523 groups:
  - **6,601 `insufficient_pto_data`** — fewer than 2 rows in the group have `PTOBRANCH` data, so no comparison is possible.
  - **615 `same_identity_reinserted`** — ≥2 `PTOBRANCH`-backed rows in the group agree on `(fromNum, toNum, ckt)`. Likely a real branch re-inserted/renamed over time.
  - **307 `teid_collision_different_branches`** — ≥2 `PTOBRANCH`-backed rows in the group disagree on bus numbers. Confirmed genuine `teid` reuse across unrelated branches.
- A weaker but broader signal: **911/7,523 groups have an explicit `collapseId` link** (one row's `collapseId` points at a sibling `branchID` in the same group) — this is the schema's own "superseded by" marker, strong evidence of intentional re-numbering rather than collision.
- Another weak signal: **178/7,523 groups mix `DeviceType`** (e.g. a `Line` sharing a `teid` with a `Transformer` or `breaker`) — equipment doesn't change type over time, so these are very likely genuine collisions, not renames. (7,345/7,523 groups are internally consistent on `DeviceType`, but since `Line` dominates the table this alone is weak evidence of relatedness.)
- **Net read**: there is clear evidence of both phenomena (legitimate re-numbering *and* genuine `teid` collisions) inside `BRANCH`, but for the large majority of duplicate groups the available columns can't disambiguate which is which. If this distinction matters for the tracking table's identity design, it likely needs another data source (e.g. a `BRANCH` history/audit table with timestamps, if one exists) rather than more slicing of the current columns.
- The Snowflake mirror shows a similar shape (178 mixed-`DeviceType` groups there too) but nearly double the duplicate-`teid` count (13,596 vs 7,523) — consistent with its larger overall row count, but not yet reconciled.
