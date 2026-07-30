"""Tests for date utilities (Tranche 3)."""

from __future__ import annotations

import re

from shopify_auditor.utils.dates import timestamp_for_folder, utc_now_iso


class TestUtcNowIso:
    def test_returns_iso_format(self) -> None:
        result = utc_now_iso()
        # ISO-8601 pattern: 2025-03-21T14:30:15.123456+00:00
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", result)


class TestTimestampForFolder:
    def test_returns_compact_format(self) -> None:
        result = timestamp_for_folder()
        # YYYYMMDD_HHMMSS
        assert re.match(r"\d{8}_\d{6}", result)
