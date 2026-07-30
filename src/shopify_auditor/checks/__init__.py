"""Audit checks and registry."""

from __future__ import annotations

from pathlib import Path

from shopify_auditor.checks.base import BaseCheck
from shopify_auditor.models import AuditContext, Finding, FindingSeverity
from shopify_auditor.scoring.weights import CATEGORY_WEIGHTS


class TrustSignalCheck(BaseCheck):
    def __init__(self) -> None:
        super().__init__("trust_signals", "trust_signals", CATEGORY_WEIGHTS["trust_signals"])

    def run(self, context: AuditContext) -> list[Finding]:
        text = context.combined_text()
        findings: list[Finding] = []
        checks = [
            (
                "shipping",
                [
                    "shipping",
                    "delivery",
                    "dispatch",
                    "free shipping",
                    "ships in",
                    "express shipping",
                ],
                "Add visible shipping reassurance near the purchase area.",
            ),
            (
                "returns",
                ["return", "returns", "refund", "exchange", "money back"],
                "Add a concise returns/refund explanation on the page.",
            ),
            (
                "guarantee",
                ["guarantee", "warranty", "risk-free", "satisfaction", "lifetime"],
                "Add a guarantee or warranty promise to reduce buyer risk.",
            ),
            (
                "review",
                ["reviews", "rated", "stars", "testimonials", "customers love", "verified buyer"],
                "Show reviews or social proof closer to the product pitch.",
            ),
            (
                "contact",
                ["contact", "support", "help", "email us", "chat"],
                "Add a clear support path or reassurance near the CTA.",
            ),
            (
                "payment",
                ["secure checkout", "payment", "ssl", "encrypted", "afterpay", "klarna", "paypal"],
                "Show secure checkout or payment-option reassurance before purchase.",
            ),
        ]
        for label, terms, recommendation in checks:
            if not (self.has_terms(text, terms) or self.has_link_matching(context, terms)):
                findings.append(
                    self.finding(
                        FindingSeverity.HIGH,
                        f"No visible {label} reassurance detected.",
                        recommendation,
                        evidence=self.evidence_from_text(text, terms, label),
                        confidence=0.86,
                    )
                )
        if findings:
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Trust information may not be close to the purchase area.",
                    "Repeat the strongest trust signals near price and CTA.",
                    confidence=0.62,
                )
            )
        return findings


class CopyQualityCheck(BaseCheck):
    def __init__(self) -> None:
        super().__init__("copy_quality", "copy_quality", CATEGORY_WEIGHTS["copy_quality"])

    def run(self, context: AuditContext) -> list[Finding]:
        desc = context.product_description or context.page_text
        analysis_text = " ".join(part for part in [desc, context.page_text] if part)
        words = len(desc.split())
        findings: list[Finding] = []
        benefits = [
            "helps",
            "designed to",
            "so you can",
            "perfect for",
            "ideal for",
            "made for",
            "improves",
            "reduces",
            "saves",
            "protects",
            "supports",
        ]
        features = [
            "includes",
            "made from",
            "material",
            "dimensions",
            "size",
            "color",
            "weight",
            "capacity",
        ]
        use_cases = ["use", "when", "everyday", "travel", "work", "gym", "home", "outdoor", "gift"]
        differentiation = [
            "unlike",
            "better than",
            "compared to",
            "unique",
            "premium",
            "handcrafted",
            "patented",
        ]
        if words < 75:
            findings.append(
                self.finding(
                    FindingSeverity.HIGH,
                    "Product copy appears thin and may not answer enough buyer questions.",
                    "Expand the product description with benefits, proof, and buyer guidance.",
                    confidence=0.92,
                )
            )
        elif words < 200:
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Product copy length is moderate but may need more depth.",
                    "Add more persuasive detail, buyer context, and proof.",
                    confidence=0.72,
                )
            )
        if self.count_terms(analysis_text, features) >= 1 and not self.has_terms(
            analysis_text, benefits
        ):
            findings.append(
                self.finding(
                    FindingSeverity.HIGH,
                    "Product copy appears feature-heavy with limited benefit language.",
                    "Translate features into outcomes and reasons to buy.",
                    confidence=0.88,
                )
            )
        if not self.has_terms(desc, use_cases):
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Use cases are not clearly explained.",
                    "Explain who the product is for and when to use it.",
                    confidence=0.8,
                )
            )
        if not self.has_terms(desc, differentiation):
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Product differentiation is weak or not explicit.",
                    "Add a clear statement about why this product is better or different.",
                    confidence=0.74,
                )
            )
        return findings


class OfferClarityCheck(BaseCheck):
    def __init__(self) -> None:
        super().__init__("offer_clarity", "offer_clarity", CATEGORY_WEIGHTS["offer_clarity"])

    def run(self, context: AuditContext) -> list[Finding]:
        text = context.combined_text()
        findings: list[Finding] = []
        if not context.price_text:
            findings.append(
                self.finding(
                    FindingSeverity.HIGH,
                    "Price could not be detected.",
                    "Make price visible near the product title and CTA.",
                    confidence=0.94,
                )
            )
        cta_terms = ["add to cart", "buy now", "checkout", "purchase"]
        if not (self.has_terms(text, cta_terms) or context.cta_texts):
            findings.append(
                self.finding(
                    FindingSeverity.CRITICAL,
                    "No clear purchase CTA detected.",
                    "Add a primary purchase CTA above the fold and near product details.",
                    confidence=0.96,
                )
            )
        if not self.has_terms(
            text,
            [
                "sale",
                "save",
                "discount",
                "off",
                "compare at",
                "was",
                "now",
                "free shipping over",
                "orders over",
                "spend",
            ],
        ):
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "No clear value or offer support around the price detected.",
                    "Explain discounts, free-shipping thresholds, or value adds near price.",
                    confidence=0.69,
                )
            )
        if self.has_terms(
            text, ["size", "colour", "color", "variant", "option", "select", "choose"]
        ) and not any(
            term in text.lower() for term in ["size guide", "choose size", "select color"]
        ):
            findings.append(
                self.finding(
                    FindingSeverity.HIGH,
                    "Product has variants/options but clarity may be weak.",
                    "Clarify variant labels and selection guidance.",
                    confidence=0.77,
                )
            )
        return findings


class FAQObjectionCheck(BaseCheck):
    def __init__(self) -> None:
        super().__init__("faq_objections", "faq_objections", CATEGORY_WEIGHTS["faq_objections"])

    def run(self, context: AuditContext) -> list[Finding]:
        text = context.combined_text()
        findings: list[Finding] = []
        suggested = [
            "How long does shipping take?",
            "What is the return policy?",
            "How does sizing or fit work?",
            "What materials are used?",
            "Is there a warranty or guarantee?",
        ]
        if not (
            self.has_terms(text, ["faq", "frequently asked", "questions", "q&a"])
            or self.has_link_matching(context, ["faq"])
        ):
            findings.append(
                self.finding(
                    FindingSeverity.HIGH,
                    "No FAQ or objection-handling section detected.",
                    "Add an FAQ section that answers the biggest purchase objections.",
                    confidence=0.93,
                    suggested_questions=suggested,
                )
            )
        objection_checks = [
            (
                "Shipping time is not clearly answered.",
                [
                    "how long",
                    "shipping time",
                    "delivery time",
                    "dispatch",
                    "arrives",
                    "estimated delivery",
                ],
            ),
            (
                "Returns/refunds are not clearly answered.",
                ["return", "refund", "exchange", "return policy"],
            ),
            (
                "Sizing or fit information may be incomplete.",
                ["sizing", "size guide", "fit", "measurements", "dimensions"],
            ),
            (
                "Product quality/materials are not sufficiently explained.",
                ["material", "ingredients", "made from", "quality", "durable", "care"],
            ),
            (
                "Warranty or guarantee details are not clearly answered.",
                ["warranty", "guarantee", "risk free", "satisfaction"],
            ),
        ]
        for message, terms in objection_checks:
            if not self.has_terms(text, terms):
                findings.append(
                    self.finding(
                        FindingSeverity.MEDIUM,
                        message,
                        "Answer this objection directly on the product page or FAQ.",
                        confidence=0.82,
                        suggested_questions=suggested,
                    )
                )
        return findings


class CTAQualityCheck(BaseCheck):
    def __init__(self) -> None:
        super().__init__("cta_quality", "cta_quality", CATEGORY_WEIGHTS["cta_quality"])

    def run(self, context: AuditContext) -> list[Finding]:
        ctas = [cta.lower() for cta in context.cta_texts] or []
        text = context.combined_text().lower()
        if not ctas:
            ctas = [
                term
                for term in ["add to cart", "add to bag", "buy now", "checkout", "purchase"]
                if term in text
            ]
        findings: list[Finding] = []
        if len(ctas) == 0:
            findings.append(
                self.finding(
                    FindingSeverity.CRITICAL,
                    "No purchase CTA detected.",
                    "Add a clear add-to-cart or buy-now CTA.",
                    confidence=0.96,
                )
            )
        elif len(ctas) == 1:
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Only one purchase CTA was detected.",
                    "Repeat the CTA after key product sections to reduce scrolling friction.",
                    confidence=0.79,
                )
            )
        persuasive = ["get yours", "start now", "claim offer", "upgrade", "build your bundle"]
        if ctas and not any(term in " ".join(ctas) for term in persuasive):
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "CTA language is generic and could be more persuasive.",
                    "Test more benefit-led CTA copy while keeping clarity.",
                    confidence=0.68,
                )
            )
        if any(
            term in text
            for term in ["subscribe", "newsletter", "sign up", "learn more", "contact us"]
        ):
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Newsletter or non-purchase CTAs may distract from the purchase path.",
                    "Reduce competing CTAs around the primary purchase action.",
                    confidence=0.7,
                )
            )
        return findings


class MobileUXCheck(BaseCheck):
    def __init__(self) -> None:
        super().__init__("mobile_ux", "mobile_ux", CATEGORY_WEIGHTS["mobile_ux"])

    def run(self, context: AuditContext) -> list[Finding]:
        text = context.combined_text().lower()
        findings: list[Finding] = []
        mobile_path = context.metadata.mobile_screenshot_path
        if not mobile_path or not Path(mobile_path).exists():
            findings.append(
                self.finding(
                    FindingSeverity.HIGH,
                    "Mobile screenshot is missing, limiting mobile UX verification.",
                    "Capture and retain a mobile screenshot for every audit.",
                    confidence=0.9,
                )
            )
        if not context.cta_texts:
            findings.append(
                self.finding(
                    FindingSeverity.HIGH,
                    "Mobile purchase CTA may not be visible early enough.",
                    "Keep a purchase CTA visible early on mobile, ideally with sticky support.",
                    confidence=0.82,
                )
            )
        if (
            len(context.images) >= max(len(context.page_text.split()) // 40, 1)
            and len(context.page_text.split()) < 120
        ):
            findings.append(
                self.finding(
                    FindingSeverity.HIGH,
                    "Page appears image-heavy with limited buying information.",
                    "Balance imagery with concise benefits, trust, and buying details above the fold.",
                    confidence=0.84,
                )
            )
        if any(term in text for term in ["subscribe", "newsletter", "popup", "sign up"]):
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Popup or newsletter content may distract from the mobile purchase flow.",
                    "Delay or minimize popup prompts on mobile product pages.",
                    confidence=0.74,
                )
            )
        return findings


class ProductInformationCheck(BaseCheck):
    def __init__(self) -> None:
        super().__init__(
            "product_information", "product_information", CATEGORY_WEIGHTS["product_information"]
        )

    def run(self, context: AuditContext) -> list[Finding]:
        findings: list[Finding] = []
        title = context.product_title.strip()
        if not title:
            findings.append(
                self.finding(
                    FindingSeverity.HIGH,
                    "Product title is missing.",
                    "Add a clear product title that identifies what the item is.",
                    confidence=0.95,
                )
            )
        elif len(title) < 5 or title.lower() in {"thing", "item", "product"}:
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Product title may be overly vague.",
                    "Use a more descriptive, buyer-readable product title.",
                    confidence=0.8,
                )
            )
        image_count = len(context.images)
        if image_count == 0:
            findings.append(
                self.finding(
                    FindingSeverity.CRITICAL,
                    "No product images were detected.",
                    "Add multiple product images showing the item and its use.",
                    confidence=0.97,
                )
            )
        elif image_count == 1:
            findings.append(
                self.finding(
                    FindingSeverity.HIGH,
                    "Only one product image was detected.",
                    "Add more product images from multiple angles and contexts.",
                    confidence=0.88,
                )
            )
        elif image_count < 5:
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Product image count may be limited for first-time buyers.",
                    "Add more images, including detail and lifestyle shots.",
                    confidence=0.72,
                )
            )
        missing_alt = sum(1 for image in context.images if not image.alt.strip())
        if context.images and missing_alt >= max(1, len(context.images) // 2):
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Product image alt text appears incomplete.",
                    "Add descriptive alt text to product imagery.",
                    confidence=0.78,
                )
            )
        text = context.combined_text()
        if not self.has_terms(
            text,
            [
                "dimensions",
                "weight",
                "size",
                "material",
                "ingredients",
                "capacity",
                "includes",
                "care",
            ],
        ):
            findings.append(
                self.finding(
                    FindingSeverity.HIGH,
                    "Product specifications appear incomplete.",
                    "Add dimensions, materials, care, or other key product specs.",
                    confidence=0.9,
                )
            )
        if not self.has_terms(
            text, ["best for", "perfect for", "ideal for", "use it for", "designed for"]
        ):
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Product use cases are not explicit.",
                    "Show who the product is for and common usage scenarios.",
                    confidence=0.76,
                )
            )
        return findings


class AIReadinessCheck(BaseCheck):
    def __init__(self) -> None:
        super().__init__("ai_readiness", "ai_readiness", CATEGORY_WEIGHTS["ai_readiness"])

    def run(self, context: AuditContext) -> list[Finding]:
        text = context.combined_text().lower()
        findings: list[Finding] = []
        answered = sum(
            1
            for terms in [
                ["what is", context.product_title.lower() if context.product_title else ""],
                ["perfect for", "ideal for", "designed for", "made for"],
                ["helps", "improves", "reduces", "protects", "saves"],
                ["how to use", "use it for", "instructions"],
                ["shipping", "return", "refund"],
                ["size", "color", "variant", "option"],
            ]
            if any(term and term in text for term in terms)
        )
        if answered < 4:
            findings.append(
                self.finding(
                    FindingSeverity.HIGH,
                    "Product page may be weak for AI shopping because core buyer questions are not directly answered.",
                    "Answer what it is, who it is for, why buy it, how it is used, shipping/returns, and variant details in plain language.",
                    confidence=0.88,
                )
            )
        if "product" not in [item.lower() for item in context.metadata.structured_data_types]:
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Structured product metadata was not detected for AI-readable discovery surfaces.",
                    "Add Product JSON-LD structured data to help search and AI systems interpret the page.",
                    confidence=0.84,
                )
            )
        if not any(
            q in text for q in ["how", "what", "when", "where", "can i", "does it", "is it"]
        ):
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "FAQ-like buyer answers are limited.",
                    "Add question-style answers that mirror shopper research queries.",
                    confidence=0.71,
                )
            )
        return findings


class TechnicalHealthCheck(BaseCheck):
    def __init__(self) -> None:
        super().__init__(
            "technical_health", "technical_health", CATEGORY_WEIGHTS["technical_health"]
        )

    def run(self, context: AuditContext) -> list[Finding]:
        findings: list[Finding] = []
        meta = context.metadata
        word_count = len(context.page_text.split())
        if not meta.load_succeeded or (meta.status_code and meta.status_code >= 400):
            findings.append(
                self.finding(
                    FindingSeverity.CRITICAL,
                    "Page load failed or returned an unhealthy status.",
                    "Fix page availability before relying on the audit or sending traffic to this URL.",
                    confidence=0.97,
                )
            )
        if not context.page_title:
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Page title was not detected.",
                    "Add a descriptive page title.",
                    confidence=0.88,
                )
            )
        elif len(context.page_title.split()) < 2:
            findings.append(
                self.finding(
                    FindingSeverity.LOW,
                    "Page title appears very short.",
                    "Expand the title so it better describes the product page.",
                    confidence=0.67,
                )
            )
        if not meta.meta_description:
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Meta description was not detected.",
                    "Add a clear meta description for search previews and audit completeness.",
                    confidence=0.86,
                )
            )
        elif len(meta.meta_description.split()) < 8:
            findings.append(
                self.finding(
                    FindingSeverity.LOW,
                    "Meta description appears very short.",
                    "Expand the meta description with buyer-relevant detail.",
                    confidence=0.62,
                )
            )
        if not meta.canonical_url:
            findings.append(
                self.finding(
                    FindingSeverity.LOW,
                    "Canonical URL was not detected.",
                    "Add a canonical URL to avoid ambiguity across product variants or duplicates.",
                    confidence=0.69,
                )
            )
        if "product" not in [item.lower() for item in meta.structured_data_types]:
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Product structured data was not detected.",
                    "Add Product schema markup for richer search interpretation.",
                    confidence=0.83,
                )
            )
        if word_count < 100:
            findings.append(
                self.finding(
                    FindingSeverity.HIGH,
                    "Extracted page text is very short; product page may lack enough purchase information.",
                    "Increase crawlable product content and verify extraction quality.",
                    confidence=0.9,
                )
            )
        elif word_count < 300:
            findings.append(
                self.finding(
                    FindingSeverity.MEDIUM,
                    "Extracted page text is somewhat limited.",
                    "Add more purchase-oriented content, specs, and support answers.",
                    confidence=0.7,
                )
            )
        return findings


CHECK_REGISTRY = [
    TrustSignalCheck(),
    CopyQualityCheck(),
    OfferClarityCheck(),
    FAQObjectionCheck(),
    CTAQualityCheck(),
    MobileUXCheck(),
    ProductInformationCheck(),
    AIReadinessCheck(),
    TechnicalHealthCheck(),
]


def run_all_checks(context: AuditContext) -> list[Finding]:
    findings: list[Finding] = []
    for check in CHECK_REGISTRY:
        findings.extend(check.run(context))
    return findings


__all__ = [
    "CHECK_REGISTRY",
    "AIReadinessCheck",
    "BaseCheck",
    "CTAQualityCheck",
    "CopyQualityCheck",
    "FAQObjectionCheck",
    "MobileUXCheck",
    "OfferClarityCheck",
    "ProductInformationCheck",
    "TechnicalHealthCheck",
    "TrustSignalCheck",
    "run_all_checks",
]
