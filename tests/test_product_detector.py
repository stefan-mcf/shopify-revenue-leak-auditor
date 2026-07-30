"""Tests for Shopify product page detection (Tranche 6)."""

from __future__ import annotations

from shopify_auditor.extraction.product_detector import detect_product_page


class TestDetectProductPage:
    def test_detects_shopify_product_page(self, shopify_product_html: str) -> None:
        signals = detect_product_page(
            shopify_product_html,
            url="https://shopexample.com/products/classic-leather-tote",
        )
        assert signals["is_product_page"] is True
        assert signals["url_has_product_pattern"] is True
        assert signals["has_add_to_cart"] is True
        assert signals["has_product_json_ld"] is True
        assert signals["has_price"] is True
        assert signals["has_variant_selector"] is True
        assert signals["has_product_images"] is True
        assert signals["confidence"] >= 0.5

    def test_non_product_page(self, simple_page_html: str) -> None:
        signals = detect_product_page(
            simple_page_html,
            url="https://example.com/about",
        )
        assert signals["is_product_page"] is False

    def test_blog_page_no_signals(self, no_product_page_html: str) -> None:
        signals = detect_product_page(
            no_product_page_html,
            url="https://example.com/blog/tips",
        )
        assert signals["is_product_page"] is False
        assert signals["has_add_to_cart"] is False
        assert signals["has_product_json_ld"] is False

    def test_product_json_ld_alone_can_trigger(self, product_json_ld_html: str) -> None:
        signals = detect_product_page(
            product_json_ld_html,
            url="https://example.com/products/widget",
        )
        # Has JSON-LD Product + add to cart button + URL pattern
        assert signals["has_product_json_ld"] is True
        assert signals["has_add_to_cart"] is True

    def test_confidence_calculation(self, shopify_product_html: str) -> None:
        signals = detect_product_page(
            shopify_product_html,
            url="https://shopexample.com/products/classic-leather-tote",
        )
        assert 0.0 <= signals["confidence"] <= 1.0
