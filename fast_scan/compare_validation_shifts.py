"""Compare study shift factors (CPNODE_SHIFTS_VIEW) against DART actual shifts
(psenShiftDef type 14) for every validation-fast-scan topology-shift-set config
of a study. See fast_scan/shift_benchmarking.py::benchmark_shifts for the
reference join this reuses (DART_shifts CTE, reference-bus normalization).
"""
import argparse
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "powerflow_analytics"))
from pfa.sf import query  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("compare_validation_shifts")

REFERENCE_CPNODEID = 12791
BAD_THRESHOLD = 0.02


def get_configs(study_id: int, created_after: str) -> pd.DataFrame:
    sql = f"""
    SELECT TOPOLOGYSHIFTSETID, BRANCHLABEL, CTGLABEL, INTERFACENAME, DIRECTION,
        CREATEDATE, NOTES, FROMNUM, TONUM, CKT
    FROM AW.POPT.TOPOLOGYSHIFTSETDEF
    WHERE STUDYID={study_id} AND CREATEDATE >= '{created_after}'
    """
    return query("AW", sql)


def get_date_range(set_id: int, date_from: str | None = None, date_to: str | None = None) -> tuple[str, str]:
    sql = f"""
    SELECT MIN(orun.simdate) mn, MAX(orun.simdate) mx
    FROM SHIFT_FACTORS.DBO.CPNODE_SHIFTS_VIEW cv
    INNER JOIN AWOPF.DBO.OPFRUN orun ON cv.runid = orun.runid
    WHERE cv.PSENSHIFTID IN (
        SELECT PSENSHIFTID FROM AW.POPT.TOPOLOGYSHIFTSET WHERE TOPOLOGYSHIFTSETID={set_id}
    )
    {f"AND orun.simdate >= '{date_from}'" if date_from else ""}
    {f"AND orun.simdate <= '{date_to}'" if date_to else ""}
    """
    df = query("AW", sql)
    if df.empty or pd.isna(df.iloc[0, 0]):
        return None, None
    mn = pd.Timestamp(df.iloc[0, 0]) - pd.Timedelta(days=1)
    mx = pd.Timestamp(df.iloc[0, 1]) + pd.Timedelta(days=1)
    return mn.strftime("%Y-%m-%d"), mx.strftime("%Y-%m-%d")


def pull_joined_raw(
    set_id: int, branch_label: str, ctg_label: str, start_date: str, end_date: str,
    date_from: str | None = None, date_to: str | None = None,
) -> pd.DataFrame:
    """Pull raw joined rows (study x DART x reference-bus), unsigned psens_raw."""
    study_date_filter = ""
    if date_from:
        study_date_filter += f" AND orun.simdate >= '{date_from}'"
    if date_to:
        study_date_filter += f" AND orun.simdate <= '{date_to}'"
    sql = f"""
    WITH study_shifts AS (
        SELECT cv.PSENSHIFTID, cv.RUNID, cv.psens AS psens_raw, cv.direction,
            cv.cpnodeid, cv.name, orun.simdate, orun.simhour, cv.branchlabel, cv.ctglabel,
            orun.TOPOLOGYID, orun.RUNBEGINTIME
        FROM shift_factors.dbo.cpnode_shifts_view cv
        INNER JOIN AWOPF.DBO.OPFRUN orun ON cv.runid = orun.runid
        WHERE cv.PSENSHIFTID IN (
            SELECT PSENSHIFTID FROM AW.POPT.TOPOLOGYSHIFTSET WHERE TOPOLOGYSHIFTSETID={set_id}
        )
        AND cv.isomarketid = 6 AND cv.deadbus = 0
        {study_date_filter}
        QUALIFY ROW_NUMBER() OVER (PARTITION BY cv.PSENSHIFTID, cv.cpnodeid ORDER BY cv.RUNID) = 1
    ),
    DART_shifts AS (
        SELECT psd.psenshiftid, ps.psen, ps.cpnodeid, cp.name,
            b.branchName AS branchlabel, cdc.congContName AS ctglabel,
            TO_DATE(psd.extractionEnd) AS simdate, HOUR(psd.extractionEnd)+1 AS simhour
        FROM AW.dbo.psenShiftDef psd
        INNER JOIN AW.DBO.PSENSHIFT ps ON ps.psenshiftid = psd.psenshiftid
        INNER JOIN AW.DBO.congDefConstraint cd ON cd.congConstraintID = psd.congConstraintID
        INNER JOIN AW.DBO.congDefMonitor cdm ON cdm.congMontID = cd.congMontID
        INNER JOIN AW.DBO.congDefContingency cdc ON cdc.congContID = cd.congContID
        INNER JOIN AW.DBO.branchMonitored bm ON bm.branchMonitoredID = cdm.branchMonitoredId
        INNER JOIN AW.DBO.branch b ON b.branchID = bm.branchID
        INNER JOIN AW.DBO.CPNODE cp ON cp.cpnodeid = ps.cpnodeid
        WHERE psd.isoMarketID = 6 AND psd.psenShiftTypeId = 14
            AND psd.extractionEnd >= '{start_date}' AND psd.extractionEnd <= '{end_date}'
            AND b.branchName = '{branch_label}'
            AND cdc.congContName = '{ctg_label}'
        QUALIFY ROW_NUMBER() OVER (PARTITION BY psd.psenshiftid, ps.cpnodeid ORDER BY psd.psenshiftid) = 1
    )
    SELECT
        ss.psenshiftid, ds.psenshiftid AS dart_psenshiftid,
        ss.psens_raw, ss.direction AS study_direction,
        ds.psen AS dart_psen, ref.psen AS ref_psen,
        ss.cpnodeid, ss.name AS cpnode_name, ss.simdate, ss.simhour,
        ss.TOPOLOGYID, ss.RUNBEGINTIME
    FROM study_shifts ss
    INNER JOIN DART_shifts ds ON ss.branchlabel = ds.branchlabel
        AND ss.cpnodeid = ds.cpnodeid AND ss.ctglabel = ds.ctglabel
        AND ss.simdate = ds.simdate AND ss.simhour = ds.simhour
    INNER JOIN DART_shifts ref ON ss.simdate = ref.simdate AND ss.simhour = ref.simhour
        AND ref.psenshiftid = ds.psenshiftid AND ref.cpnodeid = {REFERENCE_CPNODEID}
    """
    df = query("AW", sql)
    df.columns = [c.lower() for c in df.columns]
    return df


def n_study_topologies(set_id: int) -> int:
    sql = f"SELECT COUNT(*) n FROM AW.POPT.TOPOLOGYSHIFTSET WHERE TOPOLOGYSHIFTSETID={set_id}"
    df = query("AW", sql)
    return int(df.iloc[0, 0]) if not df.empty else 0


def check_duplicates(set_id: int, branch_label: str, ctg_label: str, start_date: str, end_date: str) -> int:
    sql = f"""
    WITH DART_shifts AS (
        SELECT psd.psenshiftid, ps.cpnodeid,
            b.branchName AS branchlabel, cdc.congContName AS ctglabel,
            TO_DATE(psd.extractionEnd) AS simdate, HOUR(psd.extractionEnd)+1 AS simhour
        FROM AW.dbo.psenShiftDef psd
        INNER JOIN AW.DBO.PSENSHIFT ps ON ps.psenshiftid = psd.psenshiftid
        INNER JOIN AW.DBO.congDefConstraint cd ON cd.congConstraintID = psd.congConstraintID
        INNER JOIN AW.DBO.congDefMonitor cdm ON cdm.congMontID = cd.congMontID
        INNER JOIN AW.DBO.congDefContingency cdc ON cdc.congContID = cd.congContID
        INNER JOIN AW.DBO.branchMonitored bm ON bm.branchMonitoredID = cdm.branchMonitoredId
        INNER JOIN AW.DBO.branch b ON b.branchID = bm.branchID
        WHERE psd.isoMarketID = 6 AND psd.psenShiftTypeId = 14
            AND psd.extractionEnd >= '{start_date}' AND psd.extractionEnd <= '{end_date}'
            AND b.branchName = '{branch_label}'
            AND cdc.congContName = '{ctg_label}'
    )
    SELECT COUNT(*) n FROM (
        SELECT branchlabel, ctglabel, cpnodeid, simdate, simhour, COUNT(*) c
        FROM DART_shifts GROUP BY 1,2,3,4,5 HAVING COUNT(*) > 1
    )
    """
    df = query("AW", sql)
    return int(df.iloc[0, 0]) if not df.empty else 0


def compute_diffs(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df["diff_neg"] = -1 * df["psens_raw"] + df["ref_psen"] - df["dart_psen"]
    df["diff_pos"] = df["psens_raw"] + df["ref_psen"] - df["dart_psen"]
    return df


def sign_stats(df: pd.DataFrame, sign_col: str) -> dict:
    d = df[sign_col]
    ad = d.abs()
    signed = (df["psens_raw"] * (1 if sign_col == "diff_pos" else -1)) + df["ref_psen"]
    corr = np.corrcoef(signed, df["dart_psen"])[0, 1] if len(df) > 1 else np.nan
    return {
        "n_rows": len(df),
        "mae": ad.mean(),
        "rmse": np.sqrt((d**2).mean()),
        "bias": d.mean(),
        "p95_abs": ad.quantile(0.95),
        "max_abs": ad.max(),
        "share_gt_02": (ad > 0.02).mean(),
        "share_gt_05": (ad > 0.05).mean(),
        "corr": corr,
    }


def process_config(
    row: pd.Series, cache_dir: Path, use_cache: bool,
    date_from: str | None = None, date_to: str | None = None,
) -> dict:
    set_id = int(row["TOPOLOGYSHIFTSETID"])
    branch_label = str(row["BRANCHLABEL"])
    ctg_label = str(row["CTGLABEL"])
    direction = row["DIRECTION"]
    cache_suffix = f"_{date_from}_{date_to}" if (date_from or date_to) else ""
    cache_path = cache_dir / f"{set_id}{cache_suffix}.parquet"

    if use_cache and cache_path.exists():
        raw = pd.read_parquet(cache_path)
    else:
        start_date, end_date = get_date_range(set_id, date_from, date_to)
        if start_date is None:
            return {"TOPOLOGYSHIFTSETID": set_id, "BRANCHLABEL": branch_label, "CTGLABEL": ctg_label,
                    "status": "NO_STUDY_DATA"}
        raw = pull_joined_raw(set_id, branch_label, ctg_label, start_date, end_date, date_from, date_to)
        raw.to_parquet(cache_path)

    if raw.empty:
        return {"TOPOLOGYSHIFTSETID": set_id, "BRANCHLABEL": branch_label, "CTGLABEL": ctg_label,
                "DIRECTION": direction, "status": "NO_HOUR_OVERLAP"}

    dup_n = check_duplicates(set_id, branch_label, ctg_label, *get_date_range(set_id, date_from, date_to))

    df = compute_diffs(raw)
    neg = sign_stats(df, "diff_neg")
    pos = sign_stats(df, "diff_pos")
    best_sign = -1 if neg["mae"] <= pos["mae"] else 1
    best = neg if best_sign == -1 else pos
    other = pos if best_sign == -1 else neg

    n_topo_matched = int(raw["psenshiftid"].nunique())
    n_topo_total = n_study_topologies(set_id)

    default_sign = -1 * int(direction) if pd.notna(direction) else -1  # DIRECTION * -1 convention
    sign_agrees_default = best_sign == default_sign

    summary_row = {
        "TOPOLOGYSHIFTSETID": set_id,
        "BRANCHLABEL": branch_label,
        "CTGLABEL": ctg_label,
        "DIRECTION": direction,
        "status": "OK",
        "n_rows": best["n_rows"],
        "n_topologies_matched": n_topo_matched,
        "n_topologies_total": n_topo_total,
        "coverage": (n_topo_matched / n_topo_total) if n_topo_total else np.nan,
        "n_cpnodes": int(raw["cpnodeid"].nunique()),
        "simdate_min": raw["simdate"].min(),
        "simdate_max": raw["simdate"].max(),
        "best_sign": best_sign,
        "sign_agrees_default": sign_agrees_default,
        "mae": best["mae"],
        "rmse": best["rmse"],
        "bias": best["bias"],
        "p95_abs": best["p95_abs"],
        "max_abs": best["max_abs"],
        "share_gt_02": best["share_gt_02"],
        "share_gt_05": best["share_gt_05"],
        "corr": best["corr"],
        "other_sign_mae": other["mae"],
        "dup_rows_flagged": dup_n,
    }

    df["diff"] = df["diff_neg"] if best_sign == -1 else df["diff_pos"]
    df["abs_diff"] = df["diff"].abs()
    df["set_id"] = set_id
    df["branch_label"] = branch_label
    df["ctg_label"] = ctg_label

    per_topo = (
        df.groupby(["set_id", "psenshiftid", "simdate", "simhour"])
        .agg(n=("diff", "size"), mae=("abs_diff", "mean"), bias=("diff", "mean"), max_abs=("abs_diff", "max"))
        .reset_index()
    )
    per_cpnode = (
        df.groupby(["set_id", "cpnodeid", "cpnode_name"])
        .agg(
            n=("diff", "size"),
            mae=("abs_diff", "mean"),
            bias=("diff", "mean"),
            max_abs=("abs_diff", "max"),
            mean_study=("psens_raw", lambda s: s.mean() * best_sign),
            mean_dart=("dart_psen", "mean"),
            n_bad_02=("abs_diff", lambda s: (s > BAD_THRESHOLD).sum()),
        )
        .reset_index()
    )

    return {
        "summary": summary_row,
        "per_topology": per_topo,
        "per_cpnode": per_cpnode,
    }


def classify(summary_row: dict, per_topology: pd.DataFrame, per_cpnode: pd.DataFrame) -> str:
    mae = summary_row["mae"]
    max_abs = summary_row["max_abs"]
    bias = summary_row["bias"]
    if mae < 0.005 and max_abs < 0.02:
        return "OK"

    n_bad_total = per_cpnode["n_bad_02"].sum()
    if n_bad_total > 0:
        top10_cp_bad = per_cpnode.sort_values("n_bad_02", ascending=False).head(10)["n_bad_02"].sum()
        if top10_cp_bad / n_bad_total >= 0.90:
            return "LOCALIZED_NODES"

    n_topo = len(per_topology)
    if n_topo > 0:
        n_bad_topo_thresh = max(1, int(np.ceil(0.10 * n_topo)))
        bad_topo_rows = per_topology.assign(n_bad=lambda d: (d["max_abs"] > BAD_THRESHOLD))
        n_bad_topo_total = bad_topo_rows["n_bad"].sum()
        if n_bad_topo_total > 0:
            top_bad = bad_topo_rows.sort_values("max_abs", ascending=False).head(n_bad_topo_thresh)
            frac = top_bad["n_bad"].sum() / max(n_bad_topo_total, 1)
            if frac >= 0.50 and n_bad_topo_thresh <= max(1, int(0.10 * n_topo)):
                return "LOCALIZED_TOPOLOGIES"

    if abs(bias) > 0.5 * mae and mae >= 0.005:
        return "SYSTEMATIC"
    return "DIFFUSE"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--created-after", type=str, required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sets", type=str, default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--date-from", type=str, default=None)
    ap.add_argument("--date-to", type=str, default=None)
    ap.add_argument("--out-subdir", type=str, default=None)
    args = ap.parse_args()

    base_dir = Path(__file__).resolve().parent / "output" / "validation_shift_compare" / str(args.study)
    out_dir = base_dir / args.out_subdir if args.out_subdir else base_dir
    cache_dir = base_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    configs = get_configs(args.study, args.created_after)
    log.info(f"{len(configs)} configs for study {args.study}")

    skipped = []
    work = configs[configs["INTERFACENAME"].notna()]
    for _, r in work.iterrows():
        skipped.append({"TOPOLOGYSHIFTSETID": r["TOPOLOGYSHIFTSETID"], "reason": "SKIPPED_INTERFACE"})
    configs = configs[configs["INTERFACENAME"].isna()]
    configs = configs[configs["CTGLABEL"].notna()]

    if args.sets:
        ids = {int(x) for x in args.sets.split(",")}
        configs = configs[configs["TOPOLOGYSHIFTSETID"].isin(ids)]
    if args.limit:
        configs = configs.head(args.limit)

    use_cache = not args.no_cache
    summaries = []
    per_topo_all = []
    per_cpnode_all = []

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {
            ex.submit(process_config, row, cache_dir, use_cache, args.date_from, args.date_to): row
            for _, row in configs.iterrows()
        }
        for fut in as_completed(futs):
            row = futs[fut]
            set_id = int(row["TOPOLOGYSHIFTSETID"])
            try:
                result = fut.result()
            except Exception as e:
                log.error(f"set {set_id} FAILED: {e}")
                skipped.append({"TOPOLOGYSHIFTSETID": set_id, "reason": f"ERROR: {e}"})
                continue

            if result.get("status") in ("NO_HOUR_OVERLAP", "NO_STUDY_DATA"):
                skipped.append({"TOPOLOGYSHIFTSETID": set_id, "reason": result["status"]})
                log.info(f"set {set_id} {row['BRANCHLABEL']}/{row['CTGLABEL']}: {result['status']}")
                continue

            s = result["summary"]
            pt = result["per_topology"]
            pc = result["per_cpnode"]
            s["error_pattern"] = classify(s, pt, pc)
            summaries.append(s)
            per_topo_all.append(pt)
            per_cpnode_all.append(pc)
            log.info(
                f"set {set_id} {s['BRANCHLABEL']}/{s['CTGLABEL']}: sign={s['best_sign']} "
                f"mae={s['mae']:.4f} max={s['max_abs']:.4f} pattern={s['error_pattern']}"
            )

    runtime = time.time() - t0
    log.info(f"Done in {runtime:.1f}s: {len(summaries)} processed, {len(skipped)} skipped")

    summary_df = pd.DataFrame(summaries).sort_values("mae", ascending=False) if summaries else pd.DataFrame()
    per_topo_df = pd.concat(per_topo_all, ignore_index=True) if per_topo_all else pd.DataFrame()
    per_cpnode_df = pd.concat(per_cpnode_all, ignore_index=True) if per_cpnode_all else pd.DataFrame()
    skipped_df = pd.DataFrame(skipped)

    summary_df.to_csv(out_dir / "summary.csv", index=False)
    per_topo_df.to_parquet(out_dir / "per_topology.parquet")
    per_cpnode_df.to_parquet(out_dir / "per_cpnode.parquet")
    skipped_df.to_csv(out_dir / "skipped.csv", index=False)

    log.info(f"Wrote outputs to {out_dir}")
    if not summary_df.empty:
        print(summary_df.head(15)[["BRANCHLABEL", "CTGLABEL", "best_sign", "mae", "max_abs", "error_pattern"]])


if __name__ == "__main__":
    main()
