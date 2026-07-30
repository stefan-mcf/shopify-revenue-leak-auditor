"""Screenshot capture for desktop and mobile viewports."""

from __future__ import annotations

import logging
from pathlib import Path

from playwright.sync_api import Page

from shopify_auditor.browser.device_profiles import MOBILE, DeviceProfile
from shopify_auditor.utils.files import ensure_dir

logger = logging.getLogger(__name__)


_SCREENSHOT_DIR = "screenshots"


def capture_screenshot(
    page: Page,
    profile: DeviceProfile,
    output_dir: str | Path,
) -> str:
    """Capture a full-page screenshot at the given profile's viewport.

    Returns the absolute path to the saved PNG.
    """
    screenshots_dir = ensure_dir(Path(output_dir) / _SCREENSHOT_DIR)
    filename = f"{profile.name}.png"
    filepath = str(screenshots_dir / filename)

    page.set_viewport_size(profile.viewport)
    page.screenshot(path=filepath, full_page=True)
    logger.info("Screenshot saved: %s (%dx%d)", filepath, profile.width, profile.height)
    return filepath


def capture_desktop_screenshot(
    page: Page,
    output_dir: str | Path,
) -> str:
    """Capture a desktop-viewport full-page screenshot."""
    from shopify_auditor.browser.device_profiles import DESKTOP

    return capture_screenshot(page, DESKTOP, output_dir)


def capture_mobile_screenshot(
    page: Page,
    output_dir: str | Path,
) -> str:
    """Capture a mobile-viewport full-page screenshot."""
    return capture_screenshot(page, MOBILE, output_dir)
