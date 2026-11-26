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


PROCESSING_RETRIES = (15, 45, 120)
# CDSE free tier (documentation.dataspace.copernicus.eu/Quotas.html, verified
# 2026-07-20): 2 concurrent requests, 12 requests/minute, 10k PU/month. Violating the
# first two gets the account connection-dropped (the 2026-07-20 fleet incident — at
# 314/10,000 PU, so it was rate enforcement, not quota). The limiter below makes any
# number of agents self-queue into compliance: 2 fleet-wide slots + a shared 12/min
# window. Agents just call chip/timelapse; queueing is automatic.
_SLOT_FILES = [Path(tempfile.gettempdir()) / f".cdse_slot{i}.lock" for i in (0, 1)]
_RATE_FILE = Path(tempfile.gettempdir()) / ".cdse_rate.json"
_MAX_PER_MIN = 10  # stay under the documented 12/min with margin


def _acquire_slot():
    """Block until one of the 2 fleet-wide CDSE slots is free; return (fh, unlock)."""
    import fcntl
    while True:
        for sf in _SLOT_FILES:
            sf.touch(exist_ok=True)
            fh = sf.open("r+")
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return fh
            except OSError:
                fh.close()
        time.sleep(2)


def _rate_gate() -> None:
    """Shared 12/min budget (kept at 10/min): sleep until a request token frees."""
    import fcntl
    _RATE_FILE.touch(exist_ok=True)
    while True:
        with _RATE_FILE.open("r+") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                stamps = json.loads(fh.read() or "[]")
            except ValueError:
                stamps = []
            now = time.time()
            stamps = [t for t in stamps if now - t < 60]
            if len(stamps) < _MAX_PER_MIN:
                stamps.append(now)
                fh.seek(0), fh.truncate(), fh.write(json.dumps(stamps))
                return
            wait = 61 - (now - stamps[0])
        time.sleep(max(wait, 1))


def _openeo_result(graph: dict, timeout: int) -> bytes:
    """openEO sync processing within CDSE free-tier limits (see above), with backoff
    on residual capacity errors."""
    slot = _acquire_slot()
    try:
        for backoff in (*PROCESSING_RETRIES, None):
            _rate_gate()
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
    finally:
        slot.close()  # flock released the moment processing ends, not at process exit
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


def chip(lat: float, lon: float, day: str, out: Path,
         buffer_km: float, window_days: int, max_cloud: int) -> None:
    # NOTE: for plain chips prefer `s2aws.py chip` (quota-free AWS Open Data);
    # cdse.py = median composites/timelapse via openEO, rate-limited to free tier.
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
