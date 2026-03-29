"""File and MIME helper utilities."""

from pathlib import Path


def get_extension(filename: str) -> str:
    """Return lowercase extension without dot."""
    suffix = Path(filename).suffix.lower()
    return suffix[1:] if suffix.startswith(".") else suffix
