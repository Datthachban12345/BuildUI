import asyncio
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from backend.app.agent.model_adapters.base import make_trimmed_context
from backend.app.agent.model_adapters.registry import get_adapter, configured_provider
from backend.app.agent.model_adapters.openrouter_adapter import (
    OpenRouterAdapter,
    _extract_completion_content,
    _flatten_nested_create_surface,
)
from backend.app.agent.validators.a2ui_validator import (
    A2UIValidator,
    MAX_COMPONENTS_PER_SURFACE,
    contains_dangerous_content,
)
from backend.app.agent.harness.orchestrator import AgentOrchestrator
from backend.app.agent.planners.ui_planner import UIPlanner


def test_trimmed_context_keeps_ids_not_dom():
    summary = {
        "surfaceId": "page-main",
        "title": "Test",
        "component_ids": ["root", "hero-title", "cta-primary"],
        "component_props": {
            "hero-title": {"component": "Heading", "props": {"text": "Old"}}
        },
    }
    ctx = make_trimmed_context("page-main", summary)
    assert ctx["component_ids"] == ["root", "hero-title", "cta-primary"]
    assert ctx["component_props"]["hero-title"]["props"]["text"] == "Old"
    # No full DOM/HTML tree is sent to providers.
    assert "html" not in json.dumps(ctx).lower()


def test_registry_defaults_to_deterministic_without_keys(monkeypatch):
    for var in ("OPENROUTER_API_KEY", "LLM_PROVIDER"):
        monkeypatch.delenv(var, raising=False)
    adapter = get_adapter()
    assert adapter.name == "deterministic"
    assert configured_provider() == "deterministic"


def test_registry_selects_openrouter_when_key_present(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-openrouter")
    monkeypatch.setenv("LLM_PROVIDER", "auto")
    adapter = get_adapter()
    assert isinstance(adapter, OpenRouterAdapter)
    assert adapter.name == "openrouter"


def test_openrouter_adapter_unavailable_without_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    adapter = OpenRouterAdapter()
    assert asyncio.run(adapter.available()) is False


def test_openrouter_completion_content_rejects_empty_or_malformed_response():
    assert _extract_completion_content({"choices": [{"message": {"content": " {\"ok\": true} "}}]}) == " {\"ok\": true} "
    assert _extract_completion_content({"choices": []}) is None
    assert _extract_completion_content({"choices": [{"message": {"content": None}}]}) is None


def test_nested_create_surface_is_flattened_to_renderable_child_ids():
    nested = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "store",
            "components": [
                {
                    "id": "root",
                    "component": "Container",
                    "children": [
                        {
                            "id": "title",
                            "component": "Heading",
                            "props": {"text": "TechNova"},
                        }
                    ],
                }
            ],
        },
    }

    normalized = _flatten_nested_create_surface(nested)
    surface = normalized["createSurface"]
    assert [component["id"] for component in surface["components"]] == ["root", "title"]
    assert surface["components"][0]["children"] == ["title"]
    assert A2UIValidator.validate_message(normalized) == (True, None)


def test_validator_rejects_unknown_child_ids():
    message = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "store",
            "components": [
                {"id": "root", "component": "Container", "children": ["missing"]},
            ],
        },
    }
    valid, error = A2UIValidator.validate_message(message)
    assert valid is False
    assert "unknown children" in error


def test_deterministic_adapter_fallback_for_generation():
    from backend.app.agent.model_adapters.deterministic_adapter import DeterministicAdapter
    adapter = DeterministicAdapter()
    result = asyncio.run(adapter.handle("generate_new", "Tạo landing page studio ảnh"))
    assert result.ok
    assert result.a2ui["createSurface"]["components"]
    valid, _ = A2UIValidator.validate_message(result.a2ui)
    assert valid is True


def test_validator_blocks_dangerous_script_payload():
    msg = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "s1",
            "catalogId": "astryx-web-v1",
            "components": [
                {"id": "root", "component": "Text", "props": {"text": "<script>alert(1)</script>"}}
            ],
        },
    }
    assert contains_dangerous_content(msg) is True
    valid, err = A2UIValidator.validate_message(msg)
    assert valid is False
    assert "forbidden" in err


def test_validator_blocks_disallowed_action():
    msg = {
        "version": "1.0",
        "updateComponents": {
            "surfaceId": "s1",
            "components": [
                {"id": "b1", "component": "Button", "props": {"label": "x", "action": "execute_shell"}}
            ],
        },
    }
    valid, err = A2UIValidator.validate_message(msg)
    assert valid is False
    assert "not in the allowed action set" in err


def test_validator_blocks_over_quota_components():
    components = [
        {"id": f"c{i}", "component": "Text", "props": {"text": "x"}}
        for i in range(MAX_COMPONENTS_PER_SURFACE + 1)
    ]
    msg = {
        "version": "1.0",
        "createSurface": {"surfaceId": "s1", "catalogId": "astryx-web-v1", "components": components},
    }
    valid, err = A2UIValidator.validate_message(msg)
    assert valid is False
    assert "Resource quota" in err


def test_sse_stream_generate_emits_typed_events(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deterministic")
    events = asyncio.run(collect_stream("Tạo landing page cho studio ảnh", None, None))
    types = [e["type"] for e in events]
    assert "console" in types
    assert "text" in types
    assert "steps" in types
    assert "a2ui" in types
    # exactly one a2ui message
    a2ui_events = [e for e in events if e["type"] == "a2ui"]
    assert len(a2ui_events) == 1
    console_events = [e["payload"] for e in events if e["type"] == "console"]
    assert any(e.get("provider") == "deterministic" for e in console_events)
    assert any(isinstance(e.get("data"), dict) and "createSurface" in e["data"] for e in console_events)
    valid, _ = A2UIValidator.validate_message(a2ui_events[0]["payload"])
    assert valid is True


def test_sse_stream_edit_emits_update_components():
    summary = {"surfaceId": "page-main", "component_ids": ["hero-title"], "title": "T"}
    events = asyncio.run(collect_stream("Sua tieu de hero", "page-main", summary))
    a2ui_events = [e for e in events if e["type"] == "a2ui"]
    assert len(a2ui_events) == 1
    assert "updateComponents" in a2ui_events[0]["payload"] or "updateDataModel" in a2ui_events[0]["payload"]


def test_sse_stream_theme_emits_data_model_only():
    summary = {"surfaceId": "page-main", "component_ids": ["root"], "title": "T"}
    events = asyncio.run(collect_stream("Doi mau sang tim", "page-main", summary))
    a2ui_events = [e for e in events if e["type"] == "a2ui"]
    assert a2ui_events
    assert "updateDataModel" in a2ui_events[0]["payload"]


def test_sse_stream_inquiry_emits_text_only():
    events = asyncio.run(collect_stream("Website nay co nhieu component khong?", "page-main", {"surfaceId": "page-main", "component_ids": ["root"], "title": "T"}))
    a2ui_events = [e for e in events if e["type"] == "a2ui"]
    assert a2ui_events == []
    assert any(e["type"] == "text" for e in events)


def test_sse_stream_reports_backend_exception_and_completes(monkeypatch):
    async def fail_request(**kwargs):
        raise RuntimeError("simulated provider failure")

    monkeypatch.setenv("LLM_PROVIDER", "deterministic")
    from backend.app.agent.generators.a2ui_generator import A2UIGenerator
    monkeypatch.setattr(A2UIGenerator, "handle_intent", fail_request)

    async def collect_raw_stream():
        return [
            line
            async for line in AgentOrchestrator.process_chat_stream("Tạo landing page", None, None)
        ]

    lines = asyncio.run(collect_raw_stream())
    events = [json.loads(line[6:]) for line in lines if line.startswith("data: {")]
    assert any(
        "Backend xử lý lỗi (RuntimeError)" in event["payload"]["message"]
        for event in events
        if event["type"] == "console"
    )
    assert lines[-1] == "data: [DONE]\n\n"


def test_facade_generate_deterministic_valid():
    from backend.app.agent.generators.a2ui_generator import A2UIGenerator
    msg = A2UIGenerator.generate_deterministic("Tạo dashboard thống kê")
    valid, _ = A2UIValidator.validate_message(msg)
    assert valid is True
    assert "createSurface" in msg


def test_facade_classify_intent():
    from backend.app.agent.generators.a2ui_generator import A2UIGenerator
    assert A2UIGenerator.classify_intent("Tạo website trà sữa", False) == "generate_new"
    assert A2UIGenerator.classify_intent("Đổi màu theme", True) == "change_theme"


async def collect_stream(prompt, surface_id, summary):
    events = []
    async for line in AgentOrchestrator.process_chat_stream(prompt, surface_id, summary):
        line = line.strip()
        if not line or not line.startswith("data:"):
            continue
        payload_raw = line[len("data:"):].strip()
        if payload_raw == "[DONE]":
            break
        events.append(json.loads(payload_raw))
    return events

