"""Page-data extraction: text, links, images, metadata, price, product detection."""

from shopify_auditor.extraction.image_extractor import (
    count_missing_alt,
    extract_images,
    likely_product_images,
)
from shopify_auditor.extraction.link_extractor import (
    classify_link,
    extract_links,
    extract_links_classified,
    is_internal_link,
)
from shopify_auditor.extraction.metadata_extractor import extract_metadata
from shopify_auditor.extraction.price_extractor import extract_prices
from shopify_auditor.extraction.product_detector import detect_product_page
from shopify_auditor.extraction.text_extractor import (
    extract_all,
    extract_body_text,
    extract_button_texts,
    extract_headings,
    extract_meta_description,
    extract_title,
)

__all__ = [
    "classify_link",
    "count_missing_alt",
    "detect_product_page",
    "extract_all",
    "extract_body_text",
    "extract_button_texts",
    "extract_headings",
    "extract_images",
    "extract_links",
    "extract_links_classified",
    "extract_meta_description",
    "extract_metadata",
    "extract_prices",
    "extract_title",
    "is_internal_link",
    "likely_product_images",
]
