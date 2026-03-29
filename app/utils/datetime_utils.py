"""Date and time helper utilities."""

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)
