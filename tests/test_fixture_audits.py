"""Fixture-backed tests for audit coverage breadth.

These tests exercise realistic static product-page fixtures rather than only
inline snippets, so future detector/check/report changes have stable examples
for good, weak, missing-FAQ, and no-CTA pages.
"""

from __future__ import annotations

from pathlib import Path

from shopify_auditor.audit_runner import AuditRunner
from shopify_auditor.extraction.link_extractor import classify_link

FIXTURE_DIR = Path(__file__).parent / "fixtures"
REQUIRED_FIXTURES = [
    "product_good.html",
    "product_weak.html",
    "product_missing_faq.html",
    "product_no_cta.html",
]


def read_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def run_fixture(name: str):
    runner = AuditRunner(
        f"https://example.com/products/{name.removesuffix('.html').replace('_', '-')}"
    )
    runner._fallback_html = lambda: read_fixture(name)  # type: ignore[method-assign]
    return runner, runner.run_audit(load_browser=False)


def test_required_html_fixtures_exist_and_are_non_empty() -> None:
    for fixture_name in REQUIRED_FIXTURES:
        path = FIXTURE_DIR / fixture_name
        assert path.exists(), f"missing fixture: {fixture_name}"
        content = path.read_text(encoding="utf-8")
        assert "<html" in content.lower()
        assert "</html>" in content.lower()
        assert len(content) > 500


def test_good_product_fixture_extracts_core_commerce_signals() -> None:
    _runner, result = run_fixture("product_good.html")

    assert result.extracted.title.startswith("TrailPack Pro")
    assert result.extracted.meta_description
    assert result.extracted.prices
    assert result.extracted.product_signals["is_product_page"] is True
    link_labels = {label for link in result.extracted.links for label in classify_link(link)}
    assert "shipping" in link_labels
    assert "faq" in link_labels
    assert any(img["alt"] for img in result.extracted.images)


def test_weak_fixture_scores_lower_than_good_fixture() -> None:
    _good_runner, good = run_fixture("product_good.html")
    _weak_runner, weak = run_fixture("product_weak.html")

    assert weak.scorecard.overall_score < good.scorecard.overall_score
    assert len(weak.findings) > len(good.findings)
    weak_messages = " ".join(f.message.lower() for f in weak.findings)
    assert "price" in weak_messages
    assert "shipping" in weak_messages or "delivery" in weak_messages


def test_missing_faq_fixture_surfaces_objection_handling_gap() -> None:
    _runner, result = run_fixture("product_missing_faq.html")

    faq_findings = [f for f in result.findings if f.category == "faq_objections"]
    assert faq_findings
    assert any(f.suggested_questions for f in faq_findings)
    assert any("faq" in f.message.lower() or "objection" in f.message.lower() for f in faq_findings)


def test_no_cta_fixture_surfaces_purchase_path_gap() -> None:
    _runner, result = run_fixture("product_no_cta.html")

    cta_findings = [f for f in result.findings if f.category == "cta_quality"]
    assert cta_findings
    assert any(f.severity.value in {"critical", "high"} for f in cta_findings)
    assert any("cta" in f.message.lower() or "purchase" in f.message.lower() for f in cta_findings)


def test_fixture_reports_contain_required_client_sections() -> None:
    runner, _result = run_fixture("product_weak.html")
    reports = runner.generate_reports()

    markdown = reports["markdown"]
    html = reports["html"]
    for required in [
        "Executive Summary",
        "Overall Score",
        "Category Scorecard",
        "Top Revenue Leak Findings",
        "Detailed Findings by Category",
        "7-Day Implementation Checklist",
        "Limitations",
    ]:
        assert required in markdown
        assert required in html

    assert "does not guarantee revenue" in markdown.lower()
    assert "human-reviewed" in markdown.lower()
