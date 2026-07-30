"""Pydantic data models for audits, evidence, findings, and reports."""

from __future__ import annotations

from pydantic import BaseModel, Field

from shopify_auditor.models.audit import (
    AuditContext,
    AuditResult,
    ExtractedPageData,
    ImageAsset,
    LinkAsset,
    PageLoadResult,
    PageLoadStatus,
    PageMetadata,
)
from shopify_auditor.models.evidence import Evidence, EvidenceItem, EvidenceSource
from shopify_auditor.models.findings import Finding, FindingSeverity, Recommendation, Severity
from shopify_auditor.models.report import ReportMetadata, ReportOutput, ReportSection


class CategoryScore(BaseModel):
    weight: int
    penalty: int
    score: int
    findings_count: int


class Scorecard(BaseModel):
    overall_score: int
    score_label: str
    category_scores: dict[str, CategoryScore]
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    top_priorities: list[Finding] = Field(default_factory=list)


__all__ = [
    "AuditContext",
    "AuditResult",
    "ExtractedPageData",
    "ImageAsset",
    "LinkAsset",
    "PageLoadResult",
    "PageLoadStatus",
    "PageMetadata",
    "Evidence",
    "EvidenceItem",
    "EvidenceSource",
    "Finding",
    "FindingSeverity",
    "Recommendation",
    "Severity",
    "ReportMetadata",
    "ReportOutput",
    "ReportSection",
    "CategoryScore",
    "Scorecard",
]
