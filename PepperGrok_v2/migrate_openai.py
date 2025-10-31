"""Utility to migrate historical OpenAI chat logs into Pepper memories."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from app.memory import MemoryStore

CATEGORY_MAP = {
    "default": "system",
    "emotional": "emotional",
    "ritual": "ritual",
    "light": "light",
}


def iter_messages(path: Path) -> Iterable[str]:
    """Yield messages from a JSON file exported from OpenAI."""

    payload = json.loads(path.read_text("utf-8"))
    if isinstance(payload, list):
        for item in payload:
            content = item.get("content") if isinstance(item, dict) else None
            if isinstance(content, str):
                yield content


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Path to OpenAI export JSON")
    parser.add_argument("--category", default="default", choices=CATEGORY_MAP.keys())
    args = parser.parse_args()

    store = MemoryStore()
    category = CATEGORY_MAP.get(args.category, "system")
    for message in iter_messages(args.source):
        store.add(message, category=category)
    print("Migration complete.")


if __name__ == "__main__":
    main()
