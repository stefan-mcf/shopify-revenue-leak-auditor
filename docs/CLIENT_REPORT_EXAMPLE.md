# Client Report Example

This page shows the style of deliverable the tool is designed to produce. The committed full demo output lives at:

- `examples/sample_outputs/demo-product-audit/audit_report.md`
- `examples/sample_outputs/demo-product-audit/audit_report.html`
- `examples/sample_outputs/demo-product-audit/audit_data.json`

The example below is intentionally short and avoids claims of actual revenue loss or guaranteed improvement.

## Example Deliverable Summary

### Shopify Revenue Leak Audit

Audited page: `https://example.myshopify.com/products/demo-product`

Overall revenue-leak score: 64/100 - Moderate Risk

This audit reviewed the public product page for likely conversion risks across trust signals, copy quality, offer clarity, FAQ/objection handling, CTA quality, mobile UX, product information, AI-shopping readiness, and basic technical health.

The page has a workable product presentation, but the audit found several areas where buyer confidence and purchase clarity could likely be improved.

## Top Revenue Leaks

### 1. Shipping reassurance is not prominent enough

Severity: High

Why it matters: Shoppers often want to understand shipping cost and timing before committing to a purchase. If shipping reassurance is absent or hard to find, buyers may hesitate or leave the page to look for answers.

Recommendation: Add a short shipping reassurance block near the purchase area. Example: "Free shipping over $75. Ships in 1-2 business days. Easy tracking included."

### 2. FAQ and objection handling appears incomplete

Severity: High

Why it matters: Product pages that do not answer common objections can create avoidable support load and abandonment. Buyers may need clarity on returns, warranty, materials, sizing, care, or compatibility.

Recommendation: Add a concise FAQ section with answers to shipping time, returns, product fit/use, warranty, and care instructions.

### 3. Product copy is feature-heavy

Severity: Medium

Why it matters: Feature-only copy can describe what the product is without explaining why the buyer should care. Benefit-led copy helps connect product details to the shopper's desired outcome.

Recommendation: Rewrite the top product description to combine features with benefits and use cases. Add "best for" or "designed for" language.

### 4. CTA language is functional but generic

Severity: Medium

Why it matters: "Add to cart" is clear, but some products benefit from a stronger CTA that reinforces the offer or outcome.

Recommendation: Keep the standard add-to-cart button for clarity, but consider supporting microcopy nearby such as "Secure checkout" or "Start your order today."

## Category Scorecard

| Category | Score | Notes |
|---|---:|---|
| Trust Signals | 7/15 | Shipping, returns, guarantee, or support reassurance should be more visible. |
| Copy Quality | 11/15 | Copy can better connect features to buyer outcomes. |
| Offer Clarity | 11/15 | Price and CTA are present, but value framing can be clearer. |
| FAQ / Objections | 7/15 | More direct answers to buyer questions are needed. |
| CTA Quality | 8/10 | CTA exists; supporting copy could be stronger. |
| Mobile UX | 7/10 | Review mobile above-the-fold context and CTA visibility. |
| Product Information | 8/10 | Add richer specs and use-case details. |
| AI-Shopping Readiness | 3/5 | Add structured answers and clearer buyer-intent language. |
| Technical Health | 5/5 | No major basic technical issue detected in this example. |

## 7-Day Implementation Checklist

Day 1: Add shipping, returns, and support reassurance near the add-to-cart area.

Day 2: Add or expand FAQ answers for shipping time, returns, warranty, sizing/fit, materials, and care.

Day 3: Rewrite the opening product description with benefit-led copy and clearer use cases.

Day 4: Improve offer framing around price, bundles, variants, or free-shipping threshold.

Day 5: Review the mobile screenshot and move critical buying information higher on the page if needed.

Day 6: Add product specs, image alt text, and structured product answers for AI-shopping/readability.

Day 7: QA the updated page and rerun the audit to compare score and findings.

## Explanation of the Deliverable

A client-facing audit package can include:

- Markdown report for easy editing or client notes
- HTML report for visual review and screenshots
- desktop and mobile screenshots for evidence
- structured JSON for repeatable/internal analysis
- top-priority findings and a practical fix list

The report is designed to be reviewed by a human before delivery. Automated checks can highlight likely issues, but final wording should be adjusted for the actual merchant, product, traffic source, and offer context.

## Scope Boundary

This deliverable is based on public page evidence only. It does not include private analytics, customer recordings, checkout data, ad account data, or guaranteed revenue outcomes.
