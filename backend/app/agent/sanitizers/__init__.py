"""
A2UI Sanitizer — normalizes common LLM output mistakes before validation.

LLMs (especially free-tier models on OpenRouter) frequently produce A2UI-ish
JSON with small deviations from the protocol.  This module corrects those
deviations in-place so that the validator sees clean data and the user gets a
rendered website instead of a cryptic validation error.

Handled mistakes
----------------
1. ``"type": "Heading"``  instead of ``"component": "Heading"``
2. ``"name": "Heading"``  instead of ``"component": "Heading"``
3. Missing ``"component"`` altogether — inferred from props when possible
4. Missing ``"id"`` on a component — auto-generated
5. ``"children"`` containing ``null`` items (filtered out)
6. ``"children"`` containing nested dicts instead of id-strings (re-flattened)
7. Wrapper key typos: ``"create_surface"`` / ``"CreateSurface"`` etc.
8. ``"catalogId"`` missing (defaults to ``astryx-web-v1``)
9. ``"surfaceId"`` missing (defaults to ``page-main``)
10. ``null`` values inside ``props`` dict (stripped)
11. Legacy top-level ``className`` moved into ``props.className`` when absent;
    ``props.className`` wins when both are present.
"""
from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Optional, Set

from ..validators.a2ui_validator import ASTRYX_ALLOWED_COMPONENTS

# ----- key name normalizations ------------------------------------------------

_ENVELOPE_ALIASES: Dict[str, str] = {
    "create_surface":    "createSurface",
    "createsurface":     "createSurface",
    "CreateSurface":     "createSurface",
    "update_components": "updateComponents",
    "updatecomponents":  "updateComponents",
    "UpdateComponents":  "updateComponents",
    "update_data_model": "updateDataModel",
    "updatedatamodel":   "updateDataModel",
    "UpdateDataModel":   "updateDataModel",
    "delete_surface":    "deleteSurface",
    "deletesurface":     "deleteSurface",
    "DeleteSurface":     "deleteSurface",
}

# LLMs sometimes use "type" or "name" instead of "component"
_COMPONENT_KEY_ALIASES = ("type", "name", "componentType", "component_type")

# Heuristic: infer component type from props when key is entirely missing
_PROP_TO_COMPONENT: List[tuple] = [
    ({"level", "text"},        "Heading"),
    ({"label", "variant"},     "Button"),    # also Badge — resolved by size
    ({"dataPath", "columns"},  "DataTable"),
    ({"label", "value"},       "MetricsCard"),
    ({"title", "description"}, "Card"),
    ({"placeholder"},          "Input"),
    ({"cols"},                  "Grid"),
    ({"justify"},              "Row"),
    ({"maxWidth"},             "Container"),
]


def _infer_component_from_props(props: Dict[str, Any]) -> Optional[str]:
    """Best-effort guess of the component type from its props dict."""
    if not props:
        return None
    prop_keys = set(props.keys()) - {"className", "children", "id"}
    for required, ctype in _PROP_TO_COMPONENT:
        if required.issubset(prop_keys):
            # Disambiguate Button vs Badge: Button has "size"
            if ctype == "Button" and "size" in prop_keys:
                return "Button"
            if ctype == "Button" and "size" not in prop_keys and "label" in prop_keys and "variant" in prop_keys:
                return "Badge"
            return ctype
    # If only "text" is present (no "level"), it's a Text component
    if "text" in prop_keys:
        return "Text"
    return None


def normalize_component_class_name(component: Dict[str, Any]) -> None:
    """Keep A2UI className only in the component's canonical props object."""
    legacy_class_name = component.get("className")
    if not isinstance(legacy_class_name, str):
        return
    component.pop("className")

    props = component.get("props")
    if "props" in component and not isinstance(props, dict):
        return
    if not isinstance(props, dict):
        props = {}
    if "className" not in props and isinstance(legacy_class_name, str):
        props["className"] = legacy_class_name
    component["props"] = props


# ----- public API -------------------------------------------------------------

def sanitize_message(message: Any) -> Dict[str, Any]:
    """Return a **new** dict with common LLM mistakes corrected.

    The returned dict can be safely passed to ``A2UIValidator.validate_message``.
    If the input is so broken that sanitization cannot help, the returned dict
    will still fail validation — but with a clearer error than 'None'.
    """
    if not isinstance(message, dict):
        return message  # validator will reject non-dict

    out: Dict[str, Any] = {}

    # --- 1. Ensure "version": "1.0" ---
    version = message.get("version")
    if version is None:
        out["version"] = "1.0"
    elif isinstance(version, (int, float)):
        out["version"] = str(version)
    else:
        out["version"] = version

    # --- 2. Normalize envelope action key ---
    action_key: Optional[str] = None
    action_payload: Any = None

    for key, value in message.items():
        if key == "version":
            continue
        canonical = _ENVELOPE_ALIASES.get(key, key)
        if canonical in ("createSurface", "updateComponents", "updateDataModel",
                         "deleteSurface", "surfaceAction"):
            action_key = canonical
            action_payload = value
            break

    if action_key is None:
        # Nothing we can do — return as-is for the validator to handle
        return {**out, **{k: v for k, v in message.items() if k != "version"}}

    if not isinstance(action_payload, dict):
        out[action_key] = action_payload
        return out

    payload = dict(action_payload)

    # --- 3. Ensure surfaceId & catalogId ---
    if "surfaceId" not in payload or not isinstance(payload.get("surfaceId"), str):
        payload["surfaceId"] = payload.pop("surface_id", None) or "page-main"
    if action_key == "createSurface":
        if "catalogId" not in payload:
            payload["catalogId"] = payload.pop("catalog_id", None) or "astryx-web-v1"

    # --- 4. Sanitize components list ---
    if action_key in ("createSurface", "updateComponents"):
        components = payload.get("components")
        if isinstance(components, list):
            sanitized_comps, _ = _sanitize_component_list(components)
            payload["components"] = sanitized_comps

    out[action_key] = payload
    return out


def _sanitize_component_list(
    components: List[Any],
    seen_ids: Optional[Set[str]] = None,
) -> tuple:
    """Sanitize a flat-or-nested component list. Returns (sanitized_list, seen_ids)."""
    if seen_ids is None:
        seen_ids = set()

    sanitized: List[Dict[str, Any]] = []

    for comp in components:
        if not isinstance(comp, dict):
            continue  # skip non-dict items (nulls, strings, etc.)

        node = dict(comp)
        normalize_component_class_name(node)
        raw_props = node.get("props")
        if isinstance(raw_props, dict) and "children" in raw_props:
            if not isinstance(node.get("children"), list):
                children_from_props = raw_props["children"]
                if isinstance(children_from_props, (str, dict)):
                    children_from_props = [children_from_props]
                node["children"] = children_from_props
            node["props"] = {
                key: value for key, value in raw_props.items()
                if key != "children"
            }

        # 4a. Fix component key aliases ("type" → "component", etc.)
        if "component" not in node or node.get("component") is None:
            for alias in _COMPONENT_KEY_ALIASES:
                if alias in node and isinstance(node[alias], str) and node[alias]:
                    node["component"] = node.pop(alias)
                    break

        # 4b. If still missing, try to infer from props
        if not node.get("component"):
            props = node.get("props", {})
            if isinstance(props, dict):
                inferred = _infer_component_from_props(props)
                if inferred:
                    node["component"] = inferred

        # 4c. If still missing and node has children, assume Container
        if not node.get("component"):
            if node.get("children"):
                node["component"] = "Container"
            else:
                # Last resort: Text component if there's a "text" prop at top level
                if "text" in node and "component" not in node:
                    node["component"] = "Text"
                    if "props" not in node:
                        node["props"] = {"text": node.pop("text")}

        # 4d. Normalize component name casing (e.g. "heading" → "Heading")
        ctype = node.get("component")
        if isinstance(ctype, str):
            # Try title-case match
            ctype_lower = ctype.lower()
            for allowed in ASTRYX_ALLOWED_COMPONENTS:
                if allowed.lower() == ctype_lower:
                    node["component"] = allowed
                    break

        # 4e. Ensure valid id
        cid = node.get("id")
        if not cid or not isinstance(cid, str):
            cid = f"auto-{uuid.uuid4().hex[:8]}"
            node["id"] = cid

        # Deduplicate ids
        if cid in seen_ids:
            cid = f"{cid}-dup-{uuid.uuid4().hex[:6]}"
            node["id"] = cid
        seen_ids.add(cid)

        # 4f. Clean children — handle nested dicts + nulls
        children = node.get("children")
        if isinstance(children, list):
            clean_children_ids: List[str] = []
            nested_dicts: List[Dict[str, Any]] = []
            for child in children:
                if child is None:
                    continue
                if isinstance(child, str):
                    clean_children_ids.append(child)
                elif isinstance(child, dict):
                    # Nested component — flatten
                    child_id = child.get("id")
                    if not child_id or not isinstance(child_id, str):
                        child_id = f"auto-{uuid.uuid4().hex[:8]}"
                        child["id"] = child_id
                    clean_children_ids.append(child_id)
                    nested_dicts.append(child)
            node["children"] = clean_children_ids

            # Recursively sanitize nested components
            if nested_dicts:
                nested_sanitized, seen_ids = _sanitize_component_list(nested_dicts, seen_ids)
                sanitized.append(node)
                sanitized.extend(nested_sanitized)
                continue

        # 4g. Strip null values from props
        props = node.get("props")
        if isinstance(props, dict):
            node["props"] = {k: v for k, v in props.items() if v is not None}

        sanitized.append(node)

    return sanitized, seen_ids
