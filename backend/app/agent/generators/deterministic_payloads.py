"""Prompt-aware deterministic A2UI payloads used when an LLM is unavailable."""
import re
from typing import Any, Dict, List


_TECH_PRODUCTS = [
    "MacBook Pro M4",
    "Dell XPS 15",
    "ASUS ROG Zephyrus",
    "iPhone 17 Pro",
    "Samsung Galaxy S26",
    "iPad Pro M5",
    "Sony WH-1000XM6",
    "Logitech MX Master 4",
]


def _brand_from_prompt(prompt: str) -> str:
    match = re.search(
        r"(?:tên thương hiệu|brand(?: name)?)\s*[:：]\s*([^\n.;]+)",
        prompt,
        re.IGNORECASE,
    )
    return match.group(1).strip(" -*`") if match else ""


def _subject_from_prompt(prompt: str) -> str:
    match = re.search(
        r"(?:website|trang web|landing page|portfolio)\s+(?:cho|về|dành cho)\s+([^,\n.!]+)",
        prompt,
        re.IGNORECASE,
    )
    if not match:
        match = re.search(r"\b(?:bán|kinh doanh|giới thiệu)\s+([^,\n.!]+)", prompt, re.IGNORECASE)
    if not match:
        return "thương hiệu của bạn"
    subject = re.split(r"\s+(?:phong cách|có|với|bao gồm)\s+", match.group(1), maxsplit=1, flags=re.IGNORECASE)[0]
    return subject.strip(" -*`")[:60] or "thương hiệu của bạn"


def _product_names_from_prompt(prompt: str) -> List[str]:
    match = re.search(
        r"(?:tạo ít nhất\s+\d+\s+sản phẩm|dữ liệu mẫu)\s*:?\s*(.*?)(?=\n\s*\*\*\d+[.)]|\Z)",
        prompt,
        re.IGNORECASE | re.DOTALL,
    )
    if match:
        names = [
            re.sub(r"\s+", " ", line.strip().lstrip("-*• ")).strip()
            for line in match.group(1).splitlines()
            if line.strip().startswith(("-", "*", "•"))
        ]
        names = [name for name in names if name and len(name) < 100]
        if names:
            return names[:12]

    lowered = prompt.lower()
    mentioned = [name for name in _TECH_PRODUCTS if name.lower() in lowered]
    return mentioned or _TECH_PRODUCTS


def _category_for_product(name: str) -> str:
    lowered = name.lower()
    if any(token in lowered for token in ("iphone", "galaxy", "phone")):
        return "Điện thoại"
    if any(token in lowered for token in ("ipad", "tablet")):
        return "Máy tính bảng"
    if any(token in lowered for token in ("sony", "headphone", "tai nghe")):
        return "Âm thanh"
    if any(token in lowered for token in ("logitech", "mouse", "chuột")):
        return "Phụ kiện"
    if "rog" in lowered or "gaming" in lowered:
        return "Laptop gaming"
    return "Laptop"


def _message(title: str, components: List[Dict[str, Any]], data_model: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "page-main",
            "catalogId": "astryx-web-v1",
            "title": title,
            "components": components,
            "dataModel": data_model or {},
        },
    }


def _generate_storefront(prompt: str) -> Dict[str, Any]:
    brand = _brand_from_prompt(prompt) or "TechNova"
    names = _product_names_from_prompt(prompt)
    components: List[Dict[str, Any]] = [
        {
            "id": "root",
            "component": "Container",
            "props": {"maxWidth": "xl", "className": "technova-store-root"},
            "children": ["navbar", "hero", "main-content", "footer"],
        },
        {
            "id": "navbar",
            "component": "Row",
            "props": {"justify": "between", "align": "center", "gap": "md", "className": "technova-store-header"},
            "children": ["navbar-brand", "navbar-tagline"],
        },
        {
            "id": "navbar-brand",
            "component": "Heading",
            "props": {"level": 3, "text": brand, "className": "technova-brand"},
        },
        {
            "id": "navbar-tagline",
            "component": "Text",
            "props": {"text": "Công nghệ chính hãng · Tuyển chọn cho bạn", "className": "technova-section-intro"},
        },
        {
            "id": "hero",
            "component": "Container",
            "props": {"maxWidth": "full", "className": "technova-store-hero"},
            "children": ["hero-kicker", "hero-title", "hero-description"],
        },
        {
            "id": "hero-kicker",
            "component": "Badge",
            "props": {"label": "TECHNOLOGY · LIFESTYLE", "className": "technova-hero-kicker"},
        },
        {
            "id": "hero-title",
            "component": "Heading",
            "props": {"level": 1, "text": "Nâng tầm trải nghiệm công nghệ", "className": "technova-hero-title"},
        },
        {
            "id": "hero-description",
            "component": "Text",
            "props": {"text": f"Khám phá thiết bị được tuyển chọn từ {brand}.", "className": "technova-hero-description"},
        },
        {
            "id": "main-content",
            "component": "Container",
            "props": {"maxWidth": "full", "className": "technova-catalog"},
            "children": ["catalog-title", "catalog-description", "product-grid"],
        },
        {
            "id": "catalog-title",
            "component": "Heading",
            "props": {"level": 2, "text": "Thiết bị nổi bật", "className": "technova-section-title"},
        },
        {
            "id": "catalog-description",
            "component": "Text",
            "props": {"text": f"{len(names)} sản phẩm công nghệ dành cho bạn.", "className": "technova-section-intro"},
        },
        {
            "id": "product-grid",
            "component": "Grid",
            "props": {"cols": 3, "gap": "lg", "className": "technova-product-grid"},
            "children": [f"product-{index + 1}" for index in range(len(names))],
        },
    ]

    products = []
    for index, name in enumerate(names):
        category = _category_for_product(name)
        components.extend([
            {
                "id": f"product-{index + 1}",
                "component": "Card",
                "props": {
                    "title": name,
                    "description": f"{category} · Được tuyển chọn bởi {brand}.",
                    "className": "technova-product-card",
                },
                "children": [f"product-image-{index + 1}", f"product-category-{index + 1}"],
            },
            {
                "id": f"product-image-{index + 1}",
                "component": "Image",
                "props": {"alt": name, "ratio": "wide", "className": "technova-product-image"},
            },
            {
                "id": f"product-category-{index + 1}",
                "component": "Badge",
                "props": {"label": category, "className": "technova-category-badge"},
            },
        ])
        products.append({"id": index + 1, "name": name, "category": category})

    components.extend([
        {
            "id": "footer",
            "component": "Container",
            "props": {"maxWidth": "full", "className": "technova-catalog"},
            "children": ["footer-copy"],
        },
        {
            "id": "footer-copy",
            "component": "Text",
            "props": {"text": f"© 2026 {brand} · Thiết bị công nghệ chính hãng."},
        },
    ])
    return _message(f"{brand} - Thiết bị công nghệ", components, {"products": products})


def _generate_dashboard() -> Dict[str, Any]:
    components = [
        {"id": "root", "component": "Container", "props": {"maxWidth": "xl", "className": "p-8 space-y-8 bg-white"}, "children": ["header-row", "metrics-grid", "table-card"]},
        {"id": "header-row", "component": "Row", "props": {"justify": "between", "align": "center"}, "children": ["header-title"]},
        {"id": "header-title", "component": "Heading", "props": {"level": 1, "text": "Tổng quan hoạt động"}},
        {"id": "metrics-grid", "component": "Grid", "props": {"cols": 3, "gap": "md"}, "children": ["metric-1", "metric-2", "metric-3"]},
        {"id": "metric-1", "component": "MetricsCard", "props": {"label": "Tổng đơn hàng", "value": "128", "change": "+12%", "trend": "up"}},
        {"id": "metric-2", "component": "MetricsCard", "props": {"label": "Doanh thu", "value": "₫84.5M", "change": "+8.4%", "trend": "up"}},
        {"id": "metric-3", "component": "MetricsCard", "props": {"label": "Đang xử lý", "value": "16", "change": "-2", "trend": "down"}},
        {"id": "table-card", "component": "Card", "props": {"title": "Hoạt động gần đây"}, "children": ["data-table"]},
        {"id": "data-table", "component": "DataTable", "props": {"dataPath": "records", "searchable": True, "pageSize": 5, "columns": [{"key": "name", "title": "Tên"}, {"key": "status", "title": "Trạng thái", "type": "badge"}]}},
    ]
    return _message("Tổng quan hoạt động", components, {
        "records": [
            {"name": "Đơn hàng #1024", "status": "Hoàn tất"},
            {"name": "Đơn hàng #1025", "status": "Đang xử lý"},
            {"name": "Đơn hàng #1026", "status": "Đang giao"},
        ],
    })


def _generate_generic_site(prompt: str) -> Dict[str, Any]:
    brand = _brand_from_prompt(prompt)
    subject = _subject_from_prompt(prompt)
    display_name = brand or subject
    title = f"{display_name} - Website"
    components = [
        {"id": "root", "component": "Container", "props": {"maxWidth": "xl", "className": "bg-white"}, "children": ["navbar", "hero", "main-content", "pricing", "footer"]},
        {"id": "navbar", "component": "Row", "props": {"justify": "between", "align": "center", "className": "px-8 py-5 border-b border-zinc-200"}, "children": ["navbar-brand", "navbar-cta"]},
        {"id": "navbar-brand", "component": "Heading", "props": {"level": 3, "text": display_name}},
        {"id": "navbar-cta", "component": "Button", "props": {"label": "Liên hệ", "variant": "outline", "size": "sm"}},
        {"id": "hero", "component": "Container", "props": {"className": "px-8 py-24 text-center max-w-4xl mx-auto space-y-6"}, "children": ["hero-title", "hero-description", "hero-cta"]},
        {"id": "hero-title", "component": "Heading", "props": {"level": 1, "text": f"Khám phá {subject}"}},
        {"id": "hero-description", "component": "Text", "props": {"text": f"Trải nghiệm được thiết kế riêng cho {subject}, với chất lượng và sự tận tâm trong từng chi tiết."}},
        {"id": "hero-cta", "component": "Button", "props": {"label": "Khám phá ngay", "variant": "primary", "size": "lg"}},
        {"id": "main-content", "component": "Container", "props": {"className": "px-8 py-20 max-w-6xl mx-auto"}, "children": ["main-title", "feature-grid"]},
        {"id": "main-title", "component": "Heading", "props": {"level": 2, "text": "Điểm nổi bật"}},
        {"id": "feature-grid", "component": "Grid", "props": {"cols": 3, "gap": "lg"}, "children": ["feature-1", "feature-2", "feature-3"]},
        {"id": "feature-1", "component": "Card", "props": {"title": f"Dành riêng cho {subject}", "description": "Giải pháp phù hợp với nhu cầu thực tế của bạn."}},
        {"id": "feature-2", "component": "Card", "props": {"title": "Chất lượng đáng tin cậy", "description": "Chú trọng trải nghiệm nhất quán trong từng chi tiết."}},
        {"id": "feature-3", "component": "Card", "props": {"title": "Đồng hành lâu dài", "description": "Đội ngũ sẵn sàng hỗ trợ bạn khi cần."}},
        {"id": "pricing", "component": "Container", "props": {"className": "px-8 py-20 border-t border-zinc-200 max-w-5xl mx-auto text-center"}, "children": ["pricing-title", "pricing-card"]},
        {"id": "pricing-title", "component": "Heading", "props": {"level": 2, "text": "Giải pháp phù hợp"}},
        {"id": "pricing-card", "component": "Card", "props": {"title": f"{display_name}", "description": "Liên hệ để được tư vấn lựa chọn phù hợp."}},
        {"id": "footer", "component": "Container", "props": {"className": "px-8 py-10 border-t border-zinc-200 text-center"}, "children": ["footer-copy"]},
        {"id": "footer-copy", "component": "Text", "props": {"text": f"© 2026 {display_name}. All rights reserved."}},
    ]
    return _message(title, components)


def generate_deterministic(prompt: str) -> Dict[str, Any]:
    """Choose a simple local layout based on the user's actual request."""
    lowered = prompt.lower()
    if any(term in lowered for term in ("dashboard", "analytics", "thống kê", "bảng điều khiển")):
        return _generate_dashboard()
    if any(term in lowered for term in (
        "thương mại điện tử", "bán thiết bị", "cửa hàng công nghệ",
        "e-commerce", "ecommerce", "online store", "shopping cart",
    )):
        return _generate_storefront(prompt)
    return _generate_generic_site(prompt)


def generate_edit_delta(prompt: str, current_surface_id: str) -> Dict[str, Any]:
    """Surgically update a known hero or CTA node."""
    lowered = prompt.lower()
    if "hero" in lowered or "tiêu đề" in lowered:
        return {
            "version": "1.0",
            "updateComponents": {
                "surfaceId": current_surface_id or "page-main",
                "components": [{
                    "id": "hero-title",
                    "component": "Heading",
                    "props": {"level": 1, "text": "Khám phá trải nghiệm mới"},
                }],
            },
        }
    if "cta" in lowered or "nút" in lowered:
        return {
            "version": "1.0",
            "updateComponents": {
                "surfaceId": current_surface_id or "page-main",
                "components": [{
                    "id": "cta-primary",
                    "component": "Button",
                    "props": {"label": "Đăng ký ngay hôm nay", "variant": "primary", "size": "md"},
                }],
            },
        }
    return {
        "version": "1.0",
        "updateDataModel": {
            "surfaceId": current_surface_id or "page-main",
            "path": "/updatedAt",
            "value": "just_now",
        },
    }
