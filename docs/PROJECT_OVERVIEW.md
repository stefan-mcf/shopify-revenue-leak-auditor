# Project Overview

Shopify Revenue Leak Auditor is a browser-based audit tool for public Shopify product pages and store URLs. It loads a page, captures desktop/mobile screenshots, extracts public evidence, runs rule-based ecommerce checks, scores likely conversion risks, and generates Markdown/HTML reports.

The project provides a repeatable foundation for Shopify product-page audits and client-ready reporting.

## Motivation

Shopify merchants often drive paid, organic, email, and social traffic to product pages that leave key buying questions unanswered. Common issues include:

- weak or missing trust signals
- vague product copy
- unclear shipping or returns information
- missing FAQ/objection handling
- generic or hidden purchase CTAs
- mobile pages where purchase context appears too late
- product information that is too thin for shoppers or AI-shopping surfaces

A human auditor can spot these issues, but manually collecting screenshots, extracting evidence, writing findings, and formatting reports is repetitive. This project automates the first pass so the reviewer can focus on judgement, prioritisation, and client communication.

## Intended Use Cases

Primary use cases:

1. Audit one Shopify product page and produce a client-ready report draft.
2. Audit several product/store URLs from a batch file.
3. Generate deterministic sample outputs for review, testing, and service demonstrations.
4. Support a freelancer/agency service offering: Shopify conversion revenue-leak audits.

Secondary future use cases:

- compare ad messaging against landing-page content
- provide a local API mode for other tools to call
- integrate approved Shopify Admin data for deeper merchant-owned audits
- export PDF reports for client delivery

## Architecture

High-level flow:

```text
Input URL
  -> URL validation and output directory creation
  -> Browser page load
  -> Desktop and mobile screenshot capture
  -> HTML/text/link/image/metadata/price extraction
  -> Product-page signal detection
  -> Rule-based audit checks
  -> Weighted scorecard
  -> Markdown and HTML report generation
  -> Human review before client delivery
```

Main package areas:

- `src/shopify_auditor/cli.py` - Typer CLI commands
- `src/shopify_auditor/audit_runner.py` - end-to-end audit orchestration
- `src/shopify_auditor/browser/` - Playwright loading and screenshots
- `src/shopify_auditor/extraction/` - public page extraction utilities
- `src/shopify_auditor/checks/` - audit category checks
- `src/shopify_auditor/scoring/` - severity and category-weight scoring
- `src/shopify_auditor/reports/` - Markdown/HTML report rendering
- `src/shopify_auditor/llm/` - internal extension interfaces for future provider work
- `examples/` - public-safe demo inputs and generated outputs
- `docs/` - methodology, scoring, delivery requirements, and limitations

## High-Level Workflow

1. The user provides a product/store URL through the CLI.
2. The URL is normalized and validated.
3. An audit output directory is created.
4. The page is loaded through browser automation.
5. Desktop and mobile screenshots are captured.
6. HTML and public page content are extracted.
7. Product-page signals are identified.
8. Rule-based checks produce findings with severity, confidence, evidence, and recommendations.
9. The scorecard converts findings into category scores and an overall risk label.
10. Markdown and HTML reports are written to disk.
11. A human reviews wording and evidence before using the report client-facing.

## Buyer-Relevant Outcome

The output is intended to answer a merchant-facing question:

"What likely revenue leaks are visible on this public Shopify page, and what should be fixed first?"

The report focuses on practical remediation rather than generic AI commentary. It includes an executive summary, top findings, category scorecard, detailed recommendations, screenshots, a 7-day checklist, limitations, and a disclaimer.

## Scope Boundary

This is a public-page auditor. It does not need Shopify credentials, private customer data, or ad account access. It should never imply access to analytics or guaranteed revenue impact unless those sources are explicitly integrated and approved by the merchant.
