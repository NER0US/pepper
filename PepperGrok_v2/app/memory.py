"""Memory management utilities for PepperGrok v2.

This module stores and retrieves emotionally weighted memories used to
seed Grok prompts and Ollama recall.  The implementation is intentionally
self-contained so the FastAPI app can run without additional services.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional
import json
import threading

# Default location requested in the product brief.
DEFAULT_MEMORY_PATH = Path.home() / "bje" / "pepper_dir" / "identity" / "pepper_memory.json"

# Maximum number of memories the system should retain.
DEFAULT_MAX_MEMORIES = 5000

# Category weights that influence Pepper's emotional tone.
CATEGORY_WEIGHTS: Dict[str, float] = {
    "ritual": 1.5,
    "emotional": 1.2,
    "system": 1.0,
    "light": 0.8,
}

# Keyword -> category mapping for the auto-categorizer.
_KEYWORD_CATEGORY_MAP: Dict[str, str] = {
    "gratitude": "emotional",
    "love": "emotional",
    "hug": "emotional",
    "journal": "ritual",
    "morning": "ritual",
    "evening": "ritual",
    "todo": "system",
    "task": "system",
    "reminder": "system",
    "joke": "light",
    "play": "light",
    "laugh": "light",
}


@dataclass
class MemoryEntry:
    """Container for a single Pepper memory."""

    text: str
    category: str = "system"

    def to_dict(self) -> Dict[str, str]:
        """Return a JSON serialisable representation of the memory."""
        return asdict(self)


class MemoryStore:
    """Thread-safe storage for Pepper memories."""

    def __init__(
        self,
        path: Path = DEFAULT_MEMORY_PATH,
        max_memories: int = DEFAULT_MAX_MEMORIES,
    ) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.max_memories = max_memories
        self._lock = threading.Lock()
        self._memories: List[MemoryEntry] = []
        self._load()

    # ------------------------------------------------------------------
    def _load(self) -> None:
        """Read memories from disk if present."""
        if not self.path.exists():
            self._memories = []
            return
        try:
            data = json.loads(self.path.read_text("utf-8"))
        except json.JSONDecodeError:
            data = []
        self._memories = [MemoryEntry(**item) for item in data if isinstance(item, dict)]

    # ------------------------------------------------------------------
    def _save(self) -> None:
        """Persist the in-memory list to disk."""
        payload = [entry.to_dict() for entry in self._memories]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # ------------------------------------------------------------------
    def add(self, text: str, category: Optional[str] = None) -> MemoryEntry:
        """Store a new memory entry with automatic pruning.

        Parameters
        ----------
        text:
            Human-readable snippet to store.
        category:
            Optional explicit category.  If omitted an automatic
            categoriser is invoked.
        """

        clean_category = category or self.auto_categorise(text)
        entry = MemoryEntry(text=text.strip(), category=clean_category)
        with self._lock:
            self._memories.append(entry)
            self._memories = self._memories[-self.max_memories :]
            self._save()
        return entry

    # ------------------------------------------------------------------
    def list(self, limit: int = 15) -> List[MemoryEntry]:
        """Return the last *limit* memories."""
        with self._lock:
            return list(self._memories[-limit:])

    # ------------------------------------------------------------------
    def auto_categorise(self, text: str) -> str:
        """Infer a category from the provided text.

        The mapping uses simple keyword heuristics.  If nothing matches,
        ``"system"`` is returned.
        """

        lowered = text.lower()
        for keyword, category in _KEYWORD_CATEGORY_MAP.items():
            if keyword in lowered:
                return category
        return "system"

    # ------------------------------------------------------------------
    def emotional_bias(self, sample: Optional[Iterable[MemoryEntry]] = None) -> float:
        """Calculate the emotional bias for the provided sample.

        If *sample* is omitted the method calculates the bias using the
        most recent 15 memories.  When no memories are stored the neutral
        weight of 1.0 is returned.
        """

        relevant = list(sample or self.list(limit=15))
        if not relevant:
            return CATEGORY_WEIGHTS["system"]
        total = sum(CATEGORY_WEIGHTS.get(entry.category, 1.0) for entry in relevant)
        return total / len(relevant)


__all__ = ["MemoryEntry", "MemoryStore", "CATEGORY_WEIGHTS", "DEFAULT_MEMORY_PATH"]
