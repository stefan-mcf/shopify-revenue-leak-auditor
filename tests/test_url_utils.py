"""Tests for URL utilities."""

from __future__ import annotations

import pytest

from shopify_auditor.utils.urls import (
    get_domain,
    infer_slug_from_url,
    is_likely_product_url,
    is_valid_url,
    normalize_url,
)


class TestNormalizeUrl:
    def test_basic(self) -> None:
        assert normalize_url("HTTP://Example.COM/Path/") == "http://example.com/path"

    def test_preserves_local_http_server(self) -> None:
        assert normalize_url("http://localhost:8765/products/test") == (
            "http://localhost:8765/products/test"
        )

    def test_strips_fragment(self) -> None:
        assert normalize_url("https://example.com/page#section") == "https://example.com/page"

    def test_strips_trailing_slash(self) -> None:
        assert normalize_url("https://example.com/page/") == "https://example.com/page"

    def test_adds_https(self) -> None:
        assert normalize_url("example.com") == "https://example.com"

    def test_strips_whitespace(self) -> None:
        assert normalize_url("  https://example.com  ") == "https://example.com"

    def test_keeps_query_string(self) -> None:
        assert normalize_url("https://example.com/page?q=1") == "https://example.com/page?q=1"


class TestIsValidUrl:
    @pytest.mark.parametrize(
        "url, expected",
        [
            ("https://example.com", True),
            ("http://shop.myshopify.com/products/item", True),
            ("not-a-url", False),
            ("", False),
            ("ftp://example.com", False),
        ],
    )
    def test_validation(self, url: str, expected: bool) -> None:
        assert is_valid_url(url) is expected


class TestGetDomain:
    def test_standard(self) -> None:
        assert get_domain("https://shop.example.com/products/item") == "shop.example.com"

    def test_with_port(self) -> None:
        assert get_domain("https://example.com:8080/path") == "example.com:8080"

    def test_empty_on_garbage(self) -> None:
        assert get_domain("") == ""


class TestInferSlugFromUrl:
    def test_product_path(self) -> None:
        slug = infer_slug_from_url("https://example.com/products/leather-tote")
        assert "leather-tote" in slug

    def test_deep_path_gets_last(self) -> None:
        slug = infer_slug_from_url("https://example.com/collections/bags/products/duffel")
        assert "duffel" in slug

    def test_sanitised_domain_fallback(self) -> None:
        slug = infer_slug_from_url("https://example.com")
        assert "example" in slug


class TestIsLikelyProductUrl:
    @pytest.mark.parametrize(
        "url, expected",
        [
            ("https://example.com/products/leather-tote", True),
            ("https://example.com/products/123", True),
            ("https://example.com/product/my-item", True),
            ("https://example.com/about", False),
            ("https://example.com/pages/contact", False),
            ("https://example.com/item/SKU123", True),
        ],
    )
    def test_detection(self, url: str, expected: bool) -> None:
        assert is_likely_product_url(url) is expected
