"""HTML report generation for client review and delivery."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from shopify_auditor.models import AuditResult
from shopify_auditor.reports.markdown import report_context


class HTMLReportGenerator:
    def __init__(self) -> None:
        template_dir = Path(__file__).with_name("templates")
        self.env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape(["html", "xml"]))
        self.template = self.env.get_template("html_report.html")

    def generate_report(self, data: dict[str, Any] | AuditResult) -> str:
        if isinstance(data, AuditResult):
            data = report_context(data)
        return self.template.render(**data)
