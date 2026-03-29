"""Shared assets for the Streamlit UI."""

from pathlib import Path

SAMPLE_QUESTIONS = [
    "What are the core hours for remote employees?",
    "How many PTO days can be carried over?",
    "What happens if the Solana RPC endpoint is down?",
    "How quickly must a critical client issue be answered?",
]

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def load_streamlit_css() -> str:
    """Return the external CSS used by the Streamlit app."""
    return (ASSETS_DIR / "streamlit.css").read_text(encoding="utf-8")
