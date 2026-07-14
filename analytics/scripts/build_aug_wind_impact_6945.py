"""
Build the West-vs-Panhandle wind flow-impact plot for constraint 6945
(MGSES 345kV -> CATSW 345kV, contingency SRGRMGS5, congConstraintID 231176)
across the last 5 Augusts (2021-2025).

impact (flow contribution) = SCED BasePoint (dispatched MW) x PSENS (shift
factor) for psenShiftID 86037069, the current (Jul-2026) topology, applied
to each historical August's dispatch as a climatology.

Read-only / local-only: reads cached parquet under analytics/data/, writes
analytics/output/aug_wind_impact_6945.html and
analytics/output/aug_wind_impact_6945_summary.csv. No DB writes.
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "output"
OUT.mkdir(parents=True, exist_ok=True)

PSEN_ID = 86037069
YEARS = [2021, 2022, 2023, 2024, 2025]
REGION_ORDER = ["Panhandle", "West", "North", "South", "Coastal", "Unmapped"]
REGION_COLOR = {
    "Panhandle": "#d95f02",   # loads -> warm
    "West": "#1b6ba8",        # relieves -> cool
    "North": "#7570b3",
    "South": "#66a61e",
    "Coastal": "#a6761d",
    "Unmapped": "#999999",
}


def load_static():
    psen = pd.read_parquet(DATA / f"psenShift_{PSEN_ID}.parquet")
    ur = pd.read_parquet(DATA / "wind_unit_region.parquet")
    ur = ur[["unitName", "windRegion"]].drop_duplicates("unitName").copy()
    ur["unitName_u"] = ur["unitName"].str.upper().str.strip()
    return psen, ur


def process_year(year, psen, ur):
    """Returns (hourly regional-contribution df, reconciliation ok bool, n_hours)
    or (None, None, None) if no cached data for this year."""
    f = DATA / f"sced_wind_aug{year}.parquet"
    if not f.exists():
        print(f"[{year}] no cached SCED file ({f.name}) -- skipping")
        return None, None, None

    d = pd.read_parquet(f)
    if len(d) == 0:
        print(f"[{year}] cached file is empty -- skipping")
        return None, None, None

    d = d.copy()
    d["ResourceName_u"] = d["ResourceName"].str.upper().str.strip()
    d["cpnodeid_i"] = pd.to_numeric(d["cpnodeid"], errors="coerce")

    # join to psen vector (inner: units not on this constraint's sensitivity
    # list have ~0 measurable impact on it and are excluded, per verified
    # cpnode-join integrity check: 171/172 wind cpnodes match)
    j = d.merge(psen, left_on="cpnodeid_i", right_on="cpNodeId", how="inner")

    # join to region map; unmatched units bucketed as "Unmapped" (kept, not dropped)
    j = j.merge(ur[["unitName_u", "windRegion"]], left_on="ResourceName_u",
                right_on="unitName_u", how="left")
    j["windRegion"] = j["windRegion"].fillna("Unmapped")

    j["flow_contribution"] = j["BasePoint"] * j["psen"]

    # reconciliation: sum of all per-unit contributions each hour must equal
    # the sum of the region-grouped contributions each hour (Unmapped keeps
    # everything that didn't match a region, so this should tie out exactly)
    total_by_hour = j.groupby("hr")["flow_contribution"].sum()
    region_pivot = j.pivot_table(index="hr", columns="windRegion",
                                  values="flow_contribution", aggfunc="sum",
                                  fill_value=0.0)
    recon_diff = (region_pivot.sum(axis=1) - total_by_hour).abs().max()
    recon_ok = bool(recon_diff < 1e-6)
    print(f"[{year}] rows={len(d):,} matched-to-psen={len(j):,} "
          f"hours={j['hr'].nunique()} regions={sorted(j['windRegion'].unique())} "
          f"reconciliation max|diff|={recon_diff:.2e} ok={recon_ok}")

    for r in REGION_ORDER:
        if r not in region_pivot.columns:
            region_pivot[r] = 0.0
    region_pivot = region_pivot[REGION_ORDER].reset_index().rename(columns={"hr": "hour"})
    region_pivot["year"] = year
    return region_pivot, recon_ok, j["hr"].nunique()


def summarize(region_pivot):
    pan = region_pivot["Panhandle"]
    west = region_pivot["West"]
    net = pan + west
    return {
        "n_hours": len(region_pivot),
        "panhandle_mean_MW": pan.mean(),
        "panhandle_p90_MW": pan.quantile(0.90),
        "west_mean_MW": west.mean(),
        "west_p90_MW": west.quantile(0.10),  # west is negative; "p90 relief" = 10th pct (most negative-ish tail)
        "west_p90_abs_relief_MW": (-west).quantile(0.90),
        "net_pan_plus_west_mean_MW": net.mean(),
        "danger_hour_fraction": float((net > 0).mean()),
    }


def pick_peak_load_week(year):
    """Peak-load week (system ERCOT load) within `year`'s August, if load data
    is cached for that year; else None."""
    f = DATA / "ercotLoadView.parquet"
    if not f.exists():
        return None
    ld = pd.read_parquet(f)
    ld.columns = [c.lower() for c in ld.columns]
    ld["date"] = pd.to_datetime(ld["date"])
    sub = ld[(ld["date"] >= f"{year}-08-01") & (ld["date"] < f"{year}-09-01")]
    if sub.empty:
        return None
    daily = sub.groupby("date")["ercot_all_ld"].mean()
    if daily.isna().all():
        return None
    peak_day = daily.idxmax()
    # center a 7-day window on the peak day, clipped to the August
    start = max(peak_day - pd.Timedelta(days=3), pd.Timestamp(f"{year}-08-01"))
    end = min(start + pd.Timedelta(days=7), pd.Timestamp(f"{year}-09-01"))
    return start, end, peak_day


def main():
    psen, ur = load_static()
    print(f"psen vector: {len(psen)} nodes; region map: {len(ur)} units "
          f"({ur['windRegion'].value_counts().to_dict()})")

    all_hourly = {}
    recon_results = {}
    summary_rows = []

    for year in YEARS:
        region_pivot, recon_ok, n_hours = process_year(year, psen, ur)
        if region_pivot is None:
            summary_rows.append({"year": year, "n_hours": 0, "status": "NO_DATA"})
            continue
        all_hourly[year] = region_pivot
        recon_results[year] = recon_ok
        stats = summarize(region_pivot)
        stats["year"] = year
        stats["status"] = "OK" if recon_ok else "RECON_MISMATCH"
        summary_rows.append(stats)

    summary_df = pd.DataFrame(summary_rows)
    cols = ["year", "status", "n_hours", "panhandle_mean_MW", "panhandle_p90_MW",
            "west_mean_MW", "west_p90_abs_relief_MW", "net_pan_plus_west_mean_MW",
            "danger_hour_fraction"]
    summary_df = summary_df.reindex(columns=cols)
    summary_csv = OUT / "aug_wind_impact_6945_summary.csv"
    summary_df.to_csv(summary_csv, index=False)
    print(f"\nWrote summary -> {summary_csv}")
    print(summary_df.round(2).to_string(index=False))

    all_recon_ok = all(recon_results.values()) if recon_results else False
    print(f"\nAll reconciliation checks OK: {all_recon_ok}")

    if not all_hourly:
        print("BLOCKED: no August had usable data; cannot build plot.")
        return

    # ---------- build figure: Row 1 summary, then one full-month hourly panel
    #            per August showing ALL hourly data (2021-2025) ----------
    years_present = summary_df.loc[summary_df["status"] == "OK", "year"].tolist()
    sdf = summary_df.set_index("year").loc[years_present]
    n_yr = len(years_present)

    # per-August share of hours net-LOADED (net>0) vs net-RELIEVED (net<0)
    pct_pos, pct_neg = {}, {}
    for y in years_present:
        net = all_hourly[y]["Panhandle"] + all_hourly[y]["West"]
        pct_pos[y] = float((net > 0).mean())
        pct_neg[y] = float((net < 0).mean())

    row_heights = [0.13, 0.13] + [0.74 / n_yr] * n_yr
    specs = [[{}], [{}]] + [[{}]] * n_yr
    titles = [
        "Mean & P90 flow contribution by wind region, per August (2021-2025)",
        "Share of hours the constraint is net-LOADED (Pan+West > 0) vs net-RELIEVED (< 0)",
    ] + [f"Aug {y} — hourly regional flow contribution ({int(sdf.loc[y, 'n_hours'])} hrs), "
         "Panhandle loads (+) / West relieves (−) + net" for y in years_present]
    fig = make_subplots(rows=2 + n_yr, cols=1, row_heights=row_heights,
                        vertical_spacing=0.04, specs=specs, subplot_titles=titles)

    # --- Row 1: diverging mean bars (Panhandle vs West) ---
    fig.add_trace(
        go.Bar(name="Panhandle mean", x=years_present, y=sdf["panhandle_mean_MW"],
               error_y=dict(type="data",
                            array=(sdf["panhandle_p90_MW"] - sdf["panhandle_mean_MW"]).clip(lower=0),
                            arrayminus=[0] * len(sdf), visible=True),
               marker_color=REGION_COLOR["Panhandle"], showlegend=False,
               hovertemplate="Aug %{x}<br>Panhandle mean %{y:.1f} MW<extra></extra>"),
        row=1, col=1)
    fig.add_trace(
        go.Bar(name="West mean", x=years_present, y=sdf["west_mean_MW"],
               error_y=dict(type="data", array=[0] * len(sdf),
                            arrayminus=(sdf["west_mean_MW"] + sdf["west_p90_abs_relief_MW"]).clip(lower=0),
                            visible=True),
               marker_color=REGION_COLOR["West"], showlegend=False,
               hovertemplate="Aug %{x}<br>West mean %{y:.1f} MW<extra></extra>"),
        row=1, col=1)
    fig.add_hline(y=0, line_color="rgba(0,0,0,0.4)", row=1, col=1)
    fig.update_yaxes(title_text="mean MW", row=1, col=1)
    fig.update_xaxes(type="category", row=1, col=1)

    # --- Row 2: 100%-stacked share of net-loaded vs net-relieved hours ---
    fig.add_trace(
        go.Bar(name="net-RELIEVED (net<0)", x=years_present,
               y=[pct_neg[y] for y in years_present], marker_color=REGION_COLOR["West"],
               text=[f"{pct_neg[y]:.0%}" for y in years_present], textposition="inside",
               insidetextanchor="middle",
               hovertemplate="Aug %{x}<br>net-relieved %{y:.1%} of hours<extra></extra>"),
        row=2, col=1)
    fig.add_trace(
        go.Bar(name="net-LOADED (net>0)", x=years_present,
               y=[pct_pos[y] for y in years_present], marker_color=REGION_COLOR["Panhandle"],
               text=[f"{pct_pos[y]:.0%}" for y in years_present], textposition="inside",
               insidetextanchor="middle",
               hovertemplate="Aug %{x}<br>net-loaded %{y:.1%} of hours<extra></extra>"),
        row=2, col=1)
    fig.update_yaxes(title_text="% of hours", tickformat=".0%", range=[0, 1], row=2, col=1)
    fig.update_xaxes(title_text="August", type="category", row=2, col=1)

    # --- Rows 3..: full-month hourly stacked contribution, one row per August ---
    for i, year in enumerate(years_present):
        r = 3 + i
        yp = all_hourly[year].sort_values("hour")
        for reg in REGION_ORDER:
            fig.add_trace(
                go.Bar(name=reg, x=yp["hour"], y=yp[reg], marker_color=REGION_COLOR[reg],
                       legendgroup=reg, showlegend=(i == 0),
                       hovertemplate=f"{reg} " + "%{y:.1f} MW<br>%{x|%b %d %H:00}<extra></extra>"),
                row=r, col=1)
        fig.add_trace(
            go.Scatter(name="Net Panhandle+West", x=yp["hour"], y=yp["Panhandle"] + yp["West"],
                       mode="lines", line=dict(color="black", width=1.2),
                       legendgroup="net", showlegend=(i == 0),
                       hovertemplate="net %{y:.1f} MW<br>%{x|%b %d %H:00}<extra></extra>"),
            row=r, col=1)
        fig.add_hline(y=0, line_color="rgba(0,0,0,0.5)", row=r, col=1)
        fig.update_yaxes(title_text="MW", row=r, col=1)
    fig.update_xaxes(title_text="hour (Aug)", row=2 + n_yr, col=1)

    fig.update_layout(
        barmode="relative",
        title=dict(text=(
            "6945 (MGSES→CATSW) — West vs Panhandle wind flow-impact, Augusts 2021-2025"
            "<br><sup>contribution = SCED BasePoint (dispatched MW) × PSENS "
            f"(psenShiftID {PSEN_ID}, Jul-2026 topology). ALL hourly data per August "
            "(one panel per year). SCED Gen Resource dispatch is a 60-day disclosure, so "
            "each August's dispatch is paired with the CURRENT shift structure — a "
            "climatology of the impact pattern.</sup>"), x=0.02, xanchor="left"),
        height=460 + 300 * n_yr,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0),
        margin=dict(t=150))

    html_out = OUT / "aug_wind_impact_6945.html"
    fig.write_html(html_out, include_plotlyjs=True, full_html=True)
    print(f"\nWrote plot -> {html_out}")


if __name__ == "__main__":
    main()
