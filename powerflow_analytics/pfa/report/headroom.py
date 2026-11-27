"""Headroom scatter page: one figure on the shared page shell."""
from __future__ import annotations

from pathlib import Path

from pfa.report import html

# Reference/variant figures that must never be overwritten.
PROTECTED_BASENAMES = {
    "ph_headroom_wind_solar.html", "ph_headroom_wind_solar1.html",
    "ph_headroom_wind_solar_v1.html", "ph_headroom_wind_solar_sep25.html",
    "ph_headroom_load_wind_onpeak.html",
}


def check_output_path(path: str | Path) -> Path:
    p = Path(path)
    if p.name in PROTECTED_BASENAMES:
        raise RuntimeError(f"refusing to write to {p} -- this basename is protected "
                           f"(existing reference/variant figure); use a new filename.")
    return p


def render(fig, title: str) -> str:
    return html.page(title, html.figure(fig, "cdn"))
