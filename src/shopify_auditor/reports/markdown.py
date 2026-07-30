"""Markdown report generation for client-ready audit outputs."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from shopify_auditor.models import AuditResult, Finding

CATEGORY_LABELS = {
    "trust_signals": "Trust Signals",
    "copy_quality": "Copy Quality",
    "offer_clarity": "Offer Clarity",
    "faq_objections": "FAQ and Objection Handling",
    "cta_quality": "CTA Quality",
    "mobile_ux": "Mobile UX",
    "product_information": "Product Information",
    "ai_readiness": "AI-Shopping Readiness",
    "technical_health": "Technical Health",
}


class MarkdownReportGenerator:
    def __init__(self) -> None:
        template_dir = Path(__file__).with_name("templates")
        self.env = Environment(
            loader=FileSystemLoader(template_dir), autoescape=select_autoescape([])
        )
        self.template = self.env.get_template("markdown_report.md")

    def generate_report(self, data: dict[str, Any] | AuditResult) -> str:
        if isinstance(data, AuditResult):
            data = report_context(data)
        return self.template.render(**data)


def report_context(result: AuditResult, llm_analysis: str = "") -> dict[str, Any]:
    by_category: dict[str, list[Finding]] = defaultdict(list)
    for finding in result.findings:
        by_category[finding.category].append(finding)
    scorecard = result.scorecard
    category_scores = []
    for key, label in CATEGORY_LABELS.items():
        cs = getattr(scorecard, "category_scores", {}).get(key) if scorecard else None
        category_scores.append(
            {
                "key": key,
                "label": label,
                "score": getattr(cs, "score", 0) if cs else 0,
                "weight": getattr(cs, "weight", 0) if cs else 0,
                "count": len(by_category.get(key, [])),
            }
        )
    top_findings = sorted(result.findings, key=lambda f: (f.severity.rank, -f.confidence))[:10]
    return {
        "result": result,
        "scorecard": scorecard,
        "overall_score": getattr(scorecard, "overall_score", 0) if scorecard else 0,
        "score_label": getattr(scorecard, "score_label", "Not scored")
        if scorecard
        else "Not scored",
        "category_scores": category_scores,
        "category_labels": CATEGORY_LABELS,
        "findings_by_category": {k: by_category.get(k, []) for k in CATEGORY_LABELS},
        "top_findings": top_findings,
        "llm_analysis": llm_analysis,
    }
