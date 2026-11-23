import os
import json
import asyncio
import httpx
from typing import Any, Dict, List, Optional

from .base import LLMResult, ModelAdapter
from ..prompts.apple_designer import AppleDesignerPrompt
from ..validators.a2ui_validator import ASTRYX_ALLOWED_COMPONENTS

# UI-producing intents must return an A2UI envelope; the free model pool picks
# an upstream model at random, so we retry with a corrective prompt when it
# hallucinates a non-A2UI schema.
_UI_INTENTS = {"generate_new", "edit_section", "change_theme"}
_MAX_ATTEMPTS = int(os.getenv("OPENROUTER_MAX_ATTEMPTS", "3"))
_ACTION_KEYS = ("createSurface", "updateComponents", "updateDataModel")

_COMPONENT_ALIASES = {
    "div": "Container",
    "section": "Container",
    "main": "Container",
    "header": "Container",
    "footer": "Container",
    "nav": "Container",
    "article": "Container",
    "aside": "Container",
    "form": "Container",
    "h1": "Heading",
    "h2": "Heading",
    "h3": "Heading",
    "h4": "Heading",
    "h5": "Heading",
    "h6": "Heading",
    "title": "Heading",
    "p": "Text",
    "span": "Text",
    "paragraph": "Text",
    "label": "Text",
    "img": "Image",
    "picture": "Image",
    "photo": "Image",
    "productcard": "Card",
    "featurecard": "Card",
    "pricingcard": "Card",
    "testimonialcard": "Card",
    "productgrid": "Grid",
    "buttongroup": "Row",
    "cta": "Button",
    "searchinput": "Input",
    "textfield": "Input",
}


def _resolve_component_type(component: Any, props: Dict[str, Any]) -> Optional[str]:
    if not isinstance(component, str):
        if any(key in props for key in ("src", "image", "imageUrl", "url")):
            return "Image"
        if "placeholder" in props:
            return "Input"
        if "title" in props or "name" in props:
            return "Card"
        if "level" in props and ("text" in props or "content" in props):
            return "Heading"
        if "text" in props or "content" in props:
            return "Text"
        if "children" in props:
            return "Container"
        return None
    if component in ASTRYX_ALLOWED_COMPONENTS:
        return component

    normalized = "".join(character for character in component.lower() if character.isalnum())
    alias = _COMPONENT_ALIASES.get(normalized)
    if alias:
        return alias

    for allowed in ASTRYX_ALLOWED_COMPONENTS:
        if allowed.lower() == normalized:
            return allowed

    if any(word in normalized for word in ("image", "photo", "picture", "media")):
        return "Image"
    if any(word in normalized for word in ("product", "feature", "pricing", "testimonial")):
        return "Card"
    if any(word in normalized for word in ("heading", "title", "headline")):
        return "Heading"
    if any(word in normalized for word in ("text", "paragraph", "caption", "description")):
        return "Text"
    if any(word in normalized for word in ("button", "cta", "link")):
        return "Button"
    if any(word in normalized for word in ("grid", "list")):
        return "Grid"
    if any(word in normalized for word in ("container", "layout", "section", "wrapper")):
        return "Container"

    if any(key in props for key in ("src", "image", "imageUrl")):
        return "Image"
    if "placeholder" in props:
        return "Input"
    if "title" in props or "name" in props:
        return "Card"
    if "text" in props or "content" in props:
        return "Text"
    return None


def _has_visible_content(message: Dict[str, Any]) -> bool:
    """True when a createSurface has at least one leaf node below root."""
    surface = message.get("createSurface")
    if not isinstance(surface, dict) or not isinstance(surface.get("components"), list):
        return False
    by_id = {c.get("id"): c for c in surface["components"]
             if isinstance(c, dict) and isinstance(c.get("id"), str)}
    leaves = {"Heading", "Text", "Button", "Card", "Badge", "Input", "DataTable", "MetricsCard", "Image"}
    pending, visited = ["root"], set()
    while pending:
        node_id = pending.pop()
        if node_id in visited:
            continue
        visited.add(node_id)
        node = by_id.get(node_id)
        if not node:
            continue
        if node.get("component") in leaves:
            return True
        for child in node.get("children") or []:
            if isinstance(child, str):
                pending.append(child)
    return False


def _is_a2ui_envelope(obj: Any) -> bool:
    if not isinstance(obj, dict) or obj.get("version") != "1.0":
        return False
    present = [k for k in _ACTION_KEYS if k in obj]
    return len(present) == 1


def _normalize_create_surface(message: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten model-emitted nested components into A2UI node references and
    drop structurally broken nodes so they cannot poison the validator.

    The free model pool occasionally returns nested component objects instead
    of id references, nodes missing ``id``/``component``, and dangling child
    references. This tolerates all of it: keep only well-formed catalog nodes
    (deduped by id), prune references to removed nodes, and guarantee a
    ``root`` node plus a string ``surfaceId``.
    """
    surface = message.get("createSurface")
    if not isinstance(surface, dict) or not isinstance(surface.get("components"), list):
        return message

    # Pass 1: DFS-flatten into an ordered node list + the set of valid ids.
    # Broken nodes are skipped, but we still descend into their children so a
    # salvageable nested subtree is not lost.
    nodes: "Dict[str, Any]" = {}
    order: List[str] = []
    valid_ids: set[str] = set()

    def walk(component: Any) -> None:
        if not isinstance(component, dict):
            return
        node_id = component.get("id")
        raw_props = component.get("props")
        props = dict(raw_props) if isinstance(raw_props, dict) else {}
        raw_type = component.get("component") or component.get("type") or component.get("name")
        node_type = _resolve_component_type(raw_type, props)
        if node_type is None and node_id == "root":
            node_type = "Container"
        raw_children = component.get("children")
        children = raw_children if isinstance(raw_children, list) else []
        broken = (
            not isinstance(node_id, str) or not node_id
            or node_type is None
        )
        if not broken:
            normalized = {**component, "component": node_type, "props": props}
            if node_type in ("Heading", "Text"):
                text = props.get("text") or component.get("text") or component.get("content") or component.get("label")
                if text is not None:
                    props["text"] = text
            elif node_type == "Image":
                props.setdefault("src", component.get("src") or component.get("imageUrl") or component.get("url") or component.get("image") or "")
                props.setdefault("alt", component.get("alt") or component.get("title") or "")
            elif node_type == "Card":
                props.setdefault("title", component.get("title") or component.get("name") or component.get("label") or component.get("productName"))
                props.setdefault("description", component.get("description") or component.get("text") or component.get("content") or "")
            elif node_type == "Button":
                props.setdefault("label", component.get("label") or component.get("text") or component.get("title") or "Xem thêm")
            if node_id not in nodes:
                nodes[node_id] = normalized
                order.append(node_id)
            valid_ids.add(node_id)
        for child in children:
            walk(child)

    for component in surface["components"]:
        walk(component)

    # Pass 2: emit the flat list, pruning each node's child refs to valid ids.
    # If an invalid nested node is dropped, promote its valid descendants to
    # the nearest valid ancestor rather than leaving them disconnected.
    def resolve_child(child: Any) -> List[str]:
        if isinstance(child, str):
            return [child] if child in valid_ids else []
        if not isinstance(child, dict):
            return []

        child_id = child.get("id")
        child_props = child.get("props")
        child_props = child_props if isinstance(child_props, dict) else {}
        child_type = _resolve_component_type(
            child.get("component") or child.get("type") or child.get("name"),
            child_props,
        )
        if (
            isinstance(child_id, str)
            and child_id in valid_ids
            and child_type is not None
        ):
            return [child_id]

        nested = child.get("children")
        if not isinstance(nested, list):
            return []
        return [ref for nested_child in nested for ref in resolve_child(nested_child)]

    components: List[Dict[str, Any]] = []
    for node_id in order:
        original = nodes[node_id]
        raw_children = original.get("children")
        refs: List[str] = []
        if isinstance(raw_children, list):
            for child in raw_children:
                for ref in resolve_child(child):
                    if ref not in refs and ref != node_id:
                        refs.append(ref)
        node = {k: v for k, v in original.items() if k not in ("id", "component", "children")}
        node["id"] = node_id
        node["component"] = original.get("component")
        if refs:
            node["children"] = refs
        components.append(node)

    # Guarantee a root node and connect any otherwise orphaned top-level nodes.
    referenced_ids = {
        child
        for component in components
        for child in component.get("children", [])
    }
    top_level_ids = [
        node_id for node_id in order
        if node_id != "root" and node_id not in referenced_ids
    ]
    if "root" not in nodes:
        root: Dict[str, Any] = {"id": "root", "component": "Container",
                                "props": {"maxWidth": "xl", "className": "bg-white"}}
        if top_level_ids:
            root["children"] = top_level_ids
        components.insert(0, root)
    elif top_level_ids:
        root_node = next(component for component in components if component["id"] == "root")
        root_children = root_node.setdefault("children", [])
        root_node["children"] = list(dict.fromkeys(root_children + top_level_ids))

    surface_id = surface.get("surfaceId")
    if not isinstance(surface_id, str) or not surface_id:
        surface_id = "page-main"

    normalized_surface = {
        "surfaceId": surface_id,
        "catalogId": surface.get("catalogId") or "astryx-web-v1",
        "title": surface.get("title") or "Generated Page",
        "components": components,
        "dataModel": surface.get("dataModel") or {},
    }
    return {**message, "version": message.get("version") or "1.0", "createSurface": normalized_surface}


# Backwards-compatible alias.
def _flatten_nested_create_surface(message: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_create_surface(message)


DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openrouter/free"
def _configured_timeout() -> Optional[float]:
    """Read OPENROUTER_TIMEOUT; a blank, `none`, `unlimited` or `0` value means no limit.

    The free model pool can take several minutes to finish a completion, so a
    short cap (the old 45s default) makes most requests die mid-stream. The
    default is therefore unlimited; set a number of seconds to re-enable a cap.
    """
    raw = os.getenv("OPENROUTER_TIMEOUT", "").strip()
    if raw.lower() in ("", "none", "unlimited", "0"):
        return None
    return float(raw)


DEFAULT_TIMEOUT: Optional[float] = _configured_timeout()


def _extract_completion_content(payload: Any) -> Optional[str]:
    """Pull the model's text out of a chat-completion payload.

    Some upstream providers return a null `content` and put the answer in
    `reasoning` instead (seen on the free model pool), so fall back to it.
    """
    if not isinstance(payload, dict):
        return None
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return None
    message = choices[0].get("message")
    if not isinstance(message, dict):
        return None
    for field in ("content", "reasoning"):
        value = message.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return None


A2UI_SYSTEM_PROMPT = AppleDesignerPrompt.system()


def _strip_code_fences(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.lstrip("`")
        raw = raw[raw.find("\n") + 1 :] if "\n" in raw else raw
        if raw.endswith("```"):
            raw = raw[: -3]
    return raw.strip()


class OpenRouterAdapter(ModelAdapter):
    """Gateway adapter: reach OpenAI / Claude / Gemini model IDs through one key.

    Configure `OPENROUTER_API_KEY` and optionally `OPENROUTER_MODEL`
    (e.g. `openai/gpt-4o`, `anthropic/claude-3.5-sonnet`, `google/gemini-flash-1.5`)
    or `OPENROUTER_BASE_URL` for a compatible proxy.
    """

    name = "openrouter"

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)
        self.base_url = os.getenv("OPENROUTER_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        self.timeout = DEFAULT_TIMEOUT
        # No output token cap by default: the request omits max_tokens unless the
        # user pins one via OPENROUTER_MAX_TOKENS (helps on tight paid budgets).
        raw_max_tokens = os.getenv("OPENROUTER_MAX_TOKENS", "").strip()
        self.max_tokens = int(raw_max_tokens) if raw_max_tokens else None

    async def available(self) -> bool:
        return bool(self.api_key)

    async def handle(self, intent: str, prompt: str, trimmed_context: Optional[Dict[str, Any]] = None) -> LLMResult:
        if not await self.available():
            return LLMResult(text=None, a2ui=None, provider=self.name, ok=False, error="OPENROUTER_API_KEY missing")

        user_payload = self._build_user_prompt(intent, prompt, trimmed_context)
        history: List[Dict[str, str]] = [
            {"role": "system", "content": A2UI_SYSTEM_PROMPT},
            {"role": "user", "content": user_payload},
        ]
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "BuildUI Agent Harness",
        }
        last_error = "unknown"

        for attempt in range(1, _MAX_ATTEMPTS + 1):
            body: Dict[str, Any] = {
                "model": self.model,
                "messages": history,
                "temperature": 0.4,
                "response_format": {"type": "json_object"},
            }
            if self.max_tokens:
                body["max_tokens"] = self.max_tokens
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    res = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=body)
            except httpx.HTTPError as exc:
                last_error = f"network error: {exc}"
                await asyncio.sleep(2 * attempt)
                continue

            if res.status_code == 429 or res.status_code >= 500:
                last_error = f"HTTP {res.status_code}: {res.text[:200]}"
                await asyncio.sleep(2 * attempt)
                continue
            if res.status_code != 200:
                return LLMResult(text=None, a2ui=None, provider=self.name, ok=False, error=f"HTTP {res.status_code}: {res.text[:200]}")

            raw = _extract_completion_content(res.json())
            if raw is None:
                last_error = "OpenRouter returned an empty completion (likely token cap)"
                history.append(self._corrective_turn(last_error))
                continue

            try:
                parsed = json.loads(_strip_code_fences(raw))
            except json.JSONDecodeError as exc:
                last_error = f"Invalid JSON from model: {exc}"
                history.append(self._corrective_turn(last_error, raw))
                continue

            if intent == "chat_inquiry":
                return LLMResult(text=str(parsed.get("answer") or parsed.get("text") or raw).strip(), a2ui=None, provider=self.name)

            if _is_a2ui_envelope(parsed):
                if "createSurface" in parsed:
                    parsed = _normalize_create_surface(parsed)
                    if not _has_visible_content(parsed):
                        # The model returned structure but no visible content.
                        # Ask it to render the actual sections instead of
                        # hard-coding a template over its work.
                        last_error = "createSurface has no visible content"
                        history.append(self._corrective_turn(
                            "createSurface has no visible content - the surface only has "
                            "empty layout containers; add real Heading/Text/Button/Card "
                            "content in each section"))
                        continue
                return LLMResult(text=None, a2ui=parsed, provider=self.name)

            last_error = "Model output is not a valid A2UI v1.0 envelope"
            history.append(self._corrective_turn(last_error, raw))

        return LLMResult(text=None, a2ui=None, provider=self.name, ok=False, error=last_error)

    def _corrective_turn(self, reason: str, offending: Optional[str] = None) -> Dict[str, str]:
        message = (
            "Your previous output was not a valid A2UI v1.0 envelope "
            f"({reason}). Re-output ONLY a single JSON object with \"version\":\"1.0\" and exactly "
            "one of the keys createSurface, updateComponents, or updateDataModel. No prose, no markdown."
        )
        if offending:
            message += f"\n\nYour previous attempt (do not repeat its structure):\n{_strip_code_fences(offending)[:1500]}"
        return {"role": "user", "content": message}

    def _build_user_prompt(self, intent: str, prompt: str, trimmed_context: Optional[Dict[str, Any]]) -> str:
        if intent == "chat_inquiry":
            return AppleDesignerPrompt.inquiry_user_prompt(prompt)
        if intent == "generate_new":
            return AppleDesignerPrompt.generation_user_prompt(prompt)
        if intent == "change_theme":
            return AppleDesignerPrompt.theme_user_prompt(prompt)
        # edit_section
        context_json = json.dumps(trimmed_context or {}, ensure_ascii=False)
        return AppleDesignerPrompt.edit_user_prompt(prompt, context_json)
