"""Validate SP_RUN_VALIDATION_FAST_SCAN_TEST_V2's calculation against the deployed V1
validation proc's rows already sitting in FAST_SCAN_RESULTS for the same config.

proc_extraction turns the staged procedure in validation_spV2.sql (TMP_VAL_MEMBER_HOURS, three
TMP_* stages, then the INSERT INTO FAST_SCAN_RESULTS select) into ONE read-only SELECT: the
member-hours INSERT plus its two DELETEs (RN > 1, date range) become a CTE chain, the other
variables are bound to FAST_SCAN_CONFIG values and the CLI dates, and the two legs this role
can't read (PARERCOTVIEW, ERCOT_RESOURCE_ADEQUACY_REPORT_VIEW) are stubbed to empty. No CALL,
no write, no NOT EXISTS filter.
Not covered: NOT_A_VALIDATION_CONFIG / NO_MEMBERS guards, date defaulting (CLI args replace it),
the already_present / hours_missing counters, and the FAST_SCAN_RT_CONSTRAINTS delete+insert
(a write). The RT-constraints content is checked via sp_load_fast_scan_rt_constraints.sql's
SELECT (same structural extraction) instead.

V1 is on the FLOOR convention (a :57 snapshot lands on floor-hour TIMESTAMP, and pulls the
DAM hour ONE AHEAD of that floor); V2 is nearest-hour (the same :57 snapshot rounds its
HOUR_BUCKET up to that same next hour). So two alignments are reported:
  (a) same-bucket: V2.HOUR_BUCKET == V1.TIMESTAMP  -> DAM_RATE_B and PSENSHIFTID compare
  (b) flow alignment: floor(V2.TIMESTAMP) == V1.TIMESTAMP (12:57 <-> 12:00) -> INJECTION_FLOW,
      REALTIME_RATE_B compare

Then re-runs the RT-constraints SELECT with its Snapshots CTE inlined from the V2 dry-run's own
TIMESTAMP values (those rows were never written to FAST_SCAN_RESULTS), and checks that every V2
snapshot with a non-null RT_CONSTRAINT_VALUE has exactly one IS_CONFIG_CTG = TRUE row there with
the same value.

Usage (from the repo root; read-only role):
    uv run --project /workspaces/scratch-workspace python \\
        fast_scan/station_injection/validate_validation_fast_scan_v2.py \\
        --config-id 256315 --start 2026-06-02 --end 2026-06-08
"""

import argparse
from pathlib import Path

import awconnect
import pandas as pd
from awconnect import snowflake

import proc_extraction as pe

VALIDATION_SQL_FILE = Path(__file__).parent / "validation_spV2.sql"
RT_CONSTRAINTS_SQL_FILE = Path(__file__).parent / "sp_load_fast_scan_rt_constraints.sql"
OUTPUT_DIR = Path(__file__).parent / "output"


def q(sql, db="AW"):
    return snowflake.performQuery(db, sql, warehouse=snowflake.READ_ONLY_WH, logInfo=False)


STAGES = ["TMP_VAL_MEMBER_HOURS", "TMP_STATION_KV_SHIFTS", "TMP_INJECTION_FLOW", "TMP_BINDING_ROWS"]
FINAL_TARGET = "FLOW_ANALYSIS.FAST_SCAN_RESULTS"
RT_FINAL_TARGET = "FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS"
CONFIG_BINDS = {
    "v_study_id": "STUDY_ID", "v_tssid": "TOPOLOGYSHIFTSETID", "v_from_num": "FROM_NUM",
    "v_to_num": "TO_NUM", "v_ckt": "CKT", "v_ctg_label": "CTG_LABEL", "v_ptoid": "PTOID",
    "v_branch_name": "BRANCH_NAME", "v_default_rate_b": "DEFAULT_RATE_B",
    "v_default_rate_b_rt": "DEFAULT_RATE_B_RT",
}


def build_v2_query(config: dict, config_id: int, start: str, end: str) -> tuple:
    ex = pe.extract_readonly_query(
        VALIDATION_SQL_FILE.read_text(), STAGES, FINAL_TARGET, source=VALIDATION_SQL_FILE.name)
    query = pe.stub_cte(
        ex.query, "ParInjectionFlow",
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
        **{k: config[col] for k, col in CONFIG_BINDS.items()},
    }
    return pe.bind(query, values), ex


def build_rt_constraints_query(config: dict, config_id: int, start: str, end: str, snapshot_timestamps) -> str:
    ex = pe.extract_readonly_query(
        RT_CONSTRAINTS_SQL_FILE.read_text(), [], RT_FINAL_TARGET, source=RT_CONSTRAINTS_SQL_FILE.name)
    ts_values = ",\n        ".join(f"('{ts}'::TIMESTAMP_NTZ)" for ts in snapshot_timestamps)
    query = pe.stub_cte(ex.query, "Snapshots", f"SELECT COLUMN1 AS TIMESTAMP FROM VALUES\n        {ts_values}")
    values = {
        "P_ISO_MARKET_ID": 6, "P_CONFIG_ID": config_id,
        "P_START_DATE": start, "P_END_DATE": end,
        **{k: config[col] for k, col in CONFIG_BINDS.items()},
    }
    return pe.bind(query, values)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-id", type=int, required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    args = parser.parse_args()

    awconnect.configure("read_only")

    print(f"Loading config row for CONFIG_ID = {args.config_id}")
    config_df = q(f"SELECT * FROM AW.FLOW_ANALYSIS.FAST_SCAN_CONFIG WHERE CONFIG_ID = {args.config_id}")
    if config_df.empty:
        print(f"NEEDS_CONTEXT: no FAST_SCAN_CONFIG row for CONFIG_ID = {args.config_id}")
        return
    config = config_df.iloc[0].to_dict()
    print(config_df.to_string())

    print("\nCounting member hours in range (TOPOLOGYSHIFTSET x PSENSHIFTDEF x OPFRUN)...")
    mh = q(f"""
        SELECT COUNT(*) AS N FROM (
            SELECT TS, ROW_NUMBER() OVER (PARTITION BY TS ORDER BY RUNID DESC NULLS LAST, PSENSHIFTID DESC) AS RN
            FROM (
                SELECT DISTINCT tss.PSENSHIFTID, tss.TOPOLOGYID, psd.RUNID,
                       DATEADD(hour, r.SIMHOUR - 1, r.SIMDATE::DATE) AS TS
                FROM AW.POPT.TOPOLOGYSHIFTSET tss
                LEFT JOIN AW.DBO.PSENSHIFTDEF psd ON psd.PSENSHIFTID = tss.PSENSHIFTID
                JOIN (
                    SELECT DISTINCT STUDYID, TOPOLOGYID, SIMDATE, SIMHOUR
                    FROM AWOPF.DBO.OPFRUN
                    WHERE STUDYID = {config['STUDY_ID']} AND SIMDATE IS NOT NULL AND SIMHOUR IS NOT NULL
                ) r ON r.TOPOLOGYID = tss.TOPOLOGYID
                WHERE tss.TOPOLOGYSHIFTSETID = {config['TOPOLOGYSHIFTSETID']}
            )
        ) WHERE RN = 1 AND TS::DATE BETWEEN '{args.start}' AND '{args.end}'
    """)
    member_hours_in_range = int(mh.iloc[0]["N"])
    print(f"Member hours in range: {member_hours_in_range}")

    v2_query, ex = build_v2_query(config, args.config_id, args.start, args.end)
    print(pe.describe_coverage(ex, VALIDATION_SQL_FILE.name))

    print("\nRunning extracted validation-V2 SELECT...")
    v2 = q(v2_query)
    print(f"V2 row count (snapshots): {len(v2)}")
    if not v2.empty:
        print(f"V2 TIMESTAMP min/max: {v2['TIMESTAMP'].min()} / {v2['TIMESTAMP'].max()}")
    print("\nV2 first 10 rows:")
    print(v2.head(10).to_string())

    print("\nLoading V1 rows for the same config/range...")
    v1 = q(f"""
        SELECT TIMESTAMP, PSENSHIFTID, INJECTION_FLOW, DAM_RATE_B, REALTIME_RATE_B, RT_CONSTRAINT_VALUE
        FROM AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS
        WHERE CONFIG_ID = {args.config_id}
          AND TIMESTAMP >= '{args.start}' AND TIMESTAMP < DATEADD('DAY', 1, '{args.end}'::DATE)
    """)
    print(f"V1 row count: {len(v1)}")

    v2 = v2.copy()
    v2["TIMESTAMP"] = pd.to_datetime(v2["TIMESTAMP"])
    v2["HOUR_FLOOR"] = v2["TIMESTAMP"].dt.floor("h")
    v2["HOUR_BUCKET"] = (v2["TIMESTAMP"] + pd.Timedelta(minutes=30)).dt.floor("h")

    if v1.empty or v2.empty:
        print("\nCannot diff -- V1 or V2 result set is empty.")
    else:
        v1 = v1.copy()
        v1["TIMESTAMP"] = pd.to_datetime(v1["TIMESTAMP"])

        # (a) same-bucket: V2.HOUR_BUCKET == V1.TIMESTAMP
        same_bucket = v1.merge(
            v2, left_on="TIMESTAMP", right_on="HOUR_BUCKET", how="inner", suffixes=("_V1", "_V2"),
        )
        print(f"\n(a) same-bucket join (V2.HOUR_BUCKET == V1.TIMESTAMP): {len(same_bucket)} rows")
        if not same_bucket.empty:
            dam_diff = (same_bucket["DAM_RATE_B_V1"] - same_bucket["DAM_RATE_B_V2"]).abs()
            print(f"    DAM_RATE_B: mean|diff|={dam_diff.mean():.4f}  max|diff|={dam_diff.max():.4f}")
            psens_match = (same_bucket["PSENSHIFTID_V1"] == same_bucket["PSENSHIFTID_V2"])
            print(f"    PSENSHIFTID match rate: {psens_match.mean() * 100:.1f}% ({psens_match.sum()}/{len(psens_match)})")

        # (b) flow alignment: floor(V2.TIMESTAMP) == V1.TIMESTAMP
        flow_align = v1.merge(
            v2, left_on="TIMESTAMP", right_on="HOUR_FLOOR", how="inner", suffixes=("_V1", "_V2"),
        )
        print(f"\n(b) flow-alignment join (floor(V2.TIMESTAMP) == V1.TIMESTAMP): {len(flow_align)} rows")
        if not flow_align.empty:
            flow_diff = (flow_align["INJECTION_FLOW_V1"] - flow_align["INJECTION_FLOW_V2"]).abs()
            rt_diff = (flow_align["REALTIME_RATE_B_V1"] - flow_align["REALTIME_RATE_B_V2"]).abs()
            print(f"    INJECTION_FLOW: mean|diff|={flow_diff.mean():.4f}  std={flow_diff.std():.4f}  "
                  f"min={flow_diff.min():.4f}  max={flow_diff.max():.4f}  (near-constant offset check)")
            print(f"    REALTIME_RATE_B: mean|diff|={rt_diff.mean():.4f}  max|diff|={rt_diff.max():.4f}")

        v1_nonnull = v1["RT_CONSTRAINT_VALUE"].notna().sum()
        v2_nonnull = v2["RT_CONSTRAINT_VALUE"].notna().sum()
        print(f"\nRT_CONSTRAINT_VALUE non-null: V1={v1_nonnull}/{len(v1)}  V2={v2_nonnull}/{len(v2)} "
              f"(V1 averages every contingency; V2 keeps only the config's own contingency, so fewer is expected)")

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / f"validation_fast_scan_v2_sample_{args.config_id}.csv"
    v2.to_csv(out_path, index=False)
    print(f"\nWrote {len(v2)} V2 rows to {out_path}")

    # --- Sub-proc: SP_LOAD_FAST_SCAN_RT_CONSTRAINTS, Snapshots inlined from the V2 dry run ---
    print("\n\nRunning SP_LOAD_FAST_SCAN_RT_CONSTRAINTS's SELECT with Snapshots inlined from V2 timestamps...")
    snapshot_timestamps = sorted(v2["TIMESTAMP"].dt.strftime("%Y-%m-%d %H:%M:%S").unique())
    rt_query = build_rt_constraints_query(config, args.config_id, args.start, args.end, snapshot_timestamps)
    rt = q(rt_query)
    # The proc's SELECT list relies on INSERT INTO's column list for names (several
    # expressions are unaliased); restore them here since we're running it standalone.
    rt.columns = [
        "CONFIG_ID", "TIMESTAMP", "RT_INTERVAL", "CONTINGENCY", "IS_CONFIG_CTG",
        "CONSTRAINT_NAME", "RT_CONSTRAINT_VALUE", "RT_CONSTRAINT_LIMIT", "RT_ACTUAL_HEADROOM",
    ]
    print(f"Sub-proc rows: {len(rt)}")
    if not rt.empty:
        print(f"Distinct contingencies: {rt['CONTINGENCY'].nunique()}")
        print(rt['CONTINGENCY'].value_counts().to_string())

    # Every V2 snapshot with a non-null RT_CONSTRAINT_VALUE should have exactly one
    # IS_CONFIG_CTG = TRUE row in the sub-proc output with the same value.
    v2_nonnull_rows = v2[v2["RT_CONSTRAINT_VALUE"].notna()][["TIMESTAMP", "RT_CONSTRAINT_VALUE"]].copy()
    rt_config_ctg = rt[rt["IS_CONFIG_CTG"] == True][["TIMESTAMP", "RT_CONSTRAINT_VALUE"]].copy() if not rt.empty else rt
    if not rt.empty:
        rt_config_ctg["TIMESTAMP"] = pd.to_datetime(rt_config_ctg["TIMESTAMP"])
    check = v2_nonnull_rows.merge(
        rt_config_ctg, on="TIMESTAMP", how="left", suffixes=("_V2", "_RT"),
    ) if not rt.empty else v2_nonnull_rows.assign(RT_CONSTRAINT_VALUE_RT=pd.NA)
    n_expected = len(v2_nonnull_rows)
    counts = rt_config_ctg.groupby("TIMESTAMP").size() if not rt.empty and not rt_config_ctg.empty else pd.Series(dtype=int)
    exactly_one = v2_nonnull_rows["TIMESTAMP"].map(lambda t: counts.get(t, 0) == 1).sum() if len(counts) else 0
    value_match = 0
    if not rt.empty:
        merged_check = v2_nonnull_rows.merge(rt_config_ctg, on="TIMESTAMP", suffixes=("_V2", "_RT"))
        value_match = (merged_check["RT_CONSTRAINT_VALUE_V2"].round(2) == merged_check["RT_CONSTRAINT_VALUE_RT"].round(2)).sum()
    print(f"\nV2 snapshots with non-null RT_CONSTRAINT_VALUE: {n_expected}")
    print(f"  ... with exactly one IS_CONFIG_CTG=TRUE row in sub-proc output: {exactly_one}/{n_expected}")
    print(f"  ... where that row's value matches V2's RT_CONSTRAINT_VALUE: {value_match}/{n_expected}")


if __name__ == "__main__":
    main()
