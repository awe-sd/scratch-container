"""Sentinel-2 true-color chips from the Copernicus Data Space Ecosystem (CDSE).

Auth: CDSE_USERNAME/CDSE_PASSWORD in ~/.config/gis-research.env -> password-grant OAuth
token -> openEO sync processing API (no dashboard OAuth-client setup needed).

Usage:
  uv run gis-research/scripts/research_tools/cdse.py chip \
      --lat 31.6925 --lon -99.5483 --date 2025-06-01 --out imagery/s2_2025-06-01.png \
      [--buffer-km 1.6] [--window-days 15] [--max-cloud 40]

  uv run gis-research/scripts/research_tools/cdse.py timelapse \
      --lat 31.6925 --lon -99.5483 --start 2024-07-01 --end 2026-07-01 \
      --out-dir imagery/ [--cadence month|dekad] [--buffer-km 1.6] [--max-cloud 40]

`chip` = median composite of scenes within +/-window-days of the date (cloud-filtered),
true color (B04/B03/B02), ~10 m/px.
`timelapse` = ONE openEO job computing per-period composites server-side (aggregate_temporal),
downloaded as netCDF, rendered locally to frame PNGs + an animated timelapse.gif — much
faster than requesting each date as a separate chip.
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


def timelapse(lat: float, lon: float, start: str, end: str, out_dir: Path,
              cadence: str, buffer_km: float, max_cloud: int) -> None:
    """One openEO job → per-period median composites (netCDF) → frame PNGs + animated GIF."""
    period = {"month": "month", "dekad": "dekad"}[cadence]  # dekad = 10-day periods
    graph = {
        "process": {
            "process_graph": {
                "load": {
                    "process_id": "load_collection",
                    "arguments": {
                        "id": "SENTINEL2_L2A",
                        "spatial_extent": bbox(lat, lon, buffer_km),
                        "temporal_extent": [start, end],
                        "bands": ["B04", "B03", "B02"],
                        "properties": {"eo:cloud_cover": {"process_graph": {"cc": {
                            "process_id": "lte",
                            "arguments": {"x": {"from_parameter": "value"}, "y": max_cloud},
                            "result": True}}}},
                    },
                },
                "agg": {
                    "process_id": "aggregate_temporal_period",
                    "arguments": {"data": {"from_node": "load"}, "period": period,
                                  "reducer": {"process_graph": {"m": {
                                      "process_id": "median",
                                      "arguments": {"data": {"from_parameter": "data"}},
                                      "result": True}}}},
                },
                "save": {
                    "process_id": "save_result",
                    "arguments": {"data": {"from_node": "agg"}, "format": "netCDF"},
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
    print(f"requesting {cadence}ly composites {start}..{end} (single openEO job) ...")
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"openEO error {e.code}: {e.read()[:500].decode(errors='replace')}")

    out_dir.mkdir(parents=True, exist_ok=True)
    nc_path = out_dir / "timelapse_raw.nc"
    nc_path.write_bytes(data)

    import numpy as np
    import xarray as xr
    from PIL import Image, ImageDraw

    ds = xr.open_dataset(nc_path)
    frames, labels = [], []
    for i, t in enumerate(ds["t"].values):
        label = str(t)[:10]
        rgb = np.stack([ds[b].isel(t=i).values for b in ("B04", "B03", "B02")], axis=-1)
        if np.all(np.isnan(rgb)):
            continue  # fully cloud-filtered period
        img = np.clip(np.nan_to_num(rgb) / 2500.0 * 255.0, 0, 255).astype("uint8")
        im = Image.fromarray(img).convert("RGB")
        ImageDraw.Draw(im).rectangle([0, 0, 92, 14], fill=(0, 0, 0))
        ImageDraw.Draw(im).text((3, 2), label, fill=(255, 255, 0))
        fp = out_dir / f"s2_{label}.png"
        im.save(fp)
        frames.append(im)
        labels.append(label)
    if not frames:
        sys.exit("no usable frames (all periods fully clouded out) — raise --max-cloud or widen range")
    gif = out_dir / "timelapse.gif"
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=700, loop=0)
    nc_path.unlink()  # raw netCDF is large and regenerable
    print(f"wrote {len(frames)} frames ({labels[0]} .. {labels[-1]}) + {gif}")


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
    t = sub.add_parser("timelapse", help="one-job composite series -> frame PNGs + GIF")
    t.add_argument("--lat", type=float, required=True)
    t.add_argument("--lon", type=float, required=True)
    t.add_argument("--start", required=True, help="YYYY-MM-DD")
    t.add_argument("--end", required=True, help="YYYY-MM-DD")
    t.add_argument("--out-dir", type=Path, required=True)
    t.add_argument("--cadence", choices=["month", "dekad"], default="month")
    t.add_argument("--buffer-km", type=float, default=1.6)
    t.add_argument("--max-cloud", type=int, default=40)
    a = ap.parse_args()
    if a.cmd == "chip":
        chip(a.lat, a.lon, a.date, a.out, a.buffer_km, a.window_days, a.max_cloud)
    else:
        timelapse(a.lat, a.lon, a.start, a.end, a.out_dir, a.cadence, a.buffer_km, a.max_cloud)


if __name__ == "__main__":
    main()
