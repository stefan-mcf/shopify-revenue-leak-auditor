"""Optional LLM client facade.

The MVP must run without paid API access.  This module therefore exposes a
small disabled-by-default facade used by the optional analyzer.  Real provider
support can be added later without changing the audit pipeline contract.
"""

from __future__ import annotations

from dataclasses import dataclass

from shopify_auditor.config import get_settings


@dataclass
class LLMClient:
    """Minimal optional LLM client wrapper."""

    enabled: bool = False
    provider: str = ""
    api_key: str = ""
    timeout_seconds: int = 30

    @classmethod
    def from_env(cls, force_enable: bool = False) -> "LLMClient":
        settings = get_settings()
        enabled = bool(force_enable or settings.enable_llm_analysis) and bool(settings.llm_api_key)
        return cls(enabled=enabled, provider=settings.llm_provider, api_key=settings.llm_api_key)

    def complete(self, prompt: str) -> str:
        """Return a completion or a safe disabled message.

        No network call is made in the MVP implementation.  This keeps the core
        project deterministic and usable without credentials.
        """
        if not self.enabled:
            return "LLM analysis is disabled or not configured."
        return "LLM provider integration is not configured in this MVP build."
