"""Extract likely price information from HTML."""

from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup

# Currency symbols and common price patterns
_CURRENCY_SYMBOLS = r"[$€£¥₹₩₽₪₫₱₴₸₺₼]"
_PRICE_PATTERN = re.compile(
    r"(" + _CURRENCY_SYMBOLS + r")\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?)"
    r"|"
    r"(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?)\s*(" + _CURRENCY_SYMBOLS + r")",
    re.UNICODE,
)

# Patterns commonly found in Shopify price-related elements
_SALE_CLASSES = re.compile(r"sale|compare.?at|was[-\s]?price|original[-\s]?price", re.I)
_PRICE_CLASSES = re.compile(r"price|amount|money|cost", re.I)


def extract_prices(html: str) -> list[dict[str, Any]]:
    """Extract likely price values from HTML.

    Returns a list of dicts with keys:
        *value* (float or None), *raw* (the matched string),
        *currency* (symbol or empty), *is_sale* (bool).
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[dict[str, Any]] = []

    seen_texts: set[str] = set()

    # Strategy 1: Scan elements with price-related classes/ids
    for tag in soup.find_all(class_=_PRICE_CLASSES):
        text = tag.get_text(separator=" ", strip=True)
        if text and text not in seen_texts:
            seen_texts.add(text)
            is_sale = bool(_SALE_CLASSES.search(" ".join(tag.get("class", []))))
            parsed = _parse_price_text(text)
            if parsed:
                results.append(
                    {"value": parsed["value"], "raw": parsed["raw"],
                     "currency": parsed["currency"], "is_sale": is_sale}
                )

    # Strategy 2: Just look at all visible text for price patterns
    body_text = soup.get_text(separator=" ", strip=True)
    for match in _PRICE_PATTERN.finditer(body_text):
        raw = match.group().strip()
        if raw and raw not in seen_texts:
            seen_texts.add(raw)
            currency = match.group(1) or match.group(4) or ""
            num_str = match.group(2) or match.group(3) or ""
            value = _parse_number(num_str)
            if value is not None:
                results.append(
                    {"value": value, "raw": raw,
                     "currency": currency, "is_sale": False}
                )

    return results


# ------------------------------------------------------------------
# Internal
# ------------------------------------------------------------------


def _parse_price_text(text: str) -> dict[str, Any] | None:
    """Try to extract a single numeric price from a text blob."""
    for match in _PRICE_PATTERN.finditer(text):
        currency = match.group(1) or match.group(4) or ""
        num_str = match.group(2) or match.group(3) or ""
        value = _parse_number(num_str)
        if value is not None:
            return {"value": value, "raw": match.group().strip(), "currency": currency}
    return None


def _parse_number(num_str: str) -> float | None:
    """Parse a locale-formatted number into a float.

    Handles both ``1,234.56`` and ``1.234,56`` styles.
    """
    if not num_str:
        return None
    # If contains both dot and comma, the last separator is decimal
    if "." in num_str and "," in num_str:
        if num_str.rfind(",") > num_str.rfind("."):
            # European: 1.234,56
            num_str = num_str.replace(".", "").replace(",", ".")
        else:
            # US: 1,234.56
            num_str = num_str.replace(",", "")
    else:
        num_str = num_str.replace(",", "")
    try:
        return float(num_str)
    except ValueError:
        return None
