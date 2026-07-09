"""
Compare branch Status between the user's PowerWorld base model export and our
pipeline's consolidated output (`output/branch_tracking_table.csv`), flagging
disagreements.

Pure local-file comparison -- no database access.

Inputs:
  - data/base_model.csv
      PowerWorld export. Three "label" columns ("Labels All" + two unnamed)
      carry up to 3 values per row in RANDOM order: a string label, a teid
      (all-digits), and an rdfid (UUID-shaped). We classify by format, not
      position, and ignore the string label entirely (per user instruction).
  - data/CIM_Jul_ML1_1_07142026_Redacted_20260801-003000_TeidMap.csv
      CIM export used to map rdfid -> teid (RdfId -> TransmissionElementId)
      when base_model.csv's row has no directly-parseable teid label.
  - output/branch_tracking_table.csv
      Our pipeline's consolidated per-teid table (teid, branch_id,
      implied_default_status, from_bus, to_bus, ckt, DeviceType, pct_closed, ...).

Output:
  - output/base_model_status_comparison.csv
      Only the disagreement rows (base model Status vs. our
      implied_default_status differ), one row per base_model row that
      disagreed (a teid with multiple base_model rows -- e.g. multi-section
      lines -- can appear more than once).

Run with: uv run branch_tracking/scripts/compare_base_model_status.py [base_model_csv]

The optional argument selects a different PowerWorld export (default:
data/base_model.csv). E.g. data/base_model_outages.csv is the same case with
outages applied (statuses reflect outaged elements) and an extra "MW Loss"
column. Because the extra column shifts the unnamed label columns, the label
columns are detected dynamically: "Labels All" plus every column after it.
The output filename is derived from the input name:
base_model.csv -> output/base_model_status_comparison.csv,
base_model_outages.csv -> output/base_model_outages_status_comparison.csv.
"""

import re
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE_MODEL_CSV = REPO_ROOT / "branch_tracking/data/base_model.csv"
TEID_MAP_CSV = (
    REPO_ROOT
    / "branch_tracking/data/CIM_Jul_ML1_1_07142026_Redacted_20260801-003000_TeidMap.csv"
)
BRANCH_TRACKING_CSV = REPO_ROOT / "branch_tracking/output/branch_tracking_table.csv"
OUTPUT_DIR = REPO_ROOT / "branch_tracking/output"

UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
TEID_RE = re.compile(r"^\d+$")


def label_columns(df):
    """Return "Labels All" plus every column after it. PowerWorld puts the
    label group last, but the columns preceding it vary between exports
    (e.g. base_model_outages.csv adds "MW Loss"), so position can't be
    hardcoded."""
    cols = list(df.columns)
    idx = cols.index("Labels All")
    return cols[idx:]


def classify_label(value):
    """Classify a single label-column value by format.

    Returns ('teid', str) or ('rdfid', str) or ('other', str) or (None, None)
    for missing/blank values.
    """
    if value is None:
        return None, None
    v = str(value).strip()
    if not v or v.lower() == "nan":
        return None, None
    if TEID_RE.match(v):
        return "teid", v
    if UUID_RE.match(v):
        return "rdfid", v
    return "other", v


def extract_teid_rdfid(row, label_cols):
    """Scan the label columns of a base_model row, classify each value by
    format, and return (teid_or_None, rdfid_or_None). If more than one teid
    or rdfid value is present (shouldn't happen), the first one found wins.
    """
    teid = None
    rdfid = None
    for col in label_cols:
        kind, val = classify_label(row.get(col))
        if kind == "teid" and teid is None:
            teid = val
        elif kind == "rdfid" and rdfid is None:
            rdfid = val
        # kind == "other" (the string label) is intentionally ignored.
    return teid, rdfid


def main():
    if len(sys.argv) > 2:
        sys.exit("usage: compare_base_model_status.py [base_model_csv]")
    base_model_csv = (
        Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else DEFAULT_BASE_MODEL_CSV
    )
    output_csv = OUTPUT_DIR / f"{base_model_csv.stem}_status_comparison.csv"

    # --- 1. Load the PowerWorld export ---------------------------------
    base = pd.read_csv(base_model_csv, encoding="utf-8-sig", dtype=str)
    base.columns = [c.strip() for c in base.columns]
    total_base_rows = len(base)
    label_cols = label_columns(base)

    extracted = base.apply(
        extract_teid_rdfid, axis=1, result_type="expand", label_cols=label_cols
    )
    extracted.columns = ["label_teid", "label_rdfid"]
    base = pd.concat([base, extracted], axis=1)

    n_neither = int(((base["label_teid"].isna()) & (base["label_rdfid"].isna())).sum())

    # --- 2. Resolve to a teid: direct label first, else via CIM TeidMap ---
    teid_map_df = pd.read_csv(TEID_MAP_CSV, dtype=str, usecols=["RdfId", "TransmissionElementId"])
    teid_map_df = teid_map_df.dropna(subset=["RdfId"])
    # Some RdfId values could theoretically repeat with different teids;
    # keep first, but track ambiguity for visibility.
    dup_rdfid_in_map = teid_map_df["RdfId"].duplicated().sum()
    rdfid_to_teid = dict(
        zip(teid_map_df["RdfId"], teid_map_df["TransmissionElementId"])
    )

    def resolve(row):
        if pd.notna(row["label_teid"]):
            return row["label_teid"], "direct_label"
        if pd.notna(row["label_rdfid"]):
            mapped = rdfid_to_teid.get(row["label_rdfid"])
            if mapped is not None and str(mapped).strip() and str(mapped).lower() != "nan":
                return str(mapped), "rdfid_mapped"
            return None, "rdfid_unmapped"
        return None, "no_label"

    resolved = base.apply(resolve, axis=1, result_type="expand")
    resolved.columns = ["resolved_teid", "match_type"]
    base = pd.concat([base, resolved], axis=1)

    n_direct = int((base["match_type"] == "direct_label").sum())
    n_rdfid_mapped = int((base["match_type"] == "rdfid_mapped").sum())
    n_rdfid_unmapped = int((base["match_type"] == "rdfid_unmapped").sum())
    n_no_label = int((base["match_type"] == "no_label").sum())
    n_unresolved = n_rdfid_unmapped + n_no_label

    unresolved_sample = base[base["resolved_teid"].isna()][
        ["From Name", "To Name", "Circuit", "Branch Device Type", "label_teid", "label_rdfid", "match_type"]
    ].head(10)

    # Duplicate resolved teids within base_model (e.g. multi-section lines)
    resolved_teid_counts = base.loc[base["resolved_teid"].notna(), "resolved_teid"].value_counts()
    dup_teids_in_base = resolved_teid_counts[resolved_teid_counts > 1]
    n_dup_teid_rows_base = int(dup_teids_in_base.sum())
    n_dup_teid_values_base = int(len(dup_teids_in_base))

    # --- 3. Join to our pipeline output ---------------------------------
    ours = pd.read_csv(BRANCH_TRACKING_CSV, dtype=str)
    ours["teid"] = ours["teid"].astype(str).str.strip()
    dup_teids_in_ours = ours["teid"].duplicated().sum()
    ours_small = ours[
        ["teid", "branch_id", "implied_default_status", "from_bus", "to_bus", "ckt", "DeviceType", "pct_closed"]
    ].drop_duplicates(subset=["teid"], keep="first")

    merged = base.merge(
        ours_small, left_on="resolved_teid", right_on="teid", how="left", suffixes=("", "_ours")
    )

    n_matched_to_table = int(merged["teid"].notna().sum())
    n_no_match_in_table = int(
        (merged["resolved_teid"].notna() & merged["teid"].isna()).sum()
    )

    has_status_pair = merged["implied_default_status"].notna() & (
        merged["implied_default_status"].astype(str).str.strip() != ""
    )
    n_blank_implied = int(merged["teid"].notna().sum() - has_status_pair.sum())

    comparable = merged[has_status_pair].copy()
    comparable["Status"] = comparable["Status"].astype(str).str.strip()
    comparable["implied_default_status"] = comparable["implied_default_status"].astype(str).str.strip()

    agree_mask = comparable["Status"] == comparable["implied_default_status"]
    n_agree = int(agree_mask.sum())
    disagreements = comparable[~agree_mask].copy()
    n_disagree = int(len(disagreements))

    base_closed_ours_open = disagreements[
        (disagreements["Status"] == "Closed") & (disagreements["implied_default_status"] == "Open")
    ]
    base_open_ours_closed = disagreements[
        (disagreements["Status"] == "Open") & (disagreements["implied_default_status"] == "Closed")
    ]
    n_base_closed_ours_open = len(base_closed_ours_open)
    n_base_open_ours_closed = len(base_open_ours_closed)
    n_other_disagree = n_disagree - n_base_closed_ours_open - n_base_open_ours_closed

    # --- 4. Write disagreement CSV --------------------------------------
    out = disagreements.drop(columns=["teid"]).rename(
        columns={
            "resolved_teid": "teid",
            "Status": "base_model_status",
            "From Name": "base_from_name",
            "To Name": "base_to_name",
            "Circuit": "base_circuit",
            "Branch Device Type": "base_device_type",
        }
    )
    out_cols = [
        "teid",
        "branch_id",
        "base_model_status",
        "implied_default_status",
        "pct_closed",
        "base_from_name",
        "base_to_name",
        "base_circuit",
        "base_device_type",
        "from_bus",
        "to_bus",
        "ckt",
        "DeviceType",
        "match_type",
    ]
    out = out[out_cols].sort_values(["teid", "base_from_name"])
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_csv, index=False)

    # --- 5. Print summary -------------------------------------------------
    print(f"=== {base_model_csv.name} parsing ===")
    print(f"Total base-model rows: {total_base_rows}")
    print(f"  Resolved via direct teid label: {n_direct}")
    print(f"  Resolved via rdfid -> TeidMap:   {n_rdfid_mapped}")
    print(f"  Unresolvable (rdfid present but unmapped): {n_rdfid_unmapped}")
    print(f"  Unresolvable (no teid or rdfid label at all): {n_no_label}")
    print(f"  Total unresolvable: {n_unresolved}")
    print(f"  Rows with neither teid nor rdfid classified label: {n_neither}")
    print(f"  Duplicate RdfId values in CIM TeidMap: {dup_rdfid_in_map}")
    if len(unresolved_sample):
        print("  Sample unresolvable rows:")
        print(unresolved_sample.to_string(index=False))

    print()
    print("=== duplicate teids ===")
    print(f"Distinct resolved teid values appearing >1x in base_model: {n_dup_teid_values_base}")
    print(f"  (accounting for {n_dup_teid_rows_base} base_model rows)")
    print(f"Duplicate teid values in branch_tracking_table.csv (ours): {dup_teids_in_ours}")

    print()
    print("=== join to branch_tracking_table.csv ===")
    print(f"Base-model rows resolved to a teid: {total_base_rows - n_unresolved}")
    print(f"  Matched to a row in our table:     {n_matched_to_table}")
    print(f"  Resolved teid but no match in our table: {n_no_match_in_table}")
    print(f"  Matched but implied_default_status blank (skipped): {n_blank_implied}")
    print(f"  Compared (matched + status populated): {len(comparable)}")

    print()
    print("=== status comparison ===")
    print(f"Agreement: {n_agree}")
    print(f"Disagreement: {n_disagree}")
    print(f"  base=Closed / ours=Open: {n_base_closed_ours_open}")
    print(f"  base=Open / ours=Closed: {n_base_open_ours_closed}")
    if n_other_disagree:
        print(f"  other (unexpected status values): {n_other_disagree}")

    print()
    print(f"Output written to: {output_csv}")


if __name__ == "__main__":
    main()
