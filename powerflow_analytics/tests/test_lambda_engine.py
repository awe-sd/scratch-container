"""Hand-computed pair-stack math for lambda_engine.lambda_depth_curve."""
from __future__ import annotations

from pfa.analysis.lambda_engine import lambda_at_depth, lambda_depth_curve

# Synthetic relief set: two UP units (negative SF), one DOWN unit (positive SF).
UP = [
    {"sced": "UP1", "sf": -0.5, "price": 20.0, "avail": 50.0},
    {"sced": "UP2", "sf": -0.3, "price": 30.0, "avail": 100.0},
]
DOWN = [
    {"sced": "DN1", "sf": 0.4, "price": 10.0, "avail": 80.0},
]

# By hand:
#   UP1/DN1: dsf = 0.4 - (-0.5) = 0.9, lambda = (20-10)/0.9 = 11.11
#   UP2/DN1: dsf = 0.4 - (-0.3) = 0.7, lambda = (30-10)/0.7 = 28.57
# Greedy always prefers the cheaper pair first (UP1/DN1, lambda=11.11):
#   consumes min(50, 80) = 50 MW of generation * dsf 0.9 = 45 MW of flow.
#   UP1 exhausted; DN1 has 30 MW of generation headroom left.
# Then UP2/DN1 (lambda=28.57) is the only pair left:
#   consumes min(100, 30) = 30 MW * dsf 0.7 = 21 MW of flow -> depth 45 -> 66.
#   DN1 exhausted; stack empties.


def test_pair_stack_two_step_curve():
    curve = lambda_depth_curve(UP, DOWN, max_depth=500)
    assert len(curve) == 2
    assert curve[0]["depth_lo"] == 0.0
    assert round(curve[0]["depth_hi"], 2) == 45.0
    assert curve[0]["lambda"] == round(10.0 / 0.9, 2)
    assert round(curve[1]["depth_hi"], 2) == 66.0
    assert curve[1]["lambda"] == round(20.0 / 0.7, 2)


def test_lambda_nondecreasing_in_depth():
    curve = lambda_depth_curve(UP, DOWN, max_depth=500)
    lambdas = [s["lambda"] for s in curve]
    assert lambdas == sorted(lambdas)


def test_lambda_at_depth_lookup():
    curve = lambda_depth_curve(UP, DOWN, max_depth=500)
    assert lambda_at_depth(curve, 25) == round(10.0 / 0.9, 2)
    assert lambda_at_depth(curve, 50) == round(20.0 / 0.7, 2)
    assert lambda_at_depth(curve, 60) == round(20.0 / 0.7, 2)
    # beyond the curve entirely (stacks exhausted at 66) -> None
    assert lambda_at_depth(curve, 1000) == round(20.0 / 0.7, 2)
