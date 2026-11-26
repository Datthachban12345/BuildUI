import asyncio
import json
import logging
import os
from typing import AsyncGenerator, Any, Dict, Optional

from ..planners.ui_planner import UIPlanner
from ..generators.a2ui_generator import A2UIGenerator
from ..generators.live_assembly import chunk_create_surface, section_label
from ..model_adapters.registry import get_adapter
from ..validators.a2ui_validator import A2UIValidator

# Default gap between Live Assembly blocks so the canvas visibly assembles
# section by section. Read per-block (not at import time) so tests can
# monkeypatch LIVE_ASSEMBLY_BLOCK_DELAY=0 for speed.
_DEFAULT_BLOCK_DELAY_SECONDS = 0.35

logger = logging.getLogger(__name__)


def _sse_event(event_type: str, payload: Any) -> str:
    return f"data: {json.dumps({'type': event_type, 'payload': payload}, ensure_ascii=False)}\n\n"


def _done() -> str:
    return "data: [DONE]\n\n"


class AgentOrchestrator:
    """Routes intent, delegates model work, validates, then streams typed SSE."""

    @classmethod
    async def process_chat_stream(
        cls,
        prompt: str,
        current_surface_id: Optional[str] = None,
        current_surface_summary: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        adapter = get_adapter()
        intent = UIPlanner.classify_intent(prompt, bool(current_surface_id))
        context = current_surface_summary or {}
        if current_surface_id:
            context = {**context, "surfaceId": current_surface_id}

        provider_name = "OpenRouter" if adapter.name == "openrouter" else "Deterministic (offline)"
        model = getattr(adapter, "model", None)
        yield _sse_event("console", {
            "level": "info",
            "message": f"Bắt đầu xử lý bằng {provider_name}",
            "provider": adapter.name,
            "model": model,
        })
        yield _sse_event("console", {
            "level": "info",
            "message": f"Intent: {intent}",
        })

        if intent == "generate_new":
            yield _sse_event("text", f'Tôi đã tiếp nhận yêu cầu: "{prompt}". Bắt đầu xây dựng website mới... ')
            yield _sse_event("steps", UIPlanner.create_generation_plan(prompt))
        elif intent == "edit_section":
            yield _sse_event("text", f'Tiếp nhận yêu cầu chỉnh sửa: "{prompt}". Đang định vị node liên quan... ')
            yield _sse_event("steps", UIPlanner.create_edit_plan())
        elif intent == "change_theme":
            yield _sse_event("text", f'Đang cập nhật theme theo yêu cầu: "{prompt}"... ')
            yield _sse_event("steps", UIPlanner.create_theme_plan())
        else:
            yield _sse_event("text", "Đang chuẩn bị câu trả lời... ")

        streamed_surface = False
        try:
            progress_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

            async def report_progress(event: Dict[str, Any]) -> None:
                await progress_queue.put(event)

            task = asyncio.create_task(A2UIGenerator.handle_intent(
                intent=intent,
                prompt=prompt,
                current_surface_id=current_surface_id,
                current_surface_summary=context,
                adapter=adapter,
                progress_callback=report_progress,
            ))
            while not task.done():
                try:
                    event = await asyncio.wait_for(progress_queue.get(), timeout=0.05)
                except asyncio.TimeoutError:
                    continue
                if event["type"] == "a2ui" and "createSurface" in event.get("payload", {}):
                    streamed_surface = True
                yield _sse_event(event["type"], event["payload"])

            result = await task
            while not progress_queue.empty():
                event = progress_queue.get_nowait()
                if event["type"] == "a2ui" and "createSurface" in event.get("payload", {}):
                    streamed_surface = True
                yield _sse_event(event["type"], event["payload"])
        except Exception as exc:
            logger.exception("Agent stream failed while handling intent=%s", intent)
            yield _sse_event("console", {
                "level": "error",
                "message": f"Backend xử lý lỗi ({type(exc).__name__}). Xem log backend.",
            })
            yield _sse_event("text", "Agent gặp lỗi phía backend; xem console backend để biết chi tiết.")
            yield _done()
            return

        if result.fallback_reason:
            yield _sse_event("console", {
                "level": "warning",
                "message": f"Provider gặp lỗi; đã chuyển sang {result.provider}.",
                "data": result.fallback_reason,
            })
        else:
            yield _sse_event("console", {
                "level": "success" if result.ok else "error",
                "message": f"Đã nhận kết quả từ {result.provider}.",
            })
        if result.quality_warnings:
            yield _sse_event("console", {
                "level": "warning",
                "message": "Model vẫn còn thiếu một số tiêu chí bố cục sau các lần tự sửa.",
                "data": result.quality_warnings,
            })

        response_data = result.text if result.text is not None else result.a2ui
        if response_data is not None:
            yield _sse_event("console", {
                "level": "info",
                "message": "Phản hồi từ model" if result.provider == "openrouter" else "Kết quả xử lý",
                "data": response_data,
            })

        if result.text:
            yield _sse_event("text", result.text)

        if result.a2ui is not None:
            valid, error = A2UIValidator.validate_message(result.a2ui)
            if valid:
                blocks = chunk_create_surface(result.a2ui)
                if streamed_surface:
                    yield _sse_event("a2ui", result.a2ui)
                elif intent == "generate_new" and len(blocks) > 1:
                    # Swarm Live Assembly: ship the skeleton first so the canvas
                    # mounts immediately, then stream each section block.
                    yield _sse_event("console", {
                        "level": "info",
                        "message": f"Live Assembly: khởi tạo khung sườn ({len(blocks) - 1} khối section)",
                    })
                    yield _sse_event("a2ui", blocks[0])
                    total = len(blocks) - 1
                    for index, block in enumerate(blocks[1:], start=1):
                        delay = float(os.getenv("LIVE_ASSEMBLY_BLOCK_DELAY", str(_DEFAULT_BLOCK_DELAY_SECONDS)))
                        if delay > 0:
                            await asyncio.sleep(delay)
                        first_id = str(block["updateComponents"]["components"][0]["id"])
                        yield _sse_event("console", {
                            "level": "info",
                            "message": f"Lắp ráp khối {index}/{total}: {section_label(first_id)}",
                        })
                        yield _sse_event("a2ui", block)
                else:
                    yield _sse_event("a2ui", result.a2ui)
            else:
                yield _sse_event("text", f"Không thể áp dụng cập nhật an toàn: {error}")
        elif not result.text and intent != "chat_inquiry":
            yield _sse_event("text", "Không thể áp dụng thay đổi lần này. Hãy thử mô tả cụ thể hơn.")

        yield _done()
