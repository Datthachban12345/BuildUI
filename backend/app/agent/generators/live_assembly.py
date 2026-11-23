"""Swarm Live Assembly: chunk a createSurface into skeleton + per-section blocks.

Instead of waiting for one big createSurface to arrive and render everything at
once, the harness streams: skeleton (root + empty section containers) -> one
updateComponents block per section (navbar, hero, main-content, pricing,
footer...). The canvas assembles top-down in real time.
"""
from typing import Any, Dict, List, Tuple

from ..prompts.apple_designer import CANONICAL_SECTIONS


def _root_and_sections(surface: Dict[str, Any]) -> Tuple[str, List[str]]:
    components = surface.get("components") or []
    referenced = set()
    for node in components:
        if isinstance(node, dict):
            for child in node.get("children") or []:
                referenced.add(child)
    root_id = "root" if any(c.get("id") == "root" for c in components if isinstance(c, dict)) else next(
        (c.get("id") for c in components if isinstance(c, dict) and c.get("id") not in referenced), None)
    if not root_id:
        return "", []
    root = next((c for c in components if isinstance(c, dict) and c.get("id") == root_id), None)
    section_ids = [s for s in (root.get("children") or []) if s]
    return root_id, section_ids


def chunk_create_surface(message: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Split a valid createSurface message into [skeleton, block1, block2, ...].

    Returns [] when chunking is not safe (no root, fewer than 2 sections, or a
    section id missing from the flat list); the caller then emits the original
    message untouched.
    """
    if not isinstance(message, dict) or "createSurface" not in message:
        return []
    surface = message["createSurface"]
    components = surface.get("components")
    if not isinstance(components, list) or not components:
        return []

    by_id = {c.get("id"): c for c in components if isinstance(c, dict) and c.get("id")}
    root_id, section_ids = _root_and_sections(surface)
    if not root_id or len(section_ids) < 2 or not all(s in by_id for s in section_ids):
        return []

    def subtree_ids(section_id: str) -> List[str]:
        ids: List[str] = [section_id]
        stack = [section_id]
        while stack:
            current = stack.pop()
            node = by_id.get(current) or {}
            for child in node.get("children") or []:
                if child not in ids:
                    ids.append(child)
                    stack.append(child)
        return ids

    # 1. Skeleton: root + empty section containers, dataModel up front so
    #    DataTables/Input can bind immediately while blocks stream in.
    skeleton_nodes: List[Dict[str, Any]] = []
    root = by_id[root_id]
    skeleton_nodes.append({
        "id": root_id,
        "component": root.get("component", "Container"),
        "props": dict(root.get("props") or {}),
        "children": list(section_ids),
    })
    for section_id in section_ids:
        node = by_id[section_id]
        skeleton_nodes.append({
            "id": section_id,
            "component": node.get("component", "Container"),
            "props": dict(node.get("props") or {}),
        })
    skeleton = {
        "version": message.get("version", "1.0"),
        "createSurface": {
            "surfaceId": surface.get("surfaceId"),
            "catalogId": surface.get("catalogId", "astryx-web-v1"),
            "title": surface.get("title"),
            "components": skeleton_nodes,
            "dataModel": surface.get("dataModel") or {},
        },
    }

    # 2. One block per section: the section node (with children) + its subtree.
    blocks: List[Dict[str, Any]] = [skeleton]
    for section_id in section_ids:
        ids_in_order = [sid for sid in subtree_ids(section_id) if sid in by_id]
        block_components = []
        for index, node_id in enumerate(ids_in_order):
            node = dict(by_id[node_id])
            if index == 0:
                node["children"] = list((by_id.get(section_id) or {}).get("children") or [])
            block_components.append(node)
        blocks.append({
            "version": message.get("version", "1.0"),
            "updateComponents": {
                "surfaceId": surface.get("surfaceId"),
                "components": block_components,
            },
        })
    return blocks

SECTION_LABELS: Dict[str, str] = dict(zip(
    CANONICAL_SECTIONS,
    ["Navigation", "Hero", "Nội dung chính", "Bảng giá / Form", "Footer"],
))
# Aliases used by the deterministic templates / LLM output
SECTION_LABELS.update({
    "hero-section": "Hero",
    "services-section": "Khu vực dịch vụ",
    "pricing-section": "Bảng giá",
    "contact-section": "Form liên hệ",
    "header-row": "Thanh tiêu đề",
    "metrics-grid": "Thẻ chỉ số",
    "table-card": "Bảng dữ liệu",
})


def section_label(section_id: str) -> str:
    return SECTION_LABELS.get(section_id, section_id)
