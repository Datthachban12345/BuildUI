# Quy tắc làm việc trong buildUI

> File áp dụng chính vẫn là [`../CLAUDE.md`](../CLAUDE.md) ở root. File này là bản tham chiếu tài liệu; giữ `CLAUDE.md` root ở local để Claude Code tiếp tục tự động đọc quy tắc của repository.

## Server / background task

Khi cần khởi động server (uvicorn backend, vite frontend) hoặc bất kỳ background task nào để kiểm thử / smoke test, phải dừng nó ngay khi bước kiểm tra kết thúc.

- Không để server chạy ngầm qua lượt trả lời hoặc sau phiên làm việc.
- Server sản phẩm chỉ do user khởi động qua `npm run dev` ở root.
- Trước khi kết thúc bước có chạy server, kiểm tra port `8000` và `5173` đã trống, đồng thời dừng mọi task nền còn sống.
- Xóa các file hoặc code thử nghiệm không còn được sử dụng.
