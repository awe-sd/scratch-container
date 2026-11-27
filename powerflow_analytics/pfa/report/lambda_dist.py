"""Console text for `pfa lambda-dist`."""
from __future__ import annotations

from pfa.analysis.lambda_dist import LambdaDist


def text(r: LambdaDist) -> str:
    out = [f"Relief set for study {r.study}, constraint {r.constraint}"]
    if r.stage == "relief":
        return "\n".join(out + ["  no relief-set units found (SF band empty or unmapped)"])
    if r.stage == "offers":
        return "\n".join(out + ["  no DAM offer/capacity data for mapped resources"])
    out.append(r.display[["BUSNUM", "ID", "SIDE", "SF", "SCED", "IS_RENEWABLE", "P60", "HSL", "AWARDED", "LSL"]].to_string(index=False))
    out.append(f"\nUP stack: {r.n_up} units, DOWN stack: {r.n_down} units ({r.n_curtail} curtailment)")
    out.append("\nlambda(depth):")
    for d, val in r.checkpoints:
        out.append(f"  D={d:>4} MW  lambda={'n/a' if val is None else f'${val:,.1f}'}")
    if r.stage == "no_config":
        return "\n".join(out + ["\nno fast-scan config found for this constraint — skipping distribution"])
    if r.stage == "no_need":
        return "\n".join(out + ["\nfast-scan config has no negative-headroom hours — no distribution"])
    cov = r.cov
    out.append(f"\nrelief set exhausts at D={cov['exhaustion_depth_mw']} MW of flow ({r.paired_mw:.0f} MW of paired capacity)")
    out.append(f"of {cov['n_hours']} negative-headroom hours (config {r.config_id}): "
               f"{cov['n_priced']} priced by this relief set, {cov['n_unpriceable']} need more relief than the set can supply")
    pct = r.pct
    if pct:
        out.append("\nlambda distribution (priced hours only):")
        out.append(f"  P25={pct.get('P25')}  P50={pct.get('P50')}  P75={pct.get('P75')}  P90={pct.get('P90')}  max={pct.get('max')}  n={pct.get('n')}")
    if r.regimes is not None:
        out.append("\nby solar regime (SOLAR_IMPACT > 1 MW = solar hour):")
        for label, p in r.regimes:
            out.append(f"  {label:>5}: P50=${p['P50']}  P90=${p['P90']}  n={p['n']}" if p else f"  {label:>5}: no priced hours")
    return "\n".join(out)
