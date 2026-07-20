"""Sentinel-2 chips from the AWS Open Data registry — PRIMARY imagery tool.

Same ESA Sentinel-2 L2A data as CDSE, served from the public `s3://sentinel-cogs`
bucket (us-west-2, Cloud-Optimized GeoTIFFs, produced by Element84 from ESA granules)
and searched via the Earth Search STAC API. NO auth, NO processing-unit quota, NO
rate caps — safe for any number of parallel agents. Single-best-scene chips (lowest
cloud in the window); for median composites / timelapse GIFs use cdse.py (openEO),
which self-queues to CDSE's 2-concurrent/12-per-minute free-tier limits.

Agent usage (run from repo root with `uv run`):
  s2aws.py chip --lat 29.2405 --lon -98.51006 --date 2026-07-12 \
      --out imagery/s2_2026-07-12_wide.png [--buffer-km 2.5] [--window-days 12] \
      [--max-cloud 40]
  s2aws.py chips --lat .. --lon .. --dates 2024-07-01,2025-07-01,2026-07-01 \
      --out-dir imagery/ [...]          # one chip per date, sequential

Output line names the exact scene ID + acquisition date + cloud % (provenance).
A no-scene window prints an explicit negative line and exits 3 (not an error —
log it and widen the window or relax --max-cloud).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import date as Date, timedelta
from pathlib import Path

STAC_URL = "https://earth-search.aws.element84.com/v1/search"


def search_scenes(lat: float, lon: float, day: str, window_days: int,
                  max_cloud: int, limit: int = 4) -> list[dict]:
    d = Date.fromisoformat(day)
    t0, t1 = d - timedelta(days=window_days), d + timedelta(days=window_days)
    body = json.dumps({
        "collections": ["sentinel-2-l2a"],
        "intersects": {"type": "Point", "coordinates": [lon, lat]},
        "datetime": f"{t0}T00:00:00Z/{t1}T23:59:59Z",
        "query": {"eo:cloud_cover": {"lt": max_cloud}},
        "sort": [{"field": "properties.eo:cloud_cover", "direction": "asc"}],
        "limit": limit}).encode()
    req = urllib.request.Request(STAC_URL, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read()).get("features", [])


def chip(lat: float, lon: float, day: str, out: Path, buffer_km: float,
         window_days: int, max_cloud: int) -> int:
    try:
        items = search_scenes(lat, lon, day, window_days, max_cloud)
    except Exception as e:
        print(f"earth-search failed: {e.__class__.__name__}: {e}")
        return 1
    if not items:
        d = Date.fromisoformat(day)
        print(f"NO SCENE: nothing ≤{max_cloud}% cloud within ±{window_days}d of {day} "
              f"at {lat},{lon} — widen --window-days or relax --max-cloud "
              f"(negative evidence, log it)")
        return 3

    import numpy as np
    import rasterio
    from rasterio.warp import transform as rio_transform
    from rasterio.windows import from_bounds

    item = items[0]
    half = buffer_km * 1000.0
    layers = []
    try:
        for band in ("red", "green", "blue"):
            href = item["assets"][band]["href"]
            with rasterio.open(href) as ds:
                (x,), (y,) = rio_transform("EPSG:4326", ds.crs, [lon], [lat])
                win = from_bounds(x - half, y - half, x + half, y + half, ds.transform)
                px = min(int(win.width), 1400)
                layers.append(ds.read(1, window=win, out_shape=(px, px),
                                      boundless=True, fill_value=0))
    except Exception as e:
        print(f"COG read failed: {e.__class__.__name__}: {e}")
        return 1
    rgb = np.stack(layers, axis=-1).astype("float32")
    img = np.clip(rgb / 2500.0 * 255.0, 0, 255).astype("uint8")
    from PIL import Image
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(img).save(out)
    print(f"wrote {out} ({out.stat().st_size/1024:.0f} KB) — AWS COG scene "
          f"{item['id']} acquired {item['properties']['datetime'][:10]} "
          f"(cloud {item['properties']['eo:cloud_cover']:.1f}%), {buffer_km} km buffer "
          f"[single best scene; median composites -> cdse.py]")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("chip")
    p2 = sub.add_parser("chips")
    for p in (p1, p2):
        p.add_argument("--lat", type=float, required=True)
        p.add_argument("--lon", type=float, required=True)
        p.add_argument("--buffer-km", type=float, default=1.6)
        p.add_argument("--window-days", type=int, default=15)
        p.add_argument("--max-cloud", type=int, default=40)
    p1.add_argument("--date", required=True)
    p1.add_argument("--out", type=Path, required=True)
    p2.add_argument("--dates", required=True, help="comma-separated ISO dates")
    p2.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args()
    if a.cmd == "chip":
        sys.exit(chip(a.lat, a.lon, a.date, a.out, a.buffer_km, a.window_days, a.max_cloud))
    rc = 0
    for d in a.dates.split(","):
        d = d.strip()
        rc |= chip(a.lat, a.lon, d, a.out_dir / f"s2_{d}.png",
                   a.buffer_km, a.window_days, a.max_cloud)
    sys.exit(rc)


if __name__ == "__main__":
    main()
