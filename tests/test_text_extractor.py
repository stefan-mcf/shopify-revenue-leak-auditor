"""Tests for text extraction from HTML (Tranche 6)."""

from __future__ import annotations

from shopify_auditor.extraction.text_extractor import (
    extract_all,
    extract_body_text,
    extract_button_texts,
    extract_headings,
    extract_meta_description,
    extract_title,
)


class TestExtractTitle:
    def test_finds_title(self, shopify_product_html: str) -> None:
        assert extract_title(shopify_product_html) == "Classic Leather Tote Bag – ShopExample"

    def test_empty_when_no_title(self) -> None:
        assert extract_title("<html><body>no title</body></html>") == ""


class TestExtractMetaDescription:
    def test_finds_meta(self, shopify_product_html: str) -> None:
        desc = extract_meta_description(shopify_product_html)
        assert "Handcrafted" in desc
        assert "free shipping" in desc.lower()


class TestExtractHeadings:
    def test_finds_h1_and_h2(self, shopify_product_html: str) -> None:
        headings = extract_headings(shopify_product_html)
        texts = [h["text"] for h in headings]
        assert "Classic Leather Tote Bag" in texts
        assert "Details" in texts

    def test_heading_tags_stored(self, shopify_product_html: str) -> None:
        headings = extract_headings(shopify_product_html)
        h1s = [h for h in headings if h["tag"] == "h1"]
        assert len(h1s) == 1


class TestExtractBodyText:
    def test_extracts_visible_text(self, shopify_product_html: str) -> None:
        text = extract_body_text(shopify_product_html)
        assert "Handcrafted from full-grain leather" in text
        assert "Free shipping" in text

    def test_removes_script_style_content(self) -> None:
        html = "<html><body><p>Visible</p><script>var x=1;</script><style>.cls{}</style></body></html>"
        text = extract_body_text(html)
        assert "Visible" in text
        assert "var x" not in text
        assert ".cls" not in text


class TestExtractButtonTexts:
    def test_finds_add_to_cart(self, shopify_product_html: str) -> None:
        buttons = extract_button_texts(shopify_product_html)
        assert any("Add to Cart" in b for b in buttons)


class TestExtractAll:
    def test_returns_complete_dict(self, shopify_product_html: str) -> None:
        result = extract_all(shopify_product_html)
        assert result["title"] == "Classic Leather Tote Bag – ShopExample"
        assert len(result["headings"]) >= 2
        assert "Handcrafted" in result["body_text"]
