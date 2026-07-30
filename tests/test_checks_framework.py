from shopify_auditor.checks import CHECK_REGISTRY, run_all_checks
from shopify_auditor.models import AuditContext, FindingSeverity


def test_registry_contains_expected_checks() -> None:
    expected = {
        "trust_signals",
        "copy_quality",
        "offer_clarity",
        "faq_objections",
        "cta_quality",
        "mobile_ux",
        "product_information",
        "ai_readiness",
        "technical_health",
    }
    assert {check.category for check in CHECK_REGISTRY} == expected


def test_run_all_checks_collects_findings(weak_context: AuditContext) -> None:
    findings = run_all_checks(weak_context)
    assert findings
    assert any(f.category == "technical_health" for f in findings)
    assert any(f.severity == FindingSeverity.CRITICAL for f in findings)
