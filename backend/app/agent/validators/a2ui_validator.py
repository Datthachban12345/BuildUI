import re
from typing import Dict, Any, List, Tuple, Optional

ASTRYX_ALLOWED_COMPONENTS = {
    "Container",
    "Row",
    "Column",
    "Grid",
    "Heading",
    "Text",
    "Button",
    "Card",
    "Badge",
    "Input",
    "DataTable",
    "MetricsCard",
    "Image",
}

MAX_COMPONENTS_PER_SURFACE = 200

# A2UI Strict Security Guard: dangerous strings that must never reach the client.
_DANGEROUS_PATTERNS = [
    re.compile(r"<\s*script", re.IGNORECASE),
    re.compile(r"<\s*iframe", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"\beval\s*\(", re.IGNORECASE),
    re.compile(r"dangerouslySetInnerHTML", re.IGNORECASE),
]

# Action allowlist (Phase 7) - actions outside this set are rejected.
ALLOWED_ACTIONS = {"navigate", "submit_form", "open_modal", "scroll_to"}


def contains_dangerous_content(value: Any) -> bool:
    """Recursively scan strings for dangerous payloads. Returns True if found."""
    if isinstance(value, str):
        return any(p.search(value) for p in _DANGEROUS_PATTERNS)
    if isinstance(value, dict):
        return any(contains_dangerous_content(v) for v in value.values())
    if isinstance(value, list):
        return any(contains_dangerous_content(v) for v in value)
    return False


class A2UIValidator:
    """
    Validates A2UI v1.0 messages before they are persisted or streamed to frontend.
    Enforces protocol integrity, unique IDs, catalog membership, quotas and safety.
    """

    @classmethod
    def validate_message(cls, message: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if not isinstance(message, dict):
            return False, "Message must be a JSON object"

        if message.get("version") != "1.0":
            return False, f"Unsupported A2UI version: {message.get('version')}. Expected '1.0'"

        valid_keys = {"createSurface", "updateComponents", "updateDataModel", "deleteSurface", "surfaceAction"}
        matching_keys = [k for k in valid_keys if k in message]

        if len(matching_keys) != 1:
            return False, f"Message must contain exactly one valid action key: {sorted(valid_keys)}"

        action_key = matching_keys[0]
        payload = message[action_key]

        if not isinstance(payload, dict):
            return False, f"Payload for {action_key} must be a JSON object"

        if "surfaceId" not in payload or not isinstance(payload["surfaceId"], str):
            return False, f"Missing or invalid 'surfaceId' in {action_key}"

        if contains_dangerous_content(payload):
            return False, "Rejected: payload contains a forbidden script/iframe/eval string"

        if action_key == "createSurface":
            return cls._validate_create_surface(payload)
        elif action_key == "updateComponents":
            return cls._validate_update_components(payload)
        elif action_key == "updateDataModel":
            return cls._validate_update_data_model(payload)

        return True, None

    @classmethod
    def _validate_create_surface(cls, payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        components = payload.get("components")
        if not isinstance(components, list) or len(components) == 0:
            return False, "createSurface must include a non-empty list of 'components'"

        if len(components) > MAX_COMPONENTS_PER_SURFACE:
            return False, f"Resource quota exceeded: max {MAX_COMPONENTS_PER_SURFACE} components per surface"

        seen_ids = set()
        child_references: List[Tuple[str, List[str]]] = []
        for comp in components:
            if not isinstance(comp, dict):
                return False, "Each component must be an object"
            cid = comp.get("id")
            ctype = comp.get("component")
            if not cid or not isinstance(cid, str):
                return False, f"Component missing valid 'id': {comp}"
            if cid in seen_ids:
                return False, f"Duplicate component id: '{cid}'"
            seen_ids.add(cid)

            if not ctype or ctype not in ASTRYX_ALLOWED_COMPONENTS:
                return False, f"Component type '{ctype}' is not permitted by Astryx Catalog"

            children = comp.get("children")
            if children is not None and not isinstance(children, list):
                return False, f"Component '{cid}' children must be a list of IDs"
            if isinstance(children, list):
                if any(not isinstance(child, str) for child in children):
                    return False, f"Component '{cid}' children must contain only IDs"
                child_references.append((cid, children))

        for cid, children in child_references:
            missing = [child for child in children if child not in seen_ids]
            if missing:
                return False, f"Component '{cid}' references unknown children: {missing}"

        return True, None

    @classmethod
    def _validate_update_components(cls, payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        components = payload.get("components")
        if not isinstance(components, list):
            return False, "updateComponents must include a list of 'components'"

        for comp in components:
            if not isinstance(comp, dict):
                return False, "Each component must be an object"
            cid = comp.get("id")
            ctype = comp.get("component")
            if not cid or not isinstance(cid, str):
                return False, "Component missing valid 'id'"
            if ctype and ctype not in ASTRYX_ALLOWED_COMPONENTS:
                return False, f"Component type '{ctype}' not in Astryx Catalog"

            action = comp.get("props", {}).get("action") if isinstance(comp.get("props"), dict) else None
            if action is not None and action not in ALLOWED_ACTIONS:
                return False, f"Action '{action}' is not in the allowed action set"

        return True, None

    @classmethod
    def _validate_update_data_model(cls, payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if "value" not in payload:
            return False, "updateDataModel must include 'value'"
        path = payload.get("path")
        if path is not None and not isinstance(path, str):
            return False, "Path in updateDataModel must be a string or omitted"
        return True, None
