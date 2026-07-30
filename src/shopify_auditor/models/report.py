"""Report models — metadata, sections, and final report output."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ReportMetadata(BaseModel):
    """Metadata embedded in every audit report."""

    tool_name: str = "shopify-revenue-leak-auditor"
    tool_version: str = Field(default="0.1.0")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )
    url: str = Field("", description="Audited URL")
    domain: str = Field("", description="Domain audited")


class ReportSection(BaseModel):
    """A single section within the report."""

    title: str = Field(..., description="Section heading")
    content: str = Field("", description="Markdown/HTML body text")
    findings_count: int = Field(0)
    score: float | None = Field(None, description="Section score if applicable")


class ReportOutput(BaseModel):
    """The full report output for writing to a file."""

    metadata: ReportMetadata = Field(default_factory=ReportMetadata)
    sections: list[ReportSection] = Field(default_factory=list)
    summary: str = Field("", description="Executive summary")
    overall_score: float | None = Field(None, ge=0.0, le=100.0)
    markdown_path: str = Field("", description="Path to the written .md file")
    html_path: str = Field("", description="Path to the written .html file")
