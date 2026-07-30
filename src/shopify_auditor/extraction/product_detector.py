"""Detect whether a page is a Shopify product page."""

from __future__ import annotations

import json
import re
from typing import Any

from bs4 import BeautifulSoup

# Strong signals that this is a Shopify product page
_SHOPIFY_PRODUCT_JSON_LD_TYPES = {"Product", "product"}
_SHOPIFY_PRODUCT_CLASSES = re.compile(r"product", re.IGNORECASE)
_ADD_TO_CART_TEXT = [
    "add to cart",
    "add to bag",
    "add to basket",
    "buy now",
    "pre-order",
    "preorder",
]
_VARIANT_SELECTOR_PATTERNS = re.compile(
    r"variant|option[-\s]?select|single-option-selector", re.IGNORECASE
)


def detect_product_page(html: str, url: str = "") -> dict[str, Any]:
    """Analyse HTML and return a dict of product-page signals.

    Returns
    -------
    dict with keys:
        *is_product_page*   — bool, overall heuristic
        *url_has_product_pattern* — bool
        *has_add_to_cart*       — bool
        *has_product_json_ld*   — bool
        *has_variant_selector*  — bool
        *has_product_images*    — bool
        *confidence*            — float 0-1
    """
    soup = BeautifulSoup(html, "html.parser")
    signals: dict[str, Any] = {
        "url_has_product_pattern": False,
        "has_add_to_cart": False,
        "has_product_json_ld": False,
        "has_price": False,
        "has_variant_selector": False,
        "has_product_images": False,
    }

    # 1. URL pattern
    from shopify_auditor.utils.urls import is_likely_product_url

    signals["url_has_product_pattern"] = is_likely_product_url(url)

    # 2. Add-to-cart buttons
    signals["has_add_to_cart"] = _detect_add_to_cart(soup)

    # 3. JSON-LD with @type Product
    signals["has_product_json_ld"] = _detect_product_json_ld(soup)

    # 4. Price presence
    from shopify_auditor.extraction.price_extractor import extract_prices

    prices = extract_prices(html)
    signals["has_price"] = len(prices) > 0

    # 5. Variant selectors
    signals["has_variant_selector"] = _detect_variant_selector(soup)

    # 6. Product-image patterns
    from shopify_auditor.extraction.image_extractor import (
        extract_images,
        likely_product_images,
    )

    images = extract_images(html)
    product_imgs = likely_product_images(images)
    signals["has_product_images"] = len(product_imgs) >= 2

    # Overall confidence
    true_count = sum(1 for v in signals.values() if v)
    signals["confidence"] = round(true_count / max(len(signals), 1), 2)
    signals["is_product_page"] = signals["confidence"] >= 0.5

    return signals


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------


def _detect_add_to_cart(soup: BeautifulSoup) -> bool:
    """Detect add-to-cart buttons or forms."""
    # Check button text
    for btn in soup.find_all(["button", "a"]):
        txt = btn.get_text(strip=True).lower()
        if any(cta in txt for cta in _ADD_TO_CART_TEXT):
            return True
    # Check for common form action patterns
    for form in soup.find_all("form"):
        action = (form.get("action", "") or "").lower()
        if "cart" in action or "add" in action:
            return True
    return False


def _detect_product_json_ld(soup: BeautifulSoup) -> bool:
    """Detect ``@type: Product`` in JSON-LD script blocks."""
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.get_text(strip=True)
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            types = [data.get("@type", "")]
        elif isinstance(data, list):
            types = [item.get("@type", "") for item in data if isinstance(item, dict)]
        else:
            continue
        if any(t in _SHOPIFY_PRODUCT_JSON_LD_TYPES for t in types):
            return True
    return False


def _detect_variant_selector(soup: BeautifulSoup) -> bool:
    """Detect variant/option selectors."""
    # Check select elements with variant-related classes
    for sel in soup.find_all("select"):
        class_str = " ".join(sel.get("class", []))
        if _VARIANT_SELECTOR_PATTERNS.search(class_str):
            return True
    # Check for radio/option inputs
    for inp in soup.find_all("input", type="radio"):
        name = (inp.get("name", "") or "").lower()
        if "variant" in name or "option" in name:
            return True
    return False
