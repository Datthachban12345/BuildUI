# BuildUI

BuildUI là một monorepo tạo website bằng AI theo hướng **A2UI-first**. Người dùng gửi yêu cầu bằng ngôn ngữ tự nhiên, backend điều phối model và kiểm tra output A2UI, còn frontend render thành website tương tác trong workspace với preview, component selection và property inspector.

## Tính năng chính

- Sinh landing page, portfolio, product page và các website nhiều section từ prompt.
- Render preview tương tác thay vì chỉ sinh ảnh mockup hoặc source code.
- Stream UI từ FastAPI backend tới React frontend qua SSE.
- Chọn component trên preview và chỉnh thuộc tính trực tiếp.
- Nhập dữ liệu để hiển thị trong UI và cập nhật từng phần theo A2UI.
- Tách model adapter, validator, runtime và component catalog để giới hạn output được phép render.

## Kiến trúc

```text
React + TypeScript workspace
  ├─ Prompt chat
  ├─ Live preview / A2UI runtime
  ├─ Component selection
  └─ Property inspector
              │ HTTPS / SSE
              ▼
FastAPI agent harness
  ├─ Model adapter
  ├─ Intent / task routing
  ├─ Context builder và planner
  ├─ A2UI generator
  ├─ Validator
  └─ Stream / persistence boundary
              │ A2UI messages
              ▼
Component catalog và renderer
```

Backend không gửi HTML/JavaScript tùy ý để trình duyệt thực thi. Model trả về dữ liệu theo hợp đồng A2UI; validator kiểm tra dữ liệu trước khi frontend runtime render bằng các component đã đăng ký.

## Cấu trúc repository

```text
buildUI/
├── backend/                 # FastAPI agent harness
├── frontend/                # React + Vite + TypeScript studio
├── tests/                   # Backend và integration tests
├── docs/                    # Tài liệu kỹ thuật, kế hoạch và hướng dẫn vận hành
│   ├── plans/
│   ├── CLAUDE.md
│   ├── README.md
│   ├── ai-website-generation-agent-guide.txt
│   └── ai-website-generation-agent-technical-guide.docx
├── CLAUDE.md                # Rule làm việc bắt buộc cho Claude Code trong repo
├── package.json              # Lệnh dev, build và test ở root
└── README.md
```

## Yêu cầu môi trường

- Python và pip cho backend.
- Node.js và pnpm cho frontend.
- Biến môi trường backend: xem [backend/.env.example](backend/.env.example).

## Cài đặt

### Backend

```bash
pip install -r backend/requirements.txt
```

### Frontend

```bash
pnpm --dir frontend install
```

## Chạy kiểm thử và build

```bash
# Backend tests
pnpm run test:backend

# Frontend TypeScript/Vite build
pnpm run test:frontend

# Tất cả kiểm thử hiện có
pnpm test
```

## Chạy local development

Lệnh sau khởi động cả API và frontend:

```bash
pnpm run dev
```

Hoặc chạy riêng:

```bash
pnpm run dev:backend   # API: http://localhost:8000
pnpm run dev:frontend  # Vite: http://localhost:5173
```

Chỉ khởi động server khi cần phát triển hoặc kiểm thử. Sau smoke test phải dừng process ngay; không để server chạy ngầm sau phiên làm việc. Quy tắc đầy đủ nằm trong [CLAUDE.md](CLAUDE.md) và [docs/CLAUDE.md](docs/CLAUDE.md).

## Tài liệu

- [Mục lục tài liệu](docs/README.md)
- [Hướng dẫn kỹ thuật đầy đủ](docs/ai-website-generation-agent-guide.txt)
- [Bản DOCX của hướng dẫn kỹ thuật](docs/ai-website-generation-agent-technical-guide.docx)
- [Kế hoạch triển khai](docs/plans/implementation-plan.md)
- [Quy tắc làm việc trong repository](CLAUDE.md)

## Trạng thái kiến trúc

A2UI là hợp đồng trung tâm giữa agent và giao diện. Astryx/component catalog là lớp adapter phía renderer; tên component, props và package cụ thể phải được đối chiếu với implementation thực tế trong repository, không nên suy đoán từ tài liệu khái niệm.
