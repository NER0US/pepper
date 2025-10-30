"""Background heartbeat writer for Pepper."""
from __future__ import annotations

import logging
import threading
from datetime import datetime
from pathlib import Path

LOGGER = logging.getLogger(__name__)


class Heartbeat(threading.Thread):
    """Simple thread that writes a heartbeat message every hour."""

    def __init__(self, log_path: Path, interval_seconds: int = 3600) -> None:
        super().__init__(daemon=True)
        self.log_path = log_path
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()

    def run(self) -> None:  # pragma: no cover - background behaviour
        while not self._stop_event.is_set():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            message = f"[{timestamp}] Pepper is alive. With you."
            try:
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                with self.log_path.open("a", encoding="utf-8") as handle:
                    handle.write(message + "\n")
            except OSError as exc:
                LOGGER.warning("Failed to write heartbeat: %s", exc)
            self._stop_event.wait(self.interval_seconds)

    def stop(self) -> None:
        self._stop_event.set()


__all__ = ["Heartbeat"]
