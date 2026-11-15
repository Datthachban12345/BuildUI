# ADR-001: Architecture Decisions for AI Website Generation Agent (A2UI-First)

## Status
**ACCEPTED** - 2026-11-15

## Context & Objectives
We are building an **AI-driven Website Generation Agent** powered by an **A2UI-first (Agent-to-User Interface)** runtime and an **Astryx Component Library Adapter**.
The system needs to:
1. Generate websites dynamically and incrementally with rich interactive UI.
2. Accept arbitrary JSON or tabular data and generate an interactive dashboard/table/UI without requiring manual UI configuration.
3. Allow direct visual manipulation (Figma-like canvas artboard) alongside conversational AI editing.
4. Provide strong security and CSS/script isolation between the agent dashboard and the generated website.

---

## Architectural Decisions

### 1. Dual Sandbox Boundary & Harness Separation
* **Agent Harness (Host Backend)**:
  - Runs in FastAPI (Python) outside untrusted execution.
  - Acts as the central orchestrator (LLM Routing, Multi-agent Swarm planning, Token budget, Memory, Prompt engineering).
  - Emits normalized **A2UI v1.0 JSON Messages** through Server-Sent Events (SSE).
* **Client Preview Sandbox (Isolated Canvas)**:
  - The generated website renders inside an isolated `<iframe>` (with `sandbox="allow-scripts allow-forms allow-same-origin"`).
  - Prevents CSS collisions (Tailwind / custom styles leaking into the studio UI).
  - Shields the host application from XSS or unauthorized cookie/token access.
  - Communicates via a structured, bidirectional `PostMessage` event bridge.

### 2. Figma-like Interactive Canvas Architecture
* **Artboard Canvas Shell**:
  - Provides responsive device frames (Desktop 1440px, Tablet 768px, Mobile 375px), zoom, pan, and alignment rulers.
* **Selection & Hover Overlay (Ghost DOM)**:
  - Transmits component bounding rects and node metadata (`data-a2ui-id`) from the iframe to the parent shell.
  - Draws visual hover outlines and selection handles in the parent canvas overlay.
  - Synchronizes selection with the **Layer Tree (left panel)** and **Property Inspector (right panel)**.

### 3. Swarm-based Streaming Rebuild & Progressive Mounting
* **SSE-based Delta Streaming**:
  - Rather than waiting for a full JSON payload, the Agent Harness streams discrete A2UI messages:
    1. `createSurface`: Sets up canvas metadata and layout skeleton.
    2. `updateComponents`: Streams component blocks incrementally (Navigation -> Hero -> Content/Data View -> Footer).
    3. `updateDataModel`: Injects dataset records and reactive state.
* **Visual Assembly (UX)**:
  - Renderer renders skeleton shimmers for pending blocks and mounts components seamlessly as chunks arrive.

### 4. Data-driven Reactive Engine (JSON / Table to Interactive Surface)
* **Schema Inference**:
  - Inspects user-provided JSON/CSV/Table records to detect field types (strings, numbers, timestamps, status enums, images).
  - Automatically selects optimal UI paradigms (Metrics Cards, Filterable Data Tables, Card Grids, Detail Drawers).
* **Client-side Local Reactivity**:
  - Datasets reside in the A2UI Surface `dataModel`.
  - Filter, search, sort, and pagination execute locally in the client runtime at 60fps without server round-trips.
  - Server actions are dispatched only for generative / semantic updates.

---

## Consequences & Next Steps
- **Positive**: High security, zero style contamination, instant user feedback during generation, fluid Figma-grade editing experience.
- **Implementation path**:
  - Phase 0: Protocol Types, Monorepo Setup, FastAPI Backend & React Canvas Shell.
  - Phase 1: A2UI Runtime in Client Sandbox.
  - Phase 2: Astryx Adapter and Component Mappings.
