"""
Diagnose and (where confidently possible) map the ~880 teids that the
exact-name tier in build_dampsse_default_status.py could NOT link to an
ercotDampsseId, using ONLY the local cache in data/raw/ (no DB).

Fallback tiers, in confidence order:
  Tier 2 -- substring containment on normalized names (names_relate: one
    name contains the other), accepted only when the match is UNIQUE in
    both directions (one teid <-> one DAM name); station-pair and
    transformer-leg-aware disambiguation among name candidates.
  Tier 3 -- station-pair match: the CIM CSV gives each teid
    Substation1/Substation2; ercotDampsseDef gives fromStationId/
    toStationId -> ercotDampsseStation.stationName. Order-independent
    station-pair equality (normalized), fileType-filtered
    (Line<->1, Transformer<->2); unique, or resolved by the
    transformer-leg-aware picker, or (if data/raw/dampsse_ckt_snapshot.csv
    exists, built by cache_dampsse_ckt.py) by CIRCUIT-ID match: our CIM
    CircuitIdentifier vs the element's psseCktId -- parallel elements
    between the same stations differ by circuit id.
  (Tier 4, impedance r/x/b nearest-match, is NOT built here: our CIM
   TeidMap export carries no impedances, and BRANCH.b1/b2 are mostly
   blank -- would need PTOBRANCH-derived impedances. Deferred.)

Everything that still doesn't map gets a diagnosis bucket:
  - name_similar_but_ambiguous: substring candidates exist but aren't
    unique -- listed for manual review, not guessed.
  - station_pair_ambiguous: station-pair candidates exist but not unique.
  - absent_from_dampsse: nothing close by name OR station pair -- likely
    genuinely not modeled in the DA PSSE export (equivalenced out,
    below-model-threshold, or too new/old for the current Def dimension).

Outputs (both for review, not auto-applied to the pipeline yet):
  output/dampsse_fallback_mappings.csv -- tier-2/3 confident candidates
  output/dampsse_unmapped_diagnosis.csv -- everything else, bucketed
Read-only, local files only.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from branch_tracking.pipeline.naming import (  # noqa: E402
    normalize_name, names_relate, unit_and_leg, pick_by_leg,
)
from branch_tracking.pipeline.config import FILETYPE_FOR_DEVICE  # noqa: E402

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"
TEID_MAP_CSV = REPO_ROOT / "output" / "teid_branch_id_map.csv"
DAMPSSE_STATUS_CSV = REPO_ROOT / "output" / "dampsse_default_status.csv"
MAPPINGS_CSV = REPO_ROOT / "output" / "dampsse_fallback_mappings.csv"
DIAGNOSIS_CSV = REPO_ROOT / "output" / "dampsse_unmapped_diagnosis.csv"


def main():
    ours = pd.read_csv(TEID_MAP_CSV)
    ours = ours[ours["match_status"] != "unmatched"].copy()
    mapped = pd.read_csv(DAMPSSE_STATUS_CSV)
    mapped_teids = set(mapped["teid"])

    unmapped = ours[~ours["teid"].isin(mapped_teids)].copy()
    unmapped["opeq_norm"] = unmapped["OP_EQCODE"].apply(normalize_name)
    unmapped["sub1_norm"] = unmapped["Substation1"].apply(normalize_name)
    unmapped["sub2_norm"] = unmapped["Substation2"].apply(normalize_name)
    unmapped["ckt_norm"] = unmapped["CircuitIdentifier"].apply(
        lambda v: (str(v).strip().lstrip("0") or "0") if pd.notna(v) else None
    )
    print(f"Unmapped teids to diagnose: {unmapped['teid'].nunique()}")

    # Optional circuit-id cache (cache_dampsse_ckt.py): ercotDampsseId ->
    # set of psseCktId values seen in the recent window.
    ckt_path = RAW_DIR / "dampsse_ckt_snapshot.csv"
    ckt_by_id = {}
    if ckt_path.exists():
        ckt_df = pd.read_csv(ckt_path)
        ckt_by_id = (
            ckt_df.groupby("ercotDampsseId")["psseCktId"]
            .apply(lambda s: {str(v).strip().lstrip("0") or "0" for v in s.dropna().astype(str)})
            .to_dict()
        )
        print(f"Circuit-id cache loaded: {len(ckt_by_id)} elements")

    dampsse = pd.read_csv(RAW_DIR / "ercotDampsseDef.csv")
    stations = pd.read_csv(RAW_DIR / "ercotDampsseStation.csv").set_index("ercotDampsseStationId")
    agg = pd.read_csv(RAW_DIR / "dampsse_inservice_agg.csv")
    active_ids = set(agg["ercotDampsseId"])

    dampsse["name_norm"] = dampsse["branchNameRaw"].apply(normalize_name)
    dampsse["from_station_norm"] = dampsse["fromStationId"].map(stations["stationName"]).apply(normalize_name)
    dampsse["to_station_norm"] = dampsse["toStationId"].map(stations["stationName"]).apply(normalize_name)
    # Exclude DAM defs already claimed by the exact-name tier so fallbacks
    # can't steal an element that's already correctly mapped.
    claimed_ids = set(mapped["ercotDampsseId"].dropna().astype(int))
    pool = dampsse[~dampsse["ercotDampsseId"].isin(claimed_ids)].copy()
    print(f"DAM defs in fallback pool (unclaimed): {len(pool)}")

    pool_names = pool.dropna(subset=["name_norm"])[["ercotDampsseId", "name_norm", "branchNameRaw",
                                                     "from_station_norm", "to_station_norm"]]

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
    mp.to_csv(MAPPINGS_CSV, index=False)
    dg.to_csv(DIAGNOSIS_CSV, index=False)

    # Consensus-status tier for the still-ambiguous teids (per the user:
    # "there must be a way to infer the status for them"): we may not know
    # WHICH of the parallel candidates is ours, but when EVERY candidate
    # sharing the station pair has the same dominant status over the
    # window, the answer is the same regardless of which one it is. No
    # ercotDampsseId is assigned (identity stays ambiguous) -- only status.
    agg_idx = agg.set_index("ercotDampsseId")
    consensus_rows = []
    for d in diagnosis:
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
    consensus = pd.DataFrame(consensus_rows)
    print(f"\nStatus inferred by candidate consensus (identity still ambiguous): {len(consensus)}")
    if len(consensus):
        print(consensus["dampsse_default_status"].value_counts().to_string())

    # Status for the fallback-mapped teids, from the cached inService
    # aggregate -- same schema as dampsse_default_status.csv so the final
    # table can concatenate the two (no teid overlap by construction).
    if len(mp):
        fb = mp.merge(agg, on="ercotDampsseId", how="inner")
        fb["pct_inservice"] = (fb["n_inservice"] / fb["n_hours"]).round(4)
        fb["dampsse_default_status"] = fb["pct_inservice"].apply(
            lambda p: "Closed" if p >= 0.5 else "Open"
        )
        fb_out = fb[["teid", "ercotDampsseId", "n_hours", "n_inservice",
                     "pct_inservice", "dampsse_default_status", "tier",
                     "dampsse_name_raw"]]
        if len(consensus):
            fb_out = pd.concat(
                [fb_out, consensus[fb_out.columns.tolist()]], ignore_index=True
            )
        fb_out.to_csv(REPO_ROOT / "output" / "dampsse_default_status_fallback.csv", index=False)
        print(f"\nFallback teids with status computed from cache (incl. consensus): {len(fb_out)}")
        print(fb_out["dampsse_default_status"].value_counts().to_string())

    print(f"\nConfident fallback mappings: {len(mp)}")
    if len(mp):
        print(mp["tier"].value_counts().to_string())
        print(f"  of which active in current window: {mp['dampsse_active_in_window'].sum()}")
    print(f"\nStill unmapped (diagnosed): {len(dg)}")
    if len(dg):
        print(dg["bucket"].value_counts().to_string())
        print("\nDeviceType of the absent_from_dampsse bucket:")
        print(dg[dg["bucket"] == "absent_from_dampsse"]["DeviceType"].value_counts().to_string())
    print(f"\nWrote {MAPPINGS_CSV}")
    print(f"Wrote {DIAGNOSIS_CSV}")


if __name__ == "__main__":
    main()
