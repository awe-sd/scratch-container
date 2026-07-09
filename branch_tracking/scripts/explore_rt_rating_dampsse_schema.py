"""
Read-only schema/data exploration for two NEW candidate sources for inferring
branch in-service status (no inference logic here -- just discovery):

  (A) ercotRtDynamicRating*  -- ERCOT real-time dynamic rating publications.
      Exact table set unknown up front; discovered via INFORMATION_SCHEMA.

  (B) ercotDampsseDef        -- ERCOT DAM PSSE model publications, per-DA-hour
                                model definitions with branch status (bus
                                numbers obfuscated, bus NAMES are station
                                names; has r/x/b impedances, branch name,
                                station ids).
      ercotDampsseLnView     -- detailed hourly line data (view).

Companion to explore_outage_schema.py / explore_branch_sqlserver.py -- same
investigation style (awconnect read_only, SQL Server via db.getDfFromAwDb).
Never inserts, never creates tables. Every query is either TOP-N bounded or
has a tight WHERE filter -- this database can take 3-5 min even on filtered
queries, and unfiltered GROUP BY/COUNT on big tables can hang indefinitely,
so every query also runs in a daemon thread with a hard wall-clock timeout;
if it doesn't come back in time we print a TIMED OUT marker and move on
instead of blocking the rest of the script.
"""
import re
import threading
import time

import awconnect
import pandas as pd
from awconnect import db

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 240)
pd.set_option("display.max_colwidth", 80)
pd.set_option("display.max_rows", 200)

QUERY_TIMEOUT_SEC = 480  # ~8 minutes, per repo guidance

TABLE_NAME_FILTER = "(TABLE_NAME LIKE 'ercotRtDynamicRating%' OR TABLE_NAME LIKE 'ercotDampsse%')"

# Regex classifiers for candidate linkable-identifier / time / status / r-x-b columns.
ID_PATTERNS = {
    "rdfid/uuid-like": re.compile(r"rdf|guid|uuid", re.I),
    "teid-like": re.compile(r"teid", re.I),
    "name-like": re.compile(r"name", re.I),
    "station-like": re.compile(r"station|substation", re.I),
    "branch/equip-like": re.compile(r"branch|circuit|element|equip|\bline\b", re.I),
}
TIME_PATTERN = re.compile(r"date|hour|time|interval|session|publish|effective|snapshot|asof|as_of", re.I)
# Business-key time columns (the actual DA-hour / rating-hour the row applies to) vs
# audit/bookkeeping timestamps (when the row was inserted/loaded/published). We want the
# former when picking a single column to drive the "one hourly snapshot" query in step 5.
TIME_BUSINESS_PATTERN = re.compile(r"hour|session|interval|effective", re.I)
TIME_AUDIT_PATTERN = re.compile(r"insert|publish|load|update|create", re.I)
STATUS_PATTERN = re.compile(r"status|state|inservice|in_service|energ|open|closed", re.I)
RXB_PATTERN = re.compile(r"^(r|x|b|r0|x0|b0|r1|x1|b1)$|react|resist|suscept|imped|rating", re.I)

DATE_TYPES = {"date", "datetime", "datetime2", "smalldatetime", "time", "datetimeoffset"}
NUMERIC_TYPES = {"int", "bigint", "smallint", "tinyint", "decimal", "numeric", "float", "real"}


def run_query(sql, label, timeout=QUERY_TIMEOUT_SEC):
    """Run a query in a daemon thread with a hard timeout so one hang doesn't
    block the rest of the script. Returns the DataFrame, or None on timeout/error."""
    print(f"\n--- query: {label} ---")
    print(sql.strip())
    result = {}

    def target():
        try:
            result["df"] = db.getDfFromAwDb(sql)
        except Exception as e:  # noqa: BLE001
            result["error"] = e

    t = threading.Thread(target=target, daemon=True)
    start = time.time()
    t.start()
    t.join(timeout)
    elapsed = time.time() - start

    if t.is_alive():
        print(f"*** TIMED OUT after {elapsed:.1f}s (limit {timeout}s) -- SKIPPING, moving on ***")
        return None
    if "error" in result:
        print(f"*** ERROR after {elapsed:.1f}s: {result['error']!r} ***")
        return None
    df = result["df"]
    print(f"[{elapsed:.1f}s, {len(df)} rows]")
    return df


def classify_columns(cols):
    """cols: list of column-name strings. Returns dict[label] -> [matching col names]."""
    found = {}
    for label, pat in ID_PATTERNS.items():
        hits = [c for c in cols if pat.search(c)]
        if hits:
            found[label] = hits
    time_hits = [c for c in cols if TIME_PATTERN.search(c)]
    if time_hits:
        found["time/hour-like"] = time_hits
    status_hits = [c for c in cols if STATUS_PATTERN.search(c)]
    if status_hits:
        found["status-like"] = status_hits
    rxb_hits = [c for c in cols if RXB_PATTERN.search(c)]
    if rxb_hits:
        found["r/x/b/rating-like"] = rxb_hits
    return found


def recency_check(full_table, time_col, dtype):
    """Tight-WHERE MAX() recency check against a recent cutoff, type-aware."""
    dtype_l = (dtype or "").lower()
    if dtype_l in DATE_TYPES:
        cutoff = "'2026-06-01'"
    elif dtype_l in NUMERIC_TYPES:
        cutoff = "20260601"  # works if the int encodes YYYYMMDD; harmless (0 rows) otherwise
    else:
        cutoff = "'2026-06-01'"  # varchar/char date-formatted string, best-effort

    sql = f"SELECT MAX({time_col}) AS max_val, MIN({time_col}) AS min_val_in_window FROM {full_table} WHERE {time_col} >= {cutoff}"
    df = run_query(sql, f"{full_table}: recency check on {time_col} ({dtype})")
    if df is not None:
        print(df.to_string(index=False))
    return df


def dump_recent_hour_snapshot(full_table, time_col, dtype, max_val):
    """Given a MAX(time_col) value already found, pull a bounded sample of
    rows in that same day -- i.e. one (or a few adjacent) hourly/DA-hour
    snapshot(s). Uses a day-range filter rather than exact equality: if
    time_col is a full datetime/datetime2, a stringified pandas Timestamp
    compared with '=' can lose sub-second precision and match zero rows,
    whereas a day-range with CAST(... AS date) is robust to that."""
    if max_val is None:
        print(f"(skipping snapshot dump for {full_table} -- no max_val found)")
        return
    dtype_l = (dtype or "").lower()
    if dtype_l in NUMERIC_TYPES:
        # Numeric time keys (e.g. YYYYMMDD or an hour-index int) -- exact equality is fine,
        # there's no sub-second-precision issue for an integer.
        where_clause = f"{time_col} = {max_val}"
    elif dtype_l in DATE_TYPES:
        day_str = str(max_val)[:10]  # 'YYYY-MM-DD' prefix regardless of full timestamp precision
        where_clause = f"CAST({time_col} AS date) = '{day_str}'"
    else:
        # varchar/char -- treat as an opaque string key, exact match.
        where_clause = f"{time_col} = '{max_val}'"

    sql = f"SELECT TOP 100 * FROM {full_table} WHERE {where_clause}"
    df = run_query(sql, f"{full_table}: single-hour(ish) snapshot WHERE {where_clause}")
    if df is not None and len(df):
        try:
            uniq = sorted(df[time_col].dropna().astype(str).unique().tolist())[:10]
            print(f"(distinct {time_col} values in this {len(df)}-row sample: {uniq})")
        except Exception as e:  # noqa: BLE001 -- best-effort diagnostic, never fatal
            print(f"(could not summarize distinct {time_col} values: {e!r})")
        print(df.to_string(index=False))
        if len(df) < 5:
            print(f"*** NOTE: only {len(df)} row(s) returned -- a real DAM PSSE snapshot is expected to be "
                  f"one row per branch (hundreds/thousands). This small a count likely means {time_col} is "
                  f"the wrong column (audit timestamp, not the DA-hour business key) or a precision mismatch. ***")
    elif df is not None:
        print(f"*** 0 rows returned for {where_clause} -- {time_col} is likely the wrong column for this table. ***")


def followup():
    """Targeted follow-up after the first full run (`--followup`). The first run
    established that awDateID is a day-serial int (42171 <-> 2015-06-17,
    44926 <-> 2023-01-01), NOT YYYYMMDD, so the generic recency probe (cutoff
    20260601) matched nothing and the LnView 'recent snapshot' fell back to
    2015-era rows. This mode pins down:
      - MAX(awDateID) on ercotDampsseTimeseries (the Ln/Xf hourly base table)
      - one recent DA hour from ercotDampsseLnView including inService values
      - the inService True/False distribution for that hour (per file type)
      - recent-hour rows + publication cadence for ercotRtDynamicRating(View)
    2026-07-10 ~= day-serial 46212 given 44926 <-> 2023-01-01, so >= 46100 is a
    tight filter (~3.5 months back)."""
    awconnect.configure("read_only")

    print("=== F1. MAX(awDateID) on ercotDampsseTimeseries (tight awDateID >= 46100 filter) ===")
    df = run_query(
        "SELECT MAX(awDateID) AS max_awdateid FROM dbo.ercotDampsseTimeseries WHERE awDateID >= 46100",
        "ercotDampsseTimeseries max awDateID",
    )
    if df is None or df.empty or pd.isna(df.iloc[0]["max_awdateid"]):
        print("*** could not establish MAX(awDateID); aborting follow-up ***")
        return
    max_awdateid = int(df.iloc[0]["max_awdateid"])
    print(df.to_string(index=False))

    print("\n=== F2. ercotDampsseLnView: 30 rows for the latest awDateID, HE=10 (one DA-hour snapshot) ===")
    df = run_query(
        f"SELECT TOP 30 * FROM dbo.ercotDampsseLnView WHERE awDateID = {max_awdateid} AND HE = 10",
        "LnView single recent DA hour",
    )
    if df is not None:
        print(df.to_string(index=False))

    print("\n=== F3. inService distribution for that hour (base table, by file type) ===")
    df = run_query(
        f"""
        SELECT ercotDampsseFileTypeId, inService, COUNT(*) AS n
        FROM dbo.ercotDampsseTimeseries
        WHERE awDateID = {max_awdateid} AND HE = 10
        GROUP BY ercotDampsseFileTypeId, inService
        ORDER BY ercotDampsseFileTypeId, inService
        """,
        "inService distribution, one hour",
    )
    if df is not None:
        print(df.to_string(index=False))

    print("\n=== F4. LnView: a few inService = 0 rows for that hour (what an out-of-service branch looks like) ===")
    df = run_query(
        f"SELECT TOP 10 * FROM dbo.ercotDampsseLnView WHERE awDateID = {max_awdateid} AND HE = 10 AND inService = 0",
        "LnView out-of-service rows",
    )
    if df is not None:
        print(df.to_string(index=False))

    print("\n=== F5. ercotRtDynamicRatingView: recent rows (createTime >= '2026-07-09'), TOP 10 ===")
    df = run_query(
        "SELECT TOP 10 * FROM dbo.ercotRtDynamicRatingView WHERE createTime >= '2026-07-09'",
        "RtDynamicRatingView recent rows",
    )
    if df is not None:
        print(df.to_string(index=False))

    print("\n=== F6. ercotRtDynamicRating: rows per createTime, 2 hours of one recent day (publication cadence) ===")
    df = run_query(
        """
        SELECT createTime, COUNT(*) AS n
        FROM dbo.ercotRtDynamicRating
        WHERE createTime >= '2026-07-08' AND createTime < '2026-07-08 02:00'
        GROUP BY createTime ORDER BY createTime
        """,
        "RtDynamicRating cadence sample",
    )
    if df is not None:
        print(df.to_string(index=False))

    print("\n=== FOLLOW-UP DONE ===")


def main():
    awconnect.configure("read_only")

    print("=== 1. TABLES + VIEWS matching ercotRtDynamicRating% / ercotDampsse% ===")
    tables_df = run_query(
        f"""
        SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES
        WHERE {TABLE_NAME_FILTER}
        ORDER BY TABLE_NAME
        """,
        "INFORMATION_SCHEMA.TABLES filtered list",
    )
    if tables_df is not None:
        print(tables_df.to_string(index=False))

    print("\n=== 1b. Cross-check against INFORMATION_SCHEMA.VIEWS (should include LnView) ===")
    views_df = run_query(
        f"""
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.VIEWS
        WHERE {TABLE_NAME_FILTER}
        ORDER BY TABLE_NAME
        """,
        "INFORMATION_SCHEMA.VIEWS filtered list",
    )
    if views_df is not None:
        print(views_df.to_string(index=False))

    if tables_df is None or tables_df.empty:
        print("\n*** No tables found via INFORMATION_SCHEMA.TABLES -- aborting further steps. ***")
        return

    table_names = tables_df["TABLE_NAME"].tolist()
    schemas = dict(zip(tables_df["TABLE_NAME"], tables_df["TABLE_SCHEMA"]))

    print("\n=== 2. Full column schema for every matching table/view (single combined query) ===")
    cols_df = run_query(
        f"""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH,
               IS_NULLABLE, NUMERIC_PRECISION, NUMERIC_SCALE, ORDINAL_POSITION
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE {TABLE_NAME_FILTER}
        ORDER BY TABLE_NAME, ORDINAL_POSITION
        """,
        "INFORMATION_SCHEMA.COLUMNS combined for all matching tables",
    )
    if cols_df is None:
        print("*** Could not fetch column metadata -- aborting further steps. ***")
        return
    print(f"(covers {cols_df['TABLE_NAME'].nunique()} tables, {len(cols_df)} columns total)")

    per_table_cols = {}
    per_table_dtype = {}
    for tname, grp in cols_df.groupby("TABLE_NAME", sort=False):
        per_table_cols[tname] = grp["COLUMN_NAME"].tolist()
        per_table_dtype[tname] = dict(zip(grp["COLUMN_NAME"], grp["DATA_TYPE"]))

    # === 3. Per-table: full schema printout, TOP 5 sample, candidate-identifier classification ===
    print("\n=== 3. Per-table schema dump + TOP 5 sample + candidate identifier/time/status columns ===")
    candidates = {}
    for tname in table_names:
        schema = schemas.get(tname, "dbo")
        full_table = f"{schema}.{tname}"
        print(f"\n{'=' * 20} TABLE: {full_table} {'=' * 20}")

        grp = cols_df[cols_df["TABLE_NAME"] == tname]
        print(f"--- {full_table} SCHEMA ({len(grp)} columns) ---")
        print(
            grp[
                [
                    "COLUMN_NAME",
                    "DATA_TYPE",
                    "CHARACTER_MAXIMUM_LENGTH",
                    "IS_NULLABLE",
                    "NUMERIC_PRECISION",
                    "NUMERIC_SCALE",
                ]
            ].to_string(index=False)
        )

        found = classify_columns(per_table_cols[tname])
        candidates[tname] = found
        print(f"--- {full_table} candidate columns (by name pattern) ---")
        if found:
            for label, hits in found.items():
                print(f"  {label}: {hits}")
        else:
            print("  (no obvious matches)")

        sample_df = run_query(f"SELECT TOP 5 * FROM {full_table}", f"{full_table} TOP 5 sample")
        if sample_df is not None:
            print(f"--- {full_table} TOP 5 SAMPLE ---")
            print(sample_df.to_string(index=False))

    # === 4. Recency check for every table that has a time/hour-like column ===
    print("\n=== 4. Recency checks (MAX() with tight WHERE >= 2026-06-01 cutoff, type-aware) ===")
    recent_max = {}
    for tname in table_names:
        schema = schemas.get(tname, "dbo")
        full_table = f"{schema}.{tname}"
        time_cols = candidates.get(tname, {}).get("time/hour-like", [])
        if not time_cols:
            print(f"\n({full_table}: no time/hour-like column detected by name pattern -- skipping recency check)")
            continue
        # Prefer a business-key time column (HourEnding, DASessionDate, EffectiveDate --
        # the actual hour/day the row's data applies to) over an audit/bookkeeping
        # timestamp (insertDate, publishDate, loadDate) when both are present, since the
        # business-key column is what step 5 needs to pull a coherent single-hour snapshot.
        business = [c for c in time_cols if TIME_BUSINESS_PATTERN.search(c) and not TIME_AUDIT_PATTERN.search(c)]
        tcol = business[0] if business else time_cols[0]
        if business and len(time_cols) > 1:
            print(f"({full_table}: {len(time_cols)} time-like columns {time_cols}; picked business-key '{tcol}')")
        dtype = per_table_dtype[tname].get(tcol)
        df = recency_check(full_table, tcol, dtype)
        if df is not None and len(df) and pd.notna(df.iloc[0]["max_val"]):
            recent_max[tname] = (tcol, dtype, df.iloc[0]["max_val"])

    # === 5. Single recent DA-hour snapshot for ercotDampsseDef and ercotDampsseLnView specifically ===
    print("\n=== 5. Single recent DA-hour snapshot: ercotDampsseDef / ercotDampsseLnView ===")
    for tname in table_names:
        if "dampsse" not in tname.lower():
            continue
        if "def" not in tname.lower() and "lnview" not in tname.lower():
            continue
        schema = schemas.get(tname, "dbo")
        full_table = f"{schema}.{tname}"
        if tname not in recent_max:
            print(f"\n({full_table}: no recency max_val established in step 4 -- cannot pull a targeted single-hour snapshot; "
                  f"falling back to a plain TOP 20 * as a stand-in)")
            df = run_query(f"SELECT TOP 20 * FROM {full_table}", f"{full_table} fallback TOP 20 sample")
            if df is not None:
                print(df.to_string(index=False))
            continue
        tcol, dtype, max_val = recent_max[tname]
        print(f"\n({full_table}: using {tcol} = {max_val!r} as the target DA hour)")
        dump_recent_hour_snapshot(full_table, tcol, dtype, max_val)

    print("\n=== DONE ===")


if __name__ == "__main__":
    import sys

    if "--followup" in sys.argv:
        followup()
    else:
        main()
