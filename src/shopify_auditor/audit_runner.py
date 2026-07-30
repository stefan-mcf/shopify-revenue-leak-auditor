"""End-to-end audit pipeline orchestration.

The runner connects URL/output prep, browser loading, extraction, checks,
scoring, JSON export, and Markdown/HTML report generation.  It is deliberately
safe-by-default: if browser loading fails, the runner saves partial output and
still returns a structured result with an error field.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from shopify_auditor.browser.page_loader import PageLoader
from shopify_auditor.checks import run_all_checks
from shopify_auditor.config import get_settings
from shopify_auditor.extraction.image_extractor import extract_images
from shopify_auditor.extraction.link_extractor import extract_links
from shopify_auditor.extraction.metadata_extractor import extract_metadata
from shopify_auditor.extraction.price_extractor import extract_prices
from shopify_auditor.extraction.product_detector import detect_product_page
from shopify_auditor.extraction.text_extractor import extract_all
from shopify_auditor.llm.analysis import LLMAnalysis
from shopify_auditor.models import (
    AuditContext,
    AuditResult,
    ExtractedPageData,
    ImageAsset,
    LinkAsset,
    PageLoadResult,
    PageLoadStatus,
    PageMetadata,
)
from shopify_auditor.reports.html import HTMLReportGenerator
from shopify_auditor.reports.markdown import MarkdownReportGenerator
from shopify_auditor.scoring.scorecard import build_scorecard
from shopify_auditor.utils.dates import utc_now_iso
from shopify_auditor.utils.files import (
    create_audit_output_dir,
    ensure_dir,
    write_json,
    write_text,
)
from shopify_auditor.utils.text import count_words
from shopify_auditor.utils.urls import get_domain, normalize_url


class AuditRunner:
    """Run a complete audit for one public URL."""

    def __init__(
        self,
        url: str,
        output_dir: str | Path = "output",
        *,
        enable_llm: bool = False,
        llm_client: Any = None,
        headless: bool | None = None,
    ) -> None:
        self.url = normalize_url(url)
        self.output_dir = Path(output_dir)
        self.enable_llm = enable_llm
        self.llm_client = llm_client
        self.headless = get_settings().browser_headless if headless is None else headless
        self.result: AuditResult | None = None
        self.findings = []
        self.llm_analysis_module = LLMAnalysis(enabled=enable_llm, llm_client=llm_client)

    def run_audit(
        self, output_dir: str | Path | None = None, *, load_browser: bool = True
    ) -> AuditResult:
        """Execute the pipeline and return an :class:`AuditResult`.

        ``load_browser=False`` is useful for deterministic tests and future
        fixture-based demos.  Normal CLI use loads the public page.
        """
        if output_dir is not None:
            self.output_dir = Path(output_dir)
        ensure_dir(self.output_dir)

        page_result = self._load_page(load_browser=load_browser)
        html = page_result.html or self._fallback_html()
        extracted = self._extract(page_result.url or self.url, html)
        context = self._build_context(page_result, extracted)
        findings = run_all_checks(context)
        scorecard = build_scorecard(findings)

        result = AuditResult(
            input_url=self.url,
            final_url=page_result.url or self.url,
            domain=get_domain(page_result.url or self.url),
            audit_timestamp=utc_now_iso(),
            screenshot_paths=page_result.screenshot_paths,
            extracted=extracted,
            findings=findings,
            scorecard=scorecard,
            output_paths={},
            error=page_result.error if page_result.status != PageLoadStatus.SUCCESS else "",
        )
        self.result = result
        self.findings = findings
        return result

    def write_outputs(self, output_dir: str | Path | None = None) -> AuditResult:
        """Generate and write audit_data.json plus Markdown/HTML reports."""
        if self.result is None:
            self.run_audit(output_dir=output_dir)
        if output_dir is not None:
            self.output_dir = Path(output_dir)
        assert self.result is not None
        ensure_dir(self.output_dir)
        reports = self.generate_reports()

        paths = {
            "audit_data_json": str(self.output_dir / "audit_data.json"),
            "markdown_report": str(self.output_dir / "audit_report.md"),
            "html_report": str(self.output_dir / "audit_report.html"),
            # Backward-compatible aliases used by early CLI tests.
            "markdown_report_alias": str(self.output_dir / "report.md"),
            "html_report_alias": str(self.output_dir / "report.html"),
        }
        self.result.output_paths = paths
        write_json(paths["audit_data_json"], self.result.model_dump(mode="json"))
        write_text(paths["markdown_report"], reports["markdown"])
        write_text(paths["html_report"], reports["html"])
        write_text(paths["markdown_report_alias"], reports["markdown"])
        write_text(paths["html_report_alias"], reports["html"])
        return self.result

    def generate_reports(self) -> dict[str, str]:
        """Return rendered Markdown and HTML reports."""
        if self.result is None:
            # Compatibility for older tests that call generate before run_audit.
            self.run_audit(load_browser=False)
        assert self.result is not None
        llm_analysis = (
            self.llm_analysis_module.analyze_findings(self.result.findings, self.result.input_url)
            if self.enable_llm
            else ""
        )
        markdown = MarkdownReportGenerator().generate_report(
            {**self._report_context(llm_analysis), "llm_analysis": llm_analysis}
        )
        html = HTMLReportGenerator().generate_report(
            {**self._report_context(llm_analysis), "llm_analysis": llm_analysis}
        )
        return {"markdown": markdown, "html": html}

    def _generate_summary(self) -> str:
        """Return a cautious executive-summary sentence for compatibility/tests."""
        if not self.findings:
            return "No significant revenue leak findings identified by the rule-based checks."
        high_or_critical = sum(1 for f in self.findings if f.severity.value in {"critical", "high"})
        return (
            f"The audit identified {len(self.findings)} potential public-page revenue leak findings, "
            f"including {high_or_critical} higher-priority issue(s) that should be human-reviewed."
        )

    def _report_context(self, llm_analysis: str = "") -> dict[str, Any]:
        from shopify_auditor.reports.markdown import report_context

        assert self.result is not None
        return report_context(self.result, llm_analysis=llm_analysis)

    def _load_page(self, *, load_browser: bool) -> PageLoadResult:
        if not load_browser:
            return PageLoadResult(
                url=self.url,
                original_url=self.url,
                status=PageLoadStatus.SUCCESS,
                status_code=200,
                title="",
                html=self._fallback_html(),
            )
        try:
            return PageLoader(headless=self.headless).load(self.url, self.output_dir)
        except Exception as exc:  # pragma: no cover - defensive, PageLoader already catches
            return PageLoadResult(
                url=self.url,
                original_url=self.url,
                status=PageLoadStatus.ERROR,
                status_code=0,
                error=str(exc),
                html=self._fallback_html(),
            )

    def _extract(self, url: str, html: str) -> ExtractedPageData:
        text_data = extract_all(html, url=url)
        meta = extract_metadata(html)
        links = extract_links(html, base_url=url)
        images = extract_images(html, base_url=url)
        prices = extract_prices(html)
        product_signals = detect_product_page(html, url=url)
        body_text = text_data.get("body_text", "")
        return ExtractedPageData(
            url=url,
            title=text_data.get("title") or meta.get("title", ""),
            meta_description=text_data.get("meta_description") or meta.get("meta_description", ""),
            canonical_url=meta.get("canonical_url", ""),
            headings=text_data.get("headings", []),
            body_text=body_text,
            buttons=text_data.get("buttons", []),
            links=links,
            images=images,
            prices=prices,
            product_signals=product_signals,
            structured_data=meta.get("structured_data", []),
            word_count=count_words(body_text),
        )

    def _build_context(self, page: PageLoadResult, extracted: ExtractedPageData) -> AuditContext:
        structured_types: list[str] = []
        for item in extracted.structured_data:
            value = item.get("@type") if isinstance(item, dict) else None
            if isinstance(value, list):
                structured_types.extend(str(v) for v in value)
            elif value:
                structured_types.append(str(value))
        price_text = ", ".join(str(p.get("raw", "")) for p in extracted.prices if p.get("raw"))
        headings = [h.get("text", "") for h in extracted.headings]
        return AuditContext(
            url=self.url,
            final_url=page.url or self.url,
            page_title=extracted.title or page.title,
            product_title=headings[0] if headings else (extracted.title or page.title),
            price_text=price_text,
            page_text=extracted.body_text,
            product_description=extracted.body_text,
            links=[
                LinkAsset(url=link.get("href", ""), text=link.get("text", ""))
                for link in extracted.links
            ],
            images=[
                ImageAsset(src=i.get("src", ""), alt=i.get("alt", "")) for i in extracted.images
            ],
            metadata=PageMetadata(
                meta_description=extracted.meta_description,
                canonical_url=extracted.canonical_url,
                structured_data_types=structured_types,
                status_code=page.status_code,
                load_succeeded=page.status == PageLoadStatus.SUCCESS,
                mobile_screenshot_path=page.screenshot_paths.get("mobile", ""),
                desktop_screenshot_path=page.screenshot_paths.get("desktop", ""),
                final_url_changed=bool(page.url and page.url != self.url),
            ),
            headings=headings,
            cta_texts=extracted.buttons,
            page=page,
            extracted=extracted,
        )

    def _fallback_html(self) -> str:
        return (
            "<html><head><title>Audit target</title></head><body>"
            f"<h1>Audit target for {self.url}</h1>"
            "<p>Public page content could not be loaded in this environment.</p>"
            "</body></html>"
        )


def run_audit(
    url: str, output_base_dir: str | Path = "output", *, enable_llm: bool = False
) -> AuditResult:
    """Convenience function used by CLI and scripts."""
    normalized = normalize_url(url)
    output_dir = create_audit_output_dir(output_base_dir, normalized)
    runner = AuditRunner(normalized, output_dir=output_dir, enable_llm=enable_llm)
    runner.run_audit()
    return runner.write_outputs(output_dir)
