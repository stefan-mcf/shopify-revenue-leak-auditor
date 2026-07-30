# Audit Methodology

Shopify Revenue Leak Auditor uses public page inspection, browser screenshots, structured extraction, rule-based checks, weighted scoring, and report generation. The methodology is evidence-first: findings should be tied to observable public-page signals and worded as likely risks or improvement opportunities.

## Method Summary

1. Load a public URL.
2. Capture desktop and mobile screenshots.
3. Extract page text, headings, buttons, links, images, prices, metadata, and structured data.
4. Detect whether the page looks like a Shopify/product page.
5. Run category-specific checks.
6. Convert findings into a weighted scorecard.
7. Generate Markdown and HTML reports.
8. Require human review before client delivery.

## Evidence Sources

The audit can use these evidence types:

- visible-ish page text extracted from public HTML
- headings, paragraphs, buttons, and alt text
- public links and link labels
- metadata such as title, meta description, canonical URL, and OpenGraph tags
- JSON-LD/structured data where present
- likely product prices and variant language
- desktop and mobile screenshot files
- page load status and extraction quality signals

The tool should not invent analytics, conversion rates, customer behavior data, private Shopify data, or ad performance.

## Audit Categories

### Trust Signals

Checks whether the page provides visible reassurance around:

- shipping and delivery
- returns and refunds
- guarantees and warranties
- reviews and testimonials
- customer support/contact paths
- payment security and trusted payment methods

Typical finding: missing shipping or returns reassurance may reduce buyer confidence near the purchase decision.

### Copy Quality

Checks whether product copy is substantial and persuasive enough to help a buyer decide. Signals include:

- description length
- benefit-led language
- use-case language
- differentiation language
- feature-only copy risk

Typical finding: product copy appears thin or feature-heavy and may not explain who the product is for or why it is worth buying.

### Offer Clarity

Checks whether the buyer can quickly understand the offer and purchase terms. Signals include:

- price detection
- sale/discount wording
- shipping-threshold language
- variant/option clarity
- add-to-cart or buy-now language

Typical finding: the product has a price and CTA, but the surrounding value proposition or offer terms may be unclear.

### FAQ and Objection Handling

Checks for answers to common ecommerce objections:

- shipping time
- returns/refunds
- sizing or fit
- materials/quality
- warranty/guarantee
- usage/care instructions

Typical finding: no FAQ or objection-handling section was detected, so buyers may leave to answer basic questions elsewhere.

### CTA Quality

Checks whether purchase calls-to-action are present, repeated, and clear. Signals include:

- add-to-cart/buy-now text
- CTA count
- generic vs persuasive CTA language
- competing calls to action such as newsletter prompts

Typical finding: a purchase CTA exists, but only one generic CTA was detected and it may be worth strengthening or repeating.

### Mobile UX

Uses mobile screenshot presence and extracted content signals to identify likely mobile risks:

- mobile screenshot capture succeeded
- purchase CTA may be late or hard to find
- popup/promo/newsletter language may distract
- image-heavy page with limited buying information

Typical finding: mobile above-the-fold experience may not provide enough buying context before the shopper scrolls.

### Product Information Quality

Checks whether the product page has enough concrete product detail:

- product title clarity
- image count
- image alt text quality
- specs such as dimensions, size, material, capacity, ingredients, or care instructions
- use-case clarity

Typical finding: product specifications appear incomplete, creating avoidable uncertainty.

### AI-Shopping / Product Discovery Readiness

Checks whether the page is easy for search, recommendation, and AI-shopping surfaces to understand. Signals include:

- clear product title
- buyer-intent language
- direct answers to what/who/why/how questions
- shipping/return clarity
- Product structured data
- FAQ-like content

Typical finding: the page may be weak for AI-shopping discovery because it does not directly answer core product questions.

### Technical Health

Checks basic technical and extraction quality signals:

- page load status
- title and meta description
- canonical URL
- product structured data
- extracted text length

Typical finding: missing structured data or unusually short extracted content may limit audit quality and product discoverability.

## Rule-Based Checks

The core auditor uses deterministic keyword and signal checks rather than relying on an LLM. This keeps the project usable without API keys and makes test results predictable.

Rule-based checks are intentionally conservative:

- They identify likely gaps, not guaranteed causes of lost revenue.
- False positives are possible and should be reviewed by a human.
- Findings should include evidence snippets or signal descriptions where practical.
- Recommendations should be specific enough to guide a fix.

## Extension Boundary

The released CLI and API do not call an LLM provider. Internal interfaces are
kept for future provider-specific work, but they are not presented as working
product features and the core audit does not depend on them.

## Evidence-First Wording Standards

Avoid overconfident claims such as:

- "This will increase revenue by 20%."
- "Your conversion rate is low."
- "Customers hate this page."
- "This page is bad."

Prefer evidence-based language:

- "This may reduce buyer confidence."
- "This is a likely conversion risk."
- "This page may not answer a common buyer objection."
- "Consider testing this improvement."

## Human Review Policy

Before a report is used client-facing, a human should review:

- whether findings match the screenshots and extracted page evidence
- whether wording is fair and professional
- whether the recommendations are practical for the merchant
- whether any store/client-sensitive data should be removed
- whether the limitations and disclaimer are visible
