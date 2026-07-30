from shopify_auditor.checks import run_all_checks
from shopify_auditor.models import AuditContext, Finding, FindingSeverity
from shopify_auditor.scoring.scorecard import build_scorecard


def test_scorecard_is_100_with_no_findings(rich_context: AuditContext) -> None:
    scorecard = build_scorecard([])
    assert scorecard.overall_score == 100
    assert scorecard.score_label == "Strong"


def test_critical_findings_reduce_score(weak_context: AuditContext) -> None:
    findings = run_all_checks(weak_context)
    scorecard = build_scorecard(findings)
    assert scorecard.overall_score < 100
    assert scorecard.critical_count >= 1


def test_penalty_is_capped_at_category_weight() -> None:
    findings = [
        Finding(
            check_id="trust_signals",
            category="trust_signals",
            severity=FindingSeverity.CRITICAL,
            message=f"Issue {index}",
            recommendation="Fix it",
            confidence=0.9,
        )
        for index in range(5)
    ]
    scorecard = build_scorecard(findings)
    assert scorecard.category_scores["trust_signals"].score == 0


def test_score_label_assignment() -> None:
    scorecard = build_scorecard(
        [
            Finding(
                check_id=f"trust-{index}",
                category="trust_signals",
                severity=FindingSeverity.CRITICAL,
                message=f"Issue {index}",
                recommendation="Add trust",
                confidence=0.9,
            )
            for index in range(2)
        ]
    )
    assert scorecard.score_label == "Good"


def test_top_priorities_prioritize_severe_findings(weak_context: AuditContext) -> None:
    findings = run_all_checks(weak_context)
    scorecard = build_scorecard(findings)
    assert scorecard.top_priorities
    assert len(scorecard.top_priorities) <= 5
    severities = [item.severity for item in scorecard.top_priorities]
    assert severities == sorted(severities, key=lambda s: s.rank)
