"""Tests for link extraction and classification (Tranche 6)."""

from __future__ import annotations

from shopify_auditor.extraction.link_extractor import (
    classify_link,
    extract_links,
    extract_links_classified,
    is_internal_link,
)


class TestExtractLinks:
    def test_extracts_all_hrefs(self, shopify_product_html: str) -> None:
        links = extract_links(shopify_product_html)
        assert len(links) >= 7  # we have shipping, returns, faq, reviews, contact, external, privacy, terms

    def test_each_link_has_href_and_text(self, shopify_product_html: str) -> None:
        links = extract_links(shopify_product_html)
        for link in links:
            assert "href" in link
            assert "text" in link


class TestClassifyLink:
    def test_shipping_link(self) -> None:
        labels = classify_link({"href": "/shipping", "text": "Shipping Policy"})
        assert "shipping" in labels

    def test_returns_link(self) -> None:
        labels = classify_link({"href": "/returns", "text": "Returns"})
        assert "returns-refund" in labels

    def test_faq_link(self) -> None:
        labels = classify_link({"href": "/faq", "text": "FAQ"})
        assert "faq" in labels

    def test_review_link(self) -> None:
        labels = classify_link({"href": "/reviews", "text": "Customer Reviews"})
        assert "reviews" in labels

    def test_other_link(self) -> None:
        labels = classify_link({"href": "/some-random-page", "text": "Random"})
        assert labels == ["other"]


class TestIsInternalLink:
    def test_relative_is_internal(self) -> None:
        assert is_internal_link("/about", "example.com") is True

    def test_same_domain_is_internal(self) -> None:
        assert is_internal_link("https://example.com/about", "example.com") is True

    def test_different_domain_is_external(self) -> None:
        assert is_internal_link("https://other.com/about", "example.com") is False


class TestExtractLinksClassified:
    def test_contains_all_key(self, shopify_product_html: str) -> None:
        grouped = extract_links_classified(shopify_product_html, "https://shopexample.com")
        assert "all" in grouped
        assert len(grouped["all"]) >= 7

    def test_shipping_category_found(self, shopify_product_html: str) -> None:
        grouped = extract_links_classified(shopify_product_html, "https://shopexample.com")
        assert "shipping" in grouped
