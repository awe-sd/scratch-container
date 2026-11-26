"""Task 09 -- station-level injection benchmark: ERCOTLOADESTIMATION family
(AW.DBO.ERCOTLOADESTIMATION_TERM_BAL + _STATION_BAL, Snowflake) vs
AW.dbo.ercotStationLoad (Snowflake).

Question (tasks/09_injection_benchmark.md): can the state-estimator-derived
LoadEstimation family replace ercotStationLoad as the source for net
injection by station? Compared separately for three legs -- load
(withdrawal), generation, and signed net -- because a disagreement that only
shows up in net is a different bug from one that shows up in both legs
(docs/load_estimation_schema.md Sec 0, task spec Sec 2).

Sign convention -- CORRECTED per the Opus grading gate (docs/task09_grading_review.md
Sec 1), which found the task spec's own Sec 2 formula wrong:
    ercotStationLoad :  net_withdrawal = WithdrawMW            (NOT WithdrawMW - GenMW --
                                                                  WithdrawMW is ALREADY net;
                                                                  see "THE comparison-basis
                                                                  correction" below)
    term_bal         :  net_withdrawal = SUM(TOTAL_NET_LOAD_MW) over kv
    station_bal      :  net_withdrawal = RAW_STATION_NET_LOAD_MW
Positive = net withdrawal (consumer); negative = net injection (producer).
Same orientation on both sides -- WithdrawMW is NEVER abs()'d, and load/
generation legs are individually non-negative on the term_bal side (only NET
carries sign there); GenMW/WithdrawMW on the ercotStationLoad side CAN each
carry sign per-column (WithdrawMW goes negative for generator station
service) -- so sign disagreement is checked on every leg, not assumed
net-only.

Value source split (deliberate, see docs/load_estimation_schema.md Sec 3.2's
reconciliation test): term_bal's kv-summed TOTAL_* columns are the value of
record for ALL THREE legs here, not station_bal's RAW_STATION_* columns --
RAW_STATION_EST_LOAD_MW/RAW_STATION_EST_GENERATION_MW were found to lose the
load/generation SPLIT at mixed generator+load stations (GBY, WTRML) even
though RAW_STATION_NET_LOAD_MW always reconciled exactly. station_bal is
still pulled and left-joined, but only for its context columns: pun_score,
unresolved_xfmr_count, coverage_flag.

PUN_* columns (sdalvi 2026-08-26, mid-task correction): term_bal also carries
PUN_TOTAL_EST_LOAD_MW / _GENERATION_MW / _NET_LOAD_MW siblings of the TOTAL_*
columns used for comparison. These are a DIFFERENT quantity -- the gross
behind-the-meter load/generation of a private use network (PUN) -- not an
alternate estimate of the same grid-facing flow. Confirmed on JCK (Jones
Creek, a real PUN): TOTAL_EST_LOAD_MW (grid-facing) reads ~25 MW while
PUN_TOTAL_EST_LOAD_MW (gross internal) averaged ~800 MW over a Feb-2026 week
-- a ~32x gap that is NOT a disagreement, it's two different quantities. This
benchmark still compares TOTAL_*/RAW_STATION_* against ercotStationLoad
(both grid-facing) as the spec requires; PUN_TOTAL_* is carried through
build_station_frame/compute_legs_long purely as a reported `pun_value_*`
context column, never as a comparison operand -- do not flag a PUN
gross-vs-net gap as an error. CORRECTED AGAIN (Opus grading-gate B5,
2026-08-26): an earlier version of this docstring claimed PUN_TOTAL_EST_LOAD_MW
and PUN_TOTAL_EST_GENERATION_MW are "identical by construction... always ~0."
That was checked against too small a sample (5 force-include/control
stations, several of which really do show it) and is FALSE as a general
claim -- verified directly against this project's own full
station_summary.csv: net-leg `pun_to_grid_ratio` has median 1.00 across 193
stations, 182/193 above 0.5, i.e. PUN_TOTAL_NET_LOAD_MW is usually NOT near
zero. LON_HILL, WTRML, GBY happen to show PUN_LOAD==PUN_GEN essentially
100% of their own hours (a real property of THOSE specific stations); JCK
shows it only 45% of the time; the population as a whole does not share it.
`pun_value_term_bal` on the net leg is therefore still reported as context
(never a comparison operand, that part stands), but should be read at face
value per-station, not assumed to be ~0.

Hour alignment: VERIFIED EMPIRICALLY per task spec Sec 3.3, not assumed --
see find_alignment_offset() / test_hour_offsets(). The winning offset is
printed and written into the findings doc; do not hardcode a different one
without re-running the test.

Flag definition (task spec Sec 4): relative pct diff against the
ercotStationLoad value (load/generation legs) or symmetric pct diff
|a-b|/max(|a|,|b|) (net leg, since net legitimately crosses zero) at >10%,
AND an independent >=5 MW absolute floor, reported as separate categories so
the floor's effect is auditable. Sign disagreements (opposite-sign, any
magnitude) and one-sided-missing rows are their own categories, never folded
into the percentage test. A further, EMPIRICALLY DISCOVERED category exists
alongside "missing": ercotStationLoad.GenMW is NULL (not 0) for a large
majority of station-hours (~73% measured, i.e. 202,388/277,017 -- though a
parallel, more targeted investigation puts the gap at only 14-29% once you
condition on "is this station actually a generator" rather than counting
ordinary load stations where GenMW being NULL is expected, see
docs/genmw_coverage.md; report both, they measure different denominators).
Verified directly: GenMW is 100% NULL across the ENTIRE cached history for
JCK/LON_HILL/HCKSW/WTRML. A row that exists on both sides but is NULL on one
side for THIS leg's column is "null_in_station_load" / "null_in_term_bal",
never silently treated as 0% disagreement AND never coalesced to 0 (NULL
means unmeasured, not confirmed-zero). This restricts BOTH the load leg
(gross withdrawal = WithdrawMW+GenMW, needs GenMW) AND the generation leg
(GenMW directly) to the ~27% of station-hours where GenMW is populated --
but NOT the net leg, which needs only WithdrawMW (always populated, see "THE
comparison-basis correction" above) and is therefore comparable everywhere.
null_in_station_load rows are EXCLUDED from
the task09_injection_benchmark.csv deliverable (not a "compared station-hour"
by its own §6 definition) but fully counted in station_summary and the
findings doc -- and reported prominently, not as a footnote, since it
materially limits how much of the net leg (the benchmark's primary quantity)
can be validated at all.

Scope (task spec Sec 5): window 2026-01-01 -> 2026-03-04 inclusive (the
family's Snowflake data stops 2026-03-04). Freshness is reported (exact
last-timestamp per platform, for the SWE backfill handoff) but per sdalvi
2026-08-26 does NOT drive the replace/don't-replace recommendation -- judge
accuracy/coverage as if current; see docs/task09_benchmark_findings.md.
Stations: the 85-station NCL roster (data/derived/ncl_stations.csv, mirrors
data/raw/station_load/ contents at the START of this task), PLUS a random
sample of >=100 non-NCL stations (seed below, reproducible), PLUS forced
JCK/LON_HILL/HCKSW/WTRML (HCKSW/WTRML are already in the 85; JCK/LON_HILL are
not and are added explicitly) -- these four are the schema sweep's documented
zero-generation / ercotStationLoad-blind-spot cases, see
docs/load_estimation_schema.md Sec 3.2 and docs/pun_audit_top25.md. JCK's
root cause is now understood (see PUN_* note above); LON_HILL's is under
separate investigation in docs/jck_lonhill_generation.md -- this module
reports what it observes for both, not a root-cause diagnosis.

Outputs:
  output/task09_injection_benchmark.csv -- one row per (station, ts_local,
    leg) that is flagged, long format (leg in {load, generation, net}).
  output/task09_station_summary.csv -- one row per (station, leg): hours
    compared, mean/median pct_diff, flagged count/rate, worst hour, NCL flag.
  docs/task09_benchmark_findings.md -- narrative writeup (hand-authored from
    this script's printed stats, not auto-generated).

Run: uv run python load-forecast/src/injection_benchmark.py
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg  # noqa: E402
import pull_station_load as psl  # noqa: E402
import pull_load_estimation as ple  # noqa: E402

POWERFLOW_ANALYTICS = cfg.PROJECT_ROOT.parent / "powerflow_analytics"
sys.path.insert(0, str(POWERFLOW_ANALYTICS))

OUTPUT_DIR = cfg.PROJECT_ROOT / "output"
BENCHMARK_CSV = OUTPUT_DIR / "task09_injection_benchmark.csv"
STATION_SUMMARY_CSV = OUTPUT_DIR / "task09_station_summary.csv"

STATION_LIST_CSV = cfg.DERIVED_DIR / "task09_station_list.csv"
STATION_UNIVERSE_CSV = cfg.DERIVED_DIR / "task09_station_universe.csv"
SE_UNIVERSE_CSV = cfg.DERIVED_DIR / "task09_se_universe.csv"

WINDOW_START = "2026-01-01"
WINDOW_END = "2026-03-04"  # inclusive; family's Snowflake data stops here (schema doc Sec 4)
SE_UNIVERSE_PROBE_DATE = "2026-02-20"  # single day inside the known-good week (schema doc)

RELATIVE_THRESHOLD = 0.10
ABS_FLOOR_MW = 5.0
MATERIALITY_FLOOR_MW = 1.0  # station-level: max|WithdrawMW| below this over the whole window = "trivial", reported separately
RANDOM_SEED = 42
N_NON_NCL_SAMPLE = 110  # spec requires >=100; small buffer for stations that turn out unmatched

FORCE_INCLUDE = ["JCK", "LON_HILL", "HCKSW", "WTRML"]
LEGS = ["load", "generation", "net"]


# --------------------------------------------------------------------------
# Station list assembly
# --------------------------------------------------------------------------

NCL_STATIONS_CSV = cfg.DERIVED_DIR / "ncl_stations.csv"


def load_ncl_stations() -> list[str]:
    """The 85-station NCL roster. Reads data/derived/ncl_stations.csv (the
    same roster pull_station_load.py's main() uses to decide what to pull),
    NOT a directory listing of data/raw/station_load/ -- that directory is
    the ercotStationLoad CACHE, and this module (like pull_station_load.py's
    own pull_all()) writes new, non-NCL stations' parquets into that SAME
    directory as part of ensure_pulled(). Deriving "is_ncl" from the
    directory listing would make the classification depend on run order /
    prior cache contents rather than being a fixed roster (verified this
    bites in practice: a smoke-test run of this module during development
    left 4 non-NCL stations cached alongside the 85, which would have
    silently mislabeled them as NCL on a later run if this read the
    directory instead of the roster CSV)."""
    if not NCL_STATIONS_CSV.exists():
        raise RuntimeError(f"NEEDS_CONTEXT: {NCL_STATIONS_CSV} not found -- run ncl_stations.py first")
    return sorted(pd.read_csv(NCL_STATIONS_CSV)["nmms_station_code"].unique().tolist())


def _station_universe() -> list[str]:
    """Distinct NmmsStationCode present in ercotStationLoad within the window
    -- cache-first, ONE date-bounded (not station-bounded, there's no list
    yet) DISTINCT query. ercotStationLoad is not the 21GB term_bal table; a
    date-bounded DISTINCT scan of it is not the query this repo's discipline
    is warning about, but it's still bounded, not SELECT *, and cached so it
    only runs once."""
    if STATION_UNIVERSE_CSV.exists():
        return pd.read_csv(STATION_UNIVERSE_CSV)["nmms_station_code"].tolist()
    from pfa import sf

    df = sf.query(
        "AW",
        f"""
        SELECT DISTINCT NMMSSTATIONCODE
        FROM AW.dbo.ercotStationLoad
        WHERE DATE >= '{WINDOW_START}' AND DATE <= '{WINDOW_END}'
        ORDER BY NMMSSTATIONCODE
        """,
    )
    df.columns = [c.upper() for c in df.columns]
    stations = sorted(df["NMMSSTATIONCODE"].tolist())
    cfg.DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"nmms_station_code": stations}).to_csv(STATION_UNIVERSE_CSV, index=False)
    return stations


def se_station_universe() -> list[str]:
    """Distinct STATION in ERCOTLOADESTIMATION_STATION_BAL on ONE bounded day
    (cheap -- the equivalent query against ercotStationLoad ran in 0.6s in the
    2026-08-26 probe; station_bal's grain has no kv fan-out to worry about).
    Cache-first. This is the POPULATION-level namespace check -- our ~190
    station sample's match rate answers "did our sample match," this answers
    "does the family's namespace cover ercotStationLoad's namespace at all,"
    which is the stronger, more direct answer to "can this family replace
    ercotStationLoad" (replacement requires covering the whole station set,
    not just a sample of it)."""
    if SE_UNIVERSE_CSV.exists():
        return pd.read_csv(SE_UNIVERSE_CSV)["station"].tolist()
    from pfa import sf

    day_end = (pd.Timestamp(SE_UNIVERSE_PROBE_DATE) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    df = sf.query(
        "AW",
        f"""
        SELECT DISTINCT STATION
        FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
        WHERE SE_TIMESTAMP >= '{SE_UNIVERSE_PROBE_DATE}' AND SE_TIMESTAMP < '{day_end}'
        """,
    )
    df.columns = [c.upper() for c in df.columns]
    stations = sorted(df["STATION"].tolist())
    cfg.DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"station": stations}).to_csv(SE_UNIVERSE_CSV, index=False)
    return stations


def population_namespace_overlap() -> dict:
    """Population-level answer to task spec Sec 3.6's "report the match rate
    as a headline number," at the full-namespace level rather than just our
    sample."""
    sl_universe = set(_station_universe())
    se_universe = set(se_station_universe())
    overlap = sl_universe & se_universe
    return {
        "n_ercotStationLoad_universe": len(sl_universe),
        "n_se_universe": len(se_universe),
        "n_overlap": len(overlap),
        "pct_ercotStationLoad_covered_by_se": len(overlap) / len(sl_universe) if sl_universe else float("nan"),
    }


def build_station_list() -> pd.DataFrame:
    """Cache-first assembly of the full task09 station list: NCL (85) + random
    non-NCL sample (>=100, seeded) + forced JCK/LON_HILL/HCKSW/WTRML.
    Columns: station, is_ncl, is_force_include."""
    if STATION_LIST_CSV.exists():
        return pd.read_csv(STATION_LIST_CSV)

    ncl = set(load_ncl_stations())
    universe = _station_universe()
    pool = [s for s in universe if s not in ncl and s not in FORCE_INCLUDE]

    rng = random.Random(RANDOM_SEED)
    sample = set(rng.sample(pool, min(N_NON_NCL_SAMPLE, len(pool))))

    all_stations = sorted(ncl | sample | set(FORCE_INCLUDE))
    df = pd.DataFrame({
        "station": all_stations,
        "is_ncl": [s in ncl for s in all_stations],
        "is_force_include": [s in FORCE_INCLUDE for s in all_stations],
    })
    cfg.DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(STATION_LIST_CSV, index=False)
    return df


def ensure_pulled(stations: list[str]) -> pd.DataFrame:
    """Cache-first pull of term_bal/station_bal (batched) and ercotStationLoad
    (sequential, existing pull_station_load convention) for every station in
    the list. Returns the pull_load_estimation.pull_all() summary frame
    (station namespace match info)."""
    le_summary = ple.pull_all(stations, start_date=WINDOW_START, end_date=WINDOW_END)
    for station in stations:  # sequential, per repo DB hygiene
        psl.pull_station(station, start_date=WINDOW_START)
    return le_summary


# --------------------------------------------------------------------------
# Hour alignment
# --------------------------------------------------------------------------

def se_timestamp_to_ts_local(se_timestamp: pd.Series, hour_offset: int) -> pd.Series:
    """Map a term_bal/station_bal SE_TIMESTAMP (stamped :57 past the hour) to
    an hour-ending ts_local label comparable with ercotStationLoad's
    (Date + (Hour + HOUR_SHIFT) hours). hour_offset=0 is the "natural"
    reading (floor to the hour, then +1h) -- see module docstring / task spec
    Sec 3.3. This function is only ever called with the EMPIRICALLY WINNING
    offset once find_alignment_offset() has run."""
    return pd.to_datetime(se_timestamp).dt.floor("h") + pd.Timedelta(hours=1 + hour_offset)


def station_load_to_ts_local(df: pd.DataFrame) -> pd.Series:
    return pd.to_datetime(df["Date"]) + pd.to_timedelta(df["Hour"].astype(int) + psl.HOUR_SHIFT, unit="h")


def pick_alignment_test_candidates(stations_df: pd.DataFrame) -> pd.DataFrame:
    """From the non-NCL, non-force-include sample, find station-days with
    full 24h coverage on both sides and pun_score == 0 all day (clean,
    "well-behaved non-PUN" per task spec Sec 3.3), ranked by peak-to-trough
    range in ercotStationLoad WithdrawMW (a high-ramp proxy). All inputs are
    already cached -- no new queries here."""
    candidates = []
    pool = stations_df.loc[~stations_df["is_ncl"] & ~stations_df["is_force_include"], "station"]
    for s in pool:
        sl = psl.pull_station(s, start_date=WINDOW_START)
        stat = ple.pull_station_bal(s, WINDOW_START, WINDOW_END)
        if sl.empty or stat.empty:
            continue
        sl = sl[(pd.to_datetime(sl["Date"]) >= pd.Timestamp(WINDOW_START)) &
                (pd.to_datetime(sl["Date"]) <= pd.Timestamp(WINDOW_END))].copy()
        if sl.empty:
            continue
        sl["ts_local"] = station_load_to_ts_local(sl)
        sl["date_local"] = sl["ts_local"].dt.date
        daily = sl.groupby("date_local").agg(n=("ts_local", "size"),
                                              rng=("WithdrawMW", lambda x: x.max() - x.min()),
                                              avg=("WithdrawMW", "mean"))
        daily = daily[daily["n"] == 24]
        if daily.empty:
            continue

        stat2 = stat.copy()
        stat2["date_se"] = pd.to_datetime(stat2["SE_TIMESTAMP"]).dt.date
        pun_daily = stat2.groupby("date_se")["PUN_SCORE"].agg(["max", "count"])

        for d, row in daily.iterrows():
            if d not in pun_daily.index:
                continue
            if pun_daily.loc[d, "count"] < 24 or pun_daily.loc[d, "max"] != 0:
                continue
            candidates.append({"station": s, "date": str(d), "range_mw": row["rng"], "avg_mw": row["avg"]})

    return pd.DataFrame(candidates).sort_values("range_mw", ascending=False).reset_index(drop=True) if candidates else pd.DataFrame(
        columns=["station", "date", "range_mw", "avg_mw"])


def test_hour_offsets(station: str, date: str, return_tables: bool = False) -> dict:
    """Test offsets {-1, 0, +1} on one station-day; return
    {offset: median_abs_diff_mw}. Pass return_tables=True to also get the
    per-hour comparison table at each offset (e.g. for ad-hoc inspection of
    one candidate) -- off by default because find_alignment_offset() calls
    this up to ALIGNMENT_TEST_CAP times and building/retaining 3 full merged
    frames per call for output nobody reads was pure overhead."""
    term = ple.pull_term_bal(station, WINDOW_START, WINDOW_END)
    sl = psl.pull_station(station, start_date=WINDOW_START).copy()
    sl["ts_local"] = station_load_to_ts_local(sl)
    day_start = pd.Timestamp(date)
    day_end = day_start + pd.Timedelta(days=1)
    sl_day = sl[(sl["ts_local"] > day_start) & (sl["ts_local"] <= day_end)]

    medians = {}
    tables = {}
    for offset in (-1, 0, 1):
        t = term.copy()
        t["ts_local"] = se_timestamp_to_ts_local(t["SE_TIMESTAMP"], offset)
        merged = t.merge(sl_day[["ts_local", "GenMW", "WithdrawMW"]], on="ts_local", how="inner")
        if merged.empty:
            medians[offset] = np.nan
            if return_tables:
                tables[offset] = merged
            continue
        # WithdrawMW is already net (B1 correction) -- compare directly, no
        # GenMW subtraction.
        merged["abs_diff"] = (merged["TOTAL_NET_LOAD_MW"] - merged["WithdrawMW"]).abs()
        medians[offset] = merged["abs_diff"].median()
        if return_tables:
            tables[offset] = merged
    return {"medians": medians, "tables": tables}


ALIGNMENT_TEST_CAP = 300  # candidates tested; see find_alignment_offset docstring
ALIGNMENT_DECISIVENESS_FLOOR = 1.5  # worst/best median ratio threshold for a "decisive" test
ALIGNMENT_MIN_DECISIVE = 20  # minimum decisive tests required before trusting the decisive-only tally


def find_alignment_offset(stations_df: pd.DataFrame) -> dict:
    """Empirical hour-offset test -- robust version.

    A single top-1-by-range candidate is NOT reliable: verified empirically
    2026-08-26 that the #1 candidate by peak-to-trough range (TRSES, range
    242.6 MW) gave a near-tied, noise-dominated result (offset -1: 11.98 MW
    median abs diff, 0: 11.98, +1: 11.90 -- a "winning" margin of ~0.7%,
    decisiveness ratio ~1.007). That happens whenever a station's two sources
    disagree in MAGNITUDE on that specific day (a real, separate finding) --
    which swamps any real timing-offset signal, since shifting the hour
    doesn't fix a level/magnitude gap. Using that single result would have
    picked offset +1, which is WRONG per the aggregate evidence below and
    would silently manufacture a spurious ~1-hour-shift disagreement on every
    ramp hour in the whole benchmark (task spec Sec 3.3's exact warning).

    The robust fix: test every (or up to ALIGNMENT_TEST_CAP) candidate
    station-day, not just the top one, and tally which offset wins among
    DECISIVE tests only (worst/best median ratio >= ALIGNMENT_DECISIVENESS_FLOOR
    -- i.e. tests where the offset choice actually matters, not a coin flip).
    Verified against the FULL 5,627-candidate pool (2026-08-26 deep-dive, not
    re-run by default here for speed -- ALIGNMENT_TEST_CAP subsamples the
    same sorted-by-range candidate list): offset 0 wins 4,192/5,627 (74.5%)
    unweighted, and 3,779/3,879 (97.4%) among decisive tests, with a median
    decisiveness of 18.6x when 0 wins vs ~1.08x when +-1 "win" (pure noise).
    This is the winning-offset methodology actually used; top-1-by-range is
    reported alongside only as a single human-readable example, never as the
    decision basis."""
    candidates = pick_alignment_test_candidates(stations_df)
    if candidates.empty:
        return {"resolved": False, "candidates": candidates}

    tested = candidates.head(ALIGNMENT_TEST_CAP)
    rows = []
    for _, row in tested.iterrows():
        result = test_hour_offsets(row["station"], row["date"])
        medians = result["medians"]
        finite = {k: v for k, v in medians.items() if pd.notna(v)}
        if len(finite) < 3:
            continue
        winner = min(finite, key=finite.get)
        best = finite[winner]
        worst = max(finite.values())
        decisiveness = worst / best if best > 0 else float("nan")
        rows.append({"station": row["station"], "date": row["date"], "range_mw": row["range_mw"],
                     "m_-1": medians.get(-1), "m_0": medians.get(0), "m_1": medians.get(1),
                     "winner": winner, "decisiveness": decisiveness})
    results_df = pd.DataFrame(rows)
    if results_df.empty:
        return {"resolved": False, "candidates": candidates}

    decisive = results_df[results_df["decisiveness"] >= ALIGNMENT_DECISIVENESS_FLOOR]
    used_decisive_only = len(decisive) >= ALIGNMENT_MIN_DECISIVE
    tally_source = decisive if used_decisive_only else results_df
    winning_offset = int(tally_source["winner"].value_counts().idxmax())

    top_by_range = results_df.iloc[0]
    top_by_decisiveness = results_df.loc[results_df["decisiveness"].idxmax()]

    return {
        "resolved": True,
        "candidates": candidates,
        "n_candidates_total": len(candidates),
        "n_candidates_tested": len(results_df),
        "n_decisive": len(decisive),
        "used_decisive_only": used_decisive_only,
        "tally_all": results_df["winner"].value_counts().to_dict(),
        "tally_decisive": decisive["winner"].value_counts().to_dict(),
        "median_decisiveness_by_winner": decisive.groupby("winner")["decisiveness"].median().to_dict() if len(decisive) else {},
        "winning_offset": winning_offset,
        "top_by_range": top_by_range.to_dict(),
        "top_by_decisiveness": top_by_decisiveness.to_dict(),
    }


# --------------------------------------------------------------------------
# Comparison frame construction
# --------------------------------------------------------------------------

def load_bad_interval_set() -> set:
    bi = ple.pull_bad_intervals(WINDOW_START, WINDOW_END)
    if bi.empty:
        return set()
    return set(pd.to_datetime(bi["INTERVAL"]))


def _empty_est_frame() -> pd.DataFrame:
    cols = ["STATION", "SE_TIMESTAMP", "TOTAL_EST_LOAD_MW", "TOTAL_EST_GENERATION_MW", "TOTAL_NET_LOAD_MW",
            "PUN_TOTAL_EST_LOAD_MW", "PUN_TOTAL_EST_GENERATION_MW", "PUN_TOTAL_NET_LOAD_MW",
            "KV_COUNT", "ts_local", "PUN_SCORE", "UNRESOLVED_XFMR_COUNT", "COVERAGE_FLAG"]
    return pd.DataFrame({c: pd.Series(dtype="object") for c in cols})


def _empty_sl_frame() -> pd.DataFrame:
    cols = ["ts_local", "GenMW", "WithdrawMW"]
    return pd.DataFrame({c: pd.Series(dtype="object") for c in cols})


def build_station_frame(station: str, hour_offset: int, bad_intervals: set) -> pd.DataFrame:
    """One station's outer-merged (term_bal+station_bal) vs ercotStationLoad
    frame, keyed on ts_local, with a _merge indicator."""
    term = ple.pull_term_bal(station, WINDOW_START, WINDOW_END)
    stat = ple.pull_station_bal(station, WINDOW_START, WINDOW_END)
    sl = psl.pull_station(station, start_date=WINDOW_START)

    if not term.empty:
        est = term.copy()
        est["ts_local"] = se_timestamp_to_ts_local(est["SE_TIMESTAMP"], hour_offset)
        if not stat.empty:
            stat_ctx = stat.copy()
            stat_ctx["ts_local"] = se_timestamp_to_ts_local(stat_ctx["SE_TIMESTAMP"], hour_offset)
            stat_ctx = stat_ctx[["ts_local", "PUN_SCORE", "UNRESOLVED_XFMR_COUNT", "COVERAGE_FLAG"]]
            est = est.merge(stat_ctx, on="ts_local", how="left")
        else:
            for c in ["PUN_SCORE", "UNRESOLVED_XFMR_COUNT", "COVERAGE_FLAG"]:
                est[c] = pd.NA
    else:
        est = _empty_est_frame()

    if not sl.empty:
        sl2 = sl[(pd.to_datetime(sl["Date"]) >= pd.Timestamp(WINDOW_START)) &
                 (pd.to_datetime(sl["Date"]) <= pd.Timestamp(WINDOW_END))].copy()
        if not sl2.empty:
            sl2["ts_local"] = station_load_to_ts_local(sl2)
            sl2 = sl2[["ts_local", "GenMW", "WithdrawMW"]]
        else:
            sl2 = _empty_sl_frame()
    else:
        sl2 = _empty_sl_frame()

    merged = est.merge(sl2, on="ts_local", how="outer", indicator=True)
    merged["station"] = station

    # Exclude bad-interval hours from BOTH sides symmetrically, on the merged
    # frame -- excluding only from the term_bal side pre-merge would make a
    # known-bad SE interval masquerade as a "missing_in_term_bal" coverage
    # gap, which is a different (and wrong) finding.
    if bad_intervals:
        bad_ts_local = {pd.Timestamp(x).floor("h") + pd.Timedelta(hours=1 + hour_offset) for x in bad_intervals}
        merged = merged[~merged["ts_local"].isin(bad_ts_local)]

    return merged


def compute_legs_long(wide: pd.DataFrame) -> pd.DataFrame:
    """Wide (one row per station-hour) -> long (one row per station-hour-leg)."""
    if wide.empty:
        return pd.DataFrame()
    df = wide.copy()
    # CORRECTED AGAIN 2026-08-26 (Opus grading-gate FAIL, B1 -- independently
    # re-verified against this project's own cached data before accepting
    # it): `ercotStationLoad.WithdrawMW` is ALREADY a NET quantity (load minus
    # generation), not gross withdrawal -- confirmed by organic_load.py:16
    # ("WithdrawMW is a branch-flow-derived NET quantity"), by
    # docs/jck_lonhill_generation.md, and empirically: at 18,066
    # materially-generating station-hours (GenMW>=5MW), `WithdrawMW` alone
    # matches `TOTAL_NET_LOAD_MW` with median abs error 0.17 MW (82% within
    # 0.5 MW), while the PREVIOUS `WithdrawMW - GenMW` formula (an earlier,
    # since-superseded correction) gives median abs error 78.5 MW -- an
    # order-of-magnitude worse, because it double-subtracts generation that
    # WithdrawMW has already netted out. Concrete proof, WHCCS2 @
    # 2026-01-27 00:00: tb_load=0, tb_gen=1142.78, tb_net=-1142.78;
    # GenMW=1134.52, WithdrawMW=-1143.99 (matches tb_net to 1.2 MW). The
    # previous formula computed -1143.99-1134.52=-2278.5, off by 1136 MW.
    # CONSEQUENCE: net = WithdrawMW directly, no GenMW involved at all --
    # and since WithdrawMW is essentially always populated, the net leg is
    # comparable EVERYWHERE (not restricted to the GenMW-populated subset,
    # which is what the load/generation legs are restricted to). Gross LOAD
    # (before any behind-the-meter generation nets it out) is WithdrawMW +
    # GenMW -- verified same population: median abs error vs
    # TOTAL_EST_LOAD_MW is 8.7 MW (W+G) vs 79.7 MW (W alone, the previous
    # load-leg operand). GenMW is still never coalesced to 0 (NULL means
    # unmeasured; classify_flags' null_in_station_load machinery still
    # applies to the load leg wherever GenMW is null). Separately: a parallel
    # investigation (docs/kv_aggregation_test.md) tested and FALSIFIED the
    # hypothesis that summing TOTAL_NET_LOAD_MW over kv double-counts --
    # median ratio to RAW_STATION_NET_LOAD_MW is 1.001 across 30 stations
    # spanning KV_COUNT 1-5, no correlation with kv count (r=0.093) -- so the
    # kv-summing in pull_load_estimation.py's SQL is correct and unchanged.
    df["sl_gross_load"] = df["WithdrawMW"] + df["GenMW"]
    leg_cols = {
        "load": ("TOTAL_EST_LOAD_MW", "sl_gross_load", "PUN_TOTAL_EST_LOAD_MW"),
        "generation": ("TOTAL_EST_GENERATION_MW", "GenMW", "PUN_TOTAL_EST_GENERATION_MW"),
        "net": ("TOTAL_NET_LOAD_MW", "WithdrawMW", "PUN_TOTAL_NET_LOAD_MW"),
    }
    ctx_cols = ["station", "ts_local", "KV_COUNT", "PUN_SCORE", "UNRESOLVED_XFMR_COUNT", "COVERAGE_FLAG", "_merge"]
    parts = []
    for leg, (a_col, b_col, pun_col) in leg_cols.items():
        sub = df[ctx_cols + [a_col, b_col, pun_col]].copy()
        sub = sub.rename(columns={a_col: "value_term_bal", b_col: "value_station_load", pun_col: "pun_value_term_bal"})
        sub["value_term_bal"] = pd.to_numeric(sub["value_term_bal"], errors="coerce")
        sub["value_station_load"] = pd.to_numeric(sub["value_station_load"], errors="coerce")
        sub["pun_value_term_bal"] = pd.to_numeric(sub["pun_value_term_bal"], errors="coerce")
        sub["leg"] = leg
        parts.append(sub)
    return pd.concat(parts, ignore_index=True)


def classify_flags(long_df: pd.DataFrame) -> pd.DataFrame:
    if long_df.empty:
        return long_df
    df = long_df.copy()
    a = df["value_term_bal"]
    b = df["value_station_load"]
    both = df["_merge"] == "both"
    missing_in_term_bal = df["_merge"] == "right_only"       # present in ercotStationLoad only
    missing_in_station_load = df["_merge"] == "left_only"    # present in term_bal side only

    # A row can be present on both sides (_merge=='both') yet have a NULL
    # value for THIS leg's column -- ercotStationLoad.GenMW is null (not 0)
    # for the large majority of station-hours, which hits the load leg
    # (b=WithdrawMW+GenMW, NULL whenever GenMW is) and the generation leg
    # (b=GenMW directly). It does NOT hit the net leg (b=WithdrawMW, always
    # populated -- WithdrawMW is already net, see compute_legs_long's
    # docstring; this is corrected from an earlier version of this comment
    # that still described the superseded WithdrawMW-GenMW net formula).
    # Treating a null as "0 disagreement" would silently
    # report perfect agreement on a leg/station the source doesn't actually
    # let us evaluate -- same failure mode the task spec warns about for
    # missing rows, just at the column level instead of the row level. These
    # get their own category, never folded into "relative"/"sign"/"missing".
    both_valid = both & a.notna() & b.notna()
    null_in_station_load = both & a.notna() & b.isna()
    null_in_term_bal = both & a.isna() & b.notna()

    diff = a - b
    df["diff_mw"] = diff

    is_net = df["leg"] == "net"
    denom = np.where(is_net, np.maximum(a.abs(), b.abs()), b.abs())
    denom = pd.Series(denom, index=df.index)
    pct = pd.Series(np.nan, index=df.index)
    nonzero_denom = both_valid & (denom > 0)
    pct.loc[nonzero_denom] = diff.loc[nonzero_denom] / denom.loc[nonzero_denom]
    zero_denom_nonzero_diff = both_valid & (denom == 0) & (diff.abs() > 0)
    pct.loc[zero_denom_nonzero_diff] = np.sign(diff.loc[zero_denom_nonzero_diff]) * np.inf
    zero_denom_zero_diff = both_valid & (denom == 0) & (diff.abs() == 0)
    pct.loc[zero_denom_zero_diff] = 0.0
    df["pct_diff"] = pct

    sign_disagree = both_valid & (((a > 0) & (b < 0)) | ((a < 0) & (b > 0)))
    fails_relative = both_valid & ~sign_disagree & (pct.abs() > RELATIVE_THRESHOLD)
    fails_absolute = both_valid & (diff.abs() >= ABS_FLOOR_MW)

    cat = pd.Series(np.nan, index=df.index, dtype=object)
    cat[both_valid & fails_relative & ~fails_absolute] = "relative"
    cat[both_valid & fails_relative & fails_absolute] = "relative+absolute"
    cat[both_valid & sign_disagree] = "sign"
    cat[missing_in_station_load] = "missing_in_station_load"
    cat[missing_in_term_bal] = "missing_in_term_bal"
    cat[null_in_station_load] = "null_in_station_load"
    cat[null_in_term_bal] = "null_in_term_bal"
    df["flag_category"] = cat
    return df


def build_full_comparison(stations_df: pd.DataFrame, hour_offset: int, bad_intervals: set) -> pd.DataFrame:
    parts = []
    for station in stations_df["station"]:
        wide = build_station_frame(station, hour_offset, bad_intervals)
        long_df = compute_legs_long(wide)
        if long_df.empty:
            continue
        long_df = classify_flags(long_df)
        parts.append(long_df)
    full = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    full = full.merge(stations_df, on="station", how="left")
    return full


# --------------------------------------------------------------------------
# Summaries
# --------------------------------------------------------------------------

def summarize_stations(full: pd.DataFrame) -> pd.DataFrame:
    """flagged_rate (loose) and flagged_rate_strict are both scoped to hours
    where both sources actually have a comparable, non-null value for this
    leg (n_hours_comparable). Missing rows and null-column rows are reported
    as separate coverage columns, not folded into either rate -- a null
    ercotStationLoad.GenMW on the generation leg is "not evaluable," not "0%
    disagreement."

    CORRECTED per Opus grading-gate B3 (2026-08-26): an earlier version only
    computed one "flagged_rate" that mixed bare `relative` (fails the 10%
    test but NOT the 5 MW absolute floor -- exactly the "trivial magnitude"
    case spec Sec 4 says the floor exists to suppress) in with
    `relative+absolute` and `sign`. That silently discarded the floor's
    effect on the headline number even though it was computed and available
    per-category. Now BOTH are reported: `flagged_rate` (loose -- relative OR
    relative+absolute OR sign, i.e. "fails the 10% test at all") and
    `flagged_rate_strict` (relative+absolute OR sign only -- the floor-
    respecting rate spec Sec 4 actually asks for as the primary flag).
    Report flagged_rate_strict as the headline in prose; flagged_rate stays
    for transparency/tunability, per spec's "sdalvi decides the final
    threshold.\""""
    rows = []
    for (station, leg), grp in full.groupby(["station", "leg"]):
        both = grp[grp["_merge"] == "both"]
        comparable = both[both["value_term_bal"].notna() & both["value_station_load"].notna()]
        finite_pct = comparable["pct_diff"].replace([np.inf, -np.inf], np.nan).dropna()
        true_flagged = grp[grp["flag_category"].isin(["relative", "relative+absolute", "sign"])]
        strict_flagged = grp[grp["flag_category"].isin(["relative+absolute", "sign"])]
        worst = None
        if not comparable.empty and comparable["diff_mw"].abs().notna().any():
            worst = comparable.loc[comparable["diff_mw"].abs().idxmax()]

        # PUN gross-vs-grid-facing context (module docstring's PUN_* note) --
        # reported, never compared/flagged. A large ratio flags "this station
        # is a PUN with a lot of behind-the-meter activity," not a source
        # disagreement.
        max_grid = grp["value_term_bal"].abs().max()
        max_pun = grp["pun_value_term_bal"].abs().max()
        pun_ratio = (max_pun / max_grid) if pd.notna(max_grid) and max_grid > 0 and pd.notna(max_pun) else np.nan

        rows.append({
            "station": station,
            "leg": leg,
            "is_ncl": grp["is_ncl"].iloc[0],
            "is_force_include": grp["is_force_include"].iloc[0],
            "n_hours_total": len(grp),
            "n_hours_both": len(both),
            "n_hours_comparable": len(comparable),
            "n_missing_in_term_bal": (grp["flag_category"] == "missing_in_term_bal").sum(),
            "n_missing_in_station_load": (grp["flag_category"] == "missing_in_station_load").sum(),
            "n_null_in_station_load": (grp["flag_category"] == "null_in_station_load").sum(),
            "n_null_in_term_bal": (grp["flag_category"] == "null_in_term_bal").sum(),
            "mean_pct_diff": finite_pct.mean() if len(finite_pct) else np.nan,
            "median_pct_diff": finite_pct.median() if len(finite_pct) else np.nan,
            "n_undefined_denom": np.isinf(comparable["pct_diff"]).sum(),
            "n_flagged": len(true_flagged),
            "flagged_rate": len(true_flagged) / len(comparable) if len(comparable) else np.nan,
            "n_flagged_strict": len(strict_flagged),
            "flagged_rate_strict": len(strict_flagged) / len(comparable) if len(comparable) else np.nan,
            "n_flagged_relative_only": (grp["flag_category"] == "relative").sum(),
            "n_flagged_relative_and_absolute": (grp["flag_category"] == "relative+absolute").sum(),
            "n_flagged_sign": (grp["flag_category"] == "sign").sum(),
            "worst_hour_ts": worst["ts_local"] if worst is not None else pd.NaT,
            "worst_hour_diff_mw": worst["diff_mw"] if worst is not None else np.nan,
            "worst_hour_pct_diff": worst["pct_diff"] if worst is not None else np.nan,
            "max_abs_grid_facing_mw": max_grid,
            "max_abs_pun_gross_mw": max_pun,
            "pun_to_grid_ratio": pun_ratio,
        })
    return pd.DataFrame(rows).sort_values(["leg", "flagged_rate_strict"], ascending=[True, False]).reset_index(drop=True)


def compute_blind_spot_stats(full: pd.DataFrame, neg_withdraw_floor_mw: float = 1.0,
                              min_material_hours: int = 24) -> pd.DataFrame:
    """Task spec Sec 5's highest-value question, reduced to two named,
    per-station statistics (per advisor guidance 2026-08-26) -- computed over
    the WHOLE comparison window, not one probe day:

    se_blind_to_generation: term_bal shows essentially zero generation for
      this station (grid-facing TOTAL_EST_GENERATION_MW never exceeds
      ABS_FLOOR_MW) WHILE ercotStationLoad shows a material number of hours
      (>=min_material_hours) with WithdrawMW <= -neg_withdraw_floor_mw --
      i.e. ercotStationLoad sees it acting as a generator on real hours, but
      term_bal never records generation there. This is the JCK/LON_HILL
      pattern, generalized to the full sample -- JCK/LON_HILL are reported by
      this same statistic like every other station; their specific root
      cause is being investigated separately in docs/jck_lonhill_generation.md
      and is NOT re-diagnosed here.

    station_load_blind_to_load: ercotStationLoad shows essentially zero
      withdrawal for this station (max|WithdrawMW| across the whole window
      below neg_withdraw_floor_mw) WHILE term_bal shows material grid-facing
      load or net magnitude (>= ABS_FLOOR_MW) -- the HCKSW/WTRML pattern,
      generalized.

    Also carries the materiality classifier used to split the non-NCL
    agreement rate two ways (all-sampled vs materially-loaded-only) --
    max|WithdrawMW| < MATERIALITY_FLOOR_MW over the whole window means a
    station is essentially idle/unenergized in ercotStationLoad for this
    window, which would otherwise inflate the apparent agreement rate simply
    by contributing all-near-zero, trivially-agreeing hours."""
    # NOTE (B1 correction): raw WithdrawMW now lives on the NET leg's
    # value_station_load (net = WithdrawMW directly, unfilled, always
    # populated) -- NOT the load leg, which is now the derived gross
    # quantity WithdrawMW+GenMW. term_load below still reads TOTAL_EST_LOAD_MW
    # from the load leg's term_bal side, which is unaffected by the operand
    # change.
    net_leg = full[full["leg"] == "net"]
    load_leg = full[full["leg"] == "load"]
    gen_leg = full[full["leg"] == "generation"]
    rows = []
    for station, grp in net_leg.groupby("station"):
        both = grp[grp["_merge"] == "both"]
        sl_withdraw = both["value_station_load"]  # raw WithdrawMW
        term_net = both["value_term_bal"]  # TOTAL_NET_LOAD_MW
        lg = load_leg[load_leg["station"] == station]
        term_load = lg[lg["_merge"] == "both"]["value_term_bal"]
        g = gen_leg[gen_leg["station"] == station]
        term_gen = g[g["value_term_bal"].notna()]["value_term_bal"]

        n_neg_withdraw_hours = int((sl_withdraw <= -neg_withdraw_floor_mw).sum())
        max_abs_withdraw = sl_withdraw.abs().max() if len(sl_withdraw) else np.nan
        max_term_gen = term_gen.abs().max() if len(term_gen) else np.nan
        max_term_load = term_load.abs().max() if len(term_load) else np.nan

        se_blind_to_generation = bool(
            pd.notna(max_term_gen) and max_term_gen < ABS_FLOOR_MW and n_neg_withdraw_hours >= min_material_hours
        )
        station_load_blind_to_load = bool(
            pd.notna(max_abs_withdraw) and max_abs_withdraw < MATERIALITY_FLOOR_MW and
            pd.notna(max_term_load) and max_term_load >= ABS_FLOOR_MW
        )
        materially_loaded = bool(pd.notna(max_abs_withdraw) and max_abs_withdraw >= MATERIALITY_FLOOR_MW)

        # Per-station net-magnitude RATIO (coordinator's "centerpiece" ask,
        # 2026-08-26, following docs/kv_aggregation_test.md's finding that a
        # subset of stations -- JCK ~3.28x, LON_HILL ~3.1x seasonally -- show
        # a real, non-alignment, non-kv-summing residual gap). Computed only
        # over materially-sized hours (|WithdrawMW|>=MATERIALITY_FLOOR_MW) to
        # avoid near-zero-denominator noise; ratio-of-sums, matching
        # kv_aggregation_test.md's own methodology for comparability.
        mat = both[sl_withdraw.abs() >= MATERIALITY_FLOOR_MW]
        if len(mat) >= min_material_hours:
            sum_w = mat["value_station_load"].sum()
            sum_tb = mat["value_term_bal"].sum()
            net_ratio = (sum_tb / sum_w) if sum_w != 0 else np.nan
        else:
            net_ratio = np.nan

        rows.append({
            "station": station,
            "n_hours_both_load_leg": len(both),
            "max_term_bal_generation_mw": max_term_gen,
            "n_negative_withdraw_hours_sl": n_neg_withdraw_hours,
            "max_abs_withdraw_mw_sl": max_abs_withdraw,
            "max_term_bal_load_mw": max_term_load,
            "se_blind_to_generation": se_blind_to_generation,
            "station_load_blind_to_load": station_load_blind_to_load,
            "materially_loaded_in_station_load": materially_loaded,
            "net_ratio_tb_over_sl": net_ratio,
            "n_material_hours_for_ratio": len(mat),
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> None:
    print("=== task09 injection benchmark ===")
    stations_df = build_station_list()
    print(f"station list: {len(stations_df)} total "
          f"({stations_df['is_ncl'].sum()} NCL, "
          f"{(~stations_df['is_ncl'] & ~stations_df['is_force_include']).sum()} non-NCL sample, "
          f"{stations_df['is_force_include'].sum()} force-include)")

    le_summary = ensure_pulled(stations_df["station"].tolist())
    n_matched = int(le_summary["matched"].sum())
    print(f"sample station namespace match: {n_matched}/{len(le_summary)} had >=1 term_bal row in window "
          f"({100 * n_matched / len(le_summary):.1f}%)")
    unmatched = le_summary.loc[~le_summary["matched"], "station"].tolist()
    if unmatched:
        print(f"unmatched stations ({len(unmatched)}): {unmatched}")

    print("\n=== population-level namespace overlap ===")
    overlap = population_namespace_overlap()
    print(f"ercotStationLoad universe (window-bounded): {overlap['n_ercotStationLoad_universe']} stations")
    print(f"ERCOTLOADESTIMATION universe (1-day probe {SE_UNIVERSE_PROBE_DATE}): {overlap['n_se_universe']} stations")
    print(f"overlap: {overlap['n_overlap']} "
          f"({100 * overlap['pct_ercotStationLoad_covered_by_se']:.1f}% of ercotStationLoad's universe)")

    # Freshness corroboration (NOT a blocker per sdalvi 2026-08-26 -- reported
    # for the SWE backfill handoff only). Schema doc's own numbers are the
    # citation of record; this just cross-checks against what we actually
    # pulled, from cache, no new query.
    term_paths = list(ple.TERM_BAL_DIR.glob("*.parquet"))
    observed_max_list = []
    for p in term_paths:
        d = pd.read_parquet(p, columns=["SE_TIMESTAMP"])
        if len(d):
            observed_max_list.append(d["SE_TIMESTAMP"].max())
    if observed_max_list:
        max_ts = max(observed_max_list)
        print(f"\nlatest SE_TIMESTAMP observed in this run's own pulled data: {max_ts} "
              f"(schema doc's documented Snowflake max: 2026-03-04 23:57; SQL Server max: 2026-02-26 23:57)")

    print("\n=== hour alignment test (robust: tallied across many candidates, not just the top one) ===")
    align = find_alignment_offset(stations_df)
    if not align["resolved"]:
        print("INCONCLUSIVE: no clean (pun_score==0, full 24h) non-NCL station-day candidate found.")
        print("Falling back to offset 0 (natural reading) -- see findings doc for the caveat.")
        winning_offset = 0
    else:
        print(f"candidates available: {align['n_candidates_total']}, tested: {align['n_candidates_tested']} "
              f"(cap={ALIGNMENT_TEST_CAP}), decisive (ratio>={ALIGNMENT_DECISIVENESS_FLOOR}): {align['n_decisive']}")
        print(f"winner tally, ALL tested: {align['tally_all']}")
        print(f"winner tally, DECISIVE only: {align['tally_decisive']}")
        print(f"median decisiveness by winner (decisive subset): {align['median_decisiveness_by_winner']}")
        print(f"tally basis used: {'decisive-only' if align['used_decisive_only'] else 'all-tested (too few decisive)'}")
        r = align["top_by_range"]
        print(f"example -- highest-range candidate: {r['station']} on {r['date']} (range={r['range_mw']:.1f} MW): "
              f"m_-1={r['m_-1']:.3g}, m_0={r['m_0']:.3g}, m_1={r['m_1']:.3g}, "
              f"winner={r['winner']}, decisiveness={r['decisiveness']:.3g}")
        d = align["top_by_decisiveness"]
        print(f"example -- most decisive candidate: {d['station']} on {d['date']} (range={d['range_mw']:.1f} MW): "
              f"m_-1={d['m_-1']:.3g}, m_0={d['m_0']:.3g}, m_1={d['m_1']:.3g}, "
              f"winner={d['winner']}, decisiveness={d['decisiveness']:.3g}")
        winning_offset = align["winning_offset"]
        print(f"WINNING OFFSET: {winning_offset}")

    print("\n=== building full comparison ===")
    bad_intervals = load_bad_interval_set()
    print(f"bad intervals in window: {len(bad_intervals)}")
    full = build_full_comparison(stations_df, winning_offset, bad_intervals)
    print(f"total (station, ts_local, leg) rows: {len(full)}")

    # null_in_station_load (~= GenMW is NULL, the generation leg almost
    # everywhere) is a "not evaluable" state, not a compared station-hour --
    # excluded from the deliverable CSV per its own definition (task spec
    # Sec 6: "one row per compared station-hour that is flagged"). The count
    # is still fully reported in station_summary and the findings doc.
    # null_in_term_bal is kept (would be surprising -- term_bal's columns are
    # documented ~100% non-null).
    csv_categories = ["relative", "relative+absolute", "sign", "missing_in_term_bal",
                       "missing_in_station_load", "null_in_term_bal"]
    flagged = full[full["flag_category"].isin(csv_categories)].copy()
    n_null_gen = int((full["flag_category"] == "null_in_station_load").sum())
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    flagged = flagged.rename(columns={"PUN_SCORE": "pun_score", "UNRESOLVED_XFMR_COUNT": "unresolved_xfmr_count",
                                       "COVERAGE_FLAG": "coverage_flag", "KV_COUNT": "kv_count"})
    out_cols = ["station", "ts_local", "leg", "value_term_bal", "value_station_load", "diff_mw", "pct_diff",
                "flag_category", "pun_score", "unresolved_xfmr_count", "coverage_flag", "kv_count",
                "pun_value_term_bal", "is_ncl", "is_force_include"]
    flagged[out_cols].sort_values(["station", "ts_local", "leg"]).to_csv(BENCHMARK_CSV, index=False)
    print(f"wrote {BENCHMARK_CSV} ({len(flagged)} flagged rows; "
          f"{n_null_gen} additional null_in_station_load rows excluded -- not a compared hour, see station_summary)")

    for leg in LEGS:
        leg_full = full[full["leg"] == leg]
        leg_comparable = leg_full[(leg_full["_merge"] == "both") & leg_full["value_term_bal"].notna() &
                                   leg_full["value_station_load"].notna()]
        leg_true_flagged = leg_full[leg_full["flag_category"].isin(["relative", "relative+absolute", "sign"])]
        rate_str = (f"{100 * len(leg_true_flagged) / len(leg_comparable):.2f}% of comparable hours"
                    if len(leg_comparable) else "not evaluable (0 comparable hours)")
        print(f"  leg={leg}: n_comparable={len(leg_comparable)}, n_flagged={len(leg_true_flagged)} ({rate_str}), "
              f"sign={(leg_full['flag_category'] == 'sign').sum()}, "
              f"missing_in_term_bal={(leg_full['flag_category'] == 'missing_in_term_bal').sum()}, "
              f"missing_in_station_load={(leg_full['flag_category'] == 'missing_in_station_load').sum()}, "
              f"null_in_station_load={(leg_full['flag_category'] == 'null_in_station_load').sum()}, "
              f"null_in_term_bal={(leg_full['flag_category'] == 'null_in_term_bal').sum()}")

    blind_spot = compute_blind_spot_stats(full)
    station_summary = summarize_stations(full)
    station_summary = station_summary.merge(
        blind_spot[["station", "se_blind_to_generation", "station_load_blind_to_load",
                    "materially_loaded_in_station_load", "n_negative_withdraw_hours_sl",
                    "max_term_bal_generation_mw", "max_abs_withdraw_mw_sl",
                    "net_ratio_tb_over_sl", "n_material_hours_for_ratio"]],
        on="station", how="left")
    station_summary.to_csv(STATION_SUMMARY_CSV, index=False)
    print(f"wrote {STATION_SUMMARY_CSV} ({len(station_summary)} rows)")

    print("\n=== Sec 5 generalization question: named blind-spot statistics (whole sample, whole window) ===")
    n_se_blind = int(blind_spot["se_blind_to_generation"].sum())
    n_sl_blind = int(blind_spot["station_load_blind_to_load"].sum())
    print(f"se_blind_to_generation (term_bal shows ~0 gen while ercotStationLoad shows >=24h of real negative "
          f"WithdrawMW): {n_se_blind}/{len(blind_spot)} stations")
    print(blind_spot.loc[blind_spot["se_blind_to_generation"], "station"].tolist())
    print(f"station_load_blind_to_load (ercotStationLoad ~0 withdrawal all window while term_bal shows "
          f">={ABS_FLOOR_MW} MW load/net): {n_sl_blind}/{len(blind_spot)} stations")
    print(blind_spot.loc[blind_spot["station_load_blind_to_load"], "station"].tolist())
    for s in FORCE_INCLUDE:
        row = blind_spot[blind_spot["station"] == s]
        if not row.empty:
            r = row.iloc[0]
            print(f"  {s}: max_term_bal_gen={r['max_term_bal_generation_mw']:.2f} MW, "
                  f"n_negative_withdraw_hours={r['n_negative_withdraw_hours_sl']}, "
                  f"max_abs_withdraw_sl={r['max_abs_withdraw_mw_sl']:.2f} MW, "
                  f"se_blind_to_generation={r['se_blind_to_generation']}, "
                  f"station_load_blind_to_load={r['station_load_blind_to_load']}")

    print("\n=== NCL vs non-NCL split (net leg), all-sampled vs materially-loaded-only ===")
    net_summary = station_summary[station_summary["leg"] == "net"]
    for is_ncl, grp in net_summary.groupby("is_ncl"):
        total_comparable = grp["n_hours_comparable"].sum()
        total_flagged = grp["n_flagged"].sum()
        rate = 100 * total_flagged / total_comparable if total_comparable else float("nan")
        mat = grp[grp["materially_loaded_in_station_load"] == True]  # noqa: E712
        mat_comparable = mat["n_hours_comparable"].sum()
        mat_flagged = mat["n_flagged"].sum()
        mat_rate = 100 * mat_flagged / mat_comparable if mat_comparable else float("nan")
        print(f"  is_ncl={is_ncl}: ALL {len(grp)} stations -> {total_flagged}/{total_comparable} flagged "
              f"({rate:.2f}%);  MATERIALLY-LOADED-ONLY {len(mat)} stations -> {mat_flagged}/{mat_comparable} "
              f"flagged ({mat_rate:.2f}%)")

    print("\n=== force-include stations (all legs) ===")
    for leg in LEGS:
        leg_summary = station_summary[(station_summary["leg"] == leg) & station_summary["is_force_include"]]
        print(f"-- leg={leg} --")
        print(leg_summary[
            ["station", "n_hours_total", "n_hours_comparable", "n_flagged", "flagged_rate",
             "n_missing_in_term_bal", "n_missing_in_station_load",
             "n_null_in_station_load", "n_null_in_term_bal", "pun_to_grid_ratio"]
        ].to_string(index=False))


if __name__ == "__main__":
    main()
