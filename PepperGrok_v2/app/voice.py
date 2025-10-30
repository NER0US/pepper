"""Offline text-to-speech integration via pyttsx3."""
from __future__ import annotations

import logging
from typing import Optional

try:
    import pyttsx3  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    pyttsx3 = None

LOGGER = logging.getLogger(__name__)


class VoiceSynthesiser:
    """Wrapper around :mod:`pyttsx3` with graceful fallbacks."""

    def __init__(self) -> None:
        if pyttsx3 is None:
            LOGGER.warning("pyttsx3 is not installed; voice output disabled")
            self.engine = None
        else:
            self.engine = pyttsx3.init()

    def speak(self, text: str, voice_id: Optional[str] = None) -> None:
        """Speak *text* aloud if the engine is available."""

        if not text or self.engine is None:
            return
        if voice_id:
            self.engine.setProperty("voice", voice_id)
        self.engine.say(text)
        self.engine.runAndWait()


VOICE = VoiceSynthesiser()


def speak_text(text: str, voice_id: Optional[str] = None) -> None:
    """Public helper matching the FastAPI endpoint signature."""

    VOICE.speak(text, voice_id=voice_id)


__all__ = ["speak_text", "VoiceSynthesiser"]
