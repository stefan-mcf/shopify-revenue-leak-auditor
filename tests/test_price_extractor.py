"""Tests for price extraction (Tranche 6)."""

from __future__ import annotations

from shopify_auditor.extraction.price_extractor import extract_prices


class TestExtractPrices:
    def test_finds_main_price(self, shopify_product_html: str) -> None:
        prices = extract_prices(shopify_product_html)
        raw_texts = [p["raw"] for p in prices]
        assert any("$89.00" in r for r in raw_texts) or any("89.00" in r for r in raw_texts)

    def test_each_has_expected_keys(self, shopify_product_html: str) -> None:
        prices = extract_prices(shopify_product_html)
        for p in prices:
            assert "value" in p
            assert "raw" in p
            assert "currency" in p
            assert "is_sale" in p

    def test_no_prices_on_text_only_page(self, simple_page_html: str) -> None:
        prices = extract_prices(simple_page_html)
        assert len(prices) == 0

    def test_multiple_prices_detected(self, shopify_product_html: str) -> None:
        prices = extract_prices(shopify_product_html)
        assert len(prices) >= 2  # at least the price and compare-at
