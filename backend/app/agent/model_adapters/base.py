"""
Model adapter boundary.

A provider adapter turns a UI task (generate / edit / theme / inquiry)
into either an A2UI v1.0 message (or plain text for inquiries). The
orchestrator talks to this boundary only - adding a new native provider
(OpenAI, Anthropic, Gemini...) later means adding one adapter file,
never touching the orchestrator.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class LLMResult:
    """Result of one provider turn.

    text-only responses (chat_inquiry) carry `text` and `a2ui=None`;
    UI-producing responses carry a validated `a2ui` message (plus an
    optional short user-facing `text` note).
    """
    text: Optional[str]
    a2ui: Optional[Dict[str, Any]]
    provider: str
    ok: bool = True
    error: Optional[str] = None
    fallback_reason: Optional[str] = None


class ModelAdapter(ABC):
    """Common contract for all provider adapters."""

    name: str = "base"

    @abstractmethod
    async def available(self) -> bool:
        """Whether this adapter can serve requests in the current environment."""

    @abstractmethod
    async def handle(
        self,
        intent: str,
        prompt: str,
        trimmed_context: Optional[Dict[str, Any]] = None,
    ) -> LLMResult:
        """Execute the task for the given intent. Must never raise - return ok=False instead."""


def make_trimmed_context(
    surface_id: Optional[str],
    surface_summary: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Context Trimmer: build a minimal provider context from the surface summary.

    Only the ids and shallow props of the relevant nodes travel to the LLM -
    never the full DOM/HTML tree.
    """
    if not surface_summary:
        return {
            "surface_id": surface_id,
            "component_ids": [],
            "component_props": {},
        }

    component_ids: List[str] = list(surface_summary.get("component_ids", []))
    # Component-level props if the client provided them (it currently does not,
    # so the map stays empty rather than inventing state).
    component_props: Dict[str, Any] = dict(surface_summary.get("component_props", {}))

    return {
        "surface_id": surface_id or surface_summary.get("surfaceId"),
        "title": surface_summary.get("title"),
        "component_count": surface_summary.get("component_count", len(component_ids)),
        "component_ids": component_ids,
        "component_props": component_props,
    }
