"""Configuration helpers."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    default_output_dir: str = os.getenv("DEFAULT_OUTPUT_DIR", "output")
    browser_headless: bool = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
    enable_llm_analysis: bool = os.getenv("ENABLE_LLM_ANALYSIS", "false").lower() == "true"
    llm_provider: str = os.getenv("LLM_PROVIDER", "")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")


def get_settings() -> Settings:
    return Settings()
