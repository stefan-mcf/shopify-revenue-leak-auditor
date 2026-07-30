"""Tests for metadata extraction (Tranche 6)."""

from __future__ import annotations

from shopify_auditor.extraction.metadata_extractor import extract_metadata


class TestExtractMetadata:
    def test_returns_all_keys(self, shopify_product_html: str) -> None:
        meta = extract_metadata(shopify_product_html)
        assert "title" in meta
        assert "meta_description" in meta
        assert "canonical_url" in meta
        assert "og_title" in meta
        assert "og_description" in meta
        assert "structured_data" in meta

    def test_extracts_title(self, shopify_product_html: str) -> None:
        meta = extract_metadata(shopify_product_html)
        assert "Classic Leather Tote" in meta["title"]

    def test_extracts_canonical(self, shopify_product_html: str) -> None:
        meta = extract_metadata(shopify_product_html)
        assert "shopexample.com/products/classic-leather-tote" in meta["canonical_url"]

    def test_extracts_og_tags(self, shopify_product_html: str) -> None:
        meta = extract_metadata(shopify_product_html)
        assert meta["og_title"] == "Classic Leather Tote Bag"
        assert "free shipping" in meta["og_description"].lower()

    def test_extracts_json_ld(self, shopify_product_html: str) -> None:
        meta = extract_metadata(shopify_product_html)
        assert len(meta["structured_data"]) > 0
        # Should find the Product JSON-LD
        types = [sd.get("@type") for sd in meta["structured_data"]]
        assert "Product" in types

    def test_json_ld_multiple_blobs(self, product_json_ld_html: str) -> None:
        meta = extract_metadata(product_json_ld_html)
        assert len(meta["structured_data"]) >= 2  # Product + BreadcrumbList

    def test_empty_on_minimal_html(self) -> None:
        meta = extract_metadata("<html></html>")
        assert meta["title"] == ""
        assert meta["meta_description"] == ""
        assert meta["canonical_url"] == ""
        assert meta["structured_data"] == []
