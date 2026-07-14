"""
Analysis 1: which constraints were active/monitored on the highest net-load
days of the recent summer, and which are candidates to blow up in August.

Method
 1. Rank summer-2026 days by daily PEAK hourly net load (load - wind - solar).
 2. Aggregate congHrPrice (ERCOT) per constraint-group (ckey = monitored
    element + contingency, deduping ERCOT naming variants) per day:
    binding hours, max/sum shadow price, split RT vs DA by priceTypeID.
 3. Score constraints on:
      - activity concentrated in the top net-load days (lift vs other days)
      - magnitude (max SP, SP-hours) on those days
      - Aug-2025 prior (did it bind last August?)
      - recent trend (last 3 weeks vs May/June)
      - analyst records (ercotCongConstRecord Bullish notes in 2026)
 4. Emit output/august_watchlist.csv + supporting tables.
"""
import pandas as pd

from analysis_common import (
    AUG_25, OUT_DIR, SUMMER_26, between, hourly_net_load, load,
    parse_constraint_names,
)

TOP_N_DAYS = 15


def main():
    pd.set_option("display.width", 250)

    # ---- net load ranking -------------------------------------------------
    nl = hourly_net_load()
    s26 = between(nl, "date", *SUMMER_26)
    daily = (
        s26.groupby("date")
        .agg(peak_load=("ercot_all_ld", "max"), peak_net_load=("net_load", "max"))
        .sort_values("peak_net_load", ascending=False)
    )
    top_days = daily.head(TOP_N_DAYS)
    top_set = set(top_days.index)
    daily.to_csv(OUT_DIR / "summer26_daily_load_ranking.csv")
    print(f"=== Top {TOP_N_DAYS} summer-2026 days by peak net load ===")
    print(top_days.to_string())

    # ---- constraint activity ---------------------------------------------
    hp = load("congHrPrice_ercot_summers")
    hp["date"] = pd.to_datetime(hp["date"])
    defc = parse_constraint_names(load("congDefConstraint_ercot"))
    key = defc.set_index("congConstraintID")[["ckey", "elem", "cont", "code"]]
    hp = hp.join(key, on="congConstraintID")

    pt = load("lookup_priceType")
    print("\n--- priceType lookup ---")
    print(pt.to_string())
    ct = load("lookup_congType")
    print("--- congType lookup ---")
    print(ct.to_string())

    # binding, priced rows only
    hp = hp[hp["congTypeID"] == 1]
    hp["Price"] = pd.to_numeric(hp["Price"], errors="coerce")
    hp = hp[hp["Price"] > 0]

    # per constraint-group per day per priceType
    day = (
        hp.groupby(["ckey", "date", "priceTypeID"])
        .agg(bind_hours=("HE", "nunique"), max_sp=("Price", "max"), sp_sum=("Price", "sum"))
        .reset_index()
    )
    day.to_csv(OUT_DIR / "constraint_daily_activity.csv", index=False)

    d26 = between(day, "date", *SUMMER_26)
    n_top, n_other = len(top_set), d26["date"].nunique() - len(top_set)
    d26 = d26.assign(is_top=d26["date"].isin(top_set))

    g = (
        d26.groupby("ckey")
        .apply(
            lambda x: pd.Series({
                "days_top": x.loc[x.is_top, "date"].nunique(),
                "days_other": x.loc[~x.is_top, "date"].nunique(),
                "bind_hours_top": x.loc[x.is_top, "bind_hours"].sum(),
                "max_sp_top": x.loc[x.is_top, "max_sp"].max(),
                "sp_sum_top": x.loc[x.is_top, "sp_sum"].sum(),
                "max_sp_s26": x["max_sp"].max(),
                "sp_sum_s26": x["sp_sum"].sum(),
                "days_s26": x["date"].nunique(),
                "last_active": x["date"].max(),
            }),
            include_groups=False,
        )
        .reset_index()
    )
    g["p_top"] = g["days_top"] / n_top
    g["p_other"] = g["days_other"] / max(n_other, 1)
    g["netload_lift"] = (g["p_top"] + 0.01) / (g["p_other"] + 0.01)

    # Aug 2025 prior
    a25 = between(day, "date", *AUG_25).groupby("ckey").agg(
        aug25_days=("date", "nunique"), aug25_max_sp=("max_sp", "max"),
        aug25_sp_sum=("sp_sum", "sum"),
    )
    g = g.join(a25, on="ckey")

    # recent trend: last 21 days vs before, within summer 26
    cut = pd.Timestamp(SUMMER_26[1]) - pd.Timedelta(days=21)
    recent = d26[d26["date"] > cut].groupby("ckey")["sp_sum"].sum()
    earlier = d26[d26["date"] <= cut].groupby("ckey")["sp_sum"].sum()
    g["sp_sum_recent21d"] = g["ckey"].map(recent).fillna(0)
    g["sp_sum_earlier"] = g["ckey"].map(earlier).fillna(0)

    # analyst records (2026): join via constraint id -> ckey
    for rec_name in ["ercotCongConstRecord", "ercot_sppCongConstRecord"]:
        try:
            rec = load(rec_name)
            rec["Date"] = pd.to_datetime(rec["Date"])
            rec = rec[rec["Date"] >= "2026-01-01"].copy()
            rec["congConstraintID"] = pd.to_numeric(rec["congConstraintID"], errors="coerce")
            rec = rec.join(key, on="congConstraintID")
            cnt = rec.groupby("ckey").agg(**{
                f"{rec_name}_n26": ("Date", "count"),
            })
            g = g.join(cnt, on="ckey")
        except Exception as e:
            print(f"[warn] {rec_name}: {e}")

    # score: emphasize top-day concentration + magnitude + august prior
    import numpy as np
    g["score"] = (
        g["days_top"].clip(upper=10) * 2.0
        + np.log1p(g["sp_sum_top"].fillna(0)) * 1.5
        + np.log1p(g["netload_lift"].clip(upper=20)) * 3.0
        + np.log1p(g["aug25_sp_sum"].fillna(0)) * 1.0
        + np.log1p(g["sp_sum_recent21d"]) * 0.75
    )
    g = g.sort_values("score", ascending=False)

    # attach a representative display name
    rep = defc.drop_duplicates("ckey").set_index("ckey")["isoConstraintName"]
    g["example_name"] = g["ckey"].map(rep)
    g.to_csv(OUT_DIR / "august_watchlist.csv", index=False)

    print("\n=== TOP 25 August watch-list candidates ===")
    cols = ["ckey", "days_top", "days_s26", "netload_lift", "max_sp_top",
            "sp_sum_top", "aug25_days", "aug25_max_sp", "sp_sum_recent21d", "score"]
    print(g.head(25)[cols].to_string(index=False))


if __name__ == "__main__":
    main()
