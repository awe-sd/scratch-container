#!/usr/bin/env python3
"""PathOpt scatter: find paths that are LONG both constraints and CHEAP.

Usage:
    uv run --with "pyopenssl>=26.4" --project powerflow_analytics python \\
        powerflow_analytics/scripts/pathopt_scatter.py \\
        --study 14835 --run-x 10008060 --run-y 10008041 \\
        --date 2026-11-10 --hour 18 --top 100000 --min-sf 0.05

N-run mode (overlap of several PathOpt runs, pair search; --study = context study for binding stats):
    ... pathopt_scatter.py --study 14966 --out-dir output/pathopt/14966_dblbywf5 --min-sf 0.02 --holidays 2026-12-25 \\
        --runs JCKSTP18A=10023193,JCKREF27A=10023204,BLESSING1382=10023214,BLESSI_PAVLOV11=10023147 \\
        --required JCKSTP18A,JCKREF27A,BLESSING1382 \\
        --constraints JCKSTP18A=5915-42530-18@DBLBYWF5,JCKREF27A=42400-42530-27@DBLBYWF5,BLESSING1382=8121-8123-1@DBLBYWF5,BLESSI_PAVLOV11=8121-8614-1@DBLBYWF5
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Resolve sys.path from __file__
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent))

from pfa.analysis import path_scatter
from pfa.constraint_id import ConstraintId
from pfa.extract import popt


def run_multi(args):
    import numpy as np
    out = Path(args.out_dir or SCRIPT_DIR.parent / "output" / "pathopt" / f"{args.study}_multi")
    out.mkdir(parents=True, exist_ok=True)
    parse = lambda txt: {k: int(v) for k, v in (x.split("=") for x in txt.split(",") if x)}
    runs = parse(args.runs)
    vruns = parse(args.value_only or "")
    labels = list(runs)
    vlabels = list(vruns)
    alll = labels + vlabels
    required = args.required.split(",") if args.required else labels[:-1]
    floor = args.min_sf_each
    cons = {}
    for x in (args.constraints or "").split(","):
        if x:
            lab, c = x.split("=")
            cid = ConstraintId.parse(c)
            cons[lab] = (cid.fromnum, cid.tonum, cid.ckt, cid.ctglabel)
    cfg = {l: popt.get_run_config(r) for l, r in {**runs, **vruns}.items()}

    mem = {l: popt.get_topology_set_members(cfg[l].TOPOLOGYSHIFTSETID) for l in alll}
    onp = {l: path_scatter.onpeak_members(mem[l]) for l in alll}
    topo = sorted(set.intersection(*[set(onp[l]["TOPOLOGYID"]) for l in alll]))
    assert all(set(onp[l]["TOPOLOGYID"]) == set(topo) for l in alll), "on-peak topologies differ between runs"
    ps_of = {l: onp[l].drop_duplicates("TOPOLOGYID").set_index("TOPOLOGYID")["PSENSHIFTID"].reindex(topo) for l in alll}
    topo_date = onp[labels[0]].groupby("TOPOLOGYID")["SIMDATE"].agg(lambda s: sorted(set(pd.to_datetime(s).dt.strftime("%Y-%m-%d"))))
    hol = set(args.holidays.split(",")) if args.holidays else set()
    hol_cols = [i for i, t in enumerate(topo) if hol & set(topo_date[t])]
    keep_cols = [i for i in range(len(topo)) if i not in hol_cols]
    print(f"{len(topo)} on-peak periods; holiday periods {[topo[i] for i in hol_cols]}")

    cols = ["SOURCECPNODEID", "SINKCPNODEID", "SOURCENAME", "SINKNAME", "SOURCEBUSKV", "SINKBUSKV", "OPTIONPRICE",
            "MIN_SF", "AVG_SF", "MAX_SF", "SHADOWPRICEPRECENT", "BINDINGPAIRCOUNT"]
    details = {l: popt.fetch_detail({**runs, **vruns}[l], cols) for l in alll}
    for d in details.values():
        for c in ("MIN_SF", "AVG_SF", "MAX_SF", "SHADOWPRICEPRECENT", "SOURCEBUSKV", "SINKBUSKV"):
            d[c] = d[c].astype("float32")
        d["BINDINGPAIRCOUNT"] = d["BINDINGPAIRCOUNT"].astype("int16")
    U, price_cons = path_scatter.overlap_runs(details, required)
    del details
    counts = path_scatter.overlap_counts(U, labels, required)
    print(counts.to_string(index=False)); print(price_cons.to_string(index=False))
    counts.to_csv(out / "overlap_counts.csv", index=False)

    S, repro, live_cols = {}, [], {}
    for l in alll:
        n = popt.get_node_shift_factors_multi(list(ps_of[l].values))
        ps2t = dict(zip(ps_of[l].values, topo))
        n["T"] = n["PSENSHIFTID"].map(ps2t)
        P = n.pivot(index="CPNODEID", columns="T", values="PSENS")[topo]
        D = n.pivot(index="CPNODEID", columns="T", values="DEADBUS")[topo]
        S0 = path_scatter.path_sf_matrix(U, P, D)
        sign = 1.0
        row, sign = path_scatter.reproduction_check(U, S0, l, cfg[l].DIRECTION)
        repro.append(row)
        S[l] = sign * S0
        live_cols[l] = (P.abs().max(axis=0) > 1e-3).values
        del n, P, D
    repro = pd.DataFrame(repro)
    print(repro.T.to_string())

    o0 = onp[labels[0]]
    runids = sorted(set(o0.loc[~pd.to_datetime(o0["SIMDATE"]).dt.strftime("%Y-%m-%d").isin(hol), "RUNID"]))
    n_runs = len(runids)
    sp_scale, weights, sp_rows = {}, {}, []
    for l in alll:
        f, t, ckt, ctg = cons[l]
        sp = popt.fetch_constraint_sp(runids, f, t, ckt, ctg).set_index("RUNID")["SP"].reindex(runids).fillna(0.0)
        r2t = onp[l].drop_duplicates("RUNID").set_index("RUNID")["TOPOLOGYID"]
        weights[l] = sp.groupby(r2t.reindex(runids).values).sum().reindex(topo).fillna(0.0).values
        sp_scale[l] = float(sp.sum() / n_runs)
        sp_rows.append({"constraint": l, "pathopt_study": int(cfg[l].STUDYID), "n_onpeak_runs_exholiday": n_runs,
                        "n_runs_with_sp": int((sp > 0).sum()), "mean_sp_when_present": float(sp[sp > 0].mean()) if (sp > 0).any() else 0.0,
                        "sp_scale_zero_imputed": sp_scale[l]})
    sp_tab = pd.DataFrame(sp_rows); print(sp_tab.to_string(index=False)); sp_tab.to_csv(out / "pathopt_study_sp_scale.csv", index=False)

    # PathOpt MIN_SF spans all periods incl. topologies where the constraint carries no flow (psens all zero) -> pinned at 0.
    # Re-base on LIVE periods; MINB/AVGB = periods where the constraint binds in the PathOpt study. *_EXHOL drop holiday periods.
    per = pd.DataFrame({"TOPOLOGYID": topo, "DATES": [",".join(topo_date[t]) for t in topo]})
    for l in alll:
        bind = weights[l] > 0
        per[f"LIVE_{l}"], per[f"SPSUM_{l}"] = live_cols[l], weights[l]
        S[l] = np.where(live_cols[l][None, :], S[l], np.nan).astype(np.float32)
        st = path_scatter.sf_stats(S[l])
        stb = path_scatter.sf_stats(np.where(bind[None, :], S[l], np.nan))
        ste = path_scatter.sf_stats(S[l][:, keep_cols])
        for q in ("MIN_SF", "AVG_SF", "MAX_SF"):
            U[f"PO_{q}_{l}"] = U[f"{q}_{l}"]
            U[f"{q}_{l}"] = st[q].values
        U[f"MIN_SF_{l}_EXHOL"] = ste["MIN_SF"].values
        U[f"MINB_SF_{l}"], U[f"AVGB_SF_{l}"] = stb["MIN_SF"].values, stb["AVG_SF"].values
        U[f"NLIVE_{l}"], U[f"NBIND_{l}"] = st["BINDINGPAIRCOUNT"].values, stb["BINDINGPAIRCOUNT"].values
        print(f"{l}: live periods {int(live_cols[l].sum())}/{len(topo)}, binding periods {int(bind.sum())}")
    per.to_csv(out / "periods.csv", index=False)

    for l in alll:
        live = ~np.isnan(S[l]); w = weights[l][None, :] * live
        rec = 100 * (w * np.nan_to_num(S[l])).sum(1) / np.maximum(w.sum(1), 1e-12)
        m = U[f"IN_{l}"].values
        if m.any():
            c = np.corrcoef(rec[m], U.loc[m, f"SHADOWPRICEPRECENT_{l}"].values)[0, 1]
            repro.loc[repro.constraint == l, "spp_reconstruction_corr"] = c
        U[f"SHADOWPRICEPRECENT_{l}"] = np.where(m, U[f"SHADOWPRICEPRECENT_{l}"], rec)
    repro.to_csv(out / "reproduction_check.csv", index=False)
    U = path_scatter.add_value_columns(U, alll, required, sp_scale)
    nonreq = [l for l in alll if l not in required]
    for l in nonreq:
        U[f"SHORT_{l}"] = (U[f"AVG_SF_{l}"] < -0.02) & (U[f"NBIND_{l}"] > 0)
    U["SHORT_FLAG"] = U[[f"SHORT_{l}" for l in nonreq]].any(axis=1)

    U = U.drop(columns=[c for c in U.columns if c.startswith("PO_")])
    f64 = [c for c in U.columns if U[c].dtype == "float64" and c != "OPTIONPRICE" and not c.startswith("VALUE")]
    U[f64] = U[f64].astype("float32")
    ov = U[np.logical_and.reduce([U[f"IN_{l}"] for l in required])].copy()
    mn = lambda frame, suf="": frame[[f"MIN_SF_{l}{suf}" for l in required]].min(axis=1)
    floors = {f: int((mn(ov) >= f).sum()) for f in (0.0, 0.02, 0.05, 0.10)}
    floors_b = {f: int((ov[[f"MINB_SF_{l}" for l in required]].min(axis=1) >= f).sum()) for f in (0.0, 0.02, 0.05, 0.10)}
    pa, pe = (mn(ov) >= floor), (mn(ov, "_EXHOL") >= floor)
    hs = {"floor": floor, "pass": int(pa.sum()), "lost_without_holiday": int((pa & ~pe).sum()), "gained_without_holiday": int((~pa & pe).sum())}
    print("overlap(required):", len(ov), "balanced filter counts", floors, "| binding-MIN", floors_b, "| holiday", hs)
    ov["MIN_SF_REQ"] = mn(ov)
    ov.drop(columns=[c for c in ov.columns if c.startswith("WAVG_DOLLAR")]).to_parquet(out / "paths_all.parquet", index=False)
    ptt, cand = path_scatter.rank_single(ov, required, floor)
    sfcols = [f"{q}_{l}" for l in alll for q in ("MIN_SF", "AVG_SF")]
    cand_d = path_scatter.dedup_multi(cand, sfcols, decimals=3, order=["OPTIONPRICE", "SOURCENAME", "SINKNAME"]) if len(cand) else cand
    cand_d["NET_REQ"] = cand_d["VALUE_REQ"] - cand_d["OPTIONPRICE"]
    cand_d["VO_SHARE"] = (cand_d["VALUE_ALL"] - cand_d["VALUE_REQ"]) / cand_d["VALUE_ALL"]
    cand_d = cand_d.sort_values("NET", ascending=False).reset_index(drop=True)
    cand_d["MEMBER"] = cand_d["SOURCENAME"] + "→" + cand_d["SINKNAME"] + "($" + cand_d["OPTIONPRICE"].round(2).astype(str) + ")"
    cand_d = path_scatter.add_families(cand_d, sfcols, "MEMBER")
    fam = cand_d[cand_d["FAMILY_RANK"] == 1].head(30)
    fam.to_csv(out / "candidates_families.csv", index=False)
    # near-miss: passes the floor on all required legs but one, which sits in [0.4*floor, floor)
    reqmin = ov[[f"MIN_SF_{l}" for l in required]]
    nfail = (reqmin < floor).sum(axis=1)
    nm = ov[(nfail == 1) & (reqmin.min(axis=1) >= 0.4 * floor) & (ov["OPTIONPRICE"] > 0)].copy()
    nm["FAILING_LEG"] = reqmin.loc[nm.index].idxmin(axis=1).str.replace("MIN_SF_", "")
    nm["NET"], nm["NET_REQ"] = nm["VALUE_ALL"] - nm["OPTIONPRICE"], nm["VALUE_REQ"] - nm["OPTIONPRICE"]
    nm["RATIO"] = nm["VALUE_ALL"] / nm["OPTIONPRICE"]
    nm = path_scatter.dedup_multi(nm, sfcols, decimals=3, order=["OPTIONPRICE", "SOURCENAME", "SINKNAME"]).sort_values("NET", ascending=False)
    nm["MEMBER"] = nm["SOURCENAME"] + "→" + nm["SINKNAME"] + "($" + nm["OPTIONPRICE"].round(2).astype(str) + ")"
    nm = path_scatter.add_families(nm, sfcols, "MEMBER")
    nm_f = nm[nm["FAMILY_RANK"] == 1].head(15)
    nm_f.to_csv(out / "near_miss.csv", index=False)
    ptt_d = path_scatter.dedup_multi(ptt, sfcols, decimals=3, order=["OPTIONPRICE", "SOURCENAME", "SINKNAME"]) if len(ptt) else ptt
    keepcols = (["SOURCENAME", "SINKNAME", "ALIAS_COUNT", "ALIASES", "SOURCEBUSKV", "SINKBUSKV", "OPTIONPRICE"]
                + [f"{s}_{l}" for l in alll for s in ("MIN_SF", "AVG_SF", "MIN_SF_EXHOL" if False else "MAX_SF")]
                + [f"MIN_SF_{l}_EXHOL" for l in alll] + [f"MINB_SF_{l}" for l in required]
                + [f"VALUE_{l}" for l in alll] + ["VALUE_REQ", "VALUE_ALL", "SHORT_FLAG", "MIN_SF_REQ", "NET", "NET_REQ", "VO_SHARE", "RATIO",
                                             "FAMILY", "FAMILY_RANK", "FAMILY_SIZE", "FAMILY_MEMBERS"])
    cand_d[[c for c in keepcols if c in cand_d]].head(50).to_csv(out / "candidates_single.csv", index=False)
    print(f"single candidates (floor {floor}): {len(cand)} raw, {len(cand_d)} distinct (3dp SF dedup); paid-to-take {len(ptt_d)}")

    # pairs over the union; S comes from node psens so paths PathOpt dropped for a run still count
    in_req = np.logical_or.reduce([U[f"IN_{l}"] for l in required]) & (U["OPTIONPRICE"] > 0)
    ridx = np.flatnonzero(in_req.values)
    Uq = U.iloc[ridx]
    sigm = np.round(np.hstack([S[k][ridx] for k in alll]), 3)
    sig = pd.util.hash_pandas_object(pd.DataFrame(sigm).fillna(-9e9), index=False).values
    pool_idx = set()
    for key in [f"VALUE_{l}" for l in required] + ["VALUE_ALL"]:
        r = (Uq[key] / Uq["OPTIONPRICE"]).values
        d = pd.DataFrame({"r": r, "sig": sig, "i": np.arange(len(Uq))}).sort_values("r", ascending=False).drop_duplicates("sig")
        pool_idx |= set(d.head(args.pool)["i"])
    pool_pos = np.array(sorted(pool_idx))
    pool = Uq.iloc[pool_pos].reset_index(drop=True)
    Sp = {k: S[k][ridx][pool_pos] for k in alll}
    print("pair pool:", len(pool))
    pairs = path_scatter.find_pairs(pool, Sp, required, floor, extra=nonreq, value_col="VALUE_ALL", per_mw=True)
    pool["PASS_ALONE"] = (pool[[f"MIN_SF_{l}" for l in required]] >= floor).all(axis=1)
    if len(pairs):
        pairs = pairs[~(pool["PASS_ALONE"].values[pairs["A"]] | pool["PASS_ALONE"].values[pairs["B"]])]
        pairs = pairs[pool["SOURCENAME"].values[pairs["A"]] + pool["SINKNAME"].values[pairs["A"]] != pool["SOURCENAME"].values[pairs["B"]] + pool["SINKNAME"].values[pairs["B"]]]
    if len(pairs):
        sh = np.zeros(len(pairs), dtype=bool)
        for l in nonreq:
            if (U[f"NBIND_{l}"] > 0).any():
                sh |= (pairs[f"AVG_SF_{l}"].values < -0.02) & bool(per[f"SPSUM_{l}"].gt(0).any())
        pairs["SHORT_FLAG"] = sh
        for side in ("A", "B"):
            pairs[f"{side}_PATH"] = pool.loc[pairs[side], "SOURCENAME"].values + "→" + pool.loc[pairs[side], "SINKNAME"].values
            pairs[f"{side}_PRICE"] = pool.loc[pairs[side], "OPTIONPRICE"].values
        pairs["VALUE_REQ"] = pool["VALUE_REQ"].values[pairs["A"]] + pool["VALUE_REQ"].values[pairs["B"]]
        pairs = pairs.drop(columns=["A", "B"]).drop_duplicates([c for c in pairs.columns if c.startswith(("MIN_SF_", "AVG_SF_"))] + ["PRICE"])
        pairs = pairs.rename(columns={"PRICE": "PRICE_2MW", "VALUE_ALL": "VALUE_ALL_2MW", "VALUE_REQ": "VALUE_REQ_2MW", "NET": "NET_2MW"})
        pairs["PRICE_PER_MW"], pairs["VALUE_ALL_PER_MW"] = pairs["PRICE_2MW"] / 2, pairs["VALUE_ALL_2MW"] / 2
        pairs["NET_REQ_PER_MW"] = (pairs["VALUE_REQ_2MW"] - pairs["PRICE_2MW"]) / 2
        pairs["VO_SHARE"] = 1 - pairs["VALUE_REQ_2MW"] / pairs["VALUE_ALL_2MW"]
        pairs = pairs.sort_values("NET_PER_MW", ascending=False).reset_index(drop=True)
        pairs["MEMBER"] = pairs["A_PATH"] + " + " + pairs["B_PATH"]
        pairs = path_scatter.add_families(pairs, [c for c in pairs.columns if c.startswith(("MIN_SF_", "AVG_SF_")) and c != "MIN_SF_REQ"], "MEMBER")
    pairs_c = pairs
    pairs_c.head(50).to_csv(out / "candidates_pairs.csv", index=False)
    if len(pairs_c):
        pairs_c[pairs_c["FAMILY_RANK"] == 1].head(30).to_csv(out / "candidates_pair_families.csv", index=False)
    anyp = out / "candidates_pairs_any.csv"
    if anyp.exists():
        anyp.unlink()
    print(f"complementary pairs: {len(pairs_c)}; best NET_PER_MW {pairs_c['NET_PER_MW'].max() if len(pairs_c) else None}; best single NET {cand_d['NET'].max() if len(cand_d) else None}")

    ctx, ctx_sum = None, None
    if cons and args.study:
        sruns = popt.fetch_study_runs(args.study)
        sruns["SIMDATE"] = pd.to_datetime(sruns["SIMDATE"])
        sruns["ONPEAK"] = (sruns["SIMDATE"].dt.dayofweek < 5) & sruns["SIMHOUR"].between(7, 22)
        sruns["HOLIDAY"] = sruns["SIMDATE"].dt.strftime("%Y-%m-%d").isin(hol)
        ctx = sruns.set_index("RUNID")
        summ = []
        n_on = int((ctx["ONPEAK"] & ~ctx["HOLIDAY"]).sum())
        for l in alll:
            f, t, ckt, ctg = cons[l]
            lv = popt.fetch_ctg_loading(args.study, f, t, ckt, ctg).set_index("RUNID")["LIMVIOLPCT"]
            sp = popt.fetch_constraint_sp(list(ctx.index), f, t, ckt, ctg).set_index("RUNID")["SP"]
            ctx[f"LIMVIOLPCT_{l}"] = lv.reindex(ctx.index)
            ctx[f"SP_{l}"] = sp.reindex(ctx.index)
            b = ctx[f"LIMVIOLPCT_{l}"] >= 99.5
            ctx[f"BINDING_{l}"] = b
            on = ctx["ONPEAK"]
            summ.append({"constraint": l, "n_onpeak_runs_exholiday": n_on, "onpeak_binding_runs": int((b & on).sum()),
                         "onpeak_binding_on_holiday": int((b & on & ctx["HOLIDAY"]).sum()),
                         "binding_missing_sp": int((b & on & ctx[f"SP_{l}"].isna()).sum()),
                         "mean_sp_present": float(ctx.loc[b & on, f"SP_{l}"].mean()),
                         "mean_sp_zero_imputed_over_binders": float(ctx.loc[b & on, f"SP_{l}"].fillna(0).mean()),
                         "onpeak_mean_sp_all_runs_exholiday": float(ctx.loc[on & ~ctx["HOLIDAY"], f"SP_{l}"].fillna(0).sum() / n_on)})
        ctx_sum = pd.DataFrame(summ); print(ctx_sum.to_string(index=False))
        ctx.reset_index().to_csv(out / "binding_runs.csv", index=False)
        ctx_sum.to_csv(out / "binding_summary.csv", index=False)
    corr_u = pd.DataFrame({l: U[f"AVG_SF_{l}"] for l in alll}).corr()
    corr_o = pd.DataFrame({l: ov[f"AVG_SF_{l}"] for l in alll}).corr()
    both = {f"{a}&{b}": float(((ov[f"AVG_SF_{a}"] > 0) & (ov[f"AVG_SF_{b}"] > 0)).mean()) for i, a in enumerate(alll) for b in alll[i + 1:]}
    print("AVG-SF corr on overlap(required)\n", corr_o.round(3).to_string())

    path_scatter.build_multi_report(out, args, alll, required, {**runs, **vruns}, cfg, counts, price_cons, repro, sp_tab, ctx_sum, ov, cand_d, ptt_d,
                                    pairs_c, corr_u, corr_o, both, floors, hs, per, floors_b, sp_scale, n_runs, fam, nm_f)
    print("wrote", out)


def run_spread(args):
    """Long A / short B spread search (and the reverse): universe = PathOpt run A paths, B/other legs from their sets."""
    import numpy as np
    out = Path(args.out_dir or SCRIPT_DIR.parent / "output" / "pathopt" / f"{args.study}_spread")
    out.mkdir(parents=True, exist_ok=True)
    parse = lambda txt: {k: int(v) for k, v in (x.split("=") for x in txt.split(",") if x)}
    runs, vruns = parse(args.runs), parse(args.value_only or "")
    alll = list(runs) + list(vruns)
    longs, shorts = args.required.split(","), args.short.split(",")
    assert len(longs) == 1, "spread mode: exactly one long leg per direction"
    dirs = [(longs[0], shorts)]
    if len(shorts) == 1:
        dirs.append((shorts[0], longs))
    floor = args.min_sf_each
    cons = {}
    for x in args.constraints.split(","):
        lab, c = x.split("=")
        cid = ConstraintId.parse(c)
        cons[lab] = (cid.fromnum, cid.tonum, cid.ckt, cid.ctglabel)
    cfg = {l: popt.get_run_config(r) for l, r in {**runs, **vruns}.items()}
    mem = {l: popt.get_topology_set_members(cfg[l].TOPOLOGYSHIFTSETID) for l in alll}
    onp = {l: path_scatter.onpeak_members(mem[l]) for l in alll}
    topo = sorted(set.intersection(*[set(onp[l]["TOPOLOGYID"]) for l in alll]))
    ps_of = {l: onp[l].drop_duplicates("TOPOLOGYID").set_index("TOPOLOGYID")["PSENSHIFTID"].reindex(topo) for l in alll}
    topo_date = onp[alll[0]].groupby("TOPOLOGYID")["SIMDATE"].agg(lambda s: sorted(set(pd.to_datetime(s).dt.strftime("%Y-%m-%d"))))
    hol = set(args.holidays.split(",")) if args.holidays else set()
    keep_cols = [i for i, t in enumerate(topo) if not (hol & set(topo_date[t]))]
    o0 = onp[alll[0]]
    runids = sorted(set(o0.loc[~pd.to_datetime(o0["SIMDATE"]).dt.strftime("%Y-%m-%d").isin(hol), "RUNID"]))
    n_runs = len(runids)
    r2t = o0.drop_duplicates("RUNID").set_index("RUNID")["TOPOLOGYID"].reindex(runids)
    tidx = np.array([topo.index(t) for t in r2t.values])

    P, D, live_cols, sp_run, weights, sp_scale = {}, {}, {}, {}, {}, {}
    for l in alll:
        n = popt.get_node_shift_factors_multi(list(ps_of[l].values))
        n["T"] = n["PSENSHIFTID"].map(dict(zip(ps_of[l].values, topo)))
        P[l] = n.pivot(index="CPNODEID", columns="T", values="PSENS")[topo]
        D[l] = n.pivot(index="CPNODEID", columns="T", values="DEADBUS")[topo]
        live_cols[l] = (P[l].abs().max(axis=0) > 1e-3).values
        f, t, ckt, ctg = cons[l]
        sp = popt.fetch_constraint_sp(runids, f, t, ckt, ctg).set_index("RUNID")["SP"].reindex(runids).fillna(0.0)
        sp_run[l] = sp.values
        weights[l] = sp.groupby(r2t.values).sum().reindex(topo).fillna(0.0).values
        sp_scale[l] = float(sp.sum() / n_runs)
        del n
    cols = ["SOURCECPNODEID", "SINKCPNODEID", "SOURCENAME", "SINKNAME", "OPTIONPRICE", "SHADOWPRICEPRECENT"]
    details = {l: popt.fetch_detail({**runs, **vruns}[l], cols) for l in alll}
    both_live = {}
    for a in alll:
        for b_ in alll:
            if a < b_:
                m = live_cols[a] & live_cols[b_]
                cs = []
                for ti in np.flatnonzero(m):
                    x = pd.concat([P[a].iloc[:, ti], P[b_].iloc[:, ti]], axis=1).dropna()
                    ok = (D[a].iloc[:, ti].reindex(x.index) == 0) & (D[b_].iloc[:, ti].reindex(x.index) == 0)
                    x = x[ok.values]
                    cs.append(np.corrcoef(x.iloc[:, 0], x.iloc[:, 1])[0, 1])
                both_live[(a, b_)] = (int(m.sum()), float(np.nanmean(cs)) if cs else float("nan"))

    summary, comp, res = [], [], {}
    for L, Sh in dirs:
        others = [l for l in alll if l != L and l not in Sh]
        U = details[L].copy().rename(columns={"SHADOWPRICEPRECENT": f"SPPSTORED_{L}"})
        U[f"SPPSTORED_{L}"] = U[f"SPPSTORED_{L}"].astype("float32")
        for l in alll:
            if l != L:
                d = details[l][["SOURCECPNODEID", "SINKCPNODEID", "SHADOWPRICEPRECENT"]].rename(columns={"SHADOWPRICEPRECENT": f"SPPSTORED_{l}"})
                d[f"SPPSTORED_{l}"] = d[f"SPPSTORED_{l}"].astype("float32")
                U = U.merge(d, on=["SOURCECPNODEID", "SINKCPNODEID"], how="left")
        S = {}
        for l in alll:
            Sl = path_scatter.path_sf_matrix(U, P[l], D[l])
            S[l] = np.where(live_cols[l][None, :], Sl, np.nan).astype(np.float32)
            st = path_scatter.sf_stats(S[l])
            for q in ("MIN_SF", "AVG_SF", "MAX_SF"):
                U[f"{q}_{l}"] = st[q].values
            stb = path_scatter.sf_stats(np.where((weights[l] > 0)[None, :], S[l], np.nan))
            U[f"MAXB_SF_{l}"], U[f"AVGB_SF_{l}"], U[f"MINB_SF_{l}"] = stb["MAX_SF"].values, stb["AVG_SF"].values, stb["MIN_SF"].values
            live = ~np.isnan(S[l]); w = weights[l][None, :] * live
            rec = 100 * (w * np.nan_to_num(S[l])).sum(1) / np.maximum(w.sum(1), 1e-12)
            U[f"VALUE_{l}"] = sp_scale[l] * np.where(U[f"SPPSTORED_{l}"].notna(), U[f"SPPSTORED_{l}"], rec) / 100.0
            U[f"NBIND_{l}"] = int((weights[l] > 0).sum())
        U["VALUE_LONG"] = U[f"VALUE_{L}"]
        U["VALUE_SHORT"] = U[[f"VALUE_{l}" for l in Sh]].sum(axis=1)
        U["VALUE_OBLIG"] = U["VALUE_LONG"] + U["VALUE_SHORT"]
        U["VALUE_OTHER_SIGNED"] = U[[f"VALUE_{l}" for l in others]].sum(axis=1)
        U["SHORT_FLAG"] = pd.concat([(U[f"AVG_SF_{l}"] < -0.02) & (U[f"NBIND_{l}"] > 0) for l in others], axis=1).any(axis=1)
        long_ok = lambda f: (U[f"MINB_SF_{L}" if args.long_basis == "binding" else f"MIN_SF_{L}"] >= f) & (U["OPTIONPRICE"] > 0)
        short_ok = lambda f, basis=args.short_basis: (U[[(f"MAXB_SF_{l}" if basis == "binding" else f"MAX_SF_{l}") for l in Sh]] <= -f).all(axis=1)
        cnt = {f: {"long_only": int(long_ok(f).sum()), "short_live_basis": int((long_ok(f) & short_ok(f, "live")).sum()),
                   "short_binding_basis": int((long_ok(f) & short_ok(f, "binding")).sum())} for f in (0.02, 0.05, 0.10)}
        cnt_b = {f: int(((U[f"MINB_SF_{L}"] >= f) & (U["OPTIONPRICE"] > 0) & short_ok(f, "binding")).sum()) for f in (0.0, 0.02, 0.05, 0.10)}
        q = U.loc[long_ok(floor), [f"MAXB_SF_{l}" for l in Sh]].min(axis=1)
        print(f"{L}: both legs on BINDING-period basis (long MINB>=f & short MAXB<=-f): {cnt_b}; short MAXB among long-pass paths: min {q.min():.3f}, p1 {q.quantile(.01):.3f}, p10 {q.quantile(.1):.3f}")
        mask = (long_ok(floor) & short_ok(floor)).values
        cand = U[mask].copy()
        cand["NET_OPT"] = cand["VALUE_LONG"] - cand["OPTIONPRICE"]
        cand["RATIO"] = cand["VALUE_LONG"] / cand["OPTIONPRICE"]
        cand["PRICE_PER_LONG_SF"] = cand["OPTIONPRICE"] / cand[f"AVG_SF_{L}"]
        sfcols = [f"{q}_{l}" for l in alll for q in ("MIN_SF", "AVG_SF")]
        cand = path_scatter.dedup_multi(cand, sfcols, decimals=3, order=["OPTIONPRICE", "SOURCENAME", "SINKNAME"]).sort_values("NET_OPT", ascending=False).reset_index(drop=True)
        cand["MEMBER"] = cand["SOURCENAME"] + "→" + cand["SINKNAME"] + "($" + cand["OPTIONPRICE"].round(2).astype(str) + ")"
        cand = path_scatter.add_families(cand, sfcols, "MEMBER")
        # exact per-run option value over ALL legs (floor at 0 per hour) for the top rows; needs S rows of those paths
        top = cand.head(3000)
        Ut = top[["SOURCECPNODEID", "SINKCPNODEID"]]
        tot = np.zeros((len(Ut), n_runs)); tot_long = np.zeros_like(tot)
        for l in alll:
            Sl = path_scatter.path_sf_matrix(Ut, P[l], D[l])
            Sl = np.where(live_cols[l][None, :], Sl, np.nan)
            contrib = np.nan_to_num(Sl[:, tidx]) * sp_run[l][None, :]
            tot += contrib
            if l == L:
                tot_long = contrib
        cand.loc[top.index, "VALUE_ALL_OPT"] = np.maximum(tot, 0).sum(1) / n_runs
        cand.loc[top.index, "VALUE_LONG_RUNMEAN"] = np.maximum(tot_long, 0).sum(1) / n_runs
        cand["VALUE_ALL_OPT_MINUS_LONG"] = cand["VALUE_ALL_OPT"] - cand["VALUE_LONG"]
        cand["NET_ALL_OPT"] = cand["VALUE_ALL_OPT"] - cand["OPTIONPRICE"]
        # benchmark: same long leg, no short requirement, matched on long AVG_SF bands
        bm = U[long_ok(floor)].copy()
        bm["PPS"] = bm["OPTIONPRICE"] / bm[f"AVG_SF_{L}"]
        sp_ = U[mask].copy(); sp_["PPS"] = sp_["OPTIONPRICE"] / sp_[f"AVG_SF_{L}"]
        bands = [(0.05, 0.1), (0.1, 0.2), (0.2, 0.4), (0.4, 9)]
        for lo, hi in bands:
            x = sp_[(sp_[f"AVG_SF_{L}"] >= lo) & (sp_[f"AVG_SF_{L}"] < hi)]
            y = bm[(bm[f"AVG_SF_{L}"] >= lo) & (bm[f"AVG_SF_{L}"] < hi)]
            comp.append({"long": L, "short": "+".join(Sh), "avg_sf_band": f"{lo}-{hi}", "n_short_pass": len(x), "n_long_only": len(y),
                         "median_price_short_pass": x["OPTIONPRICE"].median(), "median_price_long_only": y["OPTIONPRICE"].median(),
                         "median_price_per_sf_short_pass": x["PPS"].median(), "median_price_per_sf_long_only": y["PPS"].median(),
                         "p10_price_per_sf_short_pass": x["PPS"].quantile(0.1), "p10_price_per_sf_long_only": y["PPS"].quantile(0.1)})
        comp.append({"long": L, "short": "+".join(Sh), "avg_sf_band": "all", "n_short_pass": len(sp_), "n_long_only": len(bm),
                     "median_price_short_pass": sp_["OPTIONPRICE"].median(), "median_price_long_only": bm["OPTIONPRICE"].median(),
                     "median_price_per_sf_short_pass": sp_["PPS"].median(), "median_price_per_sf_long_only": bm["PPS"].median(),
                     "p10_price_per_sf_short_pass": sp_["PPS"].quantile(0.1), "p10_price_per_sf_long_only": bm["PPS"].quantile(0.1)})
        # collinearity on this universe
        samp = np.random.default_rng(0).choice(len(U), min(len(U), 60000), replace=False)
        xa, ya = S[L][samp].ravel(), S[Sh[0]][samp].ravel()
        okp = ~np.isnan(xa) & ~np.isnan(ya)
        pc = float(np.corrcoef(xa[okp], ya[okp])[0, 1]) if okp.sum() > 10 else float("nan")
        res[(L, tuple(Sh))] = dict(cnt=cnt, n_universe=len(U), cand=cand, bm=bm, mask_n=int(mask.sum()), path_corr=pc, n_shared_obs=int(okp.sum()),
                                   frac_opposite_sign=float((np.sign(xa[okp]) != np.sign(ya[okp])).mean()) if okp.any() else float("nan"))
        nm = lambda x: x.replace("JCKSTP18A", "STP").replace("JCKREF27A", "REF")
        fam = cand[cand["FAMILY_RANK"] == 1]
        keepc = (["SOURCENAME", "SINKNAME", "OPTIONPRICE", "ALIAS_COUNT"] + [f"{q}_{l}" for l in alll for q in ("MIN_SF", "AVG_SF", "MAX_SF", "MINB_SF", "MAXB_SF", "AVGB_SF")]
                 + ["VALUE_LONG", "VALUE_SHORT", "VALUE_OBLIG", "VALUE_OTHER_SIGNED", "VALUE_ALL_OPT", "NET_OPT", "RATIO", "NET_ALL_OPT",
                    "PRICE_PER_LONG_SF", "SHORT_FLAG", "FAMILY", "FAMILY_SIZE", "FAMILY_MEMBERS"])
        fam[[c for c in keepc if c in fam]].head(50).to_csv(out / f"candidates_long{nm(L)}_short{nm('+'.join(Sh))}.csv", index=False)
        print(f"long {L} short {Sh}: universe {len(U)}, counts {cnt}, candidates {mask.sum()} -> {len(cand)} distinct, {int(fam.shape[0])} families")
    comp = pd.DataFrame(comp)
    comp.to_csv(out / "comparison.csv", index=False)
    bl = pd.DataFrame([{"a": a, "b": b_, "topologies_both_live": v[0], "mean_node_psens_corr_in_shared_topologies": v[1]} for (a, b_), v in both_live.items()])
    bl.to_csv(out / "co_live.csv", index=False)
    path_scatter.build_spread_report(out, args, dirs, res, comp, bl, sp_scale, n_runs, floor, alll, live_cols,
                                   int(cfg[alll[0]].STUDYID))
    print("wrote", out)


def main():
    parser = argparse.ArgumentParser(description="PathOpt scatter: long-both + cheap paths by MIN_SF robustness")
    parser.add_argument("--study", type=int, required=True, help="Study ID")
    parser.add_argument("--run-x", type=int, help="X-axis PathOpt run ID")
    parser.add_argument("--run-y", type=int, help="Y-axis PathOpt run ID")
    parser.add_argument("--date", help="Simulation date (YYYY-MM-DD)")
    parser.add_argument("--hour", type=int, help="Simulation hour (1-24)")
    parser.add_argument("--runs", help="N-run mode: LABEL=RUNID,... (PathOpt runs)")
    parser.add_argument("--required", help="N-run mode: labels that must all be long (default: all but last)")
    parser.add_argument("--constraints", help="N-run mode: LABEL=FROM-TO-CKT@CTG,... for study binding/SP context")
    parser.add_argument("--out-dir", help="N-run mode: output directory")
    parser.add_argument("--value-only", help="N-run mode: LABEL=RUNID,... co-binder legs valued (signed) but not required long")
    parser.add_argument("--short", help="Spread mode: SHORT leg label(s); --required is the single LONG leg; runs both directions when one short")
    parser.add_argument("--short-basis", choices=["binding", "live"], default="binding",
                        help="Spread mode: short leg tested on MAX_SF over its binding periods (default) or all live periods")
    parser.add_argument("--long-basis", choices=["binding", "live"], default="live",
                        help="Spread mode: long leg tested on MIN_SF over all live periods (default) or its binding periods only")
    parser.add_argument("--min-sf-each", type=float, default=0.05, help="N-run mode: live-period MIN_SF floor on every required constraint")
    parser.add_argument("--holidays", help="N-run/spread mode (required there): comma-separated dates for holiday sensitivity, '' for none")
    parser.add_argument("--pool", type=int, default=300, help="N-run mode: pair-search pool per constraint")
    parser.add_argument("--top", type=int, default=100000, help="Top N cheapest paths for scatter (default: 100000)")
    parser.add_argument("--min-sf", type=float, default=0.05, help="Min SF floor on both MIN_SFs (default: 0.05)")
    args = parser.parse_args()
    if args.runs and args.holidays is None:
        parser.error("--holidays is required with --runs (comma-separated dates, or '' for none)")
    if args.runs and args.short:
        return run_spread(args)
    if args.runs:
        return run_multi(args)
    if None in (args.run_x, args.run_y, args.date, args.hour):
        parser.error("either --runs or all of --run-x --run-y --date --hour are required")

    print(f"\n{'='*80}")
    print(f"PathOpt Scatter: Study {args.study}, Date {args.date} HE{args.hour}")
    print(f"X-axis: Run {args.run_x} | Y-axis: Run {args.run_y}")
    print(f"Scatter: top {args.top:,} cheapest | Candidates: full universe, MIN_SF floor ≥ {args.min_sf}")
    print(f"{'='*80}\n")

    # Step 1: Get run configs and topology set members
    print("Step 1: Getting run configs and topology set members...")
    run_x = popt.get_run_config(args.run_x)
    run_y = popt.get_run_config(args.run_y)

    print(f"  Run X: {run_x.BRANCHLABEL} / {run_x.CTGLABEL}, direction {run_x.DIRECTION}, "
          f"set {run_x.TOPOLOGYSHIFTSETID}")
    print(f"  Run Y: {run_y.BRANCHLABEL} / {run_y.CTGLABEL}, direction {run_y.DIRECTION}, "
          f"set {run_y.TOPOLOGYSHIFTSETID}")

    members_x = popt.get_topology_set_members(run_x.TOPOLOGYSHIFTSETID)
    members_y = popt.get_topology_set_members(run_y.TOPOLOGYSHIFTSETID)

    print(f"  Set X has {len(members_x)} members")
    print(f"  Set Y has {len(members_y)} members")

    # List available days at the specified hour in both sets
    members_x["SIMDATE"] = pd.to_datetime(members_x["SIMDATE"]).dt.date
    members_y["SIMDATE"] = pd.to_datetime(members_y["SIMDATE"]).dt.date

    days_x = set(members_x[members_x["SIMHOUR"] == args.hour]["SIMDATE"])
    days_y = set(members_y[members_y["SIMHOUR"] == args.hour]["SIMDATE"])
    common_days = sorted(days_x & days_y)

    print(f"\n  Days at hour {args.hour} in BOTH sets:")
    for d in common_days[:10]:
        print(f"    {d}")
    if len(common_days) > 10:
        print(f"    ... ({len(common_days)} total)")

    # Pick the chosen date
    chosen_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    if chosen_date not in common_days:
        print(f"\n  ERROR: Chosen date {chosen_date} not available in both sets at hour {args.hour}")
        print(f"  Available: {common_days}")
        sys.exit(1)

    print(f"\n  ✓ Chosen date: {chosen_date}")

    # Get psenshiftid for the chosen day/hour
    member_x = members_x[(members_x["SIMDATE"] == chosen_date) & (members_x["SIMHOUR"] == args.hour)]
    member_y = members_y[(members_y["SIMDATE"] == chosen_date) & (members_y["SIMHOUR"] == args.hour)]

    if len(member_x) == 0 or len(member_y) == 0:
        print(f"\n  ERROR: No psenshiftid found for date {chosen_date} hour {args.hour}")
        sys.exit(1)

    psenshiftid_x = member_x.iloc[0]["PSENSHIFTID"]
    runid_x = member_x.iloc[0]["RUNID"]
    psenshiftid_y = member_y.iloc[0]["PSENSHIFTID"]
    runid_y = member_y.iloc[0]["RUNID"]

    print(f"  X: psenshiftid {psenshiftid_x}, runid {runid_x}")
    print(f"  Y: psenshiftid {psenshiftid_y}, runid {runid_y}")

    # Step 2: Pull FULL PathOpt detail (all paths from both runs)
    print("\nStep 2: Pulling FULL PathOpt detail rows...")
    detail_x = popt.fetch_detail(
        args.run_x,
        columns=["SOURCECPNODEID", "SINKCPNODEID", "SOURCENAME", "SINKNAME",
                 "SOURCEBUSKV", "SINKBUSKV", "OPTIONPRICE", "MIN_SF", "MAX_SF", "AVG_SF"]
    )
    detail_y = popt.fetch_detail(
        args.run_y,
        columns=["SOURCECPNODEID", "SINKCPNODEID", "OPTIONPRICE", "MIN_SF", "MAX_SF", "AVG_SF"]
    )

    print(f"  Run X: {len(detail_x):,} paths")
    print(f"  Run Y: {len(detail_y):,} paths")

    # Step 3: Inner join on (source, sink) — FULL universe
    print("\nStep 3: Joining runs (FULL universe)...")
    full_merged = detail_x.merge(
        detail_y,
        on=["SOURCECPNODEID", "SINKCPNODEID"],
        suffixes=("_X", "_Y"),
        how="inner"
    )
    print(f"  Joined paths (full universe): {len(full_merged):,}")

    # Verify OPTIONPRICE consistency
    price_diff = (full_merged["OPTIONPRICE_X"] - full_merged["OPTIONPRICE_Y"]).abs()
    mismatches = (price_diff > 0.01).sum()
    print(f"  OPTIONPRICE mismatches (>$0.01): {mismatches}")

    # Use OPTIONPRICE from run X
    full_merged = full_merged.rename(columns={"OPTIONPRICE_X": "OPTIONPRICE"})
    full_merged = full_merged.rename(columns={
        "MIN_SF_X": "MIN_SF_X", "MAX_SF_X": "MAX_SF_X", "AVG_SF_X": "AVG_SF_X",
        "MIN_SF_Y": "MIN_SF_Y", "MAX_SF_Y": "MAX_SF_Y", "AVG_SF_Y": "AVG_SF_Y",
    })
    full_merged = full_merged.drop(columns=["OPTIONPRICE_Y"])

    # Report MIN/AVG SF stats
    neg_min_x = (full_merged["MIN_SF_X"] < 0).sum()
    neg_min_y = (full_merged["MIN_SF_Y"] < 0).sum()
    neg_avg_x = (full_merged["AVG_SF_X"] < 0).sum()
    neg_avg_y = (full_merged["AVG_SF_Y"] < 0).sum()
    print(f"  Paths with negative MIN_SF_X: {neg_min_x:,}")
    print(f"  Paths with negative MIN_SF_Y: {neg_min_y:,}")
    print(f"  Paths with negative AVG_SF_X: {neg_avg_x:,}")
    print(f"  Paths with negative AVG_SF_Y: {neg_avg_y:,}")
    print(f"  MIN_SF_X range: [{full_merged['MIN_SF_X'].min():.4f}, {full_merged['MIN_SF_X'].max():.4f}]")
    print(f"  MIN_SF_Y range: [{full_merged['MIN_SF_Y'].min():.4f}, {full_merged['MIN_SF_Y'].max():.4f}]")

    # Step 4: Dedup FULL universe
    print("\nStep 4: Deduplicating FULL universe (MIN/AVG/MAX + price, no day SF)...")
    full_merged_deduped = path_scatter.dedup_by_electrical_path(full_merged, has_day_sf=False)
    print(f"  Before dedup: {len(full_merged):,} paths")
    print(f"  After dedup: {len(full_merged_deduped):,} distinct electrical paths")

    # Step 5: Add derived columns (Y_TO_X_RATIO, DOMINANT_AXIS) — no day SF yet
    print("\nStep 5: Adding derived columns (Y_TO_X_RATIO, DOMINANT_AXIS)...")
    full_merged_deduped = path_scatter.add_derived_columns(full_merged_deduped, has_day_sf=False)

    # Step 6: Rank candidates from FULL universe
    print("\nStep 6: Ranking candidates from FULL universe...")
    paid_to_take_full, candidates_full = path_scatter.rank_by_min_sf(full_merged_deduped, min_sf_floor=args.min_sf)

    print(f"  Paid-to-take paths (OPTIONPRICE≤0): {len(paid_to_take_full)}")
    print(f"  Candidates passing MIN_SF floor (≥{args.min_sf} on both axes): {len(candidates_full):,}")

    # Step 7: Find near-miss paths
    print("\nStep 7: Finding near-miss paths (MIN_SF_X in [0.03, 0.05), MIN_SF_Y ≥ 0.05)...")
    near_miss = path_scatter.find_near_miss(full_merged_deduped, min_x_range=(0.03, 0.05), min_y_floor=0.05)
    print(f"  Near-miss paths: {len(near_miss):,}")

    # Report MIN_SF_X ≥ 0.05 count and median
    min_sf_x_pass = (full_merged_deduped["MIN_SF_X"] >= 0.05).sum()
    median_min_sf_x = full_merged_deduped["MIN_SF_X"].median()
    print(f"  Distinct paths with MIN_SF_X ≥ 0.05: {min_sf_x_pass} of {len(full_merged_deduped):,}")
    print(f"  Median MIN_SF_X: {median_min_sf_x:.6f}")

    # Step 8: Pull day SFs for top N cheapest (for scatter only)
    print(f"\nStep 8: Pulling day SFs for top {args.top:,} cheapest paths (scatter only)...")
    top_n_merged = full_merged.sort_values("OPTIONPRICE").head(args.top)
    print(f"  Top {len(top_n_merged):,} cheapest selected (price: "
          f"${top_n_merged['OPTIONPRICE'].min():.2f} to ${top_n_merged['OPTIONPRICE'].max():.2f}/MWh)")

    node_sf_x = popt.get_node_shift_factors(psenshiftid_x)
    node_sf_y = popt.get_node_shift_factors(psenshiftid_y)

    print(f"  Node SFs X: {len(node_sf_x):,} nodes")
    print(f"  Node SFs Y: {len(node_sf_y):,} nodes")

    paths_with_day_sf, dropped = path_scatter.compute_path_shift_factors(top_n_merged, node_sf_x, node_sf_y)
    print(f"  Paths with day SFs computed: {len(paths_with_day_sf):,}")
    print(f"  Paths dropped (missing nodes): {dropped}")

    # Step 9: Dedup top N with day SFs
    print("\nStep 9: Deduplicating top N with day SFs (psens + MIN/AVG + price)...")
    before_dedup = len(paths_with_day_sf)
    paths_deduped = path_scatter.dedup_by_electrical_path(paths_with_day_sf, has_day_sf=True)
    print(f"  Before dedup: {before_dedup:,} paths")
    print(f"  After dedup: {len(paths_deduped):,} distinct electrical paths")

    # Step 10: Add derived columns INCLUDING day spike
    print("\nStep 10: Adding derived columns + day spike flag...")
    paths_deduped = path_scatter.add_derived_columns(paths_deduped, has_day_sf=True)

    # Count day spikes in ALL distinct paths and in AVG>0.02 subset
    spike_count_all = paths_deduped["DAY_SPIKE"].sum()
    avg_both_002 = paths_deduped[(paths_deduped["AVG_SF_X"] > 0.02) & (paths_deduped["AVG_SF_Y"] > 0.02)]
    spike_count_avg = avg_both_002["DAY_SPIKE"].sum()
    print(f"  Day spike paths (all {len(paths_deduped):,} distinct): {spike_count_all}")
    print(f"  Day spike paths (AVG>0.02 both axes, {len(avg_both_002):,} paths): {spike_count_avg}")

    # Verify CHAR_SLR_RN→PIN_BESS_RN is flagged
    char_pin = paths_deduped[(paths_deduped["SOURCENAME"] == "CHAR_SLR_RN") &
                              (paths_deduped["SINKNAME"] == "PIN_BESS_RN")]
    if len(char_pin) > 0:
        is_spike = char_pin.iloc[0]["DAY_SPIKE"]
        print(f"  ✓ CHAR_SLR_RN→PIN_BESS_RN spike flag: {is_spike}")
    else:
        print(f"  ⚠ CHAR_SLR_RN→PIN_BESS_RN not in top {args.top:,} cheapest")

    # Step 11: Rank top N candidates
    print("\nStep 11: Ranking top N candidates...")
    paid_to_take, candidates = path_scatter.rank_by_min_sf(paths_deduped, min_sf_floor=args.min_sf)

    print(f"  Paid-to-take paths (OPTIONPRICE≤0): {len(paid_to_take)}")
    print(f"  Candidates passing MIN_SF floor: {len(candidates):,}")

    # Count spikes in candidates
    spike_count_candidates = candidates["DAY_SPIKE"].sum() if len(candidates) > 0 else 0
    print(f"  Day spike paths in candidates: {spike_count_candidates}")

    # Step 12: Output files
    print("\nStep 12: Writing output files...")
    output_dir = SCRIPT_DIR.parent / "output" / "pathopt" / f"{args.study}_{args.date}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Delete stale paths_100k.parquet if exists
    stale_path = output_dir / "paths_100k.parquet"
    if stale_path.exists():
        stale_path.unlink()
        print(f"  ✓ Deleted stale: {stale_path.name}")

    # Scatter plot
    scatter_path = output_dir / "scatter.html"
    path_scatter.build_scatter_plot(
        paths_deduped, candidates,
        args.study, args.run_x, args.run_y,
        run_x.BRANCHLABEL, run_x.CTGLABEL,
        run_y.BRANCHLABEL, run_y.CTGLABEL,
        args.date, args.hour,
        scatter_path
    )
    print(f"  ✓ Scatter plot: {scatter_path.name}")

    # Candidates CSV (from top N, with day SFs)
    candidates_csv = output_dir / "candidates.csv"
    output_cols = [
        "SOURCENAME", "SINKNAME", "ALIASES", "ALIAS_COUNT",
        "SOURCEBUSKV", "SINKBUSKV", "OPTIONPRICE",
        "MIN_SF_X", "MIN_SF_Y", "AVG_SF_X", "AVG_SF_Y", "SF_X", "SF_Y",
        "Y_TO_X_RATIO", "DOMINANT_AXIS",
        "MIN_SF_BOTH", "AVG_SCORE", "SCORE", "DAY_SPIKE",
    ]
    candidates[output_cols].to_csv(candidates_csv, index=False)
    print(f"  ✓ Candidates CSV (top {args.top:,} cut): {candidates_csv.name} ({len(candidates):,} rows)")

    # Candidates FULL CSV (from full universe, no day SFs)
    candidates_full_csv = output_dir / "candidates_full.csv"
    output_cols_full = [
        "SOURCENAME", "SINKNAME", "ALIASES", "ALIAS_COUNT",
        "SOURCEBUSKV", "SINKBUSKV", "OPTIONPRICE",
        "MIN_SF_X", "MIN_SF_Y", "AVG_SF_X", "AVG_SF_Y",
        "Y_TO_X_RATIO", "DOMINANT_AXIS",
        "MIN_SF_BOTH", "AVG_SCORE", "SCORE", "DAY_SPIKE",
    ]
    candidates_full[output_cols_full].to_csv(candidates_full_csv, index=False)
    print(f"  ✓ Candidates FULL CSV (full universe): {candidates_full_csv.name} ({len(candidates_full):,} rows)")

    # Near-miss CSV
    near_miss_csv = output_dir / "near_miss.csv"
    near_miss[output_cols_full].to_csv(near_miss_csv, index=False)
    print(f"  ✓ Near-miss CSV: {near_miss_csv.name} ({len(near_miss):,} rows)")

    # Deduped paths parquet (with day SFs and spike flag)
    paths_parquet = output_dir / "paths_deduped.parquet"
    paths_deduped.to_parquet(paths_parquet, index=False)
    print(f"  ✓ Deduped paths parquet: {paths_parquet.name} ({len(paths_deduped):,} paths)")

    # README
    readme_path = output_dir / "README.md"

    # Generate top-source notes from data
    source_counts = candidates_full.groupby("SOURCENAME")["ALIAS_COUNT"].sum().sort_values(ascending=False)
    top_sources = source_counts.head(3)
    source_notes = []
    for source in top_sources.index:
        source_paths = candidates_full[candidates_full["SOURCENAME"] == source]
        avg_ratio = source_paths["Y_TO_X_RATIO"].mean()
        dominant = source_paths["DOMINANT_AXIS"].mode().iloc[0] if len(source_paths) > 0 else "BALANCED"
        source_notes.append(f"  - **{source}**: {len(source_paths)} paths, avg Y/X ratio {avg_ratio:.1f} ({dominant}-dominant)")

    readme_content = f"""# PathOpt Scatter: Study {args.study}

**Date:** {args.date} HE{args.hour}
**Paths analyzed (scatter):** {len(paths_deduped):,} distinct (top {args.top:,} cheapest before dedup)
**Distinct electrical paths (full universe):** {len(full_merged_deduped):,}

## Constraints

- **X-axis:** {run_x.BRANCHLABEL} / {run_x.CTGLABEL} (run {args.run_x}, direction {run_x.DIRECTION}, set {run_x.TOPOLOGYSHIFTSETID})
- **Y-axis:** {run_y.BRANCHLABEL} / {run_y.CTGLABEL} (run {args.run_y}, direction {run_y.DIRECTION}, set {run_y.TOPOLOGYSHIFTSETID})

## Method

**Path SF** = psens(source) − psens(sink) from node shift factors (CPNODE_SHIFTS_VIEW).
- Positive SF = LONG (path earns when constraint binds).
- Price = OPTIONPRICE ($/MWh, forward OnPeak price class 2 option mark) from PathOpt detail.
- **Robustness score** = min(MIN_SF_X, MIN_SF_Y) / OPTIONPRICE, where MIN_SF is worst-case across PathOpt's 10-day window.
- Materiality floor: MIN_SF_X ≥ {args.min_sf} AND MIN_SF_Y ≥ {args.min_sf}.

**Electrical path deduplication:** Paths with identical (rounded psens, MIN_SF, AVG_SF, price) are grouped; one representative kept with aliases.

**Day spike flag:** Day SF > 2× AVG_SF on either axis (outlier topology on {args.date}).

**Y-to-X ratio:** AVG_SF_Y / AVG_SF_X. Dominant axis: ratio >3 → Y, <1/3 → X, else BALANCED.

## PathOpt Pre-Filtering Disclosure

PathOpt filters on **MAX_SF > 0** (best of the 10 topologies), NOT SF ∈ [0, 1.1]. The inner join produces paths that are **long both on their best day**, not long-both by construction.

**MIN_SF ranges:** X: [{full_merged["MIN_SF_X"].min():.4f}, {full_merged["MIN_SF_X"].max():.4f}], Y: [{full_merged["MIN_SF_Y"].min():.4f}, {full_merged["MIN_SF_Y"].max():.4f}]

**Paths with negative MIN/AVG:**
- Negative MIN_SF_X: {neg_min_x:,} ({100*neg_min_x/len(full_merged):.1f}%)
- Negative MIN_SF_Y: {neg_min_y:,} ({100*neg_min_y/len(full_merged):.1f}%)
- Negative AVG_SF_X: {neg_avg_x:,} ({100*neg_avg_x/len(full_merged):.1f}%)
- Negative AVG_SF_Y: {neg_avg_y:,} ({100*neg_avg_y/len(full_merged):.1f}%)

The MIN_SF floor (≥{args.min_sf} on both axes) removes these from candidates.

**MIN_SF_X scarcity:** Only {min_sf_x_pass} of {len(full_merged_deduped):,} distinct paths ({100*min_sf_x_pass/len(full_merged_deduped):.1f}%) have MIN_SF_X ≥ 0.05 (median {median_min_sf_x:.6f}). Score ≈ MIN_SF_X / price for most paths.

Load zones excluded by PathOpt's deadbus filter: LZ_HOUSTON, HB_NORTH (only HB_HOUSTON, HB_WEST, LZ_CPS, LZ_LCRA, LZ_AEN, LZ_RAYBN present).

## Results

### Full Universe (all {len(full_merged_deduped):,} distinct paths)
- **Passing MIN_SF floor (≥{args.min_sf} both axes):** {len(candidates_full):,}
- **Near-miss (MIN_SF_X in [0.03, 0.05), MIN_SF_Y ≥ 0.05):** {len(near_miss):,}
- **Paid-to-take:** {len(paid_to_take_full)} (OPTIONPRICE≤0)

### Top {args.top:,} Cheapest (scatter, with day SFs)
- **Distinct electrical paths:** {len(paths_deduped):,}
- **Day spike paths (all):** {spike_count_all} ({100*spike_count_all/len(paths_deduped):.1f}%)
- **Day spike paths (AVG>0.02 both axes):** {spike_count_avg} of {len(avg_both_002):,} ({100*spike_count_avg/len(avg_both_002) if len(avg_both_002) > 0 else 0:.1f}%)
- **Passing MIN_SF floor:** {len(candidates):,}
- **Day spike in candidates:** {spike_count_candidates}

**Score is a screen, not a valuation.** MIN_SF captures worst-case exposure across the 10-day window; use for robustness ranking only.

## Files

- `scatter.html` — Interactive scatter plot (Plotly): {args.date} day SFs for top {args.top:,} cheapest, top 25 distinct candidates highlighted, day spikes marked
- `candidates.csv` — Ranked candidates from top {args.top:,} cheapest (with day SFs)
- `candidates_full.csv` — Ranked candidates from FULL universe ({len(candidates_full):,} rows, no day SFs)
- `near_miss.csv` — Near-miss paths ({len(near_miss):,} rows)
- `paths_deduped.parquet` — All {len(paths_deduped):,} distinct paths (top {args.top:,} cheapest) with day SFs and spike flag
- `README.md` — This file

## Top Candidate Sources (from full universe)

{chr(10).join(source_notes)}
"""
    readme_path.write_text(readme_content)
    print(f"  ✓ README: {readme_path.name}")

    # Print top 15 from candidates_full
    print(f"\n{'='*80}")
    print("Top 15 Distinct Paths from FULL Universe (MIN_SF Robustness Score)")
    print(f"{'='*80}")
    print(f"{'#':<4} {'Source→Sink':<35} {'Al':<4} {'Price':<8} "
          f"{'MIN_X':<7} {'MIN_Y':<7} {'AVG_X':<7} {'AVG_Y':<7} "
          f"{'Ratio':<7} {'Dom':<9} {'Score':<8} {'Spike':<6}")
    print("-" * 140)

    for rank, (_, row) in enumerate(candidates_full.head(15).iterrows(), 1):
        path_str = f"{row.SOURCENAME}→{row.SINKNAME}"
        spike_str = "⚠" if row.DAY_SPIKE else ""
        print(f"{rank:<4} {path_str[:34]:<35} {row.ALIAS_COUNT:<4} "
              f"${row.OPTIONPRICE:>6.2f} "
              f"{row.MIN_SF_X:>6.3f} {row.MIN_SF_Y:>6.3f} "
              f"{row.AVG_SF_X:>6.3f} {row.AVG_SF_Y:>6.3f} "
              f"{row.Y_TO_X_RATIO:>6.2f} {row.DOMINANT_AXIS:<9} "
              f"{row.SCORE:>7.4f} {spike_str:<6}")

    # Print top 10 near-miss
    print(f"\n{'='*80}")
    print("Top 10 Near-Miss Paths (MIN_SF_X in [0.03, 0.05), MIN_SF_Y ≥ 0.05)")
    print(f"{'='*80}")
    print(f"{'#':<4} {'Source→Sink':<35} {'Al':<4} {'Price':<8} "
          f"{'MIN_X':<7} {'MIN_Y':<7} {'AVG_X':<7} {'AVG_Y':<7} "
          f"{'Ratio':<7} {'Dom':<9} {'Score':<8}")
    print("-" * 140)

    for rank, (_, row) in enumerate(near_miss.head(10).iterrows(), 1):
        path_str = f"{row.SOURCENAME}→{row.SINKNAME}"
        print(f"{rank:<4} {path_str[:34]:<35} {row.ALIAS_COUNT:<4} "
              f"${row.OPTIONPRICE:>6.2f} "
              f"{row.MIN_SF_X:>6.3f} {row.MIN_SF_Y:>6.3f} "
              f"{row.AVG_SF_X:>6.3f} {row.AVG_SF_Y:>6.3f} "
              f"{row.Y_TO_X_RATIO:>6.2f} {row.DOMINANT_AXIS:<9} "
              f"{row.SCORE:>7.4f}")

    print(f"\nSummary:")
    print(f"  - Full universe: {len(full_merged_deduped):,} distinct paths")
    print(f"  - Candidates (full): {len(candidates_full):,} passing MIN_SF ≥ {args.min_sf} floor")
    print(f"  - Near-miss: {len(near_miss):,} paths (MIN_SF_X in [0.03, 0.05))")
    print(f"  - Day spikes (all): {spike_count_all} of {len(paths_deduped):,} distinct ({100*spike_count_all/len(paths_deduped):.1f}%)")
    print(f"  - Day spikes (AVG>0.02 both): {spike_count_avg} of {len(avg_both_002):,} ({100*spike_count_avg/len(avg_both_002) if len(avg_both_002) > 0 else 0:.1f}%)")
    print(f"  - CHAR_SLR_RN→PIN_BESS_RN flagged: {char_pin.iloc[0]['DAY_SPIKE'] if len(char_pin) > 0 else 'N/A (not in top 100k)'}")
    print(f"  - Output: {output_dir}\n")


if __name__ == "__main__":
    main()
