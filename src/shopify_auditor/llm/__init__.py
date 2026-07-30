"""Internal extension interfaces for future provider-specific integrations."""

from shopify_auditor.llm.analysis import LLMAnalysis, OptionalAnalyzer
from shopify_auditor.llm.client import LLMClient

__all__ = ["LLMAnalysis", "LLMClient", "OptionalAnalyzer"]
