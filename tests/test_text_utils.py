"""Tests for text utilities (Tranche 3)."""

from __future__ import annotations

import pytest

from shopify_auditor.utils.text import clean_whitespace, contains_any, count_words, truncate


class TestCleanWhitespace:
    def test_collapses_spaces(self) -> None:
        assert clean_whitespace("  hello   world  ") == "hello world"

    def test_collapses_newlines(self) -> None:
        assert clean_whitespace("line1\nline2\n\nline3") == "line1 line2 line3"

    def test_empty_string(self) -> None:
        assert clean_whitespace("") == ""


class TestTruncate:
    def test_no_truncation_needed(self) -> None:
        assert truncate("short", 20) == "short"

    def test_truncates(self) -> None:
        result = truncate("a" * 100, max_chars=10)
        assert result.endswith("...")
        assert len(result) == 13  # 10 chars + "..."

    def test_exact_boundary(self) -> None:
        text = "hello world"
        assert truncate(text, 11) == text


class TestContainsAny:
    def test_finds_term(self) -> None:
        assert contains_any("Free Shipping Worldwide", ["shipping", "free"]) is True

    def test_case_insensitive(self) -> None:
        assert contains_any("FREE SHIPPING", ["free"]) is True

    def test_no_match(self) -> None:
        assert contains_any("Hello World", ["goodbye"]) is False


class TestCountWords:
    def test_basic(self) -> None:
        assert count_words("one two three") == 3

    def test_empty(self) -> None:
        assert count_words("") == 0

    def test_extra_whitespace(self) -> None:
        assert count_words("   one   two   ") == 2
