"""Shadow price of a constraint from DAM offers: spread / shift-factor difference.

One home for the unit-qualification rule, the relief set, the price-versus-depth
curve and the single redispatch-pair price:

    lambda = (offer_up - offer_down) / (SF_down - SF_up)

- relief_set(): every unit that can relieve the constraint, with shift factor,
  DAM offer and headroom, and its up/down stacks; .curve() / .price_at(depth).
- pair_estimate(): the one redispatch pair the OPF leans on (top differential
  LPDELTAMW movers of the binding runs), priced from the same formula. The
  60-day DAM disclosure lags ~2 months.
Pair fill (study 14411, 231 constraints): 31 priced; 159 had no opposite-signed
mover inside the |SF| band (physical, not a pool-size artifact), 39 no pair with
SF_down - SF_up >= 0.02, 2 no offers.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from ..constraint_id import ConstraintId, constraint_key
from ..extract import dam_offers as dam_offers_reader, fastscan, shifts

PRICE_CAP = 5000.0
MIN_SF = 0.03       # a unit must actually move the constraint to qualify
MAX_SF = 0.9        # tighter coupling is radial/bottled, not dispatchable
PAIR_MIN_SF = 0.1   # dispatch-screen pair band: below this are self-scheduled renewables with no offer curve
PAIR_MAX_SF = 0.5   # above this are radial siblings of a bottled plant, not real redispatch

N_PAIR = 40         # movers per side considered before the SF filter
CURTAIL_PRICE = -25.0  # $/MWh PTC floor: renewable curtailment cost proxy
MAX_DEPTH_MW = 500.0
STACK_MIN_SF = MIN_SF  # raising to 0.1 emptied both stacks on 1436-2081-1@DWCSRAM5 (no committed units with offers)


# ------------------------------------------------------- rule and formula --

def qualifying(sf: pd.Series) -> pd.Series:
    """Boolean mask: MIN_SF <= |SF| <= MAX_SF (both edges inclusive, as pandas `between`)."""
    return sf.abs().between(MIN_SF, MAX_SF)


def spread_price(spread: float, delta_sf: float) -> float:
    """Uncapped, unfloored spread / delta-SF."""
    return spread / delta_sf


def clamp_price(lam: float, cap: float = PRICE_CAP) -> float:
    """Floor at 0 (a binding max-flow constraint's price is never negative), cap at `cap`."""
    return max(0.0, min(lam, cap))


def offer_lambda_range(spread_low: float, spread_high: float, delta_sf: float) -> tuple[float, float]:
    """Lambda range from marginal-unit offer spread / delta shift factor, capped (not floored)."""
    if delta_sf <= 0:
        raise ValueError("delta_sf must be positive")
    return (min(spread_price(spread_low, delta_sf), PRICE_CAP),
            min(spread_price(spread_high, delta_sf), PRICE_CAP))


# ------------------------------------------------------------- DAM offers --

def _offer_at(row, frac: float):
    """Offer price at `frac` of the curve's MW span (first point at or above it)."""
    pts = [(row[f"CURVEMW{i}"], row[f"CURVEPRICE{i}"]) for i in range(1, 11)
           if pd.notna(row[f"CURVEMW{i}"]) and pd.notna(row[f"CURVEPRICE{i}"])]
    if not pts:
        return None
    mt = pts[0][0] + frac * (pts[-1][0] - pts[0][0])
    for m, p in pts:
        if m >= mt:
            return p
    return pts[-1][1]


def pair_offers(sced: list[str], hours=(12, 18)) -> pd.DataFrame:
    """Median offer at 60%/90% of curve for the latest disclosed month (HE `hours`)."""
    df = dam_offers_reader.latest_curves_at_hours(sced, hours)
    if df.empty:
        return df
    df["P60"] = df.apply(lambda r: _offer_at(r, 0.6), axis=1)
    df["P90"] = df.apply(lambda r: _offer_at(r, 0.9), axis=1)
    return df.groupby("SETTLEMENTPOINTNAME")[["P60", "P90"]].median()


def dam_capacity(sced: list[str], hours=(7, 22)) -> pd.DataFrame:
    """Per-unit median offer price (P60) and headroom (HSL, AWARDEDQUANTITY, LSL)
    over the latest disclosed 2-week window, HE `hours` inclusive."""
    df = dam_offers_reader.latest_capacity_rows(sced, hours[0], hours[1])
    if df.empty:
        return df
    df["P60"] = df.apply(lambda r: _offer_at(r, 0.6), axis=1)
    return df.groupby("SETTLEMENTPOINTNAME").agg(
        P60=("P60", "median"), HSL=("HSL", "median"),
        LSL=("LSL", "median"), AWARDED=("AWARDEDQUANTITY", "median"))


# ------------------------------------------------------ unit -> offer key --

def sced_names(pair: pd.DataFrame, bus_names: pd.DataFrame, genunit: pd.DataFrame,
               scedname: pd.DataFrame) -> pd.DataFrame:
    """Map (BUSNUM, ID) -> bus name -> GENUNIT -> the key of its DAM offer rows (column SCED).

    Primary route (OFFER_ROUTE "cpnode"): GENUNIT.CPNODEID -> CPNODE name, the settlement point the offer
    table is keyed on; needs `genunit` to carry CPNODENAME (gen_mapping.with_cpnode_names). Fallback (route
    "name"), for units whose CPNODEID is null or has no CPNODE row: the GENUNITSCEDNAME name with its
    trailing unit index stripped (SCED_NAME). SCED holds whichever key the route gives; NaN when neither exists.

    No (BUSNUM, ID) -> GENUNITID bridge exists for ERCOT (OUTGENREF is empty for ISOMARKETID=6), so BUSNAME
    is the join key into GENUNIT. A bus with several units (e.g. a 3-train CC) has several GENUNIT rows
    sharing that BUSNAME, one per per-unit SCED index (JACKCNTY_CC1_1/_2/_3) — the same index carried in
    OUTGEN2.ID; matching that trailing index against ID picks the specific unit's row rather than a sibling's.
    """
    has_cp = "CPNODENAME" in genunit.columns
    gu = genunit.merge(scedname[scedname["KIND"] == "GEN"], on="GENUNITID", how="left")
    gu["CPNODENAME"] = gu["CPNODENAME"] if has_cp else None
    gu = gu[["BUSNAME", "NAME", "CPNODENAME"]].dropna(subset=["BUSNAME"])
    gu = gu[gu["NAME"].notna() | gu["CPNODENAME"].notna()].drop_duplicates()
    gu["SUFFIX"] = gu["NAME"].str.extract(r"_(\d+)$")[0]
    m = pair.merge(bus_names, on="BUSNUM", how="left").merge(gu, on="BUSNAME", how="left")
    m["ID"] = m["ID"].astype(str).str.strip()
    # no suffix match (index conventions differ): fall back to any candidate for the bus rather than dropping the unit
    m["_rank"] = (m["SUFFIX"] != m["ID"]).astype(int)
    m["_nocp"] = m["CPNODENAME"].isna().astype(int)
    m["_noname"] = m["NAME"].isna().astype(int)
    m = m.sort_values(["_rank", "_nocp", "_noname"], kind="mergesort")
    out = m.drop_duplicates(["BUSNUM", "ID", "SIDE"])
    out = pair.merge(out[["BUSNUM", "ID", "SIDE", "NAME", "CPNODENAME"]], on=["BUSNUM", "ID", "SIDE"], how="left")
    # SCED unit names carry a trailing unit index (JACKCNTY_CC1_1); the DAM disclosure keys on the settlement point (JACKCNTY_CC1)
    out["SCED_NAME"] = out["NAME"].str.replace(r"_\d+$", "", regex=True)
    out["OFFER_ROUTE"] = out["CPNODENAME"].notna().map({True: "cpnode", False: None})
    out.loc[out["CPNODENAME"].isna() & out["SCED_NAME"].notna(), "OFFER_ROUTE"] = "name"
    out["SCED"] = out["CPNODENAME"].where(out["CPNODENAME"].notna(), out["SCED_NAME"])
    return out


# ------------------------------------------------------------- relief set --

def _relief_units(study_id: int, constraint: str, gen: pd.DataFrame, bus_names: pd.DataFrame,
                  genunit: pd.DataFrame, scedname: pd.DataFrame, direction: int) -> tuple[pd.DataFrame, int]:
    """(in-band units with their offer key and route, one row per study unit; count of study units in the SF band before mapping)."""
    cid = ConstraintId.parse(constraint)
    sfs = shifts.bus_sf_all_buses(study_id, cid)
    if sfs.empty:
        return pd.DataFrame(), 0
    sfs["SF"] = sfs["SF"].astype(float) * int(direction)
    sfs = sfs[qualifying(sfs["SF"])]
    if sfs.empty:
        return pd.DataFrame(), 0

    units = gen[["BUSNUM", "ID", "FUELTYPE", "MW", "MWMAX"]].drop_duplicates(["BUSNUM", "ID"])
    pair = units.merge(sfs[["BUSNUM", "SF"]], on="BUSNUM", how="inner")
    n_band = len(pair)
    pair["SIDE"] = pair["SF"].apply(lambda x: "down" if x > 0 else "up")
    mapped = sced_names(pair, bus_names, genunit, scedname)
    mapped = mapped.dropna(subset=["SCED"])
    # OUTGEN2.FUELTYPE carries ERCOT fuel codes, e.g. "WND (Wind)" / "SUN (Solar)"
    RENEW_CODES = ("WND", "SUN")
    mapped["IS_RENEWABLE"] = mapped["FUELTYPE"].astype(str).str.upper().str.startswith(RENEW_CODES)
    return mapped, n_band


def _fall_back_to_name(units: pd.DataFrame, cap: pd.DataFrame) -> pd.DataFrame:
    """A CPNODE-route key with no offer rows in the window is unresolved: use the SCED-name key where that one has rows
    (combined cycles: CPNODEID names the unit node, the offer table is keyed on the plant node). See CLAUDE.md 2026-11-27."""
    miss = (units["OFFER_ROUTE"] == "cpnode") & ~units["SCED"].isin(cap.index) & units["SCED_NAME"].isin(cap.index)
    out = units.copy()
    out.loc[miss, "SCED"] = out.loc[miss, "SCED_NAME"]
    out.loc[miss, "OFFER_ROUTE"] = "name"
    return out


def _one_row_per_key(mapped: pd.DataFrame) -> pd.DataFrame:
    """Several (BUSNUM, ID) units can share one offer key (a resource node serving a plant): one row per (key, SIDE),
    strongest |SF|, IS_RENEWABLE OR-ed, or the same offer curve's headroom is counted twice (once as gas, once as curtailment)."""
    mapped = mapped.copy()
    mapped["_absSF"] = mapped["SF"].abs()
    mapped["IS_RENEWABLE"] = mapped.groupby(["SCED", "SIDE"])["IS_RENEWABLE"].transform("any")
    return (mapped.sort_values("_absSF", ascending=False, kind="mergesort")
            .drop_duplicates(["SCED", "SIDE"]).drop(columns="_absSF"))


def build_stacks(relief: pd.DataFrame, cap: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    """UP stack (negative-SF units, ascending offer price) and DOWN stack
    (positive-SF units, descending offer price, with a renewable-curtailment
    leg at CURTAIL_PRICE for renewable positive-SF units that clear the SF band)."""
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
            # AWARDED==0 means DAM did not commit the unit (headroom is a startup decision): flag, don't exclude
            committed = float(row["AWARDED"]) > 0.0
            up.append({"sced": sced, "sf": sf_val, "price": float(row["P60"]), "avail": avail,
                      "committed": committed, "renewable": bool(r["IS_RENEWABLE"])})
        else:
            avail = max(0.0, float(row["AWARDED"]) - float(row["LSL"]))
            offer = float(row["P60"])
            if bool(r["IS_RENEWABLE"]):
                price = CURTAIL_PRICE
                avail = max(0.0, float(row["AWARDED"]))  # curtailable to 0
            else:
                price = float(row["P60"])
            if avail <= 0:
                continue
            down.append({"sced": sced, "sf": sf_val, "price": price, "avail": avail,
                         "renewable": bool(r["IS_RENEWABLE"]), "offer": offer})
    up.sort(key=lambda b: b["price"])
    down.sort(key=lambda b: -b["price"])
    return up, down


def lambda_depth_curve(up: list[dict], down: list[dict],
                       max_depth: float = MAX_DEPTH_MW) -> list[dict]:
    """Greedily consume the cheapest-per-MW-of-flow (up, down) pair at each
    step. Cost of a pair = (up.price - down.price) / (SF_down - SF_up);
    its flow-relief capacity = min(up.avail, down.avail) * dsf. Steps are
    (depth_lo, depth_hi, lambda) bands, non-decreasing in depth."""
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
                lam = spread_price(u["price"] - d["price"], dsf)
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
        # selection above uses the raw (possibly negative) lam so free pairs go first; the recorded value is floored
        lam = clamp_price(lam)
        steps.append({"depth_lo": depth, "depth_hi": depth + cap_flow,
                      "lambda": round(lam, 2), "pair": f"{d['sced']}↓/{u['sced']}↑",
                      "dsf": round(dsf, 3), "up_committed": bool(u.get("committed", True)),
                      "up": u["sced"], "down": d["sced"], "sf_up": u["sf"], "sf_down": d["sf"],
                      "price_up": u["price"], "price_down": d["price"], "pair_mw": cap_mw,
                      "up_renewable": bool(u.get("renewable", False)), "down_renewable": bool(d.get("renewable", False))})
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


@dataclass
class ReliefSet:
    """Units that can relieve one constraint. `units` is empty when no unit is in the SF band;
    `capacity` is empty when none of them has a DAM offer; `up`/`down` are the priced stacks;
    `n_band` counts study units inside the SF band before the SCED mapping."""
    units: pd.DataFrame
    capacity: pd.DataFrame = field(default_factory=pd.DataFrame)
    up: list = field(default_factory=list)
    down: list = field(default_factory=list)
    _curve: list | None = field(default=None, repr=False)
    n_band: int = 0

    def curve(self) -> list[dict]:
        if self._curve is None:
            self._curve = lambda_depth_curve(self.up, self.down)
        return self._curve

    def price_at(self, depth: float) -> float | None:
        return lambda_at_depth(self.curve(), depth)


def relief_set(study_id: int, constraint: str, gen: pd.DataFrame, bus_names: pd.DataFrame,
               genunit: pd.DataFrame, scedname: pd.DataFrame, direction: int = 1) -> ReliefSet:
    """Every unit with a qualifying |SF| on `constraint` (LZ_/WZ_ excluded), mapped to its
    DAM offer key (see sced_names; `units["OFFER_ROUTE"]` is the route), with DAM offers and the up/down stacks.

    Starts from every unit in the study's gen table and prices its SF off BUS_SHIFTS_VIEW.
    `direction` must be the fast-scan config's DIRECTION when the branch is bound in the
    reverse (-1) sense: SIDE is assigned off SF * direction, and a wrong direction puts every
    unit on the wrong side (study 14412 3380-3390-1@DPNAONA5, DIRECTION=-1, priced all
    relief at 0 before this).
    """
    mapped, n_band = _relief_units(study_id, constraint, gen, bus_names, genunit, scedname, direction)
    if mapped.empty:
        return ReliefSet(mapped, n_band=n_band)
    keys = set(mapped["SCED"]) | set(mapped["SCED_NAME"].dropna())
    cap = dam_capacity(sorted(keys))
    units = _one_row_per_key(_fall_back_to_name(mapped, cap)) if not cap.empty else _one_row_per_key(mapped)
    cap = cap.loc[cap.index.intersection(units["SCED"])] if not cap.empty else cap
    if cap.empty:
        return ReliefSet(units, cap, n_band=n_band)
    up, down = build_stacks(units, cap)
    return ReliefSet(units, cap, up, down, n_band=n_band)


# ------------------------------------------------- need -> price distribution --

def fastscan_need(config_id: int) -> pd.DataFrame:
    """Raw negative-headroom hours for a fast-scan config: need = -HEADROOM."""
    df = fastscan.negative_headroom(config_id)
    if df.empty:
        return df
    df["NEED_MW"] = -df["HEADROOM"].astype(float)
    return df


def lambda_distribution(curve: list[dict], need: pd.DataFrame) -> pd.DataFrame:
    """Map each negative-headroom hour's need (MW) through lambda(depth); hours
    beyond the relief set's capacity get LAMBDA=NaN (unpriceable, to be counted by the caller)."""
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


# ----------------------------------------------------- single redispatch pair --

# one report run passes the same ctgviol/gen objects for every constraint: memoize their per-study allocations
_ckey_cache: dict[int, pd.Series] = {}
_gen_pivot_cache: dict[int, pd.DataFrame] = {}


def _ctgviol_keys(ctgviol: pd.DataFrame) -> pd.Series:
    key = id(ctgviol)
    keys = _ckey_cache.get(key)
    if keys is None or len(keys) != len(ctgviol):
        keys = constraint_key(ctgviol)
        _ckey_cache.clear()
        _ckey_cache[key] = keys
    return keys


def _gen_pivot(gen: pd.DataFrame) -> pd.DataFrame:
    key = id(gen)
    piv = _gen_pivot_cache.get(key)
    if piv is None:
        piv = gen.pivot_table(index=["BUSNUM", "ID"], columns="RUNID",
                               values="LPDELTAMW", aggfunc="mean")
        _gen_pivot_cache.clear()
        _gen_pivot_cache[key] = piv
    return piv


def redispatch_pair(ctgviol: pd.DataFrame, gen: pd.DataFrame, constraint: str,
                    binding_pct: float = 99.5) -> pd.DataFrame | None:
    """Top up/down movers (differential LPDELTAMW) with bus numbers."""
    keys = _ctgviol_keys(ctgviol)
    mask = (keys.values == constraint) & (ctgviol["LIMVIOLPCT"].values >= binding_pct)
    binding_runs = set(ctgviol.loc[mask, "RUNID"])
    if not binding_runs:
        return None
    piv = _gen_pivot(gen)
    b_cols = [c for c in piv.columns if c in binding_runs]
    if not b_cols:
        return None
    o_cols = [c for c in piv.columns if c not in binding_runs]
    binding_mean = piv[b_cols].mean(axis=1)
    other_mean = piv[o_cols].mean(axis=1) if o_cols else 0.0
    diff = (binding_mean.fillna(0) - (other_mean.fillna(0) if o_cols else 0.0)).rename("DIFF_MW")
    out = diff.reset_index()
    up = out.nlargest(N_PAIR, "DIFF_MW")
    down = out.nsmallest(N_PAIR, "DIFF_MW")
    res = pd.concat([up.assign(SIDE="up"), down.assign(SIDE="down")])
    return res[abs(res["DIFF_MW"]) > 20]


def pair_price(up: pd.DataFrame, down: pd.DataFrame, offers: pd.DataFrame) -> dict | None:
    """Price the candidate (up, down) pairs: lo = P60/P60 spread, hi = P90(up)/P60(down) spread,
    each floored at 0 and divided by SF_down - SF_up (>= 0.02). Floor = cheapest pair (the LP's
    first move); ceiling = the most expensive pair, where the price goes as pairs exhaust."""
    cands = []
    for _, u in up.iterrows():
        for _, d in down.iterrows():
            dsf = float(d["SF"] - u["SF"])
            if dsf < 0.02 or u["SCED"] not in offers.index or d["SCED"] not in offers.index:
                continue
            lo = spread_price(max(0.0, float(offers.loc[u["SCED"], "P60"] - offers.loc[d["SCED"], "P60"])), dsf)
            hi = spread_price(max(0.0, float(offers.loc[u["SCED"], "P90"] - offers.loc[d["SCED"], "P60"])), dsf)
            cands.append({"lo": lo, "hi": hi, "dsf": dsf,
                          "pair": f"{d['SCED']}↓/{u['SCED']}↑"})
    if not cands:
        return None
    cands.sort(key=lambda c: c["lo"])
    deepest = max(cands, key=lambda c: c["hi"])
    return {"lam_lo": round(min(cands[0]["lo"], PRICE_CAP), 1),
            "lam_hi": round(min(deepest["hi"], PRICE_CAP), 1),
            "dsf": round(cands[0]["dsf"], 3),
            "pair": f"{cands[0]['pair']} → {deepest['pair']}"}


def pair_estimate(study_id: int, ctgviol: pd.DataFrame, gen: pd.DataFrame,
                  bus_names: pd.DataFrame, genunit: pd.DataFrame, scedname: pd.DataFrame,
                  constraint: str) -> dict | None:
    """lambda range for one constraint; None when the chain has no coverage."""
    pair = redispatch_pair(ctgviol, gen, constraint)
    if pair is None or pair.empty or (pair["SIDE"] == "up").sum() == 0:
        return None
    pair = sced_names(pair, bus_names, genunit, scedname)
    sfs = shifts.bus_sf_for_buses(study_id, ConstraintId.parse(constraint), pair["BUSNUM"].tolist())
    sfs["SF"] = sfs["SF"].astype(float)
    pair = pair.merge(sfs, on="BUSNUM", how="left")
    # only units that actually move the constraint are its marginal pair; rank by redispatch effectiveness
    pair = pair[qualifying(pair["SF"])].copy()
    pair["EFF"] = (pair["DIFF_MW"] * pair["SF"]).abs()
    pair = pair.sort_values("EFF", ascending=False).groupby("SIDE").head(4)
    up = pair[(pair["SIDE"] == "up") & pair["SCED"].notna() & pair["SF"].notna()]
    down = pair[(pair["SIDE"] == "down") & pair["SCED"].notna() & pair["SF"].notna()]
    if up.empty or down.empty:
        return None
    offers = pair_offers(pd.concat([up, down])["SCED"].tolist())
    if offers.empty:
        return None
    return pair_price(up, down, offers)
