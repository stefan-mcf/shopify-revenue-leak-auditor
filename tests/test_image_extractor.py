"""Tests for image extraction."""

from __future__ import annotations

from shopify_auditor.extraction.image_extractor import (
    count_missing_alt,
    extract_images,
    likely_product_images,
)


class TestExtractImages:
    def test_extracts_all_images(self, shopify_product_html: str) -> None:
        images = extract_images(shopify_product_html)
        # We have 3 images: tote-1, tote-2, icon-shipping
        assert len(images) == 3

    def test_each_has_src_and_alt(self, shopify_product_html: str) -> None:
        images = extract_images(shopify_product_html)
        for img in images:
            assert "src" in img
            assert "alt" in img


class TestCountMissingAlt:
    def test_counts_empty_alt(self, shopify_product_html: str) -> None:
        images = extract_images(shopify_product_html)
        # tote-2 has empty alt, icon-shipping has alt text
        missing = count_missing_alt(images)
        assert missing == 1


class TestLikelyProductImages:
    def test_filters_icons(self, shopify_product_html: str) -> None:
        images = extract_images(shopify_product_html)
        product_imgs = likely_product_images(images)
        # icon-shipping should be filtered out, leaving 2 product images
        assert len(product_imgs) == 2

    def test_preserves_product_photos(self, shopify_product_html: str) -> None:
        images = extract_images(shopify_product_html)
        product_imgs = likely_product_images(images)
        srcs = [i["src"] for i in product_imgs]
        assert "//shopexample.com/img/tote-1.jpg" in srcs
