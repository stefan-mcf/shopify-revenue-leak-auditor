"""Page-data extraction: text, links, images, metadata, price, product detection."""

from shopify_auditor.extraction.text_extractor import (
    extract_all,
    extract_body_text,
    extract_button_texts,
    extract_headings,
    extract_meta_description,
    extract_title,
)
from shopify_auditor.extraction.link_extractor import (
    classify_link,
    extract_links,
    extract_links_classified,
    is_internal_link,
)
from shopify_auditor.extraction.image_extractor import (
    count_missing_alt,
    extract_images,
    likely_product_images,
)
from shopify_auditor.extraction.metadata_extractor import extract_metadata
from shopify_auditor.extraction.price_extractor import extract_prices
from shopify_auditor.extraction.product_detector import detect_product_page

__all__ = [
    "extract_all", "extract_title", "extract_meta_description",
    "extract_headings", "extract_body_text", "extract_button_texts",
    "extract_links", "extract_links_classified", "classify_link",
    "is_internal_link",
    "extract_images", "count_missing_alt", "likely_product_images",
    "extract_metadata",
    "extract_prices",
    "detect_product_page",
]
