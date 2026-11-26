import pandas as pd
import pytest


def _mk_events(rows):
    base = {"teid": 1, "BranchId": 10, "EquipmentName": "X", "ReasonID": 4,
            "toOutageIdentifierId": 100, "toStateId": 1,
            "plannedStartDate": pd.NaT, "plannedEndDate": pd.NaT,
            "actualStartDate": pd.NaT, "actualEndDate": pd.NaT,
            "CancellationDate": pd.NaT, "CancellationReason": None,
            "status": "Apprv", "ReqStatus": "PL"}
    return pd.DataFrame([{**base, **r} for r in rows])


def test_sticky_actual_dates_survive_admin_revision():
    from branch_tracking.pipeline.dates import sticky_actual_dates
    ev = _mk_events([
        {"toStateId": 1, "actualEndDate": pd.Timestamp("2016-08-05")},
        {"toStateId": 2, "status": "RatE"},          # later admin rev, blank dates
    ])
    out = sticky_actual_dates(ev)
    assert out.loc[out["toStateId"] == 2, "actualEndDate"].iloc[0] == pd.Timestamp("2016-08-05")


def test_dedupe_keeps_highest_tostateid_per_ticket_and_branch():
    from branch_tracking.pipeline.dates import dedupe_revisions
    ev = _mk_events([
        {"BranchId": 10, "toStateId": 1}, {"BranchId": 10, "toStateId": 2},
        {"BranchId": 11, "toStateId": 2},   # bundled second device, same ticket
    ])
    out = dedupe_revisions(ev)
    assert len(out) == 2 and set(out["BranchId"]) == {10, 11}
    assert out.loc[out["BranchId"] == 10, "toStateId"].iloc[0] == 2


def test_chain_collapse_and_longest_wins_for_energization():
    from branch_tracking.pipeline.dates import assign_chain_ids, resolve_by_chain
    # 552333 pattern: 11-month chain vs later few-hour ticket
    g = _mk_events([
        {"toOutageIdentifierId": 1, "actualStartDate": pd.Timestamp("2022-01-05"),
         "actualEndDate": pd.Timestamp("2022-06-01")},
        {"toOutageIdentifierId": 2, "actualStartDate": pd.Timestamp("2022-06-02"),
         "actualEndDate": pd.Timestamp("2022-12-06")},
        {"toOutageIdentifierId": 3, "actualStartDate": pd.Timestamp("2023-05-16"),
         "actualEndDate": pd.Timestamp("2023-05-16 13:04")},
    ])
    g["event_date"] = g["actualStartDate"]
    g["event_end_date"] = g["actualEndDate"]
    g["device_name_match"] = False
    g["equip_name_norm"] = "X"
    chains = assign_chain_ids(g.sort_values("event_date"))
    assert chains == [1, 1, 2]              # first two merge, third is separate
    res = resolve_by_chain(g, boundary="end")
    assert res["event_date"] == pd.Timestamp("2022-12-06")   # longest chain's END
    assert res["n_chains"] == 2


def test_mistag_and_wrongdevice_on_real_slice(repo_root):
    from branch_tracking.pipeline.dates import resolve_dates
    events = pd.read_csv(repo_root / "branch_tracking/tests/fixtures/retirement_events_slice.csv",
                         parse_dates=["plannedStartDate", "plannedEndDate",
                                      "actualStartDate", "actualEndDate",
                                      "CancellationDate"])
    out_dir = repo_root / "branch_tracking" / "output"
    teid_map = pd.read_csv(out_dir / "teid_branch_id_map.csv")
    legit = teid_map[teid_map["match_status"] != "unmatched"]
    status = pd.read_csv(out_dir / "branch_default_status.csv")
    res = resolve_dates(events, legit, status)["result"].set_index("teid")
    current = pd.read_csv(out_dir / "teid_inservice_retirement_dates.csv").set_index("teid")
    for teid in [821, 654439, 1743, 113628]:
        if teid in res.index and teid in current.index:
            assert str(res.loc[teid, "retirement_date"]) == str(current.loc[teid, "retirement_date"]), teid
            assert res.loc[teid, "review_flag"] == current.loc[teid, "review_flag"], teid
