"""Reusable check framework."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

from shopify_auditor.models import AuditContext, Evidence, Finding, FindingSeverity


@dataclass(slots=True)
class BaseCheck(ABC):
    check_id: str
    category: str
    weight: int

    @abstractmethod
    def run(self, context: AuditContext) -> list[Finding]:
        raise NotImplementedError

    def finding(
        self,
        severity: FindingSeverity,
        message: str,
        recommendation: str,
        *,
        confidence: float = 0.8,
        evidence: Evidence | None = None,
        suggested_questions: list[str] | None = None,
    ) -> Finding:
        return Finding(
            check_id=self.check_id,
            category=self.category,
            severity=severity,
            message=message,
            recommendation=recommendation,
            confidence=confidence,
            evidence=evidence,
            suggested_questions=suggested_questions or [],
        )

    def has_terms(self, text: str, terms: list[str]) -> bool:
        haystack = text.lower()
        return any(term.lower() in haystack for term in terms)

    def count_terms(self, text: str, terms: list[str]) -> int:
        haystack = text.lower()
        return sum(1 for term in terms if term.lower() in haystack)

    def has_link_matching(self, context: AuditContext, patterns: list[str]) -> bool:
        for link in context.links:
            combined = f"{link.text} {link.url}".lower()
            if any(pattern.lower() in combined for pattern in patterns):
                return True
        return False

    def evidence_from_text(self, text: str, terms: list[str], summary: str) -> Evidence | None:
        snippets: list[str] = []
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            if any(term.lower() in sentence.lower() for term in terms):
                snippets.append(sentence.strip())
            if len(snippets) == 3:
                break
        return Evidence(summary=summary, snippets=snippets) if snippets else None

    def severity_from_condition(
        self,
        *,
        missing: bool,
        weak: bool = False,
        critical: bool = False,
    ) -> FindingSeverity:
        if critical and missing:
            return FindingSeverity.CRITICAL
        if missing:
            return FindingSeverity.HIGH
        if weak:
            return FindingSeverity.MEDIUM
        return FindingSeverity.INFO
