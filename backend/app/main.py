import json
import os
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from .agent.harness.orchestrator import AgentOrchestrator

# Load environment variables
load_dotenv()

app = FastAPI(
    title="BuildUI Agent Harness API",
    version="1.0.0",
    description="Agent Harness Core implementing A2UI v1.0 protocol for conversational website generation."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str
    current_surface_id: Optional[str] = None
    current_surface_summary: Optional[Dict[str, Any]] = None

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "buildui-agent-harness",
        "protocol": "A2UI v1.0",
        "llm_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

@app.post("/api/agent/chat")
async def agent_chat(req: ChatRequest):
    """
    Primary Conversational Endpoint:
    Receives prompt, plans UI, and streams both text reasoning and A2UI v1.0 messages.
    """
    return StreamingResponse(
        AgentOrchestrator.process_chat_stream(
            prompt=req.prompt,
            current_surface_id=req.current_surface_id,
            current_surface_summary=req.current_surface_summary
        ),
        media_type="text/event-stream"
    )

@app.get("/api/fixtures/{name}")
async def get_fixture(name: str):
    """
    Serves deterministic A2UI v1.0 fixtures for testing and evaluation.
    """
    root_dir = Path(__file__).resolve().parent.parent.parent
    fixture_path = root_dir / "tests" / "fixtures" / "a2ui" / f"{name}_fixture.json"
    if not fixture_path.exists():
        raise HTTPException(status_code=404, detail=f"Fixture '{name}' not found at {fixture_path}")
    
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)
