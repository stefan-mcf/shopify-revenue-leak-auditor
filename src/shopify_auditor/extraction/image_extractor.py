"""Extract and analyse image elements from HTML."""

from __future__ import annotations

from bs4 import BeautifulSoup


def extract_images(html: str, base_url: str = "") -> list[dict[str, str]]:
    """Extract all ``<img>`` tags and return ``{"src": …, "alt": …}`` dicts."""
    soup = BeautifulSoup(html, "html.parser")
    results: list[dict[str, str]] = []
    for img in soup.find_all("img"):
        src = img.get("src", "").strip()
        alt = img.get("alt", "").strip()
        if src:
            results.append({"src": src, "alt": alt})
    return results


def count_missing_alt(images: list[dict[str, str]]) -> int:
    """Return count of images without alt text."""
    return sum(1 for img in images if not img.get("alt"))


def likely_product_images(images: list[dict[str, str]]) -> list[dict[str, str]]:
    """Heuristic filter: return images that are likely product photos.

    Filters for larger-looking filenames (not icons, logos, or thumbnails)
    by excluding images whose src contains keywords like ``icon``,
    ``logo``, ``thumb``, ``sprite``, ``banner``, ``badge``.
    """
    exclude_keywords = {"icon", "logo", "thumb", "sprite", "banner", "badge", "checkout"}

    results: list[dict[str, str]] = []
    for img in images:
        src_lower = img["src"].lower()
        if any(kw in src_lower for kw in exclude_keywords):
            continue
        results.append(img)
    return results
