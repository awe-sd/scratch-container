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
from branch_tracking.pipeline.dampsse import (  # noqa: E402
    compute_inservice_status, consensus_status, map_fallback_tiers,
    prepare_pool, prepare_unmapped,
)

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

    unmapped = prepare_unmapped(ours[~ours["teid"].isin(mapped_teids)].copy())
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
    stations = pd.read_csv(RAW_DIR / "ercotDampsseStation.csv")
    agg = pd.read_csv(RAW_DIR / "dampsse_inservice_agg.csv")

    # Exclude DAM defs already claimed by the exact-name tier so fallbacks
    # can't steal an element that's already correctly mapped.
    claimed_ids = set(mapped["ercotDampsseId"].dropna().astype(int))
    pool = prepare_pool(dampsse, stations, claimed_ids)
    print(f"DAM defs in fallback pool (unclaimed): {len(pool)}")

    mp, dg = map_fallback_tiers(unmapped, pool, agg, ckt_by_id)
    mp.to_csv(MAPPINGS_CSV, index=False)
    dg.to_csv(DIAGNOSIS_CSV, index=False)

    # Consensus-status tier for the still-ambiguous teids (per the user:
    # "there must be a way to infer the status for them"): we may not know
    # WHICH of the parallel candidates is ours, but when EVERY candidate
    # sharing the station pair has the same dominant status over the
    # window, the answer is the same regardless of which one it is. No
    # ercotDampsseId is assigned (identity stays ambiguous) -- only status.
    consensus = consensus_status(dg, unmapped, pool, agg)
    print(f"\nStatus inferred by candidate consensus (identity still ambiguous): {len(consensus)}")
    if len(consensus):
        print(consensus["dampsse_default_status"].value_counts().to_string())

    # Status for the fallback-mapped teids, from the cached inService
    # aggregate -- same schema as dampsse_default_status.csv so the final
    # table can concatenate the two (no teid overlap by construction).
    if len(mp):
        fb = compute_inservice_status(mp.merge(agg, on="ercotDampsseId", how="inner"))
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
