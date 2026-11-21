# Quy tắc làm việc trong buildUI

## Server / background task

Khi cần khởi động server (uvicorn backend, vite frontend) hoặc bất kỳ background task nào
để **kiểm thử / smoke test**, PHẢI **dừng nó ngay** khi bước kiểm tra kết thúc.

- Không bao giờ để server chạy ngầm qua lượt trả lời, không bao giờ để lại process
  "hầm" khiến user không hay biết.
- Server sản phẩm chỉ do **user** khởi động qua `npm run dev` (repo root) — user là
  người nắm quyền bật/tắt.
- Trước khi kết thúc một bước có chạy server: chạy `netstat -ano | grep -E ":8000|:5173"`
  để xác nhận port đã trống, và `TaskStop` mọi task nền còn sống.
-Khi khởi tạo cái gì để kiểm thử mà code về sau không dùng tới hãy xóa đi
