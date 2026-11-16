import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Optional
from ..planners.ui_planner import UIPlanner
from ..generators.a2ui_generator import A2UIGenerator
from ..validators.a2ui_validator import A2UIValidator

class AgentOrchestrator:
    """
    Core Agent Harness coordinator enforcing the 7-step pipeline:
    1. Intent Routing
    2. Context Building
    3. UI Planning
    4. Tool Invocation (if needed)
    5. A2UI Generation
    6. Validation
    7. Persistence & Streaming
    """

    @classmethod
    async def process_chat_stream(
        cls,
        prompt: str,
        current_surface_id: Optional[str] = None,
        current_surface_summary: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        has_surface = bool(current_surface_id)
        intent = UIPlanner.classify_intent(prompt, has_surface)

        # Step 1: Initial acknowledgment & Intent routing
        if intent == "generate":
            yield f"data: {json.dumps({'text': f'Tôi đã tiếp nhận yêu cầu: \"{prompt}\". Bắt đầu xây dựng cấu trúc website mới...\\n'})}\n\n"
            await asyncio.sleep(0.3)

            # Step 2: Planning breakdown
            plan_steps = UIPlanner.create_generation_plan(prompt)
            yield f"data: {json.dumps({'steps': plan_steps})}\n\n"
            await asyncio.sleep(0.5)

            # Step 3: Generation (try LLM if key present, else deterministic)
            a2ui_message = await A2UIGenerator.generate_from_llm(prompt)
            if not a2ui_message:
                a2ui_message = A2UIGenerator.generate_deterministic(prompt)

            # Step 4: Strict Validation
            valid, err = A2UIValidator.validate_message(a2ui_message)
            if not valid:
                yield f"data: {json.dumps({'text': f'\\n[Lỗi kiểm tra Schema]: {err}'})}\n\n"
                yield "data: [DONE]\n\n"
                return

            # Step 5: Stream the validated A2UI message
            yield f"data: {json.dumps({'message': a2ui_message, 'text': '\\nWebsite đã được tạo thành công! Bạn có thể tương tác trực tiếp trên canvas bên phải hoặc yêu cầu chỉnh sửa tiếp theo.'})}\n\n"

        else: # Edit intent
            yield f"data: {json.dumps({'text': f'Tiếp nhận yêu cầu chỉnh sửa: \"{prompt}\". Đang định vị component cần thay đổi...\\n'})}\n\n"
            await asyncio.sleep(0.3)

            delta_message = A2UIGenerator.generate_edit_delta(prompt, current_surface_id or "page-main")
            valid, err = A2UIValidator.validate_message(delta_message)
            if not valid:
                yield f"data: {json.dumps({'text': f'\\n[Lỗi kiểm tra Schema]: {err}'})}\n\n"
                yield "data: [DONE]\n\n"
                return

            yield f"data: {json.dumps({'message': delta_message, 'text': 'Đã cập nhật thay đổi thành công trên canvas. Các section khác được giữ nguyên vẹn!'})}\n\n"

        yield "data: [DONE]\n\n"
