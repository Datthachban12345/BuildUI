"""Design-system polisher for LLM-generated A2UI surfaces.

Free-pool models reliably produce structure (ids, children, dataModel) but
often skip the Apple spacing rhythm / type scale in className. The polisher
fills exactly those gaps and nothing more:

- never touches text, data, or already-styled nodes,
- adds section spacing (py-20/24) to top-level section containers that have
  no className at all,
- upgrades unstyled headings to the Apple type scale,
- normalizes the page root to a clean white canvas.

Runs after the LLM turn and before validation, so it can never break a
surface that the model already styled correctly.
"""
from typing import Any, Dict

# Top-level section containers (direct children of "root") that lack any
# styling get the Apple vertical rhythm.
_SECTION_SPACING = "px-8 py-20 max-w-6xl mx-auto"

# Headings without className get the type-scale defaults by level.
_HEADING_SCALE: Dict[int, str] = {
    1: "text-5xl font-semibold tracking-tight text-zinc-950 leading-tight",
    2: "text-3xl font-semibold tracking-tight text-zinc-950",
    3: "text-xl font-medium tracking-tight text-zinc-900",
    4: "text-base font-medium text-zinc-800",
}


def _node_id(node: Any) -> str:
    return node.get("id") if isinstance(node, dict) else ""


def polish_create_surface(message: Dict[str, Any]) -> Dict[str, Any]:
    """Fill missing Apple design tokens in a createSurface message, in place."""
    surface = message.get("createSurface")
    if not isinstance(surface, dict) or not isinstance(surface.get("components"), list):
        return message

    by_id = {c.get("id"): c for c in surface["components"] if isinstance(c, dict) and c.get("id")}
    root = by_id.get("root")
    if not isinstance(root, dict):
        return message

    # Page root: clean white canvas.
    root_props = root.setdefault("props", {})
    if not isinstance(root_props, dict):
        root["props"] = root_props = {}
    if not root_props.get("className"):
        root_props["className"] = "bg-white"
    if not root_props.get("maxWidth"):
        root_props["maxWidth"] = "xl"

    section_ids = [s for s in (root.get("children") or []) if s in by_id]

    for node in surface["components"]:
        if not isinstance(node, dict):
            continue
        node_id = _node_id(node)
        node_type = node.get("component")
        props = node.get("props")
        if not isinstance(props, dict):
            # Nodes with no props at all are exactly the ones the free pool
            # leaves unstyled - create the dict so styling can be filled.
            if node_type in ("Container", "Row", "Grid", "Heading", "Button", "Card", "Text", "Badge"):
                node["props"] = props = {}
            else:
                continue

        # 1. Unstyled top-level section container -> Apple spacing rhythm.
        if node_id in section_ids and node_type in ("Container", "Row", "Grid") \
                and not props.get("className"):
            props["className"] = _SECTION_SPACING

        # 2. Unstyled headings -> type scale.
        if node_type == "Heading" and not props.get("className"):
            level = props.get("level", 2)
            level = level if isinstance(level, int) and 1 <= level <= 4 else 2
            props["className"] = _HEADING_SCALE[level]

        # 3. Primary buttons without styling get the pill default (the catalog
        #    renderer already styles variants; this only covers models that
        #    emit raw buttons outside the catalog defaults).
        if node_type == "Button" and not props.get("variant") and props.get("label"):
            props["variant"] = "primary"

    return message
