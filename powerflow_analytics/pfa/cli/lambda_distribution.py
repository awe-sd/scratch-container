"""Realistic shadow-price (lambda) DISTRIBUTION for a constraint, built from
the full DAM-offer relief set instead of a single redispatch pair.

Usage:
    uv run pfa lambda-dist \
        --study 14412 --constraint "1436-2081-1@DWCSRAM5"
"""
from __future__ import annotations

import argparse

from pfa.analysis import lambda_dist
from pfa.report import lambda_dist as lambda_report


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--constraint", required=True)
    args = ap.parse_args(argv)
    print(lambda_report.text(lambda_dist.analyze(args.study, args.constraint)))
