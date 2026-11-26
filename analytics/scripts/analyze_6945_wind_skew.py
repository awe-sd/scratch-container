"""
Analysis 2: West wind vs Panhandle wind skew on constraint 6945
(MGSES 345kV -> CATSW 345kV), all contingency variants.

Question (user): is 6945 binding skewed toward high or low West wind
relative to Panhandle wind — i.e. does it need the "high West load +
high Panhandle wind" pattern?

Method: hourly join of 6945 binding/shadow-price hours against
ercotWindRegionHourly actuals (West, Panhandle) and West/Far-West
weather-zone load, summer 2026. Report:
  - conditional means (binding vs non-binding hours, matched to the same
    date range and hours-of-day where 6945 ever binds)
  - tercile grid P(bind) over West x Panhandle wind
  - P(bind) by West-load tercile x Panhandle-minus-West wind spread
  - rank correlations of RT shadow price vs each driver
"""
import numpy as np
import pandas as pd

from analysis_common import (
    OUT_DIR, SUMMER_26, between, hourly_net_load, load,
    parse_constraint_names, wind_by_region,
)

ELEM = "MGSES:345KV-CATSW:345KV"
CODE_PREFIX = "6945"


def terc(s):
    return pd.qcut(s, 3, labels=["low", "mid", "high"], duplicates="drop")


def main():
    pd.set_option("display.width", 250)

    defc = parse_constraint_names(load("congDefConstraint_ercot"))
    target = defc[(defc["elem"] == ELEM) & (defc["code"].str.startswith(CODE_PREFIX))]
    ids = set(target["congConstraintID"])
    print(f"6945 constraint-id variants: {len(ids)} "
          f"(contingencies: {sorted(target['cont'].unique())})")

    hp = load("congHrPrice_ercot_summers")
    hp["date"] = pd.to_datetime(hp["date"])
    hp = hp[hp["congConstraintID"].isin(ids)].copy()
    hp = hp.join(defc.set_index("congConstraintID")["cont"], on="congConstraintID")
    hp["Price"] = pd.to_numeric(hp["Price"], errors="coerce")

    # hourly binding table (any contingency), RT and DA separately
    bind = (
        hp[hp["Price"] > 0]
        .groupby(["date", "HE", "priceTypeID"])
        .agg(sp=("Price", "max"), n_conts=("cont", "nunique"))
        .reset_index()
        .pivot_table(index=["date", "HE"], columns="priceTypeID",
                     values=["sp", "n_conts"], aggfunc="max")
    )
    bind.columns = [f"{a}_{'DA' if b == 1 else 'RT'}" for a, b in bind.columns]
    bind = bind.reset_index()

    # drivers
    nl = hourly_net_load()
    wr = wind_by_region()
    df = (
        between(nl, "date", *SUMMER_26)
        .merge(wr, on=["date", "HE"], how="left")
        .merge(bind, on=["date", "HE"], how="left")
    )
    df["west_load"] = pd.to_numeric(df["wz_west_ld"], errors="coerce") + pd.to_numeric(
        df["wz_far_west_ld"], errors="coerce")
    df["bind_rt"] = df.get("sp_RT").notna() if "sp_RT" in df else False
    df["bind_da"] = df.get("sp_DA").notna() if "sp_DA" in df else False
    df["bind_any"] = df["bind_rt"] | df["bind_da"]
    df["pan_minus_west"] = df["wind_panhandle"] - df["wind_west"]
    df = df.dropna(subset=["wind_west", "wind_panhandle"])

    # restrict comparison universe to hours-of-day where 6945 ever binds
    hrs = sorted(df.loc[df["bind_any"], "HE"].unique())
    uni = df[df["HE"].isin(hrs)].copy()
    print(f"\nSummer-26 hours in universe: {len(uni):,}  "
          f"binding (any): {int(uni['bind_any'].sum()):,} "
          f"(RT: {int(uni['bind_rt'].sum()):,}, DA: {int(uni['bind_da'].sum()):,})  "
          f"hours-of-day: {hrs}")

    # conditional means
    stats = uni.groupby("bind_any")[
        ["wind_west", "wind_panhandle", "pan_minus_west", "west_load", "net_load", "ercot_all_ld"]
    ].agg(["mean", "median"]).round(1)
    print("\n=== driver stats: binding vs non-binding hours ===")
    print(stats.to_string())
    stats.to_csv(OUT_DIR / "c6945_binding_vs_not_stats.csv")

    # z-scored skew (how many sds each driver moves when binding)
    z = {}
    for c in ["wind_west", "wind_panhandle", "pan_minus_west", "west_load", "net_load"]:
        mu, sd = uni[c].mean(), uni[c].std()
        z[c] = (uni.loc[uni.bind_any, c].mean() - mu) / sd
    print("\n=== skew of binding hours vs all hours (in sd units) ===")
    print(pd.Series(z).round(3).to_string())

    # tercile grid: P(bind) over west x panhandle wind
    uni["west_t"] = terc(uni["wind_west"])
    uni["pan_t"] = terc(uni["wind_panhandle"])
    grid = uni.pivot_table(index="pan_t", columns="west_t", values="bind_any",
                           aggfunc="mean", observed=True).round(3)
    cnt = uni.pivot_table(index="pan_t", columns="west_t", values="bind_any",
                          aggfunc="size", observed=True)
    print("\n=== P(bind) grid: rows=Panhandle wind tercile, cols=West wind tercile ===")
    print(grid.to_string())
    print("--- cell counts ---")
    print(cnt.to_string())
    grid.to_csv(OUT_DIR / "c6945_pbind_grid_pan_x_west.csv")

    # west-load x (pan - west) spread
    uni["wl_t"] = terc(uni["west_load"])
    uni["spread_t"] = terc(uni["pan_minus_west"])
    grid2 = uni.pivot_table(index="wl_t", columns="spread_t", values="bind_any",
                            aggfunc="mean", observed=True).round(3)
    print("\n=== P(bind) grid: rows=West-zone load tercile, cols=(Panhandle - West wind) tercile ===")
    print(grid2.to_string())
    grid2.to_csv(OUT_DIR / "c6945_pbind_grid_westload_x_spread.csv")

    # correlations with RT shadow price among binding RT hours
    rt = uni[uni["bind_rt"]]
    if len(rt) >= 10:
        cors = rt[["sp_RT", "wind_west", "wind_panhandle", "pan_minus_west",
                   "west_load", "net_load"]].corr(method="spearman")["sp_RT"].drop("sp_RT")
        print("\n=== Spearman corr of RT shadow price vs drivers (binding RT hours) ===")
        print(cors.round(3).to_string())

    # per-contingency binding counts (context)
    per_cont = (
        hp[hp["Price"] > 0].groupby(["cont", "priceTypeID"])
        .agg(hours=("HE", "size"), max_sp=("Price", "max"), sp_sum=("Price", "sum"))
        .round(1)
    )
    print("\n=== 6945 binding by contingency / market ===")
    print(per_cont.to_string())
    per_cont.to_csv(OUT_DIR / "c6945_by_contingency.csv")

    uni.to_csv(OUT_DIR / "c6945_hourly_universe.csv", index=False)


if __name__ == "__main__":
    main()
