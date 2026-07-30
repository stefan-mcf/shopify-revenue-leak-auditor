"""Tests for end-to-end audit runner and report generation (Tranches 16-19)."""

from __future__ import annotations

from pathlib import Path

from shopify_auditor.audit_runner import AuditRunner


PRODUCT_HTML = """
<html>
<head>
<title>Classic Leather Tote Bag – ShopExample</title>
<meta name="description" content="Handcrafted tote with free shipping and easy returns.">
<script type="application/ld+json">{"@type":"Product","name":"Classic Leather Tote Bag"}</script>
</head>
<body>
<h1>Classic Leather Tote Bag</h1>
<p>Handcrafted from full-grain leather. Perfect for work, travel, and everyday use. Includes care instructions, dimensions, warranty, secure checkout, delivery details, refunds, reviews, and support.</p>
<p class="price">$89.00</p>
<button>Add to Cart</button>
<a href="/policies/shipping-policy">Shipping</a>
<a href="/policies/refund-policy">Returns</a>
<img src="/tote-1.jpg" alt="Classic leather tote front">
<img src="/tote-2.jpg" alt="Classic leather tote side">
</body>
</html>
"""


def test_runner_can_build_result_without_browser() -> None:
    runner = AuditRunner("https://example.com/products/tote")
    result = runner.run_audit(load_browser=False)
    assert result.input_url == "https://example.com/products/tote"
    assert result.final_url == "https://example.com/products/tote"
    assert result.scorecard.overall_score <= 100
    assert isinstance(result.findings, list)


def test_runner_extracts_fixture_and_generates_reports(monkeypatch) -> None:
    runner = AuditRunner("https://example.com/products/tote", enable_llm=True, llm_client="mock")
    monkeypatch.setattr(runner, "_fallback_html", lambda: PRODUCT_HTML)
    result = runner.run_audit(load_browser=False)
    assert result.extracted.title.startswith("Classic Leather Tote")
    assert result.scorecard.overall_score <= 100

    reports = runner.generate_reports()
    assert "# Shopify Revenue Leak Audit Report" in reports["markdown"]
    assert "## Overall Score" in reports["markdown"]
    assert "## LLM Analysis (Optional)" in reports["markdown"]
    assert "Mock LLM Analysis Output" in reports["markdown"]
    assert "<html" in reports["html"]


def test_runner_writes_mvp_outputs(tmp_path: Path, monkeypatch) -> None:
    out = tmp_path / "audit"
    runner = AuditRunner("https://example.com/products/tote", output_dir=out)
    monkeypatch.setattr(runner, "_fallback_html", lambda: PRODUCT_HTML)
    runner.run_audit(load_browser=False)
    result = runner.write_outputs(out)

    assert (out / "audit_data.json").exists()
    assert (out / "audit_report.md").exists()
    assert (out / "audit_report.html").exists()
    assert (out / "report.md").exists()
    assert result.output_paths["audit_data_json"].endswith("audit_data.json")


def test_summary_generation_is_cautious() -> None:
    runner = AuditRunner("https://example.com/products/tote")
    assert "No significant" in runner._generate_summary()
    runner.run_audit(load_browser=False)
    assert "potential" in runner._generate_summary().lower()
