"""Shadow-price (lambda) DISTRIBUTION from DAM offer curves — a realistic
replacement for the single-point offer spread in offer_lambda.estimate().

Where offer_lambda.py prices ONE redispatch pair (the top differential
mover on each side, from a specific set of binding runs), this module
builds the full RELIEF SET for a constraint — every unit whose shift
factor actually couples it to the flowgate — and greedily pairs cheapest
available MW across the whole set as relief depth grows. That produces a
lambda(depth) curve instead of a lambda(pair) point estimate, plus a
mapping of that curve onto the fast-scan need distribution (how many
historical hours needed how much relief) to get a lambda DISTRIBUTION.

Relief-set membership and unit->SCED-name mapping intentionally reuse the
BUSNAME->GENUNIT->GENUNITSCEDNAME chain from offer_lambda.sced_names()
rather than OUTGEN2.CPNODENAME: OUTGEN2 does not carry a CPNODENAME/
UNITNAME_STUDY column in this schema (checked directly — only RUNID,
LABEL, GENUNITID, BUSNUM, ID, UNITTYPE, MW, MWMIN, MWMAX, EDMARGCOSTMW,
BUSMARGCOSTMW, GENSTATUS, LPDELTAMW, AGC, PARTFACT, FUELTYPE, FUELZONE,
RENEWZONE, AREANAME, ZONENAME), and offer_lambda.fetch_gen's own docstring
records that the alternate CPNODE.DISPLAYNAME source was tried and its
names don't appear in ERCOT60DDAMGENRESOURCE.SETTLEMENTPOINTNAME at all —
only the GENUNITSCEDNAME-derived name matches the DAM disclosure. Reusing
the working chain avoids re-breaking that already-diagnosed mapping.
"""
from __future__ import annotations

import re

import pandas as pd

from .. import sf
from .offer_lambda import MAX_SF, MIN_SF, sced_names
from .valuation import PRICE_CAP

CURTAIL_PRICE = -25.0  # $/MWh PTC floor: renewable curtailment cost proxy
MAX_DEPTH_MW = 500.0
DEPTH_CHECKPOINTS = (25, 50, 100, 200, 400)

# Attempted stack-membership floor of 0.1 (matching offer_lambda.PAIR_MIN_SF,
# to keep dsf wider and avoid pricing off self-scheduled-renewable SF noise)
# was tried and reverted: on 1436-2081-1@DWCSRAM5 it emptied BOTH stacks —
# the units that clear 0.1 (WCPP_CC1, JCKCNTY2_CC1, CHISMGRD_BES1,
# PINN_SLR_UNIT3, ...) either have AWARDED=0/NaN in the current DAM window
# (WCPP_CC1: HSL=379, LSL=152, AWARDED=0 -> zero down-availability, i.e. not
# committed) or no ERCOT60DDAMGENRESOURCE row at all (BESS/self-scheduled
# solar). Raising the floor doesn't reproduce the architect's $200-300
# curtailment band here — it just removes the only unit with a real offer
# curve. Left at MIN_SF (0.03) per spec; see lambda_distribution.py's
# printed report for the resulting dsf/coverage discussion.
STACK_MIN_SF = MIN_SF


def relief_set(study_id: int, constraint: str, gen: pd.DataFrame,
               bus_names: pd.DataFrame, genunit: pd.DataFrame,
               scedname: pd.DataFrame) -> pd.DataFrame:
    """Every unit with MIN_SF <= |SF| < MAX_SF on `constraint`, excluding
    LZ_/WZ_ aggregate rows, mapped to its DAM/SCED resource name.

    Unlike offer_lambda.redispatch_pair (which starts from the top movers
    in a specific set of binding OPF runs), this starts from every unit in
    the study's gen table and prices its SF directly off BUS_SHIFTS_VIEW —
    the full relief set, not just the top differential movers.
    """
    f, t, rest = constraint.split("-", 2)
    ckt, ctg = rest.split("@")
    sfs = sf.query("SHIFT_FACTORS", f"""
        SELECT BUSNUM, NAME, AVG(PSENS) SF
        FROM SHIFT_FACTORS.DBO.BUS_SHIFTS_VIEW
        WHERE ISOMARKETID=6 AND STUDYID={int(study_id)}
          AND FROMNUM={int(f)} AND TONUM={int(t)} AND CKT='{ckt}' AND CTGLABEL='{ctg}'
          AND LEFT(NAME, 3) NOT IN ('LZ_', 'WZ_')
        GROUP BY BUSNUM, NAME""")
    if sfs.empty:
        return pd.DataFrame()
    sfs["SF"] = sfs["SF"].astype(float)
    sfs = sfs[sfs["SF"].abs().between(MIN_SF, MAX_SF)]
    if sfs.empty:
        return pd.DataFrame()

    units = gen[["BUSNUM", "ID", "FUELTYPE", "MW", "MWMAX"]].drop_duplicates(["BUSNUM", "ID"])
    pair = units.merge(sfs[["BUSNUM", "SF"]], on="BUSNUM", how="inner")
    pair["SIDE"] = pair["SF"].apply(lambda x: "down" if x > 0 else "up")
    mapped = sced_names(pair, bus_names, genunit, scedname)
    mapped = mapped.dropna(subset=["SCED"])
    # OUTGEN2.FUELTYPE carries ERCOT fuel codes, e.g. "WND (Wind)" / "SUN (Solar)"
    RENEW_CODES = ("WND", "SUN")
    mapped["IS_RENEWABLE"] = mapped["FUELTYPE"].astype(str).str.upper().str.startswith(RENEW_CODES)
    # Several (BUSNUM, ID) units (e.g. a 3-train unit or a multi-row solar
    # farm) collapse to one SCED resource name. build_stacks prices per
    # SCED, so dedup here — one row per (SCED, SIDE), keeping the strongest
    # |SF| row and OR-ing IS_RENEWABLE across the group — or the same
    # physical resource's headroom gets double/triple-counted and can enter
    # the DOWN stack twice (once as gas price, once as curtailment price).
    mapped["_absSF"] = mapped["SF"].abs()
    is_renew = mapped.groupby(["SCED", "SIDE"])["IS_RENEWABLE"].transform("any")
    mapped["IS_RENEWABLE"] = is_renew
    mapped = (mapped.sort_values("_absSF", ascending=False)
              .drop_duplicates(["SCED", "SIDE"]).drop(columns="_absSF"))
    return mapped


def dam_capacity(sced: list[str], hours=(7, 22)) -> pd.DataFrame:
    """Per-unit median offer price (P60) and headroom (HSL, AWARDEDQUANTITY,
    LSL) over the latest disclosed 2-week window, HE 7-22."""
    names = ",".join(f"'{re.sub(chr(39), '', s)}'" for s in set(sced) if isinstance(s, str))
    if not names:
        return pd.DataFrame()
    cols = ",".join(f"CURVEMW{i},CURVEPRICE{i}" for i in range(1, 11))
    df = sf.query("AW", f"""
        SELECT SETTLEMENTPOINTNAME, HSL, LSL, AWARDEDQUANTITY, {cols}
        FROM AW.DBO.ERCOT60DDAMGENRESOURCE
        WHERE DELIVERYDATE >= DATEADD(day, -14, (SELECT MAX(DELIVERYDATE) FROM AW.DBO.ERCOT60DDAMGENRESOURCE))
          AND HOURENDING BETWEEN {hours[0]} AND {hours[1]}
          AND SETTLEMENTPOINTNAME IN ({names})
        LIMIT 200000""")
    if df.empty:
        return df
    if len(df) >= 200000:
        raise RuntimeError(
            "dam_capacity: hit the 200000-row LIMIT — results are truncated; "
            "narrow the hour window or relief set before trusting P60/HSL/AWARDED"
        )

    def p60(row):
        pts = [(row[f"CURVEMW{i}"], row[f"CURVEPRICE{i}"]) for i in range(1, 11)
               if pd.notna(row[f"CURVEMW{i}"]) and pd.notna(row[f"CURVEPRICE{i}"])]
        if not pts:
            return None
        mt = pts[0][0] + 0.6 * (pts[-1][0] - pts[0][0])
        for m, p in pts:
            if m >= mt:
                return p
        return pts[-1][1]

    df["P60"] = df.apply(p60, axis=1)
    agg = df.groupby("SETTLEMENTPOINTNAME").agg(
        P60=("P60", "median"), HSL=("HSL", "median"),
        LSL=("LSL", "median"), AWARDED=("AWARDEDQUANTITY", "median"))
    return agg


def build_stacks(relief: pd.DataFrame, cap: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    """UP stack (negative-SF units, sorted by ascending offer price) and
    DOWN stack (positive-SF units, sorted by descending offer price, with
    a renewable-curtailment leg at CURTAIL_PRICE for renewable positive-SF
    units that clear the SF band)."""
    up, down = [], []
    for _, r in relief.iterrows():
        sced = r["SCED"]
        if sced not in cap.index or abs(float(r["SF"])) < STACK_MIN_SF:
            continue
        row = cap.loc[sced]
        sf_val = float(r["SF"])
        if r["SIDE"] == "up":
            avail = max(0.0, float(row["HSL"]) - float(row["AWARDED"]))
            if avail <= 0:
                continue
            up.append({"sced": sced, "sf": sf_val, "price": float(row["P60"]), "avail": avail})
        else:
            avail = max(0.0, float(row["AWARDED"]) - float(row["LSL"]))
            if bool(r["IS_RENEWABLE"]):
                price = CURTAIL_PRICE
                avail = max(0.0, float(row["AWARDED"]))  # curtailable to 0
            else:
                price = float(row["P60"])
            if avail <= 0:
                continue
            down.append({"sced": sced, "sf": sf_val, "price": price, "avail": avail})
    up.sort(key=lambda b: b["price"])
    down.sort(key=lambda b: -b["price"])
    return up, down


def lambda_depth_curve(up: list[dict], down: list[dict],
                       max_depth: float = MAX_DEPTH_MW) -> list[dict]:
    """Greedily consume the cheapest-per-MW-of-flow (up, down) pair at each
    step. Cost of a pair = (up.price - down.price) / (SF_down - SF_up);
    its flow-relief capacity = min(up.avail, down.avail) * dsf. Steps are
    accumulated as (depth_lo, depth_hi, lambda) bands; the curve is
    non-decreasing in depth by construction (UP ascending, DOWN
    descending, so the argmin pair only gets pricier as cheap capacity is
    exhausted)."""
    up = [dict(b) for b in up]
    down = [dict(b) for b in down]
    steps = []
    depth = 0.0
    while depth < max_depth and up and down:
        best = None
        for ui, u in enumerate(up):
            for di, d in enumerate(down):
                dsf = d["sf"] - u["sf"]
                if dsf <= 0.001:
                    continue
                lam = (u["price"] - d["price"]) / dsf
                if best is None or lam < best[0]:
                    best = (lam, ui, di, dsf)
        if best is None:
            break
        lam, ui, di, dsf = best
        u, d = up[ui], down[di]
        cap_mw = min(u["avail"], d["avail"])
        cap_flow = cap_mw * dsf
        if cap_flow <= 1e-6:
            # exhausted pair with no flow capacity; drop the emptier side
            (up if u["avail"] <= d["avail"] else down).pop(ui if u["avail"] <= d["avail"] else di)
            continue
        lam = min(lam, PRICE_CAP)
        steps.append({"depth_lo": depth, "depth_hi": depth + cap_flow,
                      "lambda": round(lam, 2), "pair": f"{d['sced']}↓/{u['sced']}↑",
                      "dsf": round(dsf, 3)})
        depth += cap_flow
        u["avail"] -= cap_mw
        d["avail"] -= cap_mw
        if u["avail"] <= 1e-6:
            up.pop(ui)
        if d["avail"] <= 1e-6:
            down.pop(di)
    return steps


def lambda_at_depth(curve: list[dict], depth: float) -> float | None:
    """None once `depth` exceeds the relief set's total flow capacity — the
    curve has genuinely exhausted, not "priced at the last band forever"."""
    for step in curve:
        if step["depth_lo"] <= depth < step["depth_hi"]:
            return step["lambda"]
    return None


def fastscan_need(config_id: int) -> pd.DataFrame:
    """Raw negative-headroom hours for a fast-scan config: need = -HEADROOM."""
    df = sf.query("AWDEV", f"""
        SELECT TIMESTAMP, HEADROOM
        FROM AWDEV.FLOW_ANALYSIS.FAST_SCAN_RESULTS
        WHERE CONFIG_ID = {int(config_id)} AND HEADROOM < 0
    """)
    if df.empty:
        return df
    df["NEED_MW"] = -df["HEADROOM"].astype(float)
    return df


def lambda_distribution(curve: list[dict], need: pd.DataFrame) -> pd.DataFrame:
    """Map each negative-headroom hour's need (MW) through lambda(depth).
    Hours whose need exceeds the relief set's total flow capacity get
    LAMBDA=NaN (unpriceable by this relief set, not "priced at the last
    band") — the caller should report how many hours that is, not silently
    drop them into the percentile table."""
    out = need.copy()
    out["LAMBDA"] = out["NEED_MW"].apply(lambda d: lambda_at_depth(curve, d))
    return out


def coverage(dist: pd.DataFrame, curve: list[dict]) -> dict:
    total = len(dist)
    priced = int(dist["LAMBDA"].notna().sum())
    exhaustion_mw = curve[-1]["depth_hi"] if curve else 0.0
    return {"n_hours": total, "n_priced": priced,
            "n_unpriceable": total - priced,
            "exhaustion_depth_mw": round(exhaustion_mw, 1)}


def percentiles(lam: pd.Series) -> dict:
    lam = lam.dropna()
    if lam.empty:
        return {}
    return {"P25": round(lam.quantile(0.25), 1), "P50": round(lam.quantile(0.50), 1),
            "P75": round(lam.quantile(0.75), 1), "P90": round(lam.quantile(0.90), 1),
            "max": round(lam.max(), 1), "n": int(lam.shape[0])}


def solar_regime(config_id: int) -> pd.DataFrame:
    """TIMESTAMP -> SOLAR_IMPACT for the same config, so a caller can split
    the lambda distribution by solar/dark regime without a separate
    solarGenAct join — FAST_SCAN_RESULTS already carries per-hour
    SOLAR_IMPACT (MW of solar's contribution to headroom relief)."""
    return sf.query("AWDEV", f"""
        SELECT TIMESTAMP, SOLAR_IMPACT
        FROM AWDEV.FLOW_ANALYSIS.FAST_SCAN_RESULTS
        WHERE CONFIG_ID = {int(config_id)}
    """)
