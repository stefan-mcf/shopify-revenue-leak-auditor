# Shopify Revenue Leak Audit Report

**Date:** {{ result.audit_timestamp }}
**Shop URL:** {{ result.input_url }}
**Final URL:** {{ result.final_url }}
**Domain:** {{ result.domain }}

## Executive Summary

This audit reviewed the product page for likely revenue leaks across trust, copy, offer clarity, objection handling, CTA quality, mobile UX, product information, AI-shopping readiness, and basic technical health. Findings are based on public page evidence and are prioritized for practical implementation. Recommendations should be human-reviewed before implementation.

## Overall Score

**Score:** {{ overall_score }}/100
**Interpretation:** {{ score_label }}

## Top Revenue Leak Findings
{% if top_findings %}
{% for finding in top_findings %}
{{ loop.index }}. **{{ finding.severity.value|title }} — {{ finding.title }}**
   Recommendation: {{ finding.recommendation }}
{% endfor %}
{% else %}
No major revenue leaks were detected by the rule-based checks.
{% endif %}

## Category Scorecard
{% for row in category_scores %}
- **{{ row.label }}:** {{ row.score }}/{{ row.weight }} ({{ row.count }} finding{% if row.count != 1 %}s{% endif %})
{% endfor %}

## Detailed Findings by Category
{% for key, label in category_labels.items() %}
### {{ label }}
{% set items = findings_by_category[key] %}
{% if items %}
{% for finding in items %}
- **{{ finding.severity.value|title }}: {{ finding.title }}**
  - Evidence confidence: {{ '%.0f'|format(finding.confidence * 100) }}%
  - Why it matters: {{ finding.description }}
  - Recommendation: {{ finding.recommendation }}
{% endfor %}
{% else %}
- No issues detected by this rule set.
{% endif %}
{% endfor %}

## 7-Day Implementation Checklist

- **Day 1:** Fix the highest-priority trust and purchase-blocking issues.
- **Day 2:** Add or improve FAQ answers for shipping, returns, sizing, warranty, and product use.
- **Day 3:** Improve benefit-led copy and product differentiation.
- **Day 4:** Clarify offer, price support, variants, and CTA hierarchy.
- **Day 5:** Review mobile presentation and reduce purchase-path friction.
- **Day 6:** Add product specs, metadata, alt text, and AI-shopping readable answers.
- **Day 7:** QA changes, retest the page, and review the report manually.

## Screenshots

- Desktop screenshot: {{ result.screenshot_paths.get('desktop', 'not captured') }}
- Mobile screenshot: {{ result.screenshot_paths.get('mobile', 'not captured') }}

{% if llm_analysis %}
## LLM Analysis (Optional)

{{ llm_analysis }}
{% endif %}

## Limitations

This audit is based on public page inspection and automated analysis. It does not access private Shopify analytics, checkout analytics, customer behavior recordings, heatmaps, ad accounts, or customer support data unless separately integrated.

## Disclaimer

This report identifies likely conversion and revenue-leak issues. It does not guarantee revenue improvement.
