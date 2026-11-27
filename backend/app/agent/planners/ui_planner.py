import re
from typing import List

THEME_KEYWORDS = (
    "theme", "màu chủ đạo", "mau chu dao", "bảng màu", "bang mau",
    "palette", "typography", "toàn bộ giao diện", "toan bo giao dien",
    "giao diện sáng", "giao diện tối", "đổi font", "doi font", "font toàn",
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
    "?", "thế nào", "sao", "bao nhiêu", "làm gì", "giúp gì", "hiểu",
    "why", "how", "what", "when", "where", "can you", "explain",
    "bạn làm được gì", "bạn giúp được gì",
)
GREETING_KEYWORDS = ("xin chào", "chào bạn", "chào")
THANKS_KEYWORDS = ("cảm ơn", "cam on", "thanks", "thank you")
THEME_SCOPE_KEYWORDS = THEME_KEYWORDS


def _is_greeting(text: str) -> bool:
    if any(keyword in text for keyword in GREETING_KEYWORDS):
        return True
    return re.search(r"\b(?:hello|hi|hey)\b", text) is not None


class UIPlanner:
    """Classifies UI tasks into 4 canonical intents and builds execution plans."""

    @classmethod
    def classify_intent(cls, prompt: str, has_existing_surface: bool) -> str:
        text = prompt.lower().strip()

        # Intent is determined by the user's words, not whether a canvas exists.
        # Keep the parameter for callers that still pass surface state.
        is_question = any(marker in text for marker in QUESTION_MARKERS) or text.endswith(
            (" không", " được không", " chứ", " à", " hả")
        )
        if (
            _is_greeting(text)
            or any(keyword in text for keyword in THANKS_KEYWORDS)
            or any(keyword in text for keyword in ("bạn có thể làm gì", "bạn giúp được gì", "what can you do"))
            or is_question
        ):
            return "chat_inquiry"

        has_edit = any(keyword in text for keyword in EDIT_KEYWORDS)
        if has_edit and any(keyword in text for keyword in THEME_SCOPE_KEYWORDS):
            return "change_theme"

        if has_edit:
            return "edit_section"

        # Create requests require creation language or a clear page type; an
        # empty canvas alone is never enough to infer that intent.
        has_create = any(keyword in text for keyword in GENERATE_KEYWORDS)
        if has_create:
            return "generate_new"

        return "chat_inquiry"

    @classmethod
    def create_generation_plan(cls, prompt: str) -> List[str]:
        return [
            "Phân tích yêu cầu, đối tượng và phong cách",
            "Lựa chọn cấu trúc phù hợp với nội dung được yêu cầu",
            "Sinh bố cục và nội dung theo catalog A2UI",
            "Kiểm tra cấu trúc và các section thực sự được tạo",
        ]

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
