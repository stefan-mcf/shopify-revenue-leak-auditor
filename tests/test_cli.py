"""Tests for the command-line interface."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import patch

from typer.testing import CliRunner

from shopify_auditor.cli import app
from shopify_auditor.demo import DEMO_URL
from shopify_auditor.utils.files import create_audit_output_dir

runner = CliRunner()


def _configure_runner(mock_runner: object, *, error: str = "") -> object:
    instance = mock_runner.return_value
    instance.result = None
    instance.run_audit.return_value = SimpleNamespace(error=error)
    instance.generate_reports.return_value = {
        "markdown": "# Audit Report\n\nGenerated report.",
        "html": "<html><body>Generated report.</body></html>",
    }
    return instance


def test_version_output() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


@patch("shopify_auditor.audit_runner.AuditRunner")
def test_audit_url_generates_reports(mock_runner: object, tmp_path) -> None:
    instance = _configure_runner(mock_runner)
    output_dir = tmp_path / "output"

    result = runner.invoke(
        app,
        ["audit-url", "https://example.com/products/test", "-o", str(output_dir)],
    )

    assert result.exit_code == 0
    assert "Audit checks completed" in result.output
    report_dir = create_audit_output_dir(output_dir, "https://example.com/products/test")
    assert (report_dir / "audit_report.md").exists()
    assert (report_dir / "audit_report.html").exists()
    instance.run_audit.assert_called_once_with()
    mock_runner.assert_called_once_with(
        "https://example.com/products/test",
        output_dir=report_dir,
        enable_llm=False,
        llm_client=None,
    )


@patch("shopify_auditor.audit_runner.AuditRunner")
def test_audit_url_returns_nonzero_when_page_load_fails(mock_runner: object, tmp_path) -> None:
    _configure_runner(mock_runner, error="browser unavailable")

    result = runner.invoke(
        app,
        ["audit-url", "https://example.com/products/test", "-o", str(tmp_path)],
    )

    assert result.exit_code == 2
    assert "Audit could not load the page" in result.output
    assert "browser unavailable" in result.output


def test_invalid_url_rejected() -> None:
    result = runner.invoke(app, ["audit-url", "not-a-valid-url"])
    assert result.exit_code == 1
    assert "Invalid URL" in result.output


def test_cli_does_not_advertise_unimplemented_llm_option() -> None:
    result = runner.invoke(app, ["audit-url", "--help"])
    assert result.exit_code == 0
    assert "--llm" not in result.output


@patch("shopify_auditor.audit_runner.AuditRunner")
def test_batch_accepts_bare_domains_and_ignores_comments(mock_runner: object, tmp_path) -> None:
    instance = _configure_runner(mock_runner)
    url_file = tmp_path / "urls.txt"
    url_file.write_text(
        "# product pages\nexample.com/products/a\nhttps://example.com/products/b\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "batch"

    result = runner.invoke(app, ["audit-batch", str(url_file), "-o", str(output_dir)])

    assert result.exit_code == 0
    assert "URLs loaded: 2" in result.output
    assert mock_runner.call_count == 2
    assert instance.run_audit.call_count == 2
    assert instance.generate_reports.call_count == 2


@patch("shopify_auditor.audit_runner.AuditRunner")
def test_batch_returns_nonzero_when_an_audit_fails(mock_runner: object, tmp_path) -> None:
    _configure_runner(mock_runner, error="HTTP 503")
    url_file = tmp_path / "urls.txt"
    url_file.write_text("https://example.com/products/a\n", encoding="utf-8")

    result = runner.invoke(app, ["audit-batch", str(url_file), "-o", str(tmp_path / "out")])

    assert result.exit_code == 2
    assert "1 failed audit" in result.output


def test_batch_rejects_file_without_valid_urls(tmp_path) -> None:
    url_file = tmp_path / "urls.txt"
    url_file.write_text("not-a-valid-url\n", encoding="utf-8")

    result = runner.invoke(app, ["audit-batch", str(url_file), "-o", str(tmp_path / "out")])

    assert result.exit_code == 1
    assert "No valid URLs" in result.output


def test_demo_is_offline_and_generates_complete_outputs(tmp_path) -> None:
    output_dir = tmp_path / "demo"

    result = runner.invoke(app, ["demo", "-o", str(output_dir)])

    assert result.exit_code == 0
    assert "Demo audit completed" in result.output
    report_dir = create_audit_output_dir(output_dir, DEMO_URL)
    expected_files = {
        "audit_data.json",
        "audit_report.md",
        "audit_report.html",
        "report.md",
        "report.html",
    }
    assert expected_files.issubset(path.name for path in report_dir.iterdir())
    audit_data = json.loads((report_dir / "audit_data.json").read_text(encoding="utf-8"))
    assert audit_data["error"] == ""
    assert audit_data["extracted"]["canonical_url"] == DEMO_URL
