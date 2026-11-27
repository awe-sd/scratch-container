"""Deep-dive markdown: turns pfa.analysis.deep_dive results into the report text."""
from __future__ import annotations

import numpy as np
import pandas as pd

from pfa import periods
from pfa.analysis.deep_dive import CORR_MATERIALITY, DRIVER_LEAD


def _plain(d: dict | None) -> dict | None:
    """Strip numpy scalar types so dicts print as plain Python floats/ints."""
    if d is None:
        return None

    def _scalar(v):
        if isinstance(v, dict):
            return {k2: _scalar(v2) for k2, v2 in v.items()}
        if isinstance(v, np.floating):
            return float(v)
        if isinstance(v, np.integer):
            return int(v)
        return v
    return {k: _scalar(v) for k, v in d.items()}


def render_markdown(study_id: int, results: list[dict], flip_df: pd.DataFrame, synthesis: dict | None) -> str:
    lines = [f"# Constraint deep dive — study {study_id}", ""]
    for r in results:
        c = r["c"]
        lines += [f"## {c['label']} — {c['fromname']} ({c['fromnum']}) to {c['toname']} ({c['tonum']}) "
                  f"CKT {c['ckt']}, dominant ctg {c['ctglabel']} (OUTBRANCHDIRECTION={c['direction']}, "
                  f"{c['n_binding_runs']} study binding runs)", ""]

        lines += ["### 1. Binding conditions (wind/solar/load)"]
        bc = r["binding"]
        if bc.get("empty"):
            lines += ["No fast-scan headroom rows found for this config/window.", ""]
        else:
            hod = bc["hour_of_day_neg_rate"]
            mname = bc["month_name"]
            top_hours = sorted(hod, key=lambda h: (-hod[h], h))[:5]
            hod_str = ", ".join(f"{periods.fastscan_he_label(h)}={hod[h]:.3f}" for h in top_hours)
            sp = bc["span"]
            matched = f"wind matched: {bc['n_wind_matched']}, solar matched: {bc['n_solar_matched']}, load matched: {bc['n_load_matched']}"
            lines += [f"- FAST_SCAN_CONFIG_ID: {bc['config_id']}; fast-scan hours used: {bc['n_hours']:,} spanning "
                      f"{sp['start']:%Y-%m-%d} to {sp['end']:%Y-%m-%d} ({sp['months']}; requested window {bc['window']['start']}..{bc['window']['end']}) "
                      f"({matched} -- gaps are hours the feed doesn't cover, not silently dropped)",
                      *([f"- Load series unavailable: {bc['load_error']}"] if bc.get("load_error") else []),
                      f"- Driver attribution over that span ({sp['months']} {sp['start']:%Y}): **{_driver_text(bc['driver'])}**",
                      f"- Correlation of HEADROOM with wind by region / solar / load (system wind cap check: "
                      f"{bc['system_wind_cap_mw']} MW installed): `{_plain(bc['corr'])}`",
                      f"- Dominant wind region (only named if |corr| >= {CORR_MATERIALITY}): "
                      f"**{bc['dominant_wind_region'] or 'none material'}**",
                      f"- Trigger levels (hours with headroom<0 = binding hours, over the same {sp['months']} span). If headroom FALLS as a driver rises "
                      f"(corr < 0) the constraint binds when the driver is HIGH and the informative level is a LOW percentile of the driver among binding "
                      f"hours (P10: where binding starts); if corr > 0 it binds when the driver is LOW and the informative level is P90. "
                      f"Binding rate by quintile of the driver is over all hours of the span. Small n binding = thin estimate:",
                      "", _triggers_md(bc["triggers"]), ""]
            lines += _month_lines(bc, mname)
            lines += [f"- Top negative-headroom hours-of-day (window-wide, not {mname}-only): {hod_str}", ""]

        lines += ["### 2. Dispatch on the constraint (qualifying relief/harm nodes, |PSENS| 0.03-0.9, "
                  "deduped to distinct CPNODEs)"]
        disp = r["dispatch"]
        if disp.empty:
            lines += ["No qualifying CPNODE_SHIFTS_VIEW rows.", ""]
        else:
            cols = ["NAME", "PSENS", "EFFECTIVE_SIGN", "RELIEF_OR_HARM", "GENFUELTYPE", "RESOURCE_TYPE"]
            lines += [disp[cols].to_markdown(index=False), ""]

        lines += ["### 3. Price formation"]
        pf = r["price"]
        if pf["lp_stats"]:
            ls = pf["lp_stats"]
            note = "" if ls["n"] == ls["n_binding_runs"] else (
                f" (note: {ls['n_binding_runs'] - ls['n']} binding run(s) had no OPFCNLAMBDA row -- excluded, not zeroed)")
            lines += [f"- LP shadow price (OPFCNLAMBDA) over {ls['n']}/{ls['n_binding_runs']} binding runs: "
                      f"mean=${ls['mean']}, p50=${ls['p50']}, max=${ls['max']}, "
                      f"pct_penalty_tier={ls['pct_penalty_tier']}{note} "
                      f"(pct_penalty_tier flags flat 500/3500 penalty values as unpriced, not real $)."]
        else:
            lines += ["- No LP shadow-price rows found for binding runs."]
        of = pf.get("outage_flow")
        if of:
            lines += [f"- Driving outage group `{of['group']}`: adds {of['signed_fd']:+.1f} MW to this constraint in its bound sense "
                      f"(mean over {of['n_runs']} runs, signed by OUTBRANCHDIRECTION; mean pre-outage flow {of['mean_preflow']} MW)."]
        if len(pf["marginal_units"]):
            mu = pf["marginal_units"].rename(columns={"UNIT": "UNIT (SCED name)", "N": "N runs", "SF": "SF on constraint (bound sense)",
                                                      "PRICE_SETTER": "price setter for this constraint?"})
            cols = [c for c in ["UNIT (SCED name)", "BUSNUM", "ID", "FUELTYPE", "N runs", "SF on constraint (bound sense)",
                                "price setter for this constraint?"] if c in mu]
            lines += ["- Marginal units (BUSMARGCOSTMW≈EDMARGCOSTMW, MWMIN<MW<MWMAX) in binding runs; these are system-wide marginal "
                      "generators, only those with |SF| >= 0.03 on this constraint can set its price:",
                      mu[cols].to_markdown(index=False, floatfmt=".3f")]
        else:
            lines += ["- No marginal units identified by the BUSMARGCOSTMW≈EDMARGCOSTMW screen."]
        sl = pf["structural_lambda"]
        if sl and "shallow_lambda" in sl:
            def _fmt(lam, pair, regime):
                if lam is None:
                    return f"**unpriced** via {pair} -- {regime}"
                return f"${lam}/MWh via {pair} ({regime})"
            step_note = (f" **The relief set had only 1 usable pair** -- shallow and deep relief below "
                        f"are the SAME step, not two independent findings from priced depth."
                        if sl["single_step"] else "")
            commit_note = (f" Of that, only **{sl['committed_mw']} MW** pairs against DAM-committed "
                          f"(already-running) units -- ramp a trader could actually lean on; the "
                          f"remaining **{sl['uncommitted_mw']} MW** ({sl['n_uncommitted_steps']}/{sl['n_steps']} "
                          f"depth steps) requires STARTING a currently-uncommitted unit, a materially "
                          f"different and slower relief action."
                          if sl["uncommitted_mw"] > 0 else "")
            lines += [f"- Structural lambda (house number, from DAM offer stacks), {sl['n_steps']} depth "
                      f"step(s) total, exhausting at {sl['exhaustion_depth_mw']} MW of flow relief "
                      f"(beyond that the relief set has no more priced capacity).{commit_note}{step_note} "
                      f"shallow relief "
                      f"{_fmt(sl['shallow_lambda'], sl['shallow_pair'], sl['shallow_regime'])}; "
                      f"deep relief {_fmt(sl['deep_lambda'], sl['deep_pair'], sl['deep_regime'])}. "
                      f"A $0.0/MWh figure is only shown when both sides of the pair have a real DAM offer "
                      f"price and the down-side genuinely clears at/above the up-side; 'unpriced' means a "
                      f"DAM offer price was missing for one side, not a free redispatch."]
            lines += _curve_lines(sl, pf.get("outage_flow"), pf["lp_stats"])
        elif sl and "error" in sl:
            lines += [f"- Structural lambda: could not compute ({sl['error']})."]
        elif sl and sl.get("empty_curve"):
            lines += [f"- Structural lambda: relief set has {sl['n_relief_units']} unit(s) but offer "
                      f"coverage priced 0 MW ({sl['empty_desc']} / DAM disclosure gap)."]
        elif sl and sl.get("empty_relief"):
            lines += ["- Structural lambda: relief set empty (no |SF|-qualified units)."]
        else:
            lines += ["- Structural lambda: no relief set / offer coverage found."]
        lines += [""]

    if not flip_df.empty:
        lines += ["## 4. Flip attribution (tofinder outage-group impact per constraint)", ""]
        lines += [flip_df.to_markdown(index=False), "",
                  "SIGNED_FLOWDELTA = MEAN_FLOWDELTA x OUTBRANCHDIRECTION (positive = the outage group "
                  "pushes MORE flow onto this branch in its bound sense). Sorted by SIGNED_FLOWDELTA "
                  "descending so flow-adding groups rank above flow-reducing ones.", ""]
        lines += _flip_synthesis(synthesis, flip_df)
    return "\n".join(lines)


def _driver_text(d: dict) -> str:
    peak = f"peak stress hour={periods.fastscan_he_label(d['peak_hour'])}" if d["peak_hour"] is not None else "peak stress hour=None"
    corrs = f"corr with headroom: wind={d['wind_corr']}, solar={d['solar_corr']}, load={d.get('load_corr')}"
    kind = d["kind"]
    if kind == "mixed":
        return (f"mixed (no single driver leads the runner-up by >= {DRIVER_LEAD}; {corrs}; {peak}; "
                f"marginal correlations that do not control for each other or for hour of day)")
    if kind == "none":
        return f"no driver named (no |corr| reaches {CORR_MATERIALITY}; {corrs}; {peak})"
    return (f"{kind}-driven (|corr| leads the runner-up by {d['lead']}, margin needed {DRIVER_LEAD}; {corrs}; {peak}; "
            f"marginal correlations that do not control for each other or for hour of day)")


def _triggers_md(trig: dict) -> str:
    rows = []
    for var, t in trig.items():
        if not t:
            rows.append({"driver": var, "corr": "", "binds when": "no data", "n binding hours": 0})
            continue
        q = "; ".join(f"{x['lo']:,.0f}-{x['hi']:,.0f}: {x['bind_rate']:.3f} (n={x['n']})" for x in t["quintiles"])
        start = f"{t['start_pctile']} = {t['start_level']:,.0f} MW" if t.get("start_level") is not None else ""
        rows.append({"driver": var, "corr": t["corr"], "binds when": t["direction"], "n binding hours": t["n_neg"],
                     "P10": t.get("p10"), "P50": t.get("p50"), "P90": t.get("p90"), "where binding starts": start,
                     "binding rate by quintile (range MW: rate)": q})
    return pd.DataFrame(rows).fillna("").to_markdown(index=False)


def _month_lines(bc: dict, mname: str) -> list[str]:
    out = []
    cs, pooled = bc.get("config_span"), bc.get("pooled_month")
    if bc["n_month_hours"] == 0:
        end = f"{cs['end']:%Y-%m-%d}" if cs else "unknown"
        out.append(f"- No {mname} hours in window (fast-scan data for this config ends {end}).")
    else:
        out += [f"- Window {mname} on-peak (Mon-Fri HE7-22, ex-NERC holidays) hours with headroom<0: "
                f"{bc['pct_neg_onpeak_month']}% (study-topology fast-scan replay, not real-world P(bind))",
                f"- Window {mname} off-peak hours with headroom<0: {bc['pct_neg_offpeak_month']}%"]
        if bc['pct_neg_onpeak_month'] in (0, 0.0) and bc['pct_neg_offpeak_month'] in (0, 0.0):
            out.append(f"- Note: {mname} negative-headroom hours in the window are 0% on- and off-peak on THIS topology/config; "
                       f"the study-run binding evidence (LP shadow price, dispatch, structural lambda sections below) is the "
                       f"{mname}-specific evidence for this constraint.")
    if pooled and "error" not in pooled and pooled.get("p_bind") is not None:
        yrs = ", ".join(str(y) for y in pooled["years"])
        out.append(f"- Pooled history, all years ({yrs}), {mname} on-peak: headroom<0 in {100 * pooled['p_bind']:.1f}% of "
                   f"{pooled['n_onpeak_hours']:,} on-peak hours (the same pooled P(bind) the shortlist uses; not the window above).")
    elif pooled and "error" in pooled:
        out.append(f"- Pooled {mname} history unavailable: {pooled['error']}")
    else:
        out.append(f"- Pooled {mname} history: no on-peak {mname} hours stored for this config.")
    return out


def _curve_lines(sl: dict, outage_flow: dict | None, lp: dict | None) -> list[str]:
    steps = sl.get("steps") or []
    if not steps:
        return []
    rows = []
    for i, st in enumerate(steps, 1):
        flags = []
        if st.get("up_renewable"):
            flags.append("UP unit is wind/solar: cannot increase output, so its relief is curtailment-only; the engine prices it from its DAM "
                         "offer as ordinary up relief (it does not model it as curtailment)")
        if not st.get("up_committed", True):
            flags.append("up unit not DAM-committed (start required)")
        down_offer = f"{st['price_down']:.2f}" + (" (curtailment proxy)" if st.get("down_renewable") else "")
        rows.append({"step": i, "down unit": st["down"], "down SF": round(st["sf_down"], 3), "down offer $": down_offer,
                     "up unit": st["up"], "up SF": round(st["sf_up"], 3), "up offer $": round(st["price_up"], 2),
                     "delta-SF": st["dsf"], "step price $/MWh": st["lambda"], "pair MW": round(st["pair_mw"], 1),
                     "flow MW": round(st["depth_hi"] - st["depth_lo"], 1), "cumulative flow MW": round(st["depth_hi"], 1),
                     "flags": "; ".join(flags)})
    out = ["", "Depth curve (greedy cheapest pair per step; flow MW = pair MW x delta-SF):",
           pd.DataFrame(rows).to_markdown(index=False), ""]
    out.append(f"- Curve exhausted at {sl['exhaustion_depth_mw']} MW of flow relief.")
    if outage_flow:
        sfd = outage_flow["signed_fd"]
        verdict = "within" if sfd <= sl["exhaustion_depth_mw"] else "beyond"
        out.append(f"- The driving outage adds {sfd:+.1f} MW of flow: {verdict} the curve's {sl['exhaustion_depth_mw']} MW.")
    loc = sl.get("lp_p50_on_curve")
    if loc and lp:
        p50 = lp["p50"]
        if loc["where"] == "at_step":
            out.append(f"- The LP's P50 shadow price (${p50}) is reached at step {loc['step']} of the curve "
                       f"(depth {loc['depth_lo']:.1f}-{loc['depth_hi']:.1f} MW, step price ${loc['step_price']}).")
        elif loc["where"] == "below_first":
            out.append(f"- The LP's P50 shadow price (${p50}) is below the curve's first step (${loc['first_price']}).")
        elif loc["where"] == "above_last":
            out.append(f"- The LP's P50 shadow price (${p50}) is above the curve's last step (${loc['last_price']} at "
                       f"{loc['exhaustion_mw']:.1f} MW): the offer curve does not reach it.")
    out.append("")
    return out


def _flip_synthesis(f: dict | None, flip_df: pd.DataFrame) -> list[str]:
    """State the flip mechanism explicitly from the evidence in `f` (see analysis.deep_dive.flip_synthesis_facts)."""
    if f is None:
        return []
    c0, c1 = f["c0"], f["c1"]
    out = ["### Synthesis"]
    sf = f["sign_flip"]
    if sf:
        out.append(
            f"`{sf['name']}` sits on both flowgates with opposite effect: PSENS={sf['psens_0']:.4f} "
            f"on {c0['label']} vs PSENS={sf['psens_1']:.4f} on {c1['label']} -- the same injection "
            f"that loads one flowgate relieves the other.")
    if f["c0_names_c1"]:
        out.append(f"{c0['label']}'s top-ranked outage groups by SIGNED_FLOWDELTA include lines named "
                   f"for {c1['label']}'s own endpoints ({c1['fromname']}/{c1['toname']}) -- outaging "
                   f"near {c1['label']} is a directly-evidenced driver of flow moving onto {c0['label']}.")
    elif f["c1_names_c0"]:
        out.append(f"{c1['label']}'s top-ranked outage groups by SIGNED_FLOWDELTA include lines named "
                   f"for {c0['label']}'s own endpoints ({c0['fromname']}/{c0['toname']}) -- outaging "
                   f"near {c0['label']} is a directly-evidenced driver of flow moving onto {c1['label']}.")
    else:
        out.append("Neither constraint's top outage groups name the other constraint's own line by "
                   "endpoint -- the flip is evidenced by the tofinder impact ranking (section 4) and, "
                   "where present, the sign-flip above, but not by a direct 'outaging line A binds line B' "
                   "match in this data; treat the mechanism as correlational, not confirmed line-for-line.")
    if not sf and not f["c0_names_c1"] and not f["c1_names_c0"]:
        out[-1] = ("No shared dispatch node changes sign and no direct outage-group name match was found; "
                   "rely on the tofinder SIGNED_FLOWDELTA ranking in section 4 alone for the flip evidence.")
    out.append("")
    return out
