import json
import asyncio
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .core.config import settings
from .models.a2ui import GenerateWebsiteRequest, SurfaceActionMessage

tags_metadata = [
    {
        "name": "System",
        "description": "Health verification and system status endpoints.",
    },
    {
        "name": "Agent Harness",
        "description": "Orchestrates A2UI v1.0 generation, progressive streaming, and action events.",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
# BuildUI — Agent Harness & A2UI Protocol API

This API serves as the **Host Agent Harness** for generating, mutating, and streaming interactive websites and dashboard surfaces using the **A2UI v1.0** protocol.

### Core Capabilities:
- **Progressive SSE Streaming**: Real-time assembly of website sections (Nav, Hero, Data Table, Cards).
- **Data-to-UI Reactivity**: Dynamic schema inference and local client data binding.
- **Surface Action Dispatch**: Bidirectional communication between client canvas and agent harness.
    """,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get(
    "/api/health",
    tags=["System"],
    summary="Health Check",
    description="Returns the health status, agent service name, and supported A2UI protocol version."
)
async def health_check():
    return {
        "status": "healthy",
        "service": "a2ui-agent-harness",
        "version": settings.VERSION,
        "protocol": "A2UI v1.0"
    }

@app.post(
    "/api/agent/action",
    tags=["Agent Harness"],
    summary="Surface Action Dispatcher",
    description="Receives client action events triggered from interactive components on the canvas.",
    status_code=status.HTTP_200_OK
)
async def handle_surface_action(action: SurfaceActionMessage):
    """Handles client-to-agent action messages"""
    return {
        "status": "acknowledged",
        "surfaceId": action.surfaceId,
        "componentId": action.componentId,
        "action": action.action
    }

@app.post(
    "/api/agent/stream-ui",
    tags=["Agent Harness"],
    summary="Stream A2UI Messages (SSE)",
    description="Streams delta A2UI v1.0 messages (createSurface, updateComponents, updateDataModel) via Server-Sent Events.",
    response_class=StreamingResponse
)
async def stream_ui_generation(req: GenerateWebsiteRequest):
    """
    Streams A2UI v1.0 protocol messages to client over SSE (Server-Sent Events)
    Simulates the Swarm Rebuild / progressive assembly mechanism.
    """
    async def event_generator():
        surface_id = "surface-main"
        
        # Step 1: Create Surface
        msg_create = {
            "version": "1.0",
            "type": "createSurface",
            "surfaceId": surface_id,
            "catalogId": req.catalog_id,
            "title": req.prompt or "Interactive AI Website",
            "layout": {
                "type": "standard",
                "theme": {"mode": "dark", "primaryColor": "#3b82f6"}
            }
        }
        yield f"data: {json.dumps(msg_create)}\n\n"
        await asyncio.sleep(0.3)

        # Step 2: Stream Header & Navigation
        msg_nav = {
            "version": "1.0",
            "type": "updateComponents",
            "surfaceId": surface_id,
            "components": [
                {
                    "id": "navbar",
                    "type": "Container",
                    "parentId": None,
                    "props": {"className": "w-full border-b border-slate-800 bg-slate-900/80 backdrop-blur px-8 py-4 flex items-center justify-between"},
                    "children": ["brand-logo", "nav-actions"]
                },
                {
                    "id": "brand-logo",
                    "type": "Heading",
                    "parentId": "navbar",
                    "props": {"level": 3, "text": "⚡ Astryx A2UI Studio", "variant": "gradient"}
                },
                {
                    "id": "nav-actions",
                    "type": "Row",
                    "parentId": "navbar",
                    "props": {"gap": "md"},
                    "children": ["btn-docs", "btn-get-started"]
                },
                {
                    "id": "btn-docs",
                    "type": "Button",
                    "parentId": "nav-actions",
                    "props": {"label": "Documentation", "variant": "ghost", "size": "sm"}
                },
                {
                    "id": "btn-get-started",
                    "type": "Button",
                    "parentId": "nav-actions",
                    "props": {"label": "Get Started", "variant": "primary", "size": "sm"}
                }
            ]
        }
        yield f"data: {json.dumps(msg_nav)}\n\n"
        await asyncio.sleep(0.4)

        # Step 3: Stream Hero & Interactive Data Table / Cards
        msg_hero = {
            "version": "1.0",
            "type": "updateComponents",
            "surfaceId": surface_id,
            "components": [
                {
                    "id": "hero-section",
                    "type": "Container",
                    "parentId": None,
                    "props": {"className": "max-w-6xl mx-auto px-6 py-16 text-center space-y-6"},
                    "children": ["hero-heading", "hero-subtitle", "stats-grid", "data-section"]
                },
                {
                    "id": "hero-heading",
                    "type": "Heading",
                    "parentId": "hero-section",
                    "props": {
                        "level": 1,
                        "text": "Data-Driven Interactive Surfaces Generated On-the-Fly",
                        "className": "text-4xl md:text-5xl font-extrabold text-white tracking-tight"
                    }
                },
                {
                    "id": "hero-subtitle",
                    "type": "Text",
                    "parentId": "hero-section",
                    "props": {
                        "text": "Streamed incrementally via A2UI protocol. Reactively binds arbitrary JSON or table records with live client sorting and filtering.",
                        "className": "text-lg text-slate-400 max-w-2xl mx-auto"
                    }
                },
                {
                    "id": "stats-grid",
                    "type": "Grid",
                    "parentId": "hero-section",
                    "props": {"cols": 3, "gap": "md", "className": "pt-6"},
                    "children": ["kpi-1", "kpi-2", "kpi-3"]
                },
                {
                    "id": "kpi-1",
                    "type": "MetricsCard",
                    "parentId": "stats-grid",
                    "props": {"label": "Total Active Users", "value": "128,420", "change": "+14.2%", "trend": "up"}
                },
                {
                    "id": "kpi-2",
                    "type": "MetricsCard",
                    "parentId": "stats-grid",
                    "props": {"label": "Monthly Recurring Rev", "value": "$84,200", "change": "+28.4%", "trend": "up"}
                },
                {
                    "id": "kpi-3",
                    "type": "MetricsCard",
                    "parentId": "stats-grid",
                    "props": {"label": "A2UI Render Latency", "value": "12ms", "change": "-40%", "trend": "up"}
                },
                {
                    "id": "data-section",
                    "type": "Card",
                    "parentId": "hero-section",
                    "props": {
                        "title": "Interactive Records Explorer",
                        "description": "Try filtering or sorting rows directly in the client preview",
                        "className": "mt-12 text-left"
                    },
                    "children": ["data-table"]
                },
                {
                    "id": "data-table",
                    "type": "DataTable",
                    "parentId": "data-section",
                    "props": {
                        "dataPath": "dataset.records",
                        "searchable": True,
                        "pageSize": 5,
                        "columns": [
                            {"key": "id", "title": "ID", "sortable": True},
                            {"key": "name", "title": "Project Name", "sortable": True},
                            {"key": "tier", "title": "Tier", "sortable": True},
                            {"key": "status", "title": "Status", "type": "badge"},
                            {"key": "mrr", "title": "MRR ($)", "sortable": True}
                        ]
                    }
                }
            ]
        }
        yield f"data: {json.dumps(msg_hero)}\n\n"
        await asyncio.sleep(0.4)

        # Step 4: Stream Data Model (Reactive local binding)
        records = [
            {"id": "PRJ-01", "name": "AI Web Agent Core", "tier": "Enterprise", "status": "Active", "mrr": 4500},
            {"id": "PRJ-02", "name": "Astryx Design Studio", "tier": "Pro", "status": "Active", "mrr": 2100},
            {"id": "PRJ-03", "name": "Swarm Rebuilder Engine", "tier": "Enterprise", "status": "Testing", "mrr": 3800},
            {"id": "PRJ-04", "name": "Data-to-UI Schema Engine", "tier": "Standard", "status": "Active", "mrr": 1200},
            {"id": "PRJ-05", "name": "Figma Canvas Bridge", "tier": "Pro", "status": "Review", "mrr": 1950},
            {"id": "PRJ-06", "name": "A2UI Security Guard", "tier": "Enterprise", "status": "Active", "mrr": 5200}
        ]
        
        msg_data = {
            "version": "1.0",
            "type": "updateDataModel",
            "surfaceId": surface_id,
            "operation": "set",
            "path": "dataset",
            "value": {
                "records": records,
                "filterStatus": "all"
            }
        }
        yield f"data: {json.dumps(msg_data)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
