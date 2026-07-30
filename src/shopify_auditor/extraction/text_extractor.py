"""Extract visible text content from HTML using BeautifulSoup."""

from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup, Tag

from shopify_auditor.utils.text import clean_whitespace, count_words

_NON_VISIBLE_TAGS = {
    "style", "script", "meta", "link", "noscript",
    "svg", "path", "title", "head",
}


def extract_all(
    html: str,
    url: str = "",
) -> dict[str, Any]:
    """Run all text extraction routines and return a flat dict.

    Returns keys: *title*, *meta_description*, *headings*, *body_text*,
    *buttons*, *word_count*.
    """
    soup = BeautifulSoup(html, "html.parser")
    body_text = extract_body_text(soup)
    return {
        "url": url,
        "title": extract_title(soup),
        "meta_description": extract_meta_description(soup),
        "headings": extract_headings(soup),
        "body_text": body_text,
        "buttons": extract_button_texts(soup),
        "word_count": count_words(body_text),
    }


# ------------------------------------------------------------------
# Individual extractors
# ------------------------------------------------------------------


def _soup(value: str | BeautifulSoup) -> BeautifulSoup:
    """Coerce raw HTML or an existing BeautifulSoup object into soup."""
    return value if isinstance(value, BeautifulSoup) else BeautifulSoup(value, "html.parser")


def extract_title(soup: str | BeautifulSoup) -> str:
    """Return the <title> text or empty string."""
    soup = _soup(soup)
    tag = soup.find("title")
    return tag.get_text(strip=True) if tag else ""


def extract_meta_description(soup: str | BeautifulSoup) -> str:
    """Return the meta description content or empty string."""
    soup = _soup(soup)
    tag = soup.find("meta", attrs={"name": "description"})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return ""


def extract_headings(soup: str | BeautifulSoup) -> list[dict[str, str]]:
    """Return a list of {tag, text} for h1-h6 elements.

    Only includes headings with non-empty visible text.
    """
    soup = _soup(soup)
    results: list[dict[str, str]] = []
    for tag_name in ("h1", "h2", "h3", "h4", "h5", "h6"):
        for tag in soup.find_all(tag_name):
            text = clean_whitespace(tag.get_text(separator=" ", strip=True))
            if text:
                results.append({"tag": tag_name, "text": text})
    return results


def extract_body_text(soup: str | BeautifulSoup) -> str:
    """Extract visible text from the page body.

    Removes content inside ``<script>``, ``<style>``, etc., then joins
    remaining text and cleans whitespace.
    """
    soup = _soup(soup)
    if soup.body:
        for tag in soup.body.find_all(_is_non_visible):
            tag.decompose()
        text = soup.body.get_text(separator=" ", strip=True)
    else:
        text = soup.get_text(separator=" ", strip=True)
        for tag in soup.find_all(_is_non_visible):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)

    return clean_whitespace(text)


def extract_button_texts(soup: str | BeautifulSoup) -> list[str]:
    """Extract visible text from ``<button>`` and ``<input type=submit>``."""
    soup = _soup(soup)
    texts: list[str] = []
    for btn in soup.find_all("button"):
        texts.append(clean_whitespace(btn.get_text(separator=" ", strip=True)))
    for inp in soup.find_all("input", type=lambda v: v and v.lower() in ("submit", "button")):
        val = inp.get("value", "")
        if val:
            texts.append(str(val).strip())
    return [t for t in texts if t]


def extract_alt_texts(soup: str | BeautifulSoup) -> list[str]:
    """Return alt-text values from all ``<img>`` tags."""
    soup = _soup(soup)
    alts: list[str] = []
    for img in soup.find_all("img"):
        alt = img.get("alt", "")
        if alt and alt.strip():
            alts.append(alt.strip())
    return alts


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _is_non_visible(tag: Tag) -> bool:
    return tag.name in _NON_VISIBLE_TAGS
