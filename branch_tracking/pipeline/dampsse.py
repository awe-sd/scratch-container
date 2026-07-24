"""DAM PSSE mapping tiers + inService status computation.

Pure functions extracted verbatim from:
  - scripts/build_dampsse_default_status.py (exact-name tier, inService
    status computation)
  - scripts/map_unmapped_dampsse_teids.py (fallback tiers, consensus-status
    tier for still-ambiguous teids)

See those scripts' module docstrings for the full rationale (linkage
problem, tier ordering, why a consensus tier exists). No logic here should
diverge from the original scripts -- the golden-hash test
(tests/test_goldens.py) is the proof of behavioral equivalence.
"""
from .naming import normalize_name, names_relate, pick_by_leg
from .config import FILETYPE_FOR_DEVICE

import pandas as pd


def compute_inservice_status(agg: pd.DataFrame) -> pd.DataFrame:
    """Adds pct_inservice (round 4) and dampsse_default_status ("Closed"
    iff pct_inservice >= 0.5). From build_dampsse_default_status.py:main."""
    agg = agg.copy()
    agg["pct_inservice"] = (agg["n_inservice"] / agg["n_hours"]).round(4)
    agg["dampsse_default_status"] = agg["pct_inservice"].apply(
        lambda p: "Closed" if p >= 0.5 else "Open"
    )
    return agg


def map_exact_names(ours: pd.DataFrame, dampsse_def: pd.DataFrame, active_ids: set) -> pd.DataFrame:
    """Exact normalized-name match tier, one row per (teid, ercotDampsseId).
    Skips names mapping to >1 teid. From
    build_dampsse_default_status.py:main."""
    ours = ours.copy()
    ours["opeq_norm"] = ours["OP_EQCODE"].apply(normalize_name)

    dampsse_def = dampsse_def.copy()
    dampsse_def["name_norm"] = dampsse_def["branchNameRaw"].apply(normalize_name)

    ours_by_name = ours.dropna(subset=["opeq_norm"]).groupby("opeq_norm")
    name_to_teids = ours_by_name["teid"].apply(list)

    rows = []
    for name, group in dampsse_def.dropna(subset=["name_norm"]).groupby("name_norm"):
        teids = name_to_teids.get(name)
        if teids is None:
            continue
        if len(set(teids)) > 1:
            continue
        teid = teids[0]
        cands = group
        if len(cands) > 1:
            in_window = cands[cands["ercotDampsseId"].isin(active_ids)]
            cands = in_window if len(in_window) else cands.tail(1)
        for _, c in cands.iterrows():
            rows.append({
                "teid": teid,
                "ercotDampsseId": c["ercotDampsseId"],
                "dampsse_name_raw": c["branchNameRaw"],
                "dampsse_from_station": c["from_station"],
                "dampsse_to_station": c["to_station"],
                "dampsse_filetype": c["ercotDampsseFileTypeId"],
            })
    mapping = pd.DataFrame(rows).drop_duplicates(subset=["teid", "ercotDampsseId"])
    return mapping


def prepare_unmapped(ours: pd.DataFrame) -> pd.DataFrame:
    """Adds opeq_norm/sub1_norm/sub2_norm/ckt_norm normalization columns.
    From map_unmapped_dampsse_teids.py:main."""
    unmapped = ours.copy()
    unmapped["opeq_norm"] = unmapped["OP_EQCODE"].apply(normalize_name)
    unmapped["sub1_norm"] = unmapped["Substation1"].apply(normalize_name)
    unmapped["sub2_norm"] = unmapped["Substation2"].apply(normalize_name)
    unmapped["ckt_norm"] = unmapped["CircuitIdentifier"].apply(
        lambda v: (str(v).strip().lstrip("0") or "0") if pd.notna(v) else None
    )
    return unmapped


def prepare_pool(dampsse_def: pd.DataFrame, stations: pd.DataFrame, claimed_ids: set) -> pd.DataFrame:
    """Adds name_norm + from/to_station_norm; excludes rows whose
    ercotDampsseId is in claimed_ids. From
    map_unmapped_dampsse_teids.py:main."""
    dampsse_def = dampsse_def.copy()
    stations = stations.set_index("ercotDampsseStationId")
    dampsse_def["name_norm"] = dampsse_def["branchNameRaw"].apply(normalize_name)
    dampsse_def["from_station_norm"] = dampsse_def["fromStationId"].map(stations["stationName"]).apply(normalize_name)
    dampsse_def["to_station_norm"] = dampsse_def["toStationId"].map(stations["stationName"]).apply(normalize_name)
    pool = dampsse_def[~dampsse_def["ercotDampsseId"].isin(claimed_ids)].copy()
    return pool


def map_fallback_tiers(unmapped: pd.DataFrame, pool: pd.DataFrame, agg: pd.DataFrame, ckt_by_id: dict) -> tuple:
    """Verbatim fallback-tier loop from map_unmapped_dampsse_teids.py:main.
    Returns (mappings with `tier` column, diagnosis with `bucket` column)."""
    active_ids = set(agg["ercotDampsseId"])

    def accept(teid, row, c, tier):
        mappings.append({
            "teid": teid, "ercotDampsseId": c["ercotDampsseId"],
            "tier": tier,
            "our_op_eqcode": row["OP_EQCODE"], "dampsse_name_raw": c["branchNameRaw"],
            "dampsse_active_in_window": c["ercotDampsseId"] in active_ids,
        })

    mappings, diagnosis = [], []
    for _, row in unmapped.iterrows():
        teid, opeq = row["teid"], row["opeq_norm"]
        s1, s2 = row["sub1_norm"], row["sub2_norm"]
        # Only consider DAM defs of the matching kind (Line vs Transformer)
        ftype = FILETYPE_FOR_DEVICE.get(row["DeviceType"])
        my_pool = pool[pool["ercotDampsseFileTypeId"] == ftype] if ftype else pool
        my_pool_names = my_pool.dropna(subset=["name_norm"])

        def station_filter(df):
            if not (s1 and s2):
                return df.iloc[0:0]
            return df[
                ((df["from_station_norm"] == s1) & (df["to_station_norm"] == s2))
                | ((df["from_station_norm"] == s2) & (df["to_station_norm"] == s1))
            ]

        # Tier 2: substring containment on names
        if opeq:
            cand = my_pool_names[my_pool_names["name_norm"].apply(lambda n: names_relate(opeq, n))]
            if len(cand) == 1:
                accept(teid, row, cand.iloc[0], "substring_name")
                continue
            if len(cand) > 1:
                # Tier 2b: disambiguate name candidates by station pair
                # (e.g. two distinct elements both normalizing to LINE11)
                by_station = station_filter(cand)
                if len(by_station) == 1:
                    accept(teid, row, by_station.iloc[0], "substring_name_station")
                    continue
                # Tier 2c: transformer leg-aware pick among name candidates
                picked = pick_by_leg(opeq, by_station if len(by_station) else cand)
                if picked is not None:
                    accept(teid, row, picked, "substring_name_leg")
                    continue
                diagnosis.append({
                    "teid": teid, "bucket": "name_similar_but_ambiguous",
                    "our_op_eqcode": row["OP_EQCODE"],
                    "n_candidates": len(cand),
                    "candidate_names": ", ".join(cand["branchNameRaw"].head(5)),
                })
                continue

        # Tier 3: station pair (fileType-filtered), unique or leg-resolvable
        # or circuit-id-resolvable
        pair_match = station_filter(my_pool)
        if len(pair_match) == 1:
            accept(teid, row, pair_match.iloc[0], "station_pair")
            continue
        if len(pair_match) > 1:
            picked = pick_by_leg(opeq, pair_match.dropna(subset=["name_norm"]))
            if picked is not None:
                accept(teid, row, picked, "station_pair_leg")
                continue
            # Circuit-id tier: parallel elements between the same stations
            # differ by psseCktId; match against our CIM CircuitIdentifier.
            our_ckt = row.get("ckt_norm")
            if our_ckt and ckt_by_id:
                ckt_hits = pair_match[
                    pair_match["ercotDampsseId"].apply(
                        lambda i: our_ckt in ckt_by_id.get(i, set())
                    )
                ]
                if len(ckt_hits) == 1:
                    accept(teid, row, ckt_hits.iloc[0], "station_pair_ckt")
                    continue
            diagnosis.append({
                "teid": teid, "bucket": "station_pair_ambiguous",
                "our_op_eqcode": row["OP_EQCODE"],
                "n_candidates": len(pair_match),
                "candidate_names": ", ".join(pair_match["branchNameRaw"].astype(str).head(5)),
            })
            continue

        diagnosis.append({
            "teid": teid, "bucket": "absent_from_dampsse",
            "our_op_eqcode": row["OP_EQCODE"], "n_candidates": 0, "candidate_names": "",
        })

    mp = pd.DataFrame(mappings)
    dg = pd.DataFrame(diagnosis)
    # Attach context for review
    ctx = unmapped[["teid", "DeviceType", "FromName", "ToName", "Substation1", "Substation2", "Name"]]
    if len(mp):
        mp = mp.merge(ctx, on="teid", how="left")
    if len(dg):
        dg = dg.merge(ctx, on="teid", how="left")
    return mp, dg


def consensus_status(diagnosis: pd.DataFrame, unmapped: pd.DataFrame, pool: pd.DataFrame, agg: pd.DataFrame) -> pd.DataFrame:
    """Status inferred by candidate consensus, for the still-ambiguous
    teids -- when every candidate sharing the station pair (or name
    substring) has the same dominant status over the window, the status is
    known even though identity stays ambiguous. Verbatim from
    map_unmapped_dampsse_teids.py:main."""
    agg_idx = agg.set_index("ercotDampsseId")
    consensus_rows = []
    for d in diagnosis.to_dict("records"):
        if d["bucket"] not in ("station_pair_ambiguous", "name_similar_but_ambiguous"):
            continue
        teid = d["teid"]
        row = unmapped[unmapped["teid"] == teid].iloc[0]
        opeq = row["opeq_norm"]
        ftype = FILETYPE_FOR_DEVICE.get(row["DeviceType"])
        my_pool = pool[pool["ercotDampsseFileTypeId"] == ftype] if ftype else pool
        s1, s2 = row["sub1_norm"], row["sub2_norm"]
        if d["bucket"] == "station_pair_ambiguous" and s1 and s2:
            cand = my_pool[
                ((my_pool["from_station_norm"] == s1) & (my_pool["to_station_norm"] == s2))
                | ((my_pool["from_station_norm"] == s2) & (my_pool["to_station_norm"] == s1))
            ]
        else:
            cand = my_pool.dropna(subset=["name_norm"])
            cand = cand[cand["name_norm"].apply(lambda n: names_relate(opeq, n))]
        cand_agg = agg_idx.reindex(cand["ercotDampsseId"]).dropna()
        if not len(cand_agg):
            continue
        pcts = cand_agg["n_inservice"] / cand_agg["n_hours"]
        statuses = {("Closed" if p >= 0.5 else "Open") for p in pcts}
        if len(statuses) == 1:
            consensus_rows.append({
                "teid": teid, "ercotDampsseId": pd.NA,
                "n_hours": int(cand_agg["n_hours"].sum()),
                "n_inservice": int(cand_agg["n_inservice"].sum()),
                "pct_inservice": round(float(cand_agg["n_inservice"].sum() / cand_agg["n_hours"].sum()), 4),
                "dampsse_default_status": statuses.pop(),
                "tier": "candidates_consensus",
                "dampsse_name_raw": d["candidate_names"],
                "n_consensus_candidates": len(cand_agg),
            })
    return pd.DataFrame(consensus_rows)
