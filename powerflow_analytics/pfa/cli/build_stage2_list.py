"""Shortlist of CRR candidates for one study: screening (pfa.analysis.screening) + month valuation -> CSVs + HTML.

Usage:
    uv run pfa shortlist --study 14431 --cutoff 2026-09-15 --month 2026-09
"""
from __future__ import annotations

import argparse

import pandas as pd

from pfa import config, periods
from pfa.analysis.screening import PENALTY_TIERS, Thresholds, screen_study
from pfa.analysis.shortlist_value import value_columns, value_shortlist
from pfa.constraint_id import ConstraintId


# HTML render — column-spec driven (header/filter row/body/alignment all
# derive from _columns() so adding a column can't silently misalign the CSS).
def _columns(rent_col: str, label: str) -> list:
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
        (f"Outage days in {label}", lambda r: r[f"Outage days in {label}"], "int", "r"),
        ("Coverage", lambda r: r["coverage"], "text", "r"),
        ("Thin window", lambda r: r["thin window evidence"], "text", "l"),
        (f"P(bind) {label} on-peak", lambda r: r[f"P(bind) {label} on-peak"], "num3", "r"),
        ("E[lambda|bind]", lambda r: r["E[lambda|bind]"], "num1", "r"),
        ("lambda P50", lambda r: r["lambda P50"], "num1", "r"),
        ("lambda P90", lambda r: r["lambda P90"], "num1", "r"),
        ("Unpriced deep hours %", lambda r: r["unpriced deep hours %"], "num1", "r"),
        (f"{label} value $/MWh/SF", lambda r: r[f"{label} value $/MWh/SF"], "num3", "r"),
        ("Path", lambda r: r["Path"], "text", "l"),
        ("Path SF", lambda r: r["Path SF"], "text", "r"),
        ("Edge $", lambda r: r["Edge $"], "num2", "r"),
        ("Valuation status", lambda r: r["status"], "text", "l"),
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
    if kind == "num3":
        return f"{float(v):.3f}"
    if kind == "num2":
        return f"{float(v):.2f}"
    if kind == "money":
        return f"{round(float(v)):,}"
    if kind == "bool":
        return "True" if v else "False"
    return str(v)


def render_html(gated: pd.DataFrame, cache_dir: str, dirs: pd.Series, study: int, outdir: str,
                cutoff: str, th: Thresholds, month: str) -> pd.DataFrame:
    rent_col = rent_col_name(cutoff)
    label = periods.month_label(month)
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
                **{k: r[k] for k in value_columns(month)},
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
    head = "".join(f"<th class='{cls}'>{h}</th>" for h, _, _, cls in _columns(rent_col, label))
    filt = "".join(f"<th class='{cls}'><input class='f' oninput='flt()'></th>" for _, _, _, cls in _columns(rent_col, label))
    body_rows = []
    for _, row in out.iterrows():
        cells = "".join(
            f"<td class='{cls}'>{_fmt(acc(row), kind)}</td>" for _, acc, kind, cls in _columns(rent_col, label)
        )
        body_rows.append(f"<tr>{cells}</tr>")
    body = "".join(body_rows)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Stage-2 list — study {study}</title>
<style>{style}</style><script>{js}</script></head><body>
<h1>Stage-2 candidates — study {study}, {len(out)} constraints</h1>
<div class="meta">Step-1 screen output after gates (impact share &ge; {th.share_min} direction-corrected, &ge;{th.post_days_min} of 5 sampled
post-cutoff days, rent &ge; ${th.rent_min:,}, &ge;{th.nqual_min} dispatch nodes), then a soft binding-intensity band on
post_binds &times; &lambda;P50(ex-cap, post-cutoff, non-zero, non-penalty): hard floor {th.intensity_min_hard}, full pass
{th.intensity_min_full}. Rows in the soft band are kept and flagged <b>Thin intensity</b>; rows below the hard floor are
kept only if rescued by the flip-detection heuristic (<b>Flip exempt</b>). C no-dispatch (see step1_screen.csv) uses a
penalty-share test (&gt;{th.penalty_share_max*100:.0f}% of LP rows at the {PENALTY_TIERS[0]:.0f}/{PENALTY_TIERS[1]:.0f}
SCOPF penalty cap) plus the legacy flatness test. Direction = OUTBRANCHDIRECTION. Filters accept text or &gt;/&lt; on
numbers.</div>
<table id="tb"><thead><tr>{head}</tr><tr>{filt}</tr></thead><tbody>{body}</tbody></table></body></html>"""
    with open(f"{outdir}/stage2_list.html", "w") as fh:
        fh.write(html)
    return out


# ---------------------------------------------------------------------------
def main(argv=None) -> None:
    d = Thresholds()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--cutoff", required=True, help="pre/post split date YYYY-MM-DD")
    ap.add_argument("--month", required=True, help="settlement month YYYY-MM to value the shortlist for")
    ap.add_argument("--share-min", type=float, default=d.share_min)
    ap.add_argument("--post-days-min", type=int, default=d.post_days_min)
    ap.add_argument("--rent-min", type=float, default=d.rent_min)
    ap.add_argument("--nqual-min", type=int, default=d.nqual_min)
    ap.add_argument("--intensity-min-hard", type=float, default=d.intensity_min_hard)
    ap.add_argument("--intensity-min-full", type=float, default=d.intensity_min_full)
    ap.add_argument("--penalty-share-max", type=float, default=d.penalty_share_max)
    args = ap.parse_args(argv)

    th = Thresholds(
        share_min=args.share_min, post_days_min=args.post_days_min, rent_min=args.rent_min,
        nqual_min=args.nqual_min, intensity_min_hard=args.intensity_min_hard,
        intensity_min_full=args.intensity_min_full, penalty_share_max=args.penalty_share_max,
    )
    study = args.study
    cache = config.CACHE_ROOT / f"study_{study}"
    outdir = config.OUTPUT_ROOT / f"study_{study}"

    res = screen_study(study, args.cutoff, th)

    res.dirs.to_frame().to_csv(f"{outdir}/constraint_dirs.csv")
    print("-> constraint_dirs.csv | direction distribution:", res.dirs.value_counts().to_dict())

    fl = res.flips
    fl.to_csv(f"{outdir}/step1_flips.csv", index=False)
    print("FUNNEL:", res.universe["class"].value_counts().to_dict(), "| universe:", len(res.universe))
    print()
    print("=== FLIP PAIRS (baseline fades -> new binder emerges, shared bus) ===")
    print(fl.head(15).to_string(index=False) if not fl.empty else "(none)")

    res.universe.to_csv(f"{outdir}/step1_screen.csv")
    print()
    print(f"-> {outdir}/step1_screen.csv + step1_flips.csv")

    gated = value_shortlist(res, args.month)
    gated.to_csv(f"{outdir}/stage2_list.csv")

    print()
    print(f"STAGE-2 LIST — {len(gated)} constraints")
    show = [
        "FROMNAME", "TONAME", "share", "pre_binds", "post_binds", "post_days", "lam_p50_gate",
        "intensity", "NQUAL", "RENT_POST", "flip_exempt", "thin_intensity",
        "DRIVER_TICKET", "DRIVER_TICKET_STATUS",
    ]
    print(gated[show].round(2).to_string())

    dropped = res.intensity_dropped
    print()
    print("=== rows dropped by the hard intensity floor ===")
    if not dropped.empty:
        print(dropped[["FROMNAME", "TONAME", "post_binds", "lam_p50_gate", "intensity"]].round(2).to_string())
    else:
        print("(none)")

    out = render_html(gated, cache, res.dirs, study, outdir, args.cutoff, th, args.month)
    print()
    print(f"-> {outdir}/stage2_list.html | {outdir}/stage2_list.csv | {len(out)} rows")

