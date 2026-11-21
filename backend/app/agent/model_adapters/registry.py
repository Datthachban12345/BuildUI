import os
from typing import Optional

from .base import ModelAdapter
from .deterministic_adapter import DeterministicAdapter
from .openrouter_adapter import OpenRouterAdapter


def get_adapter() -> ModelAdapter:
    """Select configured adapter. New native providers plug in here later."""
    requested = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    openrouter = OpenRouterAdapter()
    deterministic = DeterministicAdapter()

    if requested == "deterministic":
        return deterministic
    if requested in ("auto", "openrouter") and openrouter.api_key:
        return openrouter
    # Explicitly requesting OpenRouter without a key remains safely offline.
    # Future OpenAI/Anthropic/Gemini adapters can be selected in this factory.
    return deterministic


def get_deterministic_adapter() -> DeterministicAdapter:
    return DeterministicAdapter()


def configured_provider() -> str:
    return get_adapter().name
