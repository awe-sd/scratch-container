"""Task 05 acceptance: run_scenario(z, y, y) reproduces year-y actuals within
size-index normalization error (synthetic world)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import scenario as sc
import shape_model as sm
from test_shape_model import synthetic_world


def test_identity_scenario_reproduces_actuals_out_of_sample():
    ld, wx, size_index = synthetic_world()
    frame = sm.build_frame(ld, wx, size_index, "NCENT")
    # train STRICTLY before the scored year — no memorization
    train_frame = frame.loc[frame["ts_local"] < "2022-01-01"]
    booster = sm.train_zone(train_frame, num_rounds=300)

    out = sc.run_scenario("NCENT", 2022, 2022, wx, size_index, booster=booster)
    actual = ld.loc[ld["ts_local"].dt.year == 2022].set_index("ts_local")["load_mw"]
    pred = out.set_index("ts_local")["load_mw_pred"]
    joined = pred.to_frame("pred").join(actual.to_frame("act"), how="inner").dropna()
    assert len(joined) > 8700
    annual_err = abs(joined["pred"].sum() - joined["act"].sum()) / joined["act"].sum()
    assert annual_err < 0.01
    hourly_mape = float(np.mean(np.abs(joined["pred"] - joined["act"]) / joined["act"]))
    assert hourly_mape < 0.03


def test_scenario_scales_with_system_year():
    # double-scaling guard: output ratio must be EXACTLY the size_idx ratio
    ld, wx, size_index = synthetic_world()
    frame = sm.build_frame(ld, wx, size_index, "NCENT")
    booster = sm.train_zone(frame, num_rounds=100)
    a = sc.run_scenario("NCENT", 2022, 2019, wx, size_index, booster=booster)
    b = sc.run_scenario("NCENT", 2022, 2023, wx, size_index, booster=booster)
    ratio = b["load_mw_pred"].sum() / a["load_mw_pred"].sum()
    assert ratio == 1.145 / 1.0  # exactly size_idx[2023]/size_idx[2019]


def test_wx2021_is_ex_uri():
    ld, wx, size_index = synthetic_world(start="2021-01-01", end="2021-12-31")
    frame = sm.build_frame(ld, wx, size_index, "NCENT")
    booster = sm.train_zone(frame, num_rounds=50)
    out = sc.run_scenario("NCENT", 2021, 2021, wx, size_index, booster=booster)
    d = (out["ts_local"] - pd.Timedelta(hours=1)).dt.strftime("%Y-%m-%d")
    assert not ((d >= "2021-02-10") & (d <= "2021-02-20")).any()
    assert len(out) < 8760  # 264 Uri hours dropped
