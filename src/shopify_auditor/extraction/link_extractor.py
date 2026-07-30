"""Extract and classify links from HTML."""

from __future__ import annotations

from urllib.parse import urlparse

from bs4 import BeautifulSoup

# Keyword sets for link classification.  All lower-case.
_SHIPPING_TERMS = {"shipping", "delivery", "dispatch", "fulfilment", "fulfillment"}
_RETURNS_TERMS = {"return", "refund", "exchange", "money back"}
_CONTACT_TERMS = {"contact", "support", "help", "chat", "email us"}
_FAQ_TERMS = {"faq", "questions", "frequently asked"}
_REVIEW_TERMS = {"review", "testimonial", "rating"}
_POLICY_TERMS = {"privacy", "terms", "cookie", "legal"}
_ABOUT_TERMS = {"about", "our story", "mission"}


def extract_links(html: str, base_url: str = "") -> list[dict[str, str]]:
    """Extract all ``<a href=…>`` links from HTML.

    Returns a list of ``{"href": …, "text": …}`` dicts.
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[dict[str, str]] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(strip=True)
        results.append({"href": href, "text": text or href})
    return results


def classify_link(link: dict[str, str]) -> list[str]:
    """Return a list of category labels for a single link dict.

    E.g. ``["shipping", "policy"]``.
    """
    labels: list[str] = []
    text_lower = link.get("text", "").lower()
    href_lower = link.get("href", "").lower()

    combined = f"{text_lower} {href_lower}"

    if any(t in combined for t in _SHIPPING_TERMS):
        labels.append("shipping")
    if any(t in combined for t in _RETURNS_TERMS):
        labels.append("returns-refund")
    if any(t in combined for t in _CONTACT_TERMS):
        labels.append("contact-support")
    if any(t in combined for t in _FAQ_TERMS):
        labels.append("faq")
    if any(t in combined for t in _REVIEW_TERMS):
        labels.append("reviews")
    if any(t in combined for t in _POLICY_TERMS):
        labels.append("policy")
    if any(t in combined for t in _ABOUT_TERMS):
        labels.append("about")

    if not labels:
        labels.append("other")

    return labels


def is_internal_link(href: str, domain: str) -> bool:
    """Return True if *href* points to the same domain (or is relative)."""
    parsed = urlparse(href)
    if not parsed.netloc:
        return True  # relative path
    return parsed.netloc.lower() == domain.lower()


def extract_links_classified(
    html: str,
    base_url: str = "",
) -> dict[str, list[dict[str, str]]]:
    """Extract all links and group by classification.

    Returns a dict mapping category labels to lists of link dicts.
    """
    domain = urlparse(base_url).netloc.lower() if base_url else ""
    all_links = extract_links(html, base_url)
    grouped: dict[str, list[dict[str, str]]] = {}

    for link in all_links:
        labels = classify_link(link)
        if is_internal_link(link["href"], domain):
            link["internal"] = True
        else:
            link["internal"] = False
        for label in labels:
            grouped.setdefault(label, []).append(link)

    # Always include an "all" key
    grouped["all"] = all_links
    return grouped
