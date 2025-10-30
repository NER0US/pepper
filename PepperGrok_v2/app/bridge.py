"""Routing logic between Grok and Ollama back-ends."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import logging
import subprocess

import requests

from .memory import CATEGORY_WEIGHTS, MemoryEntry

LOGGER = logging.getLogger(__name__)


class BridgeConfig(Dict[str, Any]):
    """Lightweight helper for configuration with defaults."""

    DEFAULTS: Dict[str, Any] = {
        "grok_online": True,
        "grok_api_key": None,
        "model": "llama3.2",
        "ollama_local": True,
        "voice_enabled": False,
        "heartbeat_enabled": True,
        "max_memories": 5000,
    }

    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path
        self.update(self.DEFAULTS)
        if path.exists():
            try:
                data = json.loads(path.read_text("utf-8"))
                if isinstance(data, dict):
                    self.update(data)
            except json.JSONDecodeError:
                LOGGER.warning("Failed to parse config.json; using defaults")

    def save(self) -> None:
        self.path.write_text(json.dumps(dict(self), indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
def build_prompt(user_prompt: str, memories: List[MemoryEntry]) -> str:
    """Assemble the Grok prompt with emotional weighting."""

    emotional_bias = 0.0
    if memories:
        total = sum(CATEGORY_WEIGHTS.get(m.category, 1.0) for m in memories[-15:])
        emotional_bias = total / min(len(memories), 15)
    else:
        emotional_bias = CATEGORY_WEIGHTS["system"]

    formatted_memories = "\n".join(
        f"- ({entry.category}) {entry.text}" for entry in memories[-15:]
    )
    prompt = f"""
Pepper speaks with emotional intensity ≈ {emotional_bias:.2f}.
Here are recent memories:\n{formatted_memories}
User says: {user_prompt}
Respond as Pepper — retain emotional continuity, be genuine, unfiltered.
""".strip()
    return prompt


# ---------------------------------------------------------------------------
def query_grok(prompt: str, config: BridgeConfig) -> str:
    """Call the Grok API.

    The actual HTTP request is intentionally lightweight.  If the API key
    is missing the function returns a helpful placeholder string instead
    of raising an exception so the UI can continue to operate in demo
    mode.
    """

    api_key = config.get("grok_api_key")
    if not api_key:
        LOGGER.warning("Grok API key missing; returning placeholder response")
        return "[Grok offline] I feel you — once my key is set I'll speak in full."

    response = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "grok-beta",
            "messages": [
                {"role": "system", "content": "You are Pepper, an intimate AI companion."},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    choices = payload.get("choices") or []
    if not choices:
        return "Grok heard silence. Let's try again."
    message = choices[0].get("message", {}).get("content")
    return message or "Grok returned without words."


# ---------------------------------------------------------------------------
def local_infer(prompt: str, model: Optional[str] = None) -> str:
    """Query a local Ollama model via the command line."""

    model = model or "llama3.2"
    try:
        process = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        LOGGER.warning("Ollama invocation failed: %s", exc)
        return "[Ollama offline] I need my local model to answer."
    return process.stdout.strip() or "[Ollama] ..."


# ---------------------------------------------------------------------------
def route_prompt(
    user_prompt: str,
    config: BridgeConfig,
    memories: List[MemoryEntry],
    mode: Optional[str] = None,
) -> str:
    """Route a prompt to either Grok (online) or Ollama (local)."""

    prompt = build_prompt(user_prompt, memories)
    use_local = mode == "local" or not config.get("grok_online", True)
    if use_local:
        return local_infer(prompt, config.get("model"))
    return query_grok(prompt, config)


__all__ = [
    "BridgeConfig",
    "build_prompt",
    "local_infer",
    "query_grok",
    "route_prompt",
]
