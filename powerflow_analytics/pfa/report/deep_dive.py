"""Deep-dive markdown: turns pfa.analysis.deep_dive results into the report text."""
from __future__ import annotations

import numpy as np
import pandas as pd

from pfa import periods
from pfa.analysis.deep_dive import CORR_MATERIALITY, DRIVER_MARGIN


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
            lines += [f"- FAST_SCAN_CONFIG_ID: {bc['config_id']}; fast-scan hours in window: {bc['n_hours']} "
                      f"(wind matched: {bc['n_wind_matched']}, solar matched: {bc['n_solar_matched']} -- "
                      f"gaps are hours the regional feed doesn't cover, not silently dropped)",
                      f"- Driver attribution: **{_driver_text(bc['driver'])}**",
                      f"- Correlation of HEADROOM with wind by region / solar (system wind cap check: "
                      f"{bc['system_wind_cap_mw']} MW installed): `{_plain(bc['corr'])}`",
                      f"- Dominant wind region (only named if |corr| >= {CORR_MATERIALITY}): "
                      f"**{bc['dominant_wind_region'] or 'none material'}**",
                      f"- Approx. headroom<=0 trigger levels (90th-pctile of that variable AMONG the "
                      f"hours headroom was already negative, with n_neg = the count of such hours the "
                      f"pctile is computed over -- i.e. \"even at this much wind/solar the constraint can "
                      f"still bind\", not a hard cutoff; small n_neg means a thin, noisy estimate): "
                      f"`{_plain(bc['thresholds'])}`",
                      f"- Historical {mname} on-peak (Mon-Fri HE7-22, ex-NERC holidays) hours with headroom<0: "
                      f"{bc['pct_neg_onpeak_month']}% (study-topology fast-scan replay, not real-world P(bind))",
                      f"- Historical {mname} off-peak hours with headroom<0: {bc['pct_neg_offpeak_month']}%",
                      f"- Top negative-headroom hours-of-day (window-wide, not {mname}-only): {hod_str}",
                      *([f"- Note: this constraint's historical-replay negative-headroom hours in {mname} "
                         f"{'are 0% on- and off-peak' if bc['pct_neg_onpeak_month'] == 0 and bc['pct_neg_offpeak_month'] == 0 else 'are near-zero'} "
                         f"on THIS topology/config; the trigger levels above are estimated from negative-headroom "
                         f"hours found across the FULL history window (mostly outside {mname}), so treat them "
                         f"as \"what it takes anywhere in the sample,\" not \"what {mname} itself produced.\" "
                         f"The study-run binding evidence (LP shadow price, dispatch, structural lambda sections "
                         f"below) is the {mname}-specific evidence for this constraint."]
                        if (bc['pct_neg_onpeak_month'] in (0, 0.0) and bc['pct_neg_offpeak_month'] in (0, 0.0))
                        else []),
                      ""]

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
        if len(pf["marginal_units"]):
            lines += ["- Marginal units (BUSMARGCOSTMW≈EDMARGCOSTMW, MWMIN<MW<MWMAX) in binding runs:",
                      pf["marginal_units"].to_markdown(index=False)]
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
    if d["kind"] == "co":
        return f"co-driven by wind and solar (corr wind={d['wind_corr']}, solar={d['solar_corr']}; margin < {DRIVER_MARGIN})"
    if d["kind"] == "solar":
        return f"solar-driven (headroom corr with solar={d['solar_corr']}; {peak})"
    if d["kind"] == "wind":
        return f"wind-driven (headroom corr with system wind={d['wind_corr']}; {peak})"
    return f"load-driven (no wind/solar corr clears |{CORR_MATERIALITY}|; {peak})"


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
