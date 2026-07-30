"""Tests for file utilities (Tranche 3)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from shopify_auditor.utils.files import (
    create_audit_output_dir,
    ensure_dir,
    safe_filename,
    write_json,
    write_text,
)


class TestEnsureDir:
    def test_creates_directory(self, tmp_path: Path) -> None:
        d = tmp_path / "a" / "b"
        assert not d.exists()
        result = ensure_dir(d)
        assert d.exists()
        assert result == d

    def test_idempotent(self, tmp_path: Path) -> None:
        d = tmp_path / "sub"
        ensure_dir(d)
        result = ensure_dir(d)
        assert d.exists()
        assert result == d


class TestWriteText:
    def test_writes_file(self, tmp_path: Path) -> None:
        p = tmp_path / "nested" / "hello.txt"
        written = write_text(p, "Hello, world!")
        assert p.read_text(encoding="utf-8") == "Hello, world!"
        assert written == p


class TestWriteJson:
    def test_writes_pretty_json(self, tmp_path: Path) -> None:
        p = tmp_path / "data.json"
        written = write_json(p, {"a": 1, "b": [2, 3]})
        content = p.read_text(encoding="utf-8")
        parsed = json.loads(content)
        assert parsed == {"a": 1, "b": [2, 3]}
        assert written == p


class TestSafeFilename:
    def test_basic_sanitise(self) -> None:
        assert safe_filename("Hello World!") == "Hello-World"

    def test_collapse_hyphens(self) -> None:
        assert safe_filename("a---b") == "a-b"

    def test_all_unsafe(self) -> None:
        assert safe_filename("???***") == ""

    def test_truncation(self) -> None:
        long_name = "a" * 100
        result = safe_filename(long_name, max_len=10)
        assert len(result) == 10

    def test_preserves_dots_and_extensions(self) -> None:
        assert safe_filename("hello.world.txt") == "hello.world.txt"


class TestCreateAuditOutputDir:
    def test_creates_deterministic_dir(self, tmp_path: Path) -> None:
        url = "https://shopexample.com/products/leather-bag"
        out = create_audit_output_dir(tmp_path, url)
        assert out.exists()
        assert "shopexample" in out.name
        assert "leather" in out.name

    def test_same_url_gives_same_dir(self, tmp_path: Path) -> None:
        url = "https://shopexample.com/products/leather-bag"
        out1 = create_audit_output_dir(tmp_path, url)
        out2 = create_audit_output_dir(tmp_path, url)
        assert out1 == out2
