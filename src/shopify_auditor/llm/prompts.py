"""Prompt builders for optional LLM-assisted report wording."""

from __future__ import annotations

from shopify_auditor.models import AuditResult, Finding

_GUARDRAIL = (
    "Use only public-page evidence. Do not invent analytics, conversion rates, "
    "revenue impact, ad performance, or private Shopify data. Prefer cautious "
    "phrasing such as likely issue, potential risk, consider testing."
)


def executive_summary_prompt(result: AuditResult) -> str:
    return (
        f"Summarize this Shopify public-page audit for {result.final_url or result.input_url}.\n"
        f"Overall score: {getattr(result.scorecard, 'overall_score', 'unknown')}.\n"
        f"Findings: {len(result.findings)}.\n{_GUARDRAIL}"
    )


def finding_refinement_prompt(finding: Finding) -> str:
    return (
        "Rewrite this finding in professional, cautious client-facing language.\n"
        f"Severity: {finding.severity.value}\nTitle: {finding.title}\n"
        f"Description: {finding.description}\nRecommendation: {finding.recommendation}\n{_GUARDRAIL}"
    )


def implementation_checklist_prompt(result: AuditResult) -> str:
    return (
        "Create a 7-day implementation checklist based only on these audit findings.\n"
        + "\n".join(f"- {f.severity.value}: {f.title}" for f in result.findings[:10])
        + f"\n{_GUARDRAIL}"
    )


def faq_suggestion_prompt(result: AuditResult) -> str:
    return "Suggest FAQ questions that answer common ecommerce objections. " + _GUARDRAIL


def ad_hook_prompt(result: AuditResult) -> str:
    return "Suggest cautious ad-hook angles aligned to page evidence only. " + _GUARDRAIL
