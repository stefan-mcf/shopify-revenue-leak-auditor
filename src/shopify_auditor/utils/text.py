"""Text utilities: whitespace, truncation, term matching."""

from __future__ import annotations

import re


def clean_whitespace(text: str) -> str:
    """Collapse consecutive whitespace (including newlines) into single spaces.

    Strips leading/trailing whitespace.
    """
    return re.sub(r"\s+", " ", text).strip()


def truncate(text: str, max_chars: int = 200) -> str:
    """Truncate text to *max_chars* characters, appending ``...`` if cut."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."


def contains_any(text: str, terms: list[str]) -> bool:
    """Case-insensitive check: does *text* contain any of the *terms*?"""
    lower = text.lower()
    for t in terms:
        if t.lower() in lower:
            return True
    return False


def count_words(text: str) -> int:
    """Count whitespace-separated words in *text*."""
    return len(text.split())
