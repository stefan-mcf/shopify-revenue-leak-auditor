"""Utilities: URL handling, file I/O, date formatting, text helpers."""

from shopify_auditor.utils.urls import (
    get_domain,
    infer_slug_from_url,
    is_likely_product_url,
    is_valid_url,
    normalize_url,
)
from shopify_auditor.utils.files import (
    create_audit_output_dir,
    ensure_dir,
    safe_filename,
    write_json,
    write_text,
)
from shopify_auditor.utils.dates import timestamp_for_folder, utc_now_iso
from shopify_auditor.utils.text import (
    clean_whitespace,
    contains_any,
    count_words,
    truncate,
)

__all__ = [
    "normalize_url", "is_valid_url", "get_domain", "infer_slug_from_url",
    "is_likely_product_url",
    "ensure_dir", "write_text", "write_json", "safe_filename",
    "create_audit_output_dir",
    "utc_now_iso", "timestamp_for_folder",
    "clean_whitespace", "truncate", "contains_any", "count_words",
]
