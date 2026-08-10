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


def sced_names(pair: pd.DataFrame, bus_names: pd.DataFrame, genunit: pd.DataFrame) -> pd.DataFrame:
    """Map (BUSNUM) -> bus name -> GENUNIT -> SCED resource name."""
    gu = genunit.copy()
    gu["SCED"] = gu["NOTES"].str.extract(r"naturalKey=SCED:(\S+)")
    m = pair.merge(bus_names, on="BUSNUM", how="left").merge(
        gu[["BUSNAME", "SCED"]].dropna().drop_duplicates("BUSNAME"), on="BUSNAME", how="left")
    # SCED unit names carry a trailing unit index (JACKCNTY_CC1_1); the DAM
    # disclosure keys on the settlement point (JACKCNTY_CC1)
    m["SCED"] = m["SCED"].str.replace(r"_\d+$", "", regex=True)
    return m


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
             bus_names: pd.DataFrame, genunit: pd.DataFrame, constraint: str,
             offers_cache: dict | None = None) -> dict | None:
    """lambda range for one constraint; None when the chain has no coverage."""
    pair = redispatch_pair(ctgviol, gen, constraint)
    if pair is None or pair.empty or (pair["SIDE"] == "up").sum() == 0:
        return None
    pair = sced_names(pair, bus_names, genunit)
    sfs = bus_shift_factors(study_id, constraint, pair["BUSNUM"].tolist())
    sfs["SF"] = sfs["SF"].astype(float)
    pair = pair.merge(sfs, on="BUSNUM", how="left")
    # a unit is only this constraint's marginal pair if it actually moves the
    # constraint — filter by |SF|, then rank by redispatch effectiveness
    pair = pair[pair["SF"].abs() >= MIN_SF].copy()
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
