"""Browser-level smoke test for the real page-loading path."""

from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest

from shopify_auditor.browser.page_loader import PageLoader
from shopify_auditor.models import PageLoadStatus


@pytest.mark.browser
def test_page_loader_captures_local_fixture(tmp_path: Path) -> None:
    fixture_dir = Path(__file__).parents[1] / "src" / "shopify_auditor"
    handler = partial(SimpleHTTPRequestHandler, directory=str(fixture_dir))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]

    try:
        result = PageLoader().load(
            f"http://localhost:{port}/demo_product_page.html",
            tmp_path,
        )
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    assert result.status == PageLoadStatus.SUCCESS
    assert result.status_code == 200
    assert result.title == "Calm Desk Lamp – Calm Home Goods"
    assert "Calm Desk Lamp" in result.html
    assert Path(result.screenshot_paths["desktop"]).exists()
    assert Path(result.screenshot_paths["mobile"]).exists()
    assert Path(result.screenshot_paths["html"]).exists()
