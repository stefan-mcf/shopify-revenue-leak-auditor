"""Optional local HTTP API for Shopify Revenue Leak Auditor.

The core helpers in this module are dependency-light so they can be tested without
installing the optional FastAPI service stack. Install the service mode with:

    pip install -e '.[api]'
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, Field

from shopify_auditor.audit_runner import AuditRunner
from shopify_auditor.models.audit import AuditResult
from shopify_auditor.models.findings import Finding
from shopify_auditor.utils.files import create_audit_output_dir, write_json, write_text
from shopify_auditor.utils.urls import is_valid_url, normalize_url


class AuditApiRequest(BaseModel):
    """Request body for local API audits."""

    url: str = Field(..., description="Product page URL to audit")
    output_dir: str = Field("output/api", description="Base output directory for generated artifacts")
    llm: bool = Field(False, description="Enable configured LLM analysis")
    include_report_bodies: bool = Field(
        True,
        description="Include Markdown/HTML report bodies in the JSON response as well as writing files",
    )


class AuditApiResponse(BaseModel):
    """Compact API response summarising an audit and its generated artifacts."""

    input_url: str
    final_url: str = ""
    domain: str = ""
    overall_score: int | float | None = None
    score_label: str = ""
    findings_count: int = 0
    top_findings: list[dict[str, Any]] = Field(default_factory=list)
    output_paths: dict[str, str] = Field(default_factory=dict)
    markdown_report: str | None = None
    html_report: str | None = None


def _score_value(scorecard: Any, *keys: str) -> Any:
    if isinstance(scorecard, dict):
        for key in keys:
            if key in scorecard:
                return scorecard[key]
        return None
    for key in keys:
        if hasattr(scorecard, key):
            return getattr(scorecard, key)
    return None


def _finding_summary(finding: Finding) -> dict[str, Any]:
    severity = finding.severity.value if hasattr(finding.severity, "value") else str(finding.severity)
    recommendation = finding.recommendation
    if hasattr(recommendation, "text"):
        recommendation = recommendation.text
    return {
        "id": finding.id,
        "check_id": finding.check_id,
        "category": finding.category,
        "severity": severity,
        "title": finding.title or finding.message,
        "description": finding.description,
        "recommendation": recommendation or "",
    }


def _write_api_outputs(result: AuditResult, reports: dict[str, str], out_path: Path) -> dict[str, str]:
    markdown_report_path = out_path / "audit_report.md"
    html_report_path = out_path / "audit_report.html"
    data_path = out_path / "audit_data.json"

    write_text(markdown_report_path, reports["markdown"])
    write_text(html_report_path, reports["html"])
    write_text(out_path / "report.md", reports["markdown"])
    write_text(out_path / "report.html", reports["html"])

    result.output_paths = {
        "audit_data_json": str(data_path),
        "markdown_report": str(markdown_report_path),
        "html_report": str(html_report_path),
        "markdown_report_alias": str(out_path / "report.md"),
        "html_report_alias": str(out_path / "report.html"),
    }
    write_json(data_path, result.model_dump(mode="json"))
    return result.output_paths


def run_audit_request(
    request: AuditApiRequest,
    *,
    runner_cls: Callable[..., Any] = AuditRunner,
) -> AuditApiResponse:
    """Run a local API audit request and return a compact response.

    Raises
    ------
    ValueError
        If the URL is invalid.
    RuntimeError
        If the runner fails to produce a result object.
    """

    normalized_url = normalize_url(request.url)
    if not is_valid_url(normalized_url):
        raise ValueError("Invalid URL provided.")

    out_path = create_audit_output_dir(request.output_dir, normalized_url)
    audit_runner = runner_cls(
        normalized_url,
        output_dir=out_path,
        enable_llm=request.llm,
        llm_client="mock" if request.llm else None,
    )
    result = audit_runner.run_audit()
    if result is None:
        result = getattr(audit_runner, "result", None)
    if result is None:
        raise RuntimeError("Audit runner did not produce a result.")

    reports = audit_runner.generate_reports()
    output_paths = _write_api_outputs(result, reports, out_path)

    sorted_findings = sorted(result.findings, key=lambda item: item.severity.rank)
    return AuditApiResponse(
        input_url=normalized_url,
        final_url=result.final_url,
        domain=result.domain,
        overall_score=_score_value(result.scorecard, "overall_score", "score", "total"),
        score_label=_score_value(result.scorecard, "label", "score_label") or "",
        findings_count=len(result.findings),
        top_findings=[_finding_summary(finding) for finding in sorted_findings[:5]],
        output_paths=output_paths,
        markdown_report=reports["markdown"] if request.include_report_bodies else None,
        html_report=reports["html"] if request.include_report_bodies else None,
    )


def create_app(*, runner_cls: Callable[..., Any] = AuditRunner) -> Any:
    """Create the optional FastAPI application.

    FastAPI is intentionally optional so the CLI remains lightweight. Install it
    with `pip install -e '.[api]'` before running local service mode.
    """

    try:
        from fastapi import FastAPI, HTTPException
    except Exception as exc:  # pragma: no cover - exact import failure depends on environment
        raise RuntimeError("Install API extras with: pip install -e '.[api]'") from exc

    app = FastAPI(
        title="Shopify Revenue Leak Auditor API",
        version="0.1.0",
        description="Local-only HTTP API wrapper around the Shopify audit pipeline.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/audit", response_model=AuditApiResponse)
    def audit(request: AuditApiRequest) -> AuditApiResponse:
        try:
            return run_audit_request(request, runner_cls=runner_cls)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


def main() -> None:
    """Run the optional local API with uvicorn."""

    try:
        import uvicorn
    except Exception as exc:  # pragma: no cover - depends on optional dependency
        raise RuntimeError("Install API extras with: pip install -e '.[api]'") from exc

    uvicorn.run("shopify_auditor.api:create_app", factory=True, host="127.0.0.1", port=8765)
