"""CLI entrypoint for Shopify Revenue Leak Auditor.

Commands
--------
version      Print package version.
audit-url    Audit a single Shopify product URL.
audit-batch  Audit multiple URLs from a file.
demo         Run a demo audit (requires a functioning pipeline).
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from shopify_auditor import __version__
from shopify_auditor.config import get_settings
from shopify_auditor.utils.files import create_audit_output_dir, write_json, write_text
from shopify_auditor.utils.urls import is_valid_url, normalize_url
from shopify_auditor import audit_runner as audit_runner_module

app = typer.Typer(
    name="shopify-audit",
    help="Audit Shopify pages for likely revenue leaks.",
    no_args_is_help=True,
)
console = Console()
settings = get_settings()


def _write_cli_outputs(audit_runner: object, out_path: Path) -> tuple[Path, Path]:
    """Write MVP output files while preserving early report.md/report.html aliases."""
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


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


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
    llm: bool = typer.Option(
        False,
        "--llm",
        help="Enable LLM analysis for the report (requires LLM client configured)",
    ),
) -> None:
    """Audit a single Shopify product URL and generate a revenue-leak report."""
    console.print(Panel.fit("Audit command accepted.", border_style="green"))

    # --- Validate ----------------------------------------------------------
    normalized = normalize_url(url)
    if not is_valid_url(normalized):
        console.print("[red]Error:[/red] Invalid URL provided.")
        raise typer.Exit(code=1)
    console.print("URL validated.")

    # --- Prepare output directory ------------------------------------------
    out_path = create_audit_output_dir(output_dir, normalized)
    console.print(f"Output directory prepared: [bold]{out_path}[/bold]")

    # --- Run audit ---------------------------------------------------------
    console.print("[blue]Running audit checks...[/blue]")
    audit_runner = audit_runner_module.AuditRunner(normalized, output_dir=out_path, enable_llm=llm, llm_client="mock" if llm else None) # Use "mock" for testing LLM
    audit_runner.run_audit()
    console.print("[green]Audit checks completed.[/green]")

    # --- Generate reports --------------------------------------------------
    console.print("[blue]Generating reports...[/blue]")
    markdown_report_path, html_report_path = _write_cli_outputs(audit_runner, out_path)

    console.print(f"[green]Reports generated:[/green]")
    console.print(f"  Markdown: [bold]{markdown_report_path}[/bold]")
    console.print(f"  HTML: [bold]{html_report_path}[/bold]")


@app.command("audit-batch")
def audit_batch(
    path: str = typer.Argument(..., help="Path to a text file with one URL per line"),
    output_dir: str = typer.Option(
        settings.default_output_dir,
        "--output-dir",
        "-o",
        help="Base output directory",
    ),
    llm: bool = typer.Option(
        False,
        "--llm",
        help="Enable LLM analysis for the report (requires LLM client configured)",
    ),
) -> None:
    """Audit multiple product URLs read from a text file."""
    console.print(Panel.fit("Batch command accepted.", border_style="green"))

    # --- Load URLs ---------------------------------------------------------
    filepath = Path(path)
    if not filepath.exists():
        console.print(f"[red]Error:[/red] File not found: {path}")
        raise typer.Exit(code=1)

    raw_lines = filepath.read_text(encoding="utf-8").strip().splitlines()
    urls = [l.strip() for l in raw_lines if l.strip()]
    console.print(f"URLs loaded: {len(urls)}")

    if not urls:
        console.print("[red]Error:[/red] No URLs found in the input file.")
        raise typer.Exit(code=1)

    valid_urls = [normalize_url(u) for u in urls if is_valid_url(u)]
    invalid_count = len(urls) - len(valid_urls)
    if invalid_count:
        console.print(f"[yellow]Warning:[/yellow] Skipped {invalid_count} invalid URL(s).")

    # --- Prepare batch output ----------------------------------------------
    from shopify_auditor.utils.dates import timestamp_for_folder

    batch_dir = Path(output_dir)
    from shopify_auditor.utils.files import ensure_dir
    ensure_dir(batch_dir)

    console.print(f"Batch output directory: [bold]{batch_dir}[/bold]")

    # --- Run audits for each URL -------------------------------------------
    for i, url in enumerate(valid_urls):
        console.print(f"[{i+1}/{len(valid_urls)}] Auditing {url}...")
        try:
            url_output_dir = create_audit_output_dir(batch_dir, url)
            audit_runner = audit_runner_module.AuditRunner(url, output_dir=url_output_dir, enable_llm=llm, llm_client="mock" if llm else None)
            audit_runner.run_audit()
            markdown_report_path, html_report_path = _write_cli_outputs(audit_runner, url_output_dir)

            console.print(f"  [green]Reports generated for {url}:[/green]")
            console.print(f"    Markdown: [bold]{markdown_report_path}[/bold]")
            console.print(f"    HTML: [bold]{html_report_path}[/bold]")
        except Exception as e:
            console.print(f"  [red]Error auditing {url}: {e}[/red]")
    console.print("[green]Batch audit completed.[/green]")


@app.command()
def demo(
    output_dir: str = typer.Option(
        "output",
        "--output-dir",
        "-o",
        help="Base output directory",
    ),
    llm: bool = typer.Option(
        False,
        "--llm",
        help="Enable LLM analysis for the report (requires LLM client configured)",
    ),
) -> None:
    """Generate a demo audit with sample data (requires MVP pipeline)."""
    console.print("Demo command accepted.")

    demo_url = "https://example.myshopify.com/products/demo-product"
    console.print(f"[blue]Running demo audit for {demo_url}...[/blue]")
    out_path = create_audit_output_dir(output_dir, demo_url)
    
    audit_runner = audit_runner_module.AuditRunner(demo_url, output_dir=out_path, enable_llm=llm, llm_client="mock" if llm else None)
    audit_runner.run_audit()
    markdown_report_path, html_report_path = _write_cli_outputs(audit_runner, out_path)

    console.print(f"[green]Reports generated:[/green]")
    console.print(f"  Markdown: [bold]{markdown_report_path}[/bold]")
    console.print(f"  HTML: [bold]{html_report_path}[/bold]")
    console.print("[green]Demo audit completed.[/green]")


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app()
