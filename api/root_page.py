"""Helpers for serving the FastAPI root chat page."""

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def load_root_page() -> str:
    """Return the assembled HTML page for the root chat interface."""
    html_template = _read_asset("root_page.html")
    return html_template.format(
        styles=_read_asset("root_page.css"),
        script=_read_asset("root_page.js"),
    )


def _read_asset(name: str) -> str:
    """Read one static asset from the api assets directory."""
    return (ASSETS_DIR / name).read_text(encoding="utf-8")
