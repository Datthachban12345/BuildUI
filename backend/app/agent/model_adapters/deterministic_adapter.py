import re
from typing import Any, Dict, Optional

from .base import LLMResult, ModelAdapter, ProgressCallback
from ..generators.deterministic_payloads import generate_deterministic, generate_edit_delta


class DeterministicAdapter(ModelAdapter):
    """Offline deterministic provider used when OpenRouter is absent/fails."""

    name = "deterministic"

    async def available(self) -> bool:
        return True

    async def handle(
        self,
        intent: str,
        prompt: str,
        trimmed_context: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> LLMResult:
        if intent == "generate_new":
            return LLMResult(text=None, a2ui=generate_deterministic(prompt), provider=self.name)
        if intent == "edit_section":
            surface_id = (trimmed_context or {}).get("surface_id") or "page-main"
            message = generate_edit_delta(prompt, surface_id)
            # A deterministic delta is possible only when its target node is known.
            ids = set((trimmed_context or {}).get("component_ids", []))
            if "updateComponents" in message:
                components = message["updateComponents"].get("components", [])
                if ids and any(component.get("id") not in ids for component in components):
                    return LLMResult(text="Chưa xác định được chính xác component cần sửa. Hãy nêu rõ vị trí hoặc tiêu đề.", a2ui=None, provider=self.name)
            return LLMResult(text=None, a2ui=message, provider=self.name)
        if intent == "change_theme":
            surface_id = (trimmed_context or {}).get("surface_id") or "page-main"
            return LLMResult(text=None, a2ui={
                "version": "1.0",
                "updateDataModel": {
                    "surfaceId": surface_id,
                    "path": "/theme",
                    "value": {"request": prompt},
                    "operation": "merge",
                },
            }, provider=self.name)
        if intent == "chat_inquiry":
            normalized = prompt.lower()
            is_greeting = (
                any(word in normalized for word in ("xin chào", "chào bạn", "chào"))
                or re.search(r"\b(?:hello|hi|hey)\b", normalized) is not None
            )
            if is_greeting:
                text = "Xin chào! Mình có thể trò chuyện, giải đáp câu hỏi hoặc giúp bạn tạo và chỉnh sửa giao diện."
            elif any(word in normalized for word in ("cảm ơn", "cam on", "thanks", "thank you")):
                text = "Rất vui được giúp bạn!"
            elif any(word in normalized for word in ("bạn có thể làm gì", "bạn làm được gì", "bạn giúp được gì", "what can you do")):
                text = "Mình có thể trả lời câu hỏi, tạo website mới, chỉnh sửa giao diện hiện có và đổi theme."
            else:
                text = "Mình đang chạy ở chế độ offline. Bạn có thể hỏi thêm hoặc mô tả giao diện muốn tạo hay chỉnh sửa."
            return LLMResult(text=text, a2ui=None, provider=self.name)
        return LLMResult(text="Mình có thể giúp tạo website, chỉnh sửa section hoặc đổi theme. Bạn muốn làm gì tiếp theo?", a2ui=None, provider=self.name)
