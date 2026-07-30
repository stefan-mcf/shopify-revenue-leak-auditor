
"""Tests for CLI entrypoint (Tranche 2, 16-19)."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner
from pathlib import Path
import os
from unittest.mock import patch, MagicMock

from shopify_auditor.cli import app
from shopify_auditor.utils.files import create_audit_output_dir

runner = CliRunner()


class TestVersion:
    def test_version_output(self) -> None:
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestAuditUrl:
    @patch('shopify_auditor.audit_runner.AuditRunner')
    def test_valid_url_accepted(self, MockAuditRunner, tmp_path) -> None:
        mock_runner_instance = MockAuditRunner.return_value
        mock_runner_instance.generate_reports.return_value = {
            "markdown": "# Mock Report\n\nContent for markdown.",
            "html": "<html><body>Mock HTML Report</body></html>"
        }

        output_dir = tmp_path / "output"
        result = runner.invoke(
            app, ["audit-url", "https://example.com/products/test", "-o", str(output_dir)]
        )
        assert result.exit_code == 0
        assert "Audit command accepted" in result.output
        assert "URL validated" in result.output
        assert "Audit checks completed" in result.output
        assert "Reports generated" in result.output

        # Reconstruct the expected output path for the report
        expected_report_dir = create_audit_output_dir(output_dir, "https://example.com/products/test")
        assert (expected_report_dir / "report.md").exists()
        assert (expected_report_dir / "report.html").exists()
        
        MockAuditRunner.assert_called_once_with("https://example.com/products/test", output_dir=expected_report_dir, enable_llm=False, llm_client=None)
        mock_runner_instance.run_audit.assert_called_once()
        mock_runner_instance.generate_reports.assert_called_once()

    def test_invalid_url_rejected(self) -> None:
        result = runner.invoke(app, ["audit-url", "not-a-valid-url"])
        assert result.exit_code == 1
        assert "Invalid URL" in result.output

    @patch('shopify_auditor.audit_runner.AuditRunner')
    def test_audit_url_with_llm_flag(self, MockAuditRunner, tmp_path) -> None:
        mock_runner_instance = MockAuditRunner.return_value
        mock_runner_instance.generate_reports.return_value = {
            "markdown": "# Mock Report\n\nContent for markdown.\nLLM analysis output: Mock LLM analysis output.",
            "html": "<html><body>Mock HTML Report</body></html>"
        }

        output_dir = tmp_path / "output"
        result = runner.invoke(
            app, ["audit-url", "https://example.com/products/test", "-o", str(output_dir), "--llm"]
        )
        assert result.exit_code == 0
        assert "Audit command accepted" in result.output
        assert "URL validated" in result.output
        assert "Audit checks completed" in result.output
        assert "Reports generated" in result.output

        # Reconstruct the expected output path for the report
        expected_report_dir = create_audit_output_dir(output_dir, "https://example.com/products/test")
        assert (expected_report_dir / "report.md").exists()
        assert (expected_report_dir / "report.html").exists()
        
        MockAuditRunner.assert_called_once_with("https://example.com/products/test", output_dir=expected_report_dir, enable_llm=True, llm_client="mock")
        mock_runner_instance.run_audit.assert_called_once()
        mock_runner_instance.generate_reports.assert_called_once()
        report_content = (expected_report_dir / "report.md").read_text()
        assert "Mock LLM analysis output." in report_content


class TestAuditBatch:
    def test_missing_file_rejected(self) -> None:
        result = runner.invoke(app, ["audit-batch", "/nonexistent/file.txt"])
        assert result.exit_code == 1
        assert "File not found" in result.output

    @patch('shopify_auditor.audit_runner.AuditRunner')
    def test_with_valid_file(self, MockAuditRunner, tmp_path) -> None:
        mock_runner_instance = MockAuditRunner.return_value
        mock_runner_instance.generate_reports.return_value = {
            "markdown": "# Batch Mock Report\n\nContent for markdown.",
            "html": "<html><body>Batch Mock HTML Report</body></html>"
        }

        url_file = tmp_path / "urls.txt"
        url_file.write_text("https://example.com/products/a\nhttps://example.com/products/b\n")
        output_dir = tmp_path / "batch_output"
        result = runner.invoke(app, ["audit-batch", str(url_file), "-o", str(output_dir)])
        assert result.exit_code == 0
        assert "Batch command accepted" in result.output
        assert "URLs loaded: 2" in result.output
        assert "Batch audit completed" in result.output
        
        # Verify calls for each URL
        MockAuditRunner.call_count == 2
        mock_runner_instance.run_audit.call_count == 2
        mock_runner_instance.generate_reports.call_count == 2

        expected_report_dir_a = create_audit_output_dir(output_dir, "https://example.com/products/a")
        expected_report_dir_b = create_audit_output_dir(output_dir, "https://example.com/products/b")
        assert (expected_report_dir_a / "report.md").exists()
        assert (expected_report_dir_b / "report.html").exists()
        # Check content for one of them
        report_content_a = (expected_report_dir_a / "report.md").read_text()
        assert "Content for markdown." in report_content_a

    @patch('shopify_auditor.audit_runner.AuditRunner')
    def test_audit_batch_with_llm_flag(self, MockAuditRunner, tmp_path) -> None:
        mock_runner_instance = MockAuditRunner.return_value
        mock_runner_instance.generate_reports.return_value = {
            "markdown": "# Batch Mock Report\n\nContent with LLM.\nLLM analysis output: Mock LLM batch analysis output.",
            "html": "<html><body>Batch Mock HTML Report with LLM</body></html>"
        }

        url_file = tmp_path / "urls.txt"
        url_file.write_text("https://example.com/products/c\nhttps://example.com/products/d\n")
        output_dir = tmp_path / "batch_llm_output"

        result = runner.invoke(app, ["audit-batch", str(url_file), "-o", str(output_dir), "--llm"])
        assert result.exit_code == 0
        assert "Batch audit completed" in result.output
        
        expected_report_dir_c = create_audit_output_dir(output_dir, "https://example.com/products/c")
        expected_report_dir_d = create_audit_output_dir(output_dir, "https://example.com/products/d")

        # Verify calls for each URL with LLM enabled
        MockAuditRunner.call_count == 2
        MockAuditRunner.assert_any_call("https://example.com/products/c", output_dir=expected_report_dir_c, enable_llm=True, llm_client="mock")
        MockAuditRunner.assert_any_call("https://example.com/products/d", output_dir=expected_report_dir_d, enable_llm=True, llm_client="mock")

        assert (expected_report_dir_c / "report.md").exists()
        assert (expected_report_dir_d / "report.html").exists()
        report_content_c = (expected_report_dir_c / "report.md").read_text()
        assert "Mock LLM batch analysis output." in report_content_c
        report_content_d = (expected_report_dir_d / "report.md").read_text()
        assert "Mock LLM batch analysis output." in report_content_d


class TestDemo:
    @patch('shopify_auditor.audit_runner.AuditRunner')
    def test_demo_command_generates_report(self, MockAuditRunner, tmp_path) -> None:
        mock_runner_instance = MockAuditRunner.return_value
        mock_runner_instance.generate_reports.return_value = {
            "markdown": "# Demo Report\n\nContent for demo.",
            "html": "<html><body>Demo HTML Report</body></html>"
        }

        output_dir = tmp_path / "demo_output"
        result = runner.invoke(app, ["demo", "-o", str(output_dir)])
        assert result.exit_code == 0
        assert "Demo command accepted" in result.output
        assert "Demo audit completed" in result.output

        demo_url = "https://example.myshopify.com/products/demo-product"
        expected_report_dir = create_audit_output_dir(output_dir, demo_url)
        assert (expected_report_dir / "report.md").exists()
        assert (expected_report_dir / "report.html").exists()
        
        MockAuditRunner.assert_called_once_with(demo_url, output_dir=expected_report_dir, enable_llm=False, llm_client=None)
        mock_runner_instance.run_audit.assert_called_once()
        mock_runner_instance.generate_reports.assert_called_once()

    @patch('shopify_auditor.audit_runner.AuditRunner')
    def test_demo_command_with_llm_flag(self, MockAuditRunner, tmp_path) -> None:
        mock_runner_instance = MockAuditRunner.return_value
        mock_runner_instance.generate_reports.return_value = {
            "markdown": "# Demo Report\n\nContent for demo.\nLLM analysis output: Mock LLM demo analysis output.",
            "html": "<html><body>Demo HTML Report with LLM</body></html>"
        }

        output_dir = tmp_path / "demo_llm_output"
        result = runner.invoke(app, ["demo", "-o", str(output_dir), "--llm"])
        assert result.exit_code == 0
        assert "Demo audit completed" in result.output

        demo_url = "https://example.myshopify.com/products/demo-product"
        expected_report_dir = create_audit_output_dir(output_dir, demo_url)
        assert (expected_report_dir / "report.md").exists()
        assert (expected_report_dir / "report.html").exists()
        
        MockAuditRunner.assert_called_once_with(demo_url, output_dir=expected_report_dir, enable_llm=True, llm_client="mock")
        mock_runner_instance.run_audit.assert_called_once()
        mock_runner_instance.generate_reports.assert_called_once()
        report_content = (expected_report_dir / "report.md").read_text()
        assert "Mock LLM demo analysis output." in report_content
