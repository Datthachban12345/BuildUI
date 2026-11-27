import os
import json
import asyncio
import httpx
import re
from typing import Any, Dict, List, Optional

from .base import LLMResult, ModelAdapter, ProgressCallback
from ..prompts.apple_designer import AppleDesignerPrompt
from ..sanitizers import normalize_component_class_name, sanitize_message
from ..validators.a2ui_validator import ASTRYX_ALLOWED_COMPONENTS
from ..validators.design_validator import assess_design_quality

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
        if not isinstance(raw_children, list):
            raw_children = props.get("children")
            if isinstance(raw_children, str):
                raw_children = [raw_children]
        children = raw_children if isinstance(raw_children, list) else []
        props.pop("children", None)
        broken = (
            not isinstance(node_id, str) or not node_id
            or node_type is None
        )
        if not broken:
            normalized = {**component, "component": node_type, "props": props}
            normalize_component_class_name(normalized)
            props = normalized["props"]
            if isinstance(raw_children, list):
                normalized["children"] = raw_children
            if node_type in ("Heading", "Text"):
                text = props.get("text") or component.get("text") or component.get("content") or component.get("label")
                if text is not None:
                    props["text"] = text
            elif node_type == "Image":
                props.setdefault("src", component.get("src") or component.get("imageUrl") or component.get("url") or component.get("image") or "")
                props.setdefault("alt", component.get("alt") or component.get("title") or "")
            elif node_type == "Card":
                title = (
                    component.get("title") or component.get("name")
                    or component.get("label") or component.get("productName")
                    or props.get("name")
                )
                if title is not None:
                    props.setdefault("title", title)
                props.setdefault(
                    "description",
                    component.get("description") or component.get("text")
                    or component.get("content") or props.get("description") or "",
                )
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

    # `children` is the canonical tree edge. If a model also listed every node
    # under root, prefer the more specific nested parent and remove duplicate
    # edges/cycles before schema validation.
    by_id = {component["id"]: component for component in components}
    root_node = by_id["root"]
    parent_by_child: Dict[str, str] = {}
    for parent in components:
        for child_id in parent.get("children") or []:
            if child_id not in by_id or child_id == "root":
                continue
            current_parent = parent_by_child.get(child_id)
            if current_parent is None or (
                current_parent == "root" and parent["id"] != "root"
            ):
                parent_by_child[child_id] = parent["id"]

    visited: set[str] = set()

    def normalize_branch(parent_id: str) -> None:
        if parent_id in visited:
            return
        visited.add(parent_id)
        node = by_id[parent_id]
        normalized_children: List[str] = []
        for child_id in node.get("children") or []:
            if (
                child_id not in by_id
                or child_id == parent_id
                or child_id in visited
                or parent_by_child.get(child_id) != parent_id
            ):
                continue
            normalized_children.append(child_id)
            normalize_branch(child_id)
        node["children"] = normalized_children

    normalize_branch("root")
    for node in components:
        node_id = node["id"]
        if node_id in visited:
            continue
        root_children = root_node.setdefault("children", [])
        if node_id not in root_children:
            root_children.append(node_id)
        parent_by_child[node_id] = "root"
        normalize_branch(node_id)

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


def _extract_complete_component_objects(raw: str) -> List[Dict[str, Any]]:
    """Extract complete top-level component objects from a partial JSON stream."""
    surface_match = re.search(r'"createSurface"\s*:\s*\{', raw)
    if not surface_match:
        return []
    components_match = re.search(r'"components"\s*:\s*\[', raw[surface_match.end():])
    if not components_match:
        return []

    start = surface_match.end() + components_match.end()
    objects: List[Dict[str, Any]] = []
    object_start: Optional[int] = None
    object_depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(raw)):
        char = raw[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            if object_depth == 0:
                object_start = index
            object_depth += 1
        elif char == "}":
            object_depth -= 1
            if object_depth == 0 and object_start is not None:
                try:
                    value = json.loads(raw[object_start:index + 1])
                except json.JSONDecodeError:
                    object_start = None
                    continue
                if isinstance(value, dict):
                    objects.append(value)
                object_start = None
        elif char == "]" and object_depth == 0:
            break
    return objects


def _partial_surface_string(raw: str, field: str, default: str) -> str:
    surface_match = re.search(r'"createSurface"\s*:\s*\{', raw)
    if not surface_match:
        return default
    match = re.search(
        rf'"{re.escape(field)}"\s*:\s*("(?:\\.|[^"\\])*")',
        raw[surface_match.end():],
    )
    if not match:
        return default
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError:
        return default
    return value if isinstance(value, str) and value else default


def _partial_create_surface(
    raw: str,
    parsed_components: List[Dict[str, Any]],
) -> Dict[str, Any]:
    known_ids: set[str] = set()
    referenced_ids: set[str] = set()

    def collect(node: Any) -> None:
        if not isinstance(node, dict):
            return
        node_id = node.get("id")
        if isinstance(node_id, str) and node_id:
            known_ids.add(node_id)
        children = node.get("children")
        if isinstance(children, list):
            for child in children:
                if isinstance(child, str):
                    referenced_ids.add(child)
                elif isinstance(child, dict):
                    collect(child)

    for component in parsed_components:
        collect(component)

    placeholders = [
        {"id": node_id, "component": "Container", "props": {}}
        for node_id in sorted(referenced_ids - known_ids)
    ]
    return sanitize_message(_normalize_create_surface({
        "version": "1.0",
        "createSurface": {
            "surfaceId": _partial_surface_string(raw, "surfaceId", "page-main"),
            "catalogId": _partial_surface_string(raw, "catalogId", "astryx-web-v1"),
            "title": _partial_surface_string(raw, "title", "Generating page"),
            "components": parsed_components + placeholders,
            "dataModel": {},
        },
    }))


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

    async def handle(
        self,
        intent: str,
        prompt: str,
        trimmed_context: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> LLMResult:
        if not await self.available():
            return LLMResult(text=None, a2ui=None, provider=self.name, ok=False, error="OPENROUTER_API_KEY missing")

        user_payload = self._build_user_prompt(intent, prompt, trimmed_context)
        system_prompt = (
            "You are a helpful conversational assistant. Reply in the user's language. "
            'Return only a JSON object with one string field named "answer". '
            "Never return A2UI, createSurface, updateComponents, or website layouts."
            if intent == "chat_inquiry"
            else A2UI_SYSTEM_PROMPT
        )
        history: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_payload},
        ]
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "BuildUI Agent Harness",
        }
        last_error = "unknown"
        best_quality_candidate: Optional[Dict[str, Any]] = None
        best_quality_warnings: Optional[List[str]] = None

        for attempt in range(1, _MAX_ATTEMPTS + 1):
            body: Dict[str, Any] = {
                "model": self.model,
                "messages": history,
                "temperature": 0.4,
                "response_format": {"type": "json_object"},
                "stream": True,
            }
            if self.max_tokens:
                body["max_tokens"] = self.max_tokens
            try:
                streamed_raw = ""
                streamed_reasoning = ""
                parsed_components: List[Dict[str, Any]] = []
                previous_nodes: Dict[str, Dict[str, Any]] = {}
                progress_started = False
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream(
                        "POST",
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=body,
                    ) as res:
                        if res.status_code != 200:
                            response_body = (await res.aread()).decode("utf-8", errors="replace")
                        else:
                            response_body = ""
                            async for line in res.aiter_lines():
                                if not line.startswith("data:"):
                                    if not streamed_raw and line.lstrip().startswith("{"):
                                        try:
                                            non_stream_payload = json.loads(line)
                                        except json.JSONDecodeError:
                                            continue
                                        non_stream_content = _extract_completion_content(non_stream_payload)
                                        if non_stream_content:
                                            streamed_raw = non_stream_content
                                    continue
                                data = line[5:].strip()
                                if data == "[DONE]":
                                    break
                                try:
                                    chunk = json.loads(data)
                                except json.JSONDecodeError:
                                    continue
                                choices = chunk.get("choices")
                                if not isinstance(choices, list) or not choices:
                                    continue
                                choice = choices[0]
                                delta = choice.get("delta") if isinstance(choice, dict) else None
                                if not isinstance(delta, dict) and isinstance(choice, dict):
                                    message = choice.get("message")
                                    content = _extract_completion_content({"choices": [{"message": message}]})
                                    if content:
                                        streamed_raw += content
                                    continue
                                if not isinstance(delta, dict):
                                    continue
                                content = delta.get("content")
                                if isinstance(content, str) and content:
                                    streamed_raw += content
                                    if intent == "generate_new" and progress_callback:
                                        completed = _extract_complete_component_objects(streamed_raw)
                                        if len(completed) > len(parsed_components):
                                            parsed_components = completed
                                            partial = _partial_create_surface(streamed_raw, parsed_components)
                                            partial_components = partial["createSurface"]["components"]
                                            current_nodes = {
                                                component["id"]: component
                                                for component in partial_components
                                            }
                                            if "root" in current_nodes:
                                                if not progress_started:
                                                    await progress_callback({
                                                        "type": "a2ui",
                                                        "payload": partial,
                                                    })
                                                    progress_started = True
                                                else:
                                                    changed = [
                                                        component for node_id, component in current_nodes.items()
                                                        if previous_nodes.get(node_id) != component
                                                    ]
                                                    if changed:
                                                        await progress_callback({
                                                            "type": "a2ui",
                                                            "payload": {
                                                                "version": "1.0",
                                                                "updateComponents": {
                                                                    "surfaceId": partial["createSurface"]["surfaceId"],
                                                                    "components": changed,
                                                                },
                                                            },
                                                        })
                                            previous_nodes = current_nodes
                                reasoning = delta.get("reasoning")
                                if isinstance(reasoning, str):
                                    streamed_reasoning += reasoning
            except httpx.HTTPError as exc:
                last_error = f"network error: {exc}"
                await asyncio.sleep(2 * attempt)
                continue

            if res.status_code == 429 or res.status_code >= 500:
                last_error = f"HTTP {res.status_code}: {response_body[:200]}"
                await asyncio.sleep(2 * attempt)
                continue
            if res.status_code != 200:
                return LLMResult(text=None, a2ui=None, provider=self.name, ok=False, error=f"HTTP {res.status_code}: {response_body[:200]}")

            raw = streamed_raw or streamed_reasoning or None
            if raw is None:
                last_error = "OpenRouter returned an empty completion (likely token cap)"
                history.append(self._corrective_turn(last_error, intent=intent))
                continue

            try:
                parsed = json.loads(_strip_code_fences(raw))
            except json.JSONDecodeError as exc:
                last_error = f"Invalid JSON from model: {exc}"
                history.append(self._corrective_turn(last_error, raw, intent=intent))
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
                            "content in each section",
                            intent=intent,
                        ))
                        continue
                    if intent == "generate_new":
                        quality_warnings = assess_design_quality(parsed, prompt)
                        if quality_warnings:
                            if (
                                best_quality_warnings is None
                                or len(quality_warnings) < len(best_quality_warnings)
                            ):
                                best_quality_candidate = parsed
                                best_quality_warnings = quality_warnings
                            last_error = "Design quality review: " + "; ".join(quality_warnings)
                            history.append(self._corrective_turn(last_error, raw, intent=intent))
                            continue
                return LLMResult(text=None, a2ui=parsed, provider=self.name)

            last_error = "Model output is not a valid A2UI v1.0 envelope"
            history.append(self._corrective_turn(last_error, raw, intent=intent))

        if best_quality_candidate is not None:
            return LLMResult(
                text=None,
                a2ui=best_quality_candidate,
                provider=self.name,
                quality_warnings=best_quality_warnings,
            )
        return LLMResult(text=None, a2ui=None, provider=self.name, ok=False, error=last_error)

    def _corrective_turn(
        self,
        reason: str,
        offending: Optional[str] = None,
        intent: Optional[str] = None,
    ) -> Dict[str, str]:
        if intent == "chat_inquiry":
            message = (
                f"Your previous conversational response needs correction ({reason}). "
                'Return only a JSON object with one string field named "answer". '
                "Do not include A2UI or a website layout."
            )
        else:
            message = (
                "Your previous output needs correction "
                f"({reason}). Re-output ONLY a single JSON object with \"version\":\"1.0\" and exactly "
                "one of the keys createSurface, updateComponents, or updateDataModel. No prose, no markdown."
            )
            message += (
                "\nRepair only the listed issues while preserving all valid ids, requested content, "
                "and unaffected sections. Follow the A2UI contract exactly: each component's "
                "className belongs only in props.className; never emit a second top-level className. "
                "When a component prop such as Container.maxWidth or Container.paddingX controls "
                "the same style, remove the conflicting utility from props.className."
            )
            if intent == "generate_new":
                message += (
                    "\nUse the section ids and current properties from the JSON below as context. "
                    "Make spacing role-specific (compact navbar/footer, more generous hero, "
                    "moderate content sections); do not copy one spacing/max-width signature "
                    "to every section. Do not claim or add unrelated sections."
                )
        if offending:
            message += f"\n\nCurrent A2UI output to repair:\n{_strip_code_fences(offending)[:6000]}"
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
