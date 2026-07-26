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
