"""Task 07 (NCL exclusion) end-to-end runner.

Chains: ncl_stations -> pull_station_load -> organic_load -> refit size index
on the organic series -> print the total-vs-organic deliverable table ->
rolling backtest comparison (NCENT, walls 2022-2024) proving/disproving the
hypothesis that organic growth error collapses toward COAST/SCENT levels.

No changes to size_index.py or backtest.py: both already take a load_hourly-
shaped frame as a parameter, so the organic frame (weather_zone, ts_local,
load_mw, event_flag -- same schema as load_hourly, just organic load_mw) is a
drop-in substitute.

Run: uv run python load-forecast/scripts/run_task07.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import backtest as bt  # noqa: E402
import config as cfg  # noqa: E402
import ncl_stations as ns  # noqa: E402
import organic_load as ol  # noqa: E402
import pull_station_load as psl  # noqa: E402
import size_index as si  # noqa: E402

ORGANIC_SIZE_INDEX_PATH = cfg.DERIVED_DIR / "size_index_organic.parquet"
BACKTEST_ZONE = "NCENT"
BACKTEST_WALLS = [2022, 2023, 2024]
# task-file reference numbers for the TOTAL series (approx) -- printed for
# context only. 2026-08-15b: verified against output/experiments.csv --
# the 2022 figure (-0.71, tag "baseline") is timestamped 21:59:43 on
# 2026-08-14, BEFORE zone_weather_hourly.parquet was regenerated at
# 22:11:12 that day to pick up the ACS->PEP population-source swap; every
# artifact generated after that regeneration (output/backtest_rolling.csv,
# 22:23:04) shows +0.43 for the same fold. -0.71 is therefore a stale,
# pre-regeneration number, not a target this pipeline has drifted from --
# it is NEVER used in delta_pp below, which always compares organic vs a
# freshly-run total-series fold from the SAME run.
REFERENCE_TOTAL_GROWTH_ERR_PP = {2022: -0.71, 2023: -1.25, 2024: -3.13}


def build_deliverable_table(total_index: pd.DataFrame, organic_index: pd.DataFrame) -> pd.DataFrame:
    """Per zone x year: total vs organic normalized_gwh, y/y growth %, and
    NCL share % (= (total-organic)/total). fitted vs extrapolated `source`
    is carried through and checked for alignment between the two series --
    growth % is computed on the concatenated fitted+extrapolated series
    (continuous by construction) but a source mismatch would mean the two
    fits disagree about which years are fitted, which is worth a loud
    warning rather than a silently blended number."""
    t = total_index.rename(columns={"normalized_gwh": "total_gwh"})
    o = organic_index.rename(columns={"normalized_gwh": "organic_gwh", "source": "organic_source"})
    m = t.merge(
        o[["weather_zone", "year", "organic_gwh", "organic_source"]],
        on=["weather_zone", "year"], how="inner",
    )

    mismatch = m.loc[m["source"] != m["organic_source"]]
    if len(mismatch):
        print(
            f"WARNING: {len(mismatch)} (zone,year) rows have mismatched fitted/extrapolated "
            "source between total and organic fits -- growth % below spans regimes there:"
        )
        print(mismatch[["weather_zone", "year", "source", "organic_source"]].to_string(index=False))

    m = m.sort_values(["weather_zone", "year"]).reset_index(drop=True)
    m["total_yoy_pct"] = m.groupby("weather_zone")["total_gwh"].pct_change() * 100
    m["organic_yoy_pct"] = m.groupby("weather_zone")["organic_gwh"].pct_change() * 100
    m["ncl_share_pct"] = 100 * (m["total_gwh"] - m["organic_gwh"]) / m["total_gwh"]

    cols = [
        "weather_zone", "year", "source", "total_gwh", "organic_gwh",
        "total_yoy_pct", "organic_yoy_pct", "ncl_share_pct",
    ]
    return m[cols].round(2)


def main() -> None:
    print("################ STEP 1: ncl_stations ################")
    ns.main()

    print("\n################ STEP 2: pull_station_load ################")
    psl.main()

    print("\n################ STEP 3: organic_load ################")
    ol.main()

    print("\n################ STEP 4: refit size index on organic ################")
    organic = pd.read_parquet(ol.ORGANIC_PATH)[["weather_zone", "ts_local", "load_mw", "event_flag"]]
    zone_weather = pd.read_parquet(cfg.DERIVED_DIR / "zone_weather_hourly.parquet")
    load_hourly = pd.read_parquet(cfg.DERIVED_DIR / "load_hourly.parquet")

    daily_organic = {z: si.build_daily(organic, zone_weather, z) for z in cfg.ZONES}
    daily_total = {z: si.build_daily(load_hourly, zone_weather, z) for z in cfg.ZONES}

    organic_index, organic_diag = si.build_size_index(
        daily_organic, through_year=2028, out_path=ORGANIC_SIZE_INDEX_PATH
    )
    total_index = pd.read_parquet(cfg.DERIVED_DIR / "size_index.parquet")
    print(f"wrote {ORGANIC_SIZE_INDEX_PATH}")

    print("\n=== DELIVERABLE TABLE: total vs organic normalized energy, growth %, NCL share % ===")
    deliverable = build_deliverable_table(total_index, organic_index)
    print(deliverable.to_string(index=False))
    deliverable_path = cfg.PROJECT_ROOT / "output" / "task07_organic_table.csv"
    deliverable_path.parent.mkdir(parents=True, exist_ok=True)
    deliverable.to_csv(deliverable_path, index=False)
    print(f"wrote {deliverable_path}")

    print(f"\n################ STEP 5: rolling backtest, {BACKTEST_ZONE} walls {BACKTEST_WALLS} ################")
    rows = []
    for wall in BACKTEST_WALLS:
        total_fold = bt.run_fold(BACKTEST_ZONE, wall, load_hourly, zone_weather, daily_total[BACKTEST_ZONE])
        organic_fold = bt.run_fold(BACKTEST_ZONE, wall, organic, zone_weather, daily_organic[BACKTEST_ZONE])
        total_ok = total_fold.get("status") == "ok"
        organic_ok = organic_fold.get("status") == "ok"
        rows.append({
            "wall_year": wall,
            "target_year": wall + 1,
            "total_growth_err_pp": total_fold.get("growth_err_pp") if total_ok else None,
            "organic_growth_err_pp": organic_fold.get("growth_err_pp") if organic_ok else None,
            "delta_pp": (
                round(organic_fold["growth_err_pp"] - total_fold["growth_err_pp"], 2)
                if total_ok and organic_ok else None
            ),
            "reference_total_growth_err_pp": REFERENCE_TOTAL_GROWTH_ERR_PP.get(wall),
        })
    cmp_df = pd.DataFrame(rows)
    print(cmp_df.to_string(index=False))
    print(
        "\n(reference_total_growth_err_pp is the approx, KNOWN-STALE total-series number quoted "
        "in tasks/07_ncl_exclusion.md -- see REFERENCE_TOTAL_GROWTH_ERR_PP's comment for why the "
        "2022 figure does not reproduce (pre-dates the 2026-08-14 ACS->PEP crosswalk swap). "
        "total_growth_err_pp above is freshly recomputed THIS run from the current code+data, and "
        "is the ONLY number delta_pp is measured against -- the stale reference never enters that "
        "subtraction, so delta_pp is internally valid regardless of the reference mismatch.)"
    )
    cmp_df["total_err_abs"] = cmp_df["total_growth_err_pp"].abs()
    cmp_df["organic_err_abs"] = cmp_df["organic_growth_err_pp"].abs()
    cmp_df["magnitude_improved"] = cmp_df["organic_err_abs"] < cmp_df["total_err_abs"]
    print(
        "\nHypothesis check (organic growth error MAGNITUDE should shrink vs total if NCL "
        "exclusion explains NCENT's under-forecast) -- reported as observed, not pre-judged:"
    )
    print(cmp_df[["wall_year", "total_err_abs", "organic_err_abs", "delta_pp", "magnitude_improved"]].to_string(index=False))
    backtest_path = cfg.PROJECT_ROOT / "output" / "task07_organic_backtest.csv"
    cmp_df.to_csv(backtest_path, index=False)
    print(f"wrote {backtest_path}")
    n_improved = int(cmp_df["magnitude_improved"].sum())
    print(
        f"\n{n_improved}/{len(cmp_df)} folds show a smaller organic error magnitude than total. "
        "Read this alongside the deliverable table's ncl_share_pct above: a small/large "
        "delta_pp here is only interpretable in light of how much of NCENT's zonal energy the "
        "gated NCL set actually represents in the relevant years -- a small NCL share bounds how "
        "much delta_pp COULD move even if the hypothesis were fully correct, independent of "
        "whether it moved in the tested direction."
    )


if __name__ == "__main__":
    main()
