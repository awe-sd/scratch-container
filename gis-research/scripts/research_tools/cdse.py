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
import tempfile
import time
import urllib.error
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


# Cross-process token cache. Every chip/sheet call used to do a fresh password-grant
# login; with several research agents running concurrently the CDSE identity endpoint
# rate-limits those logins (HTTP 403) and whole runs lose imagery. One process logs in,
# everyone reuses the token until it nears expiry (CDSE tokens last ~10 min).
TOKEN_CACHE = Path(tempfile.gettempdir()) / ".cdse_token_cache.json"
TOKEN_SLACK_SEC = 60  # refresh this long before expiry


PROCESSING_LOCK = Path(tempfile.gettempdir()) / ".cdse_processing.lock"
PROCESSING_RETRIES = (15, 45, 120)  # 503/RemoteDisconnected = account PU throttling


def _openeo_result(graph: dict, timeout: int) -> bytes:
    """ONE openEO processing request at a time, fleet-wide (flock held for the whole
    request), with backoff on capacity errors. Rationale: CDSE throttles the account's
    processing units — 8 concurrent agents each firing sync /result calls produced
    connection drops and 45-retry death spirals (Hoyte 23INR0235, 2026-07-20).
    Serialized, each chip takes ~15-40s and the quota is never exhausted."""
    import fcntl
    PROCESSING_LOCK.touch(exist_ok=True)
    with PROCESSING_LOCK.open("r+") as slot:
        fcntl.flock(slot, fcntl.LOCK_EX)  # queue here until the fleet slot frees
        for backoff in (*PROCESSING_RETRIES, None):
            req = urllib.request.Request(
                f"{OPENEO_URL}/result",
                data=json.dumps(graph).encode(),
                headers={"Content-Type": "application/json",
                         "Authorization": f"Bearer oidc/CDSE/{get_token()}"},
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    return r.read()
            except urllib.error.HTTPError as e:
                if e.code in (429, 503) or e.code >= 500:
                    if backoff is None:
                        sys.exit(f"CDSE CAPACITY: openEO {e.code} after retries — do NOT "
                                 "loop; log as negative evidence, move on, imagery "
                                 "backfill will retry later.")
                    print(f"  [openEO {e.code} — capacity backoff {backoff}s]", file=sys.stderr)
                    time.sleep(backoff)
                    continue
                sys.exit(f"openEO error {e.code}: {e.read()[:500].decode(errors='replace')}")
            except (ConnectionError, OSError) as e:  # RemoteDisconnected et al.
                if backoff is None:
                    sys.exit(f"CDSE CAPACITY: {e.__class__.__name__} after retries — do "
                             "NOT loop; log as negative evidence and move on.")
                print(f"  [{e.__class__.__name__} — capacity backoff {backoff}s]", file=sys.stderr)
                time.sleep(backoff)
    raise RuntimeError("unreachable")


def get_token() -> str:
    try:
        c = json.loads(TOKEN_CACHE.read_text())
        if time.time() < c["exp"] - TOKEN_SLACK_SEC:
            return c["token"]
    except (OSError, ValueError, KeyError):
        pass
    load_env()
    user, pw = os.environ.get("CDSE_USERNAME"), os.environ.get("CDSE_PASSWORD")
    if not (user and pw):
        sys.exit(f"CDSE_USERNAME/CDSE_PASSWORD not set (expected in {ENV_FILE})")
    # urlencode encodes @ as %40 in username, which CDSE token endpoint rejects; build manually
    body = (
        "grant_type=password&client_id=cdse-public"
        f"&username={user}&password={urllib.parse.quote(pw, safe='')}"
    ).encode()
    last_err = None
    for backoff in (0, 10, 30):  # the 403 here is rate-limiting — wait it out
        if backoff:
            time.sleep(backoff)
        try:
            with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=body),
                                        timeout=30) as r:
                tok = json.load(r)
            break
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code not in (403, 429):
                raise
    else:
        raise last_err
    token = tok["access_token"]
    exp = time.time() + tok.get("expires_in", 600)
    tmp = TOKEN_CACHE.with_suffix(".tmp")
    tmp.write_text(json.dumps({"token": token, "exp": exp}))
    os.chmod(tmp, 0o600)
    tmp.replace(TOKEN_CACHE)  # atomic — other agents may read concurrently
    return token


def bbox(lat: float, lon: float, buffer_km: float) -> dict:
    dlat = buffer_km / 111.0
    dlon = buffer_km / (111.0 * math.cos(math.radians(lat)))
    return {"west": lon - dlon, "south": lat - dlat, "east": lon + dlon, "north": lat + dlat}


STAC_URL = "https://earth-search.aws.element84.com/v1/search"


def _chip_via_aws(lat: float, lon: float, day: str, out: Path,
                  buffer_km: float, window_days: int, max_cloud: int) -> bool:
    """Quota-free chip from the public AWS Open Data Sentinel-2 L2A COGs
    (s3://sentinel-cogs via Earth Search STAC). No auth, no PU limits, parallel-safe
    — the CDSE free tier (2 concurrent / 12 req/min / 10k PU/mo) cannot serve an
    agent fleet (2026-07-20 lesson). Returns False on miss so the caller can fall
    back to openEO."""
    import urllib.request as _rq
    d = Date.fromisoformat(day)
    t0, t1 = d - timedelta(days=window_days), d + timedelta(days=window_days)
    body = json.dumps({
        "collections": ["sentinel-2-l2a"],
        "intersects": {"type": "Point", "coordinates": [lon, lat]},
        "datetime": f"{t0}T00:00:00Z/{t1}T23:59:59Z",
        "query": {"eo:cloud_cover": {"lt": max_cloud}},
        "sort": [{"field": "properties.eo:cloud_cover", "direction": "asc"}],
        "limit": 4}).encode()
    try:
        req = _rq.Request(STAC_URL, data=body, headers={"Content-Type": "application/json"})
        with _rq.urlopen(req, timeout=45) as r:
            items = json.loads(r.read()).get("features", [])
    except Exception as e:
        print(f"  [earth-search failed: {e.__class__.__name__} — openEO fallback]",
              file=sys.stderr)
        return False
    if not items:
        print(f"  [no AWS scene ≤{max_cloud}% cloud in {t0}..{t1} — openEO fallback]",
              file=sys.stderr)
        return False
    item = items[0]
    import numpy as np
    import rasterio
    from rasterio.warp import transform as rio_transform
    from rasterio.windows import from_bounds
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
        print(f"  [COG read failed: {e.__class__.__name__} — openEO fallback]",
              file=sys.stderr)
        return False
    rgb = np.stack(layers, axis=-1).astype("float32")
    img = np.clip(rgb / 2500.0 * 255.0, 0, 255).astype("uint8")
    from PIL import Image
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(img).save(out)
    scene = item["id"]
    dt = item["properties"]["datetime"][:10]
    cc = round(item["properties"]["eo:cloud_cover"], 1)
    print(f"wrote {out} ({out.stat().st_size/1024:.0f} KB) — AWS COG scene {scene} "
          f"{dt} (cloud {cc}%), {buffer_km} km buffer  [single best scene, not a "
          f"median composite]")
    return True


def chip(lat: float, lon: float, day: str, out: Path,
         buffer_km: float, window_days: int, max_cloud: int) -> None:
    if _chip_via_aws(lat, lon, day, out, buffer_km, window_days, max_cloud):
        return
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
    data = _openeo_result(graph, timeout=300)
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
    print(f"requesting {cadence}ly composites {start}..{end} (single openEO job) ...")
    data = _openeo_result(graph, timeout=900)

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


def chips_parallel(lat: float, lon: float, dates: list[str], out_dir: Path,
                   buffer_km: float, window_days: int, max_cloud: int, workers: int) -> None:
    """Fetch several crisp chips concurrently (one openEO sync job each)."""
    import time
    from concurrent.futures import ThreadPoolExecutor, as_completed
    out_dir.mkdir(parents=True, exist_ok=True)
    def one(d: str) -> str:
        for attempt in (1, 2, 3):
            try:
                chip(lat, lon, d, out_dir / f"s2_{d}.png", buffer_km, window_days, max_cloud)
                return d
            except (SystemExit, Exception) as e:   # transient disconnects happen under concurrency
                if attempt == 3:
                    raise RuntimeError(f"{d}: {e}") from e
                time.sleep(5 * attempt)
        return d
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, d): d for d in dates}
        for f in as_completed(futs):
            try:
                f.result()
            except Exception as e:                  # keep the batch alive
                print(f"FAILED {futs[f]}: {e}")


def sheet(img_dir: Path, out: Path, cols: int, thumb: int) -> None:
    """Contact sheet: grid of labeled thumbnails from s2_*.png — ONE image for agent evals."""
    from PIL import Image, ImageDraw
    frames = sorted(p for p in img_dir.glob("s2_*.png")
                    if "_wide" not in p.stem and "_xwide" not in p.stem)
    if not frames:
        sys.exit(f"no s2_*.png frames in {img_dir}")
    rows = -(-len(frames) // cols)
    grid = Image.new("RGB", (cols * thumb, rows * (thumb + 14)), (12, 12, 12))
    d = ImageDraw.Draw(grid)
    for i, p in enumerate(frames):
        im = Image.open(p).convert("RGB").resize((thumb, thumb))
        x, y = (i % cols) * thumb, (i // cols) * (thumb + 14)
        grid.paste(im, (x, y))
        d.text((x + 3, y + thumb + 1), p.stem.replace("s2_", ""), fill=(255, 255, 0))
    grid.save(out)
    print(f"wrote {out} — {len(frames)} frames, {cols}x{rows} grid, {thumb}px thumbs")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("chip", help="save a Sentinel-2 true-color chip PNG")
    c.add_argument("--lat", type=float, required=True)
    c.add_argument("--lon", type=float, required=True)
    c.add_argument("--date", required=True, help="YYYY-MM-DD (center of search window)")
    c.add_argument("--out", type=Path, required=True)
    c.add_argument("--buffer-km", type=float, default=6.0)
    c.add_argument("--window-days", type=int, default=15)
    c.add_argument("--max-cloud", type=int, default=40)
    t = sub.add_parser("timelapse", help="one-job composite series -> frame PNGs + GIF")
    t.add_argument("--lat", type=float, required=True)
    t.add_argument("--lon", type=float, required=True)
    t.add_argument("--start", required=True, help="YYYY-MM-DD")
    t.add_argument("--end", required=True, help="YYYY-MM-DD")
    t.add_argument("--out-dir", type=Path, required=True)
    t.add_argument("--cadence", choices=["month", "dekad"], default="month")
    t.add_argument("--buffer-km", type=float, default=6.0,
                   help="6 km default = xwide view, ~1200px frames (10 m/px)")
    t.add_argument("--max-cloud", type=int, default=40)
    b = sub.add_parser("chips", help="parallel crisp chips for several dates")
    b.add_argument("--lat", type=float, required=True)
    b.add_argument("--lon", type=float, required=True)
    b.add_argument("--dates", required=True, help="comma-separated YYYY-MM-DD list")
    b.add_argument("--out-dir", type=Path, required=True)
    b.add_argument("--buffer-km", type=float, default=6.0)
    b.add_argument("--window-days", type=int, default=15)
    b.add_argument("--max-cloud", type=int, default=40)
    b.add_argument("--workers", type=int, default=4)
    s = sub.add_parser("sheet", help="contact-sheet grid of s2_*.png for cheap agent evals")
    s.add_argument("--dir", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)
    s.add_argument("--cols", type=int, default=5)
    s.add_argument("--thumb", type=int, default=220)
    a = ap.parse_args()
    if a.cmd == "chip":
        chip(a.lat, a.lon, a.date, a.out, a.buffer_km, a.window_days, a.max_cloud)
    elif a.cmd == "timelapse":
        timelapse(a.lat, a.lon, a.start, a.end, a.out_dir, a.cadence, a.buffer_km, a.max_cloud)
    elif a.cmd == "chips":
        chips_parallel(a.lat, a.lon, a.dates.split(","), a.out_dir,
                       a.buffer_km, a.window_days, a.max_cloud, a.workers)
    else:
        sheet(a.dir, a.out, a.cols, a.thumb)


if __name__ == "__main__":
    main()
