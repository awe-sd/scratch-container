"""
Investigate WHY our DAM PSSE `dampsse_default_status` disagrees with the
PowerWorld base-model-*outages* study export, using DAM PSSE as the
reference status (per the user: the better indicator).

Pure local-file analysis -- no DB. Reuses the label-parsing / teid-resolution
logic from compare_base_model_status.py so the join to our table is identical.

The two disagreement directions mean different things in the *outages* case:

  * base=Closed / dampsse=Open  -- the study energizes the element but we call
    it normally-open. These are the real anomalies, and this script classifies
    each one:
      - `recent_energization_undercount`: our own in_service_date (from an
        energization outage) is 2023+, i.e. the element came into service
        partway through DAM PSSE's fixed 730-day window. Its pre-energization
        inService=0 hours dilute pct_inservice below the flat 0.5 threshold,
        so build_dampsse_default_status.py mislabels a normally-closed device
        "Open". A derivation artifact, not a real normally-open device.
      - `dampsse_suspect_auction_disagrees`: not recently energized, but the
        auction source (implied_default_status) says Closed too -- so BOTH the
        study and the auction snapshots say Closed and only DAM PSSE says Open.
        DAM PSSE is the outlier; mapping/threshold suspect.
      - `residual_review`: neither of the above -- both our sources say Open yet
        the study energizes it, and we have no recent-energization explanation.
        The genuine manual-review set (expected to be tiny).

  * base=Open / dampsse=Closed -- the study shows it open but we call it
    normally-closed. In an *outages* snapshot this is consistent with the
    element simply being outaged in this particular case (a normally-closed
    line on a scheduled outage). Reported as a count with the study's MW Loss
    column for context; not classified further.

Output: output/dampsse_outages_status_anomalies.csv (the base=Closed/dampsse=Open
worklist, one row per teid, with the classification column + evidence fields).

Run: uv run branch_tracking/scripts/adhoc/investigate_dampsse_base_model_disagreements.py
"""
import importlib.util
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
CMP_PATH = REPO_ROOT / "branch_tracking/scripts/adhoc/compare_base_model_status.py"
BASE_OUTAGES_CSV = REPO_ROOT / "branch_tracking/data/base_model_outages.csv"
OUTPUT_CSV = REPO_ROOT / "branch_tracking/output/dampsse_outages_status_anomalies.csv"
RECENT_CUTOFF = pd.Timestamp("2023-01-01")  # DAM PSSE window is ~last 730 days


def _load_compare_module():
    spec = importlib.util.spec_from_file_location("cmp", CMP_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    cmp = _load_compare_module()

    base = pd.read_csv(BASE_OUTAGES_CSV, encoding="utf-8-sig", dtype=str)
    base.columns = [c.strip() for c in base.columns]
    label_cols = cmp.label_columns(base)
    ext = base.apply(cmp.extract_teid_rdfid, axis=1, result_type="expand", label_cols=label_cols)
    ext.columns = ["label_teid", "label_rdfid"]
    base = pd.concat([base, ext], axis=1)

    tmap = pd.read_csv(cmp.TEID_MAP_CSV, dtype=str, usecols=["RdfId", "TransmissionElementId"]).dropna(subset=["RdfId"])
    rdfid_to_teid = dict(zip(tmap["RdfId"], tmap["TransmissionElementId"]))

    def resolve(row):
        if pd.notna(row["label_teid"]):
            return row["label_teid"]
        if pd.notna(row["label_rdfid"]):
            m = rdfid_to_teid.get(row["label_rdfid"])
            if m is not None and str(m).strip() and str(m).lower() != "nan":
                return str(m)
        return None

    base["resolved_teid"] = base.apply(resolve, axis=1)

    ours = pd.read_csv(cmp.BRANCH_TRACKING_CSV, dtype=str).drop_duplicates(subset=["teid"], keep="first")
    ours["teid"] = ours["teid"].astype(str).str.strip()
    m = base.merge(ours, left_on="resolved_teid", right_on="teid", how="left")
    m["Status"] = m["Status"].astype(str).str.strip()

    dam = m["dampsse_default_status"].astype(str).str.strip()
    comparable = m[dam.notna() & (dam != "") & (dam.str.lower() != "nan")].copy()
    comparable["dam"] = comparable["dampsse_default_status"].astype(str).str.strip()
    comparable["imp"] = comparable["implied_default_status"].astype(str).str.strip()
    comparable["isd"] = pd.to_datetime(comparable["in_service_date"], errors="coerce")

    total = len(comparable)
    agree = (comparable["Status"] == comparable["dam"]).sum()
    anom = comparable[(comparable["Status"] == "Closed") & (comparable["dam"] == "Open")].copy()
    rev = comparable[(comparable["Status"] == "Open") & (comparable["dam"] == "Closed")].copy()

    def classify(r):
        if pd.notna(r["isd"]) and r["isd"] >= RECENT_CUTOFF and r["in_service_date_source"] == "energization_outage":
            return "recent_energization_undercount"
        if r["imp"] == "Closed":
            return "dampsse_suspect_auction_disagrees"
        return "residual_review"

    anom["classification"] = anom.apply(classify, axis=1)

    out = anom[[
        "resolved_teid", "branch_id", "Status", "dampsse_default_status", "dampsse_pct_inservice",
        "implied_default_status", "pct_closed", "in_service_date", "in_service_date_source",
        "From Name", "To Name", "Circuit", "DeviceType", "classification",
    ]].rename(columns={"resolved_teid": "teid", "Status": "base_model_status",
                       "From Name": "base_from_name", "To Name": "base_to_name", "Circuit": "base_circuit"})
    out = out.sort_values(["classification", "dampsse_pct_inservice", "teid"])
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_CSV, index=False)

    print("=== base_model_outages vs dampsse_default_status ===")
    print(f"comparable rows: {total}   agree: {agree}   disagree: {total - agree}")
    print(f"\n[base=Closed / dampsse=Open] anomalies (study energizes, we say normally-open): {len(anom)}")
    print(out["classification"].value_counts().to_string())
    residual = out[out["classification"] == "residual_review"]
    print(f"\n  --> genuine manual-review residual: {len(residual)} teids")
    print(residual[["teid", "base_from_name", "base_to_name", "DeviceType",
                    "dampsse_pct_inservice", "in_service_date_source"]].to_string(index=False))

    print(f"\n[base=Open / dampsse=Closed] (consistent with being outaged in this snapshot): {len(rev)}")
    if "MW Loss" in rev.columns:
        mw = pd.to_numeric(rev["MW Loss"], errors="coerce").fillna(0)
        print(f"  rows with study MW Loss != 0: {(mw != 0).sum()} / {len(rev)} "
              "(an open branch carries no flow, so 0 loss does not by itself prove 'outaged')")

    print(f"\nWrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
