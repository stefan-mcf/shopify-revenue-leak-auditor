"""Tests for optional local API service helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import pytest

from shopify_auditor.api import AuditApiRequest, create_app, run_audit_request
from shopify_auditor.models.audit import AuditResult
from shopify_auditor.models.findings import Finding, FindingSeverity


@dataclass
class StubAuditRunner:
    url: str
    output_dir: Path
    enable_llm: bool = False
    llm_client: object | None = None

    def __post_init__(self) -> None:
        self.result = AuditResult(
            input_url=self.url,
            final_url=self.url,
            domain="example.com",
            scorecard={"overall_score": 82, "label": "Good"},
            findings=[
                Finding(
                    check_id="trust_001",
                    category="Trust & Proof",
                    severity=FindingSeverity.HIGH,
                    title="Missing reviews",
                    description="No review evidence was found.",
                    recommendation="Add reviews near the buy button.",
                )
            ],
        )

    def run_audit(self) -> AuditResult:
        return self.result

    def generate_reports(self) -> dict[str, str]:
        return {
            "markdown": "# Audit Report\n\nTop finding: Missing reviews.",
            "html": "<html><body>Audit Report</body></html>",
        }


def test_run_audit_request_validates_url() -> None:
    request = AuditApiRequest(url="not-a-url")

    with pytest.raises(ValueError, match="Invalid URL"):
        run_audit_request(request, runner_cls=StubAuditRunner)


def test_run_audit_request_writes_reports_and_returns_summary(tmp_path: Path) -> None:
    request = AuditApiRequest(url="example.com/products/widget", output_dir=str(tmp_path), llm=True)

    response = run_audit_request(request, runner_cls=StubAuditRunner)

    assert response.input_url == "https://example.com/products/widget"
    assert response.overall_score == 82
    assert response.score_label == "Good"
    assert response.findings_count == 1
    assert response.top_findings[0]["title"] == "Missing reviews"
    assert Path(response.output_paths["audit_data_json"]).exists()
    assert Path(response.output_paths["markdown_report"]).exists()
    assert Path(response.output_paths["html_report"]).exists()
    assert "Top finding" in response.markdown_report
    assert "Audit Report" in response.html_report


def test_run_audit_request_can_omit_report_bodies(tmp_path: Path) -> None:
    request = AuditApiRequest(
        url="https://example.com/products/widget",
        output_dir=str(tmp_path),
        include_report_bodies=False,
    )

    response = run_audit_request(request, runner_cls=StubAuditRunner)

    assert response.markdown_report is None
    assert response.html_report is None
    assert Path(response.output_paths["markdown_report"]).exists()


def test_create_app_explains_missing_optional_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "fastapi", None)

    with pytest.raises(RuntimeError, match="Install API extras"):
        create_app(runner_cls=StubAuditRunner)
