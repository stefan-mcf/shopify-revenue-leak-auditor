"""Browser automation: runner, profiles, screenshots, page loader."""

from shopify_auditor.browser.device_profiles import (
    DESKTOP,
    MOBILE,
    PROFILES,
    DeviceProfile,
)
from shopify_auditor.browser.page_loader import PageLoader
from shopify_auditor.browser.runner import BrowserRunner
from shopify_auditor.browser.screenshots import (
    capture_desktop_screenshot,
    capture_mobile_screenshot,
    capture_screenshot,
)

__all__ = [
    "DESKTOP",
    "MOBILE",
    "PROFILES",
    "BrowserRunner",
    "DeviceProfile",
    "PageLoader",
    "capture_desktop_screenshot",
    "capture_mobile_screenshot",
    "capture_screenshot",
]
