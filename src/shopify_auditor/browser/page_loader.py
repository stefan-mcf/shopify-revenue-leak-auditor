"""Page load orchestration: load a URL, capture HTML + metadata."""

from __future__ import annotations

import logging
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeout

from shopify_auditor.browser.device_profiles import DESKTOP
from shopify_auditor.browser.runner import BrowserRunner
from shopify_auditor.browser.screenshots import (
    capture_desktop_screenshot,
    capture_mobile_screenshot,
)
from shopify_auditor.models.audit import PageLoadResult, PageLoadStatus

logger = logging.getLogger(__name__)


class PageLoader:
    """Load a page, capture HTML/title and screenshots."""

    def __init__(
        self,
        headless: bool = True,
        page_load_timeout: int = 30_000,
        navigate_timeout: int = 60_000,
    ) -> None:
        self.headless = headless
        self.page_load_timeout = page_load_timeout
        self.navigate_timeout = navigate_timeout

    def load(
        self,
        url: str,
        output_dir: str | Path | None = None,
    ) -> PageLoadResult:
        """Load *url* and return a :class:`PageLoadResult`.

        If *output_dir* is provided, screenshots and HTML are saved there.
        """
        result = PageLoadResult(original_url=url)

        try:
            with BrowserRunner(headless=self.headless) as runner:
                # --- Desktop context ---
                context = runner.new_context(DESKTOP)
                page = context.new_page()
                page.set_default_timeout(self.page_load_timeout)

                try:
                    response = page.goto(url, timeout=self.navigate_timeout, wait_until="load")
                except PlaywrightTimeout:
                    result.status = PageLoadStatus.TIMEOUT
                    result.error = f"Page load timed out ({self.navigate_timeout}ms)"
                    context.close()
                    return result

                result.url = page.url
                result.title = page.title()
                result.status_code = response.status if response else 0

                if response and 200 <= response.status < 400:
                    result.status = PageLoadStatus.SUCCESS
                else:
                    result.status = PageLoadStatus.ERROR
                    result.error = f"HTTP {response.status if response else 'N/A'}"

                # HTML
                html = page.content()
                result.html = html

                # Screenshots
                if output_dir:
                    out = Path(output_dir)
                    try:
                        desktop_path = capture_desktop_screenshot(page, out)
                        result.screenshot_paths["desktop"] = desktop_path
                    except Exception:
                        logger.exception("Desktop screenshot failed")

                    # Mobile screenshot — switch viewport
                    try:
                        mobile_path = capture_mobile_screenshot(page, out)
                        result.screenshot_paths["mobile"] = mobile_path
                    except Exception:
                        logger.exception("Mobile screenshot failed")

                    # Save raw HTML
                    from shopify_auditor.utils.files import write_text

                    try:
                        html_path = str(out / "page.html")
                        write_text(html_path, html)
                        result.screenshot_paths["html"] = html_path
                    except Exception:
                        logger.exception("HTML save failed")

                context.close()

        except Exception as exc:
            result.status = PageLoadStatus.ERROR
            result.error = str(exc)
            logger.exception("Page load failed for %s", url)

        return result
