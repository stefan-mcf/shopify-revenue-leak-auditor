"""Evidence models — atomic data points extracted from a page."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EvidenceSource(str, Enum):
    """Where the evidence was found on the page."""

    HTML = "html"
    TEXT = "text"
    META = "meta"
    LINK = "link"
    IMAGE = "image"
    STRUCTURED_DATA = "structured_data"
    SCREENSHOT = "screenshot"
    PRICE = "price"
    PRODUCT_SIGNAL = "product_signal"
    BROWSER = "browser"
    UNKNOWN = "unknown"


class Evidence(BaseModel):
    """Compact evidence object used by rule checks."""

    summary: str = ""
    snippets: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    """A single piece of extracted evidence."""

    id: str = Field(default="", description="Unique id within the audit")
    category: str = Field(default="", description="E.g. trust-signals, copy-quality")
    label: str = Field(default="", description="Short human-readable label")
    value: Any = Field(None, description="The extracted value (string, list, dict…)")
    source: EvidenceSource = EvidenceSource.UNKNOWN
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence 0-1")
    raw_text: str = Field(default="", description="Raw text snippet from the page")
    url: str = Field(default="", description="The page URL this evidence came from")
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    model_config = {"frozen": False, "extra": "ignore"}
