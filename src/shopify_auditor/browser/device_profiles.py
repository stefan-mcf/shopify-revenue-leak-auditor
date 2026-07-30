"""Device profile presets for Playwright viewport configuration."""

from __future__ import annotations

from typing import Any


class DeviceProfile:
    """A viewport / user-agent combo for a target device type."""

    def __init__(
        self,
        name: str,
        width: int,
        height: int,
        user_agent: str | None = None,
        is_mobile: bool = False,
        has_touch: bool = False,
    ) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.user_agent = user_agent
        self.is_mobile = is_mobile
        self.has_touch = has_touch

    @property
    def viewport(self) -> dict[str, int]:
        return {"width": self.width, "height": self.height}

    def to_playwright_kwargs(self) -> dict[str, Any]:
        """Return a dict suitable for ``browser.new_context(**profile.to_playwright_kwargs())``."""
        kwargs: dict[str, Any] = {
            "viewport": self.viewport,
            "is_mobile": self.is_mobile,
            "has_touch": self.has_touch,
        }
        if self.user_agent:
            kwargs["user_agent"] = self.user_agent
        return kwargs

    def __repr__(self) -> str:
        return f"DeviceProfile({self.name}, {self.width}x{self.height}, mobile={self.is_mobile})"


# --- Presets -----------------------------------------------------------------

DESKTOP = DeviceProfile(
    name="desktop",
    width=1440,
    height=1000,
    is_mobile=False,
    has_touch=False,
)

MOBILE = DeviceProfile(
    name="mobile",
    width=390,
    height=844,
    is_mobile=True,
    has_touch=True,
)

# Map for programmatic lookup
PROFILES: dict[str, DeviceProfile] = {
    "desktop": DESKTOP,
    "mobile": MOBILE,
}
