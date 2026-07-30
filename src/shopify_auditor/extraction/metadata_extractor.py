"""Extract metadata elements from HTML: title, meta, OpenGraph, JSON-LD."""

from __future__ import annotations

import json
import re
from typing import Any

from bs4 import BeautifulSoup


def extract_metadata(html: str) -> dict[str, Any]:
    """Run all metadata extraction and return a combined dict.

    Keys returned:
        *title*, *meta_description*, *canonical_url*,
        *og_title*, *og_description*, *structured_data*.
    """
    soup = BeautifulSoup(html, "html.parser")

    return {
        "title": _extract_title(soup),
        "meta_description": _extract_meta_description(soup),
        "canonical_url": _extract_canonical(soup),
        "og_title": _extract_og_tag(soup, "title"),
        "og_description": _extract_og_tag(soup, "description"),
        "structured_data": _extract_json_ld(soup),
    }


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------


def _extract_title(soup: BeautifulSoup) -> str:
    tag = soup.find("title")
    return tag.get_text(strip=True) if tag else ""


def _extract_meta_description(soup: BeautifulSoup) -> str:
    tag = soup.find("meta", attrs={"name": "description"})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return ""


def _extract_canonical(soup: BeautifulSoup) -> str:
    tag = soup.find("link", rel="canonical")
    if tag and tag.get("href"):
        return tag["href"].strip()
    return ""


def _extract_og_tag(soup: BeautifulSoup, property_name: str) -> str:
    """Extract a single OpenGraph meta tag by property name suffix.

    Handles ``og:title``, ``og:description``, etc.
    """
    og_prop = f"og:{property_name}"
    tag = soup.find("meta", attrs={"property": og_prop}) or soup.find(
        "meta", attrs={"name": og_prop}
    )
    if tag and tag.get("content"):
        return tag["content"].strip()
    return ""


def _extract_json_ld(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Extract all JSON-LD script blocks and try to parse them."""
    results: list[dict[str, Any]] = []
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.get_text(strip=True)
        if not raw:
            continue
        # Sometimes there's more than one JSON object — try to extract individually
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                results.append(data)
            elif isinstance(data, list):
                results.extend(data)
        except json.JSONDecodeError:
            # Attempt regex extraction for common malformed patterns
            objects = _extract_json_objects(raw)
            results.extend(objects)
    return results


_JSON_OBJECT_RE = re.compile(r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}")


def _extract_json_objects(text: str) -> list[dict[str, Any]]:
    """Crude extraction of JSON-like dicts from a string.

    Used as a fallback when ``json.loads`` fails on the full blob.
    """
    results: list[dict[str, Any]] = []
    for match in _JSON_OBJECT_RE.finditer(text):
        try:
            obj = json.loads(match.group())
            if isinstance(obj, dict):
                results.append(obj)
        except json.JSONDecodeError:
            continue
    return results
