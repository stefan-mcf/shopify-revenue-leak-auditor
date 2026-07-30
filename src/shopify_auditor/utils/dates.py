"""Date/time helpers."""

from __future__ import annotations

from datetime import UTC, datetime


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(UTC).isoformat()


def timestamp_for_folder() -> str:
    """Compact timestamp suitable for folder names, e.g. ``20250321_143015``."""
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
