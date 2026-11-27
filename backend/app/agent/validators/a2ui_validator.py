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
_SPACING_TOKENS = {
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "12", "14", "16", "20", "24", "28", "32", "36", "40", "44", "48",
}
_SPACING_CLASS = re.compile(
    r"^-?(?:space-[xy]|px|py|pt|pr|pb|pl|mx|my|mt|mr|mb|ml|gap|p|m)-(.+)$"
)


def _validate_spacing_tokens(component_id: str, class_name: str) -> Optional[str]:
    for token in class_name.split():
        base_class = token.split(":")[-1]
        match = _SPACING_CLASS.match(base_class)
        if match and not (
            match.group(1) in _SPACING_TOKENS
            or (base_class.startswith(("m-", "mx-", "my-")) and match.group(1) == "auto")
        ):
            return (
                f"Component '{component_id}' className uses unsupported spacing "
                f"'{token}'; use 4px-based Tailwind spacing tokens"
            )
    return None


def _validate_component_props(component: Dict[str, Any]) -> Optional[str]:
    component_id = component.get("id", "<unknown>")
    if "className" in component:
        return (
            f"Component '{component_id}' className must be inside props; "
            "props.className is the canonical A2UI location"
        )
    component_type = component.get("component")
    props = component.get("props", {})
    if not isinstance(props, dict):
        return f"Component '{component_id}' props must be an object"
    if "children" in props:
        return f"Component '{component_id}' must use the top-level children field"
    if "className" in props and not isinstance(props["className"], str):
        return f"Component '{component_id}' className must be a string"
    if "className" in props:
        spacing_error = _validate_spacing_tokens(component_id, props["className"])
        if spacing_error:
            return spacing_error
        if component_type == "Container":
            class_tokens = [token.split(":")[-1] for token in props["className"].split()]
            if "maxWidth" in props and any(token.startswith("max-w-") for token in class_tokens):
                return f"Component '{component_id}' must not combine maxWidth with max-w-* in className"
            if "paddingX" in props and any(token.startswith("px-") for token in class_tokens):
                return f"Component '{component_id}' must not combine paddingX with px-* in className"

    string_props = {
        "Heading": ("text",),
        "Text": ("text",),
        "Button": ("label", "variant", "size"),
        "Card": ("title", "description", "variant"),
        "Badge": ("label", "variant"),
        "Image": ("src", "alt", "ratio", "fit", "position"),
        "Container": ("maxWidth", "paddingX"),
        "Row": ("justify", "align", "gap"),
        "MetricsCard": ("label", "value", "change", "trend"),
    }
    for prop_name in string_props.get(component_type, ()):
        if prop_name in props and not isinstance(props[prop_name], str):
            return f"Component '{component_id}' prop '{prop_name}' must be a string"

    if component_type == "Heading":
        level = props.get("level")
        if level is not None and (isinstance(level, bool) or not isinstance(level, int) or level not in range(1, 5)):
            return f"Component '{component_id}' level must be an integer from 1 to 4"
        if props.get("scale") is not None and props["scale"] not in {"sm", "md", "lg", "xl", "display"}:
            return f"Component '{component_id}' scale is not supported"
        if props.get("weight") is not None and props["weight"] not in {"normal", "medium", "semibold", "bold"}:
            return f"Component '{component_id}' weight is not supported"
        if props.get("tone") is not None and props["tone"] not in {"default", "muted", "accent", "inverse"}:
            return f"Component '{component_id}' tone is not supported"
        if props.get("align") is not None and props["align"] not in {"left", "center", "right"}:
            return f"Component '{component_id}' align is not supported"
    elif component_type == "Text":
        if props.get("size") is not None and props["size"] not in {"xs", "sm", "base", "lg", "xl"}:
            return f"Component '{component_id}' size is not supported"
        if props.get("weight") is not None and props["weight"] not in {"normal", "medium", "semibold"}:
            return f"Component '{component_id}' weight is not supported"
        if props.get("tone") is not None and props["tone"] not in {"default", "muted", "accent", "inverse"}:
            return f"Component '{component_id}' tone is not supported"
        if props.get("align") is not None and props["align"] not in {"left", "center", "right"}:
            return f"Component '{component_id}' align is not supported"
    elif component_type == "Container":
        max_width = props.get("maxWidth")
        if max_width is not None and max_width not in {"sm", "md", "lg", "xl", "full"}:
            return f"Component '{component_id}' maxWidth is not supported"
        if props.get("paddingX") is not None and props["paddingX"] not in {"none", "sm", "md", "lg"}:
            return f"Component '{component_id}' paddingX is not supported"
    elif component_type == "Row":
        if props.get("justify") is not None and props["justify"] not in {"start", "center", "end", "between", "around"}:
            return f"Component '{component_id}' justify is not supported"
        if props.get("align") is not None and props["align"] not in {"start", "center", "end"}:
            return f"Component '{component_id}' align is not supported"
        if props.get("gap") is not None and props["gap"] not in {"sm", "md", "lg"}:
            return f"Component '{component_id}' gap is not supported"
    elif component_type == "Grid":
        cols = props.get("cols")
        if cols is not None:
            if isinstance(cols, dict):
                if not cols or set(cols) - {"base", "sm", "md", "lg"}:
                    return f"Component '{component_id}' cols has unsupported breakpoints"
                if any(
                    isinstance(value, bool) or not isinstance(value, int) or value not in range(1, 5)
                    for value in cols.values()
                ):
                    return f"Component '{component_id}' responsive cols values must be integers from 1 to 4"
            elif isinstance(cols, bool) or not isinstance(cols, int) or cols not in range(1, 5):
                return f"Component '{component_id}' cols must be an integer from 1 to 4 or a responsive map"
        if props.get("gap") is not None and props["gap"] not in {"sm", "md", "lg"}:
            return f"Component '{component_id}' gap is not supported"
    elif component_type == "Image":
        src = props.get("src")
        if src is not None and src:
            is_http_url = src.lower().startswith(("https://", "http://"))
            is_relative_path = src.startswith(("/", "./", "../")) and not src.startswith("//")
            if not (is_http_url or is_relative_path):
                return f"Component '{component_id}' src must be a relative or HTTP(S) URL"
        if props.get("ratio") is not None and props["ratio"] not in {"wide", "tall", "square"}:
            return f"Component '{component_id}' ratio is not supported"
        if props.get("fit") is not None and props["fit"] not in {"cover", "contain"}:
            return f"Component '{component_id}' fit is not supported"
        if props.get("position") is not None and props["position"] not in {"center", "top", "bottom", "left", "right"}:
            return f"Component '{component_id}' position is not supported"
    elif component_type == "Button":
        if props.get("variant") is not None and props["variant"] not in {"primary", "secondary", "outline", "ghost"}:
            return f"Component '{component_id}' variant is not supported"
        if props.get("size") is not None and props["size"] not in {"sm", "md", "lg"}:
            return f"Component '{component_id}' size is not supported"
    elif component_type == "Card":
        if props.get("variant") is not None and props["variant"] not in {"default", "soft", "outline", "elevated"}:
            return f"Component '{component_id}' variant is not supported"
    return None


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
        parent_by_child: Dict[str, str] = {}
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
            props_error = _validate_component_props(comp)
            if props_error:
                return False, props_error

            children = comp.get("children")
            if children is not None and not isinstance(children, list):
                return False, f"Component '{cid}' children must be a list of IDs"
            if isinstance(children, list):
                if any(not isinstance(child, str) for child in children):
                    return False, f"Component '{cid}' children must contain only IDs"
                if len(children) != len(set(children)):
                    return False, f"Component '{cid}' has duplicate child references"
                child_references.append((cid, children))

        for cid, children in child_references:
            missing = [child for child in children if child not in seen_ids]
            if missing:
                return False, f"Component '{cid}' references unknown children: {missing}"
            for child in children:
                if child == cid:
                    return False, f"Component '{cid}' cannot be its own child"
                existing_parent = parent_by_child.get(child)
                if existing_parent and existing_parent != cid:
                    return False, f"Component '{child}' has multiple parents"
                parent_by_child[child] = cid

        children_by_parent = {cid: children for cid, children in child_references}

        def has_cycle(node_id: str, visiting: set, visited: set) -> bool:
            if node_id in visiting:
                return True
            if node_id in visited:
                return False
            visiting.add(node_id)
            for child in children_by_parent.get(node_id, []):
                if has_cycle(child, visiting, visited):
                    return True
            visiting.remove(node_id)
            visited.add(node_id)
            return False

        visited: set = set()
        if any(has_cycle(cid, set(), visited) for cid in seen_ids):
            return False, "Component hierarchy cannot contain cycles"

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
            props_error = _validate_component_props(comp)
            if props_error:
                return False, props_error

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
