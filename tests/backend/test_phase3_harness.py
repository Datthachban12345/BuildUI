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
    _has_visible_content,
)
from backend.app.agent.prompts.apple_designer import AppleDesignerPrompt
from backend.app.agent.generators.polish import polish_create_surface
from backend.app.agent.validators.a2ui_validator import (
    A2UIValidator,
    MAX_COMPONENTS_PER_SURFACE,
    contains_dangerous_content,
)
from backend.app.agent.validators.design_validator import assess_design_quality
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


def test_nested_normalizer_prefers_tree_edges_over_flat_root_child_list():
    message = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "store",
            "components": [
                {
                    "id": "root",
                    "component": "Container",
                    "props": {
                        "children": ["navbar", "hero", "main-content", "footer"],
                    },
                    "children": [
                        "navbar", "hero", "main-content", "footer",
                        "brand", "hero-title", "product-grid", "product-card",
                    ],
                },
                {"id": "navbar", "component": "Container", "children": ["brand"]},
                {"id": "brand", "component": "Heading", "props": {"text": "Store"}},
                {"id": "hero", "component": "Container", "children": ["hero-title"]},
                {"id": "hero-title", "component": "Heading", "props": {"text": "Welcome"}},
                {"id": "main-content", "component": "Container", "children": ["product-grid"]},
                {"id": "product-grid", "component": "Grid", "children": ["product-card"]},
                {"id": "product-card", "component": "Card", "props": {"title": "Product"}},
                {"id": "footer", "component": "Container"},
            ],
        },
    }

    normalized = _flatten_nested_create_surface(message)
    components = {node["id"]: node for node in normalized["createSurface"]["components"]}
    assert components["root"]["children"] == ["navbar", "hero", "main-content", "footer"]
    assert components["navbar"]["children"] == ["brand"]
    assert components["main-content"]["children"] == ["product-grid"]
    assert "children" not in components["root"]["props"]
    assert A2UIValidator.validate_message(normalized) == (True, None)


def test_unknown_component_aliases_are_mapped_to_catalog_components():
    nested = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "store",
            "components": [{
                "id": "root",
                "component": "div",
                "children": [
                    {"id": "hero-title", "component": "h1", "text": "TechNova"},
                    {
                        "id": "product-card",
                        "component": "ProductCard",
                        "props": {"name": "MacBook Pro M4", "description": "Laptop cao cấp"},
                        "children": [
                            {"id": "product-photo", "component": "img", "src": "/images/macbook.jpg"},
                        ],
                    },
                    {
                        "id": "feature-card",
                        "component": "FeatureCard",
                        "props": {"title": "Giao hàng nhanh", "description": "Toàn quốc"},
                    },
                ],
            }],
        },
    }

    normalized = _flatten_nested_create_surface(nested)
    components = {component["id"]: component for component in normalized["createSurface"]["components"]}
    assert components["root"]["component"] == "Container"
    assert components["hero-title"]["component"] == "Heading"
    assert components["hero-title"]["props"]["text"] == "TechNova"
    assert components["product-card"]["component"] == "Card"
    assert components["product-photo"]["component"] == "Image"
    assert components["product-photo"]["props"]["src"] == "/images/macbook.jpg"
    assert components["feature-card"]["component"] == "Card"
    assert A2UIValidator.validate_message(normalized) == (True, None)


def test_nested_create_surface_drops_broken_nodes_and_repairs_references():
    malformed = {
        "version": "1.0",
        "createSurface": {
            "components": [
                {
                    "id": "page",
                    "component": "Container",
                    "children": [
                        {
                            "id": "missing-component",
                            "children": [
                                {
                                    "id": "salvaged-title",
                                    "component": "Heading",
                                    "props": {"text": "TechNova"},
                                }
                            ],
                        },
                        {"component": "Text", "props": {"text": "drop: no id"}},
                        "missing-reference",
                    ],
                }
            ],
        },
    }

    normalized = _flatten_nested_create_surface(malformed)
    surface = normalized["createSurface"]
    components = {component["id"]: component for component in surface["components"]}

    assert surface["surfaceId"] == "page-main"
    assert components["root"]["children"] == ["page"]
    assert components["page"]["children"] == ["salvaged-title"]
    assert set(components) == {"root", "page", "salvaged-title"}
    assert A2UIValidator.validate_message(normalized) == (True, None)


def test_root_only_create_surface_is_not_renderable():
    empty_surface = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "store",
            "components": [
                {"id": "root", "component": "Container", "children": []},
            ],
            "dataModel": {"products": [{"name": "Laptop"}]},
        },
    }
    valid, error = A2UIValidator.validate_message(empty_surface)
    assert valid, error
    assert not _has_visible_content(empty_surface)

    visible_surface = _flatten_nested_create_surface({
        "version": "1.0",
        "createSurface": {
            "surfaceId": "store",
            "components": [
                {
                    "id": "root",
                    "component": "Container",
                    "children": [
                        {"id": "title", "component": "Heading", "props": {"text": "Store"}},
                    ],
                },
            ],
        },
    })
    assert _has_visible_content(visible_surface)


def test_root_only_surface_triggers_corrective_retry_not_template(monkeypatch):
    """A createSurface with no visible content gets a corrective retry asking
    the model to render real sections - no hard-coded template is injected."""
    import backend.app.agent.model_adapters.openrouter_adapter as adapter_mod

    class FakeResponse:
        status_code = 200

        def __init__(self):
            self.content = json.dumps({
                "version": "1.0",
                "createSurface": {
                    "surfaceId": "store",
                    "components": [
                        {"id": "root", "component": "Container"},
                    ],
                    "dataModel": {"products": [{"name": "Laptop"}]},
                },
            })

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def aread(self):
            return b""

        async def aiter_lines(self):
            delta = {"choices": [{"delta": {"content": self.content}}]}
            yield f"data: {json.dumps(delta)}"
            yield "data: [DONE]"

    class FakeAsyncClient:
        requests = []

        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        def stream(self, method, url, headers, json):
            self.requests.append(json)
            return FakeResponse()

    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-openrouter")
    monkeypatch.setattr("backend.app.agent.model_adapters.openrouter_adapter.httpx.AsyncClient", FakeAsyncClient)

    result = asyncio.run(OpenRouterAdapter().handle("generate_new", "Tạo cửa hàng công nghệ"))

    # No template injection: the adapter reports the empty-content failure so
    # the generator falls back deterministically instead.
    assert result.ok is False
    assert "no visible content" in result.error
    # Corrective retry was attempted per attempt.
    max_attempts = adapter_mod._MAX_ATTEMPTS
    assert len(FakeAsyncClient.requests) == max_attempts
    # The corrective turn mentioned adding real content.
    last_messages = FakeAsyncClient.requests[-1]["messages"]
    corrective = [m for m in last_messages if m["role"] == "user" and "visible content" in m["content"]]
    assert corrective, "expected a corrective turn asking for real section content"


@pytest.mark.parametrize(
    "props",
    [
        {"cols": 3, "gap": "lg"},
        {"cols": {"base": 1, "sm": 2, "lg": 4}, "gap": "md"},
        {"paddingX": "lg", "maxWidth": "xl"},
        {"variant": "elevated"},
    ],
)
def test_a2ui_validator_accepts_design_contract_props(props):
    component = "Grid"
    if "paddingX" in props:
        component = "Container"
    elif "variant" in props:
        component = "Card"
    message = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "contract",
            "components": [{"id": "root", "component": component, "props": props}],
        },
    }

    assert A2UIValidator.validate_message(message) == (True, None)


@pytest.mark.parametrize(
    ("component", "props", "expected_error"),
    [
        ("Grid", {"cols": {"base": 1, "tablet": 3}}, "unsupported breakpoints"),
        ("Grid", {"cols": {"base": 5}}, "integers from 1 to 4"),
        ("Card", {"variant": "glass"}, "variant is not supported"),
        ("Image", {"fit": "stretch"}, "fit is not supported"),
        ("Container", {"paddingX": "xl"}, "paddingX is not supported"),
        ("Text", {"className": "px-2.5"}, "4px-based"),
        ("Text", {"className": "mt-[13px]"}, "4px-based"),
    ],
)
def test_a2ui_validator_rejects_out_of_contract_design_props(component, props, expected_error):
    message = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "contract",
            "components": [{"id": "root", "component": component, "props": props}],
        },
    }

    valid, error = A2UIValidator.validate_message(message)
    assert not valid
    assert expected_error in error


def test_openrouter_stream_emits_surface_before_completion(monkeypatch):
    class FakeResponse:
        status_code = 200

        def __init__(self):
            self.deltas = [
                '{"version":"1.0","createSurface":{"surfaceId":"page-main","title":"Test",'
                '"components":[{"id":"root","component":"Container","children":["hero","content"]},',
                '{"id":"hero","component":"Heading","props":{"text":"Hello"}},',
                '{"id":"content","component":"Text","props":{"text":"Welcome"}}]}}',
            ]

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def aread(self):
            return b""

        async def aiter_lines(self):
            for content in self.deltas:
                yield f'data: {json.dumps({"choices": [{"delta": {"content": content}}]})}'
            yield "data: [DONE]"

    class FakeAsyncClient:
        requests = []

        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        def stream(self, method, url, headers, json):
            self.requests.append(json)
            return FakeResponse()

    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-openrouter")
    monkeypatch.setattr(
        "backend.app.agent.model_adapters.openrouter_adapter.httpx.AsyncClient",
        FakeAsyncClient,
    )
    progress = []

    async def report(event):
        progress.append(event)

    result = asyncio.run(OpenRouterAdapter().handle(
        "generate_new",
        "Tạo website",
        progress_callback=report,
    ))

    assert result.ok
    assert FakeAsyncClient.requests[0]["stream"] is True
    assert progress[0]["type"] == "a2ui"
    initial = progress[0]["payload"]["createSurface"]
    initial_components = {node["id"]: node for node in initial["components"]}
    assert initial_components["root"]["children"] == ["hero", "content"]
    assert initial_components["hero"]["component"] == "Container"
    assert any(event["payload"].get("updateComponents") for event in progress[1:])


def test_design_quality_gate_identifies_missing_commerce_composition():
    message = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "page-main",
            "components": [
                {"id": "root", "component": "Container", "children": ["navbar", "hero", "products"]},
                {"id": "navbar", "component": "Container"},
                {"id": "hero", "component": "Container", "children": ["hero-title"]},
                {"id": "hero-title", "component": "Heading", "props": {"level": 1, "text": "Điện thoại"}},
                {"id": "products", "component": "Grid", "children": ["phone-card"]},
                {"id": "phone-card", "component": "Card", "props": {"title": "Phone", "description": "Flagship"}},
            ],
        },
    }

    issues = assess_design_quality(message, "Tạo website thương mại điện tử bán điện thoại")
    assert any("call-to-action" in issue for issue in issues)
    assert any("Image" in issue for issue in issues)
    assert any("prices" in issue for issue in issues)
    assert not any("three distinct" in issue or "level-1" in issue for issue in issues)


def test_generation_prompt_builds_domain_specific_design_brief():
    prompt = AppleDesignerPrompt.generation_user_prompt("Tạo shop bán giày thủ công, phong cách tối giản")
    assert "internally turn it into a short design brief" in prompt
    assert "domain-specific art direction" in prompt
    assert "Tạo shop bán giày thủ công" in prompt
    assert "product/purchase Button" in AppleDesignerPrompt.system()


def test_openrouter_retries_structurally_weak_design_without_discarding_it(monkeypatch):
    weak_surface = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "page-main",
            "title": "Shop",
            "components": [
                {"id": "root", "component": "Container", "children": ["navbar", "hero", "products"]},
                {"id": "navbar", "component": "Container"},
                {"id": "hero", "component": "Container", "children": ["hero-title"]},
                {"id": "hero-title", "component": "Heading", "props": {"level": 1, "text": "Thiết bị"}},
                {"id": "products", "component": "Grid", "children": ["phone-card"]},
                {"id": "phone-card", "component": "Card", "props": {"title": "Phone", "description": "Flagship"}},
            ],
        },
    }
    improved_surface = json.loads(json.dumps(weak_surface))
    improved_components = improved_surface["createSurface"]["components"]
    improved_components[1]["props"] = {"className": "py-8"}
    improved_components[2]["props"] = {"className": "py-20"}
    improved_components[2]["children"].extend(["hero-copy", "hero-cta"])
    improved_components.extend([
        {"id": "hero-copy", "component": "Text", "props": {"text": "Thiết bị phù hợp mỗi ngày."}},
        {"id": "hero-cta", "component": "Button", "props": {"label": "Khám phá", "variant": "primary"}},
    ])
    improved_components[-1]["children"] = ["phone-image", "phone-price", "phone-buy"]
    improved_components.extend([
        {"id": "phone-image", "component": "Image", "props": {"alt": "Phone", "ratio": "square"}},
        {"id": "phone-price", "component": "Text", "props": {"text": "₫12.000.000"}},
        {"id": "phone-buy", "component": "Button", "props": {"label": "Mua ngay", "variant": "primary"}},
    ])
    outputs = [json.dumps(weak_surface), json.dumps(improved_surface)]

    class FakeResponse:
        status_code = 200

        def __init__(self, content):
            self.content = content

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def aread(self):
            return b""

        async def aiter_lines(self):
            yield f'data: {json.dumps({"choices": [{"delta": {"content": self.content}}]})}'
            yield "data: [DONE]"

    class FakeAsyncClient:
        requests = []

        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        def stream(self, method, url, headers, json):
            self.requests.append(json)
            return FakeResponse(outputs[len(self.requests) - 1])

    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-openrouter")
    monkeypatch.setattr(
        "backend.app.agent.model_adapters.openrouter_adapter.httpx.AsyncClient",
        FakeAsyncClient,
    )
    result = asyncio.run(OpenRouterAdapter().handle(
        "generate_new",
        "Tạo website thương mại điện tử bán điện thoại",
    ))

    assert result.ok
    assert result.quality_warnings is None
    assert len(FakeAsyncClient.requests) == 2
    correction = FakeAsyncClient.requests[1]["messages"][-1]["content"]
    assert "Design quality review" in correction
    assert "product prices" in correction
    assert result.a2ui["createSurface"]["components"][-1]["component"] == "Button"


def test_root_only_surface_has_no_visible_content():
    empty_surface = _flatten_nested_create_surface({
        "version": "1.0",
        "createSurface": {
            "surfaceId": "store",
            "components": [{"id": "root", "component": "Container"}],
        },
    })
    assert not _has_visible_content(empty_surface)


def test_polish_fills_missing_spacing_and_typography():
    """The design-system polisher adds Apple tokens only where missing."""
    message = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "page-main",
            "catalogId": "astryx-web-v1",
            "components": [
                {"id": "root", "component": "Container", "children": ["hero", "pricing"]},
                {"id": "hero", "component": "Container", "children": ["hero-title"]},
                {"id": "hero-title", "component": "Heading", "props": {"level": 1, "text": "X"}},
                {"id": "pricing", "component": "Grid", "props": {"cols": 2}, "children": []},
            ],
        },
    }
    # An already-styled section that must NOT be touched.
    message["createSurface"]["components"].append(
        {"id": "styled", "component": "Container",
         "props": {"className": "px-4 py-6"}, "children": []})
    polished = polish_create_surface(message)
    by_id = {c["id"]: c for c in polished["createSurface"]["components"]}
    assert by_id["root"]["props"]["className"] == "bg-white"
    # Unstyled top-level sections get the Apple rhythm.
    assert "py-20" in by_id["hero"]["props"]["className"]
    assert "py-20" in by_id["pricing"]["props"]["className"]
    # Unstyled heading gets the type scale.
    assert "text-5xl" in by_id["hero-title"]["props"]["className"]
    # Already-styled node is untouched.
    assert by_id["styled"]["props"]["className"] == "px-4 py-6"
    valid, _ = A2UIValidator.validate_message(polished)
    assert valid is True


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


def test_deterministic_ecommerce_fallback_uses_brand_and_products_from_prompt():
    from backend.app.agent.generators.deterministic_payloads import generate_deterministic

    prompt = """Tạo website thương mại điện tử bán thiết bị công nghệ.
Tên thương hiệu: TechNova.
Dữ liệu mẫu:
Tạo ít nhất 2 sản phẩm:
- MacBook Pro M4
- Sony WH-1000XM6
"""
    message = generate_deterministic(prompt)
    surface = message["createSurface"]
    components = {component["id"]: component for component in surface["components"]}
    assert surface["title"] == "TechNova - Thiết bị công nghệ"
    assert components["navbar-brand"]["props"]["text"] == "TechNova"
    assert components["product-1"]["props"]["title"] == "MacBook Pro M4"
    assert components["product-2"]["props"]["title"] == "Sony WH-1000XM6"
    assert "LUMEN" not in json.dumps(message)
    assert A2UIValidator.validate_message(message) == (True, None)


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


def test_schema_validator_rejects_duplicate_parents_cycles_and_unsafe_images():
    def create_surface(components):
        return {
            "version": "1.0",
            "createSurface": {"surfaceId": "test", "components": components},
        }

    duplicate_parent = create_surface([
        {"id": "root", "component": "Container", "children": ["left", "right"]},
        {"id": "left", "component": "Container", "children": ["shared"]},
        {"id": "right", "component": "Container", "children": ["shared"]},
        {"id": "shared", "component": "Text", "props": {"text": "x"}},
    ])
    valid, error = A2UIValidator.validate_message(duplicate_parent)
    assert not valid and "multiple parents" in error

    cyclic = create_surface([
        {"id": "root", "component": "Container", "children": ["section"]},
        {"id": "section", "component": "Container", "children": ["root"]},
    ])
    valid, error = A2UIValidator.validate_message(cyclic)
    assert not valid and "cycles" in error

    unsafe_image = create_surface([
        {"id": "root", "component": "Container", "children": ["image"]},
        {"id": "image", "component": "Image", "props": {"src": "data:image/png;base64,abc"}},
    ])
    valid, error = A2UIValidator.validate_message(unsafe_image)
    assert not valid and "relative or HTTP(S)" in error


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
    monkeypatch.setenv("LIVE_ASSEMBLY_BLOCK_DELAY", "0")
    events = asyncio.run(collect_stream("Tạo landing page cho studio ảnh", None, None))
    types = [e["type"] for e in events]
    assert "console" in types
    assert "text" in types
    assert "steps" in types
    assert "a2ui" in types
    console_events = [e["payload"] for e in events if e["type"] == "console"]
    assert any(e.get("provider") == "deterministic" for e in console_events)
    assert any(isinstance(e.get("data"), dict) and "createSurface" in e["data"] for e in console_events)


def test_sse_generate_streams_live_assembly_blocks(monkeypatch):
    """Phase 4: generate_new streams a skeleton then one block per section."""
    monkeypatch.setenv("LLM_PROVIDER", "deterministic")
    monkeypatch.setenv("LIVE_ASSEMBLY_BLOCK_DELAY", "0")
    events = asyncio.run(collect_stream("Tạo landing page cho studio ảnh", None, None))
    a2ui_events = [e for e in events if e["type"] == "a2ui"]
    assert len(a2ui_events) >= 4, "expected skeleton + at least 3 section blocks"

    # Block 0 is the createSurface skeleton (root + empty section containers).
    first = a2ui_events[0]["payload"]
    assert "createSurface" in first
    skeleton_components = {c["id"] for c in first["createSurface"]["components"]}
    assert "root" in skeleton_components
    # every block must validate on its own
    for event in a2ui_events[1:]:
        assert "updateComponents" in event["payload"]
        valid, err = A2UIValidator.validate_message(event["payload"])
        assert valid, err
    valid, err = A2UIValidator.validate_message(first)
    assert valid, err

    # Replaying every block through a runtime-like reducer rebuilds the
    # complete surface (no node lost during assembly).
    from backend.app.agent.generators.deterministic_payloads import generate_deterministic
    complete = generate_deterministic("Tạo landing page cho studio ảnh")
    expected_ids = {c["id"] for c in complete["createSurface"]["components"]}
    seen: set = set()
    for event in a2ui_events:
        payload = event["payload"]
        if "createSurface" in payload:
            seen.update(c["id"] for c in payload["createSurface"]["components"])
        else:
            seen.update(c["id"] for c in payload["updateComponents"]["components"])
    assert expected_ids <= seen


def test_sse_forwards_model_surface_before_completion(monkeypatch):
    from backend.app.agent.model_adapters.base import LLMResult

    final_message = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "page-main",
            "catalogId": "astryx-web-v1",
            "title": "Streamed",
            "components": [
                {"id": "root", "component": "Container", "children": ["hero", "content"]},
                {"id": "hero", "component": "Heading", "props": {"text": "Hello"}},
                {"id": "content", "component": "Text", "props": {"text": "Welcome"}},
            ],
        },
    }

    class StreamingAdapter:
        name = "openrouter"
        model = "test/streaming"

        async def available(self):
            return True

        async def handle(self, intent, prompt, trimmed_context=None, progress_callback=None):
            await progress_callback({
                "type": "a2ui",
                "payload": {
                    "version": "1.0",
                    "createSurface": {
                        "surfaceId": "page-main",
                        "catalogId": "astryx-web-v1",
                        "title": "Streamed",
                        "components": [
                            {"id": "root", "component": "Container", "children": ["hero", "content"]},
                            {"id": "hero", "component": "Container"},
                            {"id": "content", "component": "Container"},
                        ],
                    },
                },
            })
            await asyncio.sleep(0.08)
            return LLMResult(text=None, a2ui=final_message, provider=self.name)

    monkeypatch.setattr(
        "backend.app.agent.harness.orchestrator.get_adapter",
        lambda: StreamingAdapter(),
    )
    events = asyncio.run(collect_stream("Tạo landing page", None, None))
    a2ui_index = next(i for i, event in enumerate(events) if event["type"] == "a2ui")
    completed_index = next(
        i for i, event in enumerate(events)
        if event["type"] == "console" and event["payload"]["message"] == "Đã nhận kết quả từ openrouter."
    )
    assert a2ui_index < completed_index


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

