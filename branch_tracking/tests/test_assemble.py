import pandas as pd


def test_build_table_matches_current_output_exactly(repo_root):
    from branch_tracking.pipeline import assemble
    out_dir = repo_root / "branch_tracking" / "output"
    table = assemble.build_table(
        teid_map=pd.read_csv(out_dir / "teid_branch_id_map.csv"),
        dates=pd.read_csv(out_dir / "teid_inservice_retirement_dates.csv"),
        status=pd.read_csv(out_dir / "branch_default_status.csv"),
        dampsse=pd.read_csv(out_dir / "dampsse_default_status.csv"),
        dampsse_fallback=pd.read_csv(out_dir / "dampsse_default_status_fallback.csv"),
    )
    current = pd.read_csv(out_dir / "branch_tracking_table.csv")
    pd.testing.assert_frame_equal(
        table.reset_index(drop=True).astype(str),
        current.astype(str),
    )
