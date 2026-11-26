"""Validate SP_RUN_FAST_SCAN_TEST_V2's calculation against V1 production rows.

proc_extraction turns the staged procedure in sp_fast_scan_v2.sql (three TMP_* stages plus the
INSERT INTO FAST_SCAN_RESULTS select) into ONE read-only SELECT, binds the procedure's
variables to literals from FAST_SCAN_CONFIG and the CLI dates, runs it (no CALL, no write),
and diffs the result against V1 rows already in FAST_SCAN_RESULTS for the same config (V1 rows
are on the hour -- MINUTE(TIMESTAMP) = 0 -- V2 rows carry snapshot minutes, typically :57).
Not covered: the guards/date defaulting (replaced by the CLI args) and the FAST_SCAN_RT_CONSTRAINTS
delete+insert (a write; its source stage TMP_BINDING_ROWS is replayed but not compared here).

Usage (from the repo root; read-only role):
    uv run --project /workspaces/scratch-workspace python \\
        fast_scan/station_injection/validate_fast_scan_v2.py \\
        --config-id 254330 --start 2026-06-01 --end 2026-06-14 --skip-par
"""

import argparse
from pathlib import Path

import awconnect
import pandas as pd
from awconnect import snowflake

import proc_extraction as pe

SQL_FILE = Path(__file__).parent / "sp_fast_scan_v2.sql"
OUTPUT_DIR = Path(__file__).parent / "output"

STAGES = ["TMP_STATION_KV_SHIFTS", "TMP_INJECTION_FLOW", "TMP_BINDING_ROWS"]
FINAL_TARGET = "FLOW_ANALYSIS.FAST_SCAN_RESULTS"
CONFIG_BINDS = ["PSENSHIFTID", "FROM_NUM", "TO_NUM", "CKT", "CTG_LABEL", "PTOID", "BRANCH_NAME",
                "DEFAULT_RATE_B", "DEFAULT_RATE_B_RT"]
DIFF_COLUMNS = ["INJECTION_FLOW", "DAM_RATE_B", "REALTIME_RATE_B", "RT_CONSTRAINT_VALUE"]


def q(sql, db="AW"):
    return snowflake.performQuery(db, sql, warehouse=snowflake.READ_ONLY_WH, logInfo=False)


def build_query(config: dict, config_id: int, start: str, end: str, skip_par: bool) -> tuple:
    ex = pe.extract_readonly_query(
        SQL_FILE.read_text(), STAGES, FINAL_TARGET, source=SQL_FILE.name)
    query = ex.query
    if skip_par:
        query = pe.stub_cte(
            query, "ParInjectionFlow",
            "SELECT NULL::TIMESTAMP_NTZ AS HOUR_START, 0.0 AS PAR_FLOW WHERE FALSE",
        )
        query = pe.stub_cte(
            query, "RenewableUnits",
            "SELECT NULL::VARCHAR AS UNIT_CODE, NULL::VARCHAR AS FUEL_TYPE WHERE FALSE",
        )
    values = {
        **ex.declared_defaults,
        "P_CONFIG_ID": config_id, "P_INCLUDE_CURTAILMENT": True, "P_ISO_MARKET_ID": 6,
        "v_actual_start": start, "v_actual_end": end,
        **{f"v_{k.lower()}": config[k] for k in CONFIG_BINDS},
    }
    return pe.bind(query, values), ex


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-id", type=int, required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument(
        "--skip-par",
        action="store_true",
        help="stub ParInjectionFlow to an empty result for this validation run only "
        "(AW.DBO.PARERCOTVIEW is not readable from this role); the committed proc is untouched",
    )
    args = parser.parse_args()

    awconnect.configure("read_only")

    print(f"Loading config row for CONFIG_ID = {args.config_id}")
    config_df = q(f"SELECT * FROM AW.FLOW_ANALYSIS.FAST_SCAN_CONFIG WHERE CONFIG_ID = {args.config_id}")
    if config_df.empty:
        print(f"NEEDS_CONTEXT: no FAST_SCAN_CONFIG row for CONFIG_ID = {args.config_id}")
        return
    config = config_df.iloc[0].to_dict()
    print(config_df.to_string())

    query, ex = build_query(config, args.config_id, args.start, args.end, args.skip_par)
    print(pe.describe_coverage(ex, SQL_FILE.name))
    if args.skip_par:
        print("PAR flow and RenewableUnits stubbed (PARERCOTVIEW / ERCOT_RESOURCE_ADEQUACY_REPORT_VIEW not readable from this role)")

    print("\nRunning extracted V2 SELECT...")
    v2 = q(query)

    print(f"\nV2 row count: {len(v2)}")
    if not v2.empty:
        print(f"V2 TIMESTAMP min/max: {v2['TIMESTAMP'].min()} / {v2['TIMESTAMP'].max()}")
    print("\nV2 first 10 rows:")
    print(v2.head(10).to_string())

    print("\nLoading V1 rows for the same config/range (MINUTE(TIMESTAMP) = 0)...")
    v1 = q(f"""
        SELECT TIMESTAMP, INJECTION_FLOW, DAM_RATE_B, REALTIME_RATE_B, RT_CONSTRAINT_VALUE
        FROM AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS
        WHERE CONFIG_ID = {args.config_id}
          AND MINUTE(TIMESTAMP) = 0
          AND TIMESTAMP >= '{args.start}' AND TIMESTAMP < DATEADD('DAY', 1, '{args.end}'::DATE)
    """)
    print(f"V1 row count: {len(v1)}")

    if v1.empty or v2.empty:
        print("\nCannot diff -- V1 or V2 result set is empty.")
    else:
        v2 = v2.copy()
        v2["HOUR_FLOOR"] = pd.to_datetime(v2["TIMESTAMP"]).dt.floor("h")
        v1 = v1.rename(columns={c: f"{c}_V1" for c in DIFF_COLUMNS})
        merged = v1.merge(v2, left_on="TIMESTAMP", right_on="HOUR_FLOOR", how="inner", suffixes=("", "_V2"))
        print(f"\nJoined V1-to-V2 rows: {len(merged)}")
        for col in DIFF_COLUMNS:
            v1_col, v2_col = f"{col}_V1", col
            diff = (merged[v1_col] - merged[v2_col]).abs()
            null_v1_only = (merged[v1_col].isna() & merged[v2_col].notna()).sum()
            null_v2_only = (merged[v1_col].notna() & merged[v2_col].isna()).sum()
            print(
                f"{col}: mean|diff|={diff.mean():.4f}  max|diff|={diff.max():.4f}  "
                f"NULL-in-V1-only={null_v1_only}  NULL-in-V2-only={null_v2_only}"
            )

        # DAM is keyed to the NEXT hour in V2 (HOUR_BUCKET = snapshot + 30 min, then
        # floored), while V1 stamped the DAM value against the snapshot's own hour H.
        # So also check DAM_RATE_B against V1 joined one hour ahead of the hour-floor join.
        v2["HOUR_PLUS1"] = v2["HOUR_FLOOR"] + pd.Timedelta(hours=1)
        merged_plus1 = v1.merge(v2, left_on="TIMESTAMP", right_on="HOUR_PLUS1", how="inner", suffixes=("", "_V2"))
        print(f"\nJoined V1-to-V2 rows (V1 at hour-floor + 1h): {len(merged_plus1)}")
        diff_plus1 = (merged_plus1["DAM_RATE_B_V1"] - merged_plus1["DAM_RATE_B"]).abs()
        null_v1_only_p1 = (merged_plus1["DAM_RATE_B_V1"].isna() & merged_plus1["DAM_RATE_B"].notna()).sum()
        null_v2_only_p1 = (merged_plus1["DAM_RATE_B_V1"].notna() & merged_plus1["DAM_RATE_B"].isna()).sum()
        print(
            f"DAM_RATE_B (V1 @ H+1): mean|diff|={diff_plus1.mean():.4f}  max|diff|={diff_plus1.max():.4f}  "
            f"NULL-in-V1-only={null_v1_only_p1}  NULL-in-V2-only={null_v2_only_p1}"
        )

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / f"fast_scan_v2_sample_{args.config_id}.csv"
    v2.to_csv(out_path, index=False)
    print(f"\nWrote {len(v2)} V2 rows to {out_path}")


if __name__ == "__main__":
    main()
