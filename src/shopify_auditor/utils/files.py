"""File-system utilities: directory creation, output paths, JSON/text writes."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from shopify_auditor.utils.urls import get_domain, infer_slug_from_url


def ensure_dir(path: str | Path) -> Path:
    """Create directory (and parents) if it does not exist. Return the Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_text(path: str | Path, content: str) -> Path:
    """Write *content* as UTF-8 text. Create parent dirs automatically."""
    p = Path(path)
    ensure_dir(p.parent)
    p.write_text(content, encoding="utf-8")
    return p


def write_json(path: str | Path, data: Any, **kwargs: Any) -> Path:
    """Write *data* as pretty-printed JSON. Create parent dirs automatically."""
    p = Path(path)
    ensure_dir(p.parent)
    p.write_text(
        json.dumps(data, indent=2, default=str, **kwargs),
        encoding="utf-8",
    )
    return p


# Characters safe in filenames — replace everything else with hyphens.
_SAFE_CHARS = re.compile(r"[^a-zA-Z0-9._-]")


def safe_filename(value: str, max_len: int = 80) -> str:
    """Convert an arbitrary string into a filesystem-safe filename.

    *   Replaces unsafe characters with ``-``.
    *   Collapses consecutive ``-``.
    *   Strips leading/trailing ``-``.
    *   Truncates to *max_len*.
    """
    safe = _SAFE_CHARS.sub("-", value)
    safe = re.sub(r"-{2,}", "-", safe).strip("-")
    return safe[:max_len]


def create_audit_output_dir(base_dir: str | Path, url: str) -> Path:
    """Create a deterministic output directory for a given URL.

    Directory name: ``{domain}-{slug}`` where *slug* is derived from the URL
    path via :func:`infer_slug_from_url`.
    """
    domain = get_domain(url)
    slug = infer_slug_from_url(url)
    dir_name = safe_filename(f"{domain}-{slug}")
    out = Path(base_dir) / dir_name
    ensure_dir(out)
    return out
