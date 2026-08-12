"""Independent shadow-price estimate: DAM bid curves + shift factors.

For a constraint, find the redispatch pair the OPF leans on (differential
LPDELTAMW), get both units' shift factors on the constraint
(BUS_SHIFTS_VIEW), map the units to their DAM resources
(bus name -> GENUNIT.BUSNAME -> naturalKey=SCED:<resource> -> 60-day DAM
disclosure), and price the redispatch:

    lambda = (offer_up - offer_down) / (SF_down - SF_up)

offer_up is taken high on the relief unit's curve (it is being pushed up),
offer_down low on the displaced unit's curve. The 60-day disclosure lags, so
offers reflect conditions ~2 months back; the system energy lambda enters
implicitly through where the units sit on their curves. Capped at $5000.

Fill diagnosis (2026-08-11, study 14411, 231 candidate constraints): 31 filled
before this pass; a full stage-by-stage breakdown of the 200 that returned
None found:
  - redispatch_pair empty: 0 — never the cause.
  - one-sided after the |SF| filter (up XOR down empty once SCED-mapped
    candidates are restricted to MIN_SF<=|SF|<MAX_SF): 159/231 (69%) — the
    dominant, and largely genuine, cause. Doubling N_PAIR 40->80 (deeper
    candidate pool before the SF filter) only recovered 1 more constraint
    (31->32) — this is a physical fact about the flowgate, not a
    candidate-pool artifact: most binding constraints simply do not have a
    material opposite-signed mover among their top movers, i.e. no genuine
    redispatch pair exists (the same fact Defect 2's dispatch_screen pair
    rule now surfaces independently as "unenforceable").
  - dam_offers() returned nothing for the mapped SCED names: 2/231 —
    negligible; self-scheduled/no-offer-curve units are not the dominant
    cause here (contra the original hypothesis).
  - candidates existed and offers were found, but no pair cleared
    dsf=SF_down-SF_up>=0.02: 39/231 — a real chain, just insufficient SF
    separation between the two sides' resources; not chased further.
  - ok: 31/231 (32/231 at N_PAIR=80).
Net: the 31/231 fill is not a mechanical bug in the mapping/join chain (see
extract/results.py:fetch_gen for the two alternate SCED-name sources that
were checked and ruled out) — it reflects that most binding constraints in
this study genuinely lack a two-sided dispatchable pair, which is also why
Defect 2's dispatch_screen flags many of the same constraints unenforceable.
"""
from __future__ import annotations

import re

import pandas as pd

from .. import sf
from .constraints import constraint_key
from .valuation import PRICE_CAP

N_PAIR = 40   # movers per side considered before shift-factor filtering
              # (widened from 15: the |SF|>=MIN_SF filter needs a deep enough
              # candidate pool or the top-DIFF_MW movers alone often clear
              # neither side, leaving the pair unpopulated)
MIN_SF = 0.03  # a unit must actually move the constraint to be its marginal pair
MAX_SF = 0.9   # a candidate this tightly coupled is radial/bottled, not a dispatchable pair

# Per-study memoization for the two hot allocations `estimate()` re-triggers
# once per constraint (hundreds of times a run): the ctgviol CONSTRAINT key
# column, and the (BUSNUM, ID) x RUNID LPDELTAMW pivot behind redispatch_pair.
# Keyed on id() of the frame the caller passes in — valid because a single
# report run passes the *same* ctgviol/gen objects for every constraint.
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


def bus_shift_factors(study_id: int, constraint: str, busnums: list[int]) -> pd.DataFrame:
    f, t, rest = constraint.split("-", 2)
    ckt, ctg = rest.split("@")
    ids = ",".join(str(int(b)) for b in set(busnums))
    return sf.query("SHIFT_FACTORS", f"""
        SELECT BUSNUM, AVG(PSENS) SF
        FROM SHIFT_FACTORS.DBO.BUS_SHIFTS_VIEW
        WHERE ISOMARKETID=6 AND STUDYID={int(study_id)}
          AND FROMNUM={int(f)} AND TONUM={int(t)} AND CKT='{ckt}' AND CTGLABEL='{ctg}'
          AND BUSNUM IN ({ids})
        GROUP BY BUSNUM""")


def sced_names(pair: pd.DataFrame, bus_names: pd.DataFrame, genunit: pd.DataFrame,
               scedname: pd.DataFrame) -> pd.DataFrame:
    """Map (BUSNUM, ID) -> bus name -> GENUNIT -> GENUNITSCEDNAME -> SCED resource name.

    No (BUSNUM, ID) -> GENUNITID bridge exists for ERCOT (OUTGENREF is empty
    for ISOMARKETID=6), so BUSNAME is still the join key into GENUNIT. The
    fix is disambiguation once there: a bus with several units (e.g. a
    3-train CC) has several GENUNITSCEDNAME rows sharing that BUSNAME, one
    per per-unit SCED index (JACKCNTY_CC1_1/_2/_3) — the same index carried
    in OUTGEN2.ID. Matching that trailing index against ID, instead of the
    old drop_duplicates("BUSNAME"), picks the *specific* unit's SCED name
    rather than an arbitrary sibling's.
    """
    gu = genunit.merge(scedname[scedname["KIND"] == "GEN"], on="GENUNITID", how="inner")
    gu = gu[["BUSNAME", "NAME"]].dropna().drop_duplicates()
    gu["SUFFIX"] = gu["NAME"].str.extract(r"_(\d+)$")[0]
    m = pair.merge(bus_names, on="BUSNUM", how="left").merge(gu, on="BUSNAME", how="left")
    m["ID"] = m["ID"].astype(str).str.strip()
    # prefer the row whose SCED-name suffix matches OUTGEN2.ID (the specific
    # unit at a multi-unit bus); if nothing matches (index conventions can
    # differ, or the bus never had ID-suffix data), fall back to whatever
    # candidate is available for that bus rather than dropping the unit —
    # matches the old BUSNAME-only behavior for the buses where it was right,
    # while fixing the ones with a genuine sibling-unit ambiguity
    m["_rank"] = (m["SUFFIX"] != m["ID"]).astype(int)
    m = m.sort_values("_rank")
    out = m.drop_duplicates(["BUSNUM", "ID", "SIDE"])
    out = pair.merge(out[["BUSNUM", "ID", "SIDE", "NAME"]], on=["BUSNUM", "ID", "SIDE"], how="left")
    # SCED unit names carry a trailing unit index (JACKCNTY_CC1_1); the DAM
    # disclosure keys on the settlement point (JACKCNTY_CC1)
    out["SCED"] = out["NAME"].str.replace(r"_\d+$", "", regex=True)
    return out


def dam_offers(sced: list[str], hours=(12, 18)) -> pd.DataFrame:
    """Median offer at 60%/90% of curve for the latest disclosed month."""
    names = ",".join(f"'{re.sub(chr(39), '', s)}'" for s in set(sced) if isinstance(s, str))
    if not names:
        return pd.DataFrame()
    cols = ",".join(f"CURVEMW{i},CURVEPRICE{i}" for i in range(1, 11))
    df = sf.query("AW", f"""
        SELECT SETTLEMENTPOINTNAME, {cols}
        FROM AW.DBO.ERCOT60DDAMGENRESOURCE
        WHERE DELIVERYDATE >= DATEADD(day, -14, (SELECT MAX(DELIVERYDATE) FROM AW.DBO.ERCOT60DDAMGENRESOURCE))
          AND HOURENDING IN ({','.join(map(str, hours))})
          AND SETTLEMENTPOINTNAME IN ({names})
        LIMIT 5000""")
    if df.empty:
        return df

    def at(row, frac):
        pts = [(row[f"CURVEMW{i}"], row[f"CURVEPRICE{i}"]) for i in range(1, 11)
               if pd.notna(row[f"CURVEMW{i}"]) and pd.notna(row[f"CURVEPRICE{i}"])]
        if not pts:
            return None
        mt = pts[0][0] + frac * (pts[-1][0] - pts[0][0])
        for m, p in pts:
            if m >= mt:
                return p
        return pts[-1][1]

    df["P60"] = df.apply(lambda r: at(r, 0.6), axis=1)
    df["P90"] = df.apply(lambda r: at(r, 0.9), axis=1)
    return df.groupby("SETTLEMENTPOINTNAME")[["P60", "P90"]].median()


def estimate(study_id: int, ctgviol: pd.DataFrame, gen: pd.DataFrame,
             bus_names: pd.DataFrame, genunit: pd.DataFrame, scedname: pd.DataFrame,
             constraint: str, offers_cache: dict | None = None) -> dict | None:
    """lambda range for one constraint; None when the chain has no coverage."""
    pair = redispatch_pair(ctgviol, gen, constraint)
    if pair is None or pair.empty or (pair["SIDE"] == "up").sum() == 0:
        return None
    pair = sced_names(pair, bus_names, genunit, scedname)
    sfs = bus_shift_factors(study_id, constraint, pair["BUSNUM"].tolist())
    sfs["SF"] = sfs["SF"].astype(float)
    pair = pair.merge(sfs, on="BUSNUM", how="left")
    # a unit is only this constraint's marginal pair if it actually moves the
    # constraint — filter by |SF|, then rank by redispatch effectiveness
    pair = pair[pair["SF"].abs().between(MIN_SF, MAX_SF)].copy()
    pair["EFF"] = (pair["DIFF_MW"] * pair["SF"]).abs()
    pair = pair.sort_values("EFF", ascending=False).groupby("SIDE").head(4)
    up = pair[(pair["SIDE"] == "up") & pair["SCED"].notna() & pair["SF"].notna()]
    down = pair[(pair["SIDE"] == "down") & pair["SCED"].notna() & pair["SF"].notna()]
    if up.empty or down.empty:
        return None
    offers = dam_offers(pd.concat([up, down])["SCED"].tolist())
    if offers.empty:
        return None
    cands = []
    for _, u in up.iterrows():
        for _, d in down.iterrows():
            dsf = float(d["SF"] - u["SF"])
            if dsf < 0.02 or u["SCED"] not in offers.index or d["SCED"] not in offers.index:
                continue
            lo = max(0.0, float(offers.loc[u["SCED"], "P60"] - offers.loc[d["SCED"], "P60"])) / dsf
            hi = max(0.0, float(offers.loc[u["SCED"], "P90"] - offers.loc[d["SCED"], "P60"])) / dsf
            cands.append({"lo": lo, "hi": hi, "dsf": dsf,
                          "pair": f"{d['SCED']}↓/{u['SCED']}↑"})
    if not cands:
        return None
    # lambda floor = cheapest pair (the LP's first move); ceiling = the most
    # expensive pair among the movers — where the price goes as pairs exhaust
    cands.sort(key=lambda c: c["lo"])
    deepest = max(cands, key=lambda c: c["hi"])
    return {"lam_lo": round(min(cands[0]["lo"], PRICE_CAP), 1),
            "lam_hi": round(min(deepest["hi"], PRICE_CAP), 1),
            "dsf": round(cands[0]["dsf"], 3),
            "pair": f"{cands[0]['pair']} → {deepest['pair']}"}


PAIR_MIN_SF = 0.1   # floor for the *pair* test only (higher than MIN_SF):
                     # the long tail of self-scheduled wind/solar cpnodes sits
                     # at |PSENS| ~0.03-0.09 on a flowgate — they technically
                     # move it but have no offer curve and can't be
                     # dispatched for relief (see offer_lambda.estimate /
                     # Defect 3: most movers below this band lack DAM offers).
                     # Genuine redispatchable plants (gas CTs/STs) cluster
                     # >=0.1 on the canary that must NOT tag (DWCSRAM5).
PAIR_MAX_SF = 0.5    # radial/near-1.0-family sibling units of the same
                     # bottled plant (e.g. LYSSY_RN at 0.6-0.73 on STHRSCH8)
                     # sit here and would otherwise supply a same-sign
                     # "relief" that isn't a real redispatch option.


def dispatch_screen(study_id: int, constraint: str) -> str | None:
    """'unenforceable' when no dispatchable redispatch PAIR exists for this
    constraint (no dispatchable relief — ERCOT is unlikely to run the driving
    outage); None otherwise.

    Relief needs a redispatch PAIR: one cpnode whose output can go up and
    another whose output can go down, i.e. cpnodes with PSENS of OPPOSITE
    sign. A same-sign-only cluster (all cpnodes push the flowgate the same
    way) has no redispatch move that relieves it — that's what an
    unenforceable/bottled constraint looks like (e.g. STHRSCH8, whose only
    real mover, LYSSY_RN, is a >=0.5 radial plant, plus a long tail of tiny
    self-scheduled renewables, none of it opposite-signed above the noise
    floor).

    Per SHIFT_FACTORS.DBO.CPNODE_SHIFTS_VIEW: DEADBUS=0, NAME not a
    load-zone/weather-zone aggregate (LZ_%/WZ_%), and
    PAIR_MIN_SF <= |PSENS| < PAIR_MAX_SF (excludes both the radial/near-1.0
    family and the sub-0.1 renewable noise floor). Tags unenforceable only
    when no cpnode with PSENS > 0 AND no cpnode with PSENS < 0 both exist in
    that band. One aggregate query per constraint, keyed on
    (ISOMARKETID=6, STUDYID, FROMNUM, TONUM, CKT, CTGLABEL).

    Validated against both canaries: 8186-8913-1@STHRSCH8 (must tag — only
    MILTON_RN clears the band, one-sided positive, no pair) and
    1436-2081-1@DWCSRAM5 (must NOT tag — WCPP_CT1/CT2/ST1 etc. clear positive
    and CHISMGRD_RN/MDWPK_RN etc. clear negative, a genuine pair).

    DEVICE_SHIFTS (the prior source) has zero rows for recent studies
    (e.g. 14411) — CPNODE_SHIFTS_VIEW is the live source, confirmed readable.
    """
    f, t, rest = constraint.split("-", 2)
    ckt, ctg = rest.split("@")
    df = sf.query("SHIFT_FACTORS", f"""
        SELECT
          SUM(CASE WHEN PSENS > 0 THEN 1 ELSE 0 END) AS N_POS,
          SUM(CASE WHEN PSENS < 0 THEN 1 ELSE 0 END) AS N_NEG
        FROM SHIFT_FACTORS.DBO.CPNODE_SHIFTS_VIEW
        WHERE ISOMARKETID = 6 AND STUDYID = {int(study_id)}
          AND FROMNUM = {int(f)} AND TONUM = {int(t)}
          AND CKT = '{ckt}' AND CTGLABEL = '{ctg}'
          AND DEADBUS = 0
          AND LEFT(NAME, 3) NOT IN ('LZ_', 'WZ_')
          AND ABS(PSENS) >= {PAIR_MIN_SF} AND ABS(PSENS) < {PAIR_MAX_SF}
    """)
    if df is None or df.empty:
        return None
    n_pos = int(df["N_POS"].iloc[0] or 0)
    n_neg = int(df["N_NEG"].iloc[0] or 0)
    if n_pos == 0 or n_neg == 0:
        return "unenforceable — no dispatchable relief pair (LZ/WZ/radial/renewable-noise only); ERCOT unlikely to run it"
    return None
