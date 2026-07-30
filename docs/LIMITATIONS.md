# Limitations

Shopify Revenue Leak Auditor is a public-page audit assistant. It is designed to identify likely conversion risks from observable page evidence, not to prove actual revenue loss or guarantee improvement.

## Public-Page-Only By Default

The auditor inspects public URLs only. It does not access:

- Shopify Admin data
- Shopify Analytics
- checkout analytics
- order history
- customer records
- product margin or inventory data
- customer support tickets
- email/SMS platform data
- Meta Ads, Google Ads, or TikTok Ads accounts
- heatmaps or session recordings

Any future private-data integration should require explicit merchant approval, scoped permissions, and safe credential handling.

## No Guaranteed Revenue Results

The tool can identify likely friction points, such as missing trust signals or unclear offer information. It cannot prove that those issues caused lost revenue.

Reports should not claim:

- guaranteed revenue increases
- guaranteed conversion-rate lift
- known customer behavior
- actual lost revenue
- actual ad performance
- exact impact percentages

Use wording such as:

- "likely conversion risk"
- "may reduce buyer confidence"
- "worth reviewing or testing"
- "based on public page evidence"

## Browser Extraction Limitations

Browser and HTML extraction can be affected by:

- cookie banners
- popups and overlays
- geo-specific content
- A/B tests
- personalization
- lazy-loaded sections
- anti-bot protections
- slow third-party apps
- content hidden behind tabs or accordions
- responsive layout differences

Screenshots and extracted text should be reviewed before client delivery.

## Rule-Based Analysis Limitations

The auditor relies mostly on deterministic rules and keyword/signal detection. This makes the tool predictable and usable without API keys, but it also means:

- some real issues may be missed
- some findings may be false positives
- nuance depends on human review
- findings may need severity adjustment for the actual merchant context
- category scoring is a prioritisation aid, not a scientific CRO model

## LLM Provider Boundary

No LLM provider is connected to the released CLI or API. Reports are generated
from deterministic checks and templates. Internal extension interfaces do not
constitute a supported provider integration.

## Legal and Professional Boundaries

This project does not provide:

- legal advice
- financial advice
- tax advice
- accessibility compliance certification
- privacy compliance certification
- guaranteed CRO outcomes

For regulated claims, accessibility compliance, privacy issues, or legal concerns, merchants should consult qualified professionals.

## Client Delivery Guidance

Before sending a report to a client:

1. Open the desktop and mobile screenshots.
2. Confirm findings match visible page evidence.
3. Remove or soften any automated finding that feels unfair.
4. Check that no private data or credentials appear in outputs.
5. Keep recommendations practical and testable.
6. Include the limitations/disclaimer section.
7. Avoid claiming actual revenue loss or guaranteed gains.

## Appropriate Use

Appropriate:

- deterministic product-page demonstrations
- first-pass Shopify product-page audit
- freelancer/agency audit workflow
- client discussion starter
- prioritised fix-list generation
- public-page QA support

Not appropriate as-is:

- automated legal compliance review
- guaranteed revenue diagnosis
- full CRO experimentation platform
- private analytics replacement
- autonomous store changes
- defamatory or hostile public teardown of real stores
