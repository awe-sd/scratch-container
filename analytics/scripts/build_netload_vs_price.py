"""
Effective net load vs real-time energy price, last summer (Jun-Sep 2025).

net load = ERCOT load − wind − solar (hourly, from analysis_common).
energy price = dbo.ercotLambda.SystemLambda (RT system marginal energy price,
5-min SCED -> averaged to the hour). Join on (date, hour-ending).

Scatter of net load (x) vs price (y), colored by hour-of-day, with a
binned-median price curve overlaid. Read-only pull -> parquet -> plotly HTML.
"""
import sys
from pathlib import Path

import awconnect
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from awconnect import db

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_common import hourly_net_load, between  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "output"
OUT.mkdir(parents=True, exist_ok=True)
SUMMER = ("2025-06-01", "2025-09-30")


def fetch_lambda():
    f = DATA / "ercotLambda_summer25.parquet"
    if f.exists():
        return pd.read_parquet(f)
    awconnect.configure("read_only")
    df = db.getDfFromAwDb(
        "SELECT SCEDTimestamp, SystemLambda FROM dbo.ercotLambda "
        f"WHERE SCEDTimestamp >= '{SUMMER[0]} 00:00' AND SCEDTimestamp < '2025-10-01 00:00'")
    df.to_parquet(f, index=False)
    print(f"[fetch] {len(df):,} lambda rows")
    return df


def main():
    lam = fetch_lambda()
    lam["SCEDTimestamp"] = pd.to_datetime(lam["SCEDTimestamp"])
    lam["SystemLambda"] = pd.to_numeric(lam["SystemLambda"], errors="coerce")
    lam["date"] = lam["SCEDTimestamp"].dt.normalize()
    lam["HE"] = lam["SCEDTimestamp"].dt.hour + 1               # hour ending
    price = lam.groupby(["date", "HE"], as_index=False)["SystemLambda"].mean()

    nl = hourly_net_load()
    nl = between(nl, "date", *SUMMER).rename(columns={"HE": "HE"})
    df = nl.merge(price, on=["date", "HE"], how="inner").dropna(
        subset=["net_load", "SystemLambda"])
    df["hour_ts"] = df["date"] + pd.to_timedelta(df["HE"] - 1, unit="h")
    df["ts"] = df["hour_ts"].dt.strftime("%Y-%m-%d HE%H")
    df["hod"] = df["HE"]
    print(f"hours: {len(df):,}  net load {df.net_load.min():.0f}-{df.net_load.max():.0f} MW  "
          f"price {df.SystemLambda.min():.0f}-{df.SystemLambda.max():.0f} $/MWh")

    # binned median price per 2 GW net-load bin
    df["nl_bin"] = (df["net_load"] // 2000 * 2000).astype(int)
    binned = (df.groupby("nl_bin")["SystemLambda"]
                .agg(median="median", p90=lambda s: s.quantile(.9), n="size").reset_index())
    binned = binned[binned["n"] >= 5]
    binned["nl_c"] = binned["nl_bin"] + 1000
    binned.to_csv(OUT / "netload_vs_price_binned.csv", index=False)
    df.to_parquet(DATA / "netload_vs_price_summer25.parquet", index=False)

    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=df["net_load"], y=df["SystemLambda"], mode="markers",
        marker=dict(size=5, color=df["hod"], colorscale="Turbo", opacity=0.6,
                    colorbar=dict(title="hour<br>ending")),
        customdata=df["ts"],
        hovertemplate="<b>%{customdata}</b><br>net load %{x:,.0f} MW"
                      "<br>price $%{y:,.1f}/MWh<extra></extra>", name="hour"))
    fig.add_trace(go.Scatter(x=binned["nl_c"], y=binned["median"], mode="lines+markers",
                             line=dict(color="black", width=3), name="median / 2GW bin",
                             hovertemplate="~%{x:,.0f} MW<br>median $%{y:,.1f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=binned["nl_c"], y=binned["p90"], mode="lines",
                             line=dict(color="firebrick", width=2, dash="dash"),
                             name="p90 / 2GW bin"))
    fig.update_layout(
        title=dict(text=("ERCOT effective net load vs RT energy price — summer 2025 (Jun–Sep)"
                         "<br><sup>net load = load − wind − solar (hourly); price = "
                         "ercotLambda.SystemLambda (RT system marginal energy, 5-min→hourly mean). "
                         f"{len(df):,} hrs.</sup>")),
        xaxis_title="effective net load (MW)",
        yaxis_title="RT energy price — SystemLambda ($/MWh)",
        template="plotly_white", width=1150, height=680,
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"))
    out = OUT / "netload_vs_price_2025.html"
    fig.write_html(out, include_plotlyjs=True)
    print(f"-> {out}")
    print("\nmedian price by net-load bin:")
    print(binned[["nl_bin", "n", "median", "p90"]].to_string(index=False))


if __name__ == "__main__":
    main()
