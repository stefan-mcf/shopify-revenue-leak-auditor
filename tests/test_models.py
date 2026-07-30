"""Tests for Pydantic data models."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from shopify_auditor.models.audit import (
    AuditResult,
    ExtractedPageData,
    PageLoadResult,
    PageLoadStatus,
)
from shopify_auditor.models.evidence import EvidenceItem, EvidenceSource
from shopify_auditor.models.findings import Finding, Severity
from shopify_auditor.models.report import ReportMetadata, ReportOutput, ReportSection


class TestEvidenceItem:
    def test_minimal_creation(self) -> None:
        item = EvidenceItem(label="Test evidence")
        assert item.label == "Test evidence"
        assert item.source == EvidenceSource.UNKNOWN
        assert item.confidence == 0.5

    def test_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            EvidenceItem(label="bad", confidence=-0.1)
        with pytest.raises(ValidationError):
            EvidenceItem(label="bad", confidence=1.5)

    def test_serialisation(self) -> None:
        item = EvidenceItem(label="Price", value=19.99, source=EvidenceSource.PRICE)
        d = item.model_dump()
        assert d["label"] == "Price"
        assert d["value"] == 19.99
        assert d["source"] == "price"


class TestFinding:
    def test_minimal_creation(self) -> None:
        f = Finding(category="trust-signals", severity=Severity.HIGH, title="No shipping info")
        assert f.severity == Severity.HIGH
        assert f.priority == 0
        assert f.confidence == 0.7

    def test_required_fields(self) -> None:
        with pytest.raises(ValidationError):
            Finding()  # missing category, severity, title

    def test_with_evidence(self) -> None:
        ev = EvidenceItem(label="test")
        f = Finding(
            category="copy-quality",
            severity=Severity.MEDIUM,
            title="Short description",
            evidence=[ev],
        )
        assert len(f.evidence) == 1
        assert f.evidence[0].label == "test"

    def test_invalid_severity(self) -> None:
        with pytest.raises(ValidationError):
            Finding(category="x", severity="invalid", title="x")  # type: ignore[arg-type]


class TestPageLoadResult:
    def test_success_property(self) -> None:
        r = PageLoadResult(url="https://example.com", status=PageLoadStatus.SUCCESS)
        assert r.success is True

    def test_error_property(self) -> None:
        r = PageLoadResult(status=PageLoadStatus.ERROR)
        assert r.success is False


class TestExtractedPageData:
    def test_defaults(self) -> None:
        d = ExtractedPageData()
        assert d.body_text == ""
        assert d.word_count == 0
        assert d.headings == []

    def test_with_data(self) -> None:
        d = ExtractedPageData(
            url="https://example.com",
            title="Test Product",
            body_text="Product description here",
            word_count=3,
            headings=[{"tag": "h1", "text": "Test Product"}],
        )
        assert d.word_count == 3
        assert len(d.headings) == 1


class TestAuditResult:
    def test_defaults(self) -> None:
        r = AuditResult()
        assert r.input_url == ""
        assert r.findings == []
        assert r.scorecard == {}

    def test_serialises_to_json(self) -> None:
        r = AuditResult(
            input_url="https://example.com/products/x",
            domain="example.com",
            findings=[Finding(category="trust", severity=Severity.LOW, title="test")],
        )
        d = r.model_dump()
        # Should survive json.dumps
        dumped = json.dumps(d, default=str)
        loaded = json.loads(dumped)
        assert loaded["input_url"] == "https://example.com/products/x"
        assert len(loaded["findings"]) == 1


class TestReportModels:
    def test_report_metadata(self) -> None:
        m = ReportMetadata(url="https://example.com", domain="example.com")
        assert "shopify-revenue-leak-auditor" in m.tool_name

    def test_report_output(self) -> None:
        o = ReportOutput(
            summary="Good page",
            overall_score=85.0,
            sections=[ReportSection(title="Trust Signals", content="All good", findings_count=0)],
        )
        assert len(o.sections) == 1
        assert o.overall_score == 85.0
