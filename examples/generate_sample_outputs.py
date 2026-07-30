"""Generate public-safe sample outputs.

The sample uses a fictional product-page fixture and does not require network
access, Shopify credentials, or LLM API keys. If Playwright/Chromium is
available, screenshots are rendered from the fixture and generated report; a
stdlib PNG fallback keeps the script usable in minimal environments.
"""

from __future__ import annotations

from html import escape
import base64
import mimetypes
from pathlib import Path
import struct
import zlib

from shopify_auditor.audit_runner import AuditRunner
from shopify_auditor.models import PageLoadResult, PageLoadStatus
from shopify_auditor.utils.files import write_json, write_text

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_INPUTS = REPO_ROOT / "examples" / "sample_inputs"
SAMPLE_OUTPUTS = REPO_ROOT / "examples" / "sample_outputs" / "demo-product-audit"
FIXTURE_HTML = SAMPLE_INPUTS / "demo-product-page.html"
SAMPLE_URL = "https://calm-home-goods.example/products/calm-desk-lamp"


def _inline_fixture_images(html: str) -> str:
    """Inline local demo product photos for deterministic Playwright screenshots."""
    replacements = {
        "assets/demo-lamp-front.jpg": SAMPLE_INPUTS / "assets" / "demo-lamp-front.jpg",
        "assets/demo-lamp-detail.jpg": SAMPLE_INPUTS / "assets" / "demo-lamp-detail.jpg",
        "assets/demo-lamp-lifestyle.jpg": SAMPLE_INPUTS / "assets" / "demo-lamp-lifestyle.jpg",
    }
    for src, path in replacements.items():
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        html = html.replace(src, f"data:{mime_type};base64,{encoded}")
    return html


def _png(path: Path, width: int, height: int, top_rgb: tuple[int, int, int], bottom_rgb: tuple[int, int, int]) -> None:
    """Write a simple RGB PNG using only the Python standard library."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for y in range(height):
        ratio = y / max(height - 1, 1)
        rgb = tuple(int(top_rgb[i] * (1 - ratio) + bottom_rgb[i] * ratio) for i in range(3))
        rows.append(b"\x00" + bytes(rgb) * width)
    raw = b"".join(rows)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, level=9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def _fixture_screenshot_css() -> str:
    return """
    <style>
      body { margin: 0; font-family: Inter, Arial, sans-serif; color: #172033; background: #f7f4ee; }
      header { display: flex; justify-content: space-between; align-items: center; padding: 20px 52px; background: #182033; color: white; }
      nav a { color: #dbeafe; margin-left: 22px; text-decoration: none; }
      main { max-width: 1080px; margin: 0 auto; padding: 42px 32px; }
      .product-hero { background: white; border-radius: 28px; padding: 44px; box-shadow: 0 22px 70px rgba(20, 30, 50, .12); }
      h1 { font-size: 58px; line-height: .96; margin: 10px 0 16px; letter-spacing: -2px; }
      h2 { margin-top: 34px; }
      p { font-size: 18px; line-height: 1.55; max-width: 760px; }
      .price { font-size: 30px; font-weight: 800; color: #0f766e; }
      button { border: 0; border-radius: 999px; padding: 16px 28px; background: #0f766e; color: white; font-size: 18px; font-weight: 800; }
      .gallery { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin: 28px 0; }
      .gallery img { display: block; width: 100%; aspect-ratio: 1.42; border-radius: 20px; background: linear-gradient(135deg, #d6c4a9, #8aa39b); object-fit: cover; box-shadow: 0 16px 36px rgba(20, 30, 50, .12); }
      .details, .comparison, .newsletter { background: rgba(255,255,255,.78); border-radius: 22px; padding: 28px; margin-top: 20px; }
      @media (max-width: 600px) {
        header { padding: 14px 18px; font-size: 14px; }
        nav { display: none; }
        main { padding: 18px; }
        .product-hero { padding: 26px; border-radius: 20px; }
        h1 { font-size: 38px; }
        p { font-size: 16px; }
        .gallery { grid-template-columns: 1fr; }
      }
    </style>
    """


def _scorecard_html(result: object) -> str:
    rows = []
    for key, score in result.scorecard.category_scores.items():
        label = key.replace("_", " ").title()
        width = round((score.score / score.weight) * 100) if score.weight else 0
        rows.append(
            f"""
            <tr>
              <td>{escape(label)}</td>
              <td>{score.score}/{score.weight}</td>
              <td><div class='bar'><span style='width:{width}%'></span></div></td>
              <td>{score.findings_count}</td>
            </tr>
            """
        )
    return f"""
    <!doctype html>
    <html><head><meta charset='utf-8'><title>Audit Scorecard</title>
    <style>
      :root {{ --ink:#0f172a; --muted:#64748b; --line:#dbe3ef; --panel:#ffffff; --soft:#f6f8fb; --accent:#0f766e; --risk:#dc2626; }}
      body {{ margin: 0; font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg,#08111f 0%,#102034 42%,#f6f8fb 42%); color: var(--ink); }}
      main {{ max-width: 1120px; margin: 0 auto; padding: 44px 48px 54px; }}
      .hero {{ background: linear-gradient(135deg,#ffffff 0%,#f8fafc 100%); border:1px solid rgba(219,227,239,.95); border-radius: 30px; padding: 32px 38px; box-shadow: 0 28px 80px rgba(8,17,31,.20); display:grid; grid-template-columns: 1fr auto; gap:24px; align-items:center; }}
      .eyebrow {{ color:var(--accent); font-size:13px; font-weight:800; letter-spacing:.14em; text-transform:uppercase; margin:0 0 8px; }}
      h1 {{ font-size: 46px; line-height:1.02; letter-spacing:-1.6px; margin: 0 0 8px; }}
      .summary {{ color:var(--muted); font-size:17px; margin:0; max-width:660px; }}
      .score {{ min-width:190px; text-align:center; border-radius:26px; background:#fff1f2; border:1px solid #fecdd3; padding:20px 24px; }}
      .score strong {{ display:block; font-size:68px; line-height:.9; color:var(--risk); letter-spacing:-3px; }}
      .score span {{ color:#991b1b; font-weight:800; }}
      table {{ width: 100%; border-collapse: collapse; margin-top: 28px; background: white; border:1px solid var(--line); border-radius: 24px; overflow: hidden; box-shadow: 0 22px 60px rgba(15,23,42,.10); }}
      th, td {{ text-align: left; padding: 15px 18px; border-bottom: 1px solid #e8eef6; font-size:15px; }}
      th {{ background: #f0fdfa; color:#134e4a; font-size:12px; letter-spacing:.09em; text-transform:uppercase; }}
      tr:last-child td {{ border-bottom:0; }}
      .bar {{ width: 100%; height: 12px; background: #e5e7eb; border-radius: 99px; overflow: hidden; }}
      .bar span {{ display: block; height: 100%; background: linear-gradient(90deg, #dc2626, #f59e0b, #0f766e); }}
    </style></head><body><main>
      <section class='hero'>
        <div>
          <p class='eyebrow'>Product-page conversion audit</p>
          <h1>Revenue Leak Scorecard</h1>
          <p class='summary'>Prioritized scoring across trust, offer clarity, copy, objections, CTA quality, mobile UX, product information, AI-shopping readiness, and technical health.</p>
        </div>
        <div class='score'><strong>{result.scorecard.overall_score}</strong><span>/100 · {escape(result.scorecard.score_label)}</span></div>
      </section>
      <table><thead><tr><th>Category</th><th>Score</th><th>Visual</th><th>Findings</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
    </main></body></html>
    """


def _write_fallback_screenshots(paths: dict[str, Path]) -> None:
    _png(paths["desktop"], 1280, 1000, (245, 247, 250), (201, 214, 228))
    _png(paths["mobile"], 390, 844, (250, 247, 240), (216, 200, 179))
    _png(paths["report_overview"], 1280, 720, (236, 248, 243), (179, 216, 207))
    _png(paths["scorecard"], 1280, 900, (243, 240, 252), (205, 193, 232))


def _render_page_screenshots(html: str, paths: dict[str, Path]) -> None:
    """Render desktop/mobile fixture screenshots, falling back to simple PNGs."""
    try:
        from playwright.sync_api import sync_playwright

        rendered_html = _inline_fixture_images(html).replace("</head>", _fixture_screenshot_css() + "</head>")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            desktop = browser.new_page(viewport={"width": 1280, "height": 1000})
            desktop.set_content(rendered_html, wait_until="load")
            desktop.screenshot(path=paths["desktop"], full_page=False)
            desktop.close()

            mobile = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True)
            mobile.set_content(rendered_html, wait_until="load")
            mobile.screenshot(path=paths["mobile"], full_page=False)
            mobile.close()
            browser.close()
    except Exception:
        _write_fallback_screenshots(paths)


def _render_report_screenshots(report_html: str, scorecard_html: str, paths: dict[str, Path]) -> None:
    """Render report and scorecard screenshots, falling back to simple PNGs."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            report = browser.new_page(viewport={"width": 1280, "height": 720})
            report.set_content(report_html, wait_until="load")
            report.screenshot(path=paths["report_overview"], full_page=False)
            report.close()

            scorecard = browser.new_page(viewport={"width": 1280, "height": 900})
            scorecard.set_content(scorecard_html, wait_until="load")
            scorecard.screenshot(path=paths["scorecard"], full_page=False)
            scorecard.close()
            browser.close()
    except Exception:
        _png(paths["report_overview"], 1280, 720, (236, 248, 243), (179, 216, 207))
        _png(paths["scorecard"], 1280, 900, (243, 240, 252), (205, 193, 232))


def _screenshot_paths() -> tuple[dict[str, Path], dict[str, str]]:
    screenshot_dir = SAMPLE_OUTPUTS / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    absolute = {
        "desktop": screenshot_dir / "desktop.png",
        "mobile": screenshot_dir / "mobile.png",
        "report_overview": screenshot_dir / "report-overview.png",
        "scorecard": screenshot_dir / "scorecard.png",
    }
    relative = {key: str(path.relative_to(REPO_ROOT)) for key, path in absolute.items()}
    return absolute, relative


def generate() -> None:
    SAMPLE_OUTPUTS.mkdir(parents=True, exist_ok=True)
    absolute_screenshots, screenshot_paths = _screenshot_paths()
    html = FIXTURE_HTML.read_text(encoding="utf-8")
    _render_page_screenshots(html, absolute_screenshots)

    runner = AuditRunner(SAMPLE_URL, output_dir=SAMPLE_OUTPUTS, enable_llm=False)

    def load_fixture(*, load_browser: bool) -> PageLoadResult:
        return PageLoadResult(
            url=SAMPLE_URL,
            original_url=SAMPLE_URL,
            status=PageLoadStatus.SUCCESS,
            status_code=200,
            title="Calm Desk Lamp – Calm Home Goods",
            html=html,
            screenshot_paths={"desktop": screenshot_paths["desktop"], "mobile": screenshot_paths["mobile"]},
        )

    runner._load_page = load_fixture  # type: ignore[method-assign]
    result = runner.run_audit(load_browser=False)
    reports = runner.generate_reports()
    _render_report_screenshots(reports["html"], _scorecard_html(result), absolute_screenshots)

    paths = {
        "audit_data_json": str((SAMPLE_OUTPUTS / "audit_data.json").relative_to(REPO_ROOT)),
        "markdown_report": str((SAMPLE_OUTPUTS / "audit_report.md").relative_to(REPO_ROOT)),
        "html_report": str((SAMPLE_OUTPUTS / "audit_report.html").relative_to(REPO_ROOT)),
        "markdown_report_alias": str((SAMPLE_OUTPUTS / "report.md").relative_to(REPO_ROOT)),
        "html_report_alias": str((SAMPLE_OUTPUTS / "report.html").relative_to(REPO_ROOT)),
        "desktop_screenshot": screenshot_paths["desktop"],
        "mobile_screenshot": screenshot_paths["mobile"],
        "report_overview_screenshot": screenshot_paths["report_overview"],
        "scorecard_screenshot": screenshot_paths["scorecard"],
    }
    result.output_paths = paths

    write_json(SAMPLE_OUTPUTS / "audit_data.json", result.model_dump(mode="json"))
    write_text(SAMPLE_OUTPUTS / "audit_report.md", reports["markdown"])
    write_text(SAMPLE_OUTPUTS / "audit_report.html", reports["html"])
    write_text(SAMPLE_OUTPUTS / "report.md", reports["markdown"])
    write_text(SAMPLE_OUTPUTS / "report.html", reports["html"])


if __name__ == "__main__":
    generate()
    print(f"Generated sample outputs in {SAMPLE_OUTPUTS.relative_to(REPO_ROOT)}")
