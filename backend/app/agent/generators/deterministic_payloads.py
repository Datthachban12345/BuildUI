"""Legacy deterministic payloads moved out of A2UIGenerator for the adapter boundary."""
from typing import Any, Dict


def generate_deterministic(prompt: str) -> Dict[str, Any]:
    """
    Deterministic generator producing Apple-style clean light UI surfaces.
    """
    p_lower = prompt.lower()
    if "bảng" in p_lower or "thống kê" in p_lower or "dashboard" in p_lower or "analytics" in p_lower:
        # Generate Apple Style Analytics / Data Explorer Surface
        return {
            "version": "1.0",
            "createSurface": {
                "surfaceId": "page-analytics",
                "catalogId": "astryx-web-v1",
                "title": "Studio Analytics & Deliverables",
                "components": [
                    {
                        "id": "root",
                        "component": "Container",
                        "props": { "maxWidth": "xl", "className": "p-8 space-y-8 bg-white" },
                        "children": ["header-row", "metrics-grid", "table-card"]
                    },
                    {
                        "id": "header-row",
                        "component": "Row",
                        "props": { "justify": "between", "align": "center" },
                        "children": ["header-title", "header-action"]
                    },
                    {
                        "id": "header-title",
                        "component": "Heading",
                        "props": { "level": 2, "text": "Tổng quan dự án & Doanh thu", "className": "text-2xl font-semibold tracking-tight text-zinc-950" }
                    },
                    {
                        "id": "header-action",
                        "component": "Button",
                        "props": { "label": "Xuất báo cáo", "variant": "outline", "size": "sm" }
                    },
                    {
                        "id": "metrics-grid",
                        "component": "Grid",
                        "props": { "cols": 3, "gap": "md" },
                        "children": ["metric-1", "metric-2", "metric-3"]
                    },
                    {
                        "id": "metric-1",
                        "component": "MetricsCard",
                        "props": { "label": "Dự án đang thực hiện", "value": "24", "change": "+12%", "trend": "up" }
                    },
                    {
                        "id": "metric-2",
                        "component": "MetricsCard",
                        "props": { "label": "Doanh thu tháng", "value": "$142,500", "change": "+8.4%", "trend": "up" }
                    },
                    {
                        "id": "metric-3",
                        "component": "MetricsCard",
                        "props": { "label": "Đang chờ duyệt", "value": "5", "change": "-2", "trend": "down" }
                    },
                    {
                        "id": "table-card",
                        "component": "Card",
                        "props": {
                            "title": "Bàn giao khách hàng",
                            "description": "Bảng tương tác trực tiếp: tìm kiếm, sắp xếp và lọc ngay trên màn hình."
                        },
                        "children": ["data-table"]
                    },
                    {
                        "id": "data-table",
                        "component": "DataTable",
                        "props": {
                            "dataPath": "projects",
                            "searchable": True,
                            "pageSize": 5,
                            "columns": [
                                { "key": "code", "title": "Mã DA", "sortable": True },
                                { "key": "client", "title": "Khách hàng", "sortable": True },
                                { "key": "type", "title": "Dịch vụ", "sortable": True },
                                { "key": "status", "title": "Trạng thái", "type": "badge" },
                                { "key": "budget", "title": "Ngân sách ($)", "sortable": True }
                            ]
                        }
                    }
                ],
                "dataModel": {
                    "projects": [
                        { "code": "DA-101", "client": "Vogue Editorial", "type": "Chụp bìa tạp chí", "status": "Active", "budget": 4500 },
                        { "code": "DA-102", "client": "Architectural Digest", "type": "Không gian nội thất", "status": "Active", "budget": 6200 },
                        { "code": "DA-103", "client": "Nordic Brand", "type": "Lookbook Thu Đông", "status": "Review", "budget": 3800 },
                        { "code": "DA-104", "client": "TechCorp App", "type": "Chân dung nhân sự", "status": "Completed", "budget": 1500 },
                        { "code": "DA-105", "client": "Kinfolk Gallery", "type": "Triển lãm nghệ thuật", "status": "Pending", "budget": 8000 }
                    ]
                }
            }
        }
    else:
        # Generate Apple Style Minimalist Landing Page (Studio / Portfolio / Product)
        return {
            "version": "1.0",
            "createSurface": {
                "surfaceId": "page-main",
                "catalogId": "astryx-web-v1",
                "title": "Minimalist Studio Landing Page",
                "components": [
                    {
                        "id": "root",
                        "component": "Container",
                        "props": { "maxWidth": "xl", "className": "bg-white" },
                        "children": ["navbar", "hero-section", "services-section", "pricing-section", "contact-section", "footer"]
                    },
                    {
                        "id": "navbar",
                        "component": "Row",
                        "props": { "justify": "between", "align": "center", "className": "px-8 py-5 border-b border-zinc-200/80 bg-white/80 backdrop-blur-md" },
                        "children": ["nav-brand", "nav-links"]
                    },
                    {
                        "id": "nav-brand",
                        "component": "Heading",
                        "props": { "level": 3, "text": "LUMEN STUDIO", "className": "text-sm tracking-widest font-semibold text-zinc-900" }
                    },
                    {
                        "id": "nav-links",
                        "component": "Row",
                        "props": { "gap": "md" },
                        "children": ["btn-services", "btn-contact"]
                    },
                    {
                        "id": "btn-services",
                        "component": "Button",
                        "props": { "label": "Dịch vụ", "variant": "ghost", "size": "sm" }
                    },
                    {
                        "id": "btn-contact",
                        "component": "Button",
                        "props": { "label": "Đặt lịch chụp", "variant": "primary", "size": "sm" }
                    },
                    {
                        "id": "hero-section",
                        "component": "Container",
                        "props": { "className": "px-8 py-24 text-center max-w-4xl mx-auto space-y-6" },
                        "children": ["hero-pill", "hero-title", "hero-subtitle", "hero-actions"]
                    },
                    {
                        "id": "hero-pill",
                        "component": "Badge",
                        "props": { "label": "Nhiếp ảnh Chân dung & Kiến trúc", "variant": "neutral" }
                    },
                    {
                        "id": "hero-title",
                        "component": "Heading",
                        "props": {
                            "level": 1,
                            "text": "Bắt trọn khoảnh khắc tĩnh lặng giữa chuyển động",
                            "className": "text-5xl font-semibold tracking-tight text-zinc-950 leading-tight"
                        }
                    },
                    {
                        "id": "hero-subtitle",
                        "component": "Text",
                        "props": {
                            "text": "Chuyên về hình ảnh thời trang cao cấp, kiến trúc không gian và chân dung nghệ thuật với ánh sáng tự nhiên tinh tế.",
                            "className": "text-lg text-zinc-600 font-normal max-w-2xl mx-auto leading-relaxed"
                        }
                    },
                    {
                        "id": "hero-actions",
                        "component": "Row",
                        "props": { "justify": "center", "gap": "md", "className": "pt-4" },
                        "children": ["cta-primary", "cta-secondary"]
                    },
                    {
                        "id": "cta-primary",
                        "component": "Button",
                        "props": { "label": "Xem Portfolio", "variant": "primary", "size": "md" }
                    },
                    {
                        "id": "cta-secondary",
                        "component": "Button",
                        "props": { "label": "Bảng giá chi tiết", "variant": "outline", "size": "md" }
                    },
                    {
                        "id": "services-section",
                        "component": "Container",
                        "props": { "className": "px-8 py-20 max-w-6xl mx-auto" },
                        "children": ["services-header", "services-grid"]
                    },
                    {
                        "id": "services-header",
                        "component": "Heading",
                        "props": { "level": 2, "text": "Dịch vụ tiêu biểu", "className": "text-2xl font-semibold text-zinc-900 mb-10 text-center tracking-tight" }
                    },
                    {
                        "id": "services-grid",
                        "component": "Grid",
                        "props": { "cols": 3, "gap": "lg" },
                        "children": ["service-card-1", "service-card-2", "service-card-3"]
                    },
                    {
                        "id": "service-card-1",
                        "component": "Card",
                        "props": {
                            "title": "Chân dung Nghệ thuật",
                            "description": "Studio và ngoại cảnh phục vụ bìa tạp chí, ấn phẩm truyền thông và thương hiệu cá nhân đẳng cấp."
                        }
                    },
                    {
                        "id": "service-card-2",
                        "component": "Card",
                        "props": {
                            "title": "Không gian Kiến trúc",
                            "description": "Tư liệu nhiếp ảnh chuẩn mực cho công trình nhà ở cao cấp và không gian thương mại hiện đại."
                        }
                    },
                    {
                        "id": "service-card-3",
                        "component": "Card",
                        "props": {
                            "title": "Bản in Nghệ thuật",
                            "description": "Bản in ấn phẩm giới hạn trên chất liệu giấy cotton chuẩn bảo tàng lưu trữ quốc tế."
                        }
                    },
                    {
                        "id": "pricing-section",
                        "component": "Container",
                        "props": { "className": "px-8 py-20 border-t border-zinc-200/80 max-w-5xl mx-auto text-center" },
                        "children": ["pricing-header", "pricing-grid"]
                    },
                    {
                        "id": "pricing-header",
                        "component": "Heading",
                        "props": { "level": 2, "text": "Bảng giá buổi chụp", "className": "text-3xl font-semibold text-zinc-950 mb-10 tracking-tight" }
                    },
                    {
                        "id": "pricing-grid",
                        "component": "Grid",
                        "props": { "cols": 2, "gap": "lg" },
                        "children": ["price-card-standard", "price-card-editorial"]
                    },
                    {
                        "id": "price-card-standard",
                        "component": "Card",
                        "props": {
                            "title": "Gói Studio Tiêu chuẩn",
                            "description": "$450 · Buổi chụp 2 tiếng · 15 ảnh chỉnh sửa chất lượng cao · 2 trang phục · Trả file gốc ngay trong ngày",
                            "className": "text-left"
                        }
                    },
                    {
                        "id": "price-card-editorial",
                        "component": "Card",
                        "props": {
                            "title": "Gói Thương mại Trọn ngày",
                            "description": "$1,800 · Chụp trọn ngày tại địa điểm · Toàn quyền bản quyền thương mại · Chỉ đạo nghệ thuật & Stylist",
                            "className": "text-left border-zinc-900 shadow-md"
                        }
                    },
                    {
                        "id": "contact-section",
                        "component": "Container",
                        "props": { "className": "px-8 py-20 max-w-xl mx-auto text-center space-y-6" },
                        "children": ["contact-title", "contact-email-input", "contact-btn"]
                    },
                    {
                        "id": "contact-title",
                        "component": "Heading",
                        "props": { "level": 2, "text": "Liên hệ đặt lịch", "className": "text-2xl font-semibold text-zinc-950 tracking-tight" }
                    },
                    {
                        "id": "contact-email-input",
                        "component": "Input",
                        "props": { "placeholder": "Nhập địa chỉ email của bạn...", "type": "email" }
                    },
                    {
                        "id": "contact-btn",
                        "component": "Button",
                        "props": { "label": "Gửi yêu cầu đặt lịch", "variant": "primary", "size": "md" }
                    },
                    {
                        "id": "footer",
                        "component": "Container",
                        "props": { "className": "px-8 py-10 border-t border-zinc-200/80 text-center text-xs text-zinc-500" },
                        "children": ["footer-text"]
                    },
                    {
                        "id": "footer-text",
                        "component": "Text",
                        "props": { "text": "© 2026 Lumen Studio. All rights reserved. Thiết kế theo chuẩn Apple tối giản.", "className": "text-zinc-500" }
                    }
                ],
                "dataModel": {
                    "contactEmail": ""
                }
            }
        }

def generate_edit_delta(prompt: str, current_surface_id: str) -> Dict[str, Any]:
    """
    Surgically updates only the affected component node (Incremental Editing).
    """
    p_lower = prompt.lower()
    if "hero" in p_lower or "tiêu đề" in p_lower:
        return {
            "version": "1.0",
            "updateComponents": {
                "surfaceId": current_surface_id or "page-main",
                "components": [
                    {
                        "id": "hero-title",
                        "component": "Heading",
                        "props": {
                            "level": 1,
                            "text": "Không gian nghệ thuật & Chân dung thị giác đỉnh cao",
                            "className": "text-5xl font-semibold tracking-tight text-zinc-950 leading-tight"
                        }
                    }
                ]
            }
        }
    elif "cta" in p_lower or "nút" in p_lower:
        return {
            "version": "1.0",
            "updateComponents": {
                "surfaceId": current_surface_id or "page-main",
                "components": [
                    {
                        "id": "cta-primary",
                        "component": "Button",
                        "props": { "label": "Đăng ký ngay hôm nay", "variant": "primary", "size": "md" }
                    }
                ]
            }
        }
    else:
        return {
            "version": "1.0",
            "updateDataModel": {
                "surfaceId": current_surface_id or "page-main",
                "path": "/updatedAt",
                "value": "just_now"
            }
        }
