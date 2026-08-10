"""Ensure the Dash app (use_pages=True) is instantiated before any page module
is imported directly by a test — dash.register_page() requires app instantiation
to have happened first (it needs dash._pages.CONFIG wired to a real app config
via Dash.__init__; see dash._validate.validate_use_pages).

This import also fixes module identity: app.py passes the package name "app"
(not its own __name__) to dash.Dash(...), so Dash's pages-folder auto-discovery
imports the explorer page under the sys.modules key "app.pages.explorer" — the
exact same key `from app.pages import explorer` resolves to in test modules.
Because that key is already populated by the time test modules run their own
top-level imports, Python's import machinery reuses the cached module instead
of re-executing pages/explorer.py, so register_page() and the two @callback
decorators run exactly once. (Verified live: before the app.py fix, Dash's
auto-discovery used the top-level key "pages.explorer" while direct imports
used "app.pages.explorer" — two distinct module objects for one file, each
registering the "/" page and its callbacks, leaving dash.page_registry with
two entries for path "/".)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.app import app  # noqa: F401  (import order matters, see docstring)
