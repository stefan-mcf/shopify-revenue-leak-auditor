"""Shared test fixtures including shopify-like HTML pages and audit contexts."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from shopify_auditor.models import AuditContext, ImageAsset, LinkAsset, PageMetadata


@pytest.fixture
def shopify_product_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Classic Leather Tote Bag – ShopExample</title>
  <meta name="description" content="Handcrafted genuine leather tote. Free shipping.">
  <link rel="canonical" href="https://shopexample.com/products/classic-leather-tote">
  <meta property="og:title" content="Classic Leather Tote Bag">
  <meta property="og:description" content="Handcrafted genuine leather tote with free shipping.">
  <script type="application/ld+json">
  {"@context":"https://schema.org","@type":"Product","name":"Classic Leather Tote Bag","offers":{"@type":"Offer","price":"89.00","priceCurrency":"USD"}}
  </script>
</head>
<body>
  <h1>Classic Leather Tote Bag</h1>
  <h2>Details</h2>
  <p>Handcrafted from full-grain leather, this spacious tote is perfect for everyday use.</p>
  <p>Free shipping on orders over $50.</p>
  <img src="//shopexample.com/img/tote-1.jpg" alt="Leather tote bag front view">
  <img src="//shopexample.com/img/tote-2.jpg" alt="">
  <img src="//shopexample.com/img/icon-shipping.png" alt="Shipping icon">

  <span class="price">$89.00</span>
  <span class="compare-at-price">$120.00</span>

  <select class="product__select single-option-selector">
    <option>Black</option><option>Brown</option>
  </select>

  <form action="/cart/add">
    <button type="submit">Add to Cart</button>
  </form>

  <a href="/policies/shipping-policy">Shipping Policy</a>
  <a href="/pages/returns">Returns &amp; Exchanges</a>
  <a href="/pages/faq">FAQ</a>
  <a href="/pages/reviews">Customer Reviews</a>
  <a href="/pages/contact">Contact Us</a>
  <a href="https://external.com/blog">Blog post</a>

  <footer>
    <a href="/policies/privacy">Privacy</a>
    <a href="/policies/terms">Terms</a>
  </footer>
</body>
</html>"""


@pytest.fixture
def simple_page_html() -> str:
    return """<!DOCTYPE html>
<html><head><title>Simple Page</title></head>
<body>
  <h1>Welcome</h1>
  <p>This is a simple page with limited content.</p>
  <a href="/about">About</a>
  <a href="/contact">Contact</a>
</body>
</html>"""


@pytest.fixture
def no_product_page_html() -> str:
    return """<!DOCTYPE html>
<html><head><title>Blog Post</title></head>
<body>
  <h1>5 Tips for Better Ecommerce</h1>
  <p>Blog content here. No products listed.</p>
  <img src="blog-hero.jpg" alt="Blog hero image">
  <a href="/">Home</a>
</body>
</html>"""


@pytest.fixture
def product_json_ld_html() -> str:
    return """<!DOCTYPE html>
<html><head><title>Product with JSON-LD</title>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Product","name":"Widget","offers":[{"@type":"Offer","price":"19.99","priceCurrency":"USD"}]}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://example.com/"}]}
</script>
</head><body>
  <h1>Widget</h1>
  <button>Add to Cart</button>
</body>
</html>"""


@pytest.fixture()
def rich_context(tmp_path: Path) -> AuditContext:
    screenshot = tmp_path / "mobile.png"
    screenshot.write_bytes(b"png")
    return AuditContext(
        url="https://example.com/products/widget-pro",
        final_url="https://example.com/products/widget-pro",
        page_title="Widget Pro | Example",
        product_title="Widget Pro",
        price_text="$49.00",
        page_text=(
            "Widget Pro helps busy professionals stay organized every day. "
            "Designed to save time at work, travel, home, and the gym. "
            "Perfect for gifting and ideal for daily routines. "
            "Free shipping over $50 with easy returns and a 30-day guarantee. "
            "Add to cart or buy now today. FAQ: How long does shipping take? 3-5 days. "
            "What materials are used? Premium recycled aluminum. "
            "Size guide and dimensions included. Secure checkout with PayPal and Klarna. "
            "Verified buyer reviews say customers love it. Contact support anytime. "
            "Unlike generic organizers, this patented design protects your essentials and reduces clutter."
        ),
        product_description=(
            "Widget Pro helps you reduce clutter and stay prepared. Designed for commuters,"
            " travelers, and home offices with premium materials and thoughtful storage."
        ),
        links=[
            LinkAsset(url="https://example.com/policies/shipping", text="Shipping"),
            LinkAsset(url="https://example.com/policies/refund-policy", text="Returns"),
            LinkAsset(url="https://example.com/pages/contact", text="Contact"),
            LinkAsset(url="https://example.com/pages/faq", text="FAQ"),
            LinkAsset(url="https://example.com/reviews", text="Reviews"),
        ],
        images=[
            ImageAsset(src="https://example.com/1.jpg", alt="Widget Pro front view"),
            ImageAsset(src="https://example.com/2.jpg", alt="Widget Pro side storage"),
            ImageAsset(src="https://example.com/3.jpg", alt="Widget Pro in use at work"),
            ImageAsset(src="https://example.com/4.jpg", alt="Widget Pro dimensions chart"),
            ImageAsset(src="https://example.com/5.jpg", alt="Widget Pro lifestyle image"),
        ],
        metadata=PageMetadata(
            meta_description="Shop Widget Pro with free shipping and easy returns.",
            canonical_url="https://example.com/products/widget-pro",
            structured_data_types=["Product", "FAQPage"],
            status_code=200,
            load_succeeded=True,
            mobile_screenshot_path=str(screenshot),
            desktop_screenshot_path=str(screenshot),
        ),
        headings=["Widget Pro", "Why customers love it", "FAQ"],
        cta_texts=["Add to cart", "Buy now", "Build your bundle"],
    )


@pytest.fixture()
def weak_context(rich_context: AuditContext, tmp_path: Path) -> AuditContext:
    context = copy.deepcopy(rich_context)
    context.page_title = "Shop"
    context.product_title = "Thing"
    context.price_text = ""
    context.page_text = (
        "Thing includes aluminum body. Size medium. Color blue. Weight 4 oz. "
        "Sign up for our newsletter and learn more."
    )
    context.product_description = "Compact thing."
    context.links = [LinkAsset(url="https://example.com/pages/about", text="About")]
    context.images = [ImageAsset(src="https://example.com/1.jpg", alt="")]
    context.metadata.meta_description = ""
    context.metadata.canonical_url = ""
    context.metadata.structured_data_types = []
    context.metadata.load_succeeded = False
    context.metadata.status_code = 503
    context.metadata.mobile_screenshot_path = str(tmp_path / "missing-mobile.png")
    context.headings = ["Thing"]
    context.cta_texts = []
    return context
