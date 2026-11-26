"""Consolidated two-step CRR screening pipeline (step-1 screen -> flip detection -> stage-2 gate -> HTML).

Reproduces the approved study-14412 deliverable for an arbitrary study id, per
tracking issue awe-sd/scratch-container #6 (Feature 1 +
extensibility bar): eight named stage functions, each cache/CSV in -> DataFrame out,
so any stage is independently importable/testable; main() is orchestration + I/O only.

Reads only the local parquet cache + the two CSVs produced by build_report.py --tickets;
NQUAL is queried fresh from Snowflake (bulk_dispatch_nodes) for the full universe rather
than read from a prior CSV.

Usage:
    uv run powerflow_analytics/scripts/build_stage2_list.py --study 14431 --cutoff 2026-09-15
"""
from __future__ import annotations

import argparse
import gc

import numpy as np
import pandas as pd

from pfa.analysis.constraints import BINDING_PCT, constraint_key
from pfa.analysis.offer_lambda import MAX_SF as SF_MAX, MIN_SF as SF_MIN
from pfa.constraint_id import ConstraintId
from pfa.extract import shifts

# ---------------------------------------------------------------------------
# Thresholds — named constants, overridable via CLI (see argparse in main()).
# ---------------------------------------------------------------------------

PENALTY_TIERS = (500.0, 3500.0)  # SCOPF unresolvable-violation price caps
PENALTY_SHARE_MAX = 0.4  # C no-dispatch if this fraction of a constraint's LP rows sit in a penalty tier
FLATNESS_IQR_MAX = 1.0  # legacy flatness test: p50 exactly in a tier AND IQR below this

SHARE_MIN = 0.25
POST_DAYS_MIN = 3
RENT_MIN = 200_000
NQUAL_MIN = 2

INTENSITY_MIN_HARD = 600  # below this: dropped even if flip-exempt-eligible... see stage2_gate
INTENSITY_MIN_FULL = 1000  # at/above this: passes on its own, no flag needed


# ---------------------------------------------------------------------------
# Stage 1: constraint -> DIR (mode of OUTBRANCHDIRECTION from cached outctgviol2)
# ---------------------------------------------------------------------------
def constraint_directions(cache_dir: str) -> pd.Series:
    cv = pd.read_parquet(
        f"{cache_dir}/outctgviol2.parquet",
        columns=["FROMNUM", "TONUM", "CKT", "CTGLABEL", "OUTBRANCHDIRECTION"],
    )
    cv["C"] = constraint_key(cv)
    dirs = cv.groupby("C").OUTBRANCHDIRECTION.agg(lambda s: s.mode().iloc[0]).rename("DIR")
    del cv
    gc.collect()
    return dirs


# ---------------------------------------------------------------------------
# Stage 2: universe = ctgviol binding (>=BINDING_PCT) UNION outconstraint2 (LP-priced)
# ---------------------------------------------------------------------------
def build_universe(cache_dir: str, runs: pd.DataFrame, cutoff: str) -> pd.DataFrame:
    cv = pd.read_parquet(
        f"{cache_dir}/outctgviol2.parquet",
        columns=["RUNID", "FROMNUM", "TONUM", "CKT", "CTGLABEL", "LIMVIOLPCT", "FROMNAME", "TONAME"],
    )
    cv = cv[cv.LIMVIOLPCT >= BINDING_PCT].copy()
    cv["C"] = constraint_key(cv)
    cv = cv.merge(runs, on="RUNID")

    oc = pd.read_parquet(
        f"{cache_dir}/outconstraint2.parquet",
        columns=["RUNID", "FROMNUM", "TONUM", "CKT", "LPOPFCTGID", "OPFCNLAMBDA"],
    )
    oc = oc.rename(columns={"LPOPFCTGID": "CTGLABEL"})
    oc["C"] = constraint_key(oc)
    oc = oc.merge(runs, on="RUNID")

    pre = cv[~cv.post].groupby("C").RUNID.nunique().rename("pre_binds")
    post = cv[cv.post].groupby("C").RUNID.nunique().rename("post_binds")
    pdays = cv[cv.post].groupby("C").SIMDATE.nunique().rename("post_days")

    # display λ stats: all LP rows (kept for the HTML "all-rows" columns)
    lam_p50 = oc.groupby("C").OPFCNLAMBDA.median().rename("lam_p50")
    lam_mean = oc.groupby("C").OPFCNLAMBDA.mean().rename("lam_mean")
    lam_iqr = (
        oc.groupby("C").OPFCNLAMBDA.quantile(0.75) - oc.groupby("C").OPFCNLAMBDA.quantile(0.25)
    ).rename("lam_iqr")

    # penalty share: fraction of a constraint's LP rows sitting in a penalty tier
    in_tier = oc.OPFCNLAMBDA.isin(PENALTY_TIERS)
    penalty_share = in_tier.groupby(oc.C).mean().rename("penalty_share")

    # gate basis (fix #2): post-cutoff, non-zero, ex-penalty LP rows only
    ex_cap = oc[oc.post & (oc.OPFCNLAMBDA > 0) & (~oc.OPFCNLAMBDA.isin(PENALTY_TIERS))]
    lam_p50_gate = ex_cap.groupby("C").OPFCNLAMBDA.median().rename("lam_p50_gate")

    names = cv.drop_duplicates("C").set_index("C")[["FROMNAME", "TONAME", "FROMNUM", "TONUM"]]

    df = (
        pd.concat([pre, post, pdays], axis=1)
        .fillna(0)
        .join(lam_p50)
        .join(lam_mean)
        .join(lam_iqr)
        .join(penalty_share)
        .join(lam_p50_gate)
        .join(names)
    )
    del cv, oc, ex_cap
    gc.collect()
    return df


# ---------------------------------------------------------------------------
# Stage 3: direction-signed impact share vs tofinder MEAN_FLOWDELTA/MEAN_PREFLOW
# ---------------------------------------------------------------------------
def signed_impact(universe: pd.DataFrame, tofinder: pd.DataFrame, dirs: pd.Series) -> pd.DataFrame:
    tf = tofinder.join(dirs, on="CONSTRAINT")
    tf["signed_fd"] = tf.MEAN_FLOWDELTA * tf.DIR.fillna(1)
    top = (
        tf.reindex(tf.signed_fd.abs().sort_values(ascending=False).index)
        .drop_duplicates("CONSTRAINT")
        .set_index("CONSTRAINT")
    )
    df = universe.join(top[["signed_fd", "MEAN_PREFLOW"]], how="left")
    df["share"] = (df.signed_fd / df.MEAN_PREFLOW.abs()).where(df.MEAN_PREFLOW.abs() > 1)
    return df


# ---------------------------------------------------------------------------
# Stage 4: bulk dispatch-node count (NQUAL) from CPNODE_SHIFTS_VIEW, one grouped query
# ---------------------------------------------------------------------------
def bulk_dispatch_nodes(universe: pd.DataFrame, study: int) -> pd.DataFrame:
    cand = universe[(universe.post_binds > 0) | (universe.pre_binds > 0)]
    nq = shifts.cpnode_dispatch_nodes(study, list(cand.index), SF_MIN, SF_MAX)
    nq["C"] = nq["FN"] + "-" + nq["TN"] + "-" + nq["KK"] + "@" + nq["GG"]
    out = universe.join(nq.set_index("C")[["NQUAL", "MAXSF"]], how="left")
    out["NQUAL"] = out.NQUAL.fillna(0).astype(int)
    return out


# ---------------------------------------------------------------------------
# Stage 5: classification (penalty-SHARE test replaces exact-median+IQR test)
# ---------------------------------------------------------------------------
def classify(df: pd.DataFrame) -> pd.DataFrame:
    def flatness_pen(r):
        return pd.notna(r.lam_p50) and r.lam_p50 in PENALTY_TIERS and (r.lam_iqr or 0) < FLATNESS_IQR_MAX

    def penalty_share_pen(r):
        return pd.notna(r.get("penalty_share")) and r.penalty_share > PENALTY_SHARE_MAX

    def cls(r):
        if (r.pre_binds > 0 and r.post_binds == 0) or (pd.notna(r["share"]) and r["share"] < -0.10):
            return "D bearish"
        if flatness_pen(r) or penalty_share_pen(r) or r.NQUAL == 0 or r.NQUAL == 1:
            return "C no-dispatch"
        if r.pre_binds >= max(1, 0.5 * r.post_binds):
            return "B baseline"
        if pd.notna(r["share"]) and r["share"] >= SHARE_MIN:
            return "A target"
        return "weak"

    df = df.copy()
    df["class"] = df.apply(cls, axis=1)
    return df


# ---------------------------------------------------------------------------
# Stage 6: flip detection — D-bearish constraints sharing an endpoint bus with a
# post-only A/weak member that binds under a different contingency.
# ---------------------------------------------------------------------------
def detect_flips(df: pd.DataFrame) -> pd.DataFrame:
    D = df[df["class"] == "D bearish"]
    NEW = df[(df.pre_binds == 0) & (df.post_binds > 0)]
    flips = []
    for c, d in D.iterrows():
        line = ConstraintId.parse(c).line_key
        for b in (d.FROMNUM, d.TONUM):
            hits = NEW[(NEW.FROMNUM == b) | (NEW.TONUM == b)]
            for c2, n in hits.iterrows():
                if ConstraintId.parse(c2).line_key != line:
                    flips.append(
                        {
                            "fades": c,
                            "fades_name": f"{d.FROMNAME}-{d.TONAME}",
                            "pre": int(d.pre_binds),
                            "emerges": c2,
                            "emerges_name": f"{n.FROMNAME}-{n.TONAME}",
                            "post": int(n.post_binds),
                            "shared_bus": int(b),
                        }
                    )
    fl = pd.DataFrame(flips)
    if not fl.empty:
        fl = fl.drop_duplicates(["fades", "emerges"]).sort_values("post", ascending=False)
    return fl


# ---------------------------------------------------------------------------
# Stage 7: stage-2 gate + soft intensity band
# ---------------------------------------------------------------------------
def stage2_gate(
    df: pd.DataFrame,
    flips: pd.DataFrame,
    share_min: float = SHARE_MIN,
    post_days_min: int = POST_DAYS_MIN,
    rent_min: float = RENT_MIN,
    nqual_min: int = NQUAL_MIN,
    intensity_min_hard: float = INTENSITY_MIN_HARD,
    intensity_min_full: float = INTENSITY_MIN_FULL,
) -> pd.DataFrame:
    A = df[df["class"] == "A target"].copy()
    gated = A[
        (A["share"] >= share_min)
        & (A.post_days >= post_days_min)
        & (A.RENT_POST >= rent_min)
        & (A.NQUAL >= nqual_min)
    ].copy()

    flip_targets = set(flips["emerges"]) if not flips.empty else set()
    intensity = gated.post_binds * gated.lam_p50_gate
    gated["intensity"] = intensity
    is_flip_target = gated.index.to_series().isin(flip_targets)
    hard_pass = intensity >= intensity_min_hard
    full_pass = intensity >= intensity_min_full

    keep = hard_pass | is_flip_target
    gated = gated[keep].copy()
    hard_pass, full_pass, is_flip_target = hard_pass[keep], full_pass[keep], is_flip_target[keep]

    gated["flip_exempt"] = is_flip_target & ~hard_pass
    gated["thin_intensity"] = hard_pass & ~full_pass & ~gated["flip_exempt"]
    return gated.sort_values("RENT_POST", ascending=False)


# ---------------------------------------------------------------------------
# Stage 8: HTML render — column-spec driven (header/filter row/body/alignment all
# derive from _columns() so adding a column can't silently misalign the CSS).
# ---------------------------------------------------------------------------
def _columns(rent_col: str) -> list:
    return [
        # (header, accessor(row_dict), kind, css_class)
        ("Label", lambda r: r["Label"], "text", "l"),
        ("From bus", lambda r: r["From bus"], "id", "r"),
        ("From name", lambda r: r["From name"], "text", "l"),
        ("To bus", lambda r: r["To bus"], "id", "r"),
        ("To name", lambda r: r["To name"], "text", "l"),
        ("Ckt", lambda r: r["Ckt"], "text", "l"),
        ("Contingency", lambda r: r["Contingency"], "text", "l"),
        ("Direction", lambda r: r["Direction"], "id", "r"),
        ("Impact share", lambda r: r["Impact share"], "num2", "r"),
        ("Pre binds", lambda r: r["Pre binds"], "int", "r"),
        ("Post binds", lambda r: r["Post binds"], "int", "r"),
        ("Post days (of 5)", lambda r: r["Post days (of 5)"], "int", "r"),
        ("λ avg (all)", lambda r: r["lam avg"], "num1", "r"),
        ("λ P50 (all)", lambda r: r["lam p50"], "num1", "r"),
        ("λ P50 (ex-cap, gate basis)", lambda r: r["lam p50 gate"], "num1", "r"),
        ("Dispatch nodes", lambda r: r["Dispatch nodes"], "int", "r"),
        (rent_col, lambda r: r[rent_col], "money", "r"),
        ("Ticket", lambda r: r["Ticket"], "text", "l"),
        ("Status", lambda r: r["Status"], "text", "l"),
        ("Flip exempt", lambda r: r["Flip exempt"], "bool", "l"),
        ("Thin intensity", lambda r: r["Thin intensity"], "bool", "l"),
    ]


def rent_col_name(cutoff: str) -> str:
    d = pd.Timestamp(cutoff)
    return f"Rent post-{d.month}/{d.day} ($)"


def _fmt(v, kind):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if kind == "id":
        return str(v)  # bus/circuit/direction ids: never comma-formatted
    if kind == "int":
        return f"{int(v):,}"
    if kind == "num1":
        return f"{float(v):.1f}"
    if kind == "num2":
        return f"{float(v):.2f}"
    if kind == "money":
        return f"{round(float(v)):,}"
    if kind == "bool":
        return "True" if v else "False"
    return str(v)


def render_html(gated: pd.DataFrame, cache_dir: str, dirs: pd.Series, study: int, outdir: str,
                cutoff: str) -> pd.DataFrame:
    rent_col = rent_col_name(cutoff)
    br = (
        pd.read_parquet(f"{cache_dir}/outbranch2.parquet", columns=["LABEL", "FROMNUM", "TONUM", "CKT"])
        .drop_duplicates(["FROMNUM", "TONUM", "CKT"])
        .set_index(["FROMNUM", "TONUM", "CKT"])
    )

    rows = []
    for c, r in gated.iterrows():
        cid = ConstraintId.parse(c)
        f, t, ckt, ctg = cid.fromnum, cid.tonum, cid.ckt, cid.ctglabel
        lab = br.loc[(f, t, ckt), "LABEL"] if (f, t, ckt) in br.index else None
        rows.append(
            {
                "Label": lab,
                "From bus": f,
                "From name": r.FROMNAME,
                "To bus": t,
                "To name": r.TONAME,
                "Ckt": ckt,
                "Contingency": ctg,
                "Direction": int(dirs.get(c, 1)),
                "Impact share": r["share"],
                "Pre binds": int(r.pre_binds),
                "Post binds": int(r.post_binds),
                "Post days (of 5)": int(r.post_days),
                "lam avg": r.lam_mean,
                "lam p50": r.lam_p50,
                "lam p50 gate": r.lam_p50_gate,
                "Dispatch nodes": int(r.NQUAL),
                rent_col: r.RENT_POST,
                "Ticket": r.DRIVER_TICKET if pd.notna(r.DRIVER_TICKET) else "",
                "Status": r.DRIVER_TICKET_STATUS if pd.notna(r.DRIVER_TICKET_STATUS) else "",
                "Flip exempt": bool(r.flip_exempt),
                "Thin intensity": bool(r.thin_intensity),
            }
        )
    out = pd.DataFrame(rows).sort_values(rent_col, ascending=False)

    style = """
body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:2rem;color:#1a1a2e;background:#fafafa}
h1{font-size:1.3rem} .meta{color:#555;font-size:.9rem;margin-bottom:1rem;max-width:75rem}
table{border-collapse:collapse;font-size:.82rem;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.12)}
th,td{border:1px solid #ddd;padding:4px 8px;text-align:right;white-space:nowrap}
th{background:#22304a;color:#fff;position:sticky;top:0}
td.l,th.l{text-align:left}
tr:nth-child(even){background:#f4f6fa}
input.f{width:95%;font-size:.72rem;box-sizing:border-box}
"""
    js = """
function flt(){const t=document.getElementById('tb');const ins=[...document.querySelectorAll('input.f')];
[...t.tBodies[0].rows].forEach(r=>{let ok=true;ins.forEach((inp,i)=>{const v=inp.value.trim().toLowerCase();if(!v)return;
const cell=r.cells[i].innerText.trim();const num=parseFloat(cell.replace(/,/g,''));
if(v[0]==='>'&&!isNaN(num)){if(!(num>parseFloat(v.slice(1))))ok=false}
else if(v[0]==='<'&&!isNaN(num)){if(!(num<parseFloat(v.slice(1))))ok=false}
else if(!cell.toLowerCase().includes(v))ok=false;});r.style.display=ok?'':'none';});}
"""
    head = "".join(f"<th class='{cls}'>{h}</th>" for h, _, _, cls in _columns(rent_col))
    filt = "".join(f"<th class='{cls}'><input class='f' oninput='flt()'></th>" for _, _, _, cls in _columns(rent_col))
    body_rows = []
    for _, row in out.iterrows():
        cells = "".join(
            f"<td class='{cls}'>{_fmt(acc(row), kind)}</td>" for _, acc, kind, cls in _columns(rent_col)
        )
        body_rows.append(f"<tr>{cells}</tr>")
    body = "".join(body_rows)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Stage-2 list — study {study}</title>
<style>{style}</style><script>{js}</script></head><body>
<h1>Stage-2 candidates — study {study}, {len(out)} constraints</h1>
<div class="meta">Step-1 screen output after gates (impact share &ge; {SHARE_MIN} direction-corrected, &ge;{POST_DAYS_MIN} of 5 sampled
post-cutoff days, rent &ge; ${RENT_MIN:,}, &ge;{NQUAL_MIN} dispatch nodes), then a soft binding-intensity band on
post_binds &times; &lambda;P50(ex-cap, post-cutoff, non-zero, non-penalty): hard floor {INTENSITY_MIN_HARD}, full pass
{INTENSITY_MIN_FULL}. Rows in the soft band are kept and flagged <b>Thin intensity</b>; rows below the hard floor are
kept only if rescued by the flip-detection heuristic (<b>Flip exempt</b>). C no-dispatch (see step1_screen.csv) uses a
penalty-share test (&gt;{PENALTY_SHARE_MAX*100:.0f}% of LP rows at the {PENALTY_TIERS[0]:.0f}/{PENALTY_TIERS[1]:.0f}
SCOPF penalty cap) plus the legacy flatness test. Direction = OUTBRANCHDIRECTION. Filters accept text or &gt;/&lt; on
numbers.</div>
<table id="tb"><thead><tr>{head}</tr><tr>{filt}</tr></thead><tbody>{body}</tbody></table></body></html>"""
    with open(f"{outdir}/stage2_list.html", "w") as fh:
        fh.write(html)
    return out


# ---------------------------------------------------------------------------
# main(): orchestration + I/O only
# ---------------------------------------------------------------------------
def main() -> None:
    global PENALTY_SHARE_MAX
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--cutoff", required=True, help="pre/post split date YYYY-MM-DD")
    ap.add_argument("--share-min", type=float, default=SHARE_MIN)
    ap.add_argument("--post-days-min", type=int, default=POST_DAYS_MIN)
    ap.add_argument("--rent-min", type=float, default=RENT_MIN)
    ap.add_argument("--nqual-min", type=int, default=NQUAL_MIN)
    ap.add_argument("--intensity-min-hard", type=float, default=INTENSITY_MIN_HARD)
    ap.add_argument("--intensity-min-full", type=float, default=INTENSITY_MIN_FULL)
    ap.add_argument("--penalty-share-max", type=float, default=PENALTY_SHARE_MAX)
    args = ap.parse_args()
    PENALTY_SHARE_MAX = args.penalty_share_max

    study = args.study
    cache = f"powerflow_analytics/cache/study_{study}"
    outdir = f"powerflow_analytics/output/study_{study}"

    runs = pd.read_parquet(f"{cache}/opfrun.parquet", columns=["RUNID", "SIMDATE"])
    runs["post"] = pd.to_datetime(runs.SIMDATE) >= args.cutoff
    sim_lo, sim_hi = runs.SIMDATE.min(), runs.SIMDATE.max()
    if not (sim_lo <= pd.to_datetime(args.cutoff) <= sim_hi):
        print(f"WARNING: --cutoff {args.cutoff} falls outside this study's SIMDATE range [{sim_lo}, {sim_hi}]")

    # Stage 1
    dirs = constraint_directions(cache)
    dirs.to_frame().to_csv(f"{outdir}/constraint_dirs.csv")
    print("-> constraint_dirs.csv | direction distribution:", dirs.value_counts().to_dict())

    # Stage 2
    df = build_universe(cache, runs, args.cutoff)

    rk = (
        pd.read_csv(f"{outdir}/ranked_constraints.csv", low_memory=False)
        .drop_duplicates("CONSTRAINT")
        .set_index("CONSTRAINT")
    )
    df = df.join(rk[["TOTAL_RENT", "RENT_POST", "DRIVER_TICKET", "DRIVER_TICKET_STATUS"]], how="left")

    # Stage 3
    tf = pd.read_csv(f"{outdir}/tofinder_summary.csv")
    df = signed_impact(df, tf, dirs)

    # Stage 4
    df = bulk_dispatch_nodes(df, study)

    # Stage 5
    df = classify(df)

    # Stage 6
    fl = detect_flips(df)
    fl.to_csv(f"{outdir}/step1_flips.csv", index=False)

    print("FUNNEL:", df["class"].value_counts().to_dict(), "| universe:", len(df))
    print()
    print("=== FLIP PAIRS (baseline fades -> new binder emerges, shared bus) ===")
    print(fl.head(15).to_string(index=False) if not fl.empty else "(none)")

    df.sort_values(["class", "RENT_POST"], ascending=[True, False]).to_csv(f"{outdir}/step1_screen.csv")
    print()
    print(f"-> {outdir}/step1_screen.csv + step1_flips.csv")

    # Stage 7
    gated = stage2_gate(
        df, fl,
        share_min=args.share_min, post_days_min=args.post_days_min, rent_min=args.rent_min,
        nqual_min=args.nqual_min, intensity_min_hard=args.intensity_min_hard,
        intensity_min_full=args.intensity_min_full,
    )
    gated.to_csv(f"{outdir}/stage2_list.csv")

    print()
    print(f"STAGE-2 LIST — {len(gated)} constraints")
    show = [
        "FROMNAME", "TONAME", "share", "pre_binds", "post_binds", "post_days", "lam_p50_gate",
        "intensity", "NQUAL", "RENT_POST", "flip_exempt", "thin_intensity",
        "DRIVER_TICKET", "DRIVER_TICKET_STATUS",
    ]
    print(gated[show].round(2).to_string())

    # rows that cleared the stage-2 gate but were hard-dropped by intensity (for the report)
    A = df[df["class"] == "A target"]
    gate_only = A[
        (A["share"] >= args.share_min)
        & (A.post_days >= args.post_days_min)
        & (A.RENT_POST >= args.rent_min)
        & (A.NQUAL >= args.nqual_min)
    ].copy()
    flip_targets = set(fl["emerges"]) if not fl.empty else set()
    gate_only["intensity"] = gate_only.post_binds * gate_only.lam_p50_gate
    dropped = gate_only[
        (gate_only["intensity"] < args.intensity_min_hard) & (~gate_only.index.to_series().isin(flip_targets))
    ]
    print()
    print("=== rows dropped by the hard intensity floor ===")
    if not dropped.empty:
        print(dropped[["FROMNAME", "TONAME", "post_binds", "lam_p50_gate", "intensity"]].round(2).to_string())
    else:
        print("(none)")

    # Stage 8
    out = render_html(gated, cache, dirs, study, outdir, args.cutoff)
    print()
    print(f"-> {outdir}/stage2_list.html | {outdir}/stage2_list.csv | {len(out)} rows")


if __name__ == "__main__":
    main()
