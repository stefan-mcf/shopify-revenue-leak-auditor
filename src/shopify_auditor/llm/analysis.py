"""Optional LLM analysis layer.

Disabled by default; failures never fail the audit.
"""

from __future__ import annotations

from typing import Any

from shopify_auditor.llm.client import LLMClient
from shopify_auditor.llm.prompts import executive_summary_prompt
from shopify_auditor.models import AuditResult, Finding


class LLMAnalysis:
    """Backward-compatible optional analyzer used by tests and the runner."""

    def __init__(self, enabled: bool = False, llm_client: Any = None) -> None:
        self.enabled = enabled
        if isinstance(llm_client, LLMClient):
            self.client = llm_client
        elif llm_client == "mock":
            self.client = None
        else:
            self.client = LLMClient.from_env(force_enable=enabled)
        self.llm_client = llm_client

    def analyze_findings(self, findings: list[Finding], shop_url: str) -> str:
        if not self.enabled:
            return "LLM analysis is disabled. Rule-based findings were used."
        if self.llm_client == "mock":
            return (
                "Mock LLM Analysis Output: Based on public page inspection, prioritize "
                "the highest-severity trust, CTA, offer clarity, and objection-handling gaps."
            )
        try:
            if self.client is None or not self.client.enabled:
                return "LLM analysis is disabled or not configured."
            return self.client.complete(
                "Summarize these public-page findings without inventing analytics:\n"
                + "\n".join(f"- {f.severity.value}: {f.title}" for f in findings[:12])
                + f"\nURL: {shop_url}"
            )
        except Exception as exc:  # pragma: no cover - defensive fallback
            return f"LLM analysis failed safely: {exc}"


class OptionalAnalyzer:
    """Tranche 19 optional analyzer facade for AuditResult enrichment."""

    def __init__(self, enabled: bool = False, client: LLMClient | None = None) -> None:
        self.enabled = enabled
        self.client = client or LLMClient.from_env(force_enable=enabled)

    def enrich_summary(self, result: AuditResult) -> str:
        if not self.enabled or not self.client.enabled:
            return ""
        try:
            return self.client.complete(executive_summary_prompt(result))
        except Exception:
            return ""
