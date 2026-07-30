"""Optional LLM integration package.

Core audits work without API keys.  Set ENABLE_LLM_ANALYSIS=true and provider
credentials only when adding provider-specific support.
"""

from shopify_auditor.llm.analysis import LLMAnalysis, OptionalAnalyzer
from shopify_auditor.llm.client import LLMClient

__all__ = ["LLMAnalysis", "LLMClient", "OptionalAnalyzer"]
