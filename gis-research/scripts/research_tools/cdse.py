"""Sentinel-2 true-color chips from the Copernicus Data Space Ecosystem (CDSE).

Auth: CDSE_USERNAME/CDSE_PASSWORD in ~/.config/gis-research.env -> password-grant OAuth
token -> openEO sync processing API (no dashboard OAuth-client setup needed).

Usage:
  uv run gis-research/scripts/research_tools/cdse.py chip \
      --lat 31.6925 --lon -99.5483 --date 2025-06-01 --out imagery/s2_2025-06-01.png \
      [--buffer-km 1.6] [--window-days 15] [--max-cloud 40]

The chip is a median composite of scenes within +/-window-days of the date (cloud-filtered),
true color (B04/B03/B02), ~10 m/px. Typical use: quarterly series over a project site.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import date as Date, timedelta

ENV_FILE = Path.home() / ".config" / "gis-research.env"
TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
OPENEO_URL = "https://openeo.dataspace.copernicus.eu/openeo/1.2"


def load_env() -> None:
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())


def get_token() -> str:
    load_env()
    user, pw = os.environ.get("CDSE_USERNAME"), os.environ.get("CDSE_PASSWORD")
    if not (user and pw):
        sys.exit(f"CDSE_USERNAME/CDSE_PASSWORD not set (expected in {ENV_FILE})")
    body = urllib.parse.urlencode({
        "grant_type": "password", "client_id": "cdse-public",
        "username": user, "password": pw,
    }).encode()
    with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=body), timeout=30) as r:
        tok = json.load(r)
    return tok["access_token"]


def bbox(lat: float, lon: float, buffer_km: float) -> dict:
    dlat = buffer_km / 111.0
    dlon = buffer_km / (111.0 * math.cos(math.radians(lat)))
    return {"west": lon - dlon, "south": lat - dlat, "east": lon + dlon, "north": lat + dlat}


def chip(lat: float, lon: float, day: str, out: Path,
         buffer_km: float, window_days: int, max_cloud: int) -> None:
    d = Date.fromisoformat(day)
    t0, t1 = d - timedelta(days=window_days), d + timedelta(days=window_days)
    graph = {
        "process": {
            "process_graph": {
            "load": {
                "process_id": "load_collection",
                "arguments": {
                    "id": "SENTINEL2_L2A",
                    "spatial_extent": bbox(lat, lon, buffer_km),
                    "temporal_extent": [str(t0), str(t1)],
                    "bands": ["B04", "B03", "B02"],
                    "properties": {"eo:cloud_cover": {"process_graph": {"cc": {
                        "process_id": "lte", "arguments": {"x": {"from_parameter": "value"},
                                                           "y": max_cloud},
                        "result": True}}}},
                },
            },
            "median": {
                "process_id": "reduce_dimension",
                "arguments": {"data": {"from_node": "load"}, "dimension": "t",
                              "reducer": {"process_graph": {"m": {
                                  "process_id": "median",
                                  "arguments": {"data": {"from_parameter": "data"}},
                                  "result": True}}}},
            },
            "scale": {
                "process_id": "apply",
                "arguments": {"data": {"from_node": "median"},
                              "process": {"process_graph": {"s": {
                                  "process_id": "linear_scale_range",
                                  "arguments": {"x": {"from_parameter": "x"},
                                                "inputMin": 0, "inputMax": 2500,
                                                "outputMin": 0, "outputMax": 255},
                                  "result": True}}}},
            },
            "save": {
                "process_id": "save_result",
                "arguments": {"data": {"from_node": "scale"}, "format": "PNG"},
                "result": True,
            },
            }
        }
    }
    req = urllib.request.Request(
        f"{OPENEO_URL}/result",
        data=json.dumps(graph).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer oidc/CDSE/{get_token()}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"openEO error {e.code}: {e.read()[:500].decode(errors='replace')}")
    if data[:4] != b"\x89PNG":
        sys.exit(f"unexpected response (not PNG): {data[:200]!r}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(f"wrote {out} ({len(data)/1024:.0f} KB) — {day} ±{window_days}d, "
          f"{buffer_km} km buffer, cloud≤{max_cloud}%")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("chip", help="save a Sentinel-2 true-color chip PNG")
    c.add_argument("--lat", type=float, required=True)
    c.add_argument("--lon", type=float, required=True)
    c.add_argument("--date", required=True, help="YYYY-MM-DD (center of search window)")
    c.add_argument("--out", type=Path, required=True)
    c.add_argument("--buffer-km", type=float, default=1.6)
    c.add_argument("--window-days", type=int, default=15)
    c.add_argument("--max-cloud", type=int, default=40)
    a = ap.parse_args()
    chip(a.lat, a.lon, a.date, a.out, a.buffer_km, a.window_days, a.max_cloud)


if __name__ == "__main__":
    main()
