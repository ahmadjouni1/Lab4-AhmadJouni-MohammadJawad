import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# --- Project info ---
project = "School Manager"
author = "Ahmad Jouni"
release = "1.0"

# --- Extensions ---
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

# Mock GUI deps so autodoc doesn’t fail when PyQt5 isn’t importable at build time
autodoc_mock_imports = ["PyQt5", "sip"]

templates_path = ["_templates"]
exclude_patterns = []

# --- Theme ---
# Prefer Read-the-Docs theme, fall back to alabaster if not available
try:
    import sphinx_rtd_theme  # noqa: F401
    html_theme = "sphinx_rtd_theme"
    html_theme_options = {
        "collapse_navigation": False,
        "navigation_depth": 4,
        "style_external_links": True,
    }
except Exception:
    html_theme = "alabaster"

html_static_path = ["_static"]
