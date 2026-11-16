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
}

class A2UIValidator:
    """
    Validates A2UI v1.0 messages before they are persisted or streamed to frontend.
    Enforces protocol integrity, unique IDs, catalog membership, and safe properties.
    """

    @classmethod
    def validate_message(cls, message: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if not isinstance(message, dict):
            return False, "Message must be a JSON object"

        if message.get("version") != "1.0":
            return False, f"Unsupported A2UI version: {message.get('version')}. Expected '1.0'"

        # Envelope check
        valid_keys = {"createSurface", "updateComponents", "updateDataModel", "deleteSurface", "surfaceAction"}
        matching_keys = [k for k in valid_keys if k in message]

        if len(matching_keys) != 1:
            return False, f"Message must contain exactly one valid action key: {valid_keys}"

        action_key = matching_keys[0]
        payload = message[action_key]

        if not isinstance(payload, dict):
            return False, f"Payload for {action_key} must be a JSON object"

        if "surfaceId" not in payload or not isinstance(payload["surfaceId"], str):
            return False, f"Missing or invalid 'surfaceId' in {action_key}"

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

        seen_ids = set()
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

            # Check children references if present
            children = comp.get("children")
            if children is not None and not isinstance(children, list):
                return False, f"Component '{cid}' children must be a list of IDs"

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

        return True, None

    @classmethod
    def _validate_update_data_model(cls, payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if "value" not in payload:
            return False, "updateDataModel must include 'value'"
        path = payload.get("path")
        if path is not None and not isinstance(path, str):
            return False, "Path in updateDataModel must be a string or omitted"
        return True, None
