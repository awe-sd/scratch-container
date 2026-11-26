"""
July-2026 hot / high-net-load days -> RT congestion watch-list for August.

Ranks each July-2026 operating day by PEAK effective net load
(ercot_all_ld - wind - solar), then for the hottest days lists every
transmission constraint that BOUND in real time (congHrPrice priceTypeID=2 RT,
congTypeID=1 BINDING). Output = a plain list of (day -> constraints seen) plus a
recurring-constraint rollup (constraints that showed up on multiple hot days are
the ones most likely to re-appear, harder, under higher August temps).

Everything is keyed on the ERCOT operating day via awDateID (awDate.date), so
load / wind / solar / congestion align without timezone skew. Physical
constraints are de-duplicated across naming variants by parsing
isoConstraintName -> elem|contingency (analysis_common.parse_constraint_names).

READ-ONLY. Caches July pulls to analytics/data/jul26_*.parquet.
"""
import sys
from pathlib import Path

import awconnect
import pandas as pd
from awconnect import db

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from analysis_common import parse_constraint_names  # noqa: E402

DATA = SCRIPTS.parents[0] / "data"
OUT = SCRIPTS.parents[0] / "output"
DATA.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

JUL = ("2026-07-01", "2026-07-16")   # operating-day window (inclusive), month-to-date
TOP_N_DAYS = 8                        # how many hottest days to list constraints for


def _cache(name, sql):
    f = DATA / f"{name}.parquet"
    if f.exists():
        return pd.read_parquet(f)
    df = db.getDfFromAwDb(sql)
    df.to_parquet(f, index=False)
    print(f"[fetch] {name}: {len(df):,} rows")
    return df


def fetch_net_load():
    ld = _cache("jul26_load",
                f"SELECT date, he AS HE, ercot_all_ld FROM AW.dbo.ercotLoadView "
                f"WHERE date >= '{JUL[0]}' AND date <= '{JUL[1]}'")
    wind = _cache("jul26_wind",
                  f"SELECT d.date, w.HE, w.windGen, w.priceTypeID FROM AW.dbo.windGenAct w "
                  f"JOIN AW.dbo.awDate d ON d.awDateID = w.awDateID "
                  f"WHERE w.isoZoneID = 67 AND d.date >= '{JUL[0]}' AND d.date <= '{JUL[1]}'")
    solar = _cache("jul26_solar",
                   f"SELECT d.date, s.HE, s.solarGen, s.priceTypeID FROM AW.dbo.solarGenAct s "
                   f"JOIN AW.dbo.awDate d ON d.awDateID = s.awDateID "
                   f"WHERE s.isoZoneID = 67 AND d.date >= '{JUL[0]}' AND d.date <= '{JUL[1]}'")
    for df in (ld, wind, solar):
        df["date"] = pd.to_datetime(df["date"])
    # actual flavor = the priceTypeID with the most rows
    wind = wind[wind.priceTypeID == wind.groupby("priceTypeID").size().idxmax()]
    solar = solar[solar.priceTypeID == solar.groupby("priceTypeID").size().idxmax()]
    df = (ld.merge(wind[["date", "HE", "windGen"]], on=["date", "HE"], how="left")
            .merge(solar[["date", "HE", "solarGen"]], on=["date", "HE"], how="left"))
    for c in ("ercot_all_ld", "windGen", "solarGen"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["net_load"] = df["ercot_all_ld"] - df["windGen"].fillna(0) - df["solarGen"].fillna(0)
    return df


def fetch_binding():
    cong = _cache("jul26_binding_ercot",
                  f"SELECT d.date, hp.HE, hp.congConstraintID, hp.Price, "
                  f"       hp.ConstraintValue, hp.ConstraintLimit "
                  f"FROM AW.dbo.congHrPrice hp JOIN AW.dbo.awDate d ON d.awDateID = hp.awDateID "
                  f"WHERE hp.isomarketid = 6 AND hp.priceTypeID = 2 AND hp.congTypeID = 1 "
                  f"AND d.date >= '{JUL[0]}' AND d.date <= '{JUL[1]}'")
    defc = _cache("jul26_defc",
                  "SELECT congConstraintID, MIN(isoConstraintName) AS isoConstraintName "
                  "FROM AW.dbo.congDefConstraint GROUP BY congConstraintID")
    cong["date"] = pd.to_datetime(cong["date"])
    cong["Price"] = pd.to_numeric(cong["Price"], errors="coerce")
    cong = cong.merge(defc, on="congConstraintID", how="left")
    cong = parse_constraint_names(cong)   # adds elem, cont, code, ckey
    return cong


def main():
    awconnect.configure("read_only")

    nl = fetch_net_load()
    daily = (nl.groupby("date")
               .agg(peak_net_load=("net_load", "max"),
                    peak_load=("ercot_all_ld", "max")).reset_index()
               .sort_values("peak_net_load", ascending=False))
    daily["rank"] = range(1, len(daily) + 1)
    print("\n=== July-2026 days ranked by PEAK net load (MW) ===")
    print(daily.assign(day=daily["date"].dt.strftime("%a %m-%d"))
              [["rank", "day", "peak_net_load", "peak_load"]]
              .to_string(index=False, formatters={"peak_net_load": "{:,.0f}".format,
                                                  "peak_load": "{:,.0f}".format}))

    hot_days = daily.head(TOP_N_DAYS)["date"].tolist()
    cong = fetch_binding()
    hot = cong[cong["date"].isin(hot_days)].copy()

    # per (day, physical constraint): hours bound + worst shadow price
    per = (hot.groupby(["date", "code", "elem", "cont"])
              .agg(hours_bound=("HE", "nunique"),
                   max_shadow=("Price", "max"),
                   mean_shadow=("Price", "mean")).reset_index())
    per = per.merge(daily[["date", "rank", "peak_net_load"]], on="date")
    per = per.sort_values(["rank", "max_shadow"], ascending=[True, False])
    per["day"] = per["date"].dt.strftime("%a %m-%d")

    list_cols = ["day", "peak_net_load", "code", "elem", "cont", "hours_bound", "max_shadow"]
    csv1 = OUT / "july_hot_days_constraints.csv"
    per[["date"] + list_cols[1:]].to_csv(csv1, index=False)

    print(f"\n=== Constraints that BOUND (RT) on the top {TOP_N_DAYS} net-load days ===")
    for d in sorted(hot_days):
        sub = per[per["date"] == d].sort_values("max_shadow", ascending=False)
        if sub.empty:
            continue
        r = int(sub["rank"].iloc[0]); pnl = sub["peak_net_load"].iloc[0]
        print(f"\n  {d:%a %Y-%m-%d}  (net-load rank #{r}, peak {pnl:,.0f} MW) — "
              f"{sub['code'].nunique()} constraints:")
        for _, x in sub.iterrows():
            print(f"      {x['code']:<10} {x['elem']:<34} CONT:{x['cont']:<10} "
                  f"{x['hours_bound']:>2}h  max ${x['max_shadow']:>8,.0f}")

    # recurring rollup: constraints across MULTIPLE hot days = August watch-list
    roll = (per.groupby(["code", "elem", "cont"])
               .agg(hot_days_seen=("date", "nunique"),
                    total_hours=("hours_bound", "sum"),
                    worst_shadow=("max_shadow", "max"),
                    days=("day", lambda s: ", ".join(sorted(set(s))))).reset_index()
               .sort_values(["hot_days_seen", "worst_shadow"], ascending=False))
    csv2 = OUT / "july_recurring_constraints_watchlist.csv"
    roll.to_csv(csv2, index=False)

    print(f"\n=== RECURRING constraints (seen on >=2 of the top {TOP_N_DAYS} hot days) — "
          "August watch-list ===")
    rec = roll[roll["hot_days_seen"] >= 2]
    for _, x in rec.iterrows():
        print(f"  {x['code']:<10} {x['elem']:<34} CONT:{x['cont']:<10} "
              f"{x['hot_days_seen']}d {x['total_hours']:>3}h  worst ${x['worst_shadow']:>8,.0f}  [{x['days']}]")
    print(f"\n-> {csv1}\n-> {csv2}")
    print(f"\n{per['code'].nunique()} distinct constraints across the top {TOP_N_DAYS} days; "
          f"{len(rec)} recur on >=2 hot days.")


if __name__ == "__main__":
    main()
