# Scoring Rubric

The scorecard turns audit findings into a 100-point revenue-leak risk score. The model is intentionally simple and explainable so a client can understand why the page received its score.

## Category Weights

| Category | Weight |
|---|---:|
| Trust Signals | 15 |
| Copy Quality | 15 |
| Offer Clarity | 15 |
| FAQ / Objection Handling | 15 |
| CTA Quality | 10 |
| Mobile UX | 10 |
| Product Information Quality | 10 |
| AI-Shopping Readiness | 5 |
| Technical Health | 5 |
| Total | 100 |

Higher-weight categories represent areas that commonly affect buyer confidence and purchase readiness on a Shopify product page.

## Severity Levels

| Severity | Meaning |
|---|---|
| Critical | Likely to directly block purchase action or create major buyer uncertainty. |
| High | Likely to reduce trust, clarity, or conversion confidence. |
| Medium | Noticeable improvement opportunity that should be addressed. |
| Low | Minor optimisation or polish issue. |
| Info | Neutral observation or audit context; no score penalty. |

## Severity Penalties

| Severity | Penalty |
|---|---:|
| Critical | 12 |
| High | 8 |
| Medium | 4 |
| Low | 2 |
| Info | 0 |

Penalties are applied inside each category and capped by that category's weight. This prevents one category from driving the total score below zero or dominating unrelated categories.

Example:

- Trust Signals weight: 15
- Findings: one High issue and two Medium issues
- Raw penalty: 8 + 4 + 4 = 16
- Capped penalty: 15
- Trust Signals category score: 0/15

## Overall Score

The total score is calculated as:

```text
overall_score = sum(category_weight - capped_category_penalty)
```

A page with no findings scores 100. A page with many severe findings scores lower, with category penalties capped by their configured weights.

## Score Labels

| Score Range | Label | Interpretation |
|---:|---|---|
| 90-100 | Strong | The page has a solid public-facing foundation with minor optimisation opportunities. |
| 75-89 | Good | The page is usable but has several clear conversion improvements available. |
| 60-74 | Moderate Risk | Several likely revenue leaks exist and should be prioritised. |
| 40-59 | High Risk | The page likely needs substantial trust, copy, offer, or UX work. |
| 0-39 | Severe Risk | The page may fail to answer core buyer questions or support purchase confidence. |

## Top Priorities

Top priorities should be selected from the most severe and commercially relevant findings. Suggested ordering:

1. Critical findings
2. High severity findings
3. Findings in high-weight categories
4. Repeated issues across trust, FAQ, offer clarity, and CTA
5. Medium issues that are quick to fix and client-relevant

## Commercial Interpretation

The score is not a conversion-rate estimate. It is a structured public-page risk score.

A low score means the page has more visible evidence of likely conversion friction. It does not prove revenue loss. A higher score means fewer obvious issues were detected by the available checks. It does not guarantee strong revenue performance.

## Client-Safe Wording

Use the score as a prioritisation aid:

- "The page scored 62/100, indicating moderate visible revenue-leak risk."
- "The largest score reductions came from FAQ, trust, and offer clarity gaps."
- "These are recommended fixes to review and test, not guaranteed revenue outcomes."

Avoid:

- "This score proves your page is losing sales."
- "Fixing these issues will increase revenue by X%."
- "Your conversion rate is bad."

## Human Review

The scoring model is deterministic and useful for consistent triage, but human review should confirm:

- whether the finding is fair for the actual page context
- whether the severity feels commercially reasonable
- whether evidence snippets support the recommendation
- whether any automated false positives should be softened or removed
