"""Detect DAM PSSE stations that are topologically SPLIT, and classify how
consistently they are split across snapshots ("normally split" reference set).

Motivation
----------
Many stations in the DAM PSSE model are represented as two (or more)
electrically separate buses. When a station is split, a Closed line landing on
the unloaded side carries no flow, so Closed/inService status there is
misleading for parallel-circuit / cut-in reasoning (this caused the KINGFISHER
and PLATEAUT false positives in the cut-in conflict analysis). This script
builds the reference set the cut-in topology check must consult: stations that
are split in most snapshots ("normally split") vs. transiently split.

Detection (all bus-number comparison strictly WITHIN one snapshot)
------------------------------------------------------------------
DAM PSSE bus numbers are RANDOM per snapshot -- they vary even hour to hour
within a day (verified: 11,411 of 11,451 branches on awDateID 46240 change
psseFrom/ToBusNumber across HE) and have no relationship to CIM/tracking-table
bus numbers. So a "snapshot" here is one (awDateID, HE) pair; we sample HE=12
once per day. Only station identity (name+kV) and derived per-snapshot
booleans are compared across snapshots.

For each snapshot and each station (ercotDampsseStationId = stationName +
stationKv, the stable name-level identity; DAM PSSE has no separate per-bus
name table -- ercotDampsseRawView would have provided raw per-row station
names but is broken, referencing a dropped dbo.ercotDampsseRaw), collect the
PSSE bus numbers touched by IN-SERVICE branches (inService = 1, fileType 1
lines + 2 transformers) at that station. If the in-service endpoints land on
>1 distinct bus number for the same station, the station is split in that
snapshot.

Endpoint mapping honours ercotDampsseTimeseries.fromToFlipped: when set, the
row's psseFromBusNumber belongs to ercotDampsseDef.toStationId and vice versa.
(Verified empirically on awDateID 46240 HE 12: honouring the flip yields 1,353
multi-bus stations vs 4,844 when ignored -- ignoring it manufactures phantom
splits.)

Aggregation across snapshots
----------------------------
Window: daily HE=12 snapshots from WINDOW_START_DATE (2026-06-01, user choice:
this summer only) through the current max awDateID. Per station: n_snapshots_present (station had >=1 in-service
endpoint), n_snapshots_split, pct_split. Classification thresholds (tunable):
  normally_split              pct_split >= 0.90 and in-service-present on
                              >= 270 of the last 365 daily snapshots
  normally_split_new_station  pct_split >= 0.90 but in-service-present < 270
                              of the last 365 days -- commissioning cut-in
                              hubs whose line corridors are staged on separate
                              buses mimic splits (PLATE/KNGFSHER pattern);
                              NOT part of the normally-split reference set
  sometimes_split             0.10 <= pct_split < 0.90
  rarely_split                0 < pct_split < 0.10
Stations never split in the window are excluded from the outputs (counted in
the summary only).

Read-only: reads SQL Server AW.dbo via baseline's read profile; writes ONLY
  branch_tracking/output/normally_split_stations.csv
  branch_tracking/output/normally_split_stations.html

Run:  cd /home/node/baseline && uv run python \
        /workspaces/scratch-workspace/branch_tracking/scripts/adhoc/detect_split_stations.py
"""
from __future__ import annotations

import html as html_mod
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "/home/node/baseline")
from baseline import profiles  # noqa: E402
from baseline.pipeline.config import awdateid_for_date, date_for_awdateid  # noqa: E402

OUT_DIR = Path(__file__).resolve().parents[2] / "output"
CSV_PATH = OUT_DIR / "normally_split_stations.csv"
HTML_PATH = OUT_DIR / "normally_split_stations.html"

WINDOW_START_DATE = "2026-06-01"  # user choice: this summer only (Jun 2026 .. now)
SNAPSHOT_HE = 12           # one snapshot per day: hour-ending 12
THRESH_NORMAL = 0.90
THRESH_SOMETIMES = 0.10

# Ground-truth stations (per user):
#   JKSES / REYST           -- endpoints of teid 4850 line 7090__A; the ONLY
#                              confirmed positive: one of them should be split.
#   PLATEAUT (DAM 'PLATE') and KINGFISHER ('KNGFSHER') -- both NEW,
#                              not-yet-energized stations; NEGATIVE controls.
#                              Neither may land in the normally_split
#                              reference class. (Investigated: during
#                              commissioning a new cut-in hub appears with its
#                              two line corridors staged on separate buses --
#                              e.g. PLATE carries 6450_C/D on one bus and
#                              6460_I/J on another -- which mimics a split.
#                              Distinguisher: the station only recently
#                              appeared in the model at all, hence the
#                              station-age guard below.)
VALIDATION_STATIONS = {
    "JKSES": ("JKSES (teid 4850 / 7090__A)", "one of JKSES/REYST expect SPLIT"),
    "REYST": ("REYST (teid 4850 / 7090__A)", "one of JKSES/REYST expect SPLIT"),
    "PLATE": ("PLATEAUT", "negative control (new station) - must NOT be normally_split"),
    "KNGFSHER": ("KINGFISHER", "negative control (new station) - must NOT be normally_split"),
}

# New-station guard: a would-be normally_split station must ALSO have been
# present with in-service branches for at least MIN_HISTORY_DAYS of the last
# HISTORY_LOOKBACK_DAYS daily snapshots; otherwise it is reclassified to
# normally_split_new_station and kept OUT of the reference set. (Station age
# by first model appearance does NOT work: PLATE's branches published with
# inService=0 for a year before commissioning. In-service presence does:
# over the last 365 days JKSES/REYST are present 365/365, PLATE 61, KNGFSHER 41.)
HISTORY_LOOKBACK_DAYS = 365
MIN_HISTORY_DAYS = 270

# Endpoint CTE: one row per (snapshot, station, busNumber) endpoint of an
# in-service branch, honouring fromToFlipped. {where_extra} narrows the window.
EP_CTE = """
WITH ep AS (
  SELECT t.awDateID,
         CASE WHEN t.fromToFlipped = 1 THEN d.toStationId ELSE d.fromStationId END AS stationId,
         t.psseFromBusNumber AS busNum
  FROM AW.dbo.ercotDampsseTimeseries t
  JOIN AW.dbo.ercotDampsseDef d ON d.ercotDampsseId = t.ercotDampsseId
  WHERE t.ercotDampsseFileTypeId IN (1, 2)
    AND t.HE = {he} AND t.inService = 1 {where_extra}
  UNION ALL
  SELECT t.awDateID,
         CASE WHEN t.fromToFlipped = 1 THEN d.fromStationId ELSE d.toStationId END,
         t.psseToBusNumber
  FROM AW.dbo.ercotDampsseTimeseries t
  JOIN AW.dbo.ercotDampsseDef d ON d.ercotDampsseId = t.ercotDampsseId
  WHERE t.ercotDampsseFileTypeId IN (1, 2)
    AND t.HE = {he} AND t.inService = 1 {where_extra}
)
"""


def classify(pct: float) -> str:
    if pct >= THRESH_NORMAL:
        return "normally_split"
    if pct >= THRESH_SOMETIMES:
        return "sometimes_split"
    if pct > 0:
        return "rarely_split"
    return "never_split"


def main() -> None:
    profiles.configure("read", "detect_split_stations")
    from awconnect import db  # import after configure

    max_id = int(db.getDfFromAwDb(
        "SELECT MAX(awDateID) AS m FROM AW.dbo.ercotDampsseTimeseries"
    )["m"].iloc[0])
    import datetime
    cutoff = awdateid_for_date(datetime.date.fromisoformat(WINDOW_START_DATE)) - 1
    print(f"window: awDateID ({cutoff}, {max_id}] = "
          f"{date_for_awdateid(cutoff + 1)}..{date_for_awdateid(max_id)}, HE={SNAPSHOT_HE}")

    # --- per-station split aggregate over the window (one query, SQL-side) ---
    cte = EP_CTE.format(he=SNAPSHOT_HE, where_extra=f"AND t.awDateID > {cutoff}")
    agg = db.getDfFromAwDb(cte + """
    , per AS (
        SELECT awDateID, stationId, COUNT(DISTINCT busNum) AS n_buses
        FROM ep GROUP BY awDateID, stationId
    )
    SELECT stationId,
           COUNT(*)                                          AS n_snapshots_present,
           SUM(CASE WHEN n_buses > 1 THEN 1 ELSE 0 END)      AS n_snapshots_split,
           MAX(n_buses)                                      AS max_buses,
           MAX(CASE WHEN n_buses > 1 THEN awDateID END)      AS last_split_awdateid
    FROM per GROUP BY stationId
    """)
    print(f"stations present in window: {len(agg)}")

    stations = db.getDfFromAwDb(
        "SELECT ercotDampsseStationId AS stationId, stationName, stationKv "
        "FROM AW.dbo.ercotDampsseStation"
    )
    agg = agg.merge(stations, on="stationId", how="left")
    agg["pct_split"] = agg["n_snapshots_split"] / agg["n_snapshots_present"]
    agg["classification"] = agg["pct_split"].map(classify)

    # --- new-station guard: commissioning cut-in hubs mimic splits ----------
    # A brand-new hub appears in DAM with its line corridors staged on
    # separate buses before the tie is closed (verified on PLATE: 6450_C/D on
    # one bus, 6460_I/J on another for ~2 months). Guard: in-service presence
    # history over a 1-year lookback -- same endpoint logic, one aggregate.
    hist_cte = EP_CTE.format(
        he=SNAPSHOT_HE,
        where_extra=f"AND t.awDateID > {max_id - HISTORY_LOOKBACK_DAYS}")
    hist = db.getDfFromAwDb(hist_cte + """
    , per AS (
        SELECT awDateID, stationId, COUNT(DISTINCT busNum) AS n_buses
        FROM ep GROUP BY awDateID, stationId
    )
    SELECT stationId,
           COUNT(*)                                     AS hist_days_present,
           SUM(CASE WHEN n_buses > 1 THEN 1 ELSE 0 END) AS hist_days_split,
           MIN(awDateID)                                AS first_inservice_awdateid
    FROM per GROUP BY stationId
    """)
    agg = agg.merge(hist, on="stationId", how="left")
    agg["hist_pct_split"] = agg["hist_days_split"] / agg["hist_days_present"]
    is_new = agg["hist_days_present"].fillna(0) < MIN_HISTORY_DAYS
    agg.loc[is_new & (agg["classification"] == "normally_split"),
            "classification"] = "normally_split_new_station"
    agg["first_inservice_date"] = agg["first_inservice_awdateid"].map(
        lambda i: date_for_awdateid(int(i)) if pd.notna(i) else None
    )

    # --- human-readable evidence from the single most recent snapshot ---
    split_ids = agg.loc[agg["n_snapshots_split"] > 0, "stationId"].tolist()
    cte1 = EP_CTE.format(he=SNAPSHOT_HE, where_extra=f"AND t.awDateID = {max_id}")
    ev = db.getDfFromAwDb(cte1.replace(
        "t.psseFromBusNumber AS busNum",
        "t.psseFromBusNumber AS busNum, d.branchName",
    ).replace(
        "t.psseToBusNumber\n", "t.psseToBusNumber, d.branchName\n",
    ) + f"""
    SELECT stationId, busNum, branchName FROM ep
    WHERE stationId IN ({','.join(map(str, split_ids)) or 'NULL'})
    """)
    # in-service load/gen bus numbers on the same evidence snapshot -- a bus
    # number absent from BOTH sets is an electrically "empty" split half
    # (candidate for the later implied-open phase).
    ld = db.getDfFromAwDb(f"""
        SELECT DISTINCT psseBusNumber FROM AW.dbo.ercotDampsseLdTimeseries
        WHERE awDateID = {max_id} AND HE = {SNAPSHOT_HE} AND inService = 1
    """)
    gn = db.getDfFromAwDb(f"""
        SELECT DISTINCT psseBusNumber FROM AW.dbo.ercotDampsseGnTimeseries
        WHERE awDateId = {max_id} AND HE = {SNAPSHOT_HE} AND inService = 1
    """)
    ld_buses = set(ld["psseBusNumber"].astype(int))
    gn_buses = set(gn["psseBusNumber"].astype(int))

    def bus_tag(b: int) -> str:
        tags = (["load"] if b in ld_buses else []) + (["gen"] if b in gn_buses else [])
        return "+".join(tags) if tags else "EMPTY"

    ev_txt = (
        ev.sort_values(["stationId", "busNum", "branchName"])
          .groupby(["stationId", "busNum"])["branchName"]
          .apply(lambda s: ",".join(sorted(set(s))))
          .reset_index()
          .assign(txt=lambda d: "bus " + d["busNum"].astype(str)
                  + " (" + d["busNum"].astype(int).map(bus_tag) + "): ["
                  + d["branchName"] + "]")
          .groupby("stationId")["txt"].apply(" | ".join)
          .rename("evidence_latest_snapshot")
    )

    out = agg[agg["n_snapshots_split"] > 0].merge(ev_txt, on="stationId", how="left")
    out["last_split_date"] = out["last_split_awdateid"].map(
        lambda i: date_for_awdateid(int(i)) if pd.notna(i) else None
    )
    out = out.sort_values(["pct_split", "n_snapshots_split"], ascending=False)
    cols = ["stationName", "stationKv", "n_snapshots_present", "n_snapshots_split",
            "pct_split", "max_buses", "classification", "hist_days_present",
            "hist_days_split", "hist_pct_split", "first_inservice_date",
            "last_split_date", "evidence_latest_snapshot"]
    out_csv = out[cols].rename(columns={"stationName": "bus_name"}).copy()
    out_csv["pct_split"] = out_csv["pct_split"].round(4)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv.to_csv(CSV_PATH, index=False)
    print(f"wrote {CSV_PATH} ({len(out_csv)} rows)")

    dist = agg["classification"].value_counts()
    print("classification distribution:\n", dist.to_string())

    # validation
    val_rows = agg[agg["stationName"].isin(VALIDATION_STATIONS)]
    print("validation stations:\n", val_rows[
        ["stationName", "stationKv", "n_snapshots_present", "n_snapshots_split",
         "pct_split", "classification"]].to_string(index=False))

    write_html(out, agg, dist, val_rows, cutoff, max_id)
    print(f"wrote {HTML_PATH}")


def write_html(out, agg, dist, val_rows, cutoff, max_id) -> None:
    e = html_mod.escape
    colors = {"normally_split": "#f87171",
              "normally_split_new_station": "#a78bfa",
              "sometimes_split": "#fbbf24", "rarely_split": "#4ade80"}
    blurbs = {
        "normally_split": "Split in ≥90% of snapshots where present AND in-service-present ≥270 of the last 365 days — the station's NORMAL state is two (or more) separate buses. Two Closed lines here are NOT evidence of a real parallel circuit; the cut-in check must consult this list.",
        "normally_split_new_station": "Would be normally_split by pct, but the station has had in-service branches on fewer than 270 of the last 365 days — almost certainly a NEW cut-in hub whose line corridors are staged on separate buses during commissioning (PLATE pattern: 6450_C/D on one bus, 6460_I/J on another). NOT part of the normally-split reference set; these are cut-in candidates, not split stations.",
        "sometimes_split": "Split in 10–90% of snapshots — extended reconfiguration, phased cut-in, or long outage. Treat with caution; check the last-split date.",
        "rarely_split": "Split in <10% of snapshots — almost certainly a transient outage/switching event, not a normal topology.",
    }
    n_never = int((agg["classification"] == "never_split").sum())

    parts = []
    parts.append(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Normally split DAM PSSE stations</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ background:#0f172a; color:#e2e8f0; margin:0; padding:2rem;
         font:14px/1.55 ui-sans-serif,system-ui,-apple-system,sans-serif; }}
  h1 {{ font-size:1.5rem; margin:0 0 .4rem; }}
  h2 {{ font-size:1.05rem; margin:0 0 .3rem; display:flex; align-items:center; gap:.5rem; }}
  .sub {{ color:#93a3b8; max-width:64rem; }}
  .sub code, .blurb code {{ background:#1e2a3d; padding:.1rem .3rem; border-radius:3px; color:#c7d2e0; }}
  section {{ margin:2rem 0; }}
  .blurb {{ color:#93a3b8; margin:.1rem 0 .7rem; max-width:64rem; }}
  .dot {{ width:.7rem; height:.7rem; border-radius:50%; display:inline-block; }}
  .n {{ color:#93a3b8; font-weight:400; }}
  ul.sum {{ list-style:none; padding:0; display:flex; flex-wrap:wrap; gap:1.2rem; }}
  ul.sum li {{ display:flex; align-items:center; gap:.4rem; }}
  .scroll {{ overflow-x:auto; border:1px solid #24314a; border-radius:6px; max-height:38rem; }}
  table {{ border-collapse:collapse; width:100%; font-size:12.5px; white-space:nowrap; }}
  th,td {{ padding:.4rem .55rem; text-align:left; border-bottom:1px solid #1e2a3d; }}
  th {{ background:#162134; color:#a9b6c9; font-weight:600; position:sticky; top:0; }}
  tr:hover td {{ background:#162134; }}
  td.ev {{ white-space:normal; min-width:26rem; color:#93a3b8; }}
  .good {{ color:#4ade80; }} .bad {{ color:#fbbf24; font-weight:600; }}
  .warn {{ background:#2a1f14; border:1px solid #6b4a1d; border-radius:6px;
           padding:.8rem 1rem; margin:1.2rem 0; max-width:64rem; }}
</style></head><body>
<h1>Normally split DAM PSSE stations</h1>
<p class="sub">A station is <b>split</b> in a snapshot when the in-service
branches landing at that station (same <code>stationName</code>+kV in
<code>AW.dbo.ercotDampsseStation</code>) touch <b>more than one distinct PSSE
bus number</b>. Bus numbers are random per snapshot (they change even hour to
hour), so all comparison is strictly within a single (awDateID, HE) snapshot;
we sample <b>HE={SNAPSHOT_HE}</b> once per day over this summer only (user choice):
awDateID {cutoff + 1}–{max_id}
({e(str(date_for_awdateid(cutoff + 1)))} … {e(str(date_for_awdateid(max_id)))}).
Endpoint→station mapping honours <code>fromToFlipped</code>
(ignoring it produces 4,844 phantom multi-bus stations vs 1,353 on the latest
snapshot). Source: <code>AW.dbo.ercotDampsseTimeseries</code> ⋈
<code>ercotDampsseDef</code>, fileTypes 1 (lines) + 2 (transformers),
<code>inService=1</code>. Read-only; nothing written to any database.</p>
<div class="warn"><b>Why this exists:</b> at a normally split station one side
may serve no load, so a Closed line into it carries no flow — two Closed lines
there are <b>not</b> a real parallel circuit. The cut-in / parallel-circuit
topology check must consult this reference set (KINGFISHER and PLATEAUT false
positives came from exactly this confusion).</div>
""")

    # validation box
    vparts = []
    for _, r in val_rows.iterrows():
        label, expect = VALIDATION_STATIONS.get(
            r["stationName"], (r["stationName"], ""))
        vparts.append(
            f"<b>{e(label)}</b> (DAM <code>{e(r['stationName'])}</code> "
            f"{int(r['stationKv'])} kV, {e(expect)}): split in "
            f"{int(r['n_snapshots_split'])} of "
            f"{int(r['n_snapshots_present'])} snapshots "
            f"({r['pct_split']:.1%}) → <b>{e(r['classification'])}</b>"
        )
    parts.append('<div class="warn"><b>Validation (known ground truth):</b><br>'
                 + "<br>".join(vparts) + "</div>")

    parts.append('<ul class="sum">')
    for cls in ("normally_split", "normally_split_new_station",
                "sometimes_split", "rarely_split"):
        parts.append(f'<li><span class="dot" style="background:{colors[cls]}"></span>'
                     f'<b>{int(dist.get(cls, 0))}</b> {cls}</li>')
    parts.append(f'<li><span class="dot" style="background:#475569"></span>'
                 f'<b>{n_never}</b> never_split (not listed)</li></ul>')

    hdr = ("<tr><th>station (bus name)</th><th>kV</th><th>snapshots present</th>"
           "<th>snapshots split</th><th>pct split</th><th>max buses</th>"
           "<th>1yr days present</th><th>1yr days split</th><th>first in-service (1yr lookback)</th>"
           "<th>last split</th><th>evidence — latest snapshot "
           f"(awDateID {max_id}): bus number (load/gen attached, or EMPTY) → in-service branches</th></tr>")
    for cls in ("normally_split", "normally_split_new_station",
                "sometimes_split", "rarely_split"):
        sub = out[out["classification"] == cls]
        parts.append(f'<section><h2><span class="dot" style="background:{colors[cls]}">'
                     f'</span>{cls} <span class="n">({len(sub)})</span></h2>'
                     f'<p class="blurb">{blurbs[cls]}</p>'
                     f'<div class="scroll"><table><thead>{hdr}</thead><tbody>')
        for _, r in sub.iterrows():
            ev = r["evidence_latest_snapshot"]
            parts.append(
                f"<tr><td><b>{e(str(r['stationName']))}</b></td>"
                f"<td>{int(r['stationKv'])}</td>"
                f"<td>{int(r['n_snapshots_present'])}</td>"
                f"<td>{int(r['n_snapshots_split'])}</td>"
                f"<td>{r['pct_split']:.1%}</td><td>{int(r['max_buses'])}</td>"
                f"<td>{int(r['hist_days_present']) if pd.notna(r['hist_days_present']) else ''}</td>"
                f"<td>{int(r['hist_days_split']) if pd.notna(r['hist_days_split']) else ''}</td>"
                f"<td>{e(str(r['first_inservice_date']))}</td>"
                f"<td>{e(str(r['last_split_date']))}</td>"
                f"<td class='ev'>{e(ev) if isinstance(ev, str) else ''}</td></tr>")
        parts.append("</tbody></table></div></section>")

    parts.append("""
<p class="sub" style="margin-top:2rem">Generated by
<code>branch_tracking/scripts/adhoc/detect_split_stations.py</code>.
Read-only analysis; nothing here was written to any database.</p>
</body></html>""")
    HTML_PATH.write_text("".join(parts))


if __name__ == "__main__":
    main()
