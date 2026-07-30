"""URL normalization, validation, slug and product URL detection."""

from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse

# Common Shopify/regex product URL patterns
_PRODUCT_PATTERNS = [
    re.compile(r"/products/", re.IGNORECASE),
    re.compile(r"/product/", re.IGNORECASE),
    re.compile(r"/item/", re.IGNORECASE),
    re.compile(r"/dp/", re.IGNORECASE),  # Amazon-style
    re.compile(r"product_id=", re.IGNORECASE),
    re.compile(r"id=\d{5,}", re.IGNORECASE),
]


def normalize_url(url: str) -> str:
    """Normalize a URL: lower scheme+netloc, strip trailing slash, remove fragment.

    Args:
        url: Raw input URL.

    Returns:
        Normalized URL string.

    Raises:
        ValueError: If the URL cannot be parsed.
    """
    url = url.strip()
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    # Lower scheme, netloc and path for deterministic slugs/tests
    normalized = parsed._replace(
        scheme="https",
        netloc=parsed.netloc.lower(),
        path=parsed.path.lower(),
        fragment="",
    )
    path = normalized.path.rstrip("/")
    normalized = normalized._replace(path=path)
    return urlunparse(normalized)


def is_valid_url(url: str) -> bool:
    """Check whether *url* is a syntactically valid HTTP(S) URL.

    Does *not* guarantee the resource is reachable.
    """
    try:
        parsed = urlparse(url.strip())
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return False
        host = (parsed.hostname or "").strip(".")
        return "." in host or host in {"localhost"}
    except Exception:
        return False


def get_domain(url: str) -> str:
    """Extract the domain (hostname) from a URL.

    Returns empty string on failure.
    """
    try:
        parsed = urlparse(url.strip())
        return parsed.netloc or ""
    except Exception:
        return ""


def infer_slug_from_url(url: str) -> str:
    """Derive a short human-readable slug from a product URL or fallback.

    Example:
        ``https://example.com/products/my-product`` -> ``example-my-product``

    Falls back to a sanitised domain fragment.
    """
    domain = get_domain(url)
    try:
        parsed = urlparse(url.strip())
        path = parsed.path.rstrip("/")
    except Exception:
        return _sanitise(domain)

    slug_candidates = [
        s for s in path.split("/") if s and s not in ("products", "product", "item")
    ]
    if slug_candidates:
        slug = slug_candidates[-1]
    else:
        slug = domain.replace(".", "-")

    return _sanitise(slug)


def is_likely_product_url(url: str) -> bool:
    """Heuristic: return True if *url* looks like an ecommerce product page."""
    try:
        url_norm = normalize_url(url)
    except ValueError:
        return False
    for pat in _PRODUCT_PATTERNS:
        if pat.search(url_norm):
            return True
    return False


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_INVALID_FS_CHARS = re.compile(r"[^a-zA-Z0-9._-]")


def _sanitise(text: str) -> str:
    """Replace non-filename-safe characters for slug-like results."""
    return _INVALID_FS_CHARS.sub("-", text).strip("-").lower()
