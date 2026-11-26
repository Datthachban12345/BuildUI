# BuildUI — AI Website Generation Agent (A2UI-First)

An AI-driven website and interactive UI generation studio built on the **A2UI v1.0** (Agent-to-User Interface) protocol, featuring a **Figma-like interactive artboard canvas**, **Swarm-based streaming rebuild**, and **Data-to-UI reactive engine**.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    AGENT HARNESS (Host Backend)              │
│  - FastAPI / Python Coordinator                              │
│  - LLM Orchestrator (Intent Router, Planner, Context Builder) │
│  - OpenRouter token stream → partial A2UI component updates  │
│  - Protocol Serializer (A2UI v1.0 Generator & Validator)     │
│  - Reactive SSE Streaming Endpoint (`/api/agent/stream-ui`)  │
└──────────────┬────────────────────────────────┬──────────────┘
               │ (Stream A2UI Messages)         │
               ▼                                ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐
│ CLIENT FIGMA CANVAS SANDBOX  │ │ DATA-TO-UI REACTIVITY ENGINE │
│ (React + TS + Tailwind)      │ │                              │
│ - Virtual Artboard (Desktop, │ │ - Arbitrary JSON / CSV input │
│   Tablet, Mobile viewports)  │ │ - Schema type inference      │
│ - Layers & Component Tree    │ │ - Local reactive 60fps sort, │
│ - Property Inspector         │ │   search, filter & paging    │
│ - A2UI State Runtime         │ │ - Zero round-trip latency    │
└──────────────────────────────┘ └──────────────────────────────┘
```

---

## Project Structure

```
buildUI/
├── backend/                  # FastAPI Agent Harness Backend
│   ├── app/
│   │   ├── main.py           # FastAPI app & SSE streaming endpoints
│   │   ├── core/config.py    # Configuration
│   │   └── models/a2ui.py    # A2UI v1.0 Pydantic v2 schemas
│   ├── tests/
│   │   └── run_tests.py      # Backend unit & schema validation tests
│   └── requirements.txt
├── frontend/                 # React 18 + Vite + TypeScript Studio
│   ├── src/
│   │   ├── components/
│   │   │   ├── CanvasHeader.tsx      # Viewports, zoom, prompt stream bar
│   │   │   ├── CanvasArtboard.tsx    # Figma artboard & Astryx renderers
│   │   │   ├── LayersPanel.tsx       # Component tree hierarchy
│   │   │   ├── InspectorPanel.tsx    # Property inspector & live editing
│   │   │   └── DataImportModal.tsx   # JSON/Table schema importer
│   │   ├── core/
│   │   │   └── a2ui-runtime.ts       # A2UI message reducer & SSE consumer
│   │   ├── types/a2ui.ts             # TypeScript protocol definitions
│   │   ├── App.tsx                   # Studio orchestrator
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── packages/
│   └── a2ui-protocol/        # Shared A2UI v1.0 Protocol package
│       ├── src/index.ts
│       └── package.json
└── docs/
    ├── adr/
    │   └── ADR-001-architecture-decisions.md
    └── specs/
        ├── a2ui-v1.0-spec.md
        └── astryx-catalog-spec.md
```

---

## Quickstart

### 1. Backend (FastAPI Agent Harness)
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run tests
python -m backend.tests.run_tests

# Start API server (port 8000)
uvicorn backend.app.main:app --reload --port 8000
```

### 2. Frontend (Figma-like A2UI Studio)
```bash
cd frontend

# Install packages
pnpm install

# Start Vite dev server (port 5173)
pnpm dev
```

Visit `http://localhost:5173` to explore the studio canvas.
