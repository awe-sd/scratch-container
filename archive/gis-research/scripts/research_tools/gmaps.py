"""Google Maps helpers for project research: Places text search + Static Map image.

Credentials: GMAPS_API_KEY in ~/.config/gis-research.env (never in the repo).

Usage:
  uv run gis-research/scripts/research_tools/gmaps.py places "Hanson Solar"
  uv run gis-research/scripts/research_tools/gmaps.py staticmap --lat 31.69 --lon -99.55 \
      --zoom 13 --out imagery/map_site.png [--label "Hanson Solar site"]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ENV_FILE = Path.home() / ".config" / "gis-research.env"


def load_env() -> None:
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())


def api_key() -> str:
    load_env()
    key = os.environ.get("GMAPS_API_KEY", "")
    if not key:
        sys.exit(f"GMAPS_API_KEY not set (expected in {ENV_FILE})")
    return key


def places(query: str) -> None:
    """Places API v1 text search. Prints name | address | lat,lon | types per result."""
    req = urllib.request.Request(
        "https://places.googleapis.com/v1/places:searchText",
        data=json.dumps({"textQuery": query}).encode(),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key(),
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    hits = d.get("places", [])
    if not hits:
        print(f"NO RESULTS for {query!r}")
        return
    for p in hits:
        loc = p["location"]
        print(f"{p['displayName']['text']} | {p.get('formattedAddress','?')} | "
              f"{loc['latitude']:.6f},{loc['longitude']:.6f} | {','.join(p.get('types', [])[:4])}")


def staticmap(lat: float, lon: float, zoom: int, out: Path, label: str | None) -> None:
    """Static Maps image: hybrid (satellite+roads) with a red marker on the site."""
    params = {
        "center": f"{lat},{lon}",
        "zoom": str(zoom),
        "size": "640x640",
        "scale": "2",
        "maptype": "hybrid",
        "markers": f"color:red|{lat},{lon}",
        "key": api_key(),
    }
    url = "https://maps.googleapis.com/maps/api/staticmap?" + urllib.parse.urlencode(params)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"staticmap HTTP {e.code}: {e.read()[:300].decode(errors='replace')}\n"
                 "(403 usually means 'Maps Static API' is not enabled for this key in the "
                 "Google Cloud console)")
    if not data[:4] == b"\x89PNG":
        sys.exit(f"staticmap error: {data[:200]!r}")
    out.write_bytes(data)
    print(f"wrote {out} ({len(data)/1024:.0f} KB, zoom {zoom}, center {lat},{lon}"
          + (f", label {label!r}" if label else "") + ")")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("places", help="Places text search")
    p1.add_argument("query")
    p2 = sub.add_parser("staticmap", help="save hybrid static map PNG with site marker")
    p2.add_argument("--lat", type=float, required=True)
    p2.add_argument("--lon", type=float, required=True)
    p2.add_argument("--zoom", type=int, default=13)
    p2.add_argument("--out", type=Path, required=True)
    p2.add_argument("--label", default=None)
    a = ap.parse_args()
    if a.cmd == "places":
        places(a.query)
    else:
        staticmap(a.lat, a.lon, a.zoom, a.out, a.label)


if __name__ == "__main__":
    main()
