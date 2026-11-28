# Tài liệu BuildUI

Thư mục này chứa tài liệu kỹ thuật và kế hoạch của BuildUI. README ở root là điểm bắt đầu cho cài đặt, chạy và kiểm thử dự án.

## Tài liệu hiện có

| Tài liệu | Nội dung |
| --- | --- |
| [Hướng dẫn kỹ thuật đầy đủ](ai-website-generation-agent-guide.txt) | Mục tiêu sản phẩm, A2UI, agent harness, renderer, catalog và hướng phát triển. |
| [Bản DOCX hướng dẫn kỹ thuật](ai-website-generation-agent-technical-guide.docx) | Bản tài liệu định dạng DOCX tương ứng. |
| [Kế hoạch triển khai](plans/implementation-plan.md) | Kế hoạch refactor và tổ chức module frontend. |
| [Quy tắc Claude Code](CLAUDE.md) | Bản tham chiếu của quy tắc làm việc trong repository. |

## Quy ước tài liệu

- `docs/plans/`: kế hoạch triển khai, refactor và migration.
- `docs/adr/`: architecture decision records khi có quyết định kiến trúc cần lưu lại.
- `docs/specs/`: specification/hợp đồng kỹ thuật ổn định.
- Tài liệu vận hành áp dụng cho Claude Code vẫn phải được giữ ở `CLAUDE.md` tại root; file [docs/CLAUDE.md](CLAUDE.md) chỉ là bản tham chiếu để tài liệu được tập trung trong `docs/`.

## Cập nhật tài liệu

Khi thay đổi lệnh chạy, cấu trúc thư mục, API hoặc protocol:

1. Cập nhật README hoặc tài liệu chuyên biệt liên quan.
2. Kiểm tra các relative link trong README và docs.
3. Không đưa secrets, token hoặc file sinh tự động vào tài liệu.
4. Nếu chạy server để smoke test tài liệu/tính năng, dừng server ngay sau khi kiểm tra và xác nhận port đã trống theo quy tắc root `CLAUDE.md`.
