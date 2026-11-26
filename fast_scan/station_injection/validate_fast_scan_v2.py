"""Validate SP_RUN_FAST_SCAN_TEST_V2's main SELECT against V1 production rows.

Extracts the WITH...final-SELECT body straight out of sp_fast_scan_v2.sql (so the two
files stay in sync by construction), substitutes the procedure's binds with literals
pulled from FAST_SCAN_CONFIG, runs it as a plain SELECT (no CALL, no INSERT), and
diffs the result against V1 rows already sitting in FAST_SCAN_RESULTS for the same
config (V1 rows are on the hour -- MINUTE(TIMESTAMP) = 0 -- V2 rows carry snapshot
minutes, typically :57).

Usage:
    /workspaces/scratch-workspace/.venv/bin/python validate_fast_scan_v2.py \
        --config-id 1 --start 2024-06-01 --end 2024-06-07
"""

import argparse
import re
from pathlib import Path

import awconnect
import pandas as pd
from awconnect import snowflake

SQL_FILE = Path(__file__).parent / "sp_fast_scan_v2.sql"
OUTPUT_DIR = Path(__file__).parent / "output"

DIFF_COLUMNS = ["INJECTION_FLOW", "DAM_RATE_B", "REALTIME_RATE_B", "RT_CONSTRAINT_VALUE"]


def q(sql, db="AW"):
    return snowflake.performQuery(db, sql, warehouse=snowflake.READ_ONLY_WH, logInfo=False)


def extract_main_query(sql_text: str) -> str:
    marker = "-- 4. THE MAIN CALCULATION"
    marker_idx = sql_text.index(marker)
    with_match = re.search(r"\bWITH\b", sql_text[marker_idx:])
    if with_match is None:
        raise ValueError("could not find WITH after the '-- 4. THE MAIN CALCULATION' marker")
    with_idx = marker_idx + with_match.start()
    end_idx = sql_text.index("WHERE NOT EXISTS", with_idx)
    query = sql_text[with_idx:end_idx]
    query = query.replace("''", "'")
    return query.strip()


def sql_literal(val):
    if pd.isna(val):
        return "NULL"
    if isinstance(val, str):
        return "'" + val.replace("'", "''") + "'"
    return str(val)


def stub_cte(query: str, cte_name: str, stub_select: str) -> str:
    """Replace a named CTE's body with `stub_select` (validation-run only workaround for
    a source table this role can't read), keeping the CTE name and paren wrapper intact
    so downstream joins still compile. `stub_select` must project the same output columns
    the real CTE body did."""
    marker = f"{cte_name} AS ("
    start = query.index(marker)
    open_paren_idx = start + len(marker) - 1
    depth = 0
    i = open_paren_idx
    while True:
        if query[i] == "(":
            depth += 1
        elif query[i] == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    end_paren_idx = i
    return query[: open_paren_idx + 1] + f"\n        {stub_select}\n    " + query[end_paren_idx:]


def substitute_binds(query: str, config: dict, config_id: int, start: str, end: str) -> str:
    # Longest/most-specific names first so e.g. v_default_rate_b_rt isn't clobbered by
    # a v_default_rate_b substitution.
    subs = [
        ("P_INCLUDE_CURTAILMENT", "TRUE"),
        ("P_ISO_MARKET_ID", "6"),
        ("P_CONFIG_ID", str(config_id)),
        ("v_default_rate_b_rt", sql_literal(config["DEFAULT_RATE_B_RT"])),
        ("v_default_rate_b", sql_literal(config["DEFAULT_RATE_B"])),
        ("v_actual_start", f"'{start}'"),
        ("v_actual_end", f"'{end}'"),
        ("v_branch_name", sql_literal(config["BRANCH_NAME"])),
        ("v_psenshiftid", sql_literal(config["PSENSHIFTID"])),
        ("v_from_num", sql_literal(config["FROM_NUM"])),
        ("v_to_num", sql_literal(config["TO_NUM"])),
        ("v_ckt", sql_literal(config["CKT"])),
        ("v_ctg_label", sql_literal(config["CTG_LABEL"])),
        ("v_ptoid", sql_literal(config["PTOID"])),
        ("v_cim_file_id", "205"),
    ]
    for name, value in subs:
        query = re.sub(r":" + name + r"\b", value, query, flags=re.IGNORECASE)
    return query


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

    sql_text = SQL_FILE.read_text()
    query = extract_main_query(sql_text)
    if args.skip_par:
        query = stub_cte(
            query, "ParInjectionFlow",
            "SELECT NULL::TIMESTAMP_NTZ AS HOUR_START, 0.0 AS PAR_FLOW WHERE FALSE",
        )
        print("PAR flow stubbed to 0 (PARERCOTVIEW not readable from this role)")
        # AW.DBO.ERCOT_RESOURCE_ADEQUACY_REPORT_VIEW (RenewableUnits) is likewise
        # unauthorized for this role -- same class of gap as PARERCOTVIEW, discovered
        # while running this same validation. Stubbed under the same flag rather than
        # adding a second one for an identical situation.
        query = stub_cte(
            query, "RenewableUnits",
            "SELECT NULL::VARCHAR AS UNIT_CODE, NULL::VARCHAR AS FUEL_TYPE WHERE FALSE",
        )
        print("RenewableUnits stubbed to empty (ERCOT_RESOURCE_ADEQUACY_REPORT_VIEW not readable from this role)")
    query = substitute_binds(query, config, args.config_id, args.start, args.end)

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
