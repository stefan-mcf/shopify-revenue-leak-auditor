from shopify_auditor.models import FindingSeverity

SEVERITY_PENALTIES = {
    FindingSeverity.CRITICAL: 12,
    FindingSeverity.HIGH: 8,
    FindingSeverity.MEDIUM: 4,
    FindingSeverity.LOW: 2,
    FindingSeverity.INFO: 0,
}
