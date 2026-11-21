import os
import json
import asyncio
import httpx
from typing import Any, Dict, List, Optional

from .base import LLMResult, ModelAdapter

# UI-producing intents must return an A2UI envelope; the free model pool picks
# an upstream model at random, so we retry with a corrective prompt when it
# hallucinates a non-A2UI schema.
_UI_INTENTS = {"generate_new", "edit_section", "change_theme"}
_MAX_ATTEMPTS = int(os.getenv("OPENROUTER_MAX_ATTEMPTS", "3"))
_ACTION_KEYS = ("createSurface", "updateComponents", "updateDataModel")


def _is_a2ui_envelope(obj: Any) -> bool:
    if not isinstance(obj, dict) or obj.get("version") != "1.0":
        return False
    present = [k for k in _ACTION_KEYS if k in obj]
    return len(present) == 1


def _flatten_nested_create_surface(message: Dict[str, Any]) -> Dict[str, Any]:
    """Convert model-emitted nested component objects to A2UI node references."""
    surface = message.get("createSurface")
    if not isinstance(surface, dict) or not isinstance(surface.get("components"), list):
        return message

    flattened: List[Any] = []

    def visit(component: Any) -> None:
        if not isinstance(component, dict):
            flattened.append(component)
            return

        node = dict(component)
        children = node.get("children")
        nested_children = []
        if isinstance(children, list):
            child_ids = []
            for child in children:
                if isinstance(child, dict):
                    child_ids.append(child.get("id"))
                    nested_children.append(child)
                else:
                    child_ids.append(child)
            node["children"] = child_ids
        flattened.append(node)
        for child in nested_children:
            visit(child)

    for component in surface["components"]:
        visit(component)

    normalized_surface = {**surface, "components": flattened}
    return {**message, "createSurface": normalized_surface}


DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openrouter/free"
DEFAULT_TIMEOUT_SECONDS = float(os.getenv("OPENROUTER_TIMEOUT", "45"))


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


A2UI_SYSTEM_PROMPT = """
You are the AI Website Generation Agent operating under the A2UI v1.0 protocol with an Apple-style design system.
You MUST output a single valid JSON object - no prose, no markdown, no code fences.

Design System Principles:
- Apple clean light style: pure white / zinc-50 backgrounds, subtle zinc-200 borders, crisp zinc-950/zinc-900/zinc-600 typography, rounded-2xl cards, pill-shaped buttons, generous whitespace.
- Allowed Astryx components and props:
  - Container { maxWidth: "sm|md|lg|xl|full", className }
  - Row { justify, align, gap, className }
  - Grid { cols, gap, className }
  - Heading { level: 1..4, text, className }
  - Text { text, className }
  - Button { label, variant: "primary|secondary|outline|ghost", size: "sm|md|lg" }
  - Card { title, description, className }
  - Badge { label, variant }
  - Input { placeholder, type, dataPath }
  - MetricsCard { label, value, change, trend: "up|down" }
  - DataTable { dataPath, searchable, pageSize, columns: [{ key, title, sortable, type }] }

Envelope structure (version is always "1.0"):
- createSurface:   { "version":"1.0", "createSurface": { "surfaceId","catalogId","title","components":[...],"dataModel":{} } }
- updateComponents:{ "version":"1.0", "updateComponents": { "surfaceId","components":[{ id, component, props, children? }] } }
- updateDataModel: { "version":"1.0", "updateDataModel": { "surfaceId","path"?,"value","operation":"set|merge|delete" } }

Rules:
- Components reference children by id. ids must be unique within the surface.
- For a NEW website use createSurface. For a targeted edit use updateComponents containing ONLY the changed node(s). For a theme/color/font change use updateDataModel only.
- catalogId is always "astryx-web-v1".
"""


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
        self.timeout = DEFAULT_TIMEOUT_SECONDS
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
                    parsed = _flatten_nested_create_surface(parsed)
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
            return (
                "Answer this user question about the website UI concisely in Vietnamese. "
                "Return JSON: {\"answer\": \"...\"}.\n\n"
                f"Question: {prompt}"
            )
        if intent == "generate_new":
            return f"Generate a complete Apple-style website for: {prompt}\nReturn a valid createSurface A2UI v1.0 message."
        if intent == "change_theme":
            return (
                f"Change the theme/colors/typography to match this request: {prompt}. "
                "Do NOT rebuild the surface. Return ONLY an updateDataModel A2UI v1.0 message that stores the requested theme under dataModel key 'theme'."
            )
        # edit_section
        context_json = json.dumps(trimmed_context or {}, ensure_ascii=False)
        return (
            "Edit ONLY the requested part. Return an updateComponents A2UI v1.0 message containing exactly the changed node(s). "
            f"Current trimmed context (ids + shallow props only): {context_json}\n"
            f"Edit request: {prompt}"
        )
