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


def redispatch_pair(ctgviol: pd.DataFrame, gen: pd.DataFrame, constraint: str,
                    binding_pct: float = 99.5) -> pd.DataFrame | None:
    """Top up/down movers (differential LPDELTAMW) with bus numbers."""
    cv = ctgviol.copy()
    cv["CONSTRAINT"] = constraint_key(cv)
    binding_runs = set(cv[(cv["CONSTRAINT"] == constraint)
                          & (cv["LIMVIOLPCT"] >= binding_pct)]["RUNID"])
    if not binding_runs:
        return None
    g = gen.copy()
    g["b"] = g["RUNID"].isin(binding_runs)
    piv = g.groupby(["BUSNUM", "ID", "b"])["LPDELTAMW"].mean().unstack()
    if True not in piv.columns:
        return None
    piv["DIFF_MW"] = piv.get(True, 0).fillna(0) - piv.get(False, 0).fillna(0)
    piv = piv.reset_index()
    up = piv.nlargest(N_PAIR, "DIFF_MW")
    down = piv.nsmallest(N_PAIR, "DIFF_MW")
    out = pd.concat([up.assign(SIDE="up"), down.assign(SIDE="down")])
    return out[abs(out["DIFF_MW"]) > 20]


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


def dispatchable_shifts(study_id: int, constraint: str) -> pd.DataFrame | None:
    """Raw qualifying (non-LZ/WZ, non-radial) shifts for a constraint, from
    SHIFT_FACTORS.DBO.DEVICE_SHIFTS. None when the table has no coverage at
    all for this branch/ctg (a data gap, not evidence of unenforceability);
    an empty (but non-None) frame when it has coverage and every device that
    showed up is excluded (load-zone/weather-zone aggregates or radial
    bottled gen) — that latter case is the actual "no dispatchable relief"
    signal `dispatch_screen` acts on.

    DEVICE_SHIFTS.STUDYID tops out at 13638 as of 2026-08-10 (our studies are
    14411/14412 and post-date it entirely — 0 rows if filtered by STUDYID),
    so this filters on the branch/ctg identity only (FROMNUM/TONUM/CKT/
    CTGLABEL), which is stable across studies/topologies for the same
    physical grid element and contingency label.
    """
    f, t, rest = constraint.split("-", 2)
    ckt, ctg = rest.split("@")
    df = sf.query("SHIFT_FACTORS", f"""
        SELECT DEVICE_TYPE, NAME, LABEL, BUSNUM, PSENS, ISRADIAL, STATUS
        FROM SHIFT_FACTORS.DBO.DEVICE_SHIFTS
        WHERE ISOMARKETID = 6 AND FROMNUM = {int(f)} AND TONUM = {int(t)}
          AND CKT = '{ckt}' AND CTGLABEL = '{ctg}'
    """)
    return df if len(df) else None


def dispatch_screen(study_id: int, constraint: str) -> str | None:
    """'unenforceable' when every qualifying shift on this constraint is a
    load-zone/weather-zone aggregate or radial bottled gen (no dispatchable
    relief exists — ERCOT is unlikely to run the driving outage); None when
    there is either no DEVICE_SHIFTS coverage or at least one dispatchable
    device.
    """
    shifts = dispatchable_shifts(study_id, constraint)
    if shifts is None:
        return None
    name = shifts["NAME"].fillna("").astype(str)
    is_zone = name.str.startswith("LZ_") | name.str.startswith("WZ_")
    is_radial_gen = (shifts["DEVICE_TYPE"] == "GEN") & (shifts["PSENS"].abs() >= MAX_SF)
    is_radial_flag = shifts["ISRADIAL"].fillna(0).astype(float) == 1
    dispatchable = shifts[~(is_zone | is_radial_gen | is_radial_flag)]
    if dispatchable.empty:
        return "unenforceable — no dispatchable relief (LZ/WZ/radial only); ERCOT unlikely to run it"
    return None
