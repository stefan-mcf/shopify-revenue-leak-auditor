from __future__ import annotations

from collections import defaultdict

from shopify_auditor.models import CategoryScore, Finding, FindingSeverity, Scorecard
from shopify_auditor.scoring.severity import SEVERITY_PENALTIES
from shopify_auditor.scoring.weights import CATEGORY_WEIGHTS


def score_label_for(score: int) -> str:
    if score >= 90:
        return "Strong"
    if score >= 75:
        return "Good"
    if score >= 60:
        return "Moderate Risk"
    if score >= 40:
        return "High Risk"
    return "Severe Risk"


def build_scorecard(findings: list[Finding]) -> Scorecard:
    grouped: dict[str, list[Finding]] = defaultdict(list)
    for finding in findings:
        grouped[finding.category].append(finding)

    category_scores: dict[str, CategoryScore] = {}
    total_score = 0
    for category, weight in CATEGORY_WEIGHTS.items():
        category_findings = grouped.get(category, [])
        penalty = min(sum(SEVERITY_PENALTIES[f.severity] for f in category_findings), weight)
        score = max(weight - penalty, 0)
        category_scores[category] = CategoryScore(
            weight=weight,
            penalty=penalty,
            score=score,
            findings_count=len(category_findings),
        )
        total_score += score

    sorted_priorities = sorted(findings, key=lambda f: (f.severity.rank, -f.confidence, f.category, f.message))[:5]
    return Scorecard(
        overall_score=total_score,
        score_label=score_label_for(total_score),
        category_scores=category_scores,
        total_findings=len(findings),
        critical_count=sum(1 for f in findings if f.severity is FindingSeverity.CRITICAL),
        high_count=sum(1 for f in findings if f.severity is FindingSeverity.HIGH),
        medium_count=sum(1 for f in findings if f.severity is FindingSeverity.MEDIUM),
        low_count=sum(1 for f in findings if f.severity is FindingSeverity.LOW),
        top_priorities=sorted_priorities,
    )
