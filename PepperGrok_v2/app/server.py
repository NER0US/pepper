"""FastAPI application powering PepperGrok v2."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .bridge import BridgeConfig, route_prompt
from .heartbeat import Heartbeat
from .memory import MemoryStore
from .voice import speak_text

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "config.json"
HEARTBEAT_LOG = APP_DIR.parent / "logs" / "heartbeat.log"

config = BridgeConfig(CONFIG_PATH)
memory_store = MemoryStore(max_memories=config.get("max_memories", 5000))
heartbeat: Optional[Heartbeat] = None
if config.get("heartbeat_enabled", True):
    heartbeat = Heartbeat(HEARTBEAT_LOG)
    heartbeat.start()

app = FastAPI(title="PepperGrok v2")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = APP_DIR / "ui"
if static_dir.exists():
    app.mount("/ui", StaticFiles(directory=static_dir), name="ui")


@app.get("/status")
def status() -> Dict[str, str]:
    """Return system status details."""

    return {
        "grok_online": bool(config.get("grok_online", True)),
        "heartbeat": "running" if heartbeat and heartbeat.is_alive() else "stopped",
        "memories": len(memory_store.list(limit=config.get("max_memories", 5000))),
    }


@app.get("/memories")
def list_memories(limit: int = 15) -> Dict[str, List[Dict[str, str]]]:
    """Return the last *limit* memories."""

    memories = memory_store.list(limit=limit)
    return {
        "memories": [entry.to_dict() for entry in memories],
        "emotional_bias": memory_store.emotional_bias(memories),
    }


@app.post("/remember")
def remember(payload: Dict[str, str]) -> Dict[str, str]:
    """Store a new memory entry."""

    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="'text' is required")
    category = payload.get("category")
    entry = memory_store.add(text=text, category=category)
    return {"status": "ok", "category": entry.category}


@app.post("/query")
def query(payload: Dict[str, str]) -> Dict[str, str]:
    """Route the prompt to Grok or Ollama based on the current mode."""

    user_prompt = payload.get("prompt")
    if not user_prompt:
        raise HTTPException(status_code=400, detail="'prompt' is required")
    mode = payload.get("mode")
    memories = memory_store.list(limit=15)
    reply = route_prompt(user_prompt, config, memories, mode=mode)
    return {"response": reply}


@app.post("/speak")
def speak(payload: Dict[str, str]) -> Dict[str, str]:
    """Voice endpoint that uses pyttsx3 when available."""

    if not config.get("voice_enabled", False):
        return {"status": "disabled"}
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="'text' is required")
    speak_text(text, voice_id=payload.get("voice_id"))
    return {"status": "ok"}


@app.get("/")
def index() -> FileResponse:
    """Serve the UI entry point."""

    ui_index = static_dir / "index.html"
    if not ui_index.exists():
        raise HTTPException(status_code=404, detail="UI not built")
    return FileResponse(ui_index)


@app.on_event("shutdown")
def shutdown_event() -> None:
    """Ensure background threads are stopped on shutdown."""

    if heartbeat:
        heartbeat.stop()


if __name__ == "__main__":  # pragma: no cover - manual launch helper
    import uvicorn

    uvicorn.run("app.server:app", host="0.0.0.0", port=8000, reload=False)
