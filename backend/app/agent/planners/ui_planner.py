from typing import List

THEME_KEYWORDS = (
    "theme", "màu", "mau", "màu sắc", "mau sac", "font", "phông", "phong",
    "giao diện sáng", "giao diện tối", "palette", "typography",
    "đổi màu", "doi mau", "đổi font", "doi font", "bảng màu", "bang mau",
    "trắng", "trang", "tím", "tim", "đen", "den", "xanh", "đỏ", "do", "vàng", "vang",
)
EDIT_KEYWORDS = (
    "đổi", "doi", "sửa", "sua", "thay", "thêm", "them", "xóa", "xoá", "xoa",
    "cập nhật", "cap nhat", "update", "change", "modify", "edit", "add", "remove",
    "delete", "chỉnh", "chinh",
)
# Strong create keywords (plain "website" alone is NOT a create request).
GENERATE_KEYWORDS = (
    "tạo", "tao", "dựng", "dung", "thiết kế", "thiet ke", "generate", "create", "build",
    "portfolio", "landing", "dashboard", "trang web mới", "website mới",
)
QUESTION_MARKERS = (
    "?", "thế nào", "thế nào", "sao", "bao nhiêu", "làm gì", "giúp gì", "hiểu",
    "why", "how", "what", "when", "where", "can you", "explain",
)


class UIPlanner:
    """Classifies UI tasks into 4 canonical intents and builds execution plans."""

    @classmethod
    def classify_intent(cls, prompt: str, has_existing_surface: bool) -> str:
        text = prompt.lower().strip()

        # 1. Theme change wins on an existing surface (color/font wording is specific).
        if has_existing_surface and any(keyword in text for keyword in THEME_KEYWORDS):
            return "change_theme"

        # 2. Targeted section edit on an existing surface.
        if has_existing_surface and any(keyword in text for keyword in EDIT_KEYWORDS):
            return "edit_section"

        # 3. Explicit creation request, or no surface yet.
        is_question = any(marker in text for marker in QUESTION_MARKERS)
        has_create = any(keyword in text for keyword in GENERATE_KEYWORDS)
        if has_create and not is_question:
            return "generate_new"
        if not has_existing_surface:
            return "generate_new"

        # 4. Plain conversational inquiry.
        return "chat_inquiry"

    @classmethod
    def create_generation_plan(cls, prompt: str) -> List[str]:
        text = prompt.lower()
        steps = [
            "Phân tích yêu cầu và phong cách thiết kế",
            "Khởi tạo A2UI surface và cấu trúc trang",
            "Lắp ráp thanh điều hướng (Navbar)",
            "Xây dựng Hero và Call-to-Action",
        ]
        if any(keyword in text for keyword in ("bảng", "thống kê", "dashboard", "analytics", "data")):
            steps.extend([
                "Thiết lập các thẻ chỉ số tổng quan (Metrics)",
                "Tạo DataTable tương tác có tìm kiếm/sắp xếp",
                "Liên kết dataModel cục bộ với bảng dữ liệu",
            ])
        else:
            steps.extend([
                "Tạo khu vực dịch vụ / tính năng nổi bật",
                "Xây dựng bảng giá và form liên hệ",
                "Hoàn thiện footer và kiểm tra an toàn schema A2UI",
            ])
        return steps

    @classmethod
    def create_edit_plan(cls) -> List[str]:
        return [
            "Phân tích yêu cầu chỉnh sửa",
            "Xác định node liên quan từ context đã trim",
            "Áp dụng updateComponents chỉ cho đúng node",
        ]

    @classmethod
    def create_theme_plan(cls) -> List[str]:
        return [
            "Phân tích yêu cầu theme",
            "Sinh updateDataModel cho dữ liệu theme",
            "Giữ nguyên cấu trúc các section hiện có",
        ]
