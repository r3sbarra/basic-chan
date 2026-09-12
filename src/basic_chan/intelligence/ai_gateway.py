"""basic_chan.intelligence.ai_gateway — Multi-provider AI gateway with fallback chaining."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseAIProvider(ABC):
    """Abstract provider for LLM completions."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        pass


class MockAIProvider(BaseAIProvider):
    """Deterministic offline fallback provider for zero-API-key environments."""

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return f"[basic-chan mock response to: {prompt[:40]}...]"


class AIGateway:
    """Unified client for dispatching prompts across model providers with automatic fallback."""

    def __init__(self, primary_provider: Optional[str] = None):
        self.primary_provider = primary_provider or os.environ.get("CHAN_AI_PROVIDER", "mock")
        self._providers: Dict[str, BaseAIProvider] = {"mock": MockAIProvider()}

    def register_provider(self, name: str, provider: BaseAIProvider) -> None:
        self._providers[name] = provider

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        # Try primary provider first, fall back to mock
        order = [self.primary_provider]
        if "mock" not in order:
            order.append("mock")

        for prov_name in order:
            prov = self._providers.get(prov_name)
            if not prov:
                continue
            try:
                return prov.generate(prompt, system_prompt)
            except Exception:
                continue

        return "[basic-chan fallback: generation unavailable]"
