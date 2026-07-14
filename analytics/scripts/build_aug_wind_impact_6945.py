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

    # ---------- pick representative week (most recent year with load data) ----------
    rep_year = None
    rep_window = None
    for y in sorted(all_hourly.keys(), reverse=True):
        w = pick_peak_load_week(y)
        if w is not None:
            rep_year, rep_window = y, w
            break
    if rep_window is None:
        # fallback: pick the week (7 days) with highest mean |Panhandle contribution|
        rep_year = max(all_hourly.keys())
        rp = all_hourly[rep_year].set_index("hour")
        daily_pan = rp["Panhandle"].resample("D").mean()
        # rolling 7-day mean, pick window start with max
        roll = daily_pan.rolling(7).mean()
        end_day = roll.idxmax()
        start_day = end_day - pd.Timedelta(days=6)
        rep_window = (start_day, end_day + pd.Timedelta(days=1), None)
        print(f"No cached system-load data for peak-week selection; falling back to "
              f"highest-mean-Panhandle-contribution week in Aug {rep_year}.")

    rep_start, rep_end, rep_peak_day = rep_window
    print(f"\nRepresentative time-series week: Aug {rep_year}, "
          f"{rep_start.date()} .. {rep_end.date()}"
          + (f" (peak-load day {rep_peak_day.date()})" if rep_peak_day is not None else ""))

    rep_df = all_hourly[rep_year]
    rep_ts = rep_df[(rep_df["hour"] >= rep_start) & (rep_df["hour"] < rep_end)].sort_values("hour")

    # ---------- build figure ----------
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.42, 0.58],
        vertical_spacing=0.12,
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]],
        subplot_titles=(
            "Mean & P90 flow contribution by wind region, per August (2021-2025)",
            f"Representative week -- Aug {rep_year} ({rep_start.date()} to "
            f"{(rep_end - pd.Timedelta(days=1)).date()}): hourly stacked regional "
            f"contribution + net Panhandle+West",
        ),
    )

    # --- Row 1: grouped bars, mean with p90-based error bar, Panhandle vs West ---
    years_present = summary_df.loc[summary_df["status"] == "OK", "year"].tolist()
    sdf = summary_df.set_index("year").loc[years_present]

    fig.add_trace(
        go.Bar(
            name="Panhandle (loads +)",
            x=years_present,
            y=sdf["panhandle_mean_MW"],
            error_y=dict(
                type="data",
                array=(sdf["panhandle_p90_MW"] - sdf["panhandle_mean_MW"]).clip(lower=0),
                arrayminus=[0] * len(sdf),
                visible=True,
            ),
            marker_color=REGION_COLOR["Panhandle"],
            showlegend=False,
            hovertemplate="Aug %{x}<br>Panhandle mean %{y:.1f} MW<extra></extra>",
        ),
        row=1, col=1, secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            name="West (relieves -)",
            x=years_present,
            y=sdf["west_mean_MW"],
            error_y=dict(
                type="data",
                array=[0] * len(sdf),
                arrayminus=(sdf["west_mean_MW"] + sdf["west_p90_abs_relief_MW"]).clip(lower=0),
                visible=True,
            ),
            marker_color=REGION_COLOR["West"],
            showlegend=False,
            hovertemplate="Aug %{x}<br>West mean %{y:.1f} MW<extra></extra>",
        ),
        row=1, col=1, secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            name="Danger-hour fraction (net>0, right axis)",
            x=years_present,
            y=sdf["danger_hour_fraction"],
            mode="lines+markers",
            line=dict(color="black", dash="dot"),
            marker=dict(size=8, symbol="diamond"),
            hovertemplate="Aug %{x}<br>danger-hour frac %{y:.1%}<extra></extra>",
        ),
        row=1, col=1, secondary_y=True,
    )
    fig.update_yaxes(
        title_text="danger-hour fraction", range=[0, 1], tickformat=".0%",
        showgrid=False, secondary_y=True, row=1, col=1,
    )
    fig.add_hline(y=0, line_color="rgba(0,0,0,0.4)", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="mean flow contribution (MW, dispatched x PSENS)",
                      row=1, col=1, secondary_y=False)
    fig.update_xaxes(title_text="August", type="category", row=1, col=1)

    # --- Row 2: stacked bar of regional contributions over representative week ---
    for r in REGION_ORDER:
        fig.add_trace(
            go.Bar(
                name=r, x=rep_ts["hour"], y=rep_ts[r],
                marker_color=REGION_COLOR[r],
                legendgroup=r, showlegend=True,
                hovertemplate=f"{r}" + " %{y:.1f} MW<br>%{x}<extra></extra>",
            ),
            row=2, col=1,
        )
    net_rep = rep_ts["Panhandle"] + rep_ts["West"]
    fig.add_trace(
        go.Scatter(
            name="Net Panhandle+West", x=rep_ts["hour"], y=net_rep,
            mode="lines", line=dict(color="black", width=2),
        ),
        row=2, col=1,
    )
    fig.add_hline(y=0, line_color="rgba(0,0,0,0.5)", row=2, col=1)
    fig.update_layout(barmode="relative")
    fig.update_yaxes(title_text="flow contribution (MW)", row=2, col=1)
    fig.update_xaxes(title_text="hour", row=2, col=1)

    fig.update_layout(
        title=dict(
            text=(
                "6945 (MGSES->CATSW) -- West vs Panhandle wind flow-impact, "
                "Augusts 2021-2025<br>"
                "<sup>contribution = SCED BasePoint (dispatched MW) x PSENS "
                f"(psenShiftID {PSEN_ID}, Jul-2026 topology); SCED Gen Resource "
                "dispatch is a 60-day disclosure, so each historical August's "
                "dispatch is paired with the CURRENT shift-factor structure "
                "-- a climatology of the West-vs-Panhandle impact pattern, "
                "not a re-derivation of each year's actual topology.</sup>"
            ),
            x=0.02, xanchor="left",
        ),
        height=950,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0),
        margin=dict(t=140),
    )

    html_out = OUT / "aug_wind_impact_6945.html"
    fig.write_html(html_out, include_plotlyjs=True, full_html=True)
    print(f"\nWrote plot -> {html_out}")


if __name__ == "__main__":
    main()
