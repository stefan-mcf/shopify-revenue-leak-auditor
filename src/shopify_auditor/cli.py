"""Command-line interface for Shopify Revenue Leak Auditor."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from shopify_auditor import __version__
from shopify_auditor import audit_runner as audit_runner_module
from shopify_auditor.config import get_settings
from shopify_auditor.demo import DEMO_URL, DemoAuditRunner
from shopify_auditor.utils.files import (
    create_audit_output_dir,
    ensure_dir,
    write_json,
    write_text,
)
from shopify_auditor.utils.urls import is_valid_url, normalize_url

app = typer.Typer(
    name="shopify-audit",
    help="Audit Shopify pages for likely revenue leaks.",
    no_args_is_help=True,
)
console = Console()
settings = get_settings()


def _write_cli_outputs(audit_runner: object, out_path: Path) -> tuple[Path, Path]:
    """Write audit outputs and retain the short report aliases."""
    reports = audit_runner.generate_reports()
    markdown_report_path = out_path / "audit_report.md"
    html_report_path = out_path / "audit_report.html"
    write_text(markdown_report_path, reports["markdown"])
    write_text(html_report_path, reports["html"])
    write_text(out_path / "report.md", reports["markdown"])
    write_text(out_path / "report.html", reports["html"])
    result = getattr(audit_runner, "result", None)
    if result is not None and hasattr(result, "model_dump"):
        result.output_paths = {
            "audit_data_json": str(out_path / "audit_data.json"),
            "markdown_report": str(markdown_report_path),
            "html_report": str(html_report_path),
            "markdown_report_alias": str(out_path / "report.md"),
            "html_report_alias": str(out_path / "report.html"),
        }
        write_json(out_path / "audit_data.json", result.model_dump(mode="json"))
    return markdown_report_path, html_report_path


@app.command()
def version() -> None:
    """Print the installed package version."""
    console.print(f"shopify-revenue-leak-auditor version {__version__}")


@app.command("audit-url")
def audit_url(
    url: str = typer.Argument(..., help="Product page URL to audit"),
    output_dir: str = typer.Option(
        settings.default_output_dir,
        "--output-dir",
        "-o",
        help="Base output directory",
    ),
) -> None:
    """Audit one Shopify product URL and generate a revenue-leak report."""
    console.print(Panel.fit("Audit command accepted.", border_style="green"))

    normalized = normalize_url(url)
    if not is_valid_url(normalized):
        console.print("[red]Error:[/red] Invalid URL provided.")
        raise typer.Exit(code=1)
    console.print("URL validated.")

    out_path = create_audit_output_dir(output_dir, normalized)
    console.print(f"Output directory prepared: [bold]{out_path}[/bold]")

    console.print("[blue]Running audit checks...[/blue]")
    audit_runner = audit_runner_module.AuditRunner(
        normalized,
        output_dir=out_path,
        enable_llm=False,
        llm_client=None,
    )
    audit_result = audit_runner.run_audit()

    console.print("[blue]Generating reports...[/blue]")
    markdown_report_path, html_report_path = _write_cli_outputs(audit_runner, out_path)
    console.print("[green]Reports generated:[/green]")
    console.print(f"  Markdown: [bold]{markdown_report_path}[/bold]")
    console.print(f"  HTML: [bold]{html_report_path}[/bold]")

    if audit_result.error:
        console.print(f"[red]Audit could not load the page:[/red] {audit_result.error}")
        raise typer.Exit(code=2)
    console.print("[green]Audit checks completed.[/green]")


@app.command("audit-batch")
def audit_batch(
    path: str = typer.Argument(..., help="Path to a text file with one URL per line"),
    output_dir: str = typer.Option(
        settings.default_output_dir,
        "--output-dir",
        "-o",
        help="Base output directory",
    ),
) -> None:
    """Audit multiple product URLs read from a text file."""
    console.print(Panel.fit("Batch command accepted.", border_style="green"))

    filepath = Path(path)
    if not filepath.exists():
        console.print(f"[red]Error:[/red] File not found: {path}")
        raise typer.Exit(code=1)

    raw_lines = filepath.read_text(encoding="utf-8").splitlines()
    urls = [
        line.strip() for line in raw_lines if line.strip() and not line.lstrip().startswith("#")
    ]
    console.print(f"URLs loaded: {len(urls)}")
    if not urls:
        console.print("[red]Error:[/red] No URLs found in the input file.")
        raise typer.Exit(code=1)

    normalized_urls = [normalize_url(url) for url in urls]
    valid_urls = [url for url in normalized_urls if is_valid_url(url)]
    invalid_count = len(urls) - len(valid_urls)
    if invalid_count:
        console.print(f"[yellow]Warning:[/yellow] Skipped {invalid_count} invalid URL(s).")
    if not valid_urls:
        console.print("[red]Error:[/red] No valid URLs found in the input file.")
        raise typer.Exit(code=1)

    batch_dir = Path(output_dir)
    ensure_dir(batch_dir)
    console.print(f"Batch output directory: [bold]{batch_dir}[/bold]")

    failures = 0
    for index, url in enumerate(valid_urls, start=1):
        console.print(f"[{index}/{len(valid_urls)}] Auditing {url}...")
        try:
            url_output_dir = create_audit_output_dir(batch_dir, url)
            audit_runner = audit_runner_module.AuditRunner(
                url,
                output_dir=url_output_dir,
                enable_llm=False,
                llm_client=None,
            )
            audit_result = audit_runner.run_audit()
            markdown_report_path, html_report_path = _write_cli_outputs(
                audit_runner, url_output_dir
            )
            console.print(f"  [green]Reports generated for {url}:[/green]")
            console.print(f"    Markdown: [bold]{markdown_report_path}[/bold]")
            console.print(f"    HTML: [bold]{html_report_path}[/bold]")
            if audit_result.error:
                failures += 1
                console.print(f"  [red]Page load failed:[/red] {audit_result.error}")
        except Exception as exc:
            failures += 1
            console.print(f"  [red]Error auditing {url}: {exc}[/red]")

    if failures:
        console.print(f"[red]Batch completed with {failures} failed audit(s).[/red]")
        raise typer.Exit(code=2)
    console.print("[green]Batch audit completed.[/green]")


@app.command()
def demo(
    output_dir: str = typer.Option(
        "output",
        "--output-dir",
        "-o",
        help="Base output directory",
    ),
) -> None:
    """Generate a deterministic audit from packaged fictional page data."""
    console.print("Demo command accepted.")
    console.print(f"[blue]Running demo audit for {DEMO_URL}...[/blue]")
    out_path = create_audit_output_dir(output_dir, DEMO_URL)

    audit_runner = DemoAuditRunner(
        DEMO_URL,
        output_dir=out_path,
        enable_llm=False,
        llm_client=None,
    )
    audit_runner.run_audit()
    markdown_report_path, html_report_path = _write_cli_outputs(audit_runner, out_path)

    console.print("[green]Reports generated:[/green]")
    console.print(f"  Markdown: [bold]{markdown_report_path}[/bold]")
    console.print(f"  HTML: [bold]{html_report_path}[/bold]")
    console.print("[green]Demo audit completed.[/green]")


if __name__ == "__main__":
    app()
