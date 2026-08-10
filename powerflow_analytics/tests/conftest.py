"""Ensure the Dash app (use_pages=True) is instantiated before any page module
is imported directly by a test — dash.register_page() requires app instantiation
to have happened first (it needs dash._pages.CONFIG wired to a real app config).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.app import app  # noqa: F401  (import order matters, see docstring)
