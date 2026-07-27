"""How often do the SINK-side thermal units behind 35055 run? (summer 2025)

Sink side = VENSW end = thermal ResourceTypes with signed shift <= -0.05 on the
current vector (psenShiftID 87025608). Pull summer-2025 SCED and aggregate to the
PHYSICAL unit via cpNodeId (authoritative; collapses CC configuration-registrations
that share one cpnode). Read-only; caches to analytics/data/thm_*.parquet.
"""
from pathlib import Path
import re
import awconnect
import numpy as np
import pandas as pd
from awconnect import db, snowflake

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "output"
POST_PID = 87025608
THERMAL = {"CCGT90", "CCLE90", "CLLIG", "SCGT90", "SCLE90", "GSNONR", "GSREH", "GSSUP", "DSL"}
SUMMER_LO, SUMMER_HI = "2025-06-01", "2025-10-01"
PRICE_COLS = [f"CurvePrice{i}" for i in range(1, 16)]
MW_COLS = [f"CurveMW{i}" for i in range(1, 16)]


def offer_at_dispatch(row):
    tr = [(row[f"CurvePrice{i}"], row[f"CurveMW{i}"]) for i in range(1, 16)]
    tr = [(p, m) for p, m in tr if pd.notna(p) and pd.notna(m)]
    if not tr:
        return np.nan
    tr.sort(key=lambda x: x[1])
    for p, m in tr:
        if m >= row["BasePoint"] - 1e-6:
            return p
    return tr[-1][0]


def sink_set():
    post = pd.read_parquet(DATA / f"thm_shiftvec_{POST_PID}.parquet")
    g = post[post["ResourceName"].notna()].sort_values("shift").drop_duplicates("ResourceName")
    s = g[(g["shift"] <= -0.05) & (g["ResourceType"].isin(THERMAL))].copy()
    s["station"] = s["ResourceName"].str.split("_").str[0]
    return s[["ResourceName", "ResourceType", "shift", "cpNodeId", "cpnode_name", "station"]]


def fetch_sink_sced(names):
    f = DATA / "thm_sced_sink_summer2025.parquet"
    if f.exists():
        return pd.read_parquet(f)
    inlist = ",".join(f"'{n}'" for n in names)
    curves = ", ".join(f"T1.{c}" for c in (PRICE_COLS + MW_COLS))
    sql = f"""
        SELECT T1.TimeStamp, T2.ResourceName, T2.ResourceType, T1.TelemeteredStatus,
               T1.BasePoint, T1.HSL, T1.LSL, {curves}
        FROM AW.dbo.isoErcotScedGenResource T1
        JOIN AW.dbo.isoErcotScedGen T2 ON T1.genID = T2.genID
        WHERE T1.TimeStamp >= '{SUMMER_LO}' AND T1.TimeStamp < '{SUMMER_HI}'
          AND T2.ResourceName IN ({inlist})
    """
    df = db.getDfFromAwDb(sql)
    df.to_parquet(f, index=False)
    print(f"[sced] {len(df):,} rows, {df['ResourceName'].nunique()} resources, "
          f"{df['TimeStamp'].nunique()} intervals")
    return df


def genunit_meta(cpids):
    f = DATA / "thm_genunit_sink.parquet"
    if f.exists():
        return pd.read_parquet(f)
    inlist = ",".join(str(int(c)) for c in sorted(set(cpids)))
    gu = snowflake.performQuery(dbName="AW", warehouse=snowflake.READ_ONLY_WH,
        sqlQuery=f"""SELECT CPNODEID, UNITNAME, BUSNAME, GENFUELTYPE, NAMEPLATEMW
                     FROM AW.DBO.GENUNIT WHERE ISOMARKETID=6 AND CPNODEID IN ({inlist})""")
    gu.to_parquet(f, index=False)
    return gu


def main():
    awconnect.configure("read_only")
    pd.set_option("display.width", 220); pd.set_option("display.max_columns", None)
    sset = sink_set()
    name2cp = dict(zip(sset["ResourceName"], sset["cpNodeId"]))
    name2stn = dict(zip(sset["ResourceName"], sset["station"]))
    cp2shift = sset.groupby("cpNodeId")["shift"].min()  # strongest (most negative)

    sced = fetch_sink_sced(sset["ResourceName"].tolist())
    sced["TimeStamp"] = pd.to_datetime(sced["TimeStamp"])
    for c in ["BasePoint", "HSL", "LSL"]:
        sced[c] = pd.to_numeric(sced[c], errors="coerce")
    sced["cpNodeId"] = sced["ResourceName"].map(name2cp)
    sced["station"] = sced["ResourceName"].map(name2stn)
    sced["online"] = sced["TelemeteredStatus"].str.startswith("ON", na=False)
    sced["out_mw"] = np.where(sced["online"], sced["BasePoint"], 0.0)
    sced["offer_on"] = [offer_at_dispatch(r) if o else np.nan
                        for o, (_, r) in zip(sced["online"], sced.iterrows())]

    # physical unit = cpNodeId; one row per (cpNodeId, TimeStamp)
    pi = (sced.groupby(["cpNodeId", "station", "TimeStamp"])
          .agg(online=("online", "max"), output=("out_mw", "max"),
               hsl=("HSL", "max"), offer=("offer_on", "max"),
               rtype=("ResourceType", "first")).reset_index())
    pi["online"] = pi["online"].astype(bool)

    gu = genunit_meta(sced["cpNodeId"].dropna().unique())
    gu = gu.sort_values("NAMEPLATEMW", ascending=False).drop_duplicates("CPNODEID")
    gu = gu.rename(columns={"CPNODEID": "cpNodeId"})

    recs = []
    for cp, g in pi.groupby("cpNodeId"):
        on = g[g["online"]]
        recs.append({"cpNodeId": cp, "station": g["station"].iloc[0],
                     "ResourceType": g["rtype"].iloc[0],
                     "shift": float(cp2shift.get(cp, np.nan)),
                     "capacity_maxHSL": g["hsl"].max(),
                     "pct_online": 100.0 * g["online"].mean(),
                     "avg_output_MW_online": on["output"].mean() if len(on) else np.nan,
                     "median_offer_at_dispatch": on["offer"].median() if len(on) else np.nan})
    res = pd.DataFrame(recs).merge(gu[["cpNodeId", "UNITNAME", "NAMEPLATEMW"]],
                                   on="cpNodeId", how="left")
    res = res.sort_values("pct_online", ascending=False)
    cols = ["station", "UNITNAME", "ResourceType", "shift", "capacity_maxHSL",
            "pct_online", "avg_output_MW_online", "median_offer_at_dispatch", "NAMEPLATEMW"]
    res = res[cols]
    res.to_csv(OUT / "thermal_sink_35055_summer2025.csv", index=False)
    print(f"\n{len(res)} physical sink units (by cpNodeId):")
    print(res.round(2).to_string(index=False))

    # buckets: how often they run
    b = pd.cut(res["pct_online"], [-0.1, 5, 25, 60, 90, 100.1],
               labels=["~never (<5%)", "peaker (5-25%)", "intermittent (25-60%)",
                       "most-of-time (60-90%)", "near-baseload (>90%)"])
    print("\nrun-frequency distribution (physical units):")
    print(res.groupby(b, observed=False)["station"].count().to_string())
    print(f"\n-> {OUT/'thermal_sink_35055_summer2025.csv'}")


if __name__ == "__main__":
    main()
