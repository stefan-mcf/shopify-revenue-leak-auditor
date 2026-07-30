"""Utilities: URL handling, file I/O, date formatting, text helpers."""

from shopify_auditor.utils.dates import timestamp_for_folder, utc_now_iso
from shopify_auditor.utils.files import (
    create_audit_output_dir,
    ensure_dir,
    safe_filename,
    write_json,
    write_text,
)
from shopify_auditor.utils.text import (
    clean_whitespace,
    contains_any,
    count_words,
    truncate,
)
from shopify_auditor.utils.urls import (
    get_domain,
    infer_slug_from_url,
    is_likely_product_url,
    is_valid_url,
    normalize_url,
)

__all__ = [
    "clean_whitespace",
    "contains_any",
    "count_words",
    "create_audit_output_dir",
    "ensure_dir",
    "get_domain",
    "infer_slug_from_url",
    "is_likely_product_url",
    "is_valid_url",
    "normalize_url",
    "safe_filename",
    "timestamp_for_folder",
    "truncate",
    "utc_now_iso",
    "write_json",
    "write_text",
]
