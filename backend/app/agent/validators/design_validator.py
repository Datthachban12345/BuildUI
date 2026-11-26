"""Composition checks kept separate from A2UI schema validation."""
from typing import Any, Dict, List


_DASHBOARD_TERMS = ("dashboard", "analytics", "thống kê", "bảng điều khiển")
_COMMERCE_TERMS = (
    "thương mại điện tử", "bán hàng", "cửa hàng", "sản phẩm", "e-commerce",
    "ecommerce", "online store", "shopping", "shop", "store", "product",
    "giỏ hàng", "cart", "bán ",
)
_SPECIALIZED_TERMS = (
    "đăng nhập", "login", "sign in", "đăng ký tài khoản", "signup",
    "admin panel", "trang quản trị",
)


def _descendants(root_id: str, components: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    pending = [root_id]
    visited = set()
    while pending:
        node_id = pending.pop()
        if node_id in visited:
            continue
        visited.add(node_id)
        node = components.get(node_id)
        if not node:
            continue
        result.append(node)
        pending.extend(
            child for child in node.get("children", [])
            if isinstance(child, str)
        )
    return result


def assess_design_quality(message: Dict[str, Any], prompt: str) -> List[str]:
    """Return actionable composition issues without mutating valid A2UI."""
    surface = message.get("createSurface")
    if not isinstance(surface, dict) or not isinstance(surface.get("components"), list):
        return []

    nodes = {
        node["id"]: node
        for node in surface["components"]
        if isinstance(node, dict) and isinstance(node.get("id"), str)
    }
    root = nodes.get("root")
    if not root:
        return []

    root_children = [
        child for child in root.get("children", [])
        if isinstance(child, str) and child in nodes
    ]
    page_nodes = _descendants("root", nodes)
    prompt_lower = prompt.lower()
    is_dashboard = any(term in prompt_lower for term in _DASHBOARD_TERMS)
    is_specialized = any(term in prompt_lower for term in _SPECIALIZED_TERMS)
    is_commerce = any(term in prompt_lower for term in _COMMERCE_TERMS)
    issues: List[str] = []

    if not is_specialized and len(root_children) < 3:
        issues.append(
            "Build at least three distinct top-level page sections appropriate to the request; "
            "avoid a single heading-plus-grid layout."
        )

    if not is_dashboard and not is_specialized:
        hero_sections = [
            section_id for section_id in root_children
            if section_id == "hero" or section_id.startswith("hero-")
        ]
        hero_nodes = [
            node
            for section_id in hero_sections
            for node in _descendants(section_id, nodes)
        ]
        if not hero_nodes:
            hero_nodes = [
                node for node in page_nodes
                if node.get("id", "").lower().startswith("hero")
            ]
        has_hero_heading = any(
            node.get("component") == "Heading"
            and (node.get("props") or {}).get("level") == 1
            for node in hero_nodes
        )
        if not has_hero_heading:
            issues.append("Add a distinct hero section with one clear level-1 headline and supporting copy.")
        if not any(node.get("component") == "Text" for node in hero_nodes):
            issues.append("Add concise supporting copy inside the hero section.")
        if not any(node.get("component") == "Button" for node in hero_nodes):
            issues.append("Add a visible, relevant call-to-action Button inside the hero.")

    for section_id in root_children:
        section = nodes[section_id]
        if section.get("component") != "Container":
            continue
        class_name = str((section.get("props") or {}).get("className") or "")
        if not any(token.startswith(("py-", "pt-", "pb-")) for token in class_name.split()):
            issues.append(f"Give top-level section '{section_id}' intentional vertical spacing.")

    for node in page_nodes:
        if node.get("component") != "Grid":
            continue
        children = [
            child for child in node.get("children", [])
            if isinstance(child, str) and child in nodes
        ]
        columns = (node.get("props") or {}).get("cols", 3)
        if len(children) >= 3 and columns == 1:
            issues.append(f"Use a responsive multi-column Grid for '{node.get('id')}'.")

    if is_commerce:
        if not any(node.get("component") == "Image" for node in page_nodes):
            issues.append("Include Image slots in the product presentation.")
        if not any(node.get("component") == "Button" for node in page_nodes):
            issues.append("Give product cards a clear purchase or product-detail action.")
        visible_copy = " ".join(
            str((node.get("props") or {}).get(key, ""))
            for node in page_nodes
            for key in ("text", "title", "description", "label")
        ).lower()
        if not any(token in visible_copy for token in ("giá", "price", "₫", "đồng", "$")):
            issues.append("Show product prices in visible card content, not only in dataModel.")

    return issues
