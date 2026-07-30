"""Deterministic sample audit support for the CLI demo."""

from __future__ import annotations

from importlib.resources import files

from shopify_auditor.audit_runner import AuditRunner
from shopify_auditor.models import PageLoadResult, PageLoadStatus

DEMO_URL = "https://calm-home-goods.example/products/calm-desk-lamp"


class DemoAuditRunner(AuditRunner):
    """Run the normal audit pipeline against packaged fictional page data."""

    def _load_page(self, *, load_browser: bool) -> PageLoadResult:
        html = (
            files("shopify_auditor").joinpath("demo_product_page.html").read_text(encoding="utf-8")
        )
        return PageLoadResult(
            url=DEMO_URL,
            original_url=DEMO_URL,
            status=PageLoadStatus.SUCCESS,
            status_code=200,
            title="Calm Desk Lamp – Calm Home Goods",
            html=html,
        )
