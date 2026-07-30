"""Playwright browser lifecycle management."""

from __future__ import annotations

import logging
from typing import Any

from playwright.sync_api import Browser, BrowserContext, Playwright, sync_playwright

from shopify_auditor.browser.device_profiles import DeviceProfile

logger = logging.getLogger(__name__)


class BrowserRunner:
    """Manages Playwright browser lifecycle.

    Usage (context-manager)::

        with BrowserRunner(headless=True) as browser:
            page = browser.new_page(DeviceProfile(...))
            page.goto("https://example.com")
    """

    def __init__(
        self,
        headless: bool = True,
        launch_args: list[str] | None = None,
    ) -> None:
        self.headless = headless
        self.launch_args = launch_args or [
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ]
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> BrowserRunner:
        self.start()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start Playwright and launch the browser."""
        logger.info("Starting Playwright (headless=%s)", self.headless)
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=self.headless,
            args=self.launch_args,
        )
        logger.info("Browser launched.")

    def new_context(self, profile: DeviceProfile | None = None) -> BrowserContext:
        """Create a new browser context, optionally with a device profile."""
        if self._browser is None:
            raise RuntimeError("Browser not started. Call start() first.")

        kwargs: dict[str, Any] = {}
        if profile:
            kwargs.update(profile.to_playwright_kwargs())
        return self._browser.new_context(**kwargs)

    def close(self) -> None:
        """Close browser and stop Playwright."""
        if self._browser:
            try:
                self._browser.close()
            except Exception:
                logger.exception("Error closing browser")
            self._browser = None
        if self._playwright:
            try:
                self._playwright.stop()
            except Exception:
                logger.exception("Error stopping Playwright")
            self._playwright = None
        logger.info("Browser resources released.")
