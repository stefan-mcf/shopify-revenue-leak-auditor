"""Finding and Recommendation models."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from shopify_auditor.models.evidence import Evidence, EvidenceItem


class Severity(str, Enum):
    """Severity of a finding."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    @property
    def rank(self) -> int:
        order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        return order[self]


FindingSeverity = Severity


class Recommendation(BaseModel):
    """A suggested action to address a finding."""

    text: str = Field(..., description="Human-readable recommendation")
    effort: str = Field(default="medium", description="Estimated effort: low / medium / high")
    impact: str = Field(default="medium", description="Estimated impact: low / medium / high")
    category: str = Field(default="", description="Category this belongs to")

    model_config = {"frozen": False}


class Finding(BaseModel):
    """A single audit finding with evidence, severity, and recommendation."""

    id: str = Field(default="", description="Unique finding id")
    check_id: str = Field(default="", description="Check id that emitted this finding")
    category: str = Field(..., description="Audit category the finding belongs to")
    severity: Severity = Field(..., description="How severe this issue is")
    title: str = Field(default="", description="Short issue title")
    message: str = Field(default="", description="Short issue message")
    description: str = Field(default="", description="Detailed description of the finding")
    evidence: list[EvidenceItem] | Evidence | None = Field(default_factory=list)
    recommendation: str | Recommendation | None = Field(default=None, description="Suggested fix")
    priority: int = Field(default=0, ge=0, description="Sort priority (higher = more urgent)")
    confidence: float = Field(default=0.7, ge=0.0, le=1.0, description="Confidence in this finding 0-1")
    suggested_questions: list[str] = Field(default_factory=list)

    model_config = {"frozen": False, "extra": "ignore"}

    @model_validator(mode="after")
    def fill_text_fields(self) -> "Finding":
        if not self.title and self.message:
            self.title = self.message
        if not self.message and self.title:
            self.message = self.title
        if not self.description:
            self.description = self.message or self.title
        return self
