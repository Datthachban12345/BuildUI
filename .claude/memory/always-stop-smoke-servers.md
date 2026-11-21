---
name: always-stop-smoke-servers
description: After any smoke-test server/background task, stop it immediately; never leave processes running
metadata:
  type: feedback
---

Khi khởi động server (uvicorn :8000, vite :5173) hay background task để kiểm thử, PHẢI `TaskStop` ngay khi kiểm tra xong — không bao giờ để chạy ngầm qua lượt trả lời.

**Why:** User từng bị `npm run dev` lỗi `WinError 10013` (port 8000 bị chiếm) vì server smoke-test mà assistant chạy nền chưa được tắt. User phật ý rõ: "kể cả bạn có chạy nhưng xong nhiệm vụ phải đóng chứ".

**How to apply:** Server sản phẩm chỉ user khởi động qua `npm run dev`. Mỗi lần mình bật server để verify, cuối bước phải `netstat -ano | grep -E ":8000|:5173"` xác nhận port trống + `TaskStop` hết task nền. Quy tắc này cũng đã ghi trong [CLAUDE.md](../../CLAUDE.md).
