from typing import Any, Dict, Optional

from ..model_adapters.base import LLMResult, ModelAdapter, make_trimmed_context
from ..model_adapters.registry import get_adapter, get_deterministic_adapter
from ..planners.ui_planner import UIPlanner
from ..validators.a2ui_validator import A2UIValidator


class A2UIGenerator:
    """Compatibility facade over provider adapters and deterministic fixtures."""

    @classmethod
    async def handle_intent(
        cls,
        intent: str,
        prompt: str,
        current_surface_id: Optional[str] = None,
        current_surface_summary: Optional[Dict[str, Any]] = None,
        adapter: Optional[ModelAdapter] = None,
    ) -> LLMResult:
        context = make_trimmed_context(current_surface_id, current_surface_summary)
        adapter = adapter or get_adapter()
        result = await adapter.handle(intent, prompt, context)
        if result.ok and result.a2ui is not None:
            valid, error = A2UIValidator.validate_message(result.a2ui)
            if not valid:
                result.ok = False
                result.error = f"A2UI validation failed: {error}"
        if result.ok:
            return result

        # Generation can safely fall back offline. An edit/theme failure must
        # not replace or corrupt the existing surface; deterministic adapter
        # may still produce a safe delta, but only against known node ids.
        fallback_reason = result.error or "Provider returned an unusable result"
        fallback = get_deterministic_adapter()
        if intent in ("generate_new", "edit_section", "change_theme"):
            fallback_result = await fallback.handle(intent, prompt, context)
            fallback_result.fallback_reason = fallback_reason
            if fallback_result.a2ui is not None:
                valid, error = A2UIValidator.validate_message(fallback_result.a2ui)
                if not valid:
                    return LLMResult(text="Không thể áp dụng thay đổi an toàn. Hãy thử mô tả cụ thể hơn.", a2ui=None, provider="deterministic", ok=False, error=error)
            return fallback_result

        # If OpenRouter was unavailable for an inquiry, use a friendly local reply.
        fallback_result = await fallback.handle(intent, prompt, context)
        fallback_result.fallback_reason = fallback_reason
        return fallback_result

    @classmethod
    async def generate_from_llm(cls, prompt: str) -> Optional[Dict[str, Any]]:
        result = await cls.handle_intent("generate_new", prompt)
        return result.a2ui if result.ok else None

    @classmethod
    def generate_deterministic(cls, prompt: str) -> Dict[str, Any]:
        # Preserve legacy method used by older callers; deterministic generation
        # remains the canonical fallback implementation.
        from .deterministic_payloads import generate_deterministic
        return generate_deterministic(prompt)

    @classmethod
    def generate_edit_delta(cls, prompt: str, current_surface_id: str) -> Dict[str, Any]:
        from .deterministic_payloads import generate_edit_delta
        return generate_edit_delta(prompt, current_surface_id)

    @classmethod
    def classify_intent(cls, prompt: str, has_existing_surface: bool) -> str:
        return UIPlanner.classify_intent(prompt, has_existing_surface)
