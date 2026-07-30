"""Core audit models: page load, extracted data, audit context and result."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from shopify_auditor.models.findings import Finding


class PageLoadStatus(str, Enum):
    """Status of a page load attempt."""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


class PageLoadResult(BaseModel):
    """Result from loading a page via the browser."""

    url: str = Field("", description="Final URL after redirects")
    original_url: str = Field("", description="The URL originally requested")
    status: PageLoadStatus = PageLoadStatus.ERROR
    status_code: int = Field(0, description="HTTP status code")
    title: str = Field("", description="Page <title>")
    html: str = Field("", description="Raw page HTML")
    error: str = Field("", description="Error message if load failed")
    screenshot_paths: dict[str, str] = Field(default_factory=dict)

    model_config = {"frozen": False, "extra": "ignore"}

    @property
    def success(self) -> bool:
        return self.status == PageLoadStatus.SUCCESS


class LinkAsset(BaseModel):
    url: str = ""
    text: str = ""


class ImageAsset(BaseModel):
    src: str = ""
    alt: str = ""
    broken: bool = False


class PageMetadata(BaseModel):
    meta_description: str = ""
    canonical_url: str = ""
    structured_data_types: list[str] = Field(default_factory=list)
    status_code: int | None = None
    load_succeeded: bool = True
    mobile_screenshot_path: str = ""
    desktop_screenshot_path: str = ""
    final_url_changed: bool = False


class ExtractedPageData(BaseModel):
    """Structured data extracted from a loaded page."""

    url: str = Field("", description="Page URL extraction targeted")
    title: str = Field("", description="Page <title>")
    meta_description: str = Field("", description="Meta description if present")
    canonical_url: str = Field("", description="Canonical URL if present")
    headings: list[dict[str, str]] = Field(default_factory=list)
    body_text: str = Field("", description="Visible body text")
    buttons: list[str] = Field(default_factory=list)
    links: list[dict[str, str]] = Field(default_factory=list)
    images: list[dict[str, Any]] = Field(default_factory=list)
    prices: list[dict[str, Any]] = Field(default_factory=list)
    product_signals: dict[str, Any] = Field(default_factory=dict)
    structured_data: list[dict[str, Any]] = Field(default_factory=list)
    word_count: int = Field(0, description="Approximate word count of body_text")

    model_config = {"frozen": False, "extra": "ignore"}


class AuditContext(BaseModel):
    """Full input context for running all checks."""

    url: str = Field("", description="Audited URL")
    final_url: str = ""
    page_title: str = ""
    product_title: str = ""
    price_text: str = ""
    page_text: str = ""
    product_description: str = ""
    links: list[LinkAsset] = Field(default_factory=list)
    images: list[ImageAsset] = Field(default_factory=list)
    metadata: PageMetadata = Field(default_factory=PageMetadata)
    headings: list[str] = Field(default_factory=list)
    cta_texts: list[str] = Field(default_factory=list)
    page: PageLoadResult | None = None
    extracted: ExtractedPageData | None = None

    model_config = {"frozen": False, "extra": "ignore"}

    def combined_text(self) -> str:
        return "\n".join(
            part
            for part in [
                self.page_title,
                self.product_title,
                self.page_text,
                self.product_description,
                *self.headings,
                *self.cta_texts,
            ]
            if part
        )


class AuditResult(BaseModel):
    """Complete audit result for a single URL."""

    input_url: str = Field("", description="Original URL passed to the CLI")
    final_url: str = Field("", description="Final URL after page load")
    domain: str = Field("", description="Extracted domain")
    audit_timestamp: str = Field("", description="UTC ISO-8601 timestamp")
    screenshot_paths: dict[str, str] = Field(default_factory=dict)
    extracted: ExtractedPageData | None = None
    findings: list[Finding] = Field(default_factory=list)
    scorecard: Any = Field(default_factory=dict)
    output_paths: dict[str, str] = Field(default_factory=dict)
    error: str = Field("", description="Top-level error if the audit failed")

    model_config = {"frozen": False, "extra": "ignore"}
