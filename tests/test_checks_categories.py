from shopify_auditor.checks import (
    AIReadinessCheck,
    CTAQualityCheck,
    CopyQualityCheck,
    FAQObjectionCheck,
    MobileUXCheck,
    OfferClarityCheck,
    ProductInformationCheck,
    TechnicalHealthCheck,
    TrustSignalCheck,
)
from shopify_auditor.models import AuditContext


def test_trust_signals_flags_missing_reassurance(weak_context: AuditContext) -> None:
    findings = TrustSignalCheck().run(weak_context)
    messages = " ".join(f.message.lower() for f in findings)
    assert "shipping" in messages
    assert "review" in messages


def test_copy_quality_flags_thin_feature_heavy_copy(weak_context: AuditContext) -> None:
    findings = CopyQualityCheck().run(weak_context)
    messages = " ".join(f.message.lower() for f in findings)
    assert "thin" in messages
    assert "feature-heavy" in messages


def test_offer_clarity_flags_missing_price_and_cta(weak_context: AuditContext) -> None:
    findings = OfferClarityCheck().run(weak_context)
    messages = " ".join(f.message.lower() for f in findings)
    assert "price" in messages
    assert "cta" in messages or "purchase" in messages


def test_faq_objections_suggests_missing_questions(weak_context: AuditContext) -> None:
    findings = FAQObjectionCheck().run(weak_context)
    assert any(f.suggested_questions for f in findings)
    assert any("faq" in f.message.lower() for f in findings)


def test_cta_quality_and_mobile_ux_flag_conversion_risk(weak_context: AuditContext) -> None:
    cta_findings = CTAQualityCheck().run(weak_context)
    mobile_findings = MobileUXCheck().run(weak_context)
    assert any("cta" in f.message.lower() or "purchase" in f.message.lower() for f in cta_findings)
    assert any("mobile" in f.message.lower() or "image-heavy" in f.message.lower() for f in mobile_findings)


def test_product_information_and_ai_readiness_flag_missing_structure(weak_context: AuditContext) -> None:
    product_findings = ProductInformationCheck().run(weak_context)
    ai_findings = AIReadinessCheck().run(weak_context)
    assert any("spec" in f.message.lower() or "image" in f.message.lower() for f in product_findings)
    assert any("ai shopping" in f.message.lower() or "buyer questions" in f.message.lower() for f in ai_findings)


def test_technical_health_flags_missing_metadata(weak_context: AuditContext) -> None:
    findings = TechnicalHealthCheck().run(weak_context)
    messages = " ".join(f.message.lower() for f in findings)
    assert "meta description" in messages
    assert "structured data" in messages
