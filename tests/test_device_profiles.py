"""Tests for browser device profiles (Tranche 4)."""

from __future__ import annotations

from shopify_auditor.browser.device_profiles import (
    DESKTOP,
    MOBILE,
    PROFILES,
    DeviceProfile,
)


class TestDeviceProfile:
    def test_desktop_viewport(self) -> None:
        assert DESKTOP.viewport == {"width": 1440, "height": 1000}
        assert DESKTOP.name == "desktop"
        assert DESKTOP.is_mobile is False

    def test_mobile_viewport(self) -> None:
        assert MOBILE.viewport == {"width": 390, "height": 844}
        assert MOBILE.name == "mobile"
        assert MOBILE.is_mobile is True

    def test_to_playwright_kwargs(self) -> None:
        kwargs = DESKTOP.to_playwright_kwargs()
        assert kwargs["viewport"] == {"width": 1440, "height": 1000}
        assert kwargs["is_mobile"] is False

    def test_profiles_map(self) -> None:
        assert "desktop" in PROFILES
        assert "mobile" in PROFILES
        assert PROFILES["desktop"] is DESKTOP
        assert PROFILES["mobile"] is MOBILE

    def test_custom_profile(self) -> None:
        p = DeviceProfile("tablet", width=768, height=1024)
        assert p.name == "tablet"
        assert p.viewport == {"width": 768, "height": 1024}
