# Context

Frontend hiện đang trộn tên component theo kiểu `ChatPanel.tsx`, `PreviewCanvas.tsx`, `PropertyInspector.tsx`, `WorkspaceLayout.tsx` và đã có một `message-list-store.ts` đứng riêng. Cách đặt tên này khiến việc tìm kiếm và phân biệt UI/state trong IDE khó hơn. Mục tiêu của sprint đầu tiên là chuẩn hóa tên file theo feature: giao diện dùng `[feature]-view.tsx` (hoặc `[feature]-drawer.tsx` cho drawer), state/logic dùng `[feature]-store.ts`, đồng thời cập nhật toàn bộ import để không thay đổi hành vi hiện tại.

# Recommended approach

1. **Dựng đúng cây feature/view/store mục tiêu cho frontend hiện tại.** Không tạo các file `view.tsx` hoặc `store.ts` chung chung.
   - `workspace/WorkspaceLayout.tsx` → `workspace/workspace-view.tsx` và export `WorkspaceView`.
   - `workspace/chat/ChatPanel.tsx` → `workspace/chat/chat-view.tsx` và export `ChatView`.
   - `workspace/preview/PreviewCanvas.tsx` → `workspace/preview/preview-view.tsx` và export `PreviewView`.
   - `workspace/inspector/PropertyInspector.tsx` → `workspace/inspector/inspector-drawer.tsx` và export `InspectorDrawer`.
   - Giữ `workspace/workspace-store.ts`; wire hook này vào `workspace-view.tsx` để xóa toàn bộ state/handler bị lặp inline trong layout.
   - Tạo `workspace/chat/chat-store.ts` cho draft/input và chat-specific behavior nếu cần; không đặt chat logic lại vào view.

2. **Tách các phần con theo đúng tên feature.**
   - Tạo `chat/message-list/message-list-view.tsx`, chuyển phần render messages và auto-scroll vào đây, dùng `message-list-store.ts` đã có.
   - Tạo `chat/input-bar/input-bar-view.tsx` và `chat/input-bar/input-bar-store.ts` cho draft, submit, Enter/Shift+Enter.
   - Tạo `chat/fixture-picker/fixture-picker-view.tsx` cho menu fixture.
   - Tạo `chat/message-list/message-item/message-item-view.tsx` và `chat/message-list/message-item/step-breakdown/step-breakdown-view.tsx` cho bubble và checklist.
   - Tạo `preview/viewport-bar/viewport-bar-view.tsx` và `preview/viewport-bar/viewport-bar-store.ts` cho viewport/zoom; `preview/empty-state/empty-state-view.tsx`; `preview/artboard-frame/artboard-frame-view.tsx`.
   - Tạo các property field view/store theo phần hiện có: `text-field-view.tsx`, `variant-select-view.tsx`, `layout-spacing-view.tsx`; `inspector-store.ts` quản lý selected node và update callback boundary.
   - Các component con phải nhận props rõ ràng, không tự truy cập state toàn workspace.

3. **Chuẩn hóa A2UI, catalog và services theo loại file.**
   - `a2ui/protocol/types.ts` → `a2ui/protocol/a2ui-types.ts`.
   - `a2ui/renderer/A2UIRenderer.tsx` → `a2ui/renderer/a2ui-renderer-view.tsx`.
   - `a2ui/runtime/A2UIRuntime.ts` → `a2ui/runtime/a2ui-runtime.ts`.
   - Tách validator protocol thành `a2ui/protocol/a2ui-validator.ts` nếu logic hiện có phù hợp; không đổi behavior validator trong sprint này.
   - Đổi `catalog/adapters/astryxAdapter.tsx` thành tên kebab-case phù hợp (`astryx-adapter-view.tsx` nếu vẫn chứa React components); giữ registry/export ổn định trong bước này.
   - `services/agentApi.ts` → `services/agent-api.ts`, `fixture-loader.ts` tách riêng nếu phần fixture loader hiện đang nằm chung service.

4. **Wire store thật và loại bỏ code trùng.**
   - `workspace-view.tsx` gọi `useWorkspaceStore({ onSendPromptToBackend, onLoadFixtureData })` và truyền state/handlers xuống các view con.
   - `message-list-view.tsx` gọi `useMessageListStore(messages)`; xóa scroll effect khỏi `chat-view.tsx`.
   - `chat-view.tsx` chỉ composition/layout của `message-list-view`, `input-bar-view`, `fixture-picker-view`.
   - `preview-view.tsx` chỉ composition của `viewport-bar`, `empty-state`, `artboard-frame`; viewport/zoom không nằm inline trong preview view.
   - `inspector-drawer.tsx` chỉ hiển thị; field mapping và update callback đi qua `inspector-store`/field views.
   - `ChatMessage` chỉ có một nguồn type, ưu tiên `workspace/chat/chat-store.ts` hoặc một file type feature-named, rồi import ở message-list/store/view.

5. **Cập nhật symbol/import và xóa tên cũ.**
   - Sửa mọi import trong `App.tsx`, entrypoint, workspace, A2UI và services.
   - Đổi export component: `ChatPanel` → `ChatView`, `PreviewCanvas` → `PreviewView`, `PropertyInspector` → `InspectorDrawer`, `WorkspaceLayout` → `WorkspaceView`, `A2UIRenderer` → `A2UIRendererView`.
   - Không giữ compatibility duplicate hoặc file cũ; mục tiêu là Ctrl+P chỉ còn tên feature rõ nghĩa.
   - Không đổi `App.tsx`/`main.tsx` nếu không cần, vì đây là entrypoint và không phải file cộc lốc view/store.

6. **Giữ nguyên phạm vi hành vi.** Không triển khai model adapter, SSE mới, undo/redo, persistence hoặc phase 3–8 trong sprint refactor này; chỉ tách module và giữ nguyên luồng prompt, fixture, render, selection, inspector edit.

## Rename/move mapping chính

```text
workspace/WorkspaceLayout.tsx                  → workspace/workspace-view.tsx
workspace/chat/ChatPanel.tsx                   → workspace/chat/chat-view.tsx
workspace/preview/PreviewCanvas.tsx            → workspace/preview/preview-view.tsx
workspace/inspector/PropertyInspector.tsx      → workspace/inspector/inspector-drawer.tsx
workspace/chat/message-list/message-list-store.ts  (giữ)
a2ui/protocol/types.ts                         → a2ui/protocol/a2ui-types.ts
a2ui/runtime/A2UIRuntime.ts                    → a2ui/runtime/a2ui-runtime.ts
a2ui/renderer/A2UIRenderer.tsx                 → a2ui/renderer/a2ui-renderer-view.tsx
services/agentApi.ts                            → services/agent-api.ts
catalog/adapters/astryxAdapter.tsx             → catalog/adapters/astryx-adapter-view.tsx
```

Các folder con mới sẽ chứa implementation được tách từ UI hiện có, không phải placeholder.

# Critical files

- `frontend/src/App.tsx`
- `frontend/src/workspace/WorkspaceLayout.tsx`
- `frontend/src/workspace/workspace-store.ts`
- `frontend/src/workspace/chat/ChatPanel.tsx`
- `frontend/src/workspace/chat/message-list/message-list-store.ts`
- `frontend/src/workspace/preview/PreviewCanvas.tsx`
- `frontend/src/workspace/inspector/PropertyInspector.tsx`
- `frontend/src/a2ui/protocol/types.ts`
- `frontend/src/a2ui/runtime/A2UIRuntime.ts`
- `frontend/src/a2ui/renderer/A2UIRenderer.tsx`
- `frontend/src/services/agentApi.ts`
- `frontend/src/catalog/adapters/astryxAdapter.tsx`

# Verification

1. Tìm toàn bộ tên file cũ và import cũ bằng ripgrep; kết quả phải không còn `ChatPanel`, `PreviewCanvas`, `PropertyInspector`, `WorkspaceLayout`, `A2UIRenderer`, `A2UIRuntime`, `agentApi`, `types.ts` ở các đường dẫn đã đổi.
2. Chạy `pnpm --dir frontend build` để kiểm tra TypeScript và Vite resolve toàn bộ import.
3. Chạy ứng dụng frontend và xác nhận layout 3 vùng, gửi prompt, streaming message, load fixture, chọn component và sửa property vẫn hoạt động như trước.
4. Kiểm tra `git diff --stat`/`git status` để bảo đảm chỉ có rename, import/export cập nhật và thay đổi store cần thiết; không có file rỗng hoặc file tên cộc lốc mới.
