from typing import Dict, Any, List, Optional

class UIPlanner:
    """
    Analyzes user prompts, classifies intent, and creates a structured UI Plan.
    Enforces minimum context and single-section scope when editing.
    """

    @classmethod
    def classify_intent(cls, prompt: str, has_existing_surface: bool) -> str:
        prompt_lower = prompt.lower()
        if not has_existing_surface:
            return "generate"

        edit_keywords = ["đổi", "sửa", "thay", "thêm", "xóa", "cập nhật", "update", "change", "modify", "edit", "add", "remove"]
        if any(kw in prompt_lower for kw in edit_keywords):
            return "edit"

        return "generate"

    @classmethod
    def create_generation_plan(cls, prompt: str) -> List[str]:
        prompt_lower = prompt.lower()
        steps = [
            "1. Phân tích phong cách thiết kế & cấu trúc website",
            "2. Khởi tạo A2UI surface với theme tương thích",
            "3. Lắp ráp thanh điều hướng (Navbar)",
            "4. Xây dựng Hero banner chính & Call-to-Action",
        ]

        if "bảng" in prompt_lower or "thống kê" in prompt_lower or "dashboard" in prompt_lower or "analytics" in prompt_lower:
            steps.extend([
                "5. Thiết lập Metrics summary cards",
                "6. Tạo interactive DataTable có bộ lọc và phân trang",
                "7. Liên kết dataModel cục bộ với bảng dữ liệu"
            ])
        else:
            steps.extend([
                "5. Tạo mục dịch vụ / tính năng nổi bật (Cards grid)",
                "6. Xây dựng bảng giá / session rates",
                "7. Thêm form đặt lịch / liên hệ nhanh"
            ])

        steps.append("8. Hoàn thiện Footer & kiểm tra an toàn schema A2UI")
        return steps
