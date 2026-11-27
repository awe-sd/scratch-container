"""Two-step CRR screening + valuation report for one study.

STEP 1 (all binding constraints, local computation from cache + CSVs):
classify each into A outage-driven/dispatchable, B baseline binder,
C no-dispatch/unenforceable, D outage-relieved/bearish (see classify_constraint below).

STEP 2 (class A only, capped at 40 by post-cutoff rent): single-month
fast-scan P(bind), offer-curve lambda(depth) evaluated over the fast-scan
negative-headroom distribution, ticket/days-active coverage, and the
cheapest path-opt path's effective SF and edge.

Usage: uv run powerflow_analytics/scripts/build_screening_report.py --study 14412 --month 2026-09 --cutoff 2026-09-15
"""
from __future__ import annotations

import argparse
import gc


import pandas as pd

from pfa import config, periods
from pfa.analysis import dispatch_screen, marginal_units, shadow_price as sp
from pfa.analysis.constraints import BINDING_PCT, constraint_key
from pfa.cache import StudyCache
from pfa.constraint_id import ConstraintId
from pfa.extract import network_ref, fastscan, gen_mapping, popt, shifts


TOP_SHARE_MIN = 0.25  # class A: top tofinder group must move this share of preflow


def classify_constraint(
    top_share: float | None,
    dispatch_ok: bool | None,
    penalty: bool,
    pre_rate: float | None,
    post_rate: float | None,
) -> tuple[str, str]:
    """Returns (class_letter, reason).

    Precedence: D (bearish — the outage relieves the constraint, or it was a
    pre-cutoff binder that the outage set makes go away) beats everything
    else, since it flips the trading direction; then A (outage-driven,
    dispatchable — the actionable long list); then C (no dispatchable relief
    exists, or the LP prices it at the penalty tier — ERCOT unlikely to run
    the outage); then B (binds anyway, outage or not); else unclassified.
    """
    if top_share is not None and top_share < 0:
        return "D", "top outage group UNLOADS the constraint (negative flow-delta share)"
    if pre_rate is not None and post_rate is not None and pre_rate > 0 and post_rate == 0:
        return "D", "bound pre-cutoff, stops binding post-cutoff with the outage set in"

    if top_share is not None and top_share >= TOP_SHARE_MIN and dispatch_ok is not False:
        return "A", "outage-driven (top group >= 25% of preflow) and dispatch screen passes"

    if penalty or dispatch_ok is False:
        reason = []
        if penalty:
            reason.append("penalty-tier LP lambda")
        if dispatch_ok is False:
            reason.append("no dispatchable relief pair")
        return "C", " + ".join(reason)

    if pre_rate is not None and post_rate is not None and post_rate > 0 and pre_rate >= 0.5 * post_rate:
        return "B", "binds pre-cutoff at >= half the post-cutoff rate (baseline, not outage-created)"

    return "U", "no class criterion matched (thin/ambiguous evidence)"


# --------------------------------------------------------------------------
# Step-1 feature computation
# --------------------------------------------------------------------------

def pre_post_bind_rates(ctgviol: pd.DataFrame, runs: pd.DataFrame, cutoff: str):
    """Per-constraint P(bind) in pre-cutoff runs and post-cutoff runs
    (fraction of that period's runs, not raw counts — periods can have
    different run counts)."""
    r = runs.copy()
    r["_post"] = pd.to_datetime(r["SIMDATE"]) >= pd.to_datetime(cutoff)
    n_pre = r.loc[~r["_post"], "RUNID"].nunique()
    n_post = r.loc[r["_post"], "RUNID"].nunique()
    cv = ctgviol.copy()
    cv["CONSTRAINT"] = constraint_key(cv)
    cv = cv[cv["LIMVIOLPCT"] >= BINDING_PCT].merge(r[["RUNID", "_post"]], on="RUNID", how="left")
    pre_bind = cv[~cv["_post"]].groupby("CONSTRAINT")["RUNID"].nunique()
    post_bind = cv[cv["_post"]].groupby("CONSTRAINT")["RUNID"].nunique()
    rate_pre = (pre_bind / n_pre) if n_pre else pre_bind * 0.0
    rate_post = (post_bind / n_post) if n_post else post_bind * 0.0
    return rate_pre, rate_post, n_pre, n_post


def month_bind_dates(ctgviol: pd.DataFrame, runs: pd.DataFrame, cutoff: str, month: str):
    """Per-constraint: (distinct post-cutoff in-month SIMDATEs it binds on,
    distinct post-cutoff in-month SIMDATEs sampled at all) — the days-active
    proxy for un-ticketed class-A coverage."""
    r = runs.copy()
    r["SIMDATE"] = pd.to_datetime(r["SIMDATE"])
    first, last = periods.month_range(month)
    r = r[(r["SIMDATE"] >= pd.to_datetime(cutoff)) & (r["SIMDATE"] >= first) & (r["SIMDATE"] <= last)]
    n_sampled = r["SIMDATE"].dt.date.nunique()
    cv = ctgviol.copy()
    cv["CONSTRAINT"] = constraint_key(cv)
    cv = cv[cv["LIMVIOLPCT"] >= BINDING_PCT].merge(r[["RUNID", "SIMDATE"]], on="RUNID", how="inner")
    bind_days = cv.groupby("CONSTRAINT")["SIMDATE"].apply(lambda s: s.dt.date.nunique())
    return bind_days, n_sampled


def coverage_and_days(c: str, has_ticket: bool, start, end, bind_days_map, n_sampled, month: str):
    """(coverage fraction, outage days in the month, marker, thin_evidence)."""
    if has_ticket:
        first, last = periods.month_range(month)
        days = pd.bdate_range(max(pd.Timestamp(start), first), min(pd.Timestamp(end), last))
        days = days[~days.isin(periods.nerc_holidays(first.year))]
        n_days = len(days)
        cov = round(n_days * 16 / (len(periods.onpeak_days(month)) * 16), 3)
        return cov, n_days, "", n_days < 3
    n_days = int(bind_days_map.get(c, 0))
    cov = round(n_days / n_sampled, 3) if n_sampled else 0.0
    return cov, n_days, "(days-proxy)", n_days < 3


# --------------------------------------------------------------------------
# Step-2 valuation
# --------------------------------------------------------------------------

def fastscan_month_onpeak(config_id: int, month: str):
    """Fast-scan headroom for the calendar month across all years, restricted to weekday HE7-22
    on-peak rows (ex-NERC holidays); returns (p_bind_onpeak, need_df) where need_df is the
    NEED_MW frame (negative-headroom onpeak hours only, for shadow_price)."""
    df = fastscan.headroom_for_month(config_id, periods.parse_month(month)[1])
    if df.empty:
        return None, pd.DataFrame()
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])
    onpk = df[periods.fastscan_hour_class(df["TIMESTAMP"]) == "OnPeak"]
    if onpk.empty:
        return None, pd.DataFrame()
    p_bind = float((onpk["HEADROOM"] < 0).mean())
    need = onpk[onpk["HEADROOM"] < 0].copy()
    need["NEED_MW"] = -need["HEADROOM"].astype(float)
    return p_bind, need


def cpnode_sf(study_id: int, constraint: str, names: list[str]) -> dict[str, float]:
    names = [n for n in names if isinstance(n, str) and n]
    if not names:
        return {}
    cid = ConstraintId.parse(constraint)
    df = shifts.cpnode_sf_by_name(study_id, cid, names)
    return {r["NAME"]: float(r["SF"]) for _, r in df.iterrows()} if len(df) else {}


def value_row(study_id: int, c: str, gen, bus_names, genunit, scedname, month: str) -> dict:
    """Step-2 valuation components for one class-A constraint."""
    out: dict = {"_status": "ok"}
    cid = ConstraintId.parse(c)
    f, t, ctg = cid.fromnum, cid.tonum, cid.ctglabel
    cfgs = fastscan.find_configs(study_id, int(f), int(t), ctg)
    if cfgs.empty:
        out["_status"] = "no fast-scan config"
        return out
    config_id = int(cfgs["CONFIG_ID"].iloc[0])
    direction = int(cfgs["DIRECTION"].iloc[0]) if pd.notna(cfgs["DIRECTION"].iloc[0]) else 1
    label = periods.month_label(month)
    p_bind, need = fastscan_month_onpeak(config_id, month)
    if p_bind is None:
        out["_status"] = f"no {label} on-peak fast-scan hours"
        return out
    out[f"P(bind) {label} on-peak"] = round(p_bind, 3)

    # DIRECTION matters: on a reverse-bound branch (-1) a positive-PSENS
    # unit is relief (up), not the problem (down) — see relief_set's
    # docstring for the study-14412 canary this fixes (3380-3390-1@DPNAONA5).
    relief = sp.relief_set(study_id, c, gen, bus_names, genunit, scedname, direction=direction)
    if relief.units.empty:
        out["_status"] = "no relief-set units in SF band"
        return out
    if relief.capacity.empty or not relief.up or not relief.down:
        out["_status"] = "no DAM offer coverage for relief-set units"
        return out
    curve = relief.curve()
    if not curve or need.empty:
        out["_status"] = "no fast-scan negative-headroom hours"
        return out
    dist = sp.lambda_distribution(curve, need)
    priced = dist["LAMBDA"].dropna()
    if priced.empty:
        out["_status"] = "fast-scan need exceeds relief-set capacity at every hour"
        return out
    pct = sp.percentiles(priced)
    out["E[lambda|bind]"] = round(float(priced.mean()), 1)
    out["lambda P50"] = pct.get("P50")
    out["lambda P90"] = pct.get("P90")
    out["unpriced deep hours %"] = round(100.0 * dist["LAMBDA"].isna().mean(), 1)

    paths = popt.best_paths(study_id, c)
    if paths is not None:
        p = paths.iloc[0]
        source, sink = str(p["SOURCENAME"]), str(p["SINKNAME"])
        sfs = cpnode_sf(study_id, c, [source, sink])
        if source in sfs and sink in sfs:
            eff_sf = sfs[source] - sfs[sink]
            sf_marker = ""
        else:
            eff_sf = float(p["AVG_SF"])
            sf_marker = "~"
        out["Path"] = f"{source}->{sink} ${float(p['OPTIONPRICE']):.2f}"
        out["Path SF"] = f"{sf_marker}{eff_sf:.3f}"
        out["_eff_sf"] = eff_sf
        out["_path_price"] = float(p["OPTIONPRICE"])
    return out


# --------------------------------------------------------------------------
# HTML
# --------------------------------------------------------------------------

STYLE = """
body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:2rem;color:#1a1a2e;background:#fafafa}
h1{font-size:1.4rem} h2{font-size:1.1rem;margin-top:2.2rem}
.meta{color:#555;font-size:0.9rem;margin-bottom:1rem;max-width:80rem;line-height:1.4}
table{border-collapse:collapse;font-size:0.78rem;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.12);margin-bottom:1rem}
th,td{border:1px solid #ddd;padding:4px 7px;text-align:right;white-space:nowrap}
th{background:#22304a;color:#fff;position:sticky;top:0}
td:first-child,td:nth-child(2),td:nth-child(3){text-align:left}
tr:nth-child(even){background:#f4f6fa}
.classA{background:#e8f5e9!important} .classD{background:#fdecea!important}
.thin{color:#8a1f1f;font-style:italic}
tr.filter-row td{padding:2px 4px;position:sticky;top:1.9rem;background:#fff}
tr.filter-row input{width:100%;box-sizing:border-box;font-size:0.72rem;padding:2px 3px}
"""


def filterable_table(table_id: str, df: pd.DataFrame, row_classes=None) -> str:
    cols = list(df.columns)
    header = "".join(f"<th>{c}</th>" for c in cols)
    filter_row = "".join(
        f'<td><input type="text" data-col="{i}" oninput="filterTable(\'{table_id}\')"></td>'
        for i in range(len(cols)))
    body_rows = []
    for i, (_, r) in enumerate(df.iterrows()):
        cls = row_classes[i] if row_classes is not None else ""
        cattr = f' class="{cls}"' if cls else ""
        tds = "".join(f"<td>{'' if pd.isna(r[c]) else r[c]}</td>" for c in cols)
        body_rows.append(f"<tr{cattr}>{tds}</tr>")
    return (f'<table id="{table_id}"><thead><tr>{header}</tr>'
            f'<tr class="filter-row">{filter_row}</tr></thead>'
            f'<tbody>{"".join(body_rows)}</tbody></table>')


FILTER_JS = """
function filterTable(id) {
  var table = document.getElementById(id);
  var inputs = table.querySelectorAll('.filter-row input');
  var filters = [];
  inputs.forEach(function(inp) {
    if (inp.value.trim() !== '') filters.push({col: parseInt(inp.dataset.col), val: inp.value.trim()});
  });
  var rows = table.querySelectorAll('tbody tr');
  rows.forEach(function(row) {
    var cells = row.children;
    var show = true;
    filters.forEach(function(f) {
      if (!show) return;
      var text = cells[f.col] ? cells[f.col].textContent : '';
      var op = f.val[0];
      if (op === '>' || op === '<') {
        var num = parseFloat(text.replace(/,/g, ''));
        var target = parseFloat(f.val.slice(1));
        if (isNaN(num) || isNaN(target)) { show = false; }
        else if (op === '>' && !(num > target)) show = false;
        else if (op === '<' && !(num < target)) show = false;
      } else if (text.toLowerCase().indexOf(f.val.toLowerCase()) === -1) {
        show = false;
      }
    });
    row.style.display = show ? '' : 'none';
  });
}
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--month", required=True, help="settlement month YYYY-MM")
    ap.add_argument("--cutoff", required=True, help="pre/post split date YYYY-MM-DD")
    args = ap.parse_args()

    out_dir = config.OUTPUT_ROOT / f"study_{args.study}"
    cache = StudyCache(args.study)
    runs = cache.load("opfrun")
    study_name = cache.load("opfstudy")["STUDYNAME"].iloc[0]

    ranked = pd.read_csv(out_dir / "ranked_constraints.csv", low_memory=False)
    short = ranked[(ranked["N_RUNS_BINDING"] >= 1) & (ranked["TOTAL_RENT"] > 0)].drop_duplicates("CONSTRAINT")

    ctgviol = cache.load("outctgviol2", columns=[
        "RUNID", "FROMNUM", "TONUM", "CKT", "CTGLABEL", "LIMVIOLPCT", "BRANCHID",
    ])
    gen = cache.load("outgen2", columns=["RUNID", "BUSNUM", "ID", "LPDELTAMW", "FUELTYPE", "MW", "MWMAX"])
    branch = cache.load("outbranch2", columns=["RUNID", "FROMNUM", "TONUM", "CKT", "FROMNAME", "TONAME"])
    genunit = cache.load("genunit")
    scedname = gen_mapping.fetch_genunit_sced_name()
    bus_names = marginal_units.bus_name_map(branch)

    tf_sum = pd.read_csv(out_dir / "tofinder_summary.csv")
    tf_sum["FLOW_FRAC_SIGNED"] = tf_sum["MEAN_FLOWDELTA"] / tf_sum["MEAN_PREFLOW"]
    top_drv = (tf_sum.reindex(tf_sum["MEAN_FLOWDELTA"].abs().sort_values(ascending=False).index)
               .drop_duplicates("CONSTRAINT").set_index("CONSTRAINT"))

    cutoff = args.cutoff
    label = periods.month_label(args.month)
    rate_pre, rate_post, n_pre, n_post = pre_post_bind_rates(ctgviol, runs, cutoff)
    bind_days_map, n_sampled_month = month_bind_dates(ctgviol, runs, cutoff, args.month)

    # ONE bulk round trip for dispatch features on every candidate constraint
    # (was 2 queries x ~230 constraints — the architect-flagged cost problem).
    dispatch_feats = dispatch_screen.bulk_dispatch_features(args.study, short["CONSTRAINT"].tolist())
    gc.collect()

    rows = []
    for _, r in short.iterrows():
        c = r["CONSTRAINT"]
        cid = ConstraintId.parse(c)
        f, t = cid.fromnum, cid.tonum
        kv = network_ref.constraint_kv(int(f), int(t))

        penalty = False
        if "MEAN_SHADOW" in r and pd.notna(r.get("MEAN_SHADOW")):
            penalty = float(r["MEAN_SHADOW"]) >= 500

        top_share = None
        top_group = None
        if c in top_drv.index:
            d = top_drv.loc[c]
            top_share = float(d["FLOW_FRAC_SIGNED"]) if pd.notna(d["FLOW_FRAC_SIGNED"]) else None
            top_group = str(d["OUTAGE_GROUP"])

        if c in dispatch_feats.index:
            dispatch_ok = bool(dispatch_feats.loc[c, "DISPATCH_OK"])
            n_qual = int(dispatch_feats.loc[c, "N_QUAL"])
        else:
            dispatch_ok, n_qual = None, None

        pr = float(rate_pre.get(c, 0.0))
        po = float(rate_post.get(c, 0.0))
        cls, reason = classify_constraint(top_share, dispatch_ok, penalty, pr, po)

        has_ticket = pd.notna(r.get("DRIVER_TICKET")) and pd.notna(r.get("DRIVER_TICKET_START"))
        tickets_all = r.get("DRIVER_TICKETS_ALL")
        if not (isinstance(tickets_all, str) and tickets_all):
            tickets_all = (f"{r.get('DRIVER_TICKET')} ({r.get('DRIVER_TICKET_STATUS')}"
                           f"/{r.get('DRIVER_TICKET_REASON', '?')})") if has_ticket else None

        cov, n_days, marker, thin = coverage_and_days(
            c, has_ticket, r.get("DRIVER_TICKET_START"), r.get("DRIVER_TICKET_END"),
            bind_days_map, n_sampled_month, args.month)

        rows.append({
            "Constraint": c, "From": r["FROMNAME"], "To": r["TONAME"],
            "kV": int(kv) if kv else None,
            "class": cls, "_reason": reason,
            "top outage group": top_group,
            "impact share": round(top_share, 3) if top_share is not None else None,
            "tickets": tickets_all,
            "pre-cutoff binds": round(pr, 3),
            "post-cutoff binds": round(po, 3),
            "qualifying dispatch nodes": n_qual,
            f"Outage days in {label}": n_days,
            "_coverage": cov, "_cov_marker": marker, "_thin": thin,
            "Month rent ($)": int(r["TOTAL_RENT"]),
            "_rent_post": float(r["RENT_POST"]),
        })
    df = pd.DataFrame(rows)

    n_by_class = df["class"].value_counts().to_dict()

    # ---- Step 2 gate: hard thresholds, not a top-40 cap ----
    # A constraint gets full-scope research ONLY if ALL of: class A; positive
    # impact share >= 0.25 (implied by class A, re-asserted here); qualifying
    # dispatch nodes >= 2; outage-days in the month >= 3; post-cutoff rent >= $200k.
    GATE_MIN_QUAL_NODES = 2
    GATE_MIN_OUTAGE_DAYS = 3
    GATE_MIN_RENT_POST = 200_000
    HARD_CAP = 15

    classA_all = df[df["class"] == "A"]
    funnel = {"screened": len(df), "class_A": len(classA_all)}
    g = classA_all[classA_all["impact share"].fillna(0) >= 0.25]
    funnel["impact_share>=0.25"] = len(g)
    g = g[g["qualifying dispatch nodes"].fillna(0) >= GATE_MIN_QUAL_NODES]
    funnel["qual_nodes>=2"] = len(g)
    g = g[g[f"Outage days in {label}"].fillna(0) >= GATE_MIN_OUTAGE_DAYS]
    funnel["outage_days>=3"] = len(g)
    g = g[g["_rent_post"] >= GATE_MIN_RENT_POST]
    funnel["rent_post>=200k"] = len(g)
    classA = g.sort_values("_rent_post", ascending=False).head(HARD_CAP).copy()
    funnel["researched"] = len(classA)
    print(f"Step-2 gate funnel: {funnel}")

    val_rows = []
    for _, r in classA.iterrows():
        c = r["Constraint"]
        comp = value_row(args.study, c, gen, bus_names, genunit, scedname, args.month)
        p_bind = comp.get(f"P(bind) {label} on-peak")
        elam = comp.get("E[lambda|bind]")
        cov = r["_coverage"]
        value = round(p_bind * elam * cov, 3) if (p_bind is not None and elam is not None) else None
        eff_sf = comp.get("_eff_sf")
        path_price = comp.get("_path_price")
        edge = (round(value * eff_sf - path_price, 2)
                if value is not None and eff_sf is not None and path_price is not None else None)
        val_rows.append({
            "Constraint": c, "From": r["From"], "To": r["To"], "kV": r["kV"],
            "tickets": r["tickets"], f"Outage days in {label}": r[f"Outage days in {label}"],
            "coverage": f"{r['_coverage']}{r['_cov_marker']}",
            "thin window evidence": "thin window evidence" if r["_thin"] else "",
            f"P(bind) {label} on-peak": p_bind,
            "E[lambda|bind]": elam,
            "lambda P50": comp.get("lambda P50"), "lambda P90": comp.get("lambda P90"),
            "unpriced deep hours %": comp.get("unpriced deep hours %"),
            f"{label} value $/MWh/SF": value,
            "Path": comp.get("Path"), "Path SF": comp.get("Path SF"),
            "Edge $": edge,
            "status": comp.get("_status", "ok") if value is not None else comp.get("_status", "unpriced"),
            "_thin": r["_thin"], "_priced": value is not None,
        })
    val_df = pd.DataFrame(val_rows)
    if not val_df.empty:
        # Priced rows first (by value, thin-evidence ones demoted to the
        # bottom of the priced group), then unpriced rows (no DAM/fast-scan
        # coverage — a data gap, not a zero) at the very bottom, so a
        # legitimately-near-zero priced constraint is never mistaken for
        # (or ranked above/below) one we simply couldn't price.
        val_df["_sort"] = val_df[f"{label} value $/MWh/SF"].where(~val_df["_thin"], -1e9)
        val_df = val_df.sort_values(["_priced", "_sort"], ascending=[False, False]).reset_index(drop=True)
        val_df = val_df.drop(columns=["_sort", "_thin", "_priced"])

    classD = df[df["class"] == "D"].copy()

    screen_out = df[[c for c in df.columns if not c.startswith("_")]].copy()
    screen_out["reason"] = df["_reason"]
    screen_out.to_csv(out_dir / "screening_step1.csv", index=False)
    if not val_df.empty:
        val_df.to_csv(out_dir / "screening_step2_valuation.csv", index=False)

    row_classes_screen = [f"class{r}" if r in ("A", "D") else "" for r in df["class"]]

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>CRR screening — study {args.study}</title><style>{STYLE}</style></head><body>
<h1>CRR two-step screening — study {args.study} ({study_name}), {args.month}</h1>
<div class="meta">Classes: <b>A</b> outage-driven &amp; dispatchable (top tofinder outage group moves >= 25% of
preflow, positive, and a dispatchable relief pair exists) &mdash; <b>B</b> baseline binder (binds pre-cutoff at
&gt;= half the post-cutoff rate) &mdash; <b>C</b> no-dispatch/unenforceable (penalty-tier LP lambda or no
dispatchable relief pair &mdash; ERCOT unlikely to run the outage) &mdash; <b>D</b> outage-relieved/bearish
(the outage set UNLOADS the constraint, or it stops binding post-cutoff). Class counts: {n_by_class}.
Coverage for Step 2: ticketed constraints use the ticket window's {label} weekday hours / {len(periods.onpeak_days(args.month)) * 16}; un-ticketed
class-A constraints use a (days-proxy) = distinct post-cutoff {label} sim-dates it binds on / distinct
post-cutoff {label} sim-dates sampled &mdash; rows under 3 days-equivalent are flagged 'thin window evidence'
and sorted to the bottom.</div>

<h2>Step 1 — screen (all classes, filterable)</h2>
{filterable_table('screen', df[[c for c in df.columns if not c.startswith('_')] ], row_classes_screen)}

<h2>Step 2 — valuation ({len(classA)} constraints cleared the gate: class A, impact share &gt;= 0.25,
qualifying dispatch nodes &gt;= 2, outage-days in {label} &gt;= 3, post-cutoff rent &gt;= $200k; hard cap 15 by rent)</h2>
<div class="meta">Gate funnel: {funnel}</div>
{filterable_table('valuation', val_df) if not val_df.empty else '<p>No class-A constraints.</p>'}

<h2>Constraints that go away with the outages &mdash; check existing exposure (class D, bearish)</h2>
{filterable_table('bearish', classD[[c for c in classD.columns if not c.startswith('_')]]) if not classD.empty else '<p>No class-D constraints found this run.</p>'}

<script>{FILTER_JS}</script>
</body></html>"""
    (out_dir / "screening_report.html").write_text(html)

    print(f"Class counts: {n_by_class}")
    print(f"\nTop 15 class-A by {label} value:")
    if not val_df.empty:
        print(val_df.head(15).to_string(index=False))
    print(f"\nClass D (bearish): {len(classD)} constraints")
    if len(classD):
        print(classD[["Constraint", "top outage group", "impact share", "pre-cutoff binds", "post-cutoff binds"]].to_string(index=False))
    print(f"\n-> {out_dir / 'screening_report.html'}")


if __name__ == "__main__":
    main()
